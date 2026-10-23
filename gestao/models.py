from decimal import Decimal
import uuid
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
    TIPOS=[('doce','Doce'),('kit','Combo / kit')]
    nome=models.CharField(max_length=120)
    descricao=models.TextField(blank=True)
    preco=models.DecimalField(max_digits=10,decimal_places=2)
    ativo=models.BooleanField(default=True)
    tipo=models.CharField(max_length=12,choices=TIPOS,default='doce')
    imagem_url=models.URLField('URL da imagem', max_length=500, blank=True, help_text='Opcional. Prefira imagem local para não depender de sites externos.')
    imagem_local=models.CharField(max_length=255,blank=True,help_text='Caminho dentro de gestao/static/, ex.: gestao/img/produtos/brigadeiro.jpg')
    ingredientes=models.ManyToManyField(Ingrediente,through='Receita',blank=True)
    def __str__(self): return self.nome
    def custo(self):
        if self.tipo == 'kit' and self.componentes.exists():
            return sum((x.produto.custo()*x.quantidade for x in self.componentes.select_related('produto')),Decimal('0'))
        return sum((r.quantidade*r.ingrediente.custo_unitario for r in self.receitas.select_related('ingrediente')),Decimal('0'))
    def margem(self): return self.preco-self.custo()


class KitItem(models.Model):
    kit=models.ForeignKey(Produto,on_delete=models.CASCADE,related_name='componentes',limit_choices_to={'tipo':'kit'})
    produto=models.ForeignKey(Produto,on_delete=models.PROTECT,related_name='presente_em_kits',limit_choices_to={'tipo':'doce'})
    quantidade=models.PositiveIntegerField(default=1)
    class Meta: unique_together=('kit','produto')
    def __str__(self): return f'{self.quantidade}x {self.produto} em {self.kit}'


class Receita(models.Model):
    produto=models.ForeignKey(Produto,on_delete=models.CASCADE,related_name='receitas')
    ingrediente=models.ForeignKey(Ingrediente,on_delete=models.CASCADE)
    quantidade=models.DecimalField(max_digits=10,decimal_places=2,help_text='Quantidade usada por unidade do produto')
    class Meta: unique_together=('produto','ingrediente')


class ConfiguracaoLoja(models.Model):
    limite_encomendas_dia=models.PositiveIntegerField(default=5,help_text='Quantidade máxima de pedidos aceitos por data.')
    taxa_entrega=models.DecimalField(max_digits=10,decimal_places=2,default=0)
    atualizado_em=models.DateTimeField(auto_now=True)
    def __str__(self): return 'Configurações da loja'
    @classmethod
    def atual(cls):
        obj,_=cls.objects.get_or_create(pk=1)
        return obj


class Pedido(models.Model):
    STATUS=[('novo','Recebido'),('confirmado','Confirmado'),('produzido','Pronto'),('entregue','Finalizado'),('cancelado','Cancelado')]
    ENTREGA=[('retirada','Retirada'),('entrega','Entrega')]
    ORIGEM=[('site','Site'),('whatsapp','WhatsApp'),('outro','Outro')]
    cliente=models.CharField(max_length=120)
    telefone=models.CharField(max_length=30)
    data_entrega=models.DateField()
    entrega=models.CharField(max_length=20,choices=ENTREGA,default='retirada')
    endereco=models.CharField(max_length=255,blank=True)
    complemento=models.CharField(max_length=120,blank=True)
    taxa_entrega=models.DecimalField(max_digits=10,decimal_places=2,default=0)
    observacoes=models.TextField(blank=True)
    status=models.CharField(max_length=20,choices=STATUS,default='novo')
    origem=models.CharField(max_length=20,choices=ORIGEM,default='site')
    token_acompanhamento=models.UUIDField(default=uuid.uuid4,editable=False,unique=True)
    criado_em=models.DateTimeField(auto_now_add=True)
    def __str__(self): return f'#{self.pk} - {self.cliente}'
    @property
    def subtotal_produtos(self): return sum((i.subtotal for i in self.itens.select_related('produto')),Decimal('0'))
    @property
    def total(self): return self.subtotal_produtos + (self.taxa_entrega or Decimal('0'))


class ItemPedido(models.Model):
    pedido=models.ForeignKey(Pedido,on_delete=models.CASCADE,related_name='itens')
    produto=models.ForeignKey(Produto,on_delete=models.PROTECT)
    quantidade=models.PositiveIntegerField(default=1)
    preco_unitario=models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
    def save(self,*args,**kwargs):
        if self.preco_unitario is None: self.preco_unitario=self.produto.preco
        super().save(*args,**kwargs)
    @property
    def subtotal(self): return (self.preco_unitario if self.preco_unitario is not None else self.produto.preco)*self.quantidade


class Despesa(models.Model):
    descricao=models.CharField(max_length=150); valor=models.DecimalField(max_digits=10,decimal_places=2); data=models.DateField()
    def __str__(self): return self.descricao


class Compra(models.Model):
    ingrediente=models.ForeignKey(Ingrediente,on_delete=models.PROTECT,related_name='compras')
    quantidade=models.DecimalField(max_digits=10,decimal_places=2,help_text='Quantidade comprada na unidade de estoque do ingrediente')
    valor_total=models.DecimalField(max_digits=10,decimal_places=2)
    data=models.DateField(auto_now_add=True)
    criado_em=models.DateTimeField(auto_now_add=True)
    def __str__(self): return f'{self.ingrediente} - {self.quantidade} {self.ingrediente.unidade}'
