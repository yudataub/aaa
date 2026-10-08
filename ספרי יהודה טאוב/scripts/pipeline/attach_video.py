# usage: python3 attach_video.py '<json list>'  each: {"book": "<repo path of existing book>", "main": "<vid>", "extras": ["<vid>",...], "title": optional}
# Creates/updates the video page (שיעורי יוטיוב/קול תודה - פרשת השבוע/<folder>/<title>.html) and lessons.json entry for an existing book.
import sys,json,re,os,subprocess,datetime,urllib.parse
sys.path.insert(0,'/tmp/claude-0/-home-user-aaa/bf25bffc-af4e-5f9d-9c53-c58411494098/scratchpad/work')
import build
REPO='/home/user/aaa'; LJ=REPO+'/ספרי יהודה טאוב/שיעורי יוטיוב/lessons.json'
YT=REPO+'/ספרי יהודה טאוב/שיעורי יוטיוב/קול תודה - פרשת השבוע'
items=json.loads(sys.argv[1]); out=[]
L=json.load(open(LJ,encoding='utf8')); lessons=L['lessons']
now=datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
labels=json.load(open('/tmp/remaining.json',encoding='utf8'))['rem']; vt={i:t for t,i in labels}
for it in items:
    path=it['book']; src=open(REPO+'/'+path,encoding='utf8').read()
    b=build.parse_book(src); folder=path.split('/')[-2]; parsha=folder.split(' ',1)[1]
    title=it.get('title') or b['title']
    fname=re.sub(r'[\\/:*?"<>|]','',build.strip_nik(title)).strip()
    # existing page for this book?
    ex=[l for l in lessons if l['file'].startswith('קול תודה - פרשת השבוע/') and l['file'].split('/')[1]==folder and build.strip_nik(l['title']).strip()==build.strip_nik(b['title_nik']).strip()]
    ypath=(REPO+'/ספרי יהודה טאוב/שיעורי יוטיוב/'+ex[0]['file']) if ex else f"{YT}/{folder}/{fname}.html"; os.makedirs(os.path.dirname(ypath),exist_ok=True)
    book_url=build.SITE+'/'.join(urllib.parse.quote(x) for x in path.split('/'))
    if ex:
        e=ex[0]; vids=[u.rsplit('/',1)[-1] for u in (e.get('videos') or [e['video']])]
    else: vids=[it['main']]
    for v in [it['main']]+it.get('extras',[]):
        if v not in vids: vids.append(v)
    main=[(vids[0],'השיעור המלא בווידאו')]
    extra=[(v,build.clean_label(vt.get(v,'')) or 'סרטון נוסף') for v in vids[1:]]
    r=build.render(b,main,extra,book_url,ypath,title=title,extra_title='סרטונים נוספים הקשורים לשיעור')
    rel=os.path.relpath(ypath,REPO+'/ספרי יהודה טאוב/שיעורי יוטיוב')
    if ex: e=ex[0]; e['video']='https://youtu.be/'+vids[0]; e['videos']=['https://youtu.be/'+v for v in vids] if len(vids)>1 else None
    else:
        e={"title":build.sanitize(title),"subtitle":build.sanitize(b['subtitle']),"icon":"📖","category":"פרשת השבוע","tags":[parsha,"קול תודה"],"chapters":r['chapters'],"cards":[build.sanitize(c) for c in r['cards']],"clarity":"","file":rel,"edited":True,"date":now,"video":'https://youtu.be/'+vids[0],"series":"קול תודה - פרשת השבוע"}
        if len(vids)>1: e['videos']=['https://youtu.be/'+v for v in vids]
        lessons.append(e)
    if e.get('videos') is None: e.pop('videos',None)
    out.append(rel); print('page',rel,'videos',len(vids))
pref='קול תודה - פרשת השבוע/'
kt=[l for l in lessons if l['file'].startswith(pref)]; oth=[l for l in lessons if not l['file'].startswith(pref)]
kt.sort(key=lambda l:(l['file'].split('/')[1],l['title']))
for i,l in enumerate(kt,1): l['series_order']=i
L['lessons']=kt+oth; L['updated']=max(L['updated'],datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.000Z'))
open(LJ,'w',encoding='utf8').write(json.dumps(L,ensure_ascii=False,indent=2))
