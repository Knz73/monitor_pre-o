from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, BooleanField, validators
from urllib.parse import urlparse

from database import carregar_produtos, adicionar_produto
from scraper.core import pegar_preco, buscar_resultados_por_nome

import os
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
app.config["WTF_CSRF_TIME_LIMIT"] = None

executor = ThreadPoolExecutor(max_workers=4)

SITES_PERMITIDOS = {
    "mercadolivre": "mercadolivre.com.br",
    "amazon": "amazon.com.br",
    "shopee": "shopee.com.br",
}


def validar_site(site):
    return site in SITES_PERMITIDOS


class ProdutoForm(FlaskForm):
    nome = StringField("Nome do produto", [validators.InputRequired()])
    url = StringField("URL do produto", [
        validators.InputRequired(),
        validators.URL(),
        validators.Regexp(
            r"https?://(www\.)?(mercadolivre\.com\.br|amazon\.com\.br|shopee\.com\.br)/",
            message="URL deve ser de Mercado Livre, Amazon ou Shopee"
        )
    ])
    preco_desejado = FloatField("Preço alvo", [validators.InputRequired(), validators.NumberRange(min=0)])
    original = BooleanField("Produto original", default=True)
    imagem = StringField("Imagem")


@app.route("/")
def index():
    produtos = carregar_produtos()
    return render_template("index.html", produtos=produtos)


@app.route("/adicionar", methods=["GET", "POST"])
def adicionar():
    form = ProdutoForm()
    mensagem = ""

    if request.method == "POST":
        if not form.validate_on_submit():
            mensagem = "Dados inválidos"
        else:
            try:
                adicionar_produto(
                    form.nome.data.strip(),
                    form.url.data.strip(),
                    form.preco_desejado.data,
                    form.original.data,
                    form.imagem.data.strip() or None,
                )
                mensagem = "Produto adicionado com sucesso!"
                form = ProdutoForm()
            except ValueError:
                mensagem = "Preço inválido"

    return render_template("adicionar.html", form=form, mensagem=mensagem)


@app.route("/buscar")
def buscar():
    nome = request.args.get("nome", "")
    site = request.args.get("site", "mercadolivre")

    if not validar_site(site):
        return jsonify({"erro": "Site nao permitido"}), 400

    resultados = buscar_resultados_por_nome(nome, site) if nome else []
    return jsonify(resultados)

def verificar_produtos(produtos):
    resultados = []
    futures = {executor.submit(pegar_preco, p["url"]): p for p in produtos}
    for future in as_completed(futures):
        p = futures[future]
        preco_atual = future.result()
        resultados.append({
            "nome": p["nome"],
            "url": p["url"],
            "preco_desejado": p["preco_desejado"],
            "preco_atual": preco_atual,
            "original": p.get("original", True),
            "imagem": p.get("imagem"),
            "abaixo": preco_atual is not None and preco_atual <= p["preco_desejado"],
            "erro": preco_atual is None,
        })
    return resultados


@app.route("/verificar")
def verificar_page():
    produtos = carregar_produtos()
    resultados = verificar_produtos(produtos) if produtos else []
    return render_template("verificar.html", produtos=resultados)


@app.route("/verificar/api")
def verificar():
    produtos = carregar_produtos()
    resultados = verificar_produtos(produtos) if produtos else []
    return jsonify(resultados)

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)