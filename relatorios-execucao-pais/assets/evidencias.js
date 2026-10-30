
(()=>{
const G = JSON.parse(document.getElementById('gal-data').textContent);
const dlg = document.getElementById('lb'), img = dlg.querySelector('.lb-stage img'), stage = dlg.querySelector('.lb-stage');
const $ = s => dlg.querySelector(s);
let g = null, i = 0, opener = null;
function show(k){
  const L = G[g]; i = (k + L.length) % L.length; const e = L[i];
  img.classList.remove('z'); stage.classList.remove('zoom');
  img.src = e.src; img.alt = e.l;
  $('.lb-ev').textContent = e.ev; $('.lb-n').textContent = (i+1) + ' de ' + L.length + ' · ' + g;
  $('.lb-cap h5').textContent = e.t; $('.lb-cap .lg').textContent = e.l;
  $('.lb-cap .pv span').textContent = e.p; $('.lb-cap .sr').textContent = [e.f, e.d, 'coletado por Monks', e.a, 'SHA-256 ' + e.h].filter(Boolean).join(' · ');
  const one = L.length < 2; $('.lb-prev').disabled = one; $('.lb-next').disabled = one;
  $('.lb-dots').innerHTML = L.map((x,n)=>`<button type="button" aria-label="Ir para ${x.ev}" ${n===i?'aria-current="true"':''} data-n="${n}"></button>`).join('');
  [i+1, i-1].forEach(n => { const x = L[(n + L.length) % L.length]; if (x) { const p = new Image(); p.src = x.src; } });
  history.replaceState(null, '', '#' + e.ev);
}
function open(gid, k, from){ g = gid; opener = from || null; show(k); if (!dlg.open) dlg.showModal(); $('.lb-x').focus(); }
function close(){ dlg.close(); }
dlg.addEventListener('close', () => { history.replaceState(null, '', location.pathname + location.search); const cur = document.querySelector(`button.th[data-g="${g}"][data-i="${i}"]`); (cur || opener)?.focus(); });
document.querySelectorAll('button.th').forEach(b => b.addEventListener('click', () => open(b.dataset.g, +b.dataset.i, b)));
$('.lb-prev').onclick = () => show(i-1); $('.lb-next').onclick = () => show(i+1); $('.lb-x').onclick = close;
$('.lb-dots').onclick = e => { const n = e.target.dataset.n; if (n !== undefined) show(+n); };
img.onclick = () => { img.classList.toggle('z'); stage.classList.toggle('zoom'); };
dlg.addEventListener('keydown', e => {
  if (e.key === 'ArrowRight') { e.preventDefault(); show(i+1); }
  else if (e.key === 'ArrowLeft') { e.preventDefault(); show(i-1); }
  else if (e.key === 'Home') { e.preventDefault(); show(0); }
  else if (e.key === 'End') { e.preventDefault(); show(G[g].length-1); }
});
dlg.addEventListener('click', e => { if (e.target === dlg || e.target === stage) close(); });
let x0 = null, y0 = null;
stage.addEventListener('touchstart', e => { if (stage.classList.contains('zoom')) return; x0 = e.touches[0].clientX; y0 = e.touches[0].clientY; }, {passive:true});
stage.addEventListener('touchend', e => { if (x0 === null) return; const dx = e.changedTouches[0].clientX - x0, dy = e.changedTouches[0].clientY - y0; if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy)) show(i + (dx < 0 ? 1 : -1)); x0 = null; });
// link direto: #EV-A002-01 abre a galeria; #A-002 rola até a ação; #EV de dado abre o <details>
function hash(){
  const h = decodeURIComponent(location.hash.slice(1)); if (!h) return;
  const b = document.querySelector(`button.th[id="${h}"]`);
  if (b) { b.scrollIntoView({block:'center'}); open(b.dataset.g, +b.dataset.i, b); return; }
  const d = document.querySelector(`details.dado[id="${h}"]`); if (d) { d.open = true; d.scrollIntoView(); }
}
window.addEventListener('hashchange', hash); hash();
// sumário: seção atual
const links = [...document.querySelectorAll('nav.toc a')], map = new Map(links.map(a => [a.getAttribute('href').slice(1), a]));
const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { links.forEach(a => a.removeAttribute('aria-current')); const a = map.get(e.target.id); if (a) a.setAttribute('aria-current', 'true'); } }), {rootMargin:'-20% 0px -70% 0px'});
document.querySelectorAll('section.sec, article.card').forEach(s => io.observe(s));
// tema
const tb = document.querySelector('.themebtn');
tb.onclick = () => { const r = document.documentElement, d = r.dataset.theme === 'dark' || (!r.dataset.theme && matchMedia('(prefers-color-scheme: dark)').matches); r.dataset.theme = d ? 'light' : 'dark'; };
})();
