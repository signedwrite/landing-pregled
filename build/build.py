"""Static site generator for the landing.hr preview.
All visible text comes from the existing landing.hr (content/site.json); only layout and design change.
Every internal URL is relative, so the output works on any host or sub-path."""
import json, os, re, shutil, sys, html as H, datetime
from bs4 import BeautifulSoup

ROOT = sys.argv[1]
SRC = json.load(open(f'{ROOT}/content/site.json', encoding='utf8'))
HOME = SRC['home']
OUT = f'{ROOT}/dist'
IMG = f'{ROOT}/site/assets/img'
PHONE, PHONE_TEL, MAIL = '+385 92 233 5366', '+385922335366', 'office@landing.hr'
ORIG = 'https://landing.hr'
DEFAULT_CTA = ('Trebate geodetske usluge?', 'Kontaktirajte nas za besplatnu ponudu. Odgovaramo u roku 24 sata!')

ACRONYMS = {'gis': 'GIS', '3d': '3D', 'hkoig': 'HKOIG', 'gml': 'GML', 'rh': 'RH'}
def sentence(t):
    t = re.sub(r'\s+', ' ', t).strip()
    if not t.isupper(): return t
    t = t.lower()
    t = re.sub(r'\b(\w+)\b', lambda m: ACRONYMS.get(m.group(1), m.group(1)), t)
    return t[:1].upper() + t[1:]
def ws(t): return re.sub(r'\s+', ' ', t).strip()

# ---------- content model (texts from the current homepage, in its order) ----------
SVC_SLUGS = ['parcelacijski-elaborat', 'upis-objekta', 'evidentiranje-promjena-oblika-povrsine-cestice',
             'geodetski-elaborat-za-legalizaciju', 'geodetska-situacija-za-projektiranje', 'etaziranje-objekata',
             'posredovanje-prodaja-kupnja-nekretnina']
SERVICES = []
for slug, s in zip(SVC_SLUGS, HOME['services']):
    title = sentence(s['title']).replace('Geodestka', 'Geodetska').replace('Etažiranja objekata', 'Etažiranje objekata')
    name = os.path.basename(s['img']).replace('Large.jpeg', 'Large-1024x682.jpeg')
    SERVICES.append(dict(slug=slug, title=title, text=ws(s['text']), img=name, photo=name.endswith(('jpeg', 'jpg')) and 'EVIDENT' not in name))
SPECIAL_SLUGS = ['inzenjerska-geodezija', 'aerofotogrametrija-dron', '3d-lasersko-skeniranje', None]
SPECIAL = [dict(slug=sl, title=sentence(x['title']).replace('AEROFOTOGRAMETRIJA', 'Aerofotogrametrija'), text=ws(x['text'])) for sl, x in zip(SPECIAL_SLUGS, HOME['special'])]
# price list exactly as provided by LAND ING
PRICES = [('Elaborat upisa objekta', 'upis-objekta', 'od 500 €', '7-14 dana'), ('Parcelacija zemljišta', 'parcelacijski-elaborat', 'od 500 €', '14-21 dan'),
          ('Etažiranje', 'etaziranje-objekata', 'od 400 €', '10-15 dana'), ('Iskolčenje građevine', None, 'od 300 €', '1-3 dana'),
          ('Iskolčenje (određivanje) međe', None, 'od 200 €', '1-3 dana'), ('Geodetski elaborat za legalizaciju', 'geodetski-elaborat-za-legalizaciju', 'od 500 €', '5-10 dana')]
PRICE_NOTE = '* Navedene cijene su orijentacijske. Kontaktirajte nas za besplatnu ponudu prilagođenu vašem projektu.'
LOCATIONS = [('geodet-osijek', 'Geodetske usluge Osijek', 'Pouzdane geodetske usluge za Slavoniju i Baranju'),
             ('geodet-zadar', 'Geodetske usluge Zadar', 'Stručne geodetske usluge za Zadarsku županiju'),
             ('geodet-biograd', 'Geodetske usluge Biograd na Moru', 'Geodetske usluge za Biograd i okolicu')]
PARTNERS = [('GIS d.o.o.', 'Geodetske usluge', 'https://www.gis-osijek.com/', 'grbWeb1.png'),
            ('Genius GIS d.o.o.', 'Geoinformacijski sustavi', 'https://genius-gis.hr/', 'LOGO.png'),
            ('ACES d.o.o. Zadar', 'Projektiranje i konzalting', 'https://www.aces.hr/', 'aces-logo-2-copy-1189x523.png')]
