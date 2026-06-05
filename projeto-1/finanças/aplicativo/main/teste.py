# teste.py
import httpx

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "pt-BR,pt;q=0.9",
}

resp = httpx.get("https://lista.mercadolivre.com.br/notebook", headers=HEADERS, follow_redirects=True)
print(resp.text[:3000])