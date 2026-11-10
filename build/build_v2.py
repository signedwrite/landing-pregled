"""landing.hr v2: same content model and helpers as build.py, layout of the approved design mockup,
colors from the LAND ING logo. Output: dist2/ (published under /v2/)."""
import sys, os, shutil, html as H, datetime, re
SRC_FILE = os.path.join(os.path.dirname(__file__), 'build.py')
code = open(SRC_FILE, encoding='utf8').read().split('# ---------- build ----------')[0]
exec(code)  # brings SRC, SERVICES, SPECIAL, PRICES, LOCATIONS, PARTNERS, clean_body, rewrite_links, helpers

OUT = f'{ROOT}/dist2'
NAV2 = [('Usluge', 'index.html#usluge'), ('Posebne usluge', 'index.html#posebne'), ('Lokacije', 'index.html#lokacije'),
        ('Blog', 'news/index.html'), ('Kontakt', 'contact/index.html')]
LOC_IMG = {'geodet-osijek': 'p1.jpg', 'geodet-zadar': 'p2.jpg', 'geodet-biograd': 'p3.jpg'}

def write(path, html):
    full = os.path.join(OUT, path); os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, 'w', encoding='utf8').write(html)

def head(title, desc, p, canonical):
    return f'''<!doctype html><html lang="hr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>{H.escape(title)}</title><meta name="description" content="{H.escape(desc or '')}">
<link rel="icon" href="{p}assets/img/cropped-land_ing_ikona-32x32.jpg">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{p}assets/site.css">
</head><body>
<div class="preview-note">Radna verzija nove stranice za pregled. Prava stranica: <a href="{ORIG}{canonical}">landing.hr</a></div>
'''

def header(p, current=''):
    links = ''.join(f'<a href="{p}{u}"{" aria-current=page" if current == n else ""}>{n}</a>' for n, u in NAV2)
    return f'''<header class="site-head"><div class="wrap head-row">
<a class="brand" href="{p}index.html" aria-label="LAND ING d.o.o., naslovnica"><img src="{p}assets/img/logo-crop.png" alt="LAND ING geodetski inženjering"></a>
<button class="menu-btn" aria-expanded="false" aria-controls="nav"><span></span><span class="sr">Izbornik</span></button>
<nav id="nav" aria-label="Glavni izbornik">{links}<a class="btn" href="{p}index.html#kontakt">Zatraži ponudu</a></nav>
</div></header>'''

def footer(p):
    loc = ''.join(f'<a href="{p}{s}/index.html">{n}</a>' for s, n, _ in LOCATIONS)
    return f'''<footer class="site-foot"><div class="wrap foot-row">
<div class="foot-top">
<div class="foot-brand"><img src="{p}assets/img/logo-crop.png" alt="LAND ING geodetski inženjering"><p>LAND ING d.o.o. Mjerimo svijet.</p></div>
<div class="foot-cols">
<div><strong>Navigacija</strong><a href="{p}index.html#usluge">Usluge</a><a href="{p}index.html#posebne">Posebne usluge</a><a href="{p}index.html#lokacije">Lokacije</a><a href="{p}news/index.html">Blog</a></div>
<div><strong>Lokacije</strong>{loc}</div>
<div><strong>Kontakt</strong><a href="tel:{PHONE_TEL}">{PHONE}</a><a href="mailto:{MAIL}">{MAIL}</a><span>OIB: 30446646311</span><span>IBAN: HR1123400091111293529</span></div>
</div></div>
<div class="foot-base"><span>© {datetime.date.today().year} LAND ING d.o.o.</span><a href="{p}cookie-policy-eu/index.html">Politika kolačića (EU)</a></div>
</div></footer>
<script src="{p}assets/site.js" defer></script></body></html>'''

def post_card(po, p, tag='h3'):
    return f'''<li><a class="post" href="{p}{po["path"].strip("/")}/index.html"><time datetime="{po["date"]}">{hr_date(po["date"])}</time>
<{tag}>{H.escape(po["title"])}</{tag}>{f'<p>{H.escape(po["description"] or po["excerpt"])}</p>' if tag == 'h2' else ''}<span class="more">Pročitaj članak</span></a></li>'''

