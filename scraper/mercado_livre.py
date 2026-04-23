def preco_mercado_livre(soup):
    preco = soup.find("span", class_="andes-money-amount__fraction")

    if preco:
        texto = preco.text.replace(".", "").replace(",", ".")
        return float(texto)

    return None
