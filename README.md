# Monitor de Preços

Aplicação para monitoramento de preços de produtos em sites de e-commerce brasileiros (Mercado Livre, Amazon e Shopee). Possui interface web e linha de comando.

## Funcionalidades

- **Interface web** (Flask + Tailwind CSS)
- **Interface CLI** interativa
- **Busca automática** de produtos por nome
- **Validação de originalidade** do produto por similaridade de título
- **Verificação de preços** em paralelo com ThreadPoolExecutor
- **Fallback para Playwright** quando scraping tradicional falha
- **Proteção CSRF** no formulário de cadastro
- **Notificação visual** quando o preço desejado é atingido
- **Armazenamento local** em `produtos.json`

## Pré-requisitos

- Python 3.9+
- Chromium (instalado automaticamente pelo Playwright)

## Instalação

```bash
git clone https://github.com/Knz73/monitor_pre-o.git
cd monitor_pre-o

pip install -r requirements.txt
python -m playwright install chromium
```

## Configuração

Variável de ambiente opcional:

```bash
set SECRET_KEY=sua-chave-secreta-aqui
```

Sem essa variável, a aplicação usa uma chave de desenvolvimento.

## Uso

### Interface web

```bash
python app.py
```

Acesse `http://localhost:5000`

### Interface CLI

```bash
python main.py
```

Menu:
- **1** — Adicionar produto (manual ou busca por nome)
- **2** — Verificar preços dos produtos cadastrados
- **3** — Monitorar automaticamente (a cada 5 minutos)
- **4** — Listar produtos cadastrados
- **0** — Sair

## Estrutura do projeto

```
├── app.py                      # Servidor Flask
├── main.py                     # Interface CLI
├── database.py                 # Operações com produtos.json
├── scraper/
│   ├── core.py                 # Lógica de scraping e routing
│   ├── mercado_livre.py        # Parser Mercado Livre
│   ├── amazon.py               # Parser Amazon
│   ├── shopee.py               # Parser Shopee
│   └── playwright_scraper.py   # Fallback headless browser
├── templates/
│   ├── index.html              # Página inicial (grid de produtos)
│   ├── adicionar.html          # Formulário de cadastro
│   └── verificar.html          # Página de verificação
└── requirements.txt
```

## Tecnologias

- **Flask** — servidor web
- **Flask-WTF** — proteção CSRF e validação de forms
- **BeautifulSoup** — parsing HTML
- **Playwright** — scraping em páginas com JavaScript
- **requests** — requisições HTTP

## Observações

- Scrapers dependem da estrutura HTML dos sites, que pode mudar sem aviso.
- Playwright é usado como fallback apenas quando o scraping tradicional não encontra preço.
- A verificação paralela usa até 4 workers simultâneos.
