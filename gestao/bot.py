def responder(texto,produtos,dias_antecedencia,link_pedido,nome_loja):
    t=(texto or '').lower().strip()
    if any(x in t for x in ['cardápio','cardapio','preço','preco']):
        itens='\n'.join(f'- {p.nome}: R$ {p.preco:.2f}' for p in produtos)
        return f'{nome_loja}\n{itens}\n\nFaça seu pedido em: {link_pedido}'
    if 'prazo' in t or 'anteced' in t: return f'Trabalhamos com pelo menos {dias_antecedencia} dias de antecedência.'
    return f'Olá! Sou o assistente da {nome_loja}. Posso informar cardápio, preços e prazo. Para pedir: {link_pedido}'
