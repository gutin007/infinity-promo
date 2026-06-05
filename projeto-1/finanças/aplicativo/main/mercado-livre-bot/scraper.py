import time
import random
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

from config import (
    URL_OFERTAS, MAX_PAGES, REQUEST_DELAY, VERBOSE,
    USER_AGENTS, get_affiliate_url, CATEGORIAS
)


def criar_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument(f"user-agent={random.choice(USER_AGENTS)}")
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


def extrair_produtos_pagina(driver):
    produtos = []

    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "ol.ui-search-layout"))
        )
    except TimeoutException:
        log("Timeout aguardando carregar produtos")
        return produtos

    time.sleep(2)

    soup = BeautifulSoup(driver.page_source, "lxml")

    itens = soup.select("ol.ui-search-layout > li")
    if not itens:
        itens = soup.select("li.ui-search-layout__item")

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
        item.select_one("a.ui-search-link__title-card") or
        item.select_one("h2.ui-search-item__title") or
        item.select_one("a.poly-component__title") or
        item.select_one("h3.poly-component__title")
    )
    if titulo_elem:
        produto["titulo"] = titulo_elem.get_text(strip=True)

    link_elem = (
        item.select_one("a.ui-search-link") or
        item.select_one("a.ui-search-link__title-card") or
        item.select_one("a.poly-component__title")
    )
    if link_elem:
        url = link_elem.get("href", "")
        if url.startswith("//"):
            url = "https:" + url
        produto["url_original"] = url
        produto["url_afiliado"] = get_affiliate_url(url)

    preco_original = None
    preco_desconto = None

    price_old = (
        item.select_one("s.ui-search-price__original-value") or
        item.select_one("span.ui-search-price__original-value") or
        item.select_one("s.poly-price__original") or
        item.select_one("span.poly-price__original")
    )
    if price_old:
        preco_original = parse_preco(price_old.get_text(strip=True))

    price_new = (
        item.select_one("span.ui-search-price__second-line") or
        item.select_one("span.ui-search-price__current-value") or
        item.select_one("span.poly-price__current") or
        item.select_one("span.andes-money-amount__fraction")
    )
    if price_new:
        preco_desconto = parse_preco(price_new.get_text(strip=True))

    if preco_original and preco_desconto and preco_original > 0:
        desconto = ((preco_original - preco_desconto) / preco_original) * 100
        produto["porcentagem_desconto"] = round(desconto, 1)
    else:
        produto["porcentagem_desconto"] = None

    produto["preco_original"] = preco_original
    produto["preco_desconto"] = preco_desconto

    img_elem = (
        item.select_one("img.ui-search-result-image__image") or
        item.select_one("img.poly-component__image") or
        item.select_one("img[data-src]")
    )
    if img_elem:
        produto["imagem_url"] = img_elem.get("src") or img_elem.get("data-src", "")

    produto["especificacoes"] = extrair_especificacoes(item)

    produto["categoria"] = detectar_categoria(produto.get("titulo", ""))

    produto["data_coleta"] = datetime.now().isoformat()

    return produto


def parse_preco(texto):
    if not texto:
        return None

    texto = texto.replace("R$", "").replace(" ", "").strip()
    texto = texto.replace(".", "").replace(",", ".")

    try:
        return float(texto)
    except ValueError:
        return None


def extrair_especificacoes(item):
    specs = []

    specs_elem = item.select("li.ui-search-card-attributes__attribute")
    if not specs_elem:
        specs_elem = item.select("ul.poly-attributes-list > li")

    for spec in specs_elem:
        texto = spec.get_text(strip=True)
        if texto:
            specs.append(texto)

    return " | ".join(specs) if specs else ""


