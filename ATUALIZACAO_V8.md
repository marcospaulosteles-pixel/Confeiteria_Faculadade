# Doce Encanto — V8 Gestão integrada para confeitaria

A V8 evolui a V7.5 sem trocar a base Django nem remover o cardápio público, LGPD, acessibilidade, estoque, produção, receitas ou relatórios existentes.

## Conceito
A organização foi inspirada em sistemas integrados de gestão de serviços, adaptando a lógica para confeitaria:

- Agenda -> agenda de encomendas e capacidade diária.
- Comanda -> pedido/encomenda.
- Cadastro de clientes -> CRM baseado no histórico real dos pedidos.
- Serviços -> produtos e fichas técnicas/receitas.
- Consumo técnico -> baixa de ingredientes pela ficha técnica ao produzir.
- Estoque -> compra, custo médio, estoque mínimo, validade e auditoria de movimentações.
- Caixa -> valores previstos, recebidos, saldo a receber e despesas.
- BI -> relatório de 90 dias com ticket médio, produtos e canais.

## Novidades principais
1. Central V8 com atalhos por operação.
2. Agenda de encomendas para os próximos 31 dias.
3. Tela de clientes com frequência, total comprado, ticket médio e alerta de reativação após 90 dias.
4. Controle de recebimento por pedido, forma de pagamento e saldo.
5. Auditoria de estoque: compras criam entradas e produção cria saídas automaticamente.
6. Relatório gerencial dos últimos 90 dias.
7. Nova navegação administrativa.

## Atualização
Depois de substituir os arquivos/implantar a V8, rode:

```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

No Render, o build já deve executar os comandos previstos pelo projeto conforme a configuração existente.

## Compatibilidade
A migration `0006_v8_gestao.py` adiciona os campos de pagamento e a tabela de movimentações sem apagar dados anteriores.

## Edição Render
Foi criada uma edição específica para hospedagem no Render. Consulte `README_RENDER.md` e `RENDER_DEPLOY_CHECKLIST.md` antes de publicar.
