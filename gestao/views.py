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

from . import bot, services, whatsapp
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
            request.session["ultimo_pedido"] = pedido.pk
            return redirect("pedido_enviado")
    return render(request, "gestao/cardapio.html", {"produtos": produtos, "form": form,
                                                    "dias": settings.ANTECEDENCIA_MINIMA_DIAS})


def pedido_enviado(request):
    """Confirmação do pedido, com botão para enviar o resumo à confeiteira pelo WhatsApp."""
    pedido = None
    pk = request.session.get("ultimo_pedido")
    if pk:
        pedido = Pedido.objects.filter(pk=pk).prefetch_related("itens__produto").first()
    link_whats = ""
    if pedido and settings.WHATSAPP_LOJA:
        link_whats = whatsapp.link(settings.WHATSAPP_LOJA, whatsapp.texto_pedido_para_loja(pedido))
    return render(request, "gestao/enviado.html", {"pedido": pedido, "link_whats": link_whats})


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
from decimal import Decimal
from django.db.models import Sum
from .forms import IngredienteForm, CompraForm, ProdutoRapidoForm, DespesaForm
from .models import Compra, Despesa, Receita

@staff_member_required
def central(request):
    hoje=date.today()
    proximos=list(Pedido.objects.filter(data_entrega__gte=hoje,status__in=['novo','confirmado','produzido']).prefetch_related('itens__produto').order_by('data_entrega')[:12])
    ingredientes=list(Ingrediente.objects.all().order_by('nome'))
    fin=services.resumo_financeiro(hoje.year,hoje.month)
    confirmados=list(Pedido.objects.filter(status='confirmado').prefetch_related('itens__produto__receitas__ingrediente'))
    return render(request,'gestao/central.html',{'hoje':hoje,'proximos':proximos,'novos':Pedido.objects.filter(status='novo').count(),'confirmados':len(confirmados),'baixos':[i for i in ingredientes if i.estoque_baixo()],'vencendo':[i for i in ingredientes if i.vencendo()],'fin':fin,'compras':services.lista_de_compras(confirmados)})

@staff_member_required
def estoque(request):
    return render(request,'gestao/estoque.html',{'ingredientes':Ingrediente.objects.all().order_by('nome')})

@staff_member_required
def novo_ingrediente(request):
    form=IngredienteForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        form.save(); messages.success(request,'Ingrediente cadastrado. Agora ele já pode ser usado nas receitas.'); return redirect('estoque')
    return render(request,'gestao/form_simples.html',{'form':form,'titulo':'Novo ingrediente','subtitulo':'Cadastre uma vez e o sistema passa a acompanhar estoque, custo e validade.','botao':'Salvar ingrediente'})

@staff_member_required
def nova_compra(request):
    form=CompraForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        with transaction.atomic():
            compra=form.save()
            ing=compra.ingrediente; anterior=ing.quantidade; novo=compra.quantidade
            if anterior+novo > 0:
                ing.custo_unitario=((anterior*ing.custo_unitario)+compra.valor_total)/(anterior+novo)
            ing.quantidade=anterior+novo; ing.save(update_fields=['quantidade','custo_unitario'])
        messages.success(request,f'Compra registrada. Estoque de {ing.nome} atualizado e custo médio recalculado automaticamente.'); return redirect('estoque')
    custo=None
    if request.method=='POST' and form.is_bound:
        try: custo=Decimal(request.POST.get('valor_total','0'))/Decimal(request.POST.get('quantidade','1'))
        except: pass
    return render(request,'gestao/form_simples.html',{'form':form,'titulo':'Registrar compra','subtitulo':'Informe somente o ingrediente, a quantidade e o total pago. O sistema atualiza o estoque e calcula o custo médio.','botao':'Registrar entrada','dica':'Exemplo: 10 latas por R$ 69,90 → o sistema calcula R$ 6,99 por lata.'})

@staff_member_required
def produtos_gestao(request):
    produtos=Produto.objects.all().prefetch_related('receitas__ingrediente').order_by('nome')
    return render(request,'gestao/produtos_gestao.html',{'produtos':produtos})

@staff_member_required
def novo_produto(request):
    form=ProdutoRapidoForm(request.POST or None)
    ingredientes=Ingrediente.objects.all().order_by('nome')
    if request.method=='POST' and form.is_valid():
        rendimento=form.cleaned_data['rendimento']; linhas=[]
        for n in range(1,7):
            iid=request.POST.get(f'ing_{n}'); qtd=request.POST.get(f'qtd_{n}')
            if iid and qtd:
                try: linhas.append((Ingrediente.objects.get(pk=iid),Decimal(qtd)))
                except (Ingrediente.DoesNotExist,ValueError): pass
        if not linhas:
            form.add_error(None,'Adicione pelo menos um ingrediente da receita.')
        else:
            with transaction.atomic():
                produto=form.save()
                for ing,qtd in linhas: Receita.objects.create(produto=produto,ingrediente=ing,quantidade=qtd/Decimal(rendimento))
            messages.success(request,f'{produto.nome} cadastrado. O custo e a margem agora são calculados automaticamente pela receita.'); return redirect('produtos_gestao')
    return render(request,'gestao/novo_produto.html',{'form':form,'ingredientes':ingredientes})

@staff_member_required
def financeiro(request):
    hoje=date.today(); form=DespesaForm(request.POST or None)
    if request.method=='POST' and form.is_valid(): form.save(); messages.success(request,'Despesa registrada.'); return redirect('financeiro')
    return render(request,'gestao/financeiro.html',{'fin':services.resumo_financeiro(hoje.year,hoje.month),'form':form,'despesas':Despesa.objects.order_by('-data')[:15]})
