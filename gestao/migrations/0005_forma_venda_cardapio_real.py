from django.db import migrations, models


def carregar_cardapio(apps, schema_editor):
    Produto = apps.get_model('gestao', 'Produto')
    # Mantém produtos antigos para histórico, mas retira do cardápio público.
    Produto.objects.update(ativo=False)
    itens = [
        ('Brigadeiro meio amargo', 'Brigadeiro artesanal de chocolate meio amargo.', '145.00', 'cento', 100),
        ('Beijinho', 'Clássico docinho de coco, preparado artesanalmente.', '145.00', 'cento', 100),
        ('Casadinho', 'Combinação artesanal de sabores em um docinho clássico.', '145.00', 'cento', 100),
        ('Brigadeiro de Ninho', 'Brigadeiro cremoso preparado com leite Ninho.', '145.00', 'cento', 100),
        ('Docinho de Leite Ninho', 'Docinho artesanal de leite Ninho.', '165.00', 'cento', 100),
        ('Churros', 'Docinho sabor churros, finalizado com doce de leite.', '165.00', 'cento', 100),
        ('Ferreiro Rocher', 'Docinho com xerém de amendoim e Nutella.', '165.00', 'cento', 100),
        ('Cajuzinho', 'Cajuzinho artesanal, ideal para festas e comemorações.', '165.00', 'cento', 100),
        ('Brigadeiro de paçoca', 'Brigadeiro artesanal com sabor de paçoca.', '165.00', 'cento', 100),
        ('Trufa', 'Trufa artesanal. Recheios: brigadeiro, coco, maracujá e Ninho.', '2.50', 'unidade', 20),
        ('Galícia', 'Recheios disponíveis: brigadeiro, coco, maracujá e Ninho.', '4.00', 'unidade', 20),
        ('Maçã do Amor', 'Maçã do amor artesanal, feita sob encomenda.', '8.00', 'unidade', 10),
    ]
    for nome, descricao, preco, forma, minimo in itens:
        dados = {
            'descricao': descricao, 'preco': preco, 'forma_venda': forma,
            'quantidade_minima': minimo, 'tipo': 'doce', 'ativo': True,
        }
        # filter().first() evita erro caso já exista mais de um produto com o mesmo nome.
        existente = Produto.objects.filter(nome=nome).order_by('id').first()
        if existente:
            for campo, valor in dados.items():
                setattr(existente, campo, valor)
            existente.save()
        else:
            Produto.objects.create(nome=nome, **dados)


class Migration(migrations.Migration):
    dependencies = [('gestao', '0004_visual_v7')]
    operations = [
        migrations.AddField(model_name='produto', name='forma_venda', field=models.CharField(choices=[('unidade','Por unidade'),('cento','Por cento (100 unidades)')], default='unidade', help_text='Define se o preço informado vale por 1 unidade ou por 100 unidades.', max_length=10)),
        migrations.AddField(model_name='produto', name='quantidade_minima', field=models.PositiveIntegerField(default=1, help_text='Quantidade mínima de doces aceita no pedido.')),
        migrations.AddField(model_name='itempedido', name='quantidade_base_preco', field=models.PositiveIntegerField(default=1, help_text='Quantidade de unidades coberta pelo preço registrado (1 ou 100).')),
        migrations.RunPython(carregar_cardapio, migrations.RunPython.noop),
    ]
