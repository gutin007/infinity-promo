# Webhook — Infinity Promo

Endpoint que recebe promoções de um bot externo (Python) e salva no Supabase.

## URL do endpoint

| Ambiente | URL |
|----------|-----|
| **Desenvolvimento local** | `http://localhost:54321/functions/v1/webhook` |
| **Produção** | `https://kywgmckuoueojcsomaxu.supabase.co/functions/v1/webhook` |

## Autenticação

Toda requisição precisa do header:

```
Authorization: Bearer infinity_promo_secret_2026
Content-Type: application/json
```

## Payload aceito

```json
{
  "titulo": "Smartphone Galaxy S24 Ultra",
  "url_original": "https://www.samsung.com.br/galaxy-s24-ultra",
  "url_afiliado": "https://amzn.to/xxxxx",
  "preco_original": 8499.00,
  "preco_desconto": 5999.00,
  "porcentagem_desconto": 29,
  "imagem_url": "https://...",
  "especificacoes": "{\"RAM\":\"12GB\",\"Bateria\":\"5000mAh\"}",
  "categoria": "Eletrônicos"
}
```

Apenas `titulo` e `url_original` são obrigatórios. Os demais são opcionais.

`especificacoes` aceita:
- String JSON válida (recomendado): `"{\"RAM\":\"12GB\"}"`
- Formato `chave: valor` por linha: `"RAM: 12GB\nBateria: 5000mAh"`

## Exemplo em Python

```python
import requests

WEBHOOK_URL = 'https://kywgmckuoueojcsomaxu.supabase.co/functions/v1/webhook'
# Em dev local: 'http://localhost:54321/functions/v1/webhook'
WEBHOOK_TOKEN = 'infinity_promo_secret_2026'

def enviar_promocao(produto: dict):
    response = requests.post(
        WEBHOOK_URL,
        json=produto,
        headers={
            'Authorization': f'Bearer {WEBHOOK_TOKEN}',
            'Content-Type': 'application/json'
        }
    )
    return response.json()

# Exemplo de uso
if __name__ == '__main__':
    resultado = enviar_promocao({
        'titulo': 'Smartphone Galaxy S24 Ultra',
        'url_original': 'https://www.samsung.com.br/galaxy-s24-ultra',
        'url_afiliado': 'https://amzn.to/xxxxx',
        'preco_original': 8499.00,
        'preco_desconto': 5999.00,
        'porcentagem_desconto': 29,
        'imagem_url': 'https://picsum.photos/seed/galaxy/400/300',
        'especificacoes': '{"RAM":"12GB","Bateria":"5000mAh"}',
        'categoria': 'Eletrônicos'
    })
    print(resultado)
    # Sucesso:  {'success': True, 'id': 'uuid-aqui'}
    # Erro:     {'success': False, 'error': 'mensagem'}
```

## Respostas

| Status | Significado | Body |
|--------|-------------|------|
| `200` | Sucesso — produto inserido | `{"success": true, "id": "uuid"}` |
| `400` | Campos obrigatórios ausentes ou JSON inválido | `{"success": false, "error": "..."}` |
| `401` | Token ausente ou inválido | `{"success": false, "error": "Unauthorized"}` |
| `405` | Método diferente de POST | `{"success": false, "error": "Method not allowed"}` |
| `500` | Erro no Supabase (ex: slug duplicado) | `{"success": false, "error": "..."}` |

## Configurar o `.env` (para o bot Python)

O repositório tem um arquivo **`.env.example`** na raiz com a estrutura das variáveis:

```
SUPABASE_URL=
SUPABASE_KEY=
WEBHOOK_SECRET=
```

Para rodar o bot Python localmente, copie o exemplo para um arquivo `.env` na raiz e preencha com os valores reais:

```bash
cp .env.example .env
# edite o .env e preencha as três variáveis
```

⚠️ **Nunca commite o `.env` no Git.** O `.gitignore` da raiz já ignora `.env` e `*.env`, mas confira antes de cada `git add` / `git commit`. Quem tiver acesso ao repositório conseguirá ver as chaves — incluindo a `service_role` do Supabase, que dá acesso total ao banco.

| Variável | Onde é usada |
|----------|--------------|
| `SUPABASE_URL` | Bot Python (e também o site estático, mas lá está hardcoded em `js/supabase.js`) |
| `SUPABASE_KEY` | Bot Python (no site estático é a `publishable` key, hardcoded em `js/supabase.js`) |
| `WEBHOOK_SECRET` | Bot Python para autenticar no endpoint. **A mesma string precisa ser configurada no Supabase via `supabase secrets set WEBHOOK_SECRET=...`** |

> Nota: a Edge Function **não** lê do `.env` do projeto — ela lê das secrets do Supabase configuradas via CLI (`supabase secrets set`).

## Deploy (uma vez só)

### 1. Instalar o Supabase CLI (se ainda não tem)

```bash
# Windows (Scoop)
scoop install supabase

# Ou via npm (qualquer SO)
npm install -g supabase
```

### 2. Login e linkar ao projeto

```bash
supabase login
supabase link --project-ref kywgmckuoueojcsomaxu
```

### 3. Configurar o token como secret

```bash
supabase secrets set WEBHOOK_SECRET=infinity_promo_secret_2026
```

> ⚠️ O token **NÃO** vai no `.env.local` do site estático — ele é secret da Edge Function, gerenciado pelo Supabase.

### 4. Deploy da função

```bash
supabase functions deploy webhook
```

### 5. Testar localmente (opcional)

```bash
supabase functions serve webhook --env-file ./supabase/.env.local
```

Crie `./supabase/.env.local` antes com:

```
WEBHOOK_SECRET=infinity_promo_secret_2026
```

## Mapeamento de campos

| Campo do bot | Campo no Supabase | Observação |
|--------------|-------------------|------------|
| `titulo` | `name`, `description`, `slug` | slug é gerado a partir do título |
| `url_afiliado` ou `url_original` | `link` | usa afiliado se existir, senão original |
| `preco_original` | `original_price` | default `0` se ausente |
| `preco_desconto` | `sale_price` | default `0` se ausente |
| `porcentagem_desconto` | `discount` | default `0` se ausente |
| `imagem_url` | `image_url` | `null` se ausente |
| `categoria` | `category` | `"Geral"` se vazio |
| `especificacoes` | `specs` (jsonb) | parseia JSON ou `chave: valor` |
| `url_original` | `store_name` | extrai o domínio (ex: `amazon.com.br`) |
| — | `active` | sempre `true` |
| — | `free_shipping` | sempre `false` |
| — | `coupon` | sempre `null` |
