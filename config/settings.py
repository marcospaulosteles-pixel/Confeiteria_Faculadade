from pathlib import Path
import os
import re

import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent
IS_RENDER = os.getenv("RENDER", "").lower() == "true" or bool(os.getenv("RENDER_EXTERNAL_HOSTNAME"))

SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")
DEBUG = os.getenv("DEBUG", "False").lower() in ("1", "true", "yes")

if IS_RENDER and SECRET_KEY == "dev-only-change-me":
    raise RuntimeError("SECRET_KEY não configurada no Render.")

ALLOWED_HOSTS = ["127.0.0.1", "localhost"]
render_host = os.getenv("RENDER_EXTERNAL_HOSTNAME", "").strip()
if render_host:
    ALLOWED_HOSTS.append(render_host)

extra_hosts = [h.strip() for h in os.getenv("ALLOWED_HOSTS", "").split(",") if h.strip()]
ALLOWED_HOSTS.extend(extra_hosts)
ALLOWED_HOSTS = list(dict.fromkeys(ALLOWED_HOSTS))

CSRF_TRUSTED_ORIGINS = []
if render_host:
    CSRF_TRUSTED_ORIGINS.append(f"https://{render_host}")
for host in extra_hosts:
    clean_host = host.replace("https://", "").replace("http://", "").strip("/")
    if clean_host:
        CSRF_TRUSTED_ORIGINS.append(f"https://{clean_host}")
for origin in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(","):
    origin = origin.strip()
    if origin:
        CSRF_TRUSTED_ORIGINS.append(origin)
CSRF_TRUSTED_ORIGINS = list(dict.fromkeys(CSRF_TRUSTED_ORIGINS))

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "gestao",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [],
    "APP_DIRS": True,
    "OPTIONS": {
        "context_processors": [
            "django.template.context_processors.request",
            "django.contrib.auth.context_processors.auth",
            "django.contrib.messages.context_processors.messages",
            "gestao.context_processors.loja",
        ]
    },
}]
WSGI_APPLICATION = "config.wsgi.application"

# No Render, o banco deve ser PostgreSQL via DATABASE_URL. Não fazemos fallback
# para SQLite em produção porque o filesystem do serviço é efêmero.
database_url = os.getenv("DATABASE_URL", "").strip()
if IS_RENDER and not database_url:
    raise RuntimeError("DATABASE_URL não configurada no Render. Conecte um PostgreSQL antes do deploy.")

DATABASES = {
    "default": dj_database_url.config(
        default=database_url or f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
        conn_health_checks=True,
    )
}

AUTH_PASSWORD_VALIDATORS = []
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
ANTECEDENCIA_MINIMA_DIAS = int(os.getenv("ANTECEDENCIA_MINIMA_DIAS", "3"))
NOME_LOJA = os.getenv("NOME_LOJA", "Doces feitos com amor")
NOME_MARCA = os.getenv("NOME_MARCA", "Doce Encanto")
WHATSAPP_LOJA = re.sub(r"\D", "", os.getenv("WHATSAPP_LOJA", ""))
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
LOGIN_URL = "/admin/login/"

# Segurança para proxy HTTPS do Render.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_SSL_REDIRECT = IS_RENDER and not DEBUG
SECURE_HSTS_SECONDS = 31536000 if IS_RENDER and not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = IS_RENDER and not DEBUG
SECURE_HSTS_PRELOAD = False

# Dados jurídicos: preencher no Render > Environment. Nunca inventar.
LEGAL_NOME = os.getenv("LEGAL_NOME", "A preencher antes da publicação comercial")
LEGAL_DOCUMENTO = os.getenv("LEGAL_DOCUMENTO", "A preencher antes da publicação comercial")
LEGAL_ENDERECO = os.getenv("LEGAL_ENDERECO", "A preencher antes da publicação comercial")
LEGAL_CONTATO = os.getenv("LEGAL_CONTATO", "A preencher antes da publicação comercial")
LEGAL_EMAIL_PRIVACIDADE = os.getenv("LEGAL_EMAIL_PRIVACIDADE", "A preencher antes da publicação comercial")
