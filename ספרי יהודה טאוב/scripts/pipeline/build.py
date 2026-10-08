import json, re, html, subprocess, sys, urllib.parse
from html.parser import HTMLParser
REPO="/home/user/aaa"
TPL=REPO+"/ספרי יהודה טאוב/שיעורי יוטיוב/2026-07-02 - הלולב שמלמד לחיות.html"
SITE="https://yudataub.github.io/aaa/"
COLORS=[("#ff6b9d","#c62b6b"),("#a78bfa","#6d28d9"),("#ffd166","#e08e00"),("#4ecdc4","#0f8f87"),("#74b9ff","#1e63c9"),("#ff9f43","#c4620a")]
ICONS=["📖","🌿","💛","🕯️","🎶","✨","🔍","🌟","🧭","🍃"]
NIK=re.compile(r'[֑-ׇ]')

NK=r'[\u0591-\u05C7]*'
YHVH=re.compile('י'+NK+'ה'+NK+'ו'+NK+'ה'+NK)
ELOH=re.compile('(א'+NK+'ל('+NK+'))ה('+NK+'י)')
def sanitize(t):
    t=YHVH.sub("ה'",t)
    def e(m):
        return m.group(1)+('ק' if '\u05B9' in m.group(2) else 'וק')+m.group(3)
    return ELOH.sub(e,t)
def strip_nik(s): return NIK.sub('',s)
def esc(s): return html.escape(s,quote=False)

class Node:
    def __init__(s,tag,attrs): s.tag=tag; s.attrs=dict(attrs); s.kids=[]; s.parent=None
    def cls(s): return (s.attrs.get('class') or '').split()
VOID={'br','img','input','meta','link','hr'}
class P(HTMLParser):
    def __init__(s): super().__init__(convert_charrefs=True); s.root=Node('root',[]); s.cur=s.root
    def handle_starttag(s,tag,attrs):
        n=Node(tag,attrs); n.parent=s.cur; s.cur.kids.append(n)
        if tag not in VOID: s.cur=n
    def handle_endtag(s,tag):
        c=s.cur
        while c is not s.root and c.tag!=tag: c=c.parent
        if c is not s.root: s.cur=c.parent
    def handle_data(s,d): s.cur.kids.append(d)
def text(n):
    return ''.join(k if isinstance(k,str) else text(k) for k in n.kids)
def inner(n):
    out=[]
    for k in n.kids:
        if isinstance(k,str): out.append(esc(k))
        elif k.tag in('strong','b'): out.append('<strong>'+inner(k)+'</strong>')
        elif k.tag in('em','i'): out.append('<em>'+inner(k)+'</em>')
        elif k.tag=='br': out.append('<br>')
        else: out.append(inner(k))
    return re.sub(r'\s+',' ',''.join(out)).strip()

