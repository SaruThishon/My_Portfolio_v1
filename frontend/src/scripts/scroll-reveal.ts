// Intersection Observer based scroll reveal
// Works with .reveal, .reveal-left, .reveal-scale classes

const revealElements = document.querySelectorAll<HTMLElement>('.reveal, .reveal-left, .reveal-scale');

if (revealElements.length && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target); // play once
        }
      });
    },
    {
      threshold: 0.1,
      rootMargin: '0px 0px -48px 0px',
    }
  );
  revealElements.forEach((el) => observer.observe(el));
} else {
  // Reduced motion or no elements: show all immediately
  revealElements.forEach((el) => el.classList.add('is-visible'));
}
