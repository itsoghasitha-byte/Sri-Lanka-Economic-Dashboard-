/* Mobile-friendly 3D-inspired tilt and reveal; disabled when reduced motion is requested. */
(() => {
  const reduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const cards = document.querySelectorAll('.metric-card,.preview-window,.panel,.card,.safety-card,.media-card,.landmark-card,.scenario-card,.side-card');
  cards.forEach(el => el.classList.add('immersive-card'));
  if (!reduced && window.matchMedia('(hover:hover) and (pointer:fine)').matches) {
    cards.forEach(el => {
      el.addEventListener('pointermove', e => {
        const r = el.getBoundingClientRect();
        const x = (e.clientX - r.left) / r.width;
        const y = (e.clientY - r.top) / r.height;
        const rx = (0.5 - y) * 4;
        const ry = (x - 0.5) * 5;
        el.style.transform = 'perspective(900px) rotateX(' + rx.toFixed(2) + 'deg) rotateY(' + ry.toFixed(2) + 'deg) translateY(-2px)';
      });
      el.addEventListener('pointerleave', () => { el.style.transform = ''; });
    });
  }
  if (!reduced && 'IntersectionObserver' in window) {
    const targets = document.querySelectorAll('.landmark-card,.metric-card,.api-console,.panel,.safety-card,.media-card');
    targets.forEach((el, i) => { el.classList.add('immersive-reveal'); el.style.transitionDelay = Math.min(i % 4, 3) * 55 + 'ms'; });
    const observer = new IntersectionObserver(entries => entries.forEach(entry => {
      if (entry.isIntersecting) { entry.target.classList.add('is-visible'); observer.unobserve(entry.target); }
    }), {threshold: 0.12});
    targets.forEach(el => observer.observe(el));
  } else {
    document.querySelectorAll('.immersive-reveal').forEach(el => el.classList.add('is-visible'));
  }
})();
