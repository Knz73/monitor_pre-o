import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, urlparse

from .mercado_livre import preco_mercado_livre
from .amazon import preco_amazon
from .shopee import preco_shopee
from .playwright_scraper import pegar_preco_playwright

logger = logging.getLogger(__name__)

def pegar_html(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Referer": "https://www.google.com/"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.text
    except Exception as e:
        logger.warning("Erro ao buscar %s: %s", url, e)

    return None

def extrair_preco_texto(texto):
    if not texto:
        return None
    preco = texto.replace("R$", "").replace("US$", "").replace("\n", " ").strip()
    return preco if preco else None


def buscar_resultados_mercado_livre(query, max_results=5):
    search = quote_plus(query)
    url = f"https://lista.mercadolivre.com.br/{search}"
    html = pegar_html(url)
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    resultados = []

    for item in soup.select("a.ui-search-link"):
        href = item.get("href")
        if not href:
            continue

        title = item.get_text(strip=True)
        price_tag = item.select_one("span.price-tag-fraction") or item.select_one("span.price-tag-text-sr-only")
        price = extrair_preco_texto(price_tag.text if price_tag else None)
        img_tag = item.select_one("img")
        imagem = img_tag.get("data-src") or img_tag.get("src") if img_tag else None

        if title and href not in [r["url"] for r in resultados]:
            resultados.append({"title": title, "url": href, "price": price, "imagem": imagem})
            if len(resultados) >= max_results:
                break

    return resultados


def buscar_resultados_amazon(query, max_results=5):
    search = quote_plus(query)
    url = f"https://www.amazon.com.br/s?k={search}"
    html = pegar_html(url)
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    resultados = []

    for item in soup.select("div[data-component-type='s-search-result']"):
        link = item.select_one("h2 a") or item.select_one("h2 a.a-link-normal")
        if not link or not link.get("href"):
            continue

        href = link["href"]
        if not href.startswith("http"):
            href = "https://www.amazon.com.br" + href

        title = link.get_text(strip=True)
        price_tag = item.select_one("span.a-price > span.a-offscreen")
        price = extrair_preco_texto(price_tag.text if price_tag else None)
        img_tag = item.select_one("img.s-image")
        imagem = img_tag.get("src") if img_tag else None

        if title and href not in [r["url"] for r in resultados]:
            resultados.append({"title": title, "url": href, "price": price, "imagem": imagem})
            if len(resultados) >= max_results:
                break

    return resultados


def buscar_resultados_shopee(query, max_results=5):
    search = quote_plus(query)
    url = f"https://shopee.com.br/search?keyword={search}"
    html = pegar_html(url)
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    resultados = []

    for item in soup.select("a[href*='/product/']"):
        href = item.get("href")
        if not href or "/shop/" in href:
            continue

        title = item.get_text(strip=True)
        price_tag = item.select_one("span._1w9jLIQ") or item.select_one("span._341bFJ7")
        price = extrair_preco_texto(price_tag.text if price_tag else None)
        img_tag = item.select_one("img")
        imagem = img_tag.get("src") if img_tag else None

        if href.startswith("/"):
            href = "https://shopee.com.br" + href

        if title and href not in [r["url"] for r in resultados]:
            resultados.append({"title": title, "url": href, "price": price, "imagem": imagem})
            if len(resultados) >= max_results:
                break

    return resultados


def buscar_resultados_por_nome(nome, site="mercadolivre", max_results=5):
    if site == "amazon":
        return buscar_resultados_amazon(nome, max_results)
    elif site == "shopee":
        return buscar_resultados_shopee(nome, max_results)
    return buscar_resultados_mercado_livre(nome, max_results)


def buscar_url_por_nome(nome, site="mercadolivre"):
    resultados = buscar_resultados_por_nome(nome, site, max_results=1)
    return resultados[0]["url"] if resultados else None


def normalizar_texto(texto):
    return " ".join(
        palavra for palavra in
        "".join(c.lower() if c.isalnum() else " " for c in texto).split()
        if len(palavra) > 2
    )


def validar_original_por_nome(nome, titulo):
    nome_tokens = set(normalizar_texto(nome).split())
    titulo_tokens = set(normalizar_texto(titulo).split())
    if not nome_tokens or not titulo_tokens:
        return None

    comuns = nome_tokens.intersection(titulo_tokens)
    ratio = len(comuns) / min(len(nome_tokens), len(titulo_tokens))
    if ratio >= 0.6:
        return True
    if ratio <= 0.3:
        return False
    return None

def identificar_site(url):
    dominio = urlparse(url).netloc

    if "mercadolivre" in dominio:
        return "mercado_livre"
    elif "amazon" in dominio:
        return "amazon"
    elif "shopee" in dominio:
        return "shopee"
    else:
        return "desconhecido"
    

def pegar_preco(url):
    html = pegar_html(url)

    if not html:
        logger.info("Scraping tradicional falhou, tentando Playwright para %s", url)
        return pegar_preco_playwright(url)

    soup = BeautifulSoup(html, "html.parser")
    site = identificar_site(url)

    if site == "mercado_livre":
        preco = preco_mercado_livre(soup)
    
    elif site == "amazon":
        preco = preco_amazon(soup)
    
    elif site == "shopee":
        preco = preco_shopee(soup)
    
    else:
        return None

    if preco is None:
        logger.info("Preco nao encontrado no scraping tradicional, tentando Playwright para %s", url)
        return pegar_preco_playwright(url)

    return preco