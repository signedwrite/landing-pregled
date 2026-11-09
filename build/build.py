"""Static site generator for the landing.hr preview.
Reads content/site.json (extracted from the WordPress site) and writes dist/.
Every internal URL is relative, so the output works on any host or sub-path."""
import json, os, re, shutil, sys, html as H, datetime
from bs4 import BeautifulSoup

ROOT = sys.argv[1]
SRC = json.load(open(f'{ROOT}/content/site.json', encoding='utf8'))
OUT = f'{ROOT}/dist'
IMG = f'{ROOT}/site/assets/img'
PHONE, PHONE_TEL, MAIL = '+385 92 233 5366', '+385922335366', 'office@landing.hr'
ORIG = 'https://landing.hr'

# ---------- content model ----------
SERVICES = [  # slug, name, one-liner, image, price, duration
 ('geodetski-elaborat-za-legalizaciju', 'Geodetski elaborat za legalizaciju', 'Snimak izvedenog stanja za rješenje o izvedenom stanju.', 'LEGALIZACIJA.jpg', 'od 500 €', '5–10 dana'),
 ('upis-objekta', 'Upis objekta', 'Upis zgrade u katastar i zemljišnu knjigu.', 'upis_objekta.png', 'od 500 €', '7–14 dana'),
 ('parcelacijski-elaborat', 'Parcelacijski elaborat', 'Dioba ili spajanje katastarskih čestica.', 'iStock-1947465680-Large-1024x682.jpeg', 'od 500 €', '14–21 dan'),
 ('etaziranje-objekata', 'Etažiranje objekata', 'Podjela zgrade na posebne dijelove i etažno vlasništvo.', 'etaziranje.png', 'od 400 €', '10–15 dana'),
 ('evidentiranje-promjena-oblika-povrsine-cestice', 'Evidentiranje promjena čestice', 'Usklađivanje oblika i površine čestice sa stvarnim stanjem.', 'EVIDENTIRANJE_2.jpg', 'na upit', ''),
 ('geodetska-situacija-za-projektiranje', 'Geodetska situacija za projektiranje', '3D model terena kao podloga projektantu.', 'podloge_za_projektiranje_3.png', 'na upit', ''),
 ('posredovanje-prodaja-kupnja-nekretnina', 'Posredovanje u prometu nekretnina', 'Kupoprodaja uz provjeru katastra i zemljišne knjige.', 'iStock-1220084677-Large-1024x682.jpeg', 'na upit', ''),
]
EXTRA_PRICES = [('Iskolčenje građevine', 'od 300 €', '1–3 dana'), ('Iskolčenje (određivanje) međe', 'od 200 €', '1–3 dana')]
SPECIAL = [
 ('inzenjerska-geodezija', 'Inženjerska geodezija', 'Geodetska podrška na gradilištu: iskolčenja, kontrola temelja, konstrukcija, cesta i tunela.'),
 ('aerofotogrametrija-dron', 'Aerofotogrametrija', 'Snimanje terena dronom za kartiranje, kubature i praćenje radova.'),
 ('3d-lasersko-skeniranje', '3D lasersko skeniranje', 'Oblak točaka i 3D modeli zgrada, terena i kulturne baštine.'),
 (None, 'GIS sustavi', 'Prikupljanje, obrada i vizualizacija prostornih podataka, digitalne karte i georeferenciranje.'),
]
LOCATIONS = [
 ('geodet-osijek', 'Osijek', 'Osječko-baranjska županija', 'Ured Osijek'),
 ('geodet-zadar', 'Zadar', 'Zadarska županija i otoci', 'Ured Zadar'),
 ('geodet-biograd', 'Biograd na Moru', 'Zadarska i Šibensko-kninska županija', 'Ured Biograd'),
]
PARTNERS = [('GIS d.o.o.', 'Geodetske usluge, Osijek', 'https://www.gis-osijek.com/', 'grbWeb1.png'),
            ('Genius GIS d.o.o.', 'Geoinformacijski sustavi', 'https://genius-gis.hr/', 'LOGO.png'),
            ('ACES d.o.o.', 'Projektiranje i konzalting, Zadar', 'https://www.aces.hr/', 'aces-logo-2-copy-1189x523.png')]
