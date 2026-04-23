import json
import os

Arquivo = "produtos.json"

def carregar_produtos():
    if not os.path.exists(Arquivo):
        return []
    
    with open(Arquivo, "r", encoding="utf-8") as f:
        conteudo = f.read().strip()
        if not conteudo:
            return []
        try:
            return json.loads(conteudo)
        except json.JSONDecodeError:
            return []

def salvar_produtos(produtos):
    with open(Arquivo, "w", encoding="utf-8") as f:
        json.dump(produtos, f, indent=4, ensure_ascii=False)
        
def adicionar_produto(nome, url, preco_desejado, original=True):
    produtos = carregar_produtos()

    produtos.append({
        "nome": nome,
        "url": url,
        "preco_desejado": preco_desejado,
        "original": original
    })

    salvar_produtos(produtos)