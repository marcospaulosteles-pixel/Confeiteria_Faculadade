# Doce Encanto — V5 Layout da Gestão

## O que mudou
- Novo molde `gestao_base.html`: todas as telas da gestão ganham banner no topo + conteúdo com espaçamento à esquerda (acabou o texto colado na borda).
- Banner com FOTO à direita e DEGRADÊ da esquerda (cor creme sólida) para a direita (foto aparecendo).
- Menu da gestão com a página atual destacada.
- Corrigido: as telas da V4 usavam classes de estilo que não existiam no CSS (cartao, suave, botao, aviso, numeros, rolagem, acoes...). Agora estão todas definidas: cartões, tabelas, botões e alertas ficam estilizados.
- Tela "Pedido recebido" (cliente) com cartão centralizado.
- Nenhuma mudança em models, views, urls ou migrações: não precisa migrar banco.

## Como colocar a foto
Salve a foto como `gestao/static/gestao/img/confeitaria.jpg` (horizontal, ~1600x700 px, até ~300 KB).
Sem o arquivo, o banner mostra um fundo vinho com degradê (não dá erro).
Use foto sua ou de banco gratuito com licença (Unsplash, Pexels).

## Atualização no GitHub
Envie o conteúdo desta pasta para a raiz do repositório (mesmo processo da V4) e faça o commit. O Render faz o deploy sozinho.
Arquivos alterados: base.html, gestao_base.html (novo), central, estoque, financeiro, form_simples, novo_produto, produtos_gestao, producao, enviado.
