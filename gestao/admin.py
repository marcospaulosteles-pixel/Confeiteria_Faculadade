from django.contrib import admin
from .models import Ingrediente,Produto,Receita,KitItem,Pedido,ItemPedido,Despesa,Compra,ConfiguracaoLoja
class ReceitaInline(admin.TabularInline): model=Receita; extra=1
class KitItemInline(admin.TabularInline): model=KitItem; fk_name='kit'; extra=1
@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display=('nome','tipo','preco','forma_venda','quantidade_minima','ativo'); list_filter=('tipo','forma_venda','ativo'); inlines=[ReceitaInline,KitItemInline]
class ItemInline(admin.TabularInline): model=ItemPedido; extra=0; fields=('produto','quantidade','preco_unitario')
@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display=('id','cliente','data_entrega','status','origem','entrega'); list_filter=('status','origem','entrega'); search_fields=('cliente','telefone'); inlines=[ItemInline]
admin.site.register(Ingrediente); admin.site.register(Despesa); admin.site.register(ConfiguracaoLoja)
@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin): list_display=('ingrediente','quantidade','valor_total','data')
