
(function(){
 const cards=[...document.querySelectorAll('article.card')];const live=document.getElementById('live');
 const state={crit:new Set(),pilar:new Set()};
 function apply(){let n=0;cards.forEach(c=>{const ok=(!state.crit.size||state.crit.has(c.dataset.crit))&&(!state.pilar.size||state.pilar.has(c.dataset.pilar));c.hidden=!ok;if(ok)n++});
  clearTimeout(apply.t);apply.t=setTimeout(()=>{live.textContent=n+' de '+cards.length+' achados exibidos'},300);
  const p=new URLSearchParams();if(state.crit.size)p.set('crit',[...state.crit].join(','));if(state.pilar.size)p.set('pilar',[...state.pilar].join(','));
  try{history.replaceState(null,'',(p.toString()?'?'+p:location.pathname)+location.hash)}catch(e){}}
 document.querySelectorAll('.chip').forEach(b=>{b.addEventListener('click',()=>{const k=b.dataset.k,v=b.dataset.v;const on=b.getAttribute('aria-pressed')!=='true';b.setAttribute('aria-pressed',on);on?state[k].add(v):state[k].delete(v);apply()})});
 document.getElementById('clear').addEventListener('click',()=>{state.crit.clear();state.pilar.clear();document.querySelectorAll('.chip').forEach(b=>b.setAttribute('aria-pressed','false'));apply()});
 const q=new URLSearchParams(location.search);['crit','pilar'].forEach(k=>{(q.get(k)||'').split(',').filter(Boolean).forEach(v=>{state[k].add(v);const b=document.querySelector('.chip[data-k="'+k+'"][data-v="'+v+'"]');if(b)b.setAttribute('aria-pressed','true')})});apply();
 document.getElementById('openall').addEventListener('click',()=>document.querySelectorAll('details').forEach(d=>d.open=true));
 document.getElementById('closeall').addEventListener('click',()=>document.querySelectorAll('details').forEach(d=>d.open=false));
 document.querySelectorAll('.tf').forEach(box=>{const t=document.getElementById(box.dataset.for);if(!t)return;const rows=[...t.tBodies[0].rows];const sels=[...box.querySelectorAll('select')];const q=box.querySelector('input');const out=box.querySelector('.tfn');
  function ap(){const v=q?q.value.trim().toLowerCase():'';let n=0;rows.forEach(r=>{const ok=sels.every(s=>!s.value||r.dataset[s.dataset.a]===s.value)&&(!v||(r.dataset.q||'').includes(v));r.classList.toggle('fh',!ok);if(ok)n++});out.textContent=n+' de '+rows.length+' linhas'}
  sels.forEach(s=>s.addEventListener('change',ap));if(q)q.addEventListener('input',ap);ap()});
 window.addEventListener('beforeprint',()=>document.querySelectorAll('details').forEach(d=>d.open=true));
 const links=[...document.querySelectorAll('nav.toc a')];const map=new Map(links.map(a=>[a.getAttribute('href').slice(1),a]));
 const io=new IntersectionObserver(es=>{es.forEach(en=>{if(en.isIntersecting){links.forEach(l=>l.removeAttribute('aria-current'));const a=map.get(en.target.id);if(a)a.setAttribute('aria-current','true')}})},{rootMargin:'0px 0px -75% 0px'});
 map.forEach((a,id)=>{const el=document.getElementById(id);if(el)io.observe(el)});
})();
