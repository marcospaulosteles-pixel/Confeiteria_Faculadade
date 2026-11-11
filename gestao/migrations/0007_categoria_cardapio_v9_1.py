from django.db import migrations, models


def classificar_produtos(apps, schema_editor):
    Produto = apps.get_model('gestao', 'Produto')
    for produto in Produto.objects.all().iterator():
        nome = produto.nome.casefold()
        if produto.tipo == 'kit' or any(p in nome for p in ('kit', 'combo', 'caixa de doces')):
            categoria = 'kits'
        elif 'brownie' in nome:
            categoria = 'brownies'
        elif any(p in nome for p in ('bolo', 'torta', 'cupcake')):
            categoria = 'bolos'
        elif 'brigadeiro' in nome:
            categoria = 'brigadeiros'
        else:
            categoria = 'especiais'
        produto.categoria = categoria
        produto.save(update_fields=['categoria'])


class Migration(migrations.Migration):
    dependencies = [('gestao','0006_v8_gestao')]
    operations = [
        migrations.AddField(model_name='produto', name='categoria', field=models.CharField(choices=[('brigadeiros','Brigadeiros'),('especiais','Doces especiais'),('brownies','Brownies'),('bolos','Bolos'),('kits','Kits e combos')], default='especiais', help_text='Aba do cardápio público em que este produto será exibido.', max_length=16)),
        migrations.RunPython(classificar_produtos, migrations.RunPython.noop),
    ]
