// Mobile sidebar toggle + client-side search. No build step, no frameworks.
(function () {
  var sidebar = document.querySelector('.sidebar');
  var toggle = document.querySelector('.navtoggle');
  var scrim = document.querySelector('.sidebar-scrim');
  function closeNav() { sidebar.classList.remove('open'); scrim.classList.remove('show'); }
  if (toggle) {
    toggle.addEventListener('click', function () {
      sidebar.classList.toggle('open');
      scrim.classList.toggle('show');
    });
  }
  if (scrim) scrim.addEventListener('click', closeNav);

  // Highlight the current page in the sidebar.
  var here = location.pathname.replace(/^.*\//, '') || 'index.html';
  document.querySelectorAll('.navlist a').forEach(function (a) {
    var href = a.getAttribute('href');
    if (href === here || (here === '' && href === 'index.html')) a.classList.add('active');
  });

  // ---------------------------------------------------------------- search
  var input = document.getElementById('search-input');
  var results = document.getElementById('search-results');
  if (!input || !results) return;

  var indexData = null;
  var base = document.body.getAttribute('data-base') || '';
  fetch(base + 'search-index.json').then(function (r) { return r.json(); }).then(function (d) { indexData = d; });

  function render(list, q) {
    if (!list.length) { results.innerHTML = '<div style="padding:10px 12px;color:var(--ink-faint);font-size:0.85rem;">No matches for "' + q + '"</div>'; return; }
    results.innerHTML = list.slice(0, 12).map(function (r) {
      return '<a href="' + base + r.url + '">' + r.heading + '<span class="sr-page">' + r.page + '</span></a>';
    }).join('');
  }

  input.addEventListener('input', function () {
    var q = input.value.trim().toLowerCase();
    if (!q || !indexData) { results.innerHTML = ''; return; }
    var scored = [];
    for (var i = 0; i < indexData.length; i++) {
      var e = indexData[i];
      var hay = (e.heading + ' ' + e.page + ' ' + e.snippet).toLowerCase();
      var idx = hay.indexOf(q);
      if (idx >= 0) scored.push({ e: e, score: idx + (e.heading.toLowerCase().indexOf(q) >= 0 ? -1000 : 0) });
    }
    scored.sort(function (a, b) { return a.score - b.score; });
    render(scored.map(function (s) { return s.e; }), input.value.trim());
  });
  document.addEventListener('click', function (e) {
    if (!e.target.closest('.searchbox')) results.innerHTML = '';
  });
  input.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') { results.innerHTML = ''; input.blur(); }
  });
})();