NAV = [('Usluge', 'index.html#usluge'), ('Cjenik', 'index.html#cjenik'), ('Lokacije', 'index.html#lokacije'),
       ('O nama', 'index.html#o-nama'), ('Blog', 'news/index.html'), ('Kontakt', 'contact/index.html')]
LOCAL_IMG = set(os.listdir(IMG))

ACRONYMS = {'gis': 'GIS', '3d': '3D', 'hkoig': 'HKOIG', 'gml': 'GML', 'dof': 'DOF', 'bim': 'BIM', 'eu': 'EU', 'rh': 'RH', 'ppds': 'PPDS'}
def sentence(t):
    t = t.strip()
    if not t.isupper(): return t
    t = t.lower()
    t = re.sub(r'\b(\w+)\b', lambda m: ACRONYMS.get(m.group(1), m.group(1)), t)
    return t[:1].upper() + t[1:]

# ---------- html cleanup ----------
def clean_body(html, drop_cta=True, location=False):
    s = BeautifulSoup(html, 'lxml')
    body = s.body or s
    # remove logos and decorative icons
    for im in body.find_all('img'):
        src = im.get('src', '')
        if re.search(r'logo|ikona|53e4d4b3', src): im.decompose()
    # remove short all-caps eyebrow headings
    for h in body.find_all(re.compile('^h[1-6]$')):
        t = h.get_text(' ', strip=True)
        if t and t.isupper() and len(t) < 40 and not re.search(r'\d', t): h.decompose()
    # cut trailing contact CTA (the template has its own)
    if drop_cta:
        for h in body.find_all(re.compile('^h[23]$')):
            if re.match(r'(Trebate|Kontaktirajte nas|Pošaljite upit|Javite nam se)', h.get_text(strip=True)):
                for sib in list(h.find_next_siblings()): sib.decompose()
                h.decompose(); break
    for p in body.find_all('p'):
        if not p.get_text(strip=True) and not p.find('img'): p.decompose()
    for b in body.find_all(['b']): b.name = 'strong'
    for i in body.find_all(['i']): i.name = 'em'
    # tables: first row as header
    for t in body.find_all('table'):
        rows = t.find_all('tr')
        if rows and not t.find('th'):
            for td in rows[0].find_all('td'): td.name = 'th'
        wrap = s.new_tag('div', attrs={'class': 'table-wrap'}); t.wrap(wrap)
    out = ''.join(str(c) for c in body.children)
    return out

def rewrite_links(html, prefix):
    def fix(m):
        attr, url = m.group(1), m.group(2)
        u = url.replace('https://landing.hr', '').replace('http://landing.hr', '')
        if attr == 'src':
            name = os.path.basename(u.split('?')[0])
            if name in LOCAL_IMG: return f'src="{prefix}assets/img/{name}"'
            return f'src="{ORIG}{u}"' if u.startswith('/wp-content') else m.group(0)
        if u.startswith('/') and not u.startswith('//'):
            path, _, frag = u.partition('#')
            path = path.strip('/')
            if path in ('', 'home'): tgt = 'index.html'
            elif path == 'news': tgt = 'news/index.html'
            else: tgt = path + '/index.html'
            if path in ('gis-geoinformacijski-sustavi', 'o-nama', 'usluge', 'kontakt'): tgt = 'index.html'
            return f'href="{prefix}{tgt}{"#" + frag if frag else ""}"'
        return m.group(0)
    return re.sub(r'(href|src)="([^"]*)"', fix, html)

def img(name, prefix): return f'{prefix}assets/img/{name}'

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
<div class="preview-note">Radna verzija nove stranice za pregled · prava stranica je <a href="{ORIG}{canonical}">landing.hr</a></div>
'''

def header(prefix, current=''):
    links = ''.join(f'<li><a href="{prefix}{u}"{" aria-current=page" if current == n else ""}>{n}</a></li>' for n, u in NAV)
    return f'''<header class="site-head"><div class="wrap head-row">
