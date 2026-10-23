import csv
import io
import json
from datetime import date, timedelta
from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db import transaction
from django.db.models import Sum, Q, F, DecimalField, ExpressionWrapper
from django.db.models.functions import TruncMonth
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from . import bot, services, whatsapp
from .forms import (PedidoForm, PedidoManualForm, IngredienteForm, CompraForm,
                    ProdutoRapidoForm, DespesaForm, ConfiguracaoLojaForm)
from .models import (Ingrediente, ItemPedido, Pedido, Produto, Compra, Despesa,
                     Receita, ConfiguracaoLoja)


def _aplicar_taxa(pedido):
    cfg=ConfiguracaoLoja.atual()
    pedido.taxa_entrega = cfg.taxa_entrega if pedido.entrega == 'entrega' else Decimal('0')


def cardapio(request):
    produtos = Produto.objects.filter(ativo=True).prefetch_related('componentes__produto')
    form = PedidoForm(request.POST or None)
    quantidades = {}
    if request.method == 'POST':
        for p in produtos:
            try: q = int(request.POST.get(f'qtd_{p.id}') or 0)
            except ValueError: q = 0
            if q > 0: quantidades[p] = q
        if not quantidades: form.add_error(None, 'Escolha pelo menos um doce ou kit para fazer o pedido.')
        if form.is_valid() and quantidades:
            with transaction.atomic():
                pedido = form.save(commit=False); pedido.origem='site'; _aplicar_taxa(pedido); pedido.save()
                for p,q in quantidades.items(): ItemPedido.objects.create(pedido=pedido,produto=p,quantidade=q,preco_unitario=p.preco)
            request.session['ultimo_pedido']=pedido.pk
            return redirect('pedido_enviado')
    cfg=ConfiguracaoLoja.atual()
    return render(request,'gestao/cardapio.html',{'produtos':produtos,'form':form,'dias':settings.ANTECEDENCIA_MINIMA_DIAS,'taxa_entrega':cfg.taxa_entrega})


def pedido_enviado(request):
    pedido=None; pk=request.session.get('ultimo_pedido')
    if pk: pedido=Pedido.objects.filter(pk=pk).prefetch_related('itens__produto').first()
    link_whats=''
    if pedido and settings.WHATSAPP_LOJA: link_whats=whatsapp.link(settings.WHATSAPP_LOJA,whatsapp.texto_pedido_para_loja(pedido))
    return render(request,'gestao/enviado.html',{'pedido':pedido,'link_whats':link_whats})


def acompanhar_pedido(request, token):
    pedido=get_object_or_404(Pedido.objects.prefetch_related('itens__produto'),token_acompanhamento=token)
    etapas=['novo','confirmado','produzido','entregue']
    progresso=0 if pedido.status=='cancelado' else etapas.index(pedido.status)+1 if pedido.status in etapas else 1
    return render(request,'gestao/acompanhar.html',{'pedido':pedido,'etapas':etapas,'progresso':progresso})


