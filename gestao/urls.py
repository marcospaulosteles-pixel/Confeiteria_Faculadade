from django.urls import path
from . import views
urlpatterns=[
 path('',views.cardapio,name='cardapio'),path('enviado/',views.pedido_enviado,name='pedido_enviado'),
 path('acompanhar/<uuid:token>/',views.acompanhar_pedido,name='acompanhar_pedido'),
 path('gestao/',views.central,name='central'),path('gestao/agenda/',views.agenda_encomendas,name='agenda_encomendas'),path('gestao/clientes/',views.clientes,name='clientes'),path('gestao/relatorios/',views.relatorios_v8,name='relatorios_v8'),path('painel/',views.painel,name='painel'),path('producao/',views.producao,name='producao'),
 path('gestao/pedidos/novo/',views.pedido_manual,name='pedido_manual'),path('gestao/pedidos/historico/',views.historico_pedidos,name='historico_pedidos'),
 path('gestao/relatorios/pedidos.csv',views.exportar_csv,name='exportar_csv'),path('gestao/relatorios/pedidos.pdf',views.exportar_pdf,name='exportar_pdf'),
 path('gestao/configuracoes/',views.configuracoes,name='configuracoes'),
 path('gestao/estoque/',views.estoque,name='estoque'),path('gestao/estoque/movimentacoes/',views.movimentacoes_estoque,name='movimentacoes_estoque'),path('gestao/estoque/novo/',views.novo_ingrediente,name='novo_ingrediente'),path('gestao/compras/nova/',views.nova_compra,name='nova_compra'),
 path('gestao/produtos/',views.produtos_gestao,name='produtos_gestao'),path('gestao/produtos/novo/',views.novo_produto,name='novo_produto'),path('gestao/financeiro/',views.financeiro,name='financeiro'),path('gestao/pedidos/<int:pk>/pagamento/',views.atualizar_pagamento,name='atualizar_pagamento'),
 path('privacidade/',views.politica_privacidade,name='politica_privacidade'),
 path('reembolso/',views.politica_reembolso,name='politica_reembolso'),
 path('termos/',views.termos_servico,name='termos_servico'),
 path('dados-legais/',views.dados_legais,name='dados_legais'),
 path('bot/webhook/',views.bot_webhook,name='bot_webhook')]