<a class="brand" href="{prefix}index.html" aria-label="LAND ING d.o.o., naslovnica"><img src="{prefix}assets/img/logo-crop.png" alt="LAND ING geodetski inženjering"></a>
<button class="menu-btn" aria-expanded="false" aria-controls="nav"><span></span><span class="sr">Izbornik</span></button>
<nav id="nav" aria-label="Glavni izbornik"><ul>{links}</ul>
<a class="btn btn-small" href="tel:{PHONE_TEL}">{PHONE}</a></nav>
</div></header>'''

def cta_band(prefix, heading='Trebate geodeta?'):
    return f'''<section class="cta-band"><div class="wrap cta-row">
<div><h2>{heading}</h2><p>Pošaljite broj katastarske čestice i katastarsku općinu. Besplatnu ponudu šaljemo u roku 24 sata.</p></div>
<div class="cta-actions"><a class="btn" href="tel:{PHONE_TEL}">Nazovite {PHONE}</a><a class="btn btn-ghost" href="mailto:{MAIL}">{MAIL}</a></div>
</div></section>'''

def footer(prefix):
    svc = ''.join(f'<li><a href="{prefix}{s}/index.html">{n}</a></li>' for s, n, *_ in SERVICES)
    loc = ''.join(f'<li><a href="{prefix}{s}/index.html">Geodet {n}</a></li>' for s, n, *_ in LOCATIONS)
    return f'''<footer class="site-foot"><div class="wrap foot-grid">
<div><img src="{prefix}assets/img/land_ing_logo.png" alt="LAND ING geodetski inženjering" width="113" height="80" class="foot-logo">
<p>LAND ING d.o.o.<br>Geodetski inženjering</p>
<p><a href="tel:{PHONE_TEL}">{PHONE}</a><br><a href="mailto:{MAIL}">{MAIL}</a><br>Radnim danima 8–17 h</p></div>
<div><h3>Usluge</h3><ul>{svc}</ul></div>
<div><h3>Lokacije</h3><ul>{loc}</ul><h3>Podaci o tvrtki</h3><p class="small">OIB 30446646311<br>IBAN HR1123400091111293529</p></div>
</div><div class="wrap foot-base"><span>© {datetime.date.today().year} LAND ING d.o.o.</span><a href="{prefix}cookie-policy-eu/index.html">Privatnost i kolačići</a></div></footer>
<script src="{prefix}assets/site.js" defer></script></body></html>'''

def write(path, html):
    full = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, 'w', encoding='utf8').write(html)

def prefix_for(path):
    return '../' * path.count('/')

# ---------- pages ----------
def home():
    p = ''
    h = SRC['home']
    svc_rows = ''.join(f'''<li class="svc"><a href="{p}{s}/index.html">
<img src="{img(i, p)}" alt="" loading="lazy" width="160" height="110">
<span class="svc-name">{n}</span><span class="svc-desc">{d}</span>
<span class="svc-price">{pr}</span><span class="svc-time">{t or "prema opsegu"}</span></a></li>''' for s, n, d, i, pr, t in SERVICES)
    price_rows = ''.join(f'<tr><td><a href="{p}{s}/index.html">{n}</a></td><td>{pr}</td><td>{t or "–"}</td></tr>' for s, n, d, i, pr, t in SERVICES if pr != 'na upit')
    price_rows += ''.join(f'<tr><td>{n}</td><td>{pr}</td><td>{t}</td></tr>' for n, pr, t in EXTRA_PRICES)
    special = ''.join(f'<li><h3>{f"<a href={chr(34)}{p}{s}/index.html{chr(34)}>{n}</a>" if s else n}</h3><p>{d}</p></li>' for s, n, d in SPECIAL)
    locs = ''.join(f'<li><a href="{p}{s}/index.html"><span class="loc-city">{c}</span><span class="loc-area">{a}</span></a></li>' for s, c, a, _ in LOCATIONS)
    counters = ''.join(f'<li><strong>{c["value"]}{c["suffix"]}</strong> {c["label"]}</li>' for c in h['counters'] if 'preciznost' not in c['label'])
    points = ''.join(f'<li>{x}</li>' for x in h['why']['points'])
    posts = sorted(SRC['posts'], key=lambda x: x['date'], reverse=True)[:3]
    blog = ''.join(f'<li><a href="{p}{po["path"].strip("/")}/index.html"><time datetime="{po["date"]}">{hr_date(po["date"])}</time><span>{H.escape(po["title"])}</span></a></li>' for po in posts)
    partners = ''.join(f'<li><a href="{u}" rel="noopener" target="_blank"><img src="{img(l, p)}" alt="{n}"><span><strong>{n}</strong>{d}</span></a></li>' for n, d, u, l in PARTNERS)
    html = head('LAND ING d.o.o. | Geodetske usluge Osijek, Zadar, Biograd', 'Geodetski elaborati, legalizacija, upis objekta, parcelacija i etažiranje. Uredi u Osijeku i Zadru, rad na području cijele Hrvatske.', p, '/') + header(p) + f'''