@staff_member_required
def painel(request):
    hoje = date.today()
    ingredientes = list(Ingrediente.objects.all())
    produtos = list(Produto.objects.filter(ativo=True))

    # O período escolhido controla todos os indicadores e gráficos do painel.
    periodo = request.GET.get('periodo', '6m')
    periodos_validos = {'7d', '30d', '6m', '1a'}
    if periodo not in periodos_validos:
        periodo = '6m'

    def primeiro_mes_meses_atras(meses_atras):
        indice = hoje.year * 12 + (hoje.month - 1) - meses_atras
        return date(indice // 12, indice % 12 + 1, 1)

    if periodo == '7d':
        inicio_periodo = hoje - timedelta(days=6)
        periodo_label = 'Últimos 7 dias'
        granularidade = 'dia'
    elif periodo == '30d':
        inicio_periodo = hoje - timedelta(days=29)
        periodo_label = 'Últimos 30 dias'
        granularidade = 'dia'
    elif periodo == '1a':
        inicio_periodo = primeiro_mes_meses_atras(11)
        periodo_label = 'Último ano'
        granularidade = 'mes'
    else:
        inicio_periodo = primeiro_mes_meses_atras(5)
        periodo_label = 'Últimos 6 meses'
        granularidade = 'mes'

    pedidos_periodo = list(
        Pedido.objects.filter(
            status__in=['produzido', 'entregue'],
            data_entrega__range=(inicio_periodo, hoje),
        ).prefetch_related(
            'itens__produto__receitas__ingrediente',
            'itens__produto__componentes__produto__receitas__ingrediente',
        )
    )

    despesas_periodo = list(
        Despesa.objects.filter(data__range=(inicio_periodo, hoje)).values('data', 'valor')
    )

    # Cria as posições do eixo X e a função que associa cada data ao seu ponto.
    pontos = []
    if granularidade == 'dia':
        atual = inicio_periodo
        while atual <= hoje:
            pontos.append({'chave': atual, 'label': atual.strftime('%d/%m')})
            atual += timedelta(days=1)
        chave_data = lambda d: d
    else:
        atual = date(inicio_periodo.year, inicio_periodo.month, 1)
        while atual <= date(hoje.year, hoje.month, 1):
            pontos.append({'chave': (atual.year, atual.month), 'label': atual.strftime('%m/%y')})
            if atual.month == 12:
                atual = date(atual.year + 1, 1, 1)
            else:
                atual = date(atual.year, atual.month + 1, 1)
        chave_data = lambda d: (d.year, d.month)

    financeiro_mapa = {p['chave']: {'receita': Decimal('0'), 'custo': Decimal('0'), 'despesas': Decimal('0')} for p in pontos}
    receita_total = Decimal('0')
    custo_total = Decimal('0')

    for pedido in pedidos_periodo:
        chave = chave_data(pedido.data_entrega)
        receita_pedido = pedido.total
        custo_pedido = Decimal('0')
        for item in pedido.itens.all():
            custo_pedido += item.produto.custo() * item.quantidade
        receita_total += receita_pedido
        custo_total += custo_pedido
        if chave in financeiro_mapa:
            financeiro_mapa[chave]['receita'] += receita_pedido
            financeiro_mapa[chave]['custo'] += custo_pedido

    despesas_total = Decimal('0')
    for despesa in despesas_periodo:
        chave = chave_data(despesa['data'])
        despesas_total += despesa['valor']
        if chave in financeiro_mapa:
            financeiro_mapa[chave]['despesas'] += despesa['valor']

    graf_financeiro = []
    for ponto in pontos:
        valores = financeiro_mapa[ponto['chave']]
        lucro = valores['receita'] - valores['custo'] - valores['despesas']
        graf_financeiro.append({
            'mes': ponto['label'],
            'receita': float(valores['receita']),
            'lucro': float(lucro),
        })

    fin = {
        'receita': receita_total,
        'custo': custo_total,
        'despesas': despesas_total,
        'lucro': receita_total - custo_total - despesas_total,
        'qtd_pedidos': len(pedidos_periodo),
    }
    ticket_medio = (receita_total / len(pedidos_periodo)) if pedidos_periodo else Decimal('0')

    # Consolida quantidade e receita por produto usando o preço registrado no pedido.
    produto_metricas = {}
    vendas_por_ponto = {}
    for pedido in pedidos_periodo:
        chave = chave_data(pedido.data_entrega)
        for item in pedido.itens.all():
            pid = item.produto_id
            preco = item.preco_unitario if item.preco_unitario is not None else item.produto.preco
            receita_item = preco * item.quantidade
            info = produto_metricas.setdefault(pid, {
                'id': pid, 'nome': item.produto.nome, 'qtd': 0, 'receita': Decimal('0')
            })
            info['qtd'] += item.quantidade
            info['receita'] += receita_item
            vendas_por_ponto[(chave, pid)] = vendas_por_ponto.get((chave, pid), 0) + item.quantidade

    ranking_quantidade = sorted(produto_metricas.values(), key=lambda x: (-x['qtd'], x['nome']))
    ranking_receita = sorted(produto_metricas.values(), key=lambda x: (-x['receita'], x['nome']))
    mais_vendido = ranking_quantidade[0] if ranking_quantidade else None
    maior_receita = ranking_receita[0] if ranking_receita else None

    top_produtos = ranking_quantidade[:5]
    ids_top = [x['id'] for x in top_produtos]
    graf_produtos = []
    for ponto in pontos:
        linha = {'mes': ponto['label']}
        for produto_id in ids_top:
            linha[str(produto_id)] = vendas_por_ponto.get((ponto['chave'], produto_id), 0)
        graf_produtos.append(linha)
    series_produtos = [{'id': str(x['id']), 'nome': x['nome']} for x in top_produtos]

    contexto = {
        'mes': hoje.strftime('%m/%Y'),
        'periodo': periodo,
        'periodo_label': periodo_label,
        'inicio_periodo': inicio_periodo,
        'fim_periodo': hoje,
        'fin': fin,
        'ticket_medio': ticket_medio,
        'mais_vendido': mais_vendido,
        'maior_receita': maior_receita,
        'vencendo': [i for i in ingredientes if i.vencendo()],
        'baixos': [i for i in ingredientes if i.estoque_baixo()],
        'demanda': services.demanda_mensal(),
        'produtos': [(p, p.custo(), p.margem()) for p in produtos],
        'novos': Pedido.objects.filter(status='novo').count(),
        'graf_financeiro': graf_financeiro,
        'graf_produtos': graf_produtos,
        'series_produtos': series_produtos,
    }
    return render(request, 'gestao/painel.html', contexto)


@staff_member_required
def producao(request):
    if request.method=='POST':
        pedido=get_object_or_404(Pedido,pk=request.POST.get('pedido')); acao=request.POST.get('acao')
        if acao=='confirmar' and pedido.status=='novo': pedido.status='confirmado'; pedido.save(update_fields=['status'])
        elif acao=='produzir' and pedido.status=='confirmado':
            try: services.produzir(pedido); messages.success(request,f'Pedido {pedido.pk} pronto e estoque atualizado.')
            except services.EstoqueInsuficiente as erro: messages.error(request,f'Estoque insuficiente: {erro}')
        elif acao=='entregar' and pedido.status=='produzido': pedido.status='entregue'; pedido.save(update_fields=['status'])
        elif acao=='cancelar' and pedido.status in ('novo','confirmado'): pedido.status='cancelado'; pedido.save(update_fields=['status'])
        return redirect('producao')
    abertos=list(Pedido.objects.filter(status__in=['novo','confirmado','produzido']).prefetch_related('itens__produto').order_by('data_entrega'))
    compras=services.lista_de_compras([p for p in abertos if p.status=='confirmado'])
    return render(request,'gestao/producao.html',{'pedidos':abertos,'compras':compras})


@staff_member_required
def pedido_manual(request):
    form=PedidoManualForm(request.POST or None,initial={'origem':'whatsapp'})
    produtos=Produto.objects.filter(ativo=True).order_by('nome')
    if request.method=='POST':
        itens=[]
        for p in produtos:
            try: qtd=int(request.POST.get(f'qtd_{p.pk}') or 0)
            except ValueError: qtd=0
            if qtd>0: itens.append((p,qtd))
        if not itens: form.add_error(None,'Adicione pelo menos um produto ao pedido.')
        if form.is_valid() and itens:
            with transaction.atomic():
                pedido=form.save(commit=False); _aplicar_taxa(pedido); pedido.save()
                for p,qtd in itens: ItemPedido.objects.create(pedido=pedido,produto=p,quantidade=qtd,preco_unitario=p.preco)
            messages.success(request,f'Pedido #{pedido.pk} cadastrado manualmente.')
            return redirect('historico_pedidos')
    return render(request,'gestao/pedido_manual.html',{'form':form,'produtos':produtos})


@staff_member_required
def historico_pedidos(request):
    qs=Pedido.objects.prefetch_related('itens__produto').order_by('-data_entrega','-id')
    busca=request.GET.get('q','').strip(); status=request.GET.get('status',''); inicio=request.GET.get('inicio',''); fim=request.GET.get('fim','')
    if busca:
        filtro=Q(cliente__icontains=busca)|Q(telefone__icontains=busca)
        if busca.isdigit(): filtro |= Q(id=int(busca))
        qs=qs.filter(filtro)
    if status: qs=qs.filter(status=status)
    if inicio: qs=qs.filter(data_entrega__gte=inicio)
    if fim: qs=qs.filter(data_entrega__lte=fim)
    return render(request,'gestao/historico.html',{'pedidos':qs[:300],'status_choices':Pedido.STATUS,'filtros':{'q':busca,'status':status,'inicio':inicio,'fim':fim}})


@staff_member_required
def exportar_csv(request):
    response=HttpResponse(content_type='text/csv; charset=utf-8'); response['Content-Disposition']='attachment; filename="relatorio_pedidos.csv"'; response.write('\ufeff')
    w=csv.writer(response,delimiter=';'); w.writerow(['Pedido','Cliente','Telefone','Data','Status','Origem','Entrega','Subtotal','Taxa entrega','Total'])
    for p in Pedido.objects.prefetch_related('itens__produto').order_by('-data_entrega'):
        w.writerow([p.pk,p.cliente,p.telefone,p.data_entrega.strftime('%d/%m/%Y'),p.get_status_display(),p.get_origem_display(),p.get_entrega_display(),f'{p.subtotal_produtos:.2f}',f'{p.taxa_entrega:.2f}',f'{p.total:.2f}'])
    return response


@staff_member_required
def exportar_pdf(request):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate,Table,TableStyle,Paragraph,Spacer
        from reportlab.lib.styles import getSampleStyleSheet
    except ImportError:
        return HttpResponse('Instale reportlab para exportar PDF.',status=500)
    buff=io.BytesIO(); doc=SimpleDocTemplate(buff,pagesize=A4,rightMargin=28,leftMargin=28,topMargin=28,bottomMargin=28); styles=getSampleStyleSheet()
    story=[Paragraph('Relatório de pedidos - Doce Encanto',styles['Title']),Spacer(1,12)]
    dados=[['#','Cliente','Data','Status','Origem','Total']]
    for p in Pedido.objects.prefetch_related('itens__produto').order_by('-data_entrega')[:150]: dados.append([str(p.pk),p.cliente[:24],p.data_entrega.strftime('%d/%m/%Y'),p.get_status_display(),p.get_origem_display(),f'R$ {p.total:.2f}'])
    tabela=Table(dados,repeatRows=1,colWidths=[30,150,70,80,70,70]); tabela.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#8b1835')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTSIZE',(0,0),(-1,-1),8),('GRID',(0,0),(-1,-1),.25,colors.HexColor('#eadcda')),('VALIGN',(0,0),(-1,-1),'TOP'),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#fffaf6')])]))
    story.append(tabela); doc.build(story); pdf=buff.getvalue(); buff.close(); resp=HttpResponse(pdf,content_type='application/pdf'); resp['Content-Disposition']='attachment; filename="relatorio_pedidos.pdf"'; return resp


@staff_member_required
def configuracoes(request):
    cfg=ConfiguracaoLoja.atual(); form=ConfiguracaoLojaForm(request.POST or None,instance=cfg)
    if request.method=='POST' and form.is_valid(): form.save(); messages.success(request,'Configurações atualizadas.'); return redirect('configuracoes')
    return render(request,'gestao/form_simples.html',{'form':form,'titulo':'Agenda e entrega','subtitulo':'Defina o limite de encomendas aceitas por dia e a taxa padrão de entrega.','botao':'Salvar configurações'})


@staff_member_required
def central(request):
    hoje=date.today(); proximos=list(Pedido.objects.filter(data_entrega__gte=hoje,status__in=['novo','confirmado','produzido']).prefetch_related('itens__produto').order_by('data_entrega')[:12]); ingredientes=list(Ingrediente.objects.all().order_by('nome')); fin=services.resumo_financeiro(hoje.year,hoje.month); confirmados=list(Pedido.objects.filter(status='confirmado').prefetch_related('itens__produto__receitas__ingrediente'))
    return render(request,'gestao/central.html',{'hoje':hoje,'proximos':proximos,'novos':Pedido.objects.filter(status='novo').count(),'confirmados':len(confirmados),'baixos':[i for i in ingredientes if i.estoque_baixo()],'vencendo':[i for i in ingredientes if i.vencendo()],'fin':fin,'compras':services.lista_de_compras(confirmados)})

@staff_member_required
def estoque(request): return render(request,'gestao/estoque.html',{'ingredientes':Ingrediente.objects.all().order_by('nome')})

@staff_member_required
def novo_ingrediente(request):
    form=IngredienteForm(request.POST or None)
    if request.method=='POST' and form.is_valid(): form.save(); messages.success(request,'Ingrediente cadastrado.'); return redirect('estoque')
    return render(request,'gestao/form_simples.html',{'form':form,'titulo':'Novo ingrediente','subtitulo':'Cadastre uma vez e o sistema acompanha estoque, custo e validade.','botao':'Salvar ingrediente'})

@staff_member_required
def nova_compra(request):
    form=CompraForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        with transaction.atomic():
            compra=form.save(); ing=compra.ingrediente; anterior=ing.quantidade; novo=compra.quantidade
            if anterior+novo>0: ing.custo_unitario=((anterior*ing.custo_unitario)+compra.valor_total)/(anterior+novo)
            ing.quantidade=anterior+novo; ing.save(update_fields=['quantidade','custo_unitario'])
        messages.success(request,f'Compra registrada. Estoque de {ing.nome} atualizado.'); return redirect('estoque')
    return render(request,'gestao/form_simples.html',{'form':form,'titulo':'Registrar compra','subtitulo':'Informe o ingrediente, a quantidade e o total pago.','botao':'Registrar entrada'})

@staff_member_required
def produtos_gestao(request): return render(request,'gestao/produtos_gestao.html',{'produtos':Produto.objects.all().prefetch_related('receitas__ingrediente','componentes__produto').order_by('nome')})

@staff_member_required
def novo_produto(request):
    form=ProdutoRapidoForm(request.POST or None); ingredientes=Ingrediente.objects.all().order_by('nome')
    if request.method=='POST' and form.is_valid():
        rendimento=form.cleaned_data['rendimento']; linhas=[]
        for n in range(1,7):
            iid=request.POST.get(f'ing_{n}'); qtd=request.POST.get(f'qtd_{n}')
            if iid and qtd:
                try: linhas.append((Ingrediente.objects.get(pk=iid),Decimal(qtd)))
                except (Ingrediente.DoesNotExist,ValueError): pass
        produto=form.save()
        if produto.tipo=='doce':
            for ing,qtd in linhas: Receita.objects.create(produto=produto,ingrediente=ing,quantidade=qtd/Decimal(rendimento))
        messages.success(request,f'{produto.nome} cadastrado.'); return redirect('produtos_gestao')
    return render(request,'gestao/novo_produto.html',{'form':form,'ingredientes':ingredientes})

@staff_member_required
def financeiro(request):
    hoje=date.today(); form=DespesaForm(request.POST or None)
    if request.method=='POST' and form.is_valid(): form.save(); messages.success(request,'Despesa registrada.'); return redirect('financeiro')
    return render(request,'gestao/financeiro.html',{'fin':services.resumo_financeiro(hoje.year,hoje.month),'form':form,'despesas':Despesa.objects.order_by('-data')[:15]})


@csrf_exempt
@require_POST
def bot_webhook(request):
    if settings.BOT_TOKEN and request.headers.get('X-Bot-Token')!=settings.BOT_TOKEN: return HttpResponseForbidden('token inválido')
    try: texto=json.loads(request.body or b'{}').get('mensagem','')
    except (ValueError,AttributeError): return JsonResponse({'erro':'JSON inválido'},status=400)
    resposta=bot.responder(texto,produtos=Produto.objects.filter(ativo=True),dias_antecedencia=settings.ANTECEDENCIA_MINIMA_DIAS,link_pedido=request.build_absolute_uri('/'),nome_loja=settings.NOME_LOJA)
    return JsonResponse({'resposta':resposta})


def _pagina_legal(request, titulo, subtitulo, secoes):
    return render(request, 'gestao/legal.html', {'titulo_legal':titulo,'subtitulo_legal':subtitulo,'secoes':secoes})

def politica_privacidade(request):
    return _pagina_legal(request,'Política de Privacidade','Como tratamos os dados pessoais usados para pedidos e atendimento.',[
    ('1. Quem trata os dados','O responsável pelo tratamento é o fornecedor identificado na seção “Dados legais” deste site. Os canais informados ali também podem ser usados para dúvidas de privacidade.'),
    ('2. Dados necessários','Para solicitar uma encomenda, coletamos nome, telefone/WhatsApp, data pretendida, modalidade de retirada ou entrega e detalhes do pedido. Endereço e complemento são solicitados somente quando a opção de entrega é escolhida. Observações são opcionais; evite inserir dados pessoais ou sensíveis desnecessários.'),
    ('3. Finalidades','Usamos os dados para receber a solicitação, verificar agenda, entrar em contato, preparar e entregar a encomenda, manter histórico operacional e cumprir obrigações legais aplicáveis. O formulário não confirma automaticamente o pedido.'),
    ('4. Base e minimização','Dados indispensáveis à encomenda são tratados para procedimentos relacionados ao pedido, execução da relação contratual e/ou cumprimento de obrigações aplicáveis, conforme o caso. O atendimento não é condicionado a consentimento para publicidade.'),
    ('5. Compartilhamento','Os dados podem ser processados pelos provedores técnicos necessários à hospedagem e ao funcionamento do serviço. Não vendemos dados pessoais. Outros compartilhamentos devem ocorrer somente quando necessários, por obrigação legal ou com base jurídica adequada.'),
    ('6. Cookies','Usamos cookies estritamente necessários à segurança e ao funcionamento, como sessão e proteção CSRF. Cookies opcionais de medição ou marketing não devem ser ativados antes da escolha do visitante. A preferência pode ser alterada pelo botão “Cookies” no rodapé.'),
    ('7. Retenção e segurança','Os dados devem ser mantidos somente pelo período necessário às finalidades informadas e às obrigações legais. São adotadas medidas técnicas compatíveis com o serviço, embora nenhum sistema conectado à internet ofereça risco zero.'),
    ('8. Direitos do titular','O titular pode solicitar informações e exercer os direitos previstos na LGPD pelos canais de “Dados legais”. Poderá ser necessária confirmação de identidade para proteger os próprios dados.'),
    ('9. Atualizações','Esta política pode ser atualizada para refletir mudanças no serviço ou na legislação. A versão deve ser revisada com os dados reais do fornecedor antes do uso comercial.')
    ])

def politica_reembolso(request):
    return _pagina_legal(request,'Política de cancelamento e reembolso','Regras transparentes para cancelamentos, alterações e valores pagos.',[
    ('Antes da confirmação','O envio do formulário é uma solicitação e não gera cobrança nem confirmação automática. Enquanto o pedido não for confirmado, o cliente pode desistir da solicitação sem cobrança pelo site.'),
    ('Após a confirmação','Condições de sinal, cancelamento, alteração de data e eventual retenção de valores devem ser informadas claramente antes do pagamento e considerar custos assumidos, estágio da produção e legislação de defesa do consumidor.'),
    ('Compras à distância','Pedidos contratados fora do estabelecimento estão sujeitos às regras legais aplicáveis ao comércio eletrônico e ao direito de arrependimento. Produtos personalizados, perecíveis e encomendas para data específica podem exigir análise do caso concreto; esta política não pretende retirar direitos assegurados por lei.'),
    ('Problemas com o pedido','Em caso de item incorreto, defeito, quantidade divergente ou descumprimento da oferta, use o canal de atendimento para análise e solução conforme a legislação aplicável.'),
    ('Como solicitar','Informe o número ou nome do pedido, o telefone utilizado e o motivo. Não envie dados bancários sensíveis pelo formulário público.')
    ])

def termos_servico(request):
    return _pagina_legal(request,'Termos de Serviço','Condições básicas de uso do site e solicitação de encomendas.',[
    ('Uso do site','O cardápio e o formulário permitem solicitar encomendas e consultar informações. O usuário deve fornecer dados verdadeiros e suficientes para contato e execução do pedido.'),
    ('Formação do pedido','O envio da solicitação não garante disponibilidade. A encomenda somente é confirmada após verificação da agenda, definição dos detalhes e confirmação expressa pelo atendimento.'),
    ('Preços e entrega','Preços, composição, quantidades, taxa de entrega, prazo e forma de pagamento devem ser apresentados antes da confirmação. Personalizações devem ser registradas no atendimento.'),
    ('Alergênicos','O cliente deve informar necessidades relevantes no atendimento. Ingredientes e possíveis alergênicos devem ser confirmados antes da contratação quando aplicável.'),
    ('Propriedade intelectual','Textos, identidade visual e fotografias próprias não podem ser reutilizados comercialmente sem autorização. Imagens de terceiros somente devem ser publicadas com licença ou autorização compatível.'),
    ('Responsabilidade','Informações promocionais devem ser objetivas e verificáveis. O site não deve prometer resultados, qualidade absoluta, disponibilidade ou prazos que não possam ser comprovados e cumpridos.'),
    ('Legislação','Estes termos devem ser interpretados em conjunto com a legislação brasileira aplicável, especialmente normas de proteção do consumidor e de dados pessoais.')
    ])

def dados_legais(request):
    from django.conf import settings
    dados=[('Nome empresarial / responsável',settings.LEGAL_NOME),('CPF/CNPJ',settings.LEGAL_DOCUMENTO),('Endereço comercial',settings.LEGAL_ENDERECO),('Contato',settings.LEGAL_CONTATO),('E-mail de privacidade',settings.LEGAL_EMAIL_PRIVACIDADE)]
    return render(request,'gestao/dados_legais.html',{'dados':dados})
