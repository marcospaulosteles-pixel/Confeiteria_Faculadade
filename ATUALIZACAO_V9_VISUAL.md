# Atualização V9 — identidade visual (Render)

Esta versão mantém os fluxos, URLs, banco de dados, configurações de hospedagem e regras de negócio da V8.

## Mudanças
- Rótulos visíveis “Gestão V8” atualizados para “Gestão” (menu administrativo e central).
- Paleta marrom (#744131 e #44271f), rosa (#fae8ed, #a04c69) e branco quente (#fffaf7).
- Banner da página inicial com imagem ilustrativa da vitrine de doces; banner da Gestão utiliza a mesma imagem local.
- Refinamentos de botões, cartões, tipografia, estados de foco e layout responsivo.
- Nenhum campo, modelo, migração ou cálculo foi modificado.

## Imagem
`gestao/static/gestao/img/vitrine_doces_v9.webp` é uma imagem ilustrativa gerada por IA, **não uma fotografia dos produtos reais da empreendedora**. Recomenda-se substituí-la por uma foto própria para representar fielmente os doces; pode-se substituir o arquivo pelo mesmo nome.

## Publicação no Render
1. Faça backup de banco de dados e mídias de produção antes da publicação.
2. Extraia o projeto e atualize o repositório conectado ao Render (ou publique pelo mesmo fluxo já usado).
3. Mantenha variáveis de ambiente e disco persistente do serviço atual.
4. Execute o mesmo build do projeto (`build.sh` e `render.yaml` sem mudanças).
5. Confira home, cardápio, formulário de encomenda, login da Gestão, relatórios e imagens estáticas.

**Atenção:** implantar novo código pelo Render não transfere automaticamente dados SQLite, arquivos enviados ou configurações privadas; preserve o armazenamento persistente existente.
