(function () {
  document.addEventListener('DOMContentLoaded', function () {
    var tocLinks = document.querySelectorAll('.toc a[href^="#"]');
    if (!tocLinks.length || !('IntersectionObserver' in window)) return;

    var headings = [];
    Array.prototype.forEach.call(tocLinks, function (link) {
      var heading = document.getElementById(link.getAttribute('href').slice(1));
      if (heading) headings.push(heading);
    });
    if (!headings.length) return;

    var setActive = function (id) {
      Array.prototype.forEach.call(tocLinks, function (link) {
        link.classList.toggle('is-active', link.getAttribute('href') === '#' + id);
      });
    };

    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) setActive(entry.target.id);
      });
    }, { rootMargin: '-15% 0px -70% 0px' });

    headings.forEach(function (heading) {
      observer.observe(heading);
    });
  });
})();
