# Doce Encanto — V4 Gestão Assistida

Esta versão foi desenhada para uma microempreendedora de confeitaria que trabalha sozinha e produz sob encomenda.

## Nova Central da Confeiteira
Acesse `/gestao/` com o usuário administrador. O Django Admin (`/admin/`) continua disponível como área técnica, mas deixa de ser necessário para as tarefas diárias.

### Automações
- Registrar compra aumenta o estoque automaticamente.
- O custo médio do ingrediente é recalculado a cada compra.
- Produto + receita calcula custo e margem automaticamente.
- Receita de referência pode ser cadastrada com rendimento (ex.: ingredientes para 100 brigadeiros).
- Pedidos confirmados alimentam a lista de compras.
- Ao marcar pedido como produzido, os ingredientes são baixados do estoque.
- Financeiro resume vendas, ingredientes, despesas e resultado estimado.
- Alertas mostram estoque baixo e validade próxima.

## Fluxo sugerido
1. Cadastre os ingredientes uma vez.
2. Registre compras conforme acontecem.
3. Cadastre produtos e suas receitas.
4. Confirme encomendas recebidas.
5. Consulte a produção e lista de compras.
6. Marque como produzido para baixar estoque.
7. Registre despesas gerais no Financeiro.
