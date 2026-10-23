# Doce Encanto — V6 WhatsApp

## O que mudou
- Botão flutuante "WhatsApp" nas páginas públicas e botão "Chamar no WhatsApp" no topo do cardápio, com mensagem inicial pronta.
- Depois de enviar a encomenda, o cliente vê o resumo e um botão "Enviar meu pedido pelo WhatsApp": a confeiteira recebe nome, data, itens e total já escritos.
- Na gestão (Encomendas e Central) cada pedido tem o botão "WhatsApp do cliente", com mensagem pronta que muda conforme a situação: recebido, confirmado ou pronto.
- Usa links wa.me: sem API, sem custo. O WhatsApp abre com o texto pronto e a pessoa só toca em enviar.

## Configuração obrigatória (Render)
No painel do Render, em Environment, crie a variável:
    WHATSAPP_LOJA = 55 + DDD + número, só números. Exemplo: 5534999998888
Salve e aguarde o deploy. Sem essa variável, os botões do WhatsApp não aparecem (o site continua funcionando).
Opcional: NOME_MARCA (padrão "Doce Encanto").

## Arquivos
Novos: gestao/whatsapp.py, gestao/context_processors.py, gestao/templatetags/ (2 arquivos)
Alterados: config/settings.py, gestao/views.py, render.yaml, base.html, cardapio.html, enviado.html, producao.html, central.html, gestao_base.html
Sem mudança em models ou migrações: não precisa migrar o banco.
