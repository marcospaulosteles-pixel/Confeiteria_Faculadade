# Atualização V7.2 — Painel avançado

Esta versão reúne as melhorias do painel em uma única atualização para o Render.

## Novidades

- Filtros de período: 7 dias, 30 dias, 6 meses e 1 ano.
- Todos os KPIs e gráficos respeitam o período selecionado.
- Indicador de produto mais vendido por quantidade.
- Indicador de produto que mais gerou receita no período.
- Receita total do período.
- Lucro estimado do período (receita - custo dos ingredientes - despesas cadastradas).
- Ticket médio do período.
- Gráfico de linha Receita x Lucro.
- Gráfico de linha com os 5 produtos mais vendidos.
- Em 7 e 30 dias, os gráficos usam pontos diários.
- Em 6 meses e 1 ano, os gráficos usam pontos mensais.
- Redução automática dos rótulos no eixo X para evitar sobreposição.
- Gráficos desenhados no próprio projeto, sem dependência de CDN ou biblioteca externa.

## Como publicar no Render

Substitua/atualize os arquivos do projeto no mesmo repositório Git usado pelo Render e faça push. O Render deve iniciar um novo deploy automaticamente se Auto-Deploy estiver habilitado.

Não há nova alteração de banco nesta V7.2, portanto ela não exige uma migração adicional além das migrações já incluídas na V7.

## Backups incluídos no pacote

- BACKUP_V7_1_ANTES_DA_ATUALIZACAO.zip — versão imediatamente anterior.
- BACKUP_confeitaria_visual_v6_original.zip — cópia da versão V6 original.
