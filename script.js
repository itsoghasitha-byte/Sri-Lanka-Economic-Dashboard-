(() => {
  const track = document.querySelector('#preview-track');
  const slides = [...document.querySelectorAll('.preview-slide')];
  const indicators = [...document.querySelectorAll('#slide-indicators button')];
  const caption = document.querySelector('#slide-caption');
  const zoomLabel = document.querySelector('#zoom-label');
  const viewport = document.querySelector('.preview-viewport');
  const captions = ['01 / LABOUR MARKET OVERVIEW','02 / SOURCE-FIRST RESEARCH','03 / DATA EXPLORATION'];
  let current = 0;
  let zoom = 100;
  let startX = 0;
  let deltaX = 0;
  let autoAdvance;

  function render() {
    track.style.transform = `scale(${zoom / 100}) translateX(${-current * 100}%)`;
    track.style.width = `${100 / (zoom / 100)}%`;
    slides.forEach((slide, i) => {
      slide.classList.toggle('active', i === current);
      slide.setAttribute('aria-hidden', String(i !== current));
    });
    indicators.forEach((button, i) => {
      button.classList.toggle('active', i === current);
      button.setAttribute('aria-pressed', String(i === current));
    });
    caption.textContent = captions[current];
    zoomLabel.textContent = `${zoom}%`;
  }
  function goTo(index) {
    current = (index + slides.length) % slides.length;
    render();
  }
  function stopAuto() { window.clearInterval(autoAdvance); }
  function startAuto() {
    stopAuto();
    if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      autoAdvance = window.setInterval(() => goTo(current + 1), 7000);
    }
  }
  document.querySelector('#prev-slide').addEventListener('click', () => { goTo(current - 1); startAuto(); });
  document.querySelector('#next-slide').addEventListener('click', () => { goTo(current + 1); startAuto(); });
  indicators.forEach((button, i) => button.addEventListener('click', () => { goTo(i); startAuto(); }));
  document.querySelector('#zoom-in').addEventListener('click', () => { zoom = Math.min(120, zoom + 10); render(); });
  document.querySelector('#zoom-out').addEventListener('click', () => { zoom = Math.max(80, zoom - 10); render(); });
  viewport.addEventListener('pointerdown', e => { startX = e.clientX; deltaX = 0; });
  viewport.addEventListener('pointerup', e => {
    deltaX = e.clientX - startX;
    if (Math.abs(deltaX) > 45) { goTo(current + (deltaX < 0 ? 1 : -1)); startAuto(); }
  });
  viewport.addEventListener('mouseenter', stopAuto);
  viewport.addEventListener('mouseleave', startAuto);
  viewport.addEventListener('focusin', stopAuto);
  viewport.addEventListener('focusout', startAuto);


  const themeToggle = document.querySelector('#theme-toggle');
  const savedTheme = localStorage.getItem('lanka-intel-theme');
  const prefersLight = window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches;
  function applyTheme(theme) {
    document.documentElement.dataset.theme = theme;
    const light = theme === 'light';
    themeToggle.setAttribute('aria-pressed', String(light));
    themeToggle.setAttribute('aria-label', light ? 'Switch to dark mode' : 'Switch to light mode');
    themeToggle.querySelector('.theme-icon').textContent = light ? '◐' : '☼';
    themeToggle.querySelector('.theme-label').textContent = light ? 'DARK MODE' : 'LIGHT MODE';
    const metaTheme = document.querySelector('meta[name="theme-color"]');
    if (metaTheme) metaTheme.setAttribute('content', light ? '#f5efe6' : '#17141f');
  }
  applyTheme(savedTheme === 'light' || savedTheme === 'dark' ? savedTheme : (prefersLight ? 'light' : 'dark'));
  themeToggle.addEventListener('click', () => {
    const nextTheme = document.documentElement.dataset.theme === 'light' ? 'dark' : 'light';
    localStorage.setItem('lanka-intel-theme', nextTheme);
    applyTheme(nextTheme);
  });

  const menuToggle = document.querySelector('.menu-toggle');
  const nav = document.querySelector('#site-nav');
  menuToggle.addEventListener('click', () => {
    const open = nav.classList.toggle('open');
    menuToggle.setAttribute('aria-expanded', String(open));
    menuToggle.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
  });
  nav.querySelectorAll('a').forEach(a => a.addEventListener('click', () => {
    nav.classList.remove('open');
    menuToggle.setAttribute('aria-expanded', 'false');
  }));
  document.querySelector('#year').textContent = new Date().getFullYear();

  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('in-view');
        observer.unobserve(entry.target);
      }
    }), { threshold: 0.12 });
    document.querySelectorAll('.section-heading, .metric-card, .feature-row article, .source-card, .final-cta').forEach(el => {
      el.classList.add('reveal');
      observer.observe(el);
    });
  }
  render();
  startAuto();
})();