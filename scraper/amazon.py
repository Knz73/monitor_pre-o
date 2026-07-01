import logging
import re

logger = logging.getLogger(__name__)


def preco_amazon(soup):
    selectors = [
        "span.a-price > span.a-offscreen",
        "span.a-price-whole",
        "span#priceblock_ourprice",
        "span#priceblock_dealprice",
        "span#priceblock_saleprice",
        "span.a-color-price",
    ]

    for selector in selectors:
        preco = soup.select_one(selector)
        if preco and preco.text.strip():
            texto = preco.text.replace(".", "").replace(",", ".").replace("R$", "").replace("US$", "").strip()
            texto = re.sub(r"[^\d.,]", "", texto)
            if texto:
                try:
                    return float(texto.replace(",", "."))
                except ValueError:
                    continue

    logger.warning("Preco nao encontrado na pagina da Amazon")
    return None