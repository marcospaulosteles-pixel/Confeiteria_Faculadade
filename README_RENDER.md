# Doce Encanto V8 — edição específica para Render

Esta edição foi preparada para manter a confeitaria no **Render** usando Django + Gunicorn + WhiteNoise + PostgreSQL.

## O que foi ajustado para o Render

- PostgreSQL passa a ser obrigatório quando o projeto detecta que está no Render.
- Não existe fallback silencioso para SQLite em produção.
- `SECRET_KEY` é obrigatória no Render.
- Static files continuam sendo servidos pelo WhiteNoise.
- Build executa instalação, `check`, `collectstatic`, migrations e criação/atualização opcional do administrador.
- Gunicorn escuta explicitamente a porta fornecida pelo Render (`$PORT`).
- Endpoint `/health/` foi adicionado para Health Check.
- Python foi fixado em `3.13.5` por `.python-version`.
- HTTPS/cookies seguros/HSTS são habilitados quando o projeto roda no Render com `DEBUG=False`.
- Suporte a domínio personalizado por `ALLOWED_HOSTS` e `CSRF_TRUSTED_ORIGINS`.

## Para atualizar o serviço que já existe

Se o site `confeitaria-faculdade` já está conectado a um repositório no GitHub, não é necessário criar outro serviço.

1. Faça backup do banco antes da atualização.
2. Substitua/mescle os arquivos da V8 no repositório atual.
3. Faça commit e push para a branch usada pelo Render.
4. Confirme no Render > Environment que `DATABASE_URL` e `SECRET_KEY` existem.
5. O Build Command deve ser `./build.sh`.
6. O Start Command pode vir do `render.yaml` ou ser configurado como:

```bash
gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120
```

7. Acompanhe o deploy nos logs.
8. Depois do deploy, abra `/health/`; deve responder `{"status":"ok"}`.
9. Teste `/admin/`, `/painel/`, cardápio, criação de pedido, agenda, estoque, financeiro e relatórios.

## Variáveis essenciais

Obrigatórias em produção:

- `DATABASE_URL`
- `SECRET_KEY`
- `DEBUG=False`

Recomendadas/conforme uso:

- `WHATSAPP_LOJA`
- `NOME_LOJA`
- `NOME_MARCA`
- `ANTECEDENCIA_MINIMA_DIAS`
- `DJANGO_SUPERUSER_USERNAME`
- `DJANGO_SUPERUSER_PASSWORD`
- `DJANGO_SUPERUSER_EMAIL`
- `LEGAL_NOME`
- `LEGAL_DOCUMENTO`
- `LEGAL_ENDERECO`
- `LEGAL_CONTATO`
- `LEGAL_EMAIL_PRIVACIDADE`

Para domínio próprio, informe também:

- `ALLOWED_HOSTS=seudominio.com.br,www.seudominio.com.br`
- `CSRF_TRUSTED_ORIGINS=https://seudominio.com.br,https://www.seudominio.com.br`

## Banco de dados

O projeto usa PostgreSQL no Render. O SQLite permanece apenas como facilidade para desenvolvimento fora do Render.

**Atenção ao plano gratuito:** a política atual do Render informa que bancos PostgreSQL Free expiram após 30 dias. Para dados reais da confeiteira, use um banco com persistência compatível com o uso do negócio ou faça uma estratégia de backup/migração antes da expiração.

## Arquivos e imagens

As imagens de produto deste projeto são referenciadas por URL ou ficam em arquivos estáticos versionados no repositório. Não dependa do filesystem temporário do Web Service para guardar uploads permanentes.

## Atualização V7.5 -> V8

A migration `gestao/migrations/0006_v8_gestao.py` adiciona os campos/estruturas da V8 sem apagar os dados existentes. O `build.sh` executa `python manage.py migrate --noinput` automaticamente.
