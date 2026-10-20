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