def detectar_categoria(titulo):
    titulo_lower = titulo.lower()

    categorias_map = {
        "celular": ["celular", "smartphone", "iphone", "samsung galaxy", "motorola", "xiaomi"],
        "computador": ["notebook", "computador", "pc", "desktop", "macbook", "chromebook"],
        "monitor": ["monitor", "tela", "display"],
        "tv": ["tv", "televisao", "smart tv", "led tv", "oled"],
        "audio": ["fone", "headphone", "caixa de som", "bluetooth", "airpods", "audifono"],
        "gaming": ["gamer", "xbox", "playstation", "ps5", "ps4", "nintendo", "controle"],
        "eletrodomesticos": ["geladeira", "microondas", "lavadora", "aspirador", "air fryer", "cafeteira"],
        "casa": ["ventilador", "ar condicionado", "luminaria", "cadeira", "mesa"],
        "esportes": ["bicicleta", "esteira", "halteres", "bola", "esportivo"],
        "beleza": ["maquiagem", "cabelo", "pele", "perfume", "skincare"],
        "automotivo": ["carro", "moto", "pneu", "oleo", "acessorio automotivo"],
        "ferramentas": ["furadeira", "parafusadeira", "serra", "ferramenta"],
        "moda": ["camisa", "calca", "vestido", "tenis", "sapato", "bolsa"],
    }

    for categoria, palavras in categorias_map.items():
        for palavra in palavras:
            if palavra in titulo_lower:
                return categoria

    return "geral"


def scraping_ofertas_do_dia(driver, max_paginas=None):
    if max_paginas is None:
        max_paginas = MAX_PAGES

    todos_produtos = []
    url_base = URL_OFERTAS

    log(f"Acessando ofertas do dia: {url_base}")

    try:
        driver.get(url_base)
        time.sleep(REQUEST_DELAY)

        for pagina in range(1, max_paginas + 1):
            log(f"Scraping pagina {pagina}/{max_paginas}")

            produtos = extrair_produtos_pagina(driver)
            todos_produtos.extend(produtos)

            if pagina < max_paginas:
                try:
                    next_btn = driver.find_element(
                        By.CSS_SELECTOR,
                        "a.andes-pagination__link[title='Seguinte']"
                    )
                    next_btn.click()
                    time.sleep(REQUEST_DELAY)
                except NoSuchElementException:
                    log("Nao ha mais paginas")
                    break

    except Exception as e:
        log(f"Erro ao acessar ofertas: {e}")

    return todos_produtos


def scraping_categoria(driver, categoria_nome, categoria_url, max_paginas=None):
    if max_paginas is None:
        max_paginas = MAX_PAGES

    todos_produtos = []

    log(f"Scraping categoria: {categoria_nome}")

    try:
        driver.get(categoria_url)
        time.sleep(REQUEST_DELAY)

        for pagina in range(1, max_paginas + 1):
            log(f"  Pagina {pagina}/{max_paginas}")

            produtos = extrair_produtos_pagina(driver)
            for p in produtos:
                p["categoria"] = categoria_nome
            todos_produtos.extend(produtos)

            if pagina < max_paginas:
                try:
                    next_btn = driver.find_element(
                        By.CSS_SELECTOR,
                        "a.andes-pagination__link[title='Seguinte']"
                    )
                    next_btn.click()
                    time.sleep(REQUEST_DELAY)
                except NoSuchElementException:
                    log("  Nao ha mais paginas")
                    break

    except Exception as e:
        log(f"  Erro ao acessar categoria {categoria_nome}: {e}")

    return todos_produtos


def scraping_completo(categorias_selecionadas=None):
    driver = criar_driver()
    todos_produtos = []

    try:
        log("Iniciando scraping completo...")

        produtos_ofertas = scraping_ofertas_do_dia(driver)
        todos_produtos.extend(produtos_ofertas)
        log(f"Ofertas do dia: {len(produtos_ofertas)} produtos")

        if categorias_selecionadas:
            for nome_cat, url_cat in CATEGORIAS.items():
                if nome_cat in categorias_selecionadas:
                    produtos_cat = scraping_categoria(driver, nome_cat, url_cat)
                    todos_produtos.extend(produtos_cat)
                    log(f"Categoria {nome_cat}: {len(produtos_cat)} produtos")
        else:
            for nome_cat, url_cat in list(CATEGORIAS.items())[:3]:
                produtos_cat = scraping_categoria(driver, nome_cat, url_cat)
                todos_produtos.extend(produtos_cat)
                log(f"Categoria {nome_cat}: {len(produtos_cat)} produtos")

    finally:
        driver.quit()

    produtos_unicos = remover_duplicatas(todos_produtos)
    log(f"Total final: {len(produtos_unicos)} produtos unicos")

    return produtos_unicos


def remover_duplicatas(produtos):
    urls_vistas = set()
    produtos_unicos = []

    for produto in produtos:
        url = produto.get("url_original", "")
        if url and url not in urls_vistas:
            urls_vistas.add(url)
            produtos_unicos.append(produto)

    return produtos_unicos
