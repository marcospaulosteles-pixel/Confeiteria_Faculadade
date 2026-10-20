from django.db import migrations, models
class Migration(migrations.Migration):
    dependencies=[('gestao','0001_initial')]
    operations=[migrations.AddField(model_name='produto',name='imagem_url',field=models.URLField(blank=True,help_text='Opcional: cole o link público de uma foto do doce',max_length=500,verbose_name='URL da imagem'))]
