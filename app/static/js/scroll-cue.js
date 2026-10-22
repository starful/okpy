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
    var link = e.target.closest('.article-cta__link');
    if (!link) return;
    var target = document.getElementById('related-reads');
    if (!target) return;
    e.preventDefault();
    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
})();