NAV = [('Home', 'index.html'), ('O nama', 'index.html#o-nama'), ('Usluge', 'index.html#usluge'), ('Posebne usluge', 'index.html#posebne'),
       ('Lokacije', 'index.html#lokacije'), ('Kontakt', 'contact/index.html'), ('Blog', 'news/index.html')]
LOCAL_IMG = set(os.listdir(IMG))

# ---------- html cleanup ----------
def clean_body(html):
    """Returns (body_html, cta) — the page's own closing call-to-action is lifted out so the template can show it."""
    s = BeautifulSoup(html, 'lxml'); body = s.body or s
    for im in body.find_all('img'):
        if re.search(r'logo|ikona|53e4d4b3', im.get('src', '')): im.decompose()
    for h in body.find_all(re.compile('^h[1-6]$')):  # all-caps section labels from the old layout
        t = h.get_text(' ', strip=True)
        if t and t.isupper() and len(t) < 40 and not re.search(r'\d', t): h.decompose()
    cta = None
    for h in body.find_all(re.compile('^h[23]$')):
        t = h.get_text(' ', strip=True)
        if re.match(r'(Trebate|Kontaktirajte nas)', t):
            sibs = list(h.find_next_siblings())
            first_p = next((x for x in sibs if x.name == 'p'), None)
            cta = (t, first_p.decode_contents().strip() if first_p else '')
            for sib in sibs: sib.decompose()
            h.decompose(); break
    for p in body.find_all('p'):
        if not p.get_text(strip=True) and not p.find('img'): p.decompose()
        else:
            for t in p.find_all(string=True): t.replace_with(re.sub(r'\s+', ' ', t))
    for b in body.find_all('b'): b.name = 'strong'
    for i in body.find_all('i'): i.name = 'em'
    for t in body.find_all('table'):
        rows = t.find_all('tr')
        if rows and not t.find('th'):
            for td in rows[0].find_all('td'): td.name = 'th'
        t.wrap(s.new_tag('div', attrs={'class': 'table-wrap'}))
    return ''.join(str(c) for c in body.children), cta

def rewrite_links(html, prefix):
    def fix(m):
        attr, url = m.group(1), m.group(2)
        u = url.replace('https://landing.hr', '').replace('http://landing.hr', '')
        if attr == 'src':
            name = os.path.basename(u.split('?')[0])
            if name in LOCAL_IMG: return f'src="{prefix}assets/img/{name}"'
            return f'src="{ORIG}{u}"' if u.startswith('/wp-content') else m.group(0)
        if u.startswith('/') and not u.startswith('//'):
            path, _, frag = u.partition('#'); path = path.strip('/')
            if path in ('', 'home', 'gis-geoinformacijski-sustavi', 'o-nama', 'usluge', 'kontakt'): tgt = 'index.html'
            elif path == 'news': tgt = 'news/index.html'
            else: tgt = path + '/index.html'
            return f'href="{prefix}{tgt}{"#" + frag if frag else ""}"'
        return m.group(0)
    return re.sub(r'(href|src)="([^"]*)"', fix, html)

def img(name, prefix): return f'{prefix}assets/img/{name}'
def prefix_for(path): return '../' * path.count('/')
def write(path, html):
    full = os.path.join(OUT, path); os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, 'w', encoding='utf8').write(html)

# ---------- layout ----------
def head(title, desc, prefix, canonical):
    return f'''<!doctype html><html lang="hr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>{H.escape(title)}</title><meta name="description" content="{H.escape(desc or '')}">
<link rel="icon" href="{prefix}assets/img/cropped-land_ing_ikona-32x32.jpg">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@75..100,400..800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{prefix}assets/site.css">
</head><body>
<div class="preview-note">Radna verzija nove stranice za pregled. Prava stranica: <a href="{ORIG}{canonical}">landing.hr</a></div>
<div class="topbar"><div class="wrap topbar-row"><span>Nazovite nas</span><a href="tel:{PHONE_TEL}">{PHONE}</a><a href="mailto:{MAIL}">{MAIL}</a><span class="topbar-hours">Radnim danima od 08h do 17h</span></div></div>
'''

def header(prefix, current=''):
    links = ''.join(f'<li><a href="{prefix}{u}"{" aria-current=page" if current == n else ""}>{n}</a></li>' for n, u in NAV)
    return f'''<header class="site-head"><div class="wrap head-row">
<a class="brand" href="{prefix}index.html" aria-label="LAND ING d.o.o., naslovnica"><img src="{prefix}assets/img/logo-crop.png" alt="LAND ING geodetski inženjering"></a>
<button class="menu-btn" aria-expanded="false" aria-controls="nav"><span></span><span class="sr">Izbornik</span></button>
<nav id="nav" aria-label="Glavni izbornik"><ul>{links}</ul></nav>
</div></header>'''

