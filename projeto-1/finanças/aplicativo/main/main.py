import httpx
import time
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "pt-BR,pt;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def buscar_promocoes(query: str, desconto_minimo: float = 20) -> list[dict]:
    url = f"https://lista.mercadolivre.com.br/{query.replace(' ', '-')}"

    resp = httpx.get(url, headers=HEADERS, follow_redirects=True, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    resultados = []
    cards = soup.select("li.ui-search-layout__item")

    for card in cards:
        try:
            titulo_el = card.select_one("h2.ui-search-item__title, h3.ui-search-item__title")
            link_el   = card.select_one("a.ui-search-link")

            # preço atual: primeiro andes-money-amount que NÃO está dentro de <s>
            precos_el      = card.select("span.andes-money-amount__fraction")
            preco_orig_el  = card.select_one("s span.andes-money-amount__fraction")

            if not (titulo_el and link_el and precos_el and preco_orig_el):
                continue

            def parse(el):
                return float(el.text.strip().replace(".", "").replace(",", "."))

            preco_orig = parse(preco_orig_el)

            # o preço atual é o primeiro que não bate com o original
            preco_atual = None
            for pel in precos_el:
                val = parse(pel)
                if val != preco_orig:
                    preco_atual = val
                    break

            if not preco_atual:
                continue

            desconto = round((1 - preco_atual / preco_orig) * 100, 1)

            if desconto < desconto_minimo or desconto > 99:
                continue

            resultados.append({
                "titulo":        titulo_el.text.strip(),
                "preco":         preco_atual,
                "preco_original": preco_orig,
                "desconto_pct":  desconto,  
                "link": str(link_el.get("href") or "").split("?")[0],
            })

        except Exception:
            continue

    resultados.sort(key=lambda x: x["desconto_pct"], reverse=True)
    return resultados


CATEGORIAS = [
    "notebook", "celular", "tv", "geladeira", "ar-condicionado",
    "micro-ondas", "tablet", "monitor", "headphone", "smartwatch",
]

if __name__ == "__main__":
    todas = []

    for categoria in CATEGORIAS:
        print(f"Buscando: {categoria}...")
        try:
            promos = buscar_promocoes(categoria, desconto_minimo=20)
            print(f"  {len(promos)} promoções encontradas")
            todas.extend(promos)
        except Exception as e:
            print(f"  Erro: {e}")
        time.sleep(1)  # evita ser bloqueado

    # remove duplicatas pelo link
    vistas = set()
    unicas = [p for p in todas if not (p["link"] in vistas or vistas.add(p["link"]))]
    unicas.sort(key=lambda x: x["desconto_pct"], reverse=True)

    print(f"\n{'='*60}")
    print(f"🔥 {len(unicas)} promoções acima de 20% encontradas")
    print(f"{'='*60}\n")

    for p in unicas:
        print(f"[{p['desconto_pct']}% OFF] {p['titulo'][:55]}")
        print(f"  💰 R$ {p['preco']:.2f}  (era R$ {p['preco_original']:.2f})")
        print(f"  🔗 {p['link']}\n")