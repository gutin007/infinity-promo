from dotenv import load_dotenv
import os
import sys
import requests
import time

BOT_DIR = os.path.join(os.path.dirname(__file__), 'mercado-livre-bot')
sys.path.insert(0, BOT_DIR)
load_dotenv(os.path.join(BOT_DIR, '.env'))

from botMercadoLivre import produtos, carregar_produtos_do_banco  # type: ignore
from database import init_db  # type: ignore
load_dotenv()
WEBHOOK = os.getenv("WEBHOOK")
if not WEBHOOK:
    raise ValueError("WEBHOOK não definido no .env")

init_db()

if not produtos:
    produtos = carregar_produtos_do_banco()

promomercadolivre = []
promoshopee = []

CARGOpromoShopee = '1511789248771129514'
CARGOpromoMercadoLivre = '1511789008231993344'

# MERCADO LIVRE
payload = {
    "content": f"Promoção encontrada!\n{promomercadolivre}\n <@&{CARGOpromoMercadoLivre}>",
        "allowed_mentions": {
        "roles": [1511789008231993344]
    },
    "username": "Bot da Infinity - MERCADO LIVRE",
    "avatar_url": "https://i.postimg.cc/gk159hF3/Infinity.png",
    "embeds": [{
        "title": "------INFINITY------",
        "description": "Detalhes da promoção aqui",
        "color": 0x00FF00
    }]
}

response = requests.post(WEBHOOK, json=payload)
print(response.status_code)

# SHOPI
payload = {
    "content": f"Promoção encontrada!\n{promoshopee}\n <@&{CARGOpromoShopee}>",
    "allowed_mentions": {
        "roles": [1511789248771129514]
    },
    "username": "Bot da Infinity - SHOPEE",
    "avatar_url": "https://i.postimg.cc/gk159hF3/Infinity.png",
    "embeds": [{
        "title": "------INFINITY------",
        "description": "Detalhes da promoção aqui",
        "color": 0x00FF00
    }]
}

time.sleep(1)
response = requests.post(WEBHOOK, json=payload)
print(response.status_code)