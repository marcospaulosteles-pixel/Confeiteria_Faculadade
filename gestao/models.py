from decimal import Decimal
from django.db import models

class Ingrediente(models.Model):
    UNIDADES=[('g','g'),('kg','kg'),('ml','ml'),('l','L'),('un','un')]
    nome=models.CharField(max_length=120)
    quantidade=models.DecimalField(max_digits=10,decimal_places=2,default=0)
    unidade=models.CharField(max_length=5,choices=UNIDADES,default='g')
    estoque_minimo=models.DecimalField(max_digits=10,decimal_places=2,default=0)
    validade=models.DateField(null=True,blank=True)
    custo_unitario=models.DecimalField(max_digits=10,decimal_places=4,default=0,help_text='Custo por unidade de medida')
    def __str__(self): return self.nome
    def estoque_baixo(self): return self.quantidade <= self.estoque_minimo
    def vencendo(self):
        from datetime import date,timedelta
        return bool(self.validade and date.today() <= self.validade <= date.today()+timedelta(days=7))

class Produto(models.Model):
    nome=models.CharField(max_length=120); descricao=models.TextField(blank=True)
    preco=models.DecimalField(max_digits=10,decimal_places=2); ativo=models.BooleanField(default=True)
    imagem_url=models.URLField('URL da imagem', max_length=500, blank=True, help_text='Opcional: cole o link público de uma foto do doce')
    ingredientes=models.ManyToManyField(Ingrediente,through='Receita',blank=True)
    def __str__(self): return self.nome
    def custo(self): return sum((r.quantidade*r.ingrediente.custo_unitario for r in self.receitas.select_related('ingrediente')),Decimal('0'))
    def margem(self): return self.preco-self.custo()

class Receita(models.Model):
    produto=models.ForeignKey(Produto,on_delete=models.CASCADE,related_name='receitas')
    ingrediente=models.ForeignKey(Ingrediente,on_delete=models.CASCADE)
    quantidade=models.DecimalField(max_digits=10,decimal_places=2,help_text='Quantidade usada por unidade do produto')
    class Meta: unique_together=('produto','ingrediente')

class Pedido(models.Model):
    STATUS=[('novo','Novo'),('confirmado','Confirmado'),('produzido','Produzido'),('entregue','Entregue'),('cancelado','Cancelado')]
    ENTREGA=[('retirada','Retirada'),('entrega','Entrega')]
    ORIGEM=[('site','Site'),('whatsapp','WhatsApp'),('outro','Outro')]
    cliente=models.CharField(max_length=120); telefone=models.CharField(max_length=30)
    data_entrega=models.DateField(); entrega=models.CharField(max_length=20,choices=ENTREGA,default='retirada')
    observacoes=models.TextField(blank=True); status=models.CharField(max_length=20,choices=STATUS,default='novo')
    origem=models.CharField(max_length=20,choices=ORIGEM,default='site'); criado_em=models.DateTimeField(auto_now_add=True)
    def __str__(self): return f'#{self.pk} - {self.cliente}'
    @property
    def total(self): return sum((i.subtotal for i in self.itens.select_related('produto')),Decimal('0'))

class ItemPedido(models.Model):
    pedido=models.ForeignKey(Pedido,on_delete=models.CASCADE,related_name='itens')
    produto=models.ForeignKey(Produto,on_delete=models.PROTECT); quantidade=models.PositiveIntegerField(default=1)
    @property
    def subtotal(self): return self.produto.preco*self.quantidade

class Despesa(models.Model):
    descricao=models.CharField(max_length=150); valor=models.DecimalField(max_digits=10,decimal_places=2); data=models.DateField()
    def __str__(self): return self.descricao
