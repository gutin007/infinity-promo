const faqs = [
  {
    question: "Como funcionam as promoções do Infinity Promo?",
    answer: "Buscamos e listamos manualmente as melhores ofertas disponíveis nas principais lojas online do Brasil. Todas as promoções são verificadas antes de serem publicadas."
  },
  {
    question: "Os preços mostrados são confiáveis?",
    answer: "Sim, mas os preços podem mudar a qualquer momento. Sempre verifique o valor final diretamente na loja antes de finalizar a compra."
  },
  {
    question: "Como usar um cupom de desconto?",
    answer: "Na página do produto, clique em 'Copiar cupom'. O código será copiado automaticamente. Em seguida, clique em 'Ver oferta na loja' e cole o código no campo indicado no checkout."
  },
  {
    question: "Com que frequência as promoções são atualizadas?",
    answer: "Atualizamos nossa lista de promoções todos os dias. Promoções expiradas são removidas automaticamente."
  },
  {
    question: "O Infinity Promo vende produtos diretamente?",
    answer: "Não. Somos um agregador de promoções. Ao clicar em 'Ver oferta', você é direcionado para a loja parceira onde a compra é realizada."
  },
  {
    question: "Como posso sugerir uma promoção?",
    answer: "Entre em contato conosco pela página de contato. Analisamos todas as sugestões enviadas pela comunidade."
  }
];

document.addEventListener('DOMContentLoaded', () => {
  const faqList = document.getElementById('faqList');
  if (!faqList) return;

  faqList.innerHTML = faqs.map((faq, i) => `
    <div class="faq-item">
      <button class="faq-question" type="button" aria-expanded="false" data-index="${i}">
        <span class="faq-question-text">${faq.question}</span>
        <span class="faq-icon" aria-hidden="true">+</span>
      </button>
      <div class="faq-answer">
        <div class="faq-answer-inner">
          <p>${faq.answer}</p>
        </div>
      </div>
    </div>
  `).join('');

  const items = faqList.querySelectorAll('.faq-item');

  function closeAll() {
    items.forEach(item => {
      item.classList.remove('active');
      const btn = item.querySelector('.faq-question');
      btn.setAttribute('aria-expanded', 'false');
      const answer = item.querySelector('.faq-answer');
      answer.style.maxHeight = '0px';
    });
  }

  items.forEach(item => {
    const btn = item.querySelector('.faq-question');
    const answer = item.querySelector('.faq-answer');

    btn.addEventListener('click', () => {
      const isOpen = item.classList.contains('active');

      closeAll();

      if (!isOpen) {
        item.classList.add('active');
        btn.setAttribute('aria-expanded', 'true');
        answer.style.maxHeight = answer.scrollHeight + 'px';
      }
    });
  });

  const menuToggle = document.querySelector('.menu-toggle');
  if (menuToggle) {
    menuToggle.addEventListener('click', () => {
      document.querySelector('.nav-links').classList.toggle('active');
    });
  }
});