def parse_book(src):
    i=src.find('<div class="toc">')
    if i<0: i=src.find('<nav class="toc">')
    if i<0: i=src.find('class="author"')
    j=src.find('<div class="footer">')
    if j<0: j=src.find('<script',i)
    h1=re.search(r'<h1[^>]*>(.*?)</h1>',src,re.S).group(1)
    sub=re.search(r'class="subtitle">(.*?)</div>',src,re.S).group(1)
    body=src[src.find('</div>',src.find('<div class="toc">'))+6 if False else i: j]
    # drop toc block
    p=P(); p.feed('<div>'+body+'</div>'); root=p.root.kids[0]
    chapters=[]; cur=None; card=None
    def newchap(name):
        nonlocal cur,card
        cur={'name':name,'cards':[]}; chapters.append(cur); card=None
    def newcard(title):
        nonlocal card
        card={'title':title,'blocks':[]}; cur['cards'].append(card)
    def ensure():
        nonlocal card
        if cur is None: newchap('הקדמה')
        if card is None: newcard(cur['name'])
    sources=None
    def walk(nodes,em=False):
        nonlocal sources
        for n in nodes:
            if isinstance(n,str):
                tx=re.sub(r'\s+',' ',esc(n)).strip()
                if tx: ensure(); card['blocks'].append(('em' if em else 'p',tx))
                continue
            c=n.cls()
            if n.tag=='div' and 'toc' in c: continue
            if n.tag=='div' and ('in-this-chapter' in c or 'chapter-card' in c or 'chapter-divider' in c): continue
            if 'chapter-label' in c: continue
            if n.tag=='div' and 'sources' in c:
                sources=[inner(li) for li in find_all(n,'li')]; continue
            if n.tag=='h2':
                t=re.sub(r'\s+',' ',text(n)).strip()
                newchap(t); 
                if n.attrs.get('id')=='intro': newcard('הקדמה')
            elif n.tag=='h3': ensure() if cur is None else None; newcard(re.sub(r'\s+',' ',text(n)).strip())
            elif n.tag=='p': ensure(); card['blocks'].append(('em' if em else 'p',inner(n)))
            elif n.tag in('ul','ol'): ensure(); card['blocks'].append((n.tag,[inner(li) for li in find_all(n,'li')]))
            elif n.tag=='blockquote': ensure(); card['blocks'].append(('p',inner(n)))
            elif n.tag=='div' and 'highlight-box' in c:
                ensure()
                for pp in n.kids:
                    if not isinstance(pp,str):
                        if pp.tag=='p': card['blocks'].append(('em' if cur['name']!='הקדמה' else 'p',inner(pp)))
                        elif pp.tag in('ul','ol'): card['blocks'].append((pp.tag,[inner(li) for li in find_all(pp,'li')]))
                        else:
                            tx=inner(pp)
                            if tx: card['blocks'].append(('p',tx))
                    else:
                        tx=re.sub(r'\s+',' ',esc(pp)).strip()
                        if tx: card['blocks'].append(('p',tx))
            elif n.tag=='div' and 'story-box' in c:
                ensure()
                for pp in n.kids:
                    if isinstance(pp,str): continue
                    if 'story-title' in pp.cls(): card['blocks'].append(('p','<strong>'+esc(re.sub(r'\s+',' ',text(pp)).strip())+'</strong>'))
                    elif pp.tag=='p': card['blocks'].append(('p',inner(pp)))
                    elif pp.tag in('ul','ol'): card['blocks'].append((pp.tag,[inner(li) for li in find_all(pp,'li')]))
                    else:
                        tx=inner(pp)
                        if tx: card['blocks'].append(('p',tx))
            elif n.tag in('div','section'):
                blocky=any((not isinstance(k,str)) and k.tag in('p','ul','ol','div','h2','h3','blockquote','section') for k in n.kids)
                if blocky: walk(n.kids, em=('quote-box' in c or 'verse-box' in c))
                else:
                    tx=inner(n)
                    if tx:
                        ensure(); card['blocks'].append(('em' if ('quote-box' in c or 'verse' in ' '.join(c)) else 'p',tx))
            elif n.tag in('span','a','strong','em'):
                tx=inner(n)
                if tx: ensure(); card['blocks'].append(('p',tx))
            elif n.tag in('h4',): pass
    def find_all(n,tag):
        out=[]
        for k in n.kids:
            if isinstance(k,str): continue
            if k.tag==tag: out.append(k)
            out+=find_all(k,tag)
        return out
    walk(root.kids)
    # sources tail
    src_i=src.find('<div class="sources">')
    if sources is None and src_i>0:
        p2=P(); p2.feed(src[src_i:src.find('<div class="footer">')]); sources=[inner(li) for li in find_all(p2.root,'li')]
    return {'title':strip_nik(re.sub(r'<[^>]+>','',h1)).strip(),'title_nik':re.sub(r'\s+',' ',re.sub(r'<[^>]+>','',h1)).strip(),'subtitle':re.sub(r'\s+',' ',re.sub(r'<[^>]+>','',sub)).strip(),'chapters':[c for c in chapters if c['cards']],'sources':sources or []}

def clean_label(t):
    t=re.sub(r'^[\d\s\-]+','',t.strip()); t=re.split(r',\s*פרשת',t)[0]; t=re.sub(r'\s+[-–]\s+קול תודה.*$','',t); t=re.sub(r'\s+קול תודה.*$','',t)
    return strip_nik(t).strip(' -')

def video_card(vid,label,first):
    idattr=' id="video"' if first else ''
    return f'''    <section class="video-card"{idattr}>
      <div class="video-frame"><button type="button" aria-label="▶ {esc(label)}" onclick="var f=document.createElement('iframe');f.src='https://www.youtube-nocookie.com/embed/{vid}?autoplay=1&amp;rel=0';f.allow='autoplay; encrypted-media; picture-in-picture; fullscreen';f.allowFullscreen=true;f.title=this.getAttribute('aria-label');this.replaceWith(f);"><img src="https://i.ytimg.com/vi/{vid}/hqdefault.jpg" alt="{esc(label)}" loading="lazy"><span class="play"></span></button></div>
      <div class="video-link"><span>📺 {esc(label)}</span><a href="https://www.youtube.com/watch?v={vid}" target="_blank" rel="noopener">צפייה ביוטיוב ↗</a></div>
    </section>
'''

