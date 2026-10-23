from collections import defaultdict
from decimal import Decimal
from django.db import transaction
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from .models import Despesa,ItemPedido,Pedido

class EstoqueInsuficiente(Exception): pass

def resumo_financeiro(ano,mes):
    pedidos=Pedido.objects.filter(data_entrega__year=ano,data_entrega__month=mes,status__in=['produzido','entregue']).prefetch_related('itens__produto__receitas__ingrediente','itens__produto__componentes__produto__receitas__ingrediente')
    receita=sum((p.total for p in pedidos),Decimal('0')); custo=Decimal('0')
    for p in pedidos:
        for item in p.itens.all(): custo += item.produto.custo()*item.quantidade
    despesas=Despesa.objects.filter(data__year=ano,data__month=mes).aggregate(v=Sum('valor'))['v'] or Decimal('0')
    return {'receita':receita,'custo':custo,'despesas':despesas,'lucro':receita-custo-despesas,'qtd_pedidos':pedidos.count()}

def demanda_mensal():
    dados=ItemPedido.objects.filter(pedido__status__in=['novo','confirmado','produzido','entregue']).annotate(mes=TruncMonth('pedido__data_entrega')).values('mes','produto__nome').annotate(qtd=Sum('quantidade')).order_by('mes','produto__nome')
    grupos=defaultdict(list)
    for x in dados: grupos[x['mes']].append((x['produto__nome'],x['qtd']))
    return list(grupos.items())

def _receitas_item(produto,multiplicador=Decimal('1')):
    if produto.tipo=='kit' and produto.componentes.exists():
        for comp in produto.componentes.select_related('produto').all():
            yield from _receitas_item(comp.produto,multiplicador*Decimal(comp.quantidade))
    else:
        for r in produto.receitas.select_related('ingrediente').all():
            yield r.ingrediente, r.quantidade*multiplicador

def necessidades(pedidos):
    req=defaultdict(Decimal)
    for p in pedidos:
        for item in p.itens.select_related('produto'):
            for ing,qtd in _receitas_item(item.produto,Decimal(item.quantidade)): req[ing]+=qtd
    return req

def lista_de_compras(pedidos):
    return [(ing,q-ing.quantidade) for ing,q in necessidades(pedidos).items() if q>ing.quantidade]

@transaction.atomic
def produzir(pedido):
    req=necessidades([pedido]); faltas=[f'{i.nome}: faltam {q-i.quantidade} {i.unidade}' for i,q in req.items() if q>i.quantidade]
    if faltas: raise EstoqueInsuficiente('; '.join(faltas))
    for ing,q in req.items(): ing.quantidade-=q; ing.save(update_fields=['quantidade'])
    pedido.status='produzido'; pedido.save(update_fields=['status'])
