# Atualização V7.5 — cardápio novo + layout moderno da gestão

Base: V7.3 (LGPD/acessibilidade). Dependências, `build.sh`, `render.yaml` e `settings.py` NÃO foram alterados
(continua Django 5.1.x, sem mudança de versões).

## Arquivos alterados em relação à V7.3
- gestao/migrations/0005_forma_venda_cardapio_real.py (NOVO) — cria campos e carrega o cardápio
- gestao/models.py, forms.py, admin.py, views.py, bot.py, whatsapp.py — venda por cento/unidade e pedido mínimo
- gestao/templates/gestao/cardapio.html, novo_produto.html, produtos_gestao.html
- gestao/templates/gestao/gestao_base.html — layout moderno da gestão

## Atenção antes do deploy
A migração 0005 DESATIVA todos os produtos existentes (não apaga) e ativa os 12 do cardápio novo.
Produtos com o mesmo nome são atualizados no lugar. Pedidos antigos mantêm o preço da época.
Para reverter um produto antigo: Admin > Produtos > marcar "Mostrar no cardápio".

## Cardápio
Por cento: Brigadeiro meio amargo, Beijinho, Casadinho, Brigadeiro de Ninho (R$ 145,00);
Docinho de Leite Ninho, Churros, Ferreiro Rocher, Cajuzinho, Brigadeiro de paçoca (R$ 165,00).
Por unidade: Trufa R$ 2,50 (mín. 20), Galícia R$ 4,00 (mín. 20), Maçã do Amor R$ 8,00 (mín. 10).

## Depois do deploy
1. Confirmar no log do Render que a migration 0005 foi aplicada.
2. Abrir o cardápio público e fazer um pedido de teste (ex.: 100 Beijinhos = R$ 145,00).
3. Abrir /gestao/ e conferir o novo visual.
4. Foto do cabeçalho (opcional): gestao/static/gestao/img/confeitaria.jpg
