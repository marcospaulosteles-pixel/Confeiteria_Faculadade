# Confeitaria Django — versão para Render

Esta versão foi preparada para publicação no Render com Django, Gunicorn, WhiteNoise e PostgreSQL.

## 1. Colocar no GitHub
Crie um repositório novo no GitHub e envie TODO o conteúdo desta pasta para a raiz do repositório. O arquivo `render.yaml` precisa ficar na raiz.

## 2. Publicar no Render com Blueprint
1. Entre no Render e conecte sua conta do GitHub.
2. Abra **Blueprints** > **New Blueprint Instance**.
3. Escolha o repositório deste projeto.
4. O Render lerá `render.yaml` e criará o site e o banco PostgreSQL.
5. Quando solicitado, informe:
   - `DJANGO_SUPERUSER_USERNAME`: nome do administrador (ex.: admin)
   - `DJANGO_SUPERUSER_PASSWORD`: crie uma senha forte
   - `DJANGO_SUPERUSER_EMAIL`: seu e-mail (opcional)
6. Clique para aplicar/criar o Blueprint e aguarde o deploy.
7. Abra a URL `https://...onrender.com` fornecida pelo Render.
8. Administração: acrescente `/admin/` ao endereço do site.

## 3. Endereços do sistema
- `/` — cardápio e pedidos
- `/painel/` — painel (login de administrador)
- `/producao/` — produção (login de administrador)
- `/admin/` — cadastros e administração

## Observações sobre o plano gratuito
O serviço gratuito pode entrar em repouso após um período sem acessos e demorar para iniciar novamente. O PostgreSQL gratuito do Render tem prazo limitado; consulte a documentação atual do Render antes da apresentação para confirmar as condições.