<main id="main">
<section class="hero"><div class="wrap hero-grid">
<div class="hero-copy">
<h1>Geodetske usluge od terena do upisa u zemljišnu knjigu</h1>
<p class="lead">Elaborati za legalizaciju, upis objekta, parcelaciju i etažiranje. Ovlašteni inženjeri geodezije s uredima u Osijeku i Zadru, za cijelu Hrvatsku.</p>
<div class="hero-actions"><a class="btn" href="tel:{PHONE_TEL}">Nazovite {PHONE}</a><a class="btn btn-ghost" href="#kontakt">Pošaljite upit</a></div>
<p class="hero-note">Besplatna ponuda u roku 24 sata. Dovoljni su broj čestice i katastarska općina.</p>
</div>
<figure class="survey-frame" aria-hidden="true">
<img src="{img("Untitled-design-2.jpg", p)}" alt="" width="1920" height="1080">
<svg class="parcel" viewBox="0 0 400 300" preserveAspectRatio="none"><polygon points="72,196 168,150 286,176 318,250 120,268"/>
<g class="pts"><circle cx="72" cy="196" r="3.2"/><circle cx="168" cy="150" r="3.2"/><circle cx="286" cy="176" r="3.2"/><circle cx="318" cy="250" r="3.2"/><circle cx="120" cy="268" r="3.2"/></g></svg>
<span class="tick tl"></span><span class="tick tr"></span><span class="tick bl"></span><span class="tick br"></span>
<figcaption><span>HTRS96/TM</span><span class="coord" data-e="401512.38" data-n="4883207.15">E 401 512,38 · N 4 883 207,15</span></figcaption>
</figure>
</div></section>

<section class="section" id="usluge"><div class="wrap">
<div class="section-head"><h2>Usluge</h2><p>Svaki elaborat radimo od mjerenja na terenu do provedbe u katastru i zemljišnoj knjizi.</p></div>
<div class="svc-headrow" aria-hidden="true"><span></span><span>Usluga</span><span>Cijena</span><span>Rok izrade</span></div>
<ul class="svc-list">{svc_rows}</ul>
</div></section>

<section class="section section-tint" id="posebne"><div class="wrap">
<div class="section-head"><h2>Posebne usluge</h2><p>Za projektante, izvođače i investitore.</p></div>
<ul class="special">{special}</ul>
</div></section>

<section class="section" id="cjenik"><div class="wrap split">
<div><h2>Cjenik</h2><p>Cijene su orijentacijske i ovise o veličini objekta, broju čestica i lokaciji. Točnu ponudu šaljemo besplatno.</p></div>
<div class="table-wrap"><table class="prices"><thead><tr><th>Usluga</th><th>Cijena</th><th>Rok izrade</th></tr></thead><tbody>{price_rows}</tbody></table></div>
</div></section>

<section class="section section-ink" id="lokacije"><div class="wrap">
<div class="section-head"><h2>Gdje radimo</h2><p>Uredi u Osijeku i Zadru. Teren pokrivamo u Zadarskoj, Šibensko-kninskoj, Zagrebačkoj i Osječko-baranjskoj županiji, a po dogovoru u cijeloj Hrvatskoj.</p></div>
<ul class="locs">{locs}</ul>
</div></section>

