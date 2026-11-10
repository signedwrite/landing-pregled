"""landing.hr v3: improved version of the current landing.hr design (same look, cleaned up).
Same content and helpers as build.py. Output: dist3/ (published under /v3/)."""
import sys, os, shutil, html as H, datetime, re, random
code = open(os.path.join(os.path.dirname(__file__), 'build.py'), encoding='utf8').read().split('# ---------- build ----------')[0]
exec(code)
OUT = f'{ROOT}/dist3'
NAV3 = [('Home', 'index.html'), ('O nama', 'index.html#o-nama'), ('Usluge', 'index.html#usluge'), ('Posebne usluge', 'index.html#posebne'),
        ('Lokacije', 'index.html#lokacije'), ('Kontakt', 'contact/index.html'), ('Blog', 'news/index.html')]
ICONS = {  # simple line icons for the four special services
 'inzenjerska-geodezija': '<path d="M3 21h18"/><path d="M6 21V9l6-4 6 4v12"/><path d="M10 21v-5h4v5"/><path d="M9 11h.01M15 11h.01"/>',
 'aerofotogrametrija-dron': '<circle cx="5" cy="6" r="2.5"/><circle cx="19" cy="6" r="2.5"/><circle cx="5" cy="18" r="2.5"/><circle cx="19" cy="18" r="2.5"/><path d="M7 8l3 3M17 8l-3 3M7 16l3-3M17 16l-3-3"/><rect x="10" y="10" width="4" height="4" rx="1"/>',
 '3d-lasersko-skeniranje': '<path d="M12 3l8 4.5v9L12 21l-8-4.5v-9z"/><path d="M12 12l8-4.5M12 12v9M12 12L4 7.5"/>',
 None: '<rect x="3" y="4" width="18" height="12" rx="2"/><path d="M8 20h8M12 16v4"/><path d="M7 12l3-3 2 2 4-4"/>',
}
SVG = lambda inner, cls='': f'<svg viewBox="0 0 24 24" aria-hidden="true"{f" class={chr(34)}{cls}{chr(34)}" if cls else ""}>{inner}</svg>'
I_PIN = '<path d="M12 21s-7-6.2-7-11a7 7 0 0114 0c0 4.8-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/>'
I_MAIL = '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/>'
I_PHONE = '<path d="M5 4h4l2 5-2.5 1.5a11 11 0 005 5L15 13l5 2v4a2 2 0 01-2 2A16 16 0 013 6a2 2 0 012-2"/>'
I_ID = '<rect x="3" y="5" width="18" height="14" rx="2"/><circle cx="9" cy="11" r="2"/><path d="M6 16c.6-1.5 1.7-2 3-2s2.4.5 3 2M15 10h3M15 13h3"/>'
I_BANK = '<path d="M3 10l9-6 9 6"/><path d="M5 10v8M9.5 10v8M14.5 10v8M19 10v8M3 20h18"/>'

