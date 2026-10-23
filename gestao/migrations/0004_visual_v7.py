import uuid
from django.db import migrations, models
import django.db.models.deletion


def preencher_tokens_e_precos(apps, schema_editor):
    Pedido=apps.get_model('gestao','Pedido')
    ItemPedido=apps.get_model('gestao','ItemPedido')
    for p in Pedido.objects.filter(token_acompanhamento__isnull=True):
        p.token_acompanhamento=uuid.uuid4(); p.save(update_fields=['token_acompanhamento'])
    for item in ItemPedido.objects.filter(preco_unitario__isnull=True).select_related('produto'):
        item.preco_unitario=item.produto.preco; item.save(update_fields=['preco_unitario'])


class Migration(migrations.Migration):
    dependencies=[('gestao','0003_compra')]
    operations=[
        migrations.AddField(model_name='produto',name='tipo',field=models.CharField(choices=[('doce','Doce'),('kit','Combo / kit')],default='doce',max_length=12)),
        migrations.AddField(model_name='produto',name='imagem_local',field=models.CharField(blank=True,help_text='Caminho dentro de gestao/static/, ex.: gestao/img/produtos/brigadeiro.jpg',max_length=255)),
        migrations.AlterField(model_name='produto',name='imagem_url',field=models.URLField(blank=True,help_text='Opcional. Prefira imagem local para não depender de sites externos.',max_length=500,verbose_name='URL da imagem')),
        migrations.AddField(model_name='pedido',name='endereco',field=models.CharField(blank=True,max_length=255)),
        migrations.AddField(model_name='pedido',name='complemento',field=models.CharField(blank=True,max_length=120)),
        migrations.AddField(model_name='pedido',name='taxa_entrega',field=models.DecimalField(decimal_places=2,default=0,max_digits=10)),
        migrations.AddField(model_name='pedido',name='token_acompanhamento',field=models.UUIDField(editable=False,null=True)),
        migrations.AlterField(model_name='pedido',name='status',field=models.CharField(choices=[('novo','Recebido'),('confirmado','Confirmado'),('produzido','Pronto'),('entregue','Finalizado'),('cancelado','Cancelado')],default='novo',max_length=20)),
        migrations.AddField(model_name='itempedido',name='preco_unitario',field=models.DecimalField(blank=True,decimal_places=2,max_digits=10,null=True)),
        migrations.CreateModel(name='ConfiguracaoLoja',fields=[('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),('limite_encomendas_dia',models.PositiveIntegerField(default=5,help_text='Quantidade máxima de pedidos aceitos por data.')),('taxa_entrega',models.DecimalField(decimal_places=2,default=0,max_digits=10)),('atualizado_em',models.DateTimeField(auto_now=True))]),
        migrations.CreateModel(name='KitItem',fields=[('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),('quantidade',models.PositiveIntegerField(default=1)),('kit',models.ForeignKey(limit_choices_to={'tipo':'kit'},on_delete=django.db.models.deletion.CASCADE,related_name='componentes',to='gestao.produto')),('produto',models.ForeignKey(limit_choices_to={'tipo':'doce'},on_delete=django.db.models.deletion.PROTECT,related_name='presente_em_kits',to='gestao.produto'))],options={'unique_together':{('kit','produto')}}),
        migrations.RunPython(preencher_tokens_e_precos,migrations.RunPython.noop),
        migrations.AlterField(model_name='pedido',name='token_acompanhamento',field=models.UUIDField(default=uuid.uuid4,editable=False,unique=True)),
    ]
