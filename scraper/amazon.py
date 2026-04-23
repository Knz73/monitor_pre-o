def preco_amazon(soup):
    selectors = [
        "span#priceblock_ourprice",
        "span#priceblock_dealprice",
        "span#priceblock_saleprice",
        "span.a-price > span.a-offscreen",
        "span.a-price-whole"
    ]

    for selector in selectors:
        preco = soup.select_one(selector)
        if preco and preco.text.strip():
            texto = preco.text.replace(".", "").replace(",", ".").replace("R$", "").replace("US$", "")
            try:
                return float(texto.strip())
            except ValueError:
                continue

    return None