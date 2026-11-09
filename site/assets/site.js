// Mobile menu
const btn = document.querySelector('.menu-btn'), nav = document.getElementById('nav');
if (btn && nav) {
  btn.addEventListener('click', () => {
    const open = btn.getAttribute('aria-expanded') !== 'true';
    btn.setAttribute('aria-expanded', open);
    nav.classList.toggle('open', open);
  });
  nav.addEventListener('click', e => { if (e.target.closest('a')) { btn.setAttribute('aria-expanded', 'false'); nav.classList.remove('open'); } });
}
// Contact form: the preview has no server, so it opens a pre-filled e-mail.
document.querySelectorAll('form[data-mailto]').forEach(f => f.addEventListener('submit', e => {
  e.preventDefault();
  const d = new FormData(f);
  const body = `Ime: ${d.get('ime')}\nE-mail: ${d.get('email')}\nTelefon: ${d.get('telefon') || '-'}\nČestica / k.o.: ${d.get('cestica') || '-'}\n\n${d.get('poruka')}`;
  location.href = `mailto:${f.dataset.mailto}?subject=${encodeURIComponent('Upit s web stranice')}&body=${encodeURIComponent(body)}`;
}));
