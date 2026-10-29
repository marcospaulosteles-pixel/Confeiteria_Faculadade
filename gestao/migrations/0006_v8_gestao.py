from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies=[('gestao','0005_forma_venda_cardapio_real')]
    operations=[
        migrations.AddField(model_name='pedido',name='valor_pago',field=models.DecimalField(decimal_places=2,default=0,max_digits=10)),
        migrations.AddField(model_name='pedido',name='forma_pagamento',field=models.CharField(choices=[('nao_informado','Não informado'),('pix','PIX'),('dinheiro','Dinheiro'),('cartao','Cartão'),('outro','Outro')],default='nao_informado',max_length=20)),
        migrations.CreateModel(name='MovimentoEstoque',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
            ('tipo',models.CharField(choices=[('entrada','Entrada'),('saida','Saída'),('ajuste','Ajuste')],max_length=10)),
            ('quantidade',models.DecimalField(decimal_places=3,max_digits=12)),
            ('descricao',models.CharField(blank=True,max_length=180)),
            ('criado_em',models.DateTimeField(auto_now_add=True)),
            ('compra',models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.SET_NULL,related_name='movimentos_estoque',to='gestao.compra')),
            ('ingrediente',models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,related_name='movimentacoes',to='gestao.ingrediente')),
            ('pedido',models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.SET_NULL,related_name='movimentos_estoque',to='gestao.pedido')),
        ]),
    ]