<section class="section" id="o-nama"><div class="wrap split">
<div><h2>O nama</h2><p class="lead-sm">{h["why"]["sub"]}</p></div>
<div><p>{h["why"]["text"]}</p><ul class="checks">{points}</ul><ul class="facts">{counters}</ul></div>
</div></section>

<section class="section section-tint"><div class="wrap split">
<div><h2>Iz bloga</h2><p>Vodiči o legalizaciji, uporabnim dozvolama i katastru.</p><a class="text-link" href="{p}news/index.html">Svi članci</a></div>
<ul class="post-list">{blog}</ul>
</div></section>

<section class="section"><div class="wrap">
<div class="section-head"><h2>Partneri</h2></div>
<ul class="partners">{partners}</ul>
</div></section>

{contact_section(p)}
</main>''' + footer(p)
    write('index.html', html)

def contact_section(p):
    return f'''<section class="section section-tint" id="kontakt"><div class="wrap split">
<div><h2>Kontakt</h2>
<dl class="contact-dl">
<dt>Telefon</dt><dd><a href="tel:{PHONE_TEL}">{PHONE}</a></dd>
<dt>E-mail</dt><dd><a href="mailto:{MAIL}">{MAIL}</a></dd>
<dt>Radno vrijeme</dt><dd>Radnim danima od 8 do 17 h. Prije dolaska u ured molimo nazovite.</dd>
<dt>Poslovnice</dt><dd>Osijek i Zadar</dd>
<dt>Područje rada</dt><dd>Zadarska, Šibensko-kninska, Zagrebačka i Osječko-baranjska županija</dd>
</dl></div>
<form class="form" data-mailto="{MAIL}">
<label>Ime i prezime<input name="ime" required autocomplete="name"></label>
<label>E-mail<input name="email" type="email" required autocomplete="email"></label>
<div class="form-row"><label><span>Telefon <span class="opt">(neobavezno)</span></span><input name="telefon" type="tel" autocomplete="tel"></label>
<label><span>Broj čestice i k.o. <span class="opt">(neobavezno)</span></span><input name="cestica"></label></div>
<label>Poruka<textarea name="poruka" rows="5" required></textarea></label>
<p class="small">Podatke koristimo samo za odgovor na vaš upit i ne dijelimo ih s trećima.</p>
<button class="btn" type="submit">Pošalji upit</button>
</form></div></section>'''

MONTHS = ['siječnja', 'veljače', 'ožujka', 'travnja', 'svibnja', 'lipnja', 'srpnja', 'kolovoza', 'rujna', 'listopada', 'studenoga', 'prosinca']
def hr_date(d):
    y, m, dd = d.split('-'); return f'{int(dd)}. {MONTHS[int(m) - 1]} {y}.'

def crumbs(items, p):
    li = ''.join(f'<li><a href="{p}{u}">{n}</a></li>' if u else f'<li aria-current="page">{n}</li>' for n, u in items)
    return f'<nav class="crumbs" aria-label="Putanja"><ol>{li}</ol></nav>'

def service_page(slug, kind):
    page = SRC['pages'][slug]
    path = f'{slug}/index.html'; p = prefix_for(path)
    body = clean_body(page['html'])
    title = page['title']
    sub = ''
    if kind == 'loc':
        s = BeautifulSoup(body, 'lxml'); hs = s.find_all(['h2', 'h3'])
        if hs: title = hs[0].get_text(' ', strip=True); hs[0].decompose()
        hs = s.find_all(['h2', 'h3'])
        if hs: sub = hs[0].get_text(' ', strip=True); hs[0].decompose()
        body = ''.join(str(c) for c in (s.body or s).children)
    body = rewrite_links(body, p)
    meta = next(((n, pr, t) for s_, n, d, i, pr, t in SERVICES if s_ == slug), None)
    hero_img = next((i for s_, n, d, i, pr, t in SERVICES if s_ == slug), None)
    facts = ''
    if meta and meta[1] != 'na upit':
        facts = f'<dl class="page-facts"><div><dt>Cijena</dt><dd>{meta[1]}</dd></div><div><dt>Rok izrade</dt><dd>{meta[2]}</dd></div></dl>'
    section = {'svc': ('Usluge', 'index.html#usluge'), 'special': ('Posebne usluge', 'index.html#posebne'), 'loc': ('Lokacije', 'index.html#lokacije')}[kind]
    aside = f'''<aside class="side"><div class="side-card"><h2>Zatražite ponudu</h2><p>Pošaljite broj čestice i katastarsku općinu, a ponudu dobivate u roku 24 sata.</p>
