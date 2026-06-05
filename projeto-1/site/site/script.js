import { supabase } from './js/supabase.js';
import { createProductCard } from './components/productCard.js';
import { transformProduct } from './js/transform.js';

const categories = [
  { name: 'Eletrônicos', icon: 'smartphone' },
  { name: 'Moda', icon: 'shirt' },
  { name: 'Casa & Cozinha', icon: 'home' },
  { name: 'Esportes', icon: 'dumbbell' },
  { name: 'Livros', icon: 'book-open' },
  { name: 'Games', icon: 'gamepad-2' }
];

const categoryIcons = {
  'Eletrônicos': `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="14" height="20" x="5" y="2" rx="2" ry="2"/><path d="M12 18h.01"/></svg>`,
  'Moda': `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.38 3.46 16 2 12 5 8 2 3.62 3.46a2 2 0 0 0-1.34 2.23l.58 3.47a1 1 0 0 0 .99.84H6v10c0 1.1.9 2 2 2h8a2 2 0 0 0 2-2V10h2.15a1 1 0 0 0 .99-.84l.58-3.47a2 2 0 0 0-1.34-2.23z"/></svg>`,
  'Casa & Cozinha': `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>`,
  'Esportes': `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m6.5 6.5 11 11"/><path d="m21 21-1-1"/><path d="m3 3 1 1"/><path d="m18 22 4-4"/><path d="m2 6 4-4"/><path d="m3 10 7-7"/><path d="m14 21 7-7"/></svg>`,
  'Livros': `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>`,
  'Games': `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="6" x2="10" y1="12" y2="12"/><line x1="8" x2="8" y1="10" y2="14"/><line x1="15" x2="15.01" y1="13" y2="13"/><line x1="18" x2="18.01" y1="11" y2="11"/><rect width="20" height="12" x="2" y="6" rx="2"/></svg>`
};

document.addEventListener('DOMContentLoaded', () => {
  const productsGrid = document.getElementById('productsGrid');
  const categoriesGrid = document.getElementById('categoriesGrid');
  const homeSearch = document.getElementById('homeSearch');
  const homeSearchBtn = document.getElementById('homeSearchBtn');
  const menuToggle = document.querySelector('.menu-toggle');
  const navLinks = document.querySelector('.nav-links');

  const filterToggle = document.getElementById('filterToggle');
  const filterDropdown = document.getElementById('filterDropdown');
  const applyFiltersBtn = document.getElementById('applyFilters');
  let filterOpen = false;

  let allProducts = [];
  let selectedCategory = 'all';
  let selectedDiscount = '0';
  let selectedSort = 'recent';

  filterToggle.addEventListener('click', (e) => {
    e.stopPropagation();
    filterOpen = !filterOpen;
    filterDropdown.classList.toggle('active', filterOpen);
  });

  document.addEventListener('click', (e) => {
    if (filterOpen && !filterDropdown.contains(e.target) && e.target !== filterToggle) {
      filterOpen = false;
      filterDropdown.classList.remove('active');
    }
  });

  applyFiltersBtn.addEventListener('click', () => {
    selectedCategory = document.querySelector('input[name="category"]:checked').value;
    selectedDiscount = document.querySelector('input[name="discount"]:checked').value;
    selectedSort = document.querySelector('input[name="sort"]:checked').value;
    filterOpen = false;
    filterDropdown.classList.remove('active');
    renderProducts();
  });

  function renderCategories() {
    if (!categoriesGrid) return;
    categoriesGrid.innerHTML = categories.map(cat => `
      <div class="category-card" data-category="${cat.name}">
        ${categoryIcons[cat.name] || ''}
        <span>${cat.name}</span>
      </div>
    `).join('');

    document.querySelectorAll('.category-card').forEach(card => {
      card.addEventListener('click', () => {
        const category = card.dataset.category;
        window.location.href = `busca.html?category=${encodeURIComponent(category)}`;
      });
    });
  }

  function showSkeletons(count = 6) {
    productsGrid.innerHTML = Array.from({ length: count }, () => `
      <div class="product-card skeleton-card">
        <div class="product-image skeleton-box"></div>
        <div class="product-info">
          <div class="skeleton-line short"></div>
          <div class="skeleton-line"></div>
          <div class="skeleton-line"></div>
          <div class="skeleton-line short"></div>
          <div class="skeleton-btn"></div>
        </div>
      </div>
    `).join('');
  }

  function showEmpty() {
    productsGrid.innerHTML = `
      <div class="empty-state">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" y1="8" x2="12" y2="12"/>
          <line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
        <h3>Nenhuma promoção disponível no momento</h3>
        <p>Volte mais tarde para conferir novas ofertas.</p>
      </div>
    `;
  }

  function renderProducts() {
    let filtered = [...allProducts];

    if (selectedCategory !== 'all') {
      filtered = filtered.filter(p => p.category === selectedCategory);
    }

    if (selectedDiscount !== '0') {
      filtered = filtered.filter(p => p.discount > parseInt(selectedDiscount));
    }

    if (selectedSort === 'discount') {
      filtered.sort((a, b) => b.discount - a.discount);
    } else if (selectedSort === 'price-asc') {
      filtered.sort((a, b) => a.salePrice - b.salePrice);
    } else {
      filtered.sort((a, b) => new Date(b.createdAt || 0) - new Date(a.createdAt || 0));
    }

    if (filtered.length === 0) {
      showEmpty();
    } else {
      productsGrid.innerHTML = filtered.map(product => createProductCard(product)).join('');
    }
  }

  function handleSearch() {
    const term = homeSearch.value.trim();
    if (term) {
      window.location.href = `busca.html?q=${encodeURIComponent(term)}`;
    }
  }

  homeSearch.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleSearch();
  });

  homeSearchBtn.addEventListener('click', handleSearch);

  menuToggle.addEventListener('click', () => {
    navLinks.classList.toggle('active');
  });

  renderCategories();
  showSkeletons(6);

  (async () => {
    try {
      const { data, error } = await supabase
        .from('products')
        .select('*')
        .eq('active', true)
        .order('created_at', { ascending: false })
        .limit(8);

      if (error) throw error;

      if (!data || data.length === 0) {
        showEmpty();
        return;
      }

      allProducts = data.map(transformProduct);
      renderProducts();
    } catch (err) {
      console.error('Erro ao buscar produtos:', err);
      showEmpty();
    }
  })();
});
