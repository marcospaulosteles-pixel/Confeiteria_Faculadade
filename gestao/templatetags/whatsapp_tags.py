from django import template

from .. import whatsapp

register = template.Library()


@register.filter
def wa_cliente(pedido):
    """Link do WhatsApp para falar com o cliente de um pedido (mensagem pronta)."""
    numero = whatsapp.normalizar_br(pedido.telefone)
    return whatsapp.link(numero, whatsapp.texto_para_cliente(pedido))
