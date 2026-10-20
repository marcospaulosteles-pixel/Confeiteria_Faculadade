from django.urls import path
from . import views
urlpatterns=[path('',views.cardapio,name='cardapio'),path('enviado/',views.pedido_enviado,name='pedido_enviado'),path('painel/',views.painel,name='painel'),path('producao/',views.producao,name='producao'),path('bot/webhook/',views.bot_webhook,name='bot_webhook')]
