import os
from dotenv import load_dotenv

load_dotenv()

SHOPEE_AFFILIATE_ID = os.getenv("SHOPEE_AFFILIATE_ID", "")
SHOPEE_AFFILIATE_TOKEN = os.getenv("SHOPEE_AFFILIATE_TOKEN", "")
UPDATE_INTERVAL = int(os.getenv("UPDATE_INTERVAL", "2700"))
MAX_PAGES = int(os.getenv("MAX_PAGES", "3"))
REQUEST_DELAY = int(os.getenv("REQUEST_DELAY", "4"))
VERBOSE = os.getenv("VERBOSE", "true").lower() == "true"
COUNTRY = os.getenv("COUNTRY", "br")

DOMINIOS = {
    "br": "shopee.com.br",
    "sg": "shopee.sg",
    "my": "shopee.com.my",
    "th": "shopee.co.th",
    "id": "shopee.co.id",
    "vn": "shopee.vn",
    "ph": "shopee.com.ph",
    "tw": "shopee.tw",
}

DOMAIN = DOMINIOS.get(COUNTRY, "shopee.com.br")

URL_BASE = f"https://{DOMAIN}"

URL_FLASH_SALE = f"{URL_BASE}/flash_sale"
URL_MALL = f"{URL_BASE}/mall"
URL_OFERTAS = f"{URL_BASE}/daily_discover"

CATEGORIAS = {
    "ofertas-do-dia": f"{URL_BASE}/daily_discover",
    "flash-sale": f"{URL_BASE}/flash_sale",
    "tecnologia": f"{URL_BASE}/search?keyword=tecnologia",
    "celulares": f"{URL_BASE}/search?keyword=celular",
    "notebooks": f"{URL_BASE}/search?keyword=notebook",
    "fones": f"{URL_BASE}/search?keyword=fone+bluetooth",
    "smartwatch": f"{URL_BASE}/search?keyword=smartwatch",
    "eletrodomesticos": f"{URL_BASE}/search?keyword=eletrodomesticos",
    "casa": f"{URL_BASE}/search?keyword=casa+decoracao",
    "moda-feminina": f"{URL_BASE}/search?keyword=moda+feminina",
    "moda-masculina": f"{URL_BASE}/search?keyword=moda+masculina",
    "beleza": f"{URL_BASE}/search?keyword=beleza+skincare",
    "esportes": f"{URL_BASE}/search?keyword=esportes+fitness",
    "games": f"{URL_BASE}/search?keyword=games+gamer",
    "ferramentas": f"{URL_BASE}/search?keyword=ferramentas",
    "automotivo": f"{URL_BASE}/search?keyword=automotivo",
}

DB_NAME = "promocoes_shopee.db"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
]

COMISSOES_CATEGORIA = {
    "moda": "15-30%",
    "bolsas": "15-30%",
    "calcados": "15-30%",
    "beleza": "12-25%",
    "casa": "10-20%",
    "eletronicos": "5-15%",
    "default": "3-10%",
}


def get_affiliate_url(product_url):
    if not SHOPEE_AFFILIATE_ID:
        return product_url

    separator = "&" if "?" in product_url else "?"
    return f"{product_url}{separator}af_id={SHOPEE_AFFILIATE_ID}"


def get_domain():
    return DOMAIN


def get_url_base():
    return URL_BASE
