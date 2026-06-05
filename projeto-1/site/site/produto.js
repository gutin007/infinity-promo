import { supabase } from './js/supabase.js';
import { createProductCard } from './components/productCard.js';
import { initCountdownTimer } from './components/countdown.js';
import { transformProduct } from './js/transform.js';

document.addEventListener('DOMContentLoaded', async () => {
  const urlParams = new URLSearchParams(window.location.search);
  const slug = urlParams.get('slug');

  const menuToggle = document.querySelector('.menu-toggle');
  const navLinks = document.querySelector('.nav-links');
  if (menuToggle) {
    menuToggle.addEventListener('click', () => {
      navLinks.classList.toggle('active');
    });
  }

  if (!slug) {
    window.location.replace('index.html');
    return;
  }

  let product;
  try {
    const { data, error } = await supabase
      .from('products')
      .select('*')
      .eq('slug', slug)
      .eq('active', true)
      .maybeSingle();

    if (error) throw error;
    if (!data) {
      window.location.replace('index.html');
      return;
    }
    product = transformProduct(data);
  } catch (err) {
    console.error('Erro ao buscar produto:', err);
    window.location.replace('index.html');
    return;
  }

  updateSEO(product);
  renderBreadcrumb(product);
  renderGallery(product);
  renderDetails(product);
  initCountdownTimer(document.getElementById('countdownContainer'), product.slug);
  initCouponButton(product);
  renderSpecs(product);
  initMobileCta(product);

  loadRelated(product);
});

async function loadRelated(product) {
  const grid = document.getElementById('relatedGrid');
  const section = document.querySelector('.related-section');
  try {
    const { data, error } = await supabase
      .from('products')
      .select('*')
      .eq('category', product.category)
      .eq('active', true)
      .neq('slug', product.slug)
      .order('created_at', { ascending: false })
      .limit(3);

    if (error) throw error;

    if (!data || data.length === 0) {
      if (section) section.style.display = 'none';
      return;
    }
    const related = data.map(transformProduct);
    grid.innerHTML = related.map(p => createProductCard(p)).join('');
  } catch (err) {
    console.error('Erro ao buscar produtos relacionados:', err);
    if (section) section.style.display = 'none';
  }
}

function updateSEO(product) {
  document.title = `${product.name} — Infinity Promo`;
  const desc = `De R$ ${product.originalPrice.toFixed(2).replace('.', ',')} por R$ ${product.salePrice.toFixed(2).replace('.', ',')}. ${product.description}`;
  setMeta('description', desc);
  setMeta('og:title', `${product.name} — Infinity Promo`, 'property');
  setMeta('og:description', desc, 'property');
  setMeta('og:image', `https://picsum.photos/seed/${product.imageId}/800/600`, 'property');
  setMeta('og:type', 'product', 'property');
}

function setMeta(name, content, attr = 'name') {
  let el = document.querySelector(`meta[${attr}="${name}"]`);
  if (!el) {
    el = document.createElement('meta');
    el.setAttribute(attr, name);
    document.head.appendChild(el);
  }
  el.setAttribute('content', content);
}

function renderBreadcrumb(product) {
  document.getElementById('breadcrumbCategory').textContent = product.category;
  document.getElementById('breadcrumbCategory').href = `busca.html?category=${encodeURIComponent(product.category)}`;
  document.getElementById('breadcrumbCurrent').textContent = product.name;
}

function renderGallery(product) {
  const mainImage = document.getElementById('mainImage');
  const skeleton = document.getElementById('gallerySkeleton');
  const badge = document.getElementById('galleryBadge');
  const thumbs = document.querySelectorAll('.product-thumbs .thumb');

  const gallerySeeds = [product.imageId, `${product.imageId}-2`, `${product.imageId}-3`];
  const imageUrls = gallerySeeds.map(s => `https://picsum.photos/seed/${s}/800/600`);

  mainImage.src = imageUrls[0];
  mainImage.alt = product.name;
  mainImage.addEventListener('load', () => {
    skeleton.style.display = 'none';
    mainImage.style.display = 'block';
  }, { once: true });

  mainImage.addEventListener('error', () => {
    skeleton.style.display = 'none';
    mainImage.style.display = 'block';
  }, { once: true });

  badge.textContent = `-${product.discount}%`;
  badge.style.display = 'block';

  thumbs.forEach((thumb, i) => {
    const img = thumb.querySelector('img');
    img.src = imageUrls[i];
    img.alt = `${product.name} - vista ${i + 1}`;
    thumb.addEventListener('click', () => {
      thumbs.forEach(t => t.classList.remove('active'));
      thumb.classList.add('active');
      mainImage.style.opacity = '0';
      setTimeout(() => {
        mainImage.src = imageUrls[i];
        mainImage.onload = () => { mainImage.style.opacity = '1'; };
      }, 150);
    });
  });
}

function renderDetails(product) {
  document.getElementById('productCategory').textContent = product.category;
  document.getElementById('productTitle').textContent = product.name;
  document.getElementById('originalPrice').textContent = `R$ ${product.originalPrice.toFixed(2).replace('.', ',')}`;
  document.getElementById('salePrice').textContent = `R$ ${product.salePrice.toFixed(2).replace('.', ',')}`;
  const savings = product.originalPrice - product.salePrice;
  document.getElementById('savingsLine').innerHTML = `Você economiza <strong>R$ ${savings.toFixed(2).replace('.', ',')}</strong>`;
  document.getElementById('storeLink').href = product.link;
  document.getElementById('storeName').textContent = product.store.name;
  if (product.store.freeShipping) {
    document.getElementById('freeShipping').style.display = 'inline-flex';
  }
}

function initCouponButton(product) {
  const btn = document.getElementById('couponBtn');
  const text = document.getElementById('couponBtnText');

  if (!product.coupon) {
    btn.disabled = true;
    btn.classList.add('disabled');
    text.textContent = 'Sem cupom disponível';
    return;
  }

  let resetTimer = null;

  btn.addEventListener('click', async () => {
    if (btn.classList.contains('copied')) return;
    try {
      await navigator.clipboard.writeText(product.coupon);
    } catch (err) {
      const textarea = document.createElement('textarea');
      textarea.value = product.coupon;
      textarea.setAttribute('readonly', '');
      textarea.style.position = 'absolute';
      textarea.style.left = '-9999px';
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand('copy');
      document.body.removeChild(textarea);
    }
    btn.classList.add('copied');
    text.textContent = '✓ Cupom copiado!';
    clearTimeout(resetTimer);
    resetTimer = setTimeout(() => {
      btn.classList.remove('copied');
      text.textContent = 'Copiar cupom';
    }, 2000);
  });
}

function renderSpecs(product) {
  const table = document.getElementById('specsTable');
  const rows = Object.entries(product.specs || {})
    .map(([key, value]) => `
      <div class="specs-row">
        <span class="specs-label">${key}</span>
        <span class="specs-value">${value}</span>
      </div>
    `).join('');
  table.innerHTML = rows;
  document.getElementById('productLongDescription').textContent = product.longDescription;
}

function initMobileCta(product) {
  document.getElementById('mobileCtaPrice').textContent = `R$ ${product.salePrice.toFixed(2).replace('.', ',')}`;
  document.getElementById('mobileCtaDiscount').textContent = `-${product.discount}% OFF`;
  document.getElementById('mobileCtaBtn').href = product.link;
}
