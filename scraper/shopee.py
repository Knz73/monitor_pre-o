import logging
import re

logger = logging.getLogger(__name__)


def preco_shopee(soup):
    for item in soup.select("div[data-sqe='item']"):
        price_elem = item.select_one("span._1w9jLIQ") or item.select_one("span._341bFJ7")
        if price_elem:
            texto = price_elem.text.strip()
            if "R$" in texto:
                texto = texto.replace("R$", "").replace(".", "").replace(",", ".")
                texto = re.sub(r"[^\d]", "", texto)
                try:
                    return float(texto) / 100 if len(texto) > 6 else float(texto)
                except ValueError:
                    continue

    logger.warning("Preco nao encontrado na pagina da Shopee")
    return None