/* Lightweight progressive image and navigation enhancements.
 * Browsers natively choose <source type="image/webp"> in <picture>; optional
 * data-webp-src is used only when explicitly provided by markup.
 */
(() => {
  const supportsWebP = (() => {
    try {
      const canvas = document.createElement("canvas");
      return canvas.toDataURL("image/webp").startsWith("data:image/webp");
    } catch (_) { return false; }
  })();

  const enhanceImages = () => {
    document.querySelectorAll("img").forEach((img, index) => {
      if (!img.hasAttribute("loading") && index > 0) img.loading = "lazy";
      if (!img.hasAttribute("decoding")) img.decoding = "async";
      if (supportsWebP && img.dataset.webpSrc && img.src !== img.dataset.webpSrc) {
        img.src = img.dataset.webpSrc;
      }
    });
  };

  const enhanceNativeNavigation = () => {
    const toggle = document.querySelector(".menu-toggle");
    const nav = document.querySelector("#site-nav");
    if (!toggle || !nav) return;
    toggle.setAttribute("aria-controls", nav.id);
    toggle.addEventListener("click", () => {
      const expanded = toggle.getAttribute("aria-expanded") === "true";
      toggle.setAttribute("aria-expanded", String(!expanded));
      toggle.setAttribute("aria-label", expanded ? "Open navigation" : "Close navigation");
      nav.classList.toggle("is-open", !expanded);
    });
    nav.querySelectorAll("a").forEach(link => link.addEventListener("click", () => {
      toggle.setAttribute("aria-expanded", "false");
      toggle.setAttribute("aria-label", "Open navigation");
      nav.classList.remove("is-open");
    }));
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => {
      enhanceImages();
      enhanceNativeNavigation();
    }, { once: true });
  } else {
    enhanceImages();
    enhanceNativeNavigation();
  }
})();
