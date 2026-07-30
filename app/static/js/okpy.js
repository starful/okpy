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
})();