def render(book,videos,extra,book_url,out,title=None,extra_title='הקלטות נוספות של אותו שיעור'):
    t=open(TPL,encoding='utf8').read()
    head_end=t.index('<section class="video-card"'); main_end=t.index('</main>')
    head,tail=t[:head_end],t[main_end:]
    title=title or book['title']; icon="📖"
    head=head.replace("<title>🍭 הלולב שמלמד לחיות","<title>"+icon+" "+esc(title))
    head=head.replace("<h1>🍭 הלולב שמלמד לחיות</h1>","<h1>"+icon+" "+esc(title)+"</h1>")
    head=re.sub(r'(<header class="hero">.*?<h1>.*?</h1>\s*<p>).*?(</p>)',lambda m:m.group(1)+esc(book['subtitle'])+m.group(2),head,flags=re.S)
    assert 'הלולב' not in head and 'dVHZqEjdtds' not in head, head[:300]
    chapters=[dict(c) for c in book['chapters']]
    if book['sources']:
        chapters.append({'name':'מקורות','cards':[{'title':'מקורות ומראי מקומות','blocks':[('ol',book['sources'])]}]})
    vcards=''.join(video_card(v,l,i==0) for i,(v,l) in enumerate(videos))
    if extra:
        links=''.join(f'<div><a href="https://www.youtube.com/watch?v={v}" target="_blank" rel="noopener" style="color:#c4002b;text-decoration:none;font-weight:700">{esc(l)} ↗</a></div>' for v,l in extra)
        vcards+=f'    <div style="margin:-12px 6px 24px;color:var(--ink-soft)"><div style="font-weight:700;margin-bottom:4px">{esc(extra_title)}:</div>{links}</div>\n'
    stories=[]; n=0; chap_js=[]
    total=sum(len(c['cards']) for c in chapters)
    for ci,ch in enumerate(chapters):
        c1,c2=COLORS[ci%len(COLORS)]; ic=ICONS[ci%len(ICONS)]; sts=[]
        for cd in ch['cards']:
            n+=1; sts.append({'id':n,'title':cd['title'],'icon':ic})
            body=[]
            for kind,val in cd['blocks']:
                if kind=='p': body.append('      <p>'+val+'</p>')
                elif kind=='em': body.append('      <p class="bold-para">'+val+'</p>')
                else: body.append(f'      <{kind}>'+''.join('<li>'+x+'</li>' for x in val)+f'</{kind}>')
            nav=[]
            if n>1: nav.append(f'<a href="#story-{n-1}">⟶ הקודם</a>')
            if n<total: nav.append(f'<a href="#story-{n+1}">הבא ⟵</a>')
            ktxt=f'{"אבגדהוזחטי"[ci] if ci<10 else ci+1}'
            kick=('פרק '+ktxt+' · '+esc(ch['name'])) if ch['name'] not in('הקדמה','מקורות') else esc(ch['name'])
            stories.append(f'''    <section class="story-card" id="story-{n}" data-chapter="{ci+1}" style="--chap-color:{c1};--chap-color-2:{c2};">
      <div class="story-kicker">{kick}</div>
      <h3 class="story-title">{ic} {esc(cd['title'])}</h3>
{chr(10).join(body)}
      <div class="story-footer">
        <div class="nav-links">
          {"".join(nav)}
        </div>
        <button class="copy-link-btn" onclick="copyStoryLink({n}, this)">🔗 העתק קישור</button>
        <span class="copy-toast">הקישור הועתק!</span>
      </div>
    </section>
''')
        chap_js.append({'id':ci+1,'name':ch['name'],'icon':ic,'color':c2,'stories':sts})
    tail=re.sub(r'<div class="book-meta">.*?</div>','<div class="book-meta">שיעורו של הרב יהודה טאוב · <a href="'+book_url+'" target="_blank" rel="noopener">הספר המלא עם הקראה</a></div>',tail,flags=re.S)
    tail=re.sub(r'var CHAPTERS = \[.*?\];',lambda m:'var CHAPTERS = '+json.dumps(chap_js,ensure_ascii=False)+';',tail,count=1,flags=re.S)
    doc=head+vcards+'\n'+'\n'.join(stories)+'\n  '+tail
    doc=sanitize(doc)
    chk=NIK.sub('',re.sub(r'<[^>]+>',' ',doc))
    assert 'יהוה' not in chk and not re.search(r'אלהי',chk), 'divine name left'
    open(out,'w',encoding='utf8').write(doc)
    return {'cards':[cd['title'] for c in chapters for cd in c['cards']],'chapters':len(chapters),'words':len(re.findall(r'[א-ת]{2,}',strip_nik(re.sub(r'<[^>]+>',' ',''.join(stories)))))}