def contact_block(p, heading='Kontaktirajte nas sa povjerenjem!'):
    return f'''<section class="section soft" id="kontakt"><div class="wrap contact">
<div class="contact-copy"><p class="eyebrow">Kontakt</p><h2>{heading}</h2>
<dl class="info">
<div><dt>Poslovnice</dt><dd>Osijek i Zadar<span class="small">Molimo nazovite prije dolaska</span></dd></div>
<div><dt>Telefon</dt><dd><a href="tel:{PHONE_TEL}">{PHONE}</a><span class="small">Radnim danima od 08h do 17h</span></dd></div>
<div><dt>Email</dt><dd><a href="mailto:{MAIL}">{MAIL}</a><span class="small">Za klijente i partnere</span></dd></div>
<div><dt>Područje poslovanja</dt><dd>Zadarska, Šibensko-kninska, Zagrebačka i Osječko-baranjska županija</dd></div>
<div><dt>OIB</dt><dd>30446646311</dd></div>
<div><dt>IBAN</dt><dd>HR1123400091111293529</dd></div>
</dl></div>
<form class="form" data-mailto="{MAIL}">
<label>Vaše ime<input name="ime" required autocomplete="name"></label>
<label>Vaš email<input name="email" type="email" required autocomplete="email"></label>
<label><span>Broj telefona <span class="opt">(Neobavezno polje)</span></span><input name="telefon" type="tel" autocomplete="tel"></label>
<label><span>Broj katastarske čestice <span class="opt">(Neobavezno polje)</span></span><input name="cestica"></label>
<label>Vaša poruka<textarea name="poruka" rows="5" required></textarea></label>
<button class="btn" type="submit">Pošalji</button>
<p class="small">Vaši podaci bit će korišteni isključivo za odgovaranje na vaš upit, obradu i rješavanje vašeg zahtjeva te pružanje relevantnih informacija. Vaši podaci neće biti proslijeđeni trećim stranama niti korišteni u marketinške svrhe</p>
</form></div></section>'''

def cta_box(cta):
    h, t = cta or DEFAULT_CTA
    return f'''<div class="wrap cta-wrap"><div class="cta"><div><h2>{H.escape(h)}</h2><p>{t}</p></div>
<div class="hero-actions"><a class="btn" href="tel:{PHONE_TEL}">{PHONE}</a><a class="btn btn-line" href="mailto:{MAIL}">{MAIL}</a></div></div></div>'''

def side(p, cta, exclude=None):
    h, t = cta or DEFAULT_CTA
    links = ''.join(f'<li><a href="{p}{s["slug"]}/index.html">{s["title"]}</a></li>' for s in SERVICES if s['slug'] != exclude)
    return f'''<aside class="side"><div class="side-card"><h2>{H.escape(h)}</h2><p>{t}</p>
<a class="btn" href="tel:{PHONE_TEL}">{PHONE}</a><a class="btn btn-line" href="mailto:{MAIL}">{MAIL}</a></div>
<div class="side-links"><h2>Usluge</h2><ul>{links}</ul></div></aside>'''