<a class="btn" href="tel:{PHONE_TEL}">Nazovite {PHONE}</a><a class="btn btn-ghost" href="mailto:{MAIL}">Pošaljite e-mail</a></div>
<div class="side-links"><h2>Ostale usluge</h2><ul>{''.join(f'<li><a href="{p}{s}/index.html">{n}</a></li>' for s, n, *_ in SERVICES if s != slug)}</ul></div></aside>'''
    html = head(page['doc_title'] or title, page['description'], p, f'/{slug}/') + header(p, section[0]) + f'''
<main id="main"><div class="page-hero"><div class="wrap">
{crumbs([('Naslovnica', 'index.html'), section, (sentence(title).split(' – ')[0], None)], p)}
<h1>{H.escape(title)}</h1>{f'<p class="lead">{H.escape(sub)}</p>' if sub else ''}{facts}
</div></div>
<div class="wrap article-grid">
<article class="prose">{f'<img class="article-img" src="{img(hero_img, p)}" alt="" width="900" height="600">' if hero_img and kind == 'svc' else ''}{body}</article>
{aside}</div>
{cta_band(p)}</main>''' + footer(p)
    write(path, html)

def post_page(po, prev_next):
    path = po['path'].strip('/') + '/index.html'; p = prefix_for(path)
    body = rewrite_links(clean_body(po['html']), p)
    words = len(BeautifulSoup(body, 'lxml').get_text().split())
    rel = [x for x in SRC['posts'] if x['slug'] != po['slug']]
    def score(x): return len(set(x['title'].lower().split()) & set(po['title'].lower().split()))
    rel = sorted(rel, key=score, reverse=True)[:3]
    rel_html = ''.join(f'<li><a href="{p}{x["path"].strip("/")}/index.html"><time datetime="{x["date"]}">{hr_date(x["date"])}</time><span>{H.escape(x["title"])}</span></a></li>' for x in rel)
    html = head(po['title'] + ' | LAND ING d.o.o.', po['description'], p, po['path']) + header(p, 'Blog') + f'''
<main id="main"><div class="page-hero"><div class="wrap narrow-head">
{crumbs([('Naslovnica', 'index.html'), ('Blog', 'news/index.html'), ('Članak', None)], p)}
<h1>{H.escape(po["title"])}</h1>
<p class="meta"><time datetime="{po["date"]}">{hr_date(po["date"])}</time>, čitanje oko {max(1, round(words / 200))} min</p>
</div></div>
<div class="wrap article-grid">
<article class="prose">{body}</article>
<aside class="side"><div class="side-card"><h2>Trebate geodeta?</h2><p>Pošaljite broj čestice i katastarsku općinu, a ponudu dobivate u roku 24 sata.</p>
<a class="btn" href="tel:{PHONE_TEL}">Nazovite {PHONE}</a><a class="btn btn-ghost" href="mailto:{MAIL}">Pošaljite e-mail</a></div>
<div class="side-links"><h2>Usluge</h2><ul>{''.join(f'<li><a href="{p}{s}/index.html">{n}</a></li>' for s, n, *_ in SERVICES[:4])}</ul></div></aside>
</div>
<section class="section section-tint"><div class="wrap"><div class="section-head"><h2>Povezani članci</h2></div><ul class="post-list post-list-row">{rel_html}</ul></div></section>
</main>''' + footer(p)
    write(path, html)

def blog_index():
    path = 'news/index.html'; p = '../'
    posts = sorted(SRC['posts'], key=lambda x: x['date'], reverse=True)
    items = ''.join(f'''<li><a href="{p}{po["path"].strip("/")}/index.html"><time datetime="{po["date"]}">{hr_date(po["date"])}</time>