def cta_band(cta):
    h, t = cta or DEFAULT_CTA
    return f'''<section class="cta-band"><div class="wrap cta-row">
<div><h2>{H.escape(h)}</h2><p>{t}</p></div>
<div class="cta-actions"><a class="btn" href="tel:{PHONE_TEL}">{PHONE}</a><a class="btn btn-ghost" href="mailto:{MAIL}">{MAIL}</a></div>
</div></section>'''

def side(prefix, cta, exclude=None):
    h, t = cta or DEFAULT_CTA
    links = ''.join(f'<li><a href="{prefix}{s["slug"]}/index.html">{s["title"]}</a></li>' for s in SERVICES if s['slug'] != exclude)
    return f'''<aside class="side"><div class="side-card"><h2>{H.escape(h)}</h2><p>{t}</p>
<a class="btn" href="tel:{PHONE_TEL}">{PHONE}</a><a class="btn btn-ghost" href="mailto:{MAIL}">{MAIL}</a></div>
<div class="side-links"><h2>Usluge</h2><ul>{links}</ul></div></aside>'''

def footer(prefix):
    svc = ''.join(f'<li><a href="{prefix}{s["slug"]}/index.html">{s["title"]}</a></li>' for s in SERVICES)
    loc = ''.join(f'<li><a href="{prefix}{s}/index.html">{n}</a></li>' for s, n, _ in LOCATIONS)
    return f'''<footer class="site-foot"><div class="wrap foot-grid">
<div><img src="{prefix}assets/img/logo-crop.png" alt="LAND ING geodetski inženjering" class="foot-logo">
<p><strong>LAND ING d.o.o.</strong><br>Mjerimo svijet</p>
<p>Za klijente i partnere<br><a href="tel:{PHONE_TEL}">tel. {PHONE}</a><br><a href="mailto:{MAIL}">{MAIL}</a><br>Radnim danima od 08h do 17h</p></div>
<div><h3>Usluge</h3><ul>{svc}</ul></div>
<div><h3>Lokacije</h3><ul>{loc}</ul><h3>Podaci o tvrtki</h3><p class="small">OIB 30446646311<br>IBAN HR1123400091111293529</p></div>
</div><div class="wrap foot-base"><span>© {datetime.date.today().year} LAND ING d.o.o.</span><a href="{prefix}cookie-policy-eu/index.html">Politika kolačića (EU)</a></div></footer>
<script src="{prefix}assets/site.js" defer></script></body></html>'''

def crumbs(items, p):
    li = ''.join(f'<li><a href="{p}{u}">{n}</a></li>' if u else f'<li aria-current="page">{n}</li>' for n, u in items)
    return f'<nav class="crumbs" aria-label="Putanja"><ol>{li}</ol></nav>'

MONTHS = ['siječnja', 'veljače', 'ožujka', 'travnja', 'svibnja', 'lipnja', 'srpnja', 'kolovoza', 'rujna', 'listopada', 'studenoga', 'prosinca']
def hr_date(d):
    y, m, dd = d.split('-'); return f'{int(dd)}. {MONTHS[int(m) - 1]} {y}.'

def contact_section(p, heading='Kontaktirajte nas sa povjerenjem!'):
    return f'''<section class="section section-tint" id="kontakt"><div class="wrap split">
<div><h2>{heading}</h2>
<dl class="contact-dl">
<dt>Poslovnice</dt><dd>Osijek i Zadar</dd>
<dt>Područje poslovanja</dt><dd>Zadarska, Šibensko-kninska, Zagrebačka i Osječko-baranjska županija</dd>
<dt>E-mail</dt><dd><a href="mailto:{MAIL}">{MAIL}</a><br><span class="small">Molimo nazovite prije dolaska</span></dd>
<dt>Telefon</dt><dd><a href="tel:{PHONE_TEL}">tel. {PHONE}</a><br><span class="small">Za klijente i partnere. Radnim danima od 08h do 17h</span></dd>
<dt>OIB</dt><dd>30446646311</dd>
<dt>IBAN</dt><dd>HR1123400091111293529</dd>
</dl></div>
<form class="form" data-mailto="{MAIL}">
<label>Vaše ime<input name="ime" required autocomplete="name"></label>
<label>Vaš email<input name="email" type="email" required autocomplete="email"></label>
<div class="form-row"><label><span>Broj telefona <span class="opt">(Neobavezno polje)</span></span><input name="telefon" type="tel" autocomplete="tel"></label>
<label><span>Broj katastarske čestice <span class="opt">(Neobavezno polje)</span></span><input name="cestica"></label></div>
<label>Vaša poruka<textarea name="poruka" rows="5" required></textarea></label>
<p class="small">Vaši podaci bit će korišteni isključivo za odgovaranje na vaš upit, obradu i rješavanje vašeg zahtjeva te pružanje relevantnih informacija. Vaši podaci neće biti proslijeđeni trećim stranama niti korišteni u marketinške svrhe</p>
<button class="btn" type="submit">Pošalji</button>
</form></div></section>'''