def home():
    p = ''; h = HOME; why = h['why']
    intro = h['services_intro'].replace('USLUGE ', '', 1)
    lead, rest = intro.split(' GEODETSKE ELABORATE KATASTARSKE GEODEZIJE I ZEMLJIŠNE KNJIGE ')
    nums = ''.join(f'<li><strong>{c["value"]}{c["suffix"]}</strong><span>{c["label"]}</span></li>' for c in h['counters'])
    points = ''.join(f'<li>{x}</li>' for x in why['points'])
    svc = ''.join(f'<li{" class=wide" if i == 6 else ""}><a class="card" href="{p}{s["slug"]}/index.html"><h3>{s["title"]}</h3><p>{H.escape(s["text"])}</p><span class="more">Saznajte više</span></a></li>' for i, s in enumerate(SERVICES))
    def sp_title(t):
        m = re.match(r'(.+?)\s*(\(.+\))$', t)
        return f'{m.group(1)} <small>{m.group(2)}</small>' if m else t
    special = ''.join(f'<li><{"a" if x["slug"] else "div"} class="card"{f" href={chr(34)}{p}{x[chr(115)+chr(108)+chr(117)+chr(103)]}/index.html{chr(34)}" if x["slug"] else ""}><h3>{sp_title(x["title"])}</h3><p>{H.escape(x["text"])}</p>{"<span class=more>Saznajte više</span>" if x["slug"] else ""}</{"a" if x["slug"] else "div"}></li>' for x in SPECIAL)
    prices = ''.join(f'<tr><td>{f"<a href={chr(34)}{p}{sl}/index.html{chr(34)}>{n}</a>" if sl else n}</td><td>{pr}</td><td>{t}</td></tr>' for n, sl, pr, t in PRICES)
    locs = ''.join(f'<li><a class="loc" href="{p}{s}/index.html"><div class="loc-img" style="background-image:url({p}assets/img/{LOC_IMG[s]})"></div><div class="loc-body"><h3>{n}</h3><p>{d}</p><span class="more">Saznajte više</span></div></a></li>' for s, n, d in LOCATIONS)
    partners = ''.join(f'<li><a class="partner" href="{u}" target="_blank" rel="noopener"><img src="{p}assets/img/{l}" alt=""><div><strong>{n}</strong><span>{d}</span></div></a></li>' for n, d, u, l in PARTNERS)
    posts = sorted(SRC['posts'], key=lambda x: x['date'], reverse=True)[:3]
    blog = ''.join(post_card(po, p) for po in posts)
    html = head('LAND ING d.o.o. | Geodetske usluge Osijek, Zadar, Biograd | Etažiranje, Parcelacija', 'LAND ING d.o.o. – geodetske usluge Osijek, Zadar, Biograd.', p, '/') + header(p) + f'''
<main id="vrh">
<section class="hero"><div class="hero-copy">
<p class="eyebrow" style="text-transform:none;letter-spacing:.04em;font-size:15px">LAND ING d.o.o.</p>
<h1>Mjerimo svijet.</h1>
<p class="lead">{why["headline"]}</p>
<div class="hero-actions"><a class="btn" href="#kontakt">Zatraži ponudu</a><a class="btn btn-line" href="tel:{PHONE_TEL}">Nazovite nas: {PHONE}</a></div>
<p class="hero-note">Odgovaramo u roku 24 sata</p>
</div><div class="hero-img" role="img" aria-label="Geodet s totalnom stanicom i dronom na terenu"></div></section>

<section class="numbers"><ul>{nums}</ul></section>

<section class="section" id="o-nama"><div class="wrap why">
<div class="why-copy"><p class="eyebrow">Zašto mi?</p><h2>{why["sub"]}</h2><p>{why["text"]}</p><ul class="checks">{points}</ul>
<div><a class="btn" href="#usluge">Naše usluge</a></div></div>
<div class="why-img" role="img" aria-label="Terensko vozilo i GNSS prijemnik na terenu"></div>
</div></section>

<section class="section soft" id="usluge"><div class="wrap">
<div class="head-center"><p class="eyebrow">Usluge</p><h2>{lead}</h2><p>{rest}</p></div>
<ul class="cards">{svc}</ul>
</div></section>

<section class="section" id="posebne"><div class="wrap">
<div class="head-center"><h2>Posebne usluge</h2></div>
<ul class="cards cards-2">{special}</ul>
</div></section>

<section class="section soft" id="cjenik"><div class="wrap">
<div class="head-center"><h2>Cijene</h2></div>
<div class="table-wrap"><table class="prices"><thead><tr><th>Usluga</th><th>Cijena</th><th>Rok izrade</th></tr></thead><tbody>{prices}</tbody></table></div>
<p class="small price-note">{PRICE_NOTE}</p>
</div></section>

<section class="section" id="lokacije"><div class="wrap">
<div class="head-center"><h2>Lokacije</h2></div>
<ul class="cards">{locs}</ul>
</div></section>

<section class="section soft"><div class="wrap">
<div class="head-center"><h2>Naši partneri</h2></div>
<ul class="cards">{partners}</ul>
</div></section>

<section class="section"><div class="wrap">
<div class="row-head"><h2>Blog</h2><a class="btn btn-line" href="{p}news/index.html">Svi članci</a></div>
<ul class="cards">{blog}</ul>
</div></section>

{contact_block(p)}
</main>''' + footer(p)
    write('index.html', html)

def inner_page(slug, kind):
    page = SRC['pages'][slug]; path = f'{slug}/index.html'; p = prefix_for(path)
    body, cta = clean_body(page['html'])
    title, sub = page['title'], ''
    if kind == 'loc':
        from bs4 import BeautifulSoup
        s = BeautifulSoup(body, 'lxml'); hs = s.find_all(['h2', 'h3'])
        if hs: title = hs[0].get_text(' ', strip=True); hs[0].decompose()
        hs = s.find_all(['h2', 'h3'])
        if hs: sub = hs[0].get_text(' ', strip=True); hs[0].decompose()
        body = ''.join(str(c) for c in (s.body or s).children)
    body = rewrite_links(body, p)
    price = next(((pr, t) for n, sl, pr, t in PRICES if sl == slug), None)
    facts = f'<dl class="facts"><div><dt>Cijena</dt><dd>{price[0]}</dd></div><div><dt>Rok izrade</dt><dd>{price[1]}</dd></div></dl>' if price else ''
    section = {'svc': ('Usluge', 'index.html#usluge'), 'special': ('Posebne usluge', 'index.html#posebne'), 'loc': ('Lokacije', 'index.html#lokacije')}[kind]
    eyebrow = sentence(page['eyebrow']) if page.get('eyebrow') else section[0]
    html = head(page['doc_title'] or title, page['description'], p, f'/{slug}/') + header(p, section[0]) + f'''
<main><section class="page-hero"><div class="wrap"><div class="inner">
<a class="crumbs" href="{p}{section[1]}">← {section[0]}</a>
<p class="eyebrow">{H.escape(eyebrow)}</p>
<h1>{H.escape(title)}</h1>{f'<p class="lead">{H.escape(sub)}</p>' if sub else ''}{facts}
<div class="hero-actions"><a class="btn" href="{p}index.html#kontakt">Zatraži ponudu</a><a class="btn btn-line" href="tel:{PHONE_TEL}">{PHONE}</a></div>
</div></div></section>
<div class="wrap layout"><article class="prose">{body}</article>{side(p, cta, slug)}</div>
{cta_box(cta)}</main>''' + footer(p)
    write(path, html)