<h2>{H.escape(po["title"])}</h2><p>{H.escape(po["description"] or po["excerpt"])}</p></a></li>''' for po in posts)
    html = head('Blog | LAND ING d.o.o.', 'Vodiči o legalizaciji, uporabnim dozvolama, katastru i geodetskim elaboratima.', p, '/news/') + header(p, 'Blog') + f'''
<main id="main"><div class="page-hero"><div class="wrap">{crumbs([('Naslovnica', 'index.html'), ('Blog', None)], p)}
<h1>Blog</h1><p class="lead">Vodiči o legalizaciji, uporabnim dozvolama, katastru i geodetskim elaboratima.</p></div></div>
<div class="wrap"><ul class="blog-list">{items}</ul></div>
{cta_band(p)}</main>''' + footer(p)
    write(path, html)

def contact_page():
    path = 'contact/index.html'; p = '../'
    html = head('Kontakt | LAND ING d.o.o.', 'Kontakt LAND ING d.o.o., uredi u Osijeku i Zadru.', p, '/contact/') + header(p, 'Kontakt') + f'''
<main id="main"><div class="page-hero"><div class="wrap">{crumbs([('Naslovnica', 'index.html'), ('Kontakt', None)], p)}
<h1>Javite nam se</h1><p class="lead">Odgovaramo u roku 24 sata. Za ponudu su dovoljni broj čestice i katastarska općina.</p></div></div>
{contact_section(p)}
<section class="section"><div class="wrap"><div class="section-head"><h2>Podaci o tvrtki</h2></div>
<dl class="contact-dl contact-dl-cols"><dt>Naziv</dt><dd>LAND ING d.o.o.</dd><dt>OIB</dt><dd>30446646311</dd><dt>IBAN</dt><dd>HR1123400091111293529</dd></dl></div></section>
</main>''' + footer(p)
    write(path, html)

def privacy_page():
    path = 'cookie-policy-eu/index.html'; p = '../'
    html = head('Privatnost i kolačići | LAND ING d.o.o.', 'Kako LAND ING d.o.o. postupa s osobnim podacima i kolačićima.', p, '/cookie-policy-eu/') + header(p) + f'''
<main id="main"><div class="page-hero"><div class="wrap">{crumbs([('Naslovnica', 'index.html'), ('Privatnost i kolačići', None)], p)}
<h1>Privatnost i kolačići</h1></div></div>
<div class="wrap article-grid"><article class="prose">
<h2>Kolačići</h2><p>Ova stranica ne postavlja kolačiće za praćenje ni oglašavanje. Fontovi se učitavaju s Google Fonts poslužitelja.</p>
<h2>Osobni podaci</h2><p>Podatke koje pošaljete obrascem ili e-mailom (ime, e-mail, telefon, broj čestice) koristimo isključivo za odgovor na vaš upit i izradu ponude. Ne prodajemo ih i ne dijelimo s trećima, osim kada je to potrebno za izvršenje usluge ili propisano zakonom.</p>
<h2>Vaša prava</h2><p>U svakom trenutku možete zatražiti uvid, ispravak ili brisanje svojih podataka na <a href="mailto:{MAIL}">{MAIL}</a>.</p>
<h2>Voditelj obrade</h2><p>LAND ING d.o.o., OIB 30446646311, Ulica Ante Starčevića 10, 31000 Osijek.</p>
</article></div></main>''' + footer(p)
    write(path, html)

# ---------- build ----------
if os.path.exists(OUT): shutil.rmtree(OUT)
os.makedirs(OUT)
shutil.copytree(f'{ROOT}/site/assets', f'{OUT}/assets')
home()
for s, *_ in SERVICES: service_page(s, 'svc')
for s, *_ in SPECIAL:
    if s: service_page(s, 'special')
for s, *_ in LOCATIONS: service_page(s, 'loc')
posts = SRC['posts']
for po in posts: post_page(po, None)
blog_index(); contact_page(); privacy_page()
open(f'{OUT}/robots.txt', 'w').write('User-agent: *\nDisallow: /\n')
open(f'{OUT}/.nojekyll', 'w').write('')
print('built', sum(len(f) for _, _, f in os.walk(OUT)), 'files')
