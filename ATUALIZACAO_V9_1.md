# V9.1 — navegação por categorias e ajustes de visual

- Corrigida a sobreposição do título com a foto no banner em larguras de notebook; estilos responsivos.
- Cada categoria visual agora é um botão que abre apenas os produtos daquela categoria, sem recarregar a página.
- Seleções e quantidades permanecem preenchidas ao mudar de categoria. A encomenda permanece um único formulário com validações originais do servidor.
- Novo campo **Categoria do cardápio** em Produtos (Gestão e /admin/), para atribuir brigadeiros, doces especiais, brownies, bolos e kits.
- A migração 0007 classifica os produtos existentes por nome/tipo. Revise categorias individualmente após publicar, especialmente produtos com nomes criativos ou pouco descritivos. Uma categoria sem produtos mostra uma mensagem, sem inventar itens.
- Removidos os botões de quantidade rápida (redundantes com campo numérico e controles), a segunda chamada do banner, atalhos de avaliações vazias e acompanhamento sem busca, preservando o link individual gerado após encomenda.
- Rodapé corrigido de Doce Encanto para D.Chiica.

## Publicação Render

1. Faça backup do banco de dados, arquivos de mídia e configuração.
2. Atualize os arquivos no repositório Git que o Render utiliza.
3. Confirme que o comando do build executa `python manage.py migrate` e `python manage.py collectstatic --noinput`.
4. Faça deploy e confira se a migração 0007 foi concluída.
5. Acesse Gestão > Produtos ou /admin/ e corrija a categoria de cada produto onde necessário.
6. Teste categorias, atualização de quantidades, total estimado, criação de pedidos, administração e mobile.

Não substitua o banco de dados em produção. A versão usa os mesmos pedidos já registrados.
