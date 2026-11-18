/** Projects — scroll-driven 3D ring + hover FX via CSS vars */
(function () {
  const track    = document.getElementById('pj-track')    as HTMLElement | null;
  const ring     = document.getElementById('pj-ring')     as HTMLElement | null;
  const progress = document.getElementById('pj-progress') as HTMLElement | null;
  const hint     = document.getElementById('pj-hint')     as HTMLElement | null;
  if (!track || !ring) return;

  const cards   = Array.from(ring.querySelectorAll<HTMLElement>('.pj-card'));
  const pdots   = progress ? Array.from(progress.querySelectorAll<HTMLElement>('.pj-pdot')) : [];
  const N       = cards.length;
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (N === 0) return;

  /* ── Geometry ──────────────────────────────────────────── */
  const CARD_W = 280;
  const CARD_H = 380;
  const STEP   = N > 1 ? 360 / N : 0;
  // translateZ: distance from ring centre so cards form a proper cylinder
  // Guard N=1 (tan(π) ≈ 0 → infinity); also clamp minimum
  const TZ = N > 1
    ? Math.max(180, Math.round((CARD_W / 2) / Math.tan(Math.PI / N)))
    : 0;

  ring.style.setProperty('--tz', TZ + 'px');
  ring.style.width  = CARD_W + 'px';
  ring.style.height = CARD_H + 'px';

  /* ── Scroll state ──────────────────────────────────────── */
  let targetAngle  = 0;
  let currentAngle = 0;
  let isPaused     = false;

  /* ── Helpers ───────────────────────────────────────────── */
  function lerp(a: number, b: number, t: number) {
    return a + (b - a) * t;
  }

  // Which card index is currently at the front (angle ≈ 0 facing viewer)
  function getFrontIndex(angle: number): number {
    if (N <= 1) return 0;
    const normalised = (((-angle) % 360) + 360) % 360;
    return Math.round(normalised / STEP) % N;
  }

  // Apply visual depth to cards based on distance from front
  function applyDepth(frontIdx: number) {
    cards.forEach((card, i) => {
      card.classList.toggle('is-front', i === frontIdx);
      const diff = Math.abs(i - frontIdx);
      const dist = Math.min(diff, N - diff);
      if (dist === 0)      card.style.opacity = '1';
      else if (dist === 1) card.style.opacity = '0.6';
      else                 card.style.opacity = '0.25';
    });
    pdots.forEach((d, i) => d.classList.toggle('is-active', i === frontIdx));
  }

  /* ── RAF loop ──────────────────────────────────────────── */
  function tick() {
    if (!isPaused || reduced) {
      currentAngle = lerp(currentAngle, targetAngle, reduced ? 1 : 0.08);
    }
    // Slight downward tilt makes the ring feel like you're looking at a table
    ring!.style.transform = `rotateX(-8deg) rotateY(${currentAngle}deg)`;
    applyDepth(getFrontIndex(currentAngle));
    requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);

  /* ── Scroll → targetAngle ──────────────────────────────── */
  function onScroll() {
    const rect   = track!.getBoundingClientRect();
    const trackH = track!.offsetHeight;
    const viewH  = window.innerHeight;
    // usable scroll = track height minus one viewport (last viewport exits)
    const usable = Math.max(trackH - viewH, 1);
    const prog   = Math.max(0, Math.min(1, -rect.top / usable));
    // Rotate ring so each card gets an equal share of the scroll travel
    targetAngle  = -prog * (N - 1) * STEP;
    // Hide scroll hint after first scroll
    if (hint && -rect.top > 30) hint.classList.add('is-hidden');
  }

  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* ── Pause ring rotation while hovering a card ─────────── */
  cards.forEach(card => {
    card.addEventListener('mouseenter', () => { isPaused = true; });
    card.addEventListener('mouseleave', () => { isPaused = false; });
  });

  /* ── Hover tilt via CSS vars (doesn't fight ring rotation) ─
     The card's CSS transform chain already includes:
       rotateX(--hover-rx) rotateY(--hover-ry) scale(--hover-sc)
     JS just updates those vars — no style.transform overwrite.      */
  if (!reduced && window.matchMedia('(pointer: fine)').matches) {
    const MAX_TILT = 14;

    cards.forEach(card => {
      card.addEventListener('mousemove', (e: MouseEvent) => {
        const r  = card.getBoundingClientRect();
        const mx = (e.clientX - r.left) / r.width;   // 0–1
        const my = (e.clientY - r.top)  / r.height;  // 0–1
        const rx = (my - 0.5) * -MAX_TILT * 2;        // tilt up/down
        const ry = (mx - 0.5) *  MAX_TILT * 2;        // tilt left/right
        // Update CSS vars — card's transform picks them up automatically
        card.style.setProperty('--hover-rx', rx + 'deg');
        card.style.setProperty('--hover-ry', ry + 'deg');
        card.style.setProperty('--hover-sc', '1.06');
        // Glare position
        card.style.setProperty('--mx', String(mx));
        card.style.setProperty('--my', String(my));
      });

      card.addEventListener('mouseleave', () => {
        card.style.setProperty('--hover-rx', '0deg');
        card.style.setProperty('--hover-ry', '0deg');
        card.style.setProperty('--hover-sc', '1');
        card.style.setProperty('--mx', '0.5');
        card.style.setProperty('--my', '0.5');
      });
    });
  }

  /* ── Progress dot click ────────────────────────────────── */
  pdots.forEach((dot, i) => {
    dot.style.cursor = 'pointer';
    dot.addEventListener('click', () => {
      targetAngle = -i * STEP;
    });
  });

  /* ── Keyboard nav (when track is in view) ──────────────── */
  document.addEventListener('keydown', (e: KeyboardEvent) => {
    const r = track!.getBoundingClientRect();
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
