import json, re, os, sys, copy
from bs4 import BeautifulSoup, NavigableString, Comment
RAW=sys.argv[1]; OUT=sys.argv[2]
os.makedirs(OUT,exist_ok=True)
images=set()
def norm_link(h):
    if not h: return h
    h=h.replace('https://landing.hr','').replace('http://landing.hr','').replace('https://www.landing.hr','')
    h=h.replace('/#!/','/#')
    return h or '/'
KEEP={'a':['href'],'img':['src','alt'],'td':['colspan'],'th':['colspan']}
BLOCK=['h1','h2','h3','h4','h5','h6','p','ul','ol','table','blockquote','img']
def clean(el):
    el=copy.copy(el)
    for x in el.find_all(True):
        if x.name=='img':
            src=x.get('data-src') or x.get('src') or ''
            if 'data:image' in src: src=x.get('data-lazy-src') or ''
            x.attrs={'src':src,'alt':x.get('alt','')}
            if 'landing.hr/wp-content' in src: images.add(src)
            continue
        keep=KEEP.get(x.name,[])
        x.attrs={k:v for k,v in x.attrs.items() if k in keep}
        if x.name=='a' and x.get('href'): x['href']=norm_link(x['href'])
        if x.name in ('span','font','div','section'): x.unwrap()
    if el.name=='img':
        src=el.get('data-src') or el.get('src'); el.attrs={'src':src,'alt':el.get('alt','')}
        if src and 'landing.hr/wp-content' in src: images.add(src)
    else:
        el.attrs={k:v for k,v in el.attrs.items() if k in KEEP.get(el.name,[])}
    return el
SKIPTXT=re.compile(r'^(NAZOVITE NAS|Pošaljite upit|📞 Nazovite)',re.I)
def blocks_from(root):
    for bad in root.select('script,style,noscript,form,nav,.elementor-widget-the7_horizontal-menu,.elementor-widget-the7_nav-menu,.elementor-widget-html,.elementor-widget-spacer,#comments,.comments-area,.post-navigation,.single-related-posts,.author-info,.entry-author,.post-meta,.cmplz-cookiebanner,.page-title,.scroll-top,.wpcf7'):
        bad.decompose()
    out=[]; title=None; eyebrow=None
    def walk(n):
        nonlocal title,eyebrow
        for c in n.children:
            if isinstance(c,(NavigableString,Comment)): continue
            if c.name in BLOCK:
                txt=c.get_text(' ',strip=True)
                if c.name!='img' and not txt: continue
                if c.name=='img' and not (c.get('data-src') or c.get('src')): continue
                if txt and SKIPTXT.match(txt): continue
                if c.name=='h1' and title is None:
                    title=txt
                    if out and out[-1][0] in ('h3','h4','h5','h6') and len(out[-1][1])<60:
                        eyebrow=BeautifulSoup(out.pop()[1],'lxml').get_text(strip=True)
                    continue
                out.append((c.name,str(clean(c))))
            elif c.name in ('div','section','span','strong','em','b','a') and not c.find(BLOCK) and c.get_text(strip=True) and not c.find_parent(BLOCK):
                txt=c.get_text(' ',strip=True)
                if SKIPTXT.match(txt): continue
                p=BeautifulSoup('<p></p>','lxml').p
                for ch in list(c.contents): p.append(ch)
                out.append(('p',str(clean(p))))
            else: walk(c)
    walk(root)
    # drop trailing duplicated contact CTA
    html='\n'.join(h for _,h in out)
    return title,eyebrow,html
def page(path):
    s=BeautifulSoup(open(path,encoding='utf8'),'lxml')
    meta=(s.find('meta',attrs={'name':'description'}) or {}).get('content','')
    doc_title=s.title.get_text(strip=True) if s.title else ''
    root=s.select_one('[data-elementor-type=wp-page], [data-elementor-type=wp-post]') or s.select_one('.entry-content') or s.select_one('#content')
    t,e,h=blocks_from(root)
    return dict(title=t, eyebrow=e, html=h, description=meta, doc_title=doc_title)
