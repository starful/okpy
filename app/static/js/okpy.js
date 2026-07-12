(function () {
  function bindSearch(inputs, cards, emptyEl) {
    function runSearch(q) {
      q = (q || '').trim().toLowerCase();
      var visible = 0;
      cards.forEach(function (el) {
        if (!q) {
          el.style.display = '';
          visible++;
          return;
        }
        var text = (el.textContent || '').toLowerCase();
        var show = text.indexOf(q) !== -1;
        el.style.display = show ? '' : 'none';
        if (show) visible++;
      });
      if (emptyEl) {
        emptyEl.hidden = !q || visible > 0;
      }
    }

    inputs.forEach(function (input) {
      if (!input) return;
      input.addEventListener('input', function () {
        var q = input.value;
        inputs.forEach(function (other) {
          if (other !== input) other.value = q;
        });
        runSearch(q);
      });
    });
  }

  var cards = Array.prototype.slice.call(document.querySelectorAll('[data-searchable]'));
  var emptyEl = document.getElementById('search-empty');
  bindSearch(
    [document.getElementById('post-search')],
    cards,
    emptyEl
  );

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
})();
