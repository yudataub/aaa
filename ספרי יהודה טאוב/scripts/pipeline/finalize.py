import json,re,os,sys,datetime,html,subprocess
sys.path.insert(0,'/tmp/claude-0/-home-user-aaa/bf25bffc-af4e-5f9d-9c53-c58411494098/scratchpad/work')
import build
REPO='/home/user/aaa'
SERIES='ספרי יהודה טאוב/פרשת שבוע וחגים/שיעורי קול תודה -  פרשת השבוע'
LJ='ספרי יהודה טאוב/שיעורי יוטיוב/lessons.json'
batch=json.load(open('/tmp/batch_out.json',encoding='utf8'))
# 1) series index
p=f'{REPO}/{SERIES}/index.html'; s=open(p,encoding='utf8').read()
for b in batch:
    sec=f'id="p-{b["folder"].replace(" ","-",1)}"'
    # folder like "012 ויחי" -> id p-012-ויחי  (parsha with spaces uses hyphen)
    pid='p-'+b['folder'].replace(' ','-')
    if f'id="{pid}"' not in s:  # new section (special Shabbatot, folders >=054)
        name=b['folder'].split(' ',1)[1]
        if 'class="chumash-head" id="chumash-054"' not in s and int(b['folder'][:3])>=54:
            lab='<span class="chumash-label">✨ שבתות מיוחדות</span>\n            '
            s=s.replace('    </nav>',"            "+lab+'<a class="parasha-chip" href="#'+pid+'">'+name+'</a>\n    </nav>',1)
            head='<div class="chumash-head" id="chumash-054"><span>✨ שבתות מיוחדות</span><span class="count">(0)</span></div>\n        '
        else:
            s=s.replace('    </nav>','            <a class="parasha-chip" href="#'+pid+'">'+name+'</a>\n    </nav>',1); head=''
        newsec=head+'<section class="parasha-section" id="'+pid+'" data-search="'+name+'">\n            <h2>'+name+' <span class="count">(0)</span></h2>\n            <ul class="lesson-list">\n            </ul>\n        </section>\n'
        e=s.rindex('</section>')+len('</section>')
        s=s[:e]+'\n        '+newsec+s[e:]
    i=s.index(f'id="{pid}"'); j=s.index('</section>',i)
    seg=s[i:j]
    fname=os.path.basename(b['book'])
    if fname in seg: continue
    li=f'                <li data-search="{html.escape(b["title"])} {b["parsha"]}"><a href="{b["folder"]}/{fname}">{html.escape(b["title"])}</a></li>\n'
    k=seg.index('<ul class="lesson-list">')+len('<ul class="lesson-list">')
    # find end of first newline after ul tag
    k=seg.index('\n',k)+1
    seg=seg[:k]+li+seg[k:]
    m=re.search(r'<span class="count">\((\d+)\)</span>',seg)
    seg=seg.replace(m.group(0),f'<span class="count">({int(m.group(1))+1})</span>',1)
    s=s[:i]+seg+s[j:]
# refresh chumash head counts + subtitle total
def _grp(n): return 'בראשית' if n<=12 else 'שמות' if n<=23 else 'ויקרא' if n<=33 else 'במדבר' if n<=43 else 'דברים' if n<=53 else 'שבתות מיוחדות'
tot={}
for m in re.finditer(r'<section class="parasha-section" id="p-(\d{3})-[^"]*".*?<span class="count">\((\d+)\)</span>',s,flags=re.S):
    g=_grp(int(m.group(1))); tot[g]=tot.get(g,0)+int(m.group(2))
def _hd(m):
    g=m.group(2).replace('חומש ','').strip()
    return m.group(1)+m.group(2)+m.group(3)+'(%d)'%tot.get(g,0)
s=re.sub(r'(<div class="chumash-head"[^>]*><span>)([^<]*)(</span><span class="count">)\(\d+\)',lambda m:m.group(1)+m.group(2)+m.group(3)+'(%d)'%tot.get(re.sub(r'^\S+ ','',m.group(2)).replace('חומש ',''),0),s)
s=re.sub(r'(מסודרים לפי סדר הפרשיות — )\d+( שיעורים)',lambda m:m.group(1)+str(sum(tot.values()))+m.group(2),s,1)
open(p,'w',encoding='utf8').write(s)
# 2) lessons.json
base=json.load(open(f'{REPO}/{LJ}',encoding='utf8'))
now=datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
pref='קול תודה - פרשת השבוע/'
have={l['file'] for l in base['lessons']}
for b in batch:
    if b['file'] in have: continue
    e={"title":b['title'],"subtitle":b['subtitle'],"icon":"📖","category":"פרשת השבוע","tags":([b['parsha'],"שבתות מיוחדות","קול תודה"] if int(b['folder'][:3])>=54 else [b['parsha'],"קול תודה"]),"chapters":b['chapters'],"cards":b['cards'],"clarity":"","file":b['file'],"edited":True,"date":now,"video":b['video'],"series":"קול תודה - פרשת השבוע"}
    if len(b.get('videos',[]))>1: e['videos']=b['videos']
    base['lessons'].append(e)
kt=[l for l in base['lessons'] if l['file'].startswith(pref)]; others=[l for l in base['lessons'] if not l['file'].startswith(pref)]
kt.sort(key=lambda l:(l['file'].split('/')[1],l['title']))
for i,l in enumerate(kt,1): l['series_order']=i
base['lessons']=kt+others
base['updated']=max(base['updated'],datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.000Z'))
open(f'{REPO}/{LJ}','w',encoding='utf8').write(json.dumps(base,ensure_ascii=False,indent=2))
print('lessons',len(base['lessons']),'series',len(kt))
