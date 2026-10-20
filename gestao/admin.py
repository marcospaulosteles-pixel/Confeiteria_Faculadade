from django.contrib import admin
from .models import Ingrediente,Produto,Receita,Pedido,ItemPedido,Despesa
class ReceitaInline(admin.TabularInline): model=Receita; extra=1
@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin): list_display=('nome','preco','ativo'); inlines=[ReceitaInline]
class ItemInline(admin.TabularInline): model=ItemPedido; extra=0
@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin): list_display=('id','cliente','data_entrega','status','origem'); list_filter=('status','origem'); inlines=[ItemInline]
admin.site.register(Ingrediente); admin.site.register(Despesa)