site={'pages':{},'posts':[]}
for f in sorted(os.listdir(f'{RAW}/html')):
    slug=f[:-5]
    p=page(f'{RAW}/html/{f}')
    if p['html'].strip(): site['pages'][slug]=p
    print('page',slug,p['title'],len(p['html']))
posts=json.load(open(f'{RAW}/posts.json'))
import subprocess
os.makedirs(f'{RAW}/posthtml',exist_ok=True)
for po in posts:
    fn=f"{RAW}/posthtml/{po['slug']}.html"
    if not os.path.exists(fn):
        subprocess.run(['curl','-sS','--max-time','30','-o',fn,po['link']])
    p=page(fn)
    path=norm_link(po['link'])
    t=p['title'] or BeautifulSoup(po['title']['rendered'],'lxml').get_text()
    site['posts'].append(dict(slug=po['slug'],path=path,date=po['date'][:10],title=t,description=p['description'],html=p['html'],
        excerpt=BeautifulSoup(po['excerpt']['rendered'],'lxml').get_text(' ',strip=True)[:220]))
    print('post',path,t[:50],len(p['html']))
# home
s=BeautifulSoup(open(f'{RAW}/home.html',encoding='utf8'),'lxml')
def sec(i): return s.select_one(f'[data-id="{i}"]')
home={}
w=sec('d2653a8')
hs=[h.get_text(' ',strip=True) for h in w.select('.elementor-widget-heading')]
home['why']=dict(eyebrow=hs[0],headline=hs[1],sub=hs[2],text=w.select_one('.elementor-widget-text-editor').get_text(' ',strip=True),
  points=[x.get_text(' ',strip=True) for x in w.select('.elementor-widget-the7_icon_box_grid_widget .box-heading, .elementor-widget-the7_icon_box_grid_widget h4, .elementor-widget-the7_icon_box_grid_widget h3')])
cnt=[]
for c in w.select('.elementor-widget-counter'):
    num=c.select_one('[data-to-value]'); suf=c.select_one('.elementor-counter-number-suffix')
    cnt.append([num['data-to-value'] if num else '', suf.get_text(strip=True) if suf else ''])
labels=hs[3:]
home['counters']=[dict(value=v,suffix=s_,label=l) for (v,s_),l in zip(cnt,labels)]
svc=[]
for b in sec('c5d722c').select('.elementor-widget-the7_image_box_widget'):
    img=b.select_one('img'); src=img and (img.get('data-src') or img.get('src'))
    if src: images.add(src)
    h=b.select_one('h1,h2,h3,h4,h5,.box-heading'); txt=b.select_one('.box-description, p')
    svc.append(dict(title=h.get_text(' ',strip=True) if h else '', text=(txt.get_text(' ',strip=True) if txt else b.get_text(' ',strip=True)), img=src))
home['services']=svc
home['services_intro']=sec('80d3339').get_text(' ',strip=True)
sp=[]; seen=set()
for e in sec('09c0f77').select('.elementor-widget-the7_icon_box_grid_widget .box-heading, .elementor-widget-the7_icon_box_grid_widget h4, .elementor-widget-the7_icon_box_grid_widget h3'):
    t=e.get_text(' ',strip=True)
    if t in seen: continue
    seen.add(t)
    box=e.find_parent(class_=re.compile('wf-cell|icon-box|box-content')) or e.parent
    d=box.select_one('.box-description, p')
    sp.append(dict(title=t,text=d.get_text(' ',strip=True) if d else ''))
home['special']=sp
home['hero_img']=[ (i.get('data-src') or i.get('src')) for i in sec('541d93f').select('img')]
for u in home['hero_img']: images.add(u)
bg=re.findall(r'url\((["\']?)(https://landing\.hr/wp-content/uploads/[^)"\']+)\1\)',open(f'{RAW}/home.html',encoding='utf8').read())
home['bg_images']=sorted(set(u for _,u in bg))
images.update(home['bg_images'])
site['home']=home
site['images']=sorted(i for i in images if i)
json.dump(site,open(f'{OUT}/site.json','w'),ensure_ascii=False,indent=1)
print('images',len(site['images']))
print(json.dumps(home,ensure_ascii=False,indent=1)[:3500])
