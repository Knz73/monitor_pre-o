import logging

logger = logging.getLogger(__name__)


def preco_mercado_livre(soup):
    preco = soup.find("span", class_="andes-money-amount__fraction")

    if preco:
        texto = preco.text.replace(".", "").replace(",", ".").strip()
        try:
            return float(texto)
        except ValueError:
            logger.warning("Formato de preco invalido no Mercado Livre: %s", preco.text)

    logger.warning("Preco nao encontrado na pagina do Mercado Livre")
    return None
