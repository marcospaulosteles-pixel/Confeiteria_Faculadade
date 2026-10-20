import json
from datetime import date

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db import transaction
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from . import bot, services
from .forms import PedidoForm
from .models import Ingrediente, ItemPedido, Pedido, Produto


def cardapio(request):
    """Página pública: cardápio e formulário de pedido (valida a antecedência mínima)."""
    produtos = Produto.objects.filter(ativo=True)
    form = PedidoForm(request.POST or None)
    quantidades = {}
    if request.method == "POST":
        for p in produtos:
            try:
                q = int(request.POST.get(f"qtd_{p.id}") or 0)
            except ValueError:
                q = 0
            if q > 0:
                quantidades[p] = q
        if not quantidades:
            form.add_error(None, "Escolha pelo menos um doce para fazer o pedido.")
        if form.is_valid() and quantidades:
            with transaction.atomic():
                pedido = form.save(commit=False)
                pedido.origem = "site"
                pedido.save()
                for p, q in quantidades.items():
                    ItemPedido.objects.create(pedido=pedido, produto=p, quantidade=q)
            return redirect("pedido_enviado")
    return render(request, "gestao/cardapio.html", {"produtos": produtos, "form": form,
                                                    "dias": settings.ANTECEDENCIA_MINIMA_DIAS})


def pedido_enviado(request):
    return render(request, "gestao/enviado.html")


@staff_member_required
def painel(request):
    """Financeiro do mês, alertas de validade/estoque e demanda mensal."""
    hoje = date.today()
    ingredientes = list(Ingrediente.objects.all())
    produtos = list(Produto.objects.filter(ativo=True))
    contexto = {
        "mes": hoje.strftime("%m/%Y"),
        "fin": services.resumo_financeiro(hoje.year, hoje.month),
        "vencendo": [i for i in ingredientes if i.vencendo()],
        "baixos": [i for i in ingredientes if i.estoque_baixo()],
        "demanda": services.demanda_mensal(),
        "produtos": [(p, p.custo(), p.margem()) for p in produtos],
        "novos": Pedido.objects.filter(status="novo").count(),
    }
    return render(request, "gestao/painel.html", contexto)


@staff_member_required
def producao(request):
    """Ordem de produção: pedidos em andamento por data, com lista de compras sugerida."""
    if request.method == "POST":
        pedido = get_object_or_404(Pedido, pk=request.POST.get("pedido"))
        acao = request.POST.get("acao")
        if acao == "confirmar" and pedido.status == "novo":
            pedido.status = "confirmado"
            pedido.save(update_fields=["status"])
        elif acao == "produzir" and pedido.status == "confirmado":
            try:
                services.produzir(pedido)
                messages.success(request, f"Pedido {pedido.pk} produzido e estoque atualizado.")
            except services.EstoqueInsuficiente as erro:
                messages.error(request, f"Estoque insuficiente: {erro}")
        elif acao == "entregar" and pedido.status == "produzido":
            pedido.status = "entregue"
            pedido.save(update_fields=["status"])
        elif acao == "cancelar" and pedido.status in ("novo", "confirmado"):
            pedido.status = "cancelado"
            pedido.save(update_fields=["status"])
        return redirect("producao")

    abertos = list(Pedido.objects.filter(status__in=["novo", "confirmado", "produzido"]).prefetch_related("itens__produto"))
    compras = services.lista_de_compras([p for p in abertos if p.status == "confirmado"])
    return render(request, "gestao/producao.html", {"pedidos": abertos, "compras": compras})


@csrf_exempt
@require_POST
def bot_webhook(request):
    """Recebe {"mensagem": "..."} e devolve {"resposta": "..."}.
    Conecte aqui o WhatsApp (API oficial, n8n, Make, Twilio...). Se BOT_TOKEN estiver definido, envie X-Bot-Token."""
    if settings.BOT_TOKEN and request.headers.get("X-Bot-Token") != settings.BOT_TOKEN:
        return HttpResponseForbidden("token inválido")
    try:
        texto = json.loads(request.body or b"{}").get("mensagem", "")
    except (ValueError, AttributeError):
        return JsonResponse({"erro": "JSON inválido"}, status=400)
    resposta = bot.responder(texto, produtos=Produto.objects.filter(ativo=True),
                             dias_antecedencia=settings.ANTECEDENCIA_MINIMA_DIAS,
                             link_pedido=request.build_absolute_uri("/"), nome_loja=settings.NOME_LOJA)
    return JsonResponse({"resposta": resposta})