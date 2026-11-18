/** Projects — scroll-driven 3D ring. */
(function () {
  if (window.innerWidth <= 600) return; // mobile uses CSS list fallback

  const track    = document.getElementById('pj-track')    as HTMLElement | null;
  const ring     = document.getElementById('pj-ring')     as HTMLElement | null;
  const progress = document.getElementById('pj-progress') as HTMLElement | null;
  const hint     = document.getElementById('pj-hint')     as HTMLElement | null;
  if (!track || !ring) return;

  const cards  = Array.from(ring.querySelectorAll<HTMLElement>('.pj-card'));
  const pdots  = progress ? Array.from(progress.querySelectorAll<HTMLElement>('.pj-pdot')) : [];
  const N      = cards.length;
  const noAnim = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (N === 0) return;

  const CARD_W = 300;
  const CARD_H = 400;
  const STEP   = N > 1 ? 360 / N : 0;
  const TZ     = N > 1 ? Math.max(160, Math.round((CARD_W/2)/Math.tan(Math.PI/N))) : 0;

  ring.style.width  = CARD_W + 'px';
  ring.style.height = CARD_H + 'px';

  // Set each card's BASE transform (slot in ring)
  const baseTFs = cards.map((card, i) => {
    const tf = `rotateY(${(360/N)*i}deg) translateZ(${TZ}px)`;
    card.style.transform = tf;
    return tf;
  });

  let targetAngle = 0, currentAngle = 0, isPaused = false;

  function lerp(a: number, b: number, t: number) { return a + (b-a)*t; }

  function getFront(angle: number) {
    if (N<=1) return 0;
    const a = (((-angle)%360)+360)%360;
    return Math.round(a/STEP)%N;
  }

  function applyDepth(fi: number) {
    cards.forEach((c,i) => {
      c.classList.toggle('is-front', i===fi);
      const dist = Math.min(Math.abs(i-fi), N-Math.abs(i-fi));
      // Use filter:brightness instead of opacity — opacity < 1 creates a
      // stacking context per card which breaks transform-style:preserve-3d.
      c.style.filter = dist===0?'brightness(1)':dist===1?'brightness(0.55)':'brightness(0.25)';
    });
    pdots.forEach((d,i) => d.classList.toggle('is-active', i===fi));
  }

  // RAF: rotate the ring parent, cards keep their local slot transforms
  (function tick() {
    if (!isPaused || noAnim) currentAngle = lerp(currentAngle, targetAngle, noAnim?1:0.07);
    ring!.style.transform = `rotateX(-8deg) rotateY(${currentAngle}deg)`;
    applyDepth(getFront(currentAngle));
    requestAnimationFrame(tick);
  })();

  // Scroll drives targetAngle
  function onScroll() {
    const rect   = track!.getBoundingClientRect();
    const usable = Math.max(track!.offsetHeight - window.innerHeight, 1);
    const prog   = Math.max(0, Math.min(1, -rect.top / usable));
    targetAngle  = -prog * (N-1) * STEP;
    if (hint && -rect.top > 30) hint.classList.add('is-hidden');
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // Pause on hover
  cards.forEach(c => {
    c.addEventListener('mouseenter', () => { isPaused = true; });
    c.addEventListener('mouseleave', () => { isPaused = false; });
  });

  // Hover tilt — add tilt on top of base slot transform, restore on leave
  if (!noAnim && window.matchMedia('(pointer: fine)').matches) {
    const MAX = 10;
    cards.forEach((card, i) => {
      card.addEventListener('mousemove', (e: MouseEvent) => {
        const r  = card.getBoundingClientRect();
        const mx = (e.clientX-r.left)/r.width;
        const my = (e.clientY-r.top)/r.height;
        card.style.setProperty('--mx', String(mx));
        card.style.setProperty('--my', String(my));
        card.style.transform = `${baseTFs[i]} rotateX(${(my-.5)*-MAX*2}deg) rotateY(${(mx-.5)*MAX*2}deg) scale(1.06)`;
      });
      card.addEventListener('mouseleave', () => {
        card.style.setProperty('--mx', '0.5');
        card.style.setProperty('--my', '0.5');
        card.style.transition = 'transform 0.4s cubic-bezier(.16,1,.3,1),box-shadow .3s,border-color .3s';
        card.style.transform  = baseTFs[i];
        setTimeout(() => { card.style.transition = ''; }, 420);
      });
    });
  }

  // Dot clicks + keyboard
  pdots.forEach((d,i) => { d.style.cursor='pointer'; d.addEventListener('click',()=>{ targetAngle=-i*STEP; }); });
  document.addEventListener('keydown', (e: KeyboardEvent) => {
    const r = track!.getBoundingClientRect();
    if (r.top > window.innerHeight || r.bottom < 0) return;
    if (e.key==='ArrowRight'||e.key==='ArrowDown') { e.preventDefault(); targetAngle=Math.max(-(N-1)*STEP,targetAngle-STEP); }
    if (e.key==='ArrowLeft'||e.key==='ArrowUp')    { e.preventDefault(); targetAngle=Math.min(0,targetAngle+STEP); }
  });
})();
