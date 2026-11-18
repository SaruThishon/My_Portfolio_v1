/** Projects — Scroll-driven 3D ring + fast-rabbit-28 hover FX */
(function () {
  const track    = document.getElementById('pj-track')    as HTMLElement | null;
  const stage    = document.getElementById('pj-stage')    as HTMLElement | null;
  const ring     = document.getElementById('pj-ring')     as HTMLElement | null;
  const progress = document.getElementById('pj-progress') as HTMLElement | null;
  const hint     = document.getElementById('pj-hint')     as HTMLElement | null;
  if (!track || !stage || !ring) return;

  const cards   = Array.from(ring.querySelectorAll<HTMLElement>('.pj-card'));
  const pdots   = progress ? Array.from(progress.querySelectorAll<HTMLElement>('.pj-pdot')) : [];
  const N       = cards.length;
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (N === 0) return;

  /* ── Geometry ────────────────────────────────────────────────── */
  const CARD_W = 340;
  const CARD_H = 460;
  const STEP   = 360 / N;
  const TZ     = Math.round((CARD_W / 2) / Math.tan(Math.PI / N));
  ring.style.setProperty('--tz', TZ + 'px');
  ring.style.width  = CARD_W + 'px';
  ring.style.height = CARD_H + 'px';

  /* ── State ───────────────────────────────────────────────────── */
  let targetAngle  = 0;
  let currentAngle = 0;
  let isPaused     = false;

  function lerp(a: number, b: number, t: number) { return a + (b - a) * t; }

  function getFront(angle: number) {
    const a = ((angle % 360) + 360) % 360;
    return (N - Math.round(a / STEP) % N) % N;
  }

  function applyDepth(fi: number) {
    cards.forEach((c, i) => {
      c.classList.toggle('is-front', i === fi);
      const dist = Math.min(Math.abs(i - fi), N - Math.abs(i - fi));
      c.style.opacity = dist === 0 ? '1' : dist === 1 ? '0.65' : '0.3';
    });
    pdots.forEach((d, i) => d.classList.toggle('is-active', i === fi));
  }

  /* ── RAF loop ────────────────────────────────────────────────── */
  function tick() {
    if (!isPaused) currentAngle = lerp(currentAngle, targetAngle, reduced ? 1 : 0.1);
    ring!.style.transform = `rotateX(-10deg) rotateY(${currentAngle}deg)`;
    applyDepth(getFront(-currentAngle));
    requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);

  /* ── Scroll → targetAngle ────────────────────────────────────── */
  function onScroll() {
    const rect    = track!.getBoundingClientRect();
    const usable  = Math.max(track!.offsetHeight - window.innerHeight, 1);
    const prog    = Math.max(0, Math.min(1, -rect.top / usable));
    targetAngle   = -prog * (N - 1) * STEP;
    if (hint && -rect.top > 20) hint.classList.add('is-hidden');
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* ── Pause on card hover ─────────────────────────────────────── */
  cards.forEach(c => {
    c.addEventListener('mouseenter', () => { isPaused = true; });
    c.addEventListener('mouseleave', () => { isPaused = false; });
  });

  /* ── 3D tilt + glare on mousemove ────────────────────────────── */
  if (!reduced && window.matchMedia('(pointer: fine)').matches) {
    const MAX = 12;
    cards.forEach(card => {
      card.addEventListener('mousemove', (e) => {
        const r  = card.getBoundingClientRect();
        const mx = (e.clientX - r.left) / r.width;
        const my = (e.clientY - r.top)  / r.height;
        const rx = (my - 0.5) * -MAX * 2;
        const ry = (mx - 0.5) *  MAX * 2;
        card.style.setProperty('--mx', String(mx));
        card.style.setProperty('--my', String(my));
        // Apply tilt on top of ring position
        card.style.transform =
          `rotateY(calc(360deg / var(--n) * var(--i))) ` +
          `translateZ(var(--tz)) ` +
          `rotateX(${rx}deg) rotateY(${ry}deg) scale(1.04)`;
      });
      card.addEventListener('mouseleave', () => {
        card.style.setProperty('--mx', '0.5');
        card.style.setProperty('--my', '0.5');
        card.style.transform =
          `rotateY(calc(360deg / var(--n) * var(--i))) translateZ(var(--tz))`;
      });
    });
  }

  /* ── Progress dot click ──────────────────────────────────────── */
  pdots.forEach((dot, i) => {
    dot.style.cursor = 'pointer';
    dot.addEventListener('click', () => {
      targetAngle = Math.max(-(N - 1) * STEP, Math.min(0, -i * STEP));
    });
  });

  /* ── Keyboard ────────────────────────────────────────────────── */
  document.addEventListener('keydown', (e) => {
    if (!track) return;
    const r = track.getBoundingClientRect();
    if (r.top > window.innerHeight || r.bottom < 0) return;
    if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
      e.preventDefault();
      targetAngle = Math.max(-(N - 1) * STEP, targetAngle - STEP);
    }
    if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
      e.preventDefault();
      targetAngle = Math.min(0, targetAngle + STEP);
    }
  });
})();
