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

// Active section tracking — watch both <section id> and <div id> landmarks
const sections = document.querySelectorAll('section[id], div[id="about"], div[id="projects"], div[id="skills"], div[id="journey"], div[id="contact"]');
const navLinks = document.querySelectorAll('.nav__link');

if (sections.length && navLinks.length) {
  function setActive(id: string) {
    navLinks.forEach(l => l.classList.toggle('is-active', l.getAttribute('href') === `/#${id}`));
  }

  // For the sticky scroll-track (#pj-track), we detect when we're scrolled into it
  const pjTrack = document.getElementById('pj-track');

  const obs = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) setActive(e.target.id);
    });
  }, { rootMargin: '-30% 0px -30% 0px', threshold: 0 });

  sections.forEach(s => obs.observe(s));

  // Also observe the projects track so nav highlights while scrolling through ring
  if (pjTrack) {
    const pjObs = new IntersectionObserver((entries) => {
      entries.forEach(e => {
        if (e.isIntersecting) setActive('projects');
      });
    }, { rootMargin: '0px', threshold: 0.05 });
    pjObs.observe(pjTrack);
  }
}
