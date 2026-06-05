export function transformProduct(p) {
  if (!p) return p;
  return {
    id: p.id,
    slug: p.slug,
    name: p.name,
    description: p.description,
    longDescription: p.description,
    category: p.category,
    originalPrice: Number(p.original_price),
    salePrice: Number(p.sale_price),
    discount: p.discount,
    imageId: p.slug,
    store: {
      name: p.store_name,
      freeShipping: !!p.free_shipping
    },
    coupon: p.coupon || null,
    link: p.link,
    specs: p.specs || {}
  };
}
