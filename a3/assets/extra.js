// Count-up numbers (as on the current site)
(function(){
  const els=[...document.querySelectorAll('.count[data-to]')]; if(!els.length) return;
  const reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
  const run=el=>{const to=+el.dataset.to; if(reduce){el.textContent=to;return;}
    const t0=performance.now(), d=1800; const step=t=>{const k=Math.min(1,(t-t0)/d); el.textContent=Math.round(to*(1-Math.pow(1-k,3))); if(k<1) requestAnimationFrame(step);}; requestAnimationFrame(step);};
  els.forEach(el=>el.textContent='0');
  const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){run(e.target);io.unobserve(e.target);}}),{threshold:.4});
  els.forEach(el=>io.observe(el));
})();
// Copy OIB / IBAN
document.querySelectorAll('.copy-btn').forEach(b=>b.addEventListener('click',async()=>{
  const v=b.dataset.copy; let ok=false;
  try{await navigator.clipboard.writeText(v);ok=true;}catch(e){
    const r=document.createRange(); r.selectNodeContents(b.previousElementSibling); const s=getSelection(); s.removeAllRanges(); s.addRange(r); ok=document.execCommand&&document.execCommand('copy');}
  const old=b.textContent; b.textContent=ok?(b.dataset.done||'✓'):'✓'; b.classList.add('done'); setTimeout(()=>{b.textContent=old;b.classList.remove('done');},1800);
}));
/* Google recenzije: auto-rotacija + ručno listanje */
(function(){
  var t=document.querySelector('.rv-track'); if(!t) return;
  var cards=t.children, timer, paused=false;
  function step(){var c=cards[0]; return c ? c.getBoundingClientRect().width+18 : 300;}
  function go(dir){
    var max=t.scrollWidth-t.clientWidth-4;
    if(dir>0 && t.scrollLeft>=max){t.scrollLeft=0;return;}
    if(dir<0 && t.scrollLeft<=4){t.scrollLeft=t.scrollWidth;return;}
    t.scrollBy({left:dir*step(),behavior:'smooth'});
  }
  var p=document.querySelector('.rv-prev'), n=document.querySelector('.rv-next');
  if(p) p.addEventListener('click',function(){go(-1);restart();});
  if(n) n.addEventListener('click',function(){go(1);restart();});
  function start(){ if(window.matchMedia('(prefers-reduced-motion: reduce)').matches) return; timer=setInterval(function(){ if(!paused && !document.hidden) go(1); },5000); }
  function restart(){clearInterval(timer);start();}
  ['mouseenter','focusin','touchstart'].forEach(function(e){t.addEventListener(e,function(){paused=true;},{passive:true});});
  ['mouseleave','focusout'].forEach(function(e){t.addEventListener(e,function(){paused=false;});});
  t.addEventListener('touchend',function(){setTimeout(function(){paused=false;},6000);},{passive:true});
  t.querySelectorAll('.rv-more').forEach(function(b){b.addEventListener('click',function(){
    var c=b.closest('.rv-card'), o=c.classList.toggle('open'); b.textContent=o?b.dataset.less:b.dataset.more; b.setAttribute('aria-expanded',o); paused=o;
  });});
  if('IntersectionObserver' in window){ new IntersectionObserver(function(es){ es.forEach(function(e){ if(e.isIntersecting){ if(!timer) start(); } }); }).observe(t); } else start();
})();