def network_svg():
    rnd = random.Random(7); pts = []
    for _ in range(34):
        x = rnd.choice([rnd.uniform(0, 380), rnd.uniform(820, 1200)]); y = rnd.uniform(0, 330); pts.append((x, y))
    lines = []
    for i, a in enumerate(pts):
        near = sorted(pts, key=lambda b: (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)[1:4]
        for b in near: lines.append(f'<line x1="{a[0]:.0f}" y1="{a[1]:.0f}" x2="{b[0]:.0f}" y2="{b[1]:.0f}"/>')
    dots = ''.join(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{3.5 if i % 3 else 5}"/>' for i, (x, y) in enumerate(pts))
    return f'<svg class="net" viewBox="0 0 1200 700" preserveAspectRatio="xMidYMin slice" aria-hidden="true">{"".join(lines)}{dots}</svg>'

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
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{p}assets/site.css">
</head><body>
<div class="preview-note">Radna verzija nove stranice za pregled. Prava stranica: <a href="{ORIG}{canonical}">landing.hr</a></div>
<div class="topbar"><div class="wrap"><strong>Nazovite nas</strong><a href="tel:{PHONE_TEL}">📞 {PHONE}</a><a href="mailto:{MAIL}">✉ {MAIL}</a><span class="hours">Radnim danima od 08h do 17h</span></div></div>
'''

def header(p, current=''):
    links = ''.join(f'<a href="{p}{u}"{" aria-current=page" if current == n else ""}>{n}</a>' for n, u in NAV3)
    return f'''<header class="site-head"><div class="wrap head-row">
<a class="brand" href="{p}index.html" aria-label="LAND ING d.o.o., naslovnica"><img src="{p}assets/img/logo-crop.png" alt="LAND ING geodetski inženjering"></a>
<button class="menu-btn" aria-expanded="false" aria-controls="nav"><span></span><span class="sr">Izbornik</span></button>
<nav id="nav" aria-label="Glavni izbornik">{links}</nav>
</div></header>'''

def footer(p):
    svc = ''.join(f'<a href="{p}{s["slug"]}/index.html">{s["title"]}</a>' for s in SERVICES[:5])
    loc = ''.join(f'<a href="{p}{s}/index.html">{n}</a>' for s, n, _ in LOCATIONS)
    return f'''<footer class="site-foot"><div class="wrap foot-row"><div class="foot-top">
<div class="foot-brand"><img src="{p}assets/img/logo-crop.png" alt="LAND ING geodetski inženjering"><p>Mjerimo svijet</p></div>
<div class="foot-cols"><div><strong>Usluge</strong>{svc}</div><div><strong>Lokacije</strong>{loc}</div>
<div><strong>Kontakt</strong><a href="tel:{PHONE_TEL}">{PHONE}</a><a href="mailto:{MAIL}">{MAIL}</a><span>OIB: 30446646311</span><span>IBAN: HR1123400091111293529</span></div></div></div>
<div class="foot-base"><span>© {datetime.date.today().year} LAND ING d.o.o.</span><a href="{p}cookie-policy-eu/index.html">Politika kolačića (EU)</a></div>
</div></footer><script src="{p}assets/site.js" defer></script></body></html>'''

def contact_block(p, heading='Kontaktirajte nas sa povjerenjem!'):
    return f'''<section class="contact-sec" id="kontakt"><div class="wrap contact">
<div><h2>{heading}</h2><form class="form" data-mailto="{MAIL}">
<label>Vaše ime<input name="ime" required autocomplete="name"></label>
<label>Vaš email<input name="email" type="email" required autocomplete="email"></label>
<label><span>Broj telefona <span class="opt">(Neobavezno polje)</span></span><input name="telefon" type="tel" autocomplete="tel"></label>
<label><span>Broj katastarske čestice <span class="opt">(Neobavezno polje)</span></span><input name="cestica"></label>
<label>Vaša poruka<textarea name="poruka" rows="6" required></textarea></label>
<button class="btn" type="submit">Pošalji</button>
<p class="small">Vaši podaci bit će korišteni isključivo za odgovaranje na vaš upit, obradu i rješavanje vašeg zahtjeva te pružanje relevantnih informacija. Vaši podaci neće biti proslijeđeni trećim stranama niti korišteni u marketinške svrhe</p>
</form></div>
<ul class="info">
<li><span class="ic">{SVG(I_PIN)}</span><div><b>Poslovnice</b><span>Osijek i Zadar</span><span class="small">Područje poslovanja: Zadarska, Šibensko-kninska, Zagrebačka i Osječko-baranjska županija. Molimo nazovite prije dolaska.</span></div></li>
<li><span class="ic">{SVG(I_MAIL)}</span><div><b>E-mail</b><a href="mailto:{MAIL}">{MAIL}</a><span class="small">Za klijente i partnere</span></div></li>
<li><span class="ic">{SVG(I_PHONE)}</span><div><b>Telefon</b><a href="tel:{PHONE_TEL}">{PHONE}</a><span class="small">Radnim danima od 08h do 17h</span></div></li>
<li><span class="ic">{SVG(I_ID)}</span><div><b>OIB</b><span>30446646311</span></div></li>
<li><span class="ic">{SVG(I_BANK)}</span><div><b>IBAN</b><span>HR1123400091111293529</span></div></li>
<li style="justify-content:center"><img class="info-logo" src="{p}assets/img/logo-crop.png" alt="LAND ING geodetski inženjering"></li>
</ul></div></section>'''

def cta_band(cta):
    h, t = cta or DEFAULT_CTA
    return f'''<section class="cta-band"><div class="wrap"><div><h2>{H.escape(h)}</h2><p>{t}</p></div>
<div class="hero-actions" style="margin:0"><a class="btn" href="tel:{PHONE_TEL}">{PHONE}</a><a class="btn btn-light" href="mailto:{MAIL}">{MAIL}</a></div></div></section>'''

def side(p, cta, exclude=None):
    h, t = cta or DEFAULT_CTA
    links = ''.join(f'<li><a href="{p}{s["slug"]}/index.html">{s["title"]}</a></li>' for s in SERVICES if s['slug'] != exclude)
    return f'''<aside class="side"><div class="side-card"><h2>{H.escape(h)}</h2><p>{t}</p>
<a class="btn" href="tel:{PHONE_TEL}">{PHONE}</a><a class="btn btn-light" href="mailto:{MAIL}">{MAIL}</a></div>
<div class="side-links"><h2>Usluge</h2><ul>{links}</ul></div></aside>'''

def post_card(po, p, tag='h3'):
    desc = f'<p>{H.escape(po["description"] or po["excerpt"])}</p>' if tag == 'h2' else ''
    return f'<li><a href="{p}{po["path"].strip("/")}/index.html"><time datetime="{po["date"]}">{hr_date(po["date"])}</time><{tag}>{H.escape(po["title"])}</{tag}>{desc}<span class="more">Pročitaj više</span></a></li>'

def home():
    p = ''; h = HOME; why = h['why']
    intro = h['services_intro'].replace('USLUGE ', '', 1)
    lead, rest = intro.split(' GEODETSKE ELABORATE KATASTARSKE GEODEZIJE I ZEMLJIŠNE KNJIGE ')
    counters = ''.join(f'<li><strong>{c["value"]}{c["suffix"]}</strong><span>{c["label"]}</span></li>' for c in h['counters'])
    points = ''.join(f'<li>{x}</li>' for x in why['points'])
    svc = ''.join(f'''<li><a href="{p}{s["slug"]}/index.html"><div class="svc-img"><img src="{p}assets/img/{s["img"]}" alt="" loading="lazy" class="{"photo" if s["photo"] else "plan"}"></div>
<h3>{s["title"]}</h3><p>{H.escape(s["text"])}</p><span class="more">Saznajte više</span></a></li>''' for s in SERVICES)
    def sp_title(t):
        m = re.match(r'(.+?)\s*(\(.+\))$', t)
        return f'{m.group(1)}<small>{m.group(2)}</small>' if m else t
    special = ''
    for x in SPECIAL:
        inner = f'<span class="ico">{SVG(ICONS[x["slug"]])}</span><h3>{sp_title(x["title"])}</h3><p>{H.escape(x["text"])}</p>'
        special += f'<li><a href="{p}{x["slug"]}/index.html">{inner}</a></li>' if x['slug'] else f'<li><div>{inner}</div></li>'
    prices = ''.join(f'<tr><td>{f"<a href={chr(34)}{p}{sl}/index.html{chr(34)}>{n}</a>" if sl else n}</td><td>{pr}</td><td>{t}</td></tr>' for n, sl, pr, t in PRICES)
    locs = ''.join(f'<li><a href="{p}{s}/index.html"><h3>{n}</h3><p>{d}</p><span class="more">Saznajte više</span></a></li>' for s, n, d in LOCATIONS)
    partners = ''.join(f'<li><a href="{u}" target="_blank" rel="noopener"><img src="{p}assets/img/{l}" alt=""><strong>{n}</strong><span>{d}</span></a></li>' for n, d, u, l in PARTNERS)
    posts = sorted(SRC['posts'], key=lambda x: x['date'], reverse=True)[:3]
    html = head('LAND ING d.o.o. | Geodetske usluge Osijek, Zadar, Biograd | Etažiranje, Parcelacija', 'LAND ING d.o.o. – geodetske usluge Osijek, Zadar, Biograd.', p, '/') + header(p, 'Home') + f'''
<main>
<section class="hero"><div class="hero-slides" aria-hidden="true"><div></div><div></div></div>{network_svg()}
<div class="wrap hero-copy"><h1>LAND ING d.o.o.</h1><p class="slogan">Mjerimo svijet</p>
<div class="hero-actions"><a class="btn" href="#kontakt">Kontaktirajte nas</a><a class="btn btn-light" href="#usluge">Naše usluge</a></div></div></section>

<section class="section" id="o-nama"><div class="wrap">
<div class="sec-head"><p class="kicker">Zašto mi?</p><h2 class="dark">{why["headline"]}</h2></div>
<div class="why"><div class="why-text"><h3>{why["sub"]}</h3><p>{why["text"]}</p></div>
<div><ul class="checks">{points}</ul><a class="btn" href="#usluge">Naše usluge</a></div></div>
<ul class="counters">{counters}</ul>
</div></section>

<section class="section soft" id="usluge"><div class="wrap">
<div class="sec-head"><h2>Usluge</h2><p>{lead}</p><h3>Geodetske elaborate katastarske geodezije i zemljišne knjige</h3><p>{rest}</p></div>
<ul class="svc">{svc}</ul></div></section>

<section class="section" id="posebne"><div class="wrap">
<div class="sec-head"><h2>Posebne usluge</h2></div><ul class="icons">{special}</ul></div></section>

<section class="section soft" id="cjenik"><div class="wrap">
<div class="sec-head"><h2>Cijene</h2></div>
<div class="table-wrap"><table class="prices"><thead><tr><th>Usluga</th><th>Cijena</th><th>Rok izrade</th></tr></thead><tbody>{prices}</tbody></table></div>
<p class="small price-note">{PRICE_NOTE}</p></div></section>

<section class="section" id="lokacije"><div class="wrap">
<div class="sec-head"><h2>Lokacije</h2></div><ul class="locs">{locs}</ul></div></section>

<section class="section soft"><div class="wrap">
<div class="sec-head"><h2>Blog</h2></div><ul class="posts">{''.join(post_card(po, p) for po in posts)}</ul>
<div class="center"><a class="btn btn-line" href="{p}news/index.html">Svi članci</a></div></div></section>

<section class="section"><div class="wrap">
<div class="sec-head"><h2 class="dark">Naši partneri</h2></div><ul class="partners">{partners}</ul></div></section>

{contact_block(p)}
</main>''' + footer(p)
    write('index.html', html)

def page_hero(p, crumb, title, sub='', facts='', img='hero2.jpg'):
    return f'''<section class="page-hero" style="background-image:url({p}assets/img/{img})"><div class="wrap">
<p class="crumb">{crumb}</p><h1>{H.escape(title)}</h1>{f'<p class="lead">{H.escape(sub)}</p>' if sub else ''}{facts}</div></section>'''

def inner_page(slug, kind):
    page = SRC['pages'][slug]; path = f'{slug}/index.html'; p = prefix_for(path)
    body, cta = clean_body(page['html']); title, sub = page['title'], ''
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
    crumb = f'<a href="{p}index.html">Home</a> / <a href="{p}{section[1]}">{section[0]}</a>'
    html = head(page['doc_title'] or title, page['description'], p, f'/{slug}/') + header(p, section[0]) + f'''
<main>{page_hero(p, crumb, title, sub, facts, 'hero1.jpg' if kind == 'special' else 'hero2.jpg')}
<div class="wrap layout"><article class="prose">{body}</article>{side(p, cta, slug)}</div>
{cta_band(cta)}</main>''' + footer(p)
    write(path, html)

def post_page(po):
    path = po['path'].strip('/') + '/index.html'; p = prefix_for(path)
    body, cta = clean_body(po['html']); body = rewrite_links(body, p)
    def score(x): return len(set(x['title'].lower().split()) & set(po['title'].lower().split()))
    rel = sorted([x for x in SRC['posts'] if x['slug'] != po['slug']], key=score, reverse=True)[:3]
    crumb = f'<a href="{p}index.html">Home</a> / <a href="{p}news/index.html">Blog</a> / <time datetime="{po["date"]}">{hr_date(po["date"])}</time>'
    html = head(po['title'] + ' - LAND ING d.o.o.', po['description'], p, po['path']) + header(p, 'Blog') + f'''
<main>{page_hero(p, crumb, po["title"])}
<div class="wrap layout"><article class="prose">{body}</article>{side(p, cta)}</div>
<section class="section soft"><div class="wrap"><div class="sec-head"><h2>Povezani članci</h2></div><ul class="posts">{''.join(post_card(x, p) for x in rel)}</ul></div></section>
{cta_band(cta)}</main>''' + footer(p)
    write(path, html)

def blog_index():
    path = 'news/index.html'; p = '../'
    posts = sorted(SRC['posts'], key=lambda x: x['date'], reverse=True)
    html = head('Blog - LAND ING d.o.o.', '', p, '/news/') + header(p, 'Blog') + f'''
<main>{page_hero(p, f'<a href="{p}index.html">Home</a> / Blog', 'Blog')}
<div class="wrap blog-list"><ul class="posts">{''.join(post_card(po, p, 'h2') for po in posts)}</ul></div>
{cta_band(None)}</main>''' + footer(p)
    write(path, html)

def contact_page():
    path = 'contact/index.html'; p = '../'
    html = head('Kontakt - LAND ING d.o.o.', '', p, '/contact/') + header(p, 'Kontakt') + f'''
<main>{page_hero(p, f'<a href="{p}index.html">Home</a> / Kontakt', 'Javite nam se s povjerenjem')}
{contact_block(p)}</main>''' + footer(p)
    write(path, html)

def cookie_page():
    page = SRC['pages']['cookie-policy-eu']; path = 'cookie-policy-eu/index.html'; p = '../'
    body, _ = clean_body(page['html']); body = rewrite_links(body, p)
    html = head('Politika kolačića (EU) - LAND ING d.o.o.', '', p, '/cookie-policy-eu/') + header(p) + f'''
<main>{page_hero(p, f'<a href="{p}index.html">Home</a>', 'Politika kolačića (EU)')}
<div class="wrap layout" style="grid-template-columns:1fr"><article class="prose">{body}</article></div></main>''' + footer(p)
    write(path, html)

if os.path.exists(OUT): shutil.rmtree(OUT)
os.makedirs(OUT)
shutil.copytree(f'{ROOT}/site3/assets', f'{OUT}/assets')
shutil.copy(f'{ROOT}/site/assets/site.js', f'{OUT}/assets/site.js')
home()
for s in SERVICES: inner_page(s['slug'], 'svc')
for x in SPECIAL:
    if x['slug']: inner_page(x['slug'], 'special')
for s, *_ in LOCATIONS: inner_page(s, 'loc')
for po in SRC['posts']: post_page(po)
blog_index(); contact_page(); cookie_page()
print('built v3', sum(len(f) for _, _, f in os.walk(OUT)), 'files')
