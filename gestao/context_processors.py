from django.conf import settings


def loja(request):
    """Disponibiliza o WhatsApp da loja e o nome da marca em todos os templates."""
    from . import whatsapp
    numero = settings.WHATSAPP_LOJA
    texto = f"Olá! Vim pelo site {settings.NOME_MARCA} e gostaria de fazer uma encomenda 🍰"
    return {
        "WHATSAPP_LOJA": numero,
        "WHATSAPP_LINK": whatsapp.link(numero, texto),
        "NOME_MARCA": settings.NOME_MARCA,
    }
