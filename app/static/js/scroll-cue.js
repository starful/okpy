(function () {
  function buildCue() {
    var cue = document.createElement('div');
    cue.className = 'article-cta';
    cue.innerHTML =
      '<p class="article-cta__text">まだ読み進められそう？<br>この続きも、きっと役に立ちます。</p>' +
      '<a class="article-cta__link" href="#related-reads">関連記事を見る ↓</a>';
    return cue;
  }

  document.addEventListener('DOMContentLoaded', function () {
    var body = document.getElementById('article-body');
    var related = document.getElementById('related-reads');
    if (!body || !related) return;

    var blocks = Array.prototype.filter.call(body.children, function (el) {
      return el.tagName === 'P' || el.tagName === 'UL' || el.tagName === 'OL';
    });
    if (blocks.length < 4) return;

    var mid = blocks[Math.floor(blocks.length / 2)];
    mid.parentNode.insertBefore(buildCue(), mid.nextSibling);
  });

  document.addEventListener('click', function (e) {
    var link = e.target.closest('.article-cta__link, .floating-cta__link');
    if (!link) return;
    var target = document.getElementById('related-reads');
    if (!target) return;
    e.preventDefault();
    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });

  var SCROLL_SHOW_RATIO = 0.7;
  var SCROLL_BANNER_RATIO = 0.5;
  var ticking = false;

  function scrollProgress() {
    var scrollable = document.documentElement.scrollHeight - window.innerHeight;
    return scrollable > 0 ? window.scrollY / scrollable : 0;
  }

  function updateFloatingCta() {
    ticking = false;
    var progress = scrollProgress();
    var cta = document.getElementById('floating-cta');
    if (cta) cta.classList.toggle('is-visible', progress >= SCROLL_SHOW_RATIO);
    var banner = document.getElementById('scroll-banner-cta');
    if (banner) banner.classList.toggle('is-visible', progress >= SCROLL_BANNER_RATIO);
  }

  document.addEventListener('DOMContentLoaded', function () {
    if (!document.getElementById('floating-cta') && !document.getElementById('scroll-banner-cta')) return;
    updateFloatingCta();
    window.addEventListener('scroll', function () {
      if (ticking) return;
      ticking = true;
      window.requestAnimationFrame(updateFloatingCta);
    }, { passive: true });
  });
})();
