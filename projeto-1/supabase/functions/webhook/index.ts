// supabase/functions/webhook/index.ts
// Edge Function do Supabase (Deno) que recebe promoções de um bot externo
// e insere na tabela `products` do Supabase.

import { createClient } from 'https://esm.sh/@supabase/supabase-js@2.45.0'

const WEBHOOK_SECRET = Deno.env.get('WEBHOOK_SECRET') ?? ''

interface WebhookPayload {
  titulo: string
  url_original: string
  url_afiliado?: string
  preco_original?: number
  preco_desconto?: number
  porcentagem_desconto?: number
  imagem_url?: string
  especificacoes?: string
  categoria?: string
}

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' }
  })
}

function generateSlug(title: string): string {
  return title
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9\s-]/g, '')
    .trim()
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 80)
}

function extractDomain(url: string): string {
  try {
    return new URL(url).hostname.replace(/^www\./, '')
  } catch {
    return ''
  }
}

function parseSpecs(specs: string | undefined): Record<string, string> {
  if (!specs) return {}
  try {
    const parsed = JSON.parse(specs)
    if (parsed && typeof parsed === 'object' && !Array.isArray(parsed)) {
      const out: Record<string, string> = {}
      for (const [k, v] of Object.entries(parsed)) {
        out[String(k)] = String(v)
      }
      return out
    }
  } catch {
    // not JSON, fall through to line-based parsing
  }
  const out: Record<string, string> = {}
  for (const line of specs.split(/\r?\n/)) {
    const idx = line.indexOf(':')
    if (idx > 0) {
      const key = line.slice(0, idx).trim()
      const value = line.slice(idx + 1).trim()
      if (key && value) out[key] = value
    }
  }
  return out
}

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', {
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'authorization, content-type'
      }
    })
  }

  if (req.method !== 'POST') {
    return jsonResponse({ success: false, error: 'Method not allowed' }, 405)
  }

  const auth = req.headers.get('authorization') ?? ''
  if (!WEBHOOK_SECRET || auth !== `Bearer ${WEBHOOK_SECRET}`) {
    return jsonResponse({ success: false, error: 'Unauthorized' }, 401)
  }

  let body: WebhookPayload
  try {
    body = await req.json()
  } catch {
    return jsonResponse({ success: false, error: 'Invalid JSON body' }, 400)
  }

  if (!body.titulo || !body.url_original) {
    return jsonResponse({
      success: false,
      error: 'Campos obrigatórios ausentes: titulo e url_original'
    }, 400)
  }

  const product = {
    name: body.titulo,
    slug: generateSlug(body.titulo),
    description: body.titulo,
    category: body.categoria?.trim() || 'Geral',
    original_price: body.preco_original ?? 0,
    sale_price: body.preco_desconto ?? 0,
    discount: body.porcentagem_desconto ?? 0,
    image_url: body.imagem_url ?? null,
    store_name: extractDomain(body.url_original),
    free_shipping: false,
    coupon: null,
    link: body.url_afiliado || body.url_original,
    specs: parseSpecs(body.especificacoes),
    active: true
  }

  const supabase = createClient(
    Deno.env.get('https://kywgmckuoueojcsomaxu.supabase.co') ?? '',
    Deno.env.get('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt5d2dtY2t1b3Vlb2pjc29tYXh1Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MDYxNTA4NCwiZXhwIjoyMDk2MTkxMDg0fQ.Ch_2SoXQrktr2GBadb07I7uN8UZCKya49Jks2tPkBXs') ?? ''
  )

  const { data, error } = await supabase
    .from('products')
    .insert(product)
    .select('id')
    .single()

  if (error) {
    return jsonResponse({ success: false, error: error.message }, 500)
  }

  return jsonResponse({ success: true, id: data.id }, 200)
})
