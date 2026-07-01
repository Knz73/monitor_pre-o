import json
import os
import sys
import logging

Arquivo = "produtos.json"
LockFile = Arquivo + ".lock"
logger = logging.getLogger(__name__)

if sys.platform == "win32":
    import msvcrt

    def file_lock(f):
        msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)

    def file_unlock(f):
        msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
else:
    import fcntl

    def file_lock(f):
        fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)

    def file_unlock(f):
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)

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
    with open(LockFile, "w") as lock:
        try:
            file_lock(lock)
            with open(Arquivo, "w", encoding="utf-8") as f:
                json.dump(produtos, f, indent=4, ensure_ascii=False)
        except BlockingIOError:
            logger.warning("Lock de concorrencia ao salvar produtos")
        finally:
            try:
                file_unlock(lock)
            except Exception:
                pass


def adicionar_produto(nome, url, preco_desejado, original=True, imagem=None):
    produtos = carregar_produtos()

    produtos.append({
        "nome": nome,
        "url": url,
        "preco_desejado": preco_desejado,
        "original": original,
        "imagem": imagem
    })

    salvar_produtos(produtos)


def atualizar_produto(indice, **kwargs):
    produtos = carregar_produtos()
    if 0 <= indice < len(produtos):
        produtos[indice].update(kwargs)
        salvar_produtos(produtos)
        return True
    return False