/**
 * Centralized animation system
 * Handles: stagger reveals, timeline draw, counter-up, section label flash,
 * skill wave, section heading char-reveal, button ripple
 */

const _reducedAnim = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const reduced = _reducedAnim;

// ── 1. Stagger reveals (wave entrance) ──────────────────────────────────────
const staggerGroups = document.querySelectorAll<HTMLElement>('[data-stagger]');
staggerGroups.forEach(group => {
  const children = Array.from(group.children) as HTMLElement[];
  children.forEach((child, i) => {
    child.style.setProperty('--si', String(i));
    if (!reduced) child.classList.add('stagger-child');
    else child.classList.add('stagger-child', 'stagger-visible');
  });

  if (!reduced) {
    const obs = new IntersectionObserver((entries) => {
      entries.forEach(e => {
        if (e.isIntersecting) {
          (Array.from(e.target.children) as HTMLElement[]).forEach(c => c.classList.add('stagger-visible'));
          obs.unobserve(e.target);
        }
      });
    }, { threshold: 0.1 });
    obs.observe(group);
  }
});

// ── 2. Timeline line draw ───────────────────────────────────────────────────
const timelines = document.querySelectorAll<HTMLElement>('.timeline');
timelines.forEach(tl => {
  if (reduced) { tl.classList.add('timeline--drawn'); return; }
  const obs = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) { e.target.classList.add('timeline--drawn'); obs.unobserve(e.target); }
    });
  }, { threshold: 0.1 });
  obs.observe(tl);
});

// ── 3. Count-up numbers ─────────────────────────────────────────────────────
function countUp(el: HTMLElement) {
  const target = parseInt(el.dataset.count || '0', 10);
  const duration = 1200;
  const start = performance.now();
  const tick = (now: number) => {
    const p = Math.min((now - start) / duration, 1);
    const ease = 1 - Math.pow(1 - p, 3); // ease-out cubic
    el.textContent = String(Math.round(ease * target)).padStart(String(target).length, '0');
    if (p < 1) requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick);
}

const counters = document.querySelectorAll<HTMLElement>('[data-count]');
if (!reduced && counters.length) {
  const obs = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) { countUp(e.target as HTMLElement); obs.unobserve(e.target); }
    });
  }, { threshold: 0.5 });
  counters.forEach(c => obs.observe(c));
}

// ── 4. Animated line width draw ─────────────────────────────────────────────
const drawLines = document.querySelectorAll<HTMLElement>('.draw-line');
if (!reduced && drawLines.length) {
  const obs = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) { e.target.classList.add('draw-line--visible'); obs.unobserve(e.target); }
    });
  }, { threshold: 0.3 });
  drawLines.forEach(l => obs.observe(l));
} else {
  drawLines.forEach(l => l.classList.add('draw-line--visible'));
}

// ── 5. Section label flash ───────────────────────────────────────────────────
const sectionLabels = document.querySelectorAll<HTMLElement>('.section-label');
if (!reduced && sectionLabels.length) {
  const obs = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) { e.target.classList.add('section-label--flash'); obs.unobserve(e.target); }
    });
  }, { threshold: 0.5 });
  sectionLabels.forEach(l => obs.observe(l));
}

// ── 6. Button ripple ─────────────────────────────────────────────────────────
document.querySelectorAll<HTMLElement>('.btn--ripple').forEach(btn => {
  btn.addEventListener('click', (e) => {
    const r = btn.getBoundingClientRect();
    const x = (e as MouseEvent).clientX - r.left;
    const y = (e as MouseEvent).clientY - r.top;
    const ripple = document.createElement('span');
    ripple.className = 'btn__ripple-wave';
    ripple.style.left = `${x}px`;
    ripple.style.top  = `${y}px`;
    btn.appendChild(ripple);
    setTimeout(() => ripple.remove(), 600);
  });
});

// ── 7. Floating decoration elements (subtle parallax on scroll) ─────────────
const floaters = document.querySelectorAll<HTMLElement>('[data-float]');
if (!reduced && floaters.length) {
  let ticking = false;
  window.addEventListener('scroll', () => {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(() => {
      const sy = window.scrollY;
      floaters.forEach(f => {
        const speed = parseFloat(f.dataset.float || '0.08');
        f.style.transform = `translateY(${sy * speed}px)`;
      });
      ticking = false;
    });
  }, { passive: true });
}
