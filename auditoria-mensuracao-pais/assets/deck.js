
(function(){
  var deck=document.getElementById('deck');
  var slides=[].slice.call(document.querySelectorAll('.slide'));
  var bar=document.getElementById('bar'), cnt=document.getElementById('cnt');
  var tot=slides.length, i=-1;
  var apx=slides.findIndex(function(s){return s.hasAttribute('data-first-apx')});
  function fit(){
    var s=Math.min(innerWidth/1920, innerHeight/1080);
    var x=(innerWidth-1920*s)/2, y=(innerHeight-1080*s)/2;
    deck.style.transform='translate('+x+'px,'+y+'px) scale('+s+')';
  }
  function go(n, noHash){
    n=Math.max(0,Math.min(tot-1,n));
    if(n===i) return;
    if(i>=0){slides[i].classList.remove('active');slides[i].setAttribute('aria-hidden','true');}
    i=n; slides[i].classList.add('active'); slides[i].removeAttribute('aria-hidden');
    bar.style.width=((i+1)/tot*100)+'%';
    cnt.textContent=(i+1)+' / '+tot;
    if(!noHash) history.replaceState(null,'','#/'+(i+1));
  }
  function fromHash(){var m=location.hash.match(/^#\/(\d+)/); return m?parseInt(m[1],10)-1:0;}
  slides.forEach(function(s){s.setAttribute('aria-hidden','true')});
  document.addEventListener('keydown',function(e){
    if(e.metaKey||e.ctrlKey||e.altKey) return;
    var k=e.key;
    if(k==='ArrowRight'||k==='PageDown'||(k===' '&&!e.shiftKey)){e.preventDefault();go(i+1);}
    else if(k==='ArrowLeft'||k==='PageUp'||(k===' '&&e.shiftKey)){e.preventDefault();go(i-1);}
    else if(k==='Home'){e.preventDefault();go(0);}
    else if(k==='End'){e.preventDefault();go(tot-1);}
    else if(k==='n'||k==='N'){document.body.classList.toggle('show-notes');}
    else if((k==='a'||k==='A')&&apx>=0){go(apx);}
    else if(k==='t'||k==='T'){
      var r=document.documentElement, c=r.getAttribute('data-theme');
      r.setAttribute('data-theme', c==='dark'?'light':(c==='light'?'':'dark'));
      if(!r.getAttribute('data-theme')) r.removeAttribute('data-theme');
    }
  });
  addEventListener('hashchange',function(){go(fromHash(),true)});
  addEventListener('resize',fit);
  fit(); go(fromHash(),true);
})();
