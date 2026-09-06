(function () {
  var dropdown = document.querySelector('.nav-dropdown');
  var toggle = document.getElementById('topics-toggle');
  if (dropdown && toggle) {
    toggle.addEventListener('click', function (e) {
      e.stopPropagation();
      var open = dropdown.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    document.addEventListener('click', function () {
      dropdown.classList.remove('is-open');
      toggle.setAttribute('aria-expanded', 'false');
    });
  }

  var burger = document.getElementById('nav-burger');
  var mobileNav = document.getElementById('mobile-nav');
  if (burger && mobileNav) {
    burger.addEventListener('click', function () {
      var open = mobileNav.classList.toggle('is-open');
      mobileNav.hidden = !open;
      burger.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }
  var toc = document.querySelector(".home-toc");
  if (toc && "IntersectionObserver" in window) {
    var links = [].slice.call(toc.querySelectorAll("[data-toc-target]"));
    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          var id = entry.target.id;
          links.forEach(function (a) {
            a.classList.toggle("is-active", a.getAttribute("data-toc-target") === id);
          });
        });
      },
      { rootMargin: "-25% 0px -65% 0px", threshold: 0 }
    );
    links.forEach(function (a) {
      a.addEventListener("click", function (e) {
        var el = document.getElementById(a.getAttribute("data-toc-target"));
        if (!el) return;
        e.preventDefault();
        var offset = 80;
        var top = el.getBoundingClientRect().top + window.pageYOffset - offset;
        window.scrollTo({ top: Math.max(0, top), behavior: "smooth" });
        if (history.replaceState) {
          history.replaceState(null, "", a.getAttribute("href"));
        }
      });
      var el = document.getElementById(a.getAttribute("data-toc-target"));
      if (el) observer.observe(el);
    });
  }
})();
