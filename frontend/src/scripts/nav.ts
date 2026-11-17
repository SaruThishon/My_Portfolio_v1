const nav = document.getElementById('main-nav')!;
const hamburger = nav?.querySelector('.nav__hamburger') as HTMLButtonElement | null;
const mobileMenu = document.getElementById('mobile-menu');

if (nav) {
  window.addEventListener('scroll', () => {
    nav.classList.toggle('is-scrolled', window.scrollY > 20);
  }, { passive: true });
  nav.classList.toggle('is-scrolled', window.scrollY > 20);
}

if (hamburger && mobileMenu) {
  hamburger.addEventListener('click', () => {
    const expanded = hamburger.getAttribute('aria-expanded') === 'true';
    hamburger.setAttribute('aria-expanded', String(!expanded));
    mobileMenu.setAttribute('aria-hidden', String(expanded));
    document.body.style.overflow = expanded ? '' : 'hidden';
  });
  mobileMenu.querySelectorAll('.nav__mobile-link').forEach(link => {
    link.addEventListener('click', () => {
      hamburger.setAttribute('aria-expanded', 'false');
      mobileMenu.setAttribute('aria-hidden', 'true');
      document.body.style.overflow = '';
    });
  });
}

// Active section tracking
const sections = document.querySelectorAll('section[id]');
const navLinks = document.querySelectorAll('.nav__link');
if (sections.length && navLinks.length) {
  const obs = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        navLinks.forEach(l => l.classList.toggle('is-active', l.getAttribute('href') === `/#${e.target.id}`));
      }
    });
  }, { rootMargin: '-40% 0px -40% 0px' });
  sections.forEach(s => obs.observe(s));
}
