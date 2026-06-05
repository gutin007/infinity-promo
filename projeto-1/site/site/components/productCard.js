export function createProductCard(product) {
  return `
    <div class="product-card" data-id="${product.id}">
      <div class="product-image">
        <img src="https://picsum.photos/seed/${product.imageId}/400/300" alt="${product.name}" loading="lazy">
        <span class="discount-badge">-${product.discount}%</span>
      </div>
      <div class="product-info">
        <span class="category-tag">${product.category}</span>
        <h3 class="product-name">${product.name}</h3>
        <p class="product-description">${product.description}</p>
        <div class="price-container">
          <p class="original-price">R$ ${product.originalPrice.toFixed(2).replace('.', ',')}</p>
          <p class="sale-price">R$ ${product.salePrice.toFixed(2).replace('.', ',')}</p>
        </div>
        <a href="produto.html?slug=${product.slug}" class="product-btn">Ver oferta →</a>
      </div>
    </div>
  `;
}
