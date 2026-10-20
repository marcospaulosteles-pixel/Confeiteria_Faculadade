from django.db import migrations, models
import django.db.models.deletion
class Migration(migrations.Migration):
    dependencies=[('gestao','0002_produto_imagem_url')]
    operations=[migrations.CreateModel(name='Compra',fields=[('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),('quantidade',models.DecimalField(decimal_places=2,help_text='Quantidade comprada na unidade de estoque do ingrediente',max_digits=10)),('valor_total',models.DecimalField(decimal_places=2,max_digits=10)),('data',models.DateField(auto_now_add=True)),('criado_em',models.DateTimeField(auto_now_add=True)),('ingrediente',models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,related_name='compras',to='gestao.ingrediente'))])]
