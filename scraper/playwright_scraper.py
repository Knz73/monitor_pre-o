import logging
import re
from urllib.parse import quote_plus

from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)


def _extrair_preco_mercadolivre(page):
    try:
        page.wait_for_selector("span.andes-money-amount__fraction", timeout=10000)
        texto = page.locator("span.andes-money-amount__fraction").first.inner_text()
        return _parse_preco(texto)
    except Exception as e:
        logger.debug("Falha ao extrair preco Mercado Livre via Playwright: %s", e)
    return None


def _extrair_preco_amazon(page):
    try:
        page.wait_for_selector("span.a-price > span.a-offscreen", timeout=10000)
        texto = page.locator("span.a-price > span.a-offscreen").first.inner_text()
        return _parse_preco(texto)
    except Exception as e:
        logger.debug("Falha ao extrair preco Amazon via Playwright: %s", e)
    return None


def _extrair_preco_shopee(page):
    try:
        page.wait_for_selector("span._1w9jLIQ, span._341bFJ7", timeout=10000)
        texto = page.locator("span._1w9jLIQ, span._341bFJ7").first.inner_text()
        return _parse_preco(texto)
    except Exception as e:
        logger.debug("Falha ao extrair preco Shopee via Playwright: %s", e)
    return None


def _parse_preco(texto):
    if not texto:
        return None
    texto = texto.replace("R$", "").replace("US$", "").replace("\n", " ").strip()
    texto = re.sub(r"[^\d,]", "", texto)
    texto = texto.replace(".", "").replace(",", ".")
    if texto:
        try:
            return float(texto)
        except ValueError:
            pass
    return None


def _identificar_site(url):
    dominio = url.lower()
    if "mercadolivre" in dominio:
        return "mercadolivre"
    if "amazon" in dominio:
        return "amazon"
    if "shopee" in dominio:
        return "shopee"
    return None


EXTRAIDORES = {
    "mercadolivre": _extrair_preco_mercadolivre,
    "amazon": _extrair_preco_amazon,
    "shopee": _extrair_preco_shopee,
}


def pegar_preco_playwright(url, headless=True):
    site = _identificar_site(url)
    extrator = EXTRAIDORES.get(site)
    if not extrator:
        logger.debug("Site nao suportado para Playwright: %s", url)
        return None

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=headless)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
                locale="pt-BR",
            )
            page = context.new_page()
            page.set_extra_http_headers({"Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8"})
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(2000)
            preco = extrator(page)
            browser.close()
            return preco
    except Exception as e:
        logger.warning("Erro no scraping com Playwright de %s: %s", url, e)
        return None
