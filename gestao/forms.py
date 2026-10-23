from datetime import date,timedelta
from decimal import Decimal
from django import forms
from django.conf import settings
from .models import Pedido, Ingrediente, Produto, Receita, Compra, Despesa, ConfiguracaoLoja


class PedidoForm(forms.ModelForm):
    aceite_privacidade=forms.BooleanField(
        required=True,
        label='Li o Aviso de Privacidade',
        help_text='Seus dados serão usados para receber, organizar, confirmar e atender esta encomenda.'
    )
    class Meta:
        model=Pedido
        fields=['cliente','telefone','data_entrega','entrega','endereco','complemento','observacoes']
        labels={'cliente':'Seu nome','telefone':'WhatsApp com DDD','data_entrega':'Data da entrega ou retirada','entrega':'Como prefere receber','endereco':'Endereço para entrega','complemento':'Complemento / referência','observacoes':'Observações (tema da festa, alergias, etc.)'}
        widgets={'data_entrega':forms.DateInput(attrs={'type':'date'}),'observacoes':forms.Textarea(attrs={'rows':3})}
    def clean_data_entrega(self):
        data=self.cleaned_data['data_entrega']; dias=settings.ANTECEDENCIA_MINIMA_DIAS
        minima=date.today()+timedelta(days=dias)
        if data < minima: raise forms.ValidationError(f'Trabalhamos com encomendas feitas com {dias} dias de antecedência. Escolha uma data a partir de {minima.strftime("%d/%m/%Y")}.')
        limite=ConfiguracaoLoja.atual().limite_encomendas_dia
        ocupados=Pedido.objects.filter(data_entrega=data).exclude(status='cancelado')
        if self.instance.pk: ocupados=ocupados.exclude(pk=self.instance.pk)
        if ocupados.count() >= limite: raise forms.ValidationError('Essa data já atingiu o limite de encomendas. Escolha outra data.')
        return data
    def clean(self):
        dados=super().clean()
        if dados.get('entrega')=='entrega' and not (dados.get('endereco') or '').strip():
            self.add_error('endereco','Informe o endereço para entrega.')
        return dados


class PedidoManualForm(PedidoForm):
    class Meta(PedidoForm.Meta):
        fields=['cliente','telefone','data_entrega','entrega','endereco','complemento','origem','status','observacoes']
        labels={**PedidoForm.Meta.labels,'origem':'Origem do pedido','status':'Status inicial'}


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
    rendimento=forms.IntegerField(min_value=1, initial=100, label='Rendimento de referência (unidades)', help_text='Para doces: ex. esta receita rende 100 brigadeiros. Kits podem ser montados depois no Admin.')
    class Meta:
        model=Produto; fields=['nome','descricao','preco','tipo','imagem_local','imagem_url','ativo']
        labels={'nome':'Nome','descricao':'Descrição para o cliente','preco':'Preço de venda (R$)','tipo':'Tipo','imagem_local':'Foto própria no projeto','imagem_url':'Foto externa (opcional)','ativo':'Mostrar no cardápio'}

class ReceitaLinhaForm(forms.Form):
    ingrediente=forms.ModelChoiceField(queryset=Ingrediente.objects.all().order_by('nome'), label='Ingrediente')
    quantidade=forms.DecimalField(min_value=Decimal('0.0001'), max_digits=10, decimal_places=2, label='Quantidade na receita')

class DespesaForm(forms.ModelForm):
    class Meta:
        model=Despesa; fields=['descricao','valor','data']; labels={'descricao':'O que foi pago?','valor':'Valor (R$)','data':'Data'}; widgets={'data':forms.DateInput(attrs={'type':'date'})}

class ConfiguracaoLojaForm(forms.ModelForm):
    class Meta:
        model=ConfiguracaoLoja; fields=['limite_encomendas_dia','taxa_entrega']
        labels={'limite_encomendas_dia':'Máximo de encomendas por dia','taxa_entrega':'Taxa padrão de entrega (R$)'}
