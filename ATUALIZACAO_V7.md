# Atualização V7 — Doce Encanto

## O que foi acrescentado
- Cadastro manual de pedidos (inclusive origem WhatsApp).
- Endereço, complemento e taxa de entrega, exibidos quando a opção é Entrega.
- Limite configurável de encomendas por dia.
- Produtos do tipo doce ou combo/kit; composição dos kits configurável no Django Admin.
- Suporte a fotos próprias dentro do projeto em `gestao/static/gestao/img/produtos/`.
- Preço do item preservado no momento do pedido, mantendo o histórico correto mesmo após reajustes.
- Painel com gráficos de vendas por produto e volume mensal.
- Histórico com busca/filtros por cliente, telefone, número, data e status.
- Exportação de pedidos em CSV e PDF.
- Link público e seguro de acompanhamento por UUID/token.
- Status público: Recebido → Confirmado → Pronto → Finalizado.

## Rotas principais
- `/` Cardápio e pedidos
- `/acompanhar/<token>/` Acompanhamento do cliente
- `/gestao/` Central
- `/gestao/pedidos/novo/` Cadastro manual
- `/gestao/pedidos/historico/` Histórico e relatórios
- `/painel/` Gráficos
- `/gestao/configuracoes/` Limite diário e taxa de entrega
- `/admin/` Administração completa (inclusive composição de kits)

## Atualizar uma instalação existente
1. Faça backup do código e do banco.
2. Substitua os arquivos pela V7.
3. Instale/atualize dependências: `pip install -r requirements.txt`
4. Rode: `python manage.py migrate`
5. Rode: `python manage.py collectstatic --no-input`
6. Reinicie o serviço.

A migração `0004_visual_v7.py` preserva pedidos antigos e preenche automaticamente o preço histórico e os tokens de acompanhamento.

## Fotos próprias
Coloque a imagem, por exemplo, em:
`gestao/static/gestao/img/produtos/brigadeiro.jpg`

No produto, informe o caminho:
`gestao/img/produtos/brigadeiro.jpg`

Dessa forma a foto acompanha o projeto/deploy e não depende de Pinterest.

## Observação de hospedagem
A aplicação é Django e precisa de execução Python + banco/armazenamento. Netlify é mais indicado para front-end/static e não é o destino recomendado para esta versão completa.

## Atualização V7.1 — painel de gráficos

- Gráfico de linha de Receita × Lucro estimado nos últimos 6 meses.
- Gráfico de linha com evolução dos 5 produtos mais vendidos.
- Indicador de produto mais vendido no mês.
- Indicador de ticket médio mensal.
- Gráficos responsivos e sem dependência de CDN externa.