# ---------- pages ----------
def home():
    p = ''; h = HOME; why = h['why']
    svc = ''.join(f'''<li class="svc"><a href="{p}{s["slug"]}/index.html">
<img src="{img(s["img"], p)}" alt="" loading="lazy" class="{'photo' if s['photo'] else 'plan'}">
<span class="svc-body"><span class="svc-name">{s["title"]}</span><span class="svc-desc">{H.escape(s["text"])}</span></span></a></li>''' for s in SERVICES)
    special = ''.join(f'''<li><h3>{f'<a href="{p}{x["slug"]}/index.html">{x["title"]}</a>' if x["slug"] else x["title"]}</h3><p>{H.escape(x["text"])}</p></li>''' for x in SPECIAL)
    prices = ''.join(f'<tr><td>{f"<a href={chr(34)}{p}{sl}/index.html{chr(34)}>{n}</a>" if sl else n}</td><td>{pr}</td><td>{t}</td></tr>' for n, sl, pr, t in PRICES)
    locs = ''.join(f'<li><a href="{p}{s}/index.html"><span class="loc-city">{n}</span><span class="loc-area">{d}</span></a></li>' for s, n, d in LOCATIONS)
    counters = ''.join(f'<li><strong>{c["value"]}{c["suffix"]}</strong>{c["label"]}</li>' for c in h['counters'])
    points = ''.join(f'<li>{x}</li>' for x in why['points'])
    posts = sorted(SRC['posts'], key=lambda x: x['date'], reverse=True)[:3]
    blog = ''.join(f'<li><a href="{p}{po["path"].strip("/")}/index.html"><time datetime="{po["date"]}">{hr_date(po["date"])}</time><span>{H.escape(po["title"])}</span></a></li>' for po in posts)
    partners = ''.join(f'<li><a href="{u}" rel="noopener" target="_blank"><img src="{img(l, p)}" alt=""><span><strong>{n}</strong>{d}</span></a></li>' for n, d, u, l in PARTNERS)
    intro = h['services_intro'].replace('USLUGE ', '', 1)
    lead, rest = intro.split(' GEODETSKE ELABORATE KATASTARSKE GEODEZIJE I ZEMLJIŠNE KNJIGE ')
    html = head('LAND ING d.o.o. | Geodetske usluge Osijek, Zadar, Biograd | Etažiranje, Parcelacija', 'LAND ING d.o.o. – geodetske usluge Osijek, Zadar, Biograd.', p, '/') + header(p, 'Home') + f'''
<main id="main">
<section class="hero"><div class="wrap hero-grid">
<div class="hero-copy">
<p class="hero-brand">LAND ING d.o.o.</p>
<h1>Mjerimo svijet</h1>
<p class="lead">{why["headline"].replace(chr(8203), "")}</p>
<div class="hero-actions"><a class="btn" href="tel:{PHONE_TEL}">Nazovite nas {PHONE}</a><a class="btn btn-ghost" href="#kontakt">Kontakt</a></div>
</div>
<figure class="survey-frame" aria-hidden="true">
<img src="{img("Untitled-design-2.jpg", p)}" alt="" width="1920" height="1080">
<svg class="parcel" viewBox="0 0 400 300" preserveAspectRatio="none"><polygon points="62,226 170,182 292,200 330,262 108,284"/>
<g class="pts"><circle cx="62" cy="226" r="3.2"/><circle cx="170" cy="182" r="3.2"/><circle cx="292" cy="200" r="3.2"/><circle cx="330" cy="262" r="3.2"/><circle cx="108" cy="284" r="3.2"/></g></svg>
<span class="tick tl"></span><span class="tick tr"></span><span class="tick bl"></span><span class="tick br"></span>
<figcaption><span>HTRS96/TM</span><span>E 401 512,38  N 4 883 207,15</span></figcaption>
</figure>
</div></section>

<section class="section" id="o-nama"><div class="wrap split">
<div><h2>Zašto mi?</h2><p class="lead-sm">{why["sub"]}</p><ul class="facts">{counters}</ul></div>
<div><p>{why["text"]}</p><ul class="checks">{points}</ul><a class="btn btn-ghost" href="#usluge">Naše usluge</a></div>
</div></section>

<section class="section section-tint" id="usluge"><div class="wrap">
<div class="section-head split-head"><h2>Usluge</h2><div><p class="lead-sm">{lead}</p>
<h3>Geodetske elaborate katastarske geodezije i zemljišne knjige</h3><p>{rest}</p></div></div>
<ul class="svc-grid">{svc}</ul>
</div></section>

<section class="section" id="posebne"><div class="wrap">
<div class="section-head"><h2>Posebne usluge</h2></div>
<ul class="special">{special}</ul>
</div></section>

<section class="section section-tint" id="cjenik"><div class="wrap split">
<div><h2>Cijene</h2><p class="small">{PRICE_NOTE}</p></div>
<div class="table-wrap"><table class="prices"><thead><tr><th>Usluga</th><th>Cijena</th><th>Rok izrade</th></tr></thead><tbody>{prices}</tbody></table></div>
</div></section>

<section class="section section-ink" id="lokacije"><div class="wrap">
<div class="section-head"><h2>Lokacije</h2><p>Poslovnice: Osijek i Zadar. Područje poslovanja: Zadarska, Šibensko-kninska, Zagrebačka i Osječko-baranjska županija.</p></div>
<ul class="locs">{locs}</ul>
</div></section>

<section class="section"><div class="wrap split">
<div><h2>Blog</h2><a class="text-link" href="{p}news/index.html">Svi članci</a></div>
<ul class="post-list">{blog}</ul>
</div></section>

<section class="section section-tint"><div class="wrap">
<div class="section-head"><h2>Naši partneri</h2></div>
<ul class="partners">{partners}</ul>
</div></section>

{contact_section(p)}
</main>''' + footer(p)
    write('index.html', html)

