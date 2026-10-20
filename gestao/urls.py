from django.urls import path
from . import views
urlpatterns=[
 path('',views.cardapio,name='cardapio'),path('enviado/',views.pedido_enviado,name='pedido_enviado'),
 path('gestao/',views.central,name='central'),path('painel/',views.painel,name='painel'),path('producao/',views.producao,name='producao'),
 path('gestao/estoque/',views.estoque,name='estoque'),path('gestao/estoque/novo/',views.novo_ingrediente,name='novo_ingrediente'),path('gestao/compras/nova/',views.nova_compra,name='nova_compra'),
 path('gestao/produtos/',views.produtos_gestao,name='produtos_gestao'),path('gestao/produtos/novo/',views.novo_produto,name='novo_produto'),path('gestao/financeiro/',views.financeiro,name='financeiro'),
 path('bot/webhook/',views.bot_webhook,name='bot_webhook')]
