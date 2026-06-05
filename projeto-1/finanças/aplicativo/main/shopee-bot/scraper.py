import time
import random
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

from config import (
    URL_BASE, MAX_PAGES, REQUEST_DELAY, VERBOSE,
    USER_AGENTS, get_affiliate_url, CATEGORIAS, DOMAIN
)


def criar_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument(f"user-agent={random.choice(USER_AGENTS)}")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        """
    })

    return driver


def log(mensagem):
    if VERBOSE:
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"  [{timestamp}] {mensagem}")


def scroll_pagina(driver, vezes=5):
    for i in range(vezes):
        driver.execute_script(f"window.scrollBy(0, 800);")
        time.sleep(1)


def extrair_produtos_pagina(driver):
    produtos = []

    time.sleep(3)

    scroll_pagina(driver, 6)

    soup = BeautifulSoup(driver.page_source, "lxml")

    seletores_produtos = [
        "div.shopee-search-item-result__item",
        "div.col-xs-2-4",
        "div[data-sqe='item']",
        "a[data-sqe='link']",
    ]

    itens = []
    for seletor in seletores_produtos:
        itens = soup.select(seletor)
        if itens:
            break

    if not itens:
        itens = soup.find_all("div", class_=lambda x: x and "item" in x.lower())

    log(f"Encontrados {len(itens)} itens na pagina")

    for item in itens:
        try:
            produto = extrair_dados_produto(item)
            if produto and produto.get("titulo"):
                produtos.append(produto)
        except Exception as e:
            if VERBOSE:
                log(f"Erro ao extrair produto: {e}")
            continue

    return produtos


def extrair_dados_produto(item):
    produto = {}

    titulo_elem = (
        item.select_one("div[data-sqe='name']") or
        item.select_one("div.shopee-search-item-result__item-name") or
        item.select_one("div._1NoI8_") or
        item.select_one("a div div") or
        item.find("div", class_=lambda x: x and "name" in x.lower() if x else False)
    )
    if titulo_elem:
        produto["titulo"] = titulo_elem.get_text(strip=True)

    link_elem = (
        item.select_one("a[data-sqe='link']") or
        item.select_one("a.shopee-search-item-result__item") or
        item.find("a", href=True)
    )
    if link_elem:
        url = link_elem.get("href", "")
        if url.startswith("/"):
            url = f"https://{DOMAIN}{url}"
        produto["url_original"] = url
        produto["url_afiliado"] = get_affiliate_url(url)

    produto_id = None
    if "/i." in produto.get("url_original", ""):
        try:
            parts = produto["url_original"].split("/i.")
            if len(parts) > 1:
                produto_id = parts[1].split(".")[0]
        except Exception:
            pass
    produto["produto_id"] = produto_id or ""

    preco_original = None
    preco_desconto = None

    price_elems = item.select("span")
    precos = []
    for p in price_elems:
        texto = p.get_text(strip=True)
        if "R$" in texto or texto.replace(".", "").replace(",", "").isdigit():
            valor = parse_preco(texto)
            if valor and valor > 0:
                precos.append(valor)

    if len(precos) >= 2:
        preco_original = max(precos)
        preco_desconto = min(precos)
    elif len(precos) == 1:
        preco_desconto = precos[0]

    price_current = (
        item.select_one("span._1w9jLI") or
        item.select_one("span.price") or
        item.select_one("div._245-SC")
    )
    if price_current:
        valor = parse_preco(price_current.get_text(strip=True))
        if valor:
            preco_desconto = valor

    price_original = (
        item.select_one("span._1w9jLI._1DGuEV") or
        item.select_one("span.original-price") or
        item.select_one("del")
    )
    if price_original:
        valor = parse_preco(price_original.get_text(strip=True))
        if valor:
            preco_original = valor

    if preco_original and preco_desconto and preco_original > preco_desconto:
        desconto = ((preco_original - preco_desconto) / preco_original) * 100
        produto["porcentagem_desconto"] = round(desconto, 1)
    else:
        produto["porcentagem_desconto"] = None

    produto["preco_original"] = preco_original
    produto["preco_desconto"] = preco_desconto

    img_elem = (
        item.select_one("img") or
        item.select_one("div.image-placeholder")
    )
    if img_elem:
        produto["imagem_url"] = img_elem.get("src") or img_elem.get("data-src", "")

    sold_elem = (
        item.select_one("div._245-SC") or
        item.select_one("span.sold") or
        item.find("div", string=lambda x: x and "vendido" in x.lower() if x else False)
    )
    if sold_elem:
        texto = sold_elem.get_text(strip=True)
        produto["vendidos"] = parse_vendidos(texto)
    else:
        produto["vendidos"] = None

    rating_elem = (
        item.select_one("div.shopee-rating-stars") or
        item.select_one("div.rating")
    )
    if rating_elem:
        stars = rating_elem.select("div.shopee-rating-stars__lit")
        produto["avaliacoes"] = len(stars) if stars else None
    else:
        produto["avaliacoes"] = None

    produto["especificacoes"] = extrair_especificacoes(item)

    produto["categoria"] = detectar_categoria(produto.get("titulo", ""))

    produto["vendedor"] = ""
    produto["localizacao"] = ""

    produto["data_coleta"] = datetime.now().isoformat()

    return produto


def parse_preco(texto):
    if not texto:
        return None

    texto = texto.replace("R$", "").replace(" ", "").strip()
    texto = texto.replace(".", "").replace(",", ".")

    texto = "".join(c for c in texto if c.isdigit() or c == ".")

    try:
        valor = float(texto)
        return valor if valor > 0 else None
    except ValueError:
        return None


def parse_vendidos(texto):
    if not texto:
        return None

    texto = texto.lower().strip()
    texto = texto.replace("vendidos", "").replace("vendido", "").strip()

    if "k" in texto:
        texto = texto.replace("k", "").strip()
        try:
            return int(float(texto) * 1000)
        except ValueError:
            return None

    try:
        return int(texto)
    except ValueError:
        return None


def extrair_especificacoes(item):
    specs = []

    spec_elems = item.select("div.shopee-search-item-result__item-characteristics")
    if not spec_elems:
        spec_elems = item.select("div._245-SC")

    for spec in spec_elems:
        texto = spec.get_text(strip=True)
        if texto and "vendido" not in texto.lower():
            specs.append(texto)

    return " | ".join(specs) if specs else ""


def detectar_categoria(titulo):
    titulo_lower = titulo.lower()

    categorias_map = {
        "celular": ["celular", "smartphone", "iphone", "samsung galaxy", "motorola", "xiaomi", "redmi"],
        "computador": ["notebook", "computador", "pc", "desktop", "macbook", "chromebook", "mac"],
        "monitor": ["monitor", "tela", "display", "ultrawide"],
        "tv": ["tv", "televisao", "smart tv", "led tv", "oled", "qled"],
        "audio": ["fone", "headphone", "caixa de som", "bluetooth", "airpods", "audifono", "speaker"],
        "gaming": ["gamer", "xbox", "playstation", "ps5", "ps4", "nintendo", "controle", "game"],
        "eletrodomesticos": ["geladeira", "microondas", "lavadora", "aspirador", "air fryer", "cafeteira"],
        "casa": ["ventilador", "ar condicionado", "luminaria", "cadeira", "mesa", "decoracao"],
        "esportes": ["bicicleta", "esteira", "halteres", "bola", "esportivo", "fitness"],
        "beleza": ["maquiagem", "cabelo", "pele", "perfume", "skincare", "batom"],
        "automotivo": ["carro", "moto", "pneu", "oleo", "acessorio automotivo", "led automotivo"],
        "ferramentas": ["furadeira", "parafusadeira", "serra", "ferramenta", "multimetro"],
        "moda": ["camisa", "calca", "vestido", "tenis", "sapato", "bolsa", "relogio"],
    }

    for categoria, palavras in categorias_map.items():
        for palavra in palavras:
            if palavra in titulo_lower:
                return categoria

    return "geral"


def scraping_pagina(driver, url, max_paginas=None):
    if max_paginas is None:
        max_paginas = MAX_PAGES

    todos_produtos = []

    log(f"Acessando: {url}")

    try:
        driver.get(url)
        time.sleep(REQUEST_DELAY)

        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.shopee-search-item-result__item, div.col-xs-2-4, div[data-sqe='item']"))
            )
        except TimeoutException:
            log("Timeout aguardando produtos carregarem")

        for pagina in range(1, max_paginas + 1):
            log(f"Scraping pagina {pagina}/{max_paginas}")

            produtos = extrair_produtos_pagina(driver)
            todos_produtos.extend(produtos)

            if pagina < max_paginas:
                try:
                    next_btn = driver.find_element(
                        By.CSS_SELECTOR,
                        "button.shopee-icon-button--right, a.btn-next"
                    )
                    driver.execute_script("arguments[0].click();", next_btn)
                    time.sleep(REQUEST_DELAY)
                except NoSuchElementException:
                    log("Nao ha mais paginas")
                    break

    except Exception as e:
        log(f"Erro ao acessar pagina: {e}")

    return todos_produtos


def scraping_ofertas_do_dia(driver, max_paginas=None):
    url = f"{URL_BASE}/daily_discover"
    return scraping_pagina(driver, url, max_paginas)


def scraping_flash_sale(driver):
    url = f"{URL_BASE}/flash_sale"
    return scraping_pagina(driver, url, 1)


def scraping_categoria(driver, categoria_nome, categoria_url, max_paginas=None):
    log(f"Scraping categoria: {categoria_nome}")
    produtos = scraping_pagina(driver, categoria_url, max_paginas)

    for p in produtos:
        if not p.get("categoria") or p["categoria"] == "geral":
            p["categoria"] = categoria_nome

    return produtos


def scraping_completo(categorias_selecionadas=None):
    driver = criar_driver()
    todos_produtos = []

    try:
        log("Iniciando scraping completo da Shopee...")

        try:
            driver.get(URL_BASE)
            time.sleep(3)
            log("Site da Shopee acessado com sucesso")
        except Exception as e:
            log(f"Aviso ao acessar site: {e}")

        produtos_ofertas = scraping_ofertas_do_dia(driver)
        todos_produtos.extend(produtos_ofertas)
        log(f"Ofertas do dia: {len(produtos_ofertas)} produtos")

        produtos_flash = scraping_flash_sale(driver)
        todos_produtos.extend(produtos_flash)
        log(f"Flash Sale: {len(produtos_flash)} produtos")

        if categorias_selecionadas:
            for nome_cat, url_cat in CATEGORIAS.items():
                if nome_cat in categorias_selecionadas and nome_cat not in ["ofertas-do-dia", "flash-sale"]:
                    produtos_cat = scraping_categoria(driver, nome_cat, url_cat)
                    todos_produtos.extend(produtos_cat)
                    log(f"Categoria {nome_cat}: {len(produtos_cat)} produtos")
        else:
            categorias_padrao = ["tecnologia", "celulares", "beleza"]
            for nome_cat in categorias_padrao:
                if nome_cat in CATEGORIAS:
                    produtos_cat = scraping_categoria(driver, nome_cat, CATEGORIAS[nome_cat])
                    todos_produtos.extend(produtos_cat)
                    log(f"Categoria {nome_cat}: {len(produtos_cat)} produtos")

    finally:
        driver.quit()

    produtos_unicos = remover_duplicatas(todos_produtos)
    log(f"Total final: {len(produtos_unicos)} produtos unicos")

    return produtos_unicos


def remover_duplicatas(produtos):
    ids_vistos = set()
    urls_vistas = set()
    produtos_unicos = []

    for produto in produtos:
        produto_id = produto.get("produto_id", "")
        url = produto.get("url_original", "")

        chave = produto_id or url

        if chave and chave not in ids_vistos and url not in urls_vistas:
            ids_vistos.add(chave)
            urls_vistas.add(url)
            produtos_unicos.append(produto)

    return produtos_unicos
