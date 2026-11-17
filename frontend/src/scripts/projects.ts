// Project card reveal on scroll
const cards = document.querySelectorAll<HTMLElement>('.reveal-card');
const _reducedProj = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const fine    = window.matchMedia('(pointer: fine)').matches;

if (!_reducedProj && cards.length) {
  const obs = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) { e.target.classList.add('is-visible'); obs.unobserve(e.target); }
    });
  }, { threshold: 0.07, rootMargin: '0px 0px -40px 0px' });
  cards.forEach(c => obs.observe(c));
} else {
  cards.forEach(c => c.classList.add('is-visible'));
}

// 3D tilt on mouse move (desktop fine pointer only, respects reduced-motion)
if (fine && !_reducedProj) {
  cards.forEach(card => {
    const MAX = 7;
    let raf = 0;

    card.addEventListener('mousemove', (e) => {
      cancelAnimationFrame(raf);
      raf = requestAnimationFrame(() => {
        const r = card.getBoundingClientRect();
        const dx = ((e as MouseEvent).clientX - r.left - r.width  / 2) / (r.width  / 2);
        const dy = ((e as MouseEvent).clientY - r.top  - r.height / 2) / (r.height / 2);
        const rX = -dy * MAX;
        const rY =  dx * MAX;
        card.style.transform = `perspective(1000px) rotateX(${rX}deg) rotateY(${rY}deg) scale(1.025)`;
        card.style.transition = 'transform 0.08s linear';
      });
    });

    card.addEventListener('mouseleave', () => {
      cancelAnimationFrame(raf);
      card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) scale(1)';
      card.style.transition = 'transform 0.65s cubic-bezier(.16,1,.3,1)';
    });
  });
}
