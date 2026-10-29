# Checklist de deploy — Doce Encanto V8 no Render

## Antes do deploy
- [ ] Backup do banco atual feito.
- [ ] Código da versão anterior preservado em commit/tag.
- [ ] `DATABASE_URL` aponta para o PostgreSQL correto.
- [ ] `SECRET_KEY` existe e não está no código.
- [ ] `DEBUG=False`.
- [ ] WhatsApp e dados legais conferidos.

## Configuração do serviço
- [ ] Runtime: Python.
- [ ] Build Command: `./build.sh`.
- [ ] Start Command: `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120`.
- [ ] Health Check Path: `/health/`.
- [ ] Branch correta conectada.

## Conferir nos logs do deploy
- [ ] Dependências instaladas sem erro.
- [ ] `python manage.py check` concluído.
- [ ] `collectstatic` concluído.
- [ ] Migration `0006_v8_gestao` aplicada ou já marcada como aplicada.
- [ ] Gunicorn iniciou sem crash/restart contínuo.

## Teste funcional pós-deploy
- [ ] `/health/` retorna `status: ok`.
- [ ] Home/cardápio abre.
- [ ] Imagens e CSS carregam.
- [ ] Pedido de teste pode ser criado.
- [ ] Acompanhamento do pedido funciona.
- [ ] Login administrativo funciona.
- [ ] Painel abre.
- [ ] Agenda V8 abre.
- [ ] Clientes/CRM abre.
- [ ] Estoque abre e movimentações aparecem.
- [ ] Produção funciona.
- [ ] Financeiro mostra valores.
- [ ] Relatórios V8 abrem.
- [ ] WhatsApp gera link/mensagem corretamente.
- [ ] Páginas de privacidade/termos/dados legais abrem.

## Depois do deploy
- [ ] Apagar pedido de teste, se necessário.
- [ ] Confirmar que os dados antigos continuam no banco.
- [ ] Confirmar política/plano do PostgreSQL para não perder dados por expiração.
