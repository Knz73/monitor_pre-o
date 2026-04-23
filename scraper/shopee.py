def preco_shopee(soup):
    spans = soup.find_all("span")

    for span in spans:
        texto = span.text.strip()

        if "R$" in texto:
            texto = texto.replace("R$", "").replace(".", "").replace(",", ".")
            try:
                return float(texto)
            except:
                continue

    return None