def inner_page(slug, kind):
    page = SRC['pages'][slug]
    path = f'{slug}/index.html'; p = prefix_for(path)
    body, cta = clean_body(page['html'])
    title, sub = page['title'], ''
    if kind == 'loc':
        s = BeautifulSoup(body, 'lxml'); hs = s.find_all(['h2', 'h3'])
        if hs: title = hs[0].get_text(' ', strip=True); hs[0].decompose()
        hs = s.find_all(['h2', 'h3'])
        if hs: sub = hs[0].get_text(' ', strip=True); hs[0].decompose()
        body = ''.join(str(c) for c in (s.body or s).children)
    body = rewrite_links(body, p)
    svc = next((s for s in SERVICES if s['slug'] == slug), None)
    price = next(((pr, t) for n, sl, pr, t in PRICES if sl == slug), None)
    facts = f'<dl class="page-facts"><div><dt>Cijena</dt><dd>{price[0]}</dd></div><div><dt>Rok izrade</dt><dd>{price[1]}</dd></div></dl>' if price else ''
    section = {'svc': ('Usluge', 'index.html#usluge'), 'special': ('Posebne usluge', 'index.html#posebne'), 'loc': ('Lokacije', 'index.html#lokacije')}[kind]
    eyebrow = page.get('eyebrow')
    crumb_name = sentence(eyebrow) if eyebrow else title
    html = head(page['doc_title'] or title, page['description'], p, f'/{slug}/') + header(p, section[0]) + f'''
<main id="main"><div class="page-hero"><div class="wrap page-hero-grid"><div>
{crumbs([('Home', 'index.html'), section, (crumb_name, None)], p)}
<h1>{H.escape(title)}</h1>{f'<p class="lead">{H.escape(sub)}</p>' if sub else ''}{facts}</div>
{f'<img class="page-hero-img {"photo" if svc["photo"] else "plan"}" src="{img(svc["img"], p)}" alt="">' if svc else ''}
</div></div>
<div class="wrap article-grid">
<article class="prose">{body}</article>
{side(p, cta, slug)}</div>
{cta_band(cta)}</main>''' + footer(p)
    write(path, html)