def post_page(po):
    path = po['path'].strip('/') + '/index.html'; p = prefix_for(path)
    body, cta = clean_body(po['html']); body = rewrite_links(body, p)
    def score(x): return len(set(x['title'].lower().split()) & set(po['title'].lower().split()))
    rel = sorted([x for x in SRC['posts'] if x['slug'] != po['slug']], key=score, reverse=True)[:3]
    html = head(po['title'] + ' - LAND ING d.o.o.', po['description'], p, po['path']) + header(p, 'Blog') + f'''
<main><section class="page-hero"><div class="wrap"><div class="inner">
<a class="crumbs" href="{p}news/index.html">← Svi članci</a>
<p class="eyebrow">Blog · <time datetime="{po["date"]}">{hr_date(po["date"])}</time></p>
<h1>{H.escape(po["title"])}</h1></div></div></section>
<div class="wrap layout"><article class="prose">{body}</article>{side(p, cta)}</div>
<section class="section soft"><div class="wrap"><div class="head-left"><h2>Povezani članci</h2></div><ul class="cards">{''.join(post_card(x, p) for x in rel)}</ul></div></section>
<div style="height:96px"></div>{cta_box(cta)}</main>''' + footer(p)
    write(path, html)

def blog_index():
    path = 'news/index.html'; p = '../'
    posts = sorted(SRC['posts'], key=lambda x: x['date'], reverse=True)
    html = head('Blog - LAND ING d.o.o.', '', p, '/news/') + header(p, 'Blog') + f'''
<main><section class="page-hero"><div class="wrap"><div class="inner"><p class="eyebrow">Blog</p><h1>Blog</h1></div></div></section>
<div class="wrap"><ul class="blog-grid">{''.join(post_card(po, p, 'h2') for po in posts)}</ul></div>
{cta_box(None)}</main>''' + footer(p)
    write(path, html)

def contact_page():
    path = 'contact/index.html'; p = '../'
    html = head('Kontakt - LAND ING d.o.o.', '', p, '/contact/') + header(p, 'Kontakt') + f'''
<main><section class="page-hero"><div class="wrap"><div class="inner"><p class="eyebrow">Kontakt</p><h1>Javite nam se s povjerenjem</h1></div></div></section>
{contact_block(p, 'Kontaktirajte nas sa povjerenjem!')}</main>''' + footer(p)
    write(path, html)

def cookie_page():
    page = SRC['pages']['cookie-policy-eu']; path = 'cookie-policy-eu/index.html'; p = '../'
    body, _ = clean_body(page['html']); body = rewrite_links(body, p)
    html = head('Politika kolačića (EU) - LAND ING d.o.o.', '', p, '/cookie-policy-eu/') + header(p) + f'''
<main><section class="page-hero"><div class="wrap"><div class="inner"><h1>Politika kolačića (EU)</h1></div></div></section>
<div class="wrap layout" style="grid-template-columns:1fr"><article class="prose">{body}</article></div></main>''' + footer(p)
    write(path, html)

if os.path.exists(OUT): shutil.rmtree(OUT)
os.makedirs(OUT)
shutil.copytree(f'{ROOT}/site2/assets', f'{OUT}/assets')
shutil.copy(f'{ROOT}/site/assets/site.js', f'{OUT}/assets/site.js')
home()
for s in SERVICES: inner_page(s['slug'], 'svc')
for x in SPECIAL:
    if x['slug']: inner_page(x['slug'], 'special')
for s, *_ in LOCATIONS: inner_page(s, 'loc')
for po in SRC['posts']: post_page(po)
blog_index(); contact_page(); cookie_page()
print('built v2', sum(len(f) for _, _, f in os.walk(OUT)), 'files')
