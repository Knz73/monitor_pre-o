import time 
from database import carregar_produtos, adicionar_produto
from scraper.core import pegar_preco, buscar_resultados_por_nome, validar_original_por_nome

def menu():
    print("\n==== Monitor de Preços ====")
    print("1 - Adicionar produto")
    print("2 - Verificar preços")
    print("3 - Monitorar automaticamente")
    print("0 - Sair")


def adicionar():
    nome = input("Nome do produto: ")
    modo = input("Deseja informar URL ou buscar pelo nome? (u/b): ").strip().lower()

    if modo == "b":
        site_escolha = input("Buscar em (1) Mercado Livre, (2) Amazon, (3) Shopee): ").strip()
        site_map = {"1": "mercadolivre", "2": "amazon", "3": "shopee"}
        site = site_map.get(site_escolha, "mercadolivre")
        print(f"🔎 Buscando produtos em {site.replace('_', ' ').title()}...")
        resultados = buscar_resultados_por_nome(nome, site)

        if not resultados and site != "mercadolivre":
            print(f"⚠️ Não foi possível obter resultados de {site.replace('_', ' ').title()}. Tentando Mercado Livre...")
            resultados = buscar_resultados_por_nome(nome, "mercadolivre")
            if resultados:
                site = "mercadolivre"

        if resultados:
            print("\nResultados encontrados:")
            for i, item in enumerate(resultados, start=1):
                price_text = item.get("price") or "sem preço"
                print(f"{i}. {item['title']} - {price_text}")

            escolha = input("Escolha o número do item correto (0 para digitar URL manualmente): ").strip()
            if escolha.isdigit() and 1 <= int(escolha) <= len(resultados):
                produto = resultados[int(escolha) - 1]
                url = produto["url"]
                print(f"✅ URL selecionada: {url}")

                original = validar_original_por_nome(nome, produto["title"])
                if original is False:
                    print("⚠️ O título selecionado não parece corresponder ao nome informado. Marcando como NÃO original.")
                elif original is None:
                    original_input = input("Não consegui ter certeza se é original. Deseja marcar como original? (s/n): ").strip().lower()
                    original = original_input == "s"
                else:
                    original_input = input("Parece corresponder ao nome. Marcar como original? (s/n) [s]: ").strip().lower()
                    original = (original_input != "n")
            else:
                url = input("URL: ")
                original_input = input("Produto é original? (s/n): ").strip().lower()
                original = original_input == "s"
        else:
            print("❌ Não foi possível encontrar resultados. Informe a URL manualmente.")
            url = input("URL: ")
            original_input = input("Produto é original? (s/n): ").strip().lower()
            original = original_input == "s"
    else:
        url = input("URL: ")
        original_input = input("Produto é original? (s/n): ").strip().lower()
        original = original_input == "s"

    preco_desejado = float(input("Preço desejado: "))
    adicionar_produto(nome, url, preco_desejado, original)
    print("✅ Produto adicionado!")


def verificar():
    produtos = carregar_produtos()

    if not produtos:
        print("Nenhum produto cadastrado.")
        return
    
    for p in produtos:
        if not p.get("original", True):
            print(f"\n⛔ {p['nome']} - ignorado porque não é original")
            continue

        print(f"\n🔎 {p['nome']}")

        preco_atual = pegar_preco(p["url"])

        if preco_atual:
            print(f"💰 Preço atual: R${preco_atual}")

            if preco_atual <= p["preco_desejado"]:
                print("🔥 PREÇO BAIXOU! COMPRAR!")
            else:
                print("⏳ Ainda está caro...")
        else:
            print("❌ Erro ao pegar preço")

def monitorar():
    while True:
        verificar()
        print("\n⏱️ Aguardando 5 minutos...\n")
        time.sleep(300)


# Loop Principal
while True:
    menu()
    op = input("Escolha: ")

    if op == "1":
        adicionar()
    elif op == "2":
        verificar()
    elif op == "3":
        monitorar()
    elif op == "0":
        break
    else:
        print("Opção invalida")