def post_page(po):
    path = po['path'].strip('/') + '/index.html'; p = prefix_for(path)
    body, cta = clean_body(po['html']); body = rewrite_links(body, p)
    words = len(BeautifulSoup(body, 'lxml').get_text().split())
    def score(x): return len(set(x['title'].lower().split()) & set(po['title'].lower().split()))
    rel = sorted([x for x in SRC['posts'] if x['slug'] != po['slug']], key=score, reverse=True)[:3]
    rel_html = ''.join(f'<li><a href="{p}{x["path"].strip("/")}/index.html"><time datetime="{x["date"]}">{hr_date(x["date"])}</time><span>{H.escape(x["title"])}</span></a></li>' for x in rel)
    html = head(po['title'] + ' - LAND ING d.o.o.', po['description'], p, po['path']) + header(p, 'Blog') + f'''
<main id="main"><div class="page-hero"><div class="wrap narrow-head">
{crumbs([('Home', 'index.html'), ('Blog', 'news/index.html'), (po["title"][:48] + ('…' if len(po["title"]) > 48 else ''), None)], p)}
<h1>{H.escape(po["title"])}</h1>
<p class="meta"><time datetime="{po["date"]}">{hr_date(po["date"])}</time><span aria-hidden="true">/</span>{max(1, round(words / 200))} min čitanja</p>
</div></div>
<div class="wrap article-grid">
<article class="prose">{body}</article>
{side(p, cta)}</div>
<section class="section section-tint"><div class="wrap"><div class="section-head"><h2>Povezani članci</h2></div><ul class="post-list post-list-row">{rel_html}</ul></div></section>
{cta_band(cta)}</main>''' + footer(p)
    write(path, html)

def blog_index():
    path = 'news/index.html'; p = '../'
    posts = sorted(SRC['posts'], key=lambda x: x['date'], reverse=True)
    items = ''.join(f'''<li><a href="{p}{po["path"].strip("/")}/index.html"><time datetime="{po["date"]}">{hr_date(po["date"])}</time>
<h2>{H.escape(po["title"])}</h2><p>{H.escape(po["description"] or po["excerpt"])}</p></a></li>''' for po in posts)
    html = head('Blog - LAND ING d.o.o.', '', p, '/news/') + header(p, 'Blog') + f'''
<main id="main"><div class="page-hero"><div class="wrap">{crumbs([('Home', 'index.html'), ('Blog', None)], p)}
<h1>Blog</h1></div></div>
<div class="wrap"><ul class="blog-list">{items}</ul></div>
{cta_band(None)}</main>''' + footer(p)
    write(path, html)

def contact_page():
    path = 'contact/index.html'; p = '../'
    html = head('Kontakt - LAND ING d.o.o.', '', p, '/contact/') + header(p, 'Kontakt') + f'''
<main id="main"><div class="page-hero"><div class="wrap">{crumbs([('Home', 'index.html'), ('Kontakt', None)], p)}
<h1>Javite nam se s povjerenjem</h1></div></div>
{contact_section(p, 'Kontakt')}</main>''' + footer(p)
    write(path, html)

def cookie_page():
    page = SRC['pages']['cookie-policy-eu']; path = 'cookie-policy-eu/index.html'; p = '../'
    body, _ = clean_body(page['html']); body = rewrite_links(body, p)
    html = head('Politika kolačića (EU) - LAND ING d.o.o.', '', p, '/cookie-policy-eu/') + header(p) + f'''
<main id="main"><div class="page-hero"><div class="wrap">{crumbs([('Home', 'index.html'), ('Politika kolačića (EU)', None)], p)}
<h1>Politika kolačića (EU)</h1></div></div>
<div class="wrap article-grid single"><article class="prose">{body}</article></div></main>''' + footer(p)
    write(path, html)

# ---------- build ----------
if os.path.exists(OUT): shutil.rmtree(OUT)
os.makedirs(OUT)
shutil.copytree(f'{ROOT}/site/assets', f'{OUT}/assets')
home()
for s in SERVICES: inner_page(s['slug'], 'svc')
for x in SPECIAL:
    if x['slug']: inner_page(x['slug'], 'special')
for s, *_ in LOCATIONS: inner_page(s, 'loc')
for po in SRC['posts']: post_page(po)
blog_index(); contact_page(); cookie_page()
open(f'{OUT}/robots.txt', 'w').write('User-agent: *\nDisallow: /\n')
open(f'{OUT}/.nojekyll', 'w').write('')
print('built', sum(len(f) for _, _, f in os.walk(OUT)), 'files')
