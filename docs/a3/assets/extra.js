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
  const old=b.textContent; b.textContent=ok?'Kopirano ✓':'Označeno'; b.classList.add('done'); setTimeout(()=>{b.textContent=old;b.classList.remove('done');},1800);
}));
