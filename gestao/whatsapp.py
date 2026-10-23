"""Integração simples com WhatsApp usando links wa.me (sem API, sem custo).

O link abre o WhatsApp (celular ou WhatsApp Web) com a mensagem já escrita;
a pessoa só precisa tocar em "enviar".
"""
import re
from urllib.parse import quote

from django.conf import settings


def so_digitos(valor):
    return re.sub(r"\D", "", valor or "")


def normalizar_br(telefone):
    """Deixa o telefone no formato internacional: 55 + DDD + número."""
    d = so_digitos(telefone)
    if d.startswith("00"):
        d = d[2:]
    if len(d) in (10, 11):  # DDD + número, sem país
        d = "55" + d
    return d


def link(numero, texto=""):
    numero = so_digitos(numero)
    if not numero:
        return ""
    url = f"https://wa.me/{numero}"
    return f"{url}?text={quote(texto)}" if texto else url


def _real(valor):
    return f"R$ {valor:.2f}".replace(".", ",")


def _itens(pedido):
    return "\n".join(f"• {i.quantidade}x {i.produto.nome}" for i in pedido.itens.all())


def texto_pedido_para_loja(pedido):
    """Mensagem que o CLIENTE envia para a confeiteira depois de fazer o pedido no site."""
    linhas = [
        f"Olá! Acabei de fazer um pedido pelo site {settings.NOME_MARCA}.",
        "",
        f"*Pedido #{pedido.pk}*",
        f"Nome: {pedido.cliente}",
        f"Data desejada: {pedido.data_entrega:%d/%m/%Y}",
        f"Forma: {pedido.get_entrega_display()}",
        "",
        _itens(pedido),
        "",
        f"Total estimado: {_real(pedido.total)}",
    ]
    if pedido.observacoes:
        linhas += ["", f"Observações: {pedido.observacoes}"]
    return "\n".join(linhas)


def texto_para_cliente(pedido):
    """Mensagem que a CONFEITEIRA envia ao cliente, conforme a situação do pedido."""
    primeiro = (pedido.cliente or "").split(" ")[0] or "tudo bem"
    data = f"{pedido.data_entrega:%d/%m/%Y}"
    resumo = f"{_itens(pedido)}\nTotal: {_real(pedido.total)}"
    marca = settings.NOME_MARCA
    if pedido.status == "novo":
        return (f"Olá, {primeiro}! Aqui é da {marca} 🍰\n"
                f"Recebi o seu pedido #{pedido.pk} para {data}:\n{resumo}\n\n"
                "Vou conferir minha agenda e já te confirmo a data, combinado?")
    if pedido.status == "confirmado":
        return (f"Olá, {primeiro}! Seu pedido #{pedido.pk} está *confirmado* para {data} ✅\n"
                f"{resumo}\n\nQualquer ajuste, é só me avisar por aqui. Obrigada! 💕")
    if pedido.status == "produzido":
        quando = "pronto para entrega" if pedido.entrega == "entrega" else "pronto para retirada"
        return (f"Olá, {primeiro}! Seu pedido #{pedido.pk} está *{quando}* 🎉\n"
                f"{resumo}\n\nPosso combinar o horário com você?")
    return f"Olá, {primeiro}! Aqui é da {marca} sobre o pedido #{pedido.pk}."
