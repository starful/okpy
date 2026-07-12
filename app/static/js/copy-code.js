(function () {
  function copyText(text) {
    return new Promise(function (resolve, reject) {
      var ta = document.createElement('textarea');
      ta.value = text;
      ta.setAttribute('readonly', '');
      ta.style.position = 'fixed';
      ta.style.top = '0';
      ta.style.left = '0';
      ta.style.width = '2em';
      ta.style.height = '2em';
      ta.style.opacity = '0';
      document.body.appendChild(ta);
      ta.focus();
      ta.select();
      ta.setSelectionRange(0, text.length);
      var ok = false;
      try {
        ok = document.execCommand('copy');
      } catch (e) {
        ok = false;
      }
      document.body.removeChild(ta);
      if (ok) {
        resolve();
        return;
      }
      if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(resolve).catch(reject);
        return;
      }
      reject(new Error('copy failed'));
    });
  }

  function getCodeText(btn) {
    var block = btn.closest('.code-block');
    if (!block) return '';
    var pre = block.querySelector('pre');
    if (!pre) return '';
    var code = pre.querySelector('code');
    return (code ? code.textContent : pre.textContent) || '';
  }

  function showCopied(btn) {
    btn.textContent = 'コピーしました';
    btn.classList.add('copied');
    setTimeout(function () {
      btn.textContent = 'コピー';
      btn.classList.remove('copied');
    }, 2000);
  }

  document.addEventListener('click', function (e) {
    var btn = e.target.closest('.code-copy-btn');
    if (!btn) return;
    e.preventDefault();
    var text = getCodeText(btn);
    if (!text) return;
    copyText(text).then(function () {
      showCopied(btn);
    }).catch(function () {
      btn.textContent = '失敗';
      setTimeout(function () {
        btn.textContent = 'コピー';
      }, 2000);
    });
  });
})();
