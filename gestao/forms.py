from datetime import date,timedelta
from django import forms
from django.conf import settings
from .models import Pedido
class PedidoForm(forms.ModelForm):
    class Meta:
        model=Pedido; fields=['cliente','telefone','data_entrega','entrega','observacoes']
        labels={'cliente':'Seu nome','telefone':'WhatsApp com DDD','data_entrega':'Data da entrega ou retirada','entrega':'Como prefere receber','observacoes':'Observações (tema da festa, alergias, etc.)'}
        widgets={'data_entrega':forms.DateInput(attrs={'type':'date'}),'observacoes':forms.Textarea(attrs={'rows':3})}
    def clean_data_entrega(self):
        data=self.cleaned_data['data_entrega']; dias=settings.ANTECEDENCIA_MINIMA_DIAS
        if data < date.today()+timedelta(days=dias): raise forms.ValidationError(f'Trabalhamos com encomendas feitas com {dias} dias de antecedência. Escolha uma data a partir de {(date.today()+timedelta(days=dias)).strftime("%d/%m/%Y")}.')
        return data

from decimal import Decimal
from .models import Ingrediente, Produto, Receita, Compra, Despesa, ItemPedido

class IngredienteForm(forms.ModelForm):
    class Meta:
        model=Ingrediente; fields=['nome','unidade','quantidade','estoque_minimo','validade','custo_unitario']
        labels={'nome':'Ingrediente','unidade':'Como você controla','quantidade':'Quantidade atual no estoque','estoque_minimo':'Avise-me quando chegar a','validade':'Validade (opcional)','custo_unitario':'Custo por unidade de medida'}
        widgets={'validade':forms.DateInput(attrs={'type':'date'}), 'custo_unitario':forms.NumberInput(attrs={'step':'0.0001'})}

class CompraForm(forms.ModelForm):
    class Meta:
        model=Compra; fields=['ingrediente','quantidade','valor_total']
        labels={'ingrediente':'O que você comprou?','quantidade':'Quanto entrou no estoque?','valor_total':'Quanto pagou no total?'}
        widgets={'quantidade':forms.NumberInput(attrs={'step':'0.01','min':'0.01'}),'valor_total':forms.NumberInput(attrs={'step':'0.01','min':'0.01'})}

class ProdutoRapidoForm(forms.ModelForm):
    rendimento=forms.IntegerField(min_value=1, initial=100, label='Rendimento de referência (unidades)', help_text='Ex.: esta receita rende 100 brigadeiros.')
    class Meta:
        model=Produto; fields=['nome','descricao','preco','imagem_url','ativo']
        labels={'nome':'Nome do doce','descricao':'Descrição para o cliente','preco':'Preço de venda (R$)','imagem_url':'Foto do produto (URL)','ativo':'Mostrar no cardápio'}

class ReceitaLinhaForm(forms.Form):
    ingrediente=forms.ModelChoiceField(queryset=Ingrediente.objects.all().order_by('nome'), label='Ingrediente')
    quantidade=forms.DecimalField(min_value=Decimal('0.0001'), max_digits=10, decimal_places=2, label='Quantidade na receita')

class DespesaForm(forms.ModelForm):
    class Meta:
        model=Despesa; fields=['descricao','valor','data']; labels={'descricao':'O que foi pago?','valor':'Valor (R$)','data':'Data'}; widgets={'data':forms.DateInput(attrs={'type':'date'})}
