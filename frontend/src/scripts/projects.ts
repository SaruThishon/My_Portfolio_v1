/**
 * 3D Card Carousel — inspired by Framer 3D Card Carousel Pro
 * - Cards turn towards visitor on hover; neighbours glide aside
 * - Dot pagination + arrow nav + drag/scroll
 * - Cards reveal on first scroll into view
 */

(function () {
  const carousel = document.getElementById('pj-carousel') as HTMLElement | null;
  if (!carousel) return;

  const cards = Array.from(carousel.querySelectorAll<HTMLElement>('.pj-card'));
  const dots  = Array.from(document.querySelectorAll<HTMLElement>('.pj-dot'));
  const prevBtn = document.getElementById('pj-prev') as HTMLButtonElement | null;
  const nextBtn = document.getElementById('pj-next') as HTMLButtonElement | null;
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  if (!cards.length) return;

  // ── Scroll-reveal entrance ─────────────────────────────────────────────────
  if (!reduced) {
    const obs = new IntersectionObserver((entries) => {
      entries.forEach(e => {
        if (e.isIntersecting) { e.target.classList.add('is-visible'); obs.unobserve(e.target); }
      });
    }, { threshold: 0.1 });
    cards.forEach(c => obs.observe(c));
  } else {
    cards.forEach(c => c.classList.add('is-visible'));
  }

  // ── 3D depth classes ───────────────────────────────────────────────────────
  function applyDepth(activeIdx: number) {
    cards.forEach((card, i) => {
      card.classList.remove(
        'pj-card--active', 'pj-card--left', 'pj-card--right',
        'pj-card--far-left', 'pj-card--far-right'
      );
      const diff = i - activeIdx;
      if (diff === 0)       card.classList.add('pj-card--active');
      else if (diff === -1) card.classList.add('pj-card--left');
      else if (diff ===  1) card.classList.add('pj-card--right');
      else if (diff < -1)   card.classList.add('pj-card--far-left');
      else                  card.classList.add('pj-card--far-right');
    });

    // Update dots
    dots.forEach((d, i) => {
      d.classList.toggle('pj-dot--active', i === activeIdx);
      d.setAttribute('aria-selected', String(i === activeIdx));
    });

    // Update nav buttons
    if (prevBtn) prevBtn.disabled = activeIdx === 0;
    if (nextBtn) nextBtn.disabled = activeIdx === cards.length - 1;
  }

  // ── Find which card is most centred in the viewport ────────────────────────
  function getActiveIndex(): number {
    const wrapRect = carousel!.getBoundingClientRect();
    const centre   = wrapRect.left + wrapRect.width / 2;
    let best = 0, bestDist = Infinity;
    cards.forEach((card, i) => {
      const rect = card.getBoundingClientRect();
      const dist = Math.abs(rect.left + rect.width / 2 - centre);
      if (dist < bestDist) { bestDist = dist; best = i; }
    });
    return best;
  }

  // Initial state
  applyDepth(0);

  // ── Scroll sync ────────────────────────────────────────────────────────────
  let scrollTick = false;
  carousel!.addEventListener('scroll', () => {
    if (scrollTick) return;
    scrollTick = true;
    requestAnimationFrame(() => {
      applyDepth(getActiveIndex());
      scrollTick = false;
    });
  }, { passive: true });

  // ── Programmatic scroll to card ────────────────────────────────────────────
  function scrollToCard(idx: number) {
    const card = cards[idx];
    if (!card) return;
    const carouselRect = carousel!.getBoundingClientRect();
    const cardRect     = card.getBoundingClientRect();
    const offset = cardRect.left - carouselRect.left - (carouselRect.width - cardRect.width) / 2;
    carousel!.scrollBy({ left: offset, behavior: reduced ? 'instant' : 'smooth' });
    applyDepth(idx);
  }

  // ── Dot clicks ─────────────────────────────────────────────────────────────
  dots.forEach((dot, i) => {
    dot.addEventListener('click', () => scrollToCard(i));
  });

  // ── Arrow nav ──────────────────────────────────────────────────────────────
  prevBtn?.addEventListener('click', () => {
    const cur = getActiveIndex();
    if (cur > 0) scrollToCard(cur - 1);
  });
  nextBtn?.addEventListener('click', () => {
    const cur = getActiveIndex();
    if (cur < cards.length - 1) scrollToCard(cur + 1);
  });

  // ── Drag to scroll ─────────────────────────────────────────────────────────
  let isDragging = false, startX = 0, scrollLeft = 0;

  carousel!.addEventListener('mousedown', (e) => {
    isDragging = true;
    startX = e.clientX;
    scrollLeft = carousel!.scrollLeft;
    carousel!.classList.add('is-dragging');
  });
  document.addEventListener('mousemove', (e) => {
    if (!isDragging) return;
    const dx = e.clientX - startX;
    carousel!.scrollLeft = scrollLeft - dx;
  });
  document.addEventListener('mouseup', () => {
    if (!isDragging) return;
    isDragging = false;
    carousel!.classList.remove('is-dragging');
  });

  // ── Keyboard navigation ────────────────────────────────────────────────────
  carousel!.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowLeft')  { e.preventDefault(); const c = getActiveIndex(); if (c > 0) scrollToCard(c - 1); }
    if (e.key === 'ArrowRight') { e.preventDefault(); const c = getActiveIndex(); if (c < cards.length - 1) scrollToCard(c + 1); }
  });
  carousel!.setAttribute('tabindex', '0');
})();
