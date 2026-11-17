// Custom cursor — fine pointer devices only
// Uses requestAnimationFrame lerp for smooth ring tracking

const isReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const isFinePointer = window.matchMedia('(pointer: fine)').matches;

if (isFinePointer && !isReducedMotion) {
  // Create elements
  const dot = document.createElement('div');
  dot.id = 'cursor-dot';
  dot.setAttribute('aria-hidden', 'true');

  const ring = document.createElement('div');
  ring.id = 'cursor-ring';
  ring.setAttribute('aria-hidden', 'true');

  document.body.appendChild(dot);
  document.body.appendChild(ring);
  document.body.classList.add('cursor-active');

  let mouseX = 0, mouseY = 0;
  let ringX = 0, ringY = 0;
  let isHoveringInteractive = false;

  const lerp = (a: number, b: number, n: number) => a + (b - a) * n;

  document.addEventListener('mousemove', (e) => {
    mouseX = e.clientX;
    mouseY = e.clientY;
    dot.style.transform = `translate(${mouseX}px, ${mouseY}px) translate(-50%, -50%)`;
  });

  const INTERACTIVE_SELECTORS = 'a, button, [role="button"], input, textarea, select, .pj-card, label';

  // Cursor label for project cards
  const label = document.createElement('span');
  label.id = 'cursor-label';
  label.setAttribute('aria-hidden', 'true');
  document.body.appendChild(label);

  document.addEventListener('mouseover', (e) => {
    const target = e.target as Element;
    isHoveringInteractive = !!target.closest(INTERACTIVE_SELECTORS);
    ring.classList.toggle('is-hovering', isHoveringInteractive);
    dot.classList.toggle('is-hovering', isHoveringInteractive);

    // Show "VIEW" label when over project card
    const isCard = !!target.closest('.pj-card');
    label.textContent = isCard ? 'VIEW' : '';
    label.classList.toggle('is-visible', isCard);
    ring.classList.toggle('is-on-card', isCard);
  });

  document.addEventListener('mouseleave', () => {
    dot.style.opacity = '0';
    ring.style.opacity = '0';
  });

  document.addEventListener('mouseenter', () => {
    dot.style.opacity = '1';
    ring.style.opacity = '1';
  });

  // RAF loop for smooth ring
  const tick = () => {
    ringX = lerp(ringX, mouseX, 0.12);
    ringY = lerp(ringY, mouseY, 0.12);
    ring.style.transform = `translate(${ringX}px, ${ringY}px) translate(-50%, -50%)`;
    // Sync label position with ring
    const labelEl = document.getElementById('cursor-label');
    if (labelEl) labelEl.style.transform = `translate(${ringX}px, ${ringY}px) translate(-50%, -50%)`;
    requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick);

  // Inject cursor styles
  const style = document.createElement('style');
  style.textContent = `
    #cursor-dot {
      position: fixed; top: 0; left: 0; z-index: 9999;
      width: 6px; height: 6px; border-radius: 50%;
      background: #B794F6; pointer-events: none;
      will-change: transform; transition: opacity 0.2s, width 0.2s, height 0.2s;
    }
    #cursor-dot.is-hovering {
      width: 10px; height: 10px; background: #C4A8FF;
    }
    #cursor-ring {
      position: fixed; top: 0; left: 0; z-index: 9998;
      width: 36px; height: 36px; border-radius: 50%;
      border: 1.5px solid rgba(183, 148, 246, 0.6);
      pointer-events: none; will-change: transform;
      transition: opacity 0.2s, width 0.3s, height 0.3s, border-color 0.3s;
    }
    #cursor-ring.is-hovering {
      width: 52px; height: 52px; border-color: rgba(183, 148, 246, 0.9);
    }
    #cursor-ring.is-on-card {
      width: 72px; height: 72px;
      border-color: rgba(183, 148, 246, 0.8);
      background: rgba(183, 148, 246, 0.07);
    }
    #cursor-label {
      position: fixed; top: 0; left: 0; z-index: 9997;
      font-family: 'Space Grotesk', sans-serif;
      font-size: 10px; font-weight: 700; letter-spacing: 0.15em;
      text-transform: uppercase; color: #F5F0FA;
      pointer-events: none; white-space: nowrap;
      opacity: 0; transform: translate(-50%, -50%);
      transition: opacity 0.2s ease;
      /* Position will be synced with ring via transform trick */
    }
    #cursor-label.is-visible { opacity: 1; }
  `;
  document.head.appendChild(style);
}
