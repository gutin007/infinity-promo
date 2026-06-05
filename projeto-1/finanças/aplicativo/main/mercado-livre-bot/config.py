import os
from dotenv import load_dotenv

load_dotenv()

ML_AFFILIATE_ID = os.getenv("ML_AFFILIATE_ID", "")
UPDATE_INTERVAL = int(os.getenv("UPDATE_INTERVAL", "2700"))
MAX_PAGES = int(os.getenv("MAX_PAGES", "5"))
REQUEST_DELAY = int(os.getenv("REQUEST_DELAY", "3"))
VERBOSE = os.getenv("VERBOSE", "true").lower() == "true"

URL_OFERTAS = "https://www.mercadolivre.com.br/ofertas"

CATEGORIAS = {
    "ofertas-do-dia": "https://www.mercadolivre.com.br/ofertas#deal_print_id=dynamic_1",
    "tecnologia": "https://www.mercadolivre.com.br/c/tecnologia",
    "celulares": "https://www.mercadolivre.com.br/c/celulares-e-telefones",
    "computadores": "https://www.mercadolivre.com.br/c/computadores",
    "eletrodomesticos": "https://www.mercadolivre.com.br/c/eletrodomesticos",
    "casa-movel-e-jardim": "https://www.mercadolivre.com.br/c/casa-movel-e-jardim",
    "esportes": "https://www.mercadolivre.com.br/c/esportes-e-fitness",
    "beleza": "https://www.mercadolivre.com.br/c/beleza-e-cuidado-pessoal",
    "automotivo": "https://www.mercadolivre.com.br/c/automotivo",
    "games": "https://www.mercadolivre.com.br/c/games",
    "ferramentas": "https://www.mercadolivre.com.br/c/ferramentas",
    "moda": "https://www.mercadolivre.com.br/c/moda",
}

DB_NAME = "promocoes.db"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
]

def get_affiliate_url(product_url):
    if not ML_AFFILIATE_ID:
        return product_url
    separator = "&" if "?" in product_url else "?"
    return f"{product_url}{separator}matt_tool={ML_AFFILIATE_ID}"
