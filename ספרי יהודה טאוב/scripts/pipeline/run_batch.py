import sys,json,os,re,subprocess,glob
sys.path.insert(0,'/tmp/claude-0/-home-user-aaa/bf25bffc-af4e-5f9d-9c53-c58411494098/scratchpad/work')
import make_book, build
REPO='/home/user/aaa'
SERIES=REPO+'/ספרי יהודה טאוב/פרשת שבוע וחגים/שיעורי קול תודה -  פרשת השבוע'
YT=REPO+'/ספרי יהודה טאוב/שיעורי יוטיוב/קול תודה - פרשת השבוע'
out=[]
for sp in sys.argv[1:]:
    spec=json.load(open(sp,encoding='utf8'))
    fname=re.sub(r'[\\/:*?"<>|]','',spec['title']).strip()
    bpath=f"{SERIES}/{spec['folder']}/{fname}.html"; os.makedirs(os.path.dirname(bpath),exist_ok=True)
    doc=make_book.build(spec,spec['video'],bpath)
    chk=re.sub(r'[֑-ׇ]','',re.sub(r'<[^>]+>',' ',doc))
    assert 'יהוה' not in chk and 'אלהי' not in chk, spec['title']
    # video page
    b=build.parse_book(doc)
    ypath=f"{YT}/{spec['folder']}/{fname}.html"; os.makedirs(os.path.dirname(ypath),exist_ok=True)
    book_url=build.SITE+'/'.join(__import__('urllib.parse').parse.quote(x) for x in bpath.replace(REPO+'/','').split('/'))
    ex=[(v,l) for v,l in zip(spec.get('extra_videos',[]),spec.get('extra_labels',[]))]
    r=build.render(b,[(spec['video'],spec.get('main_label','השיעור המלא בווידאו'))],ex,book_url,ypath,title=spec['title'],extra_title='חלקים נוספים בסדרה')
    words=len(re.findall(r'[א-ת]{2,}',chk))
    out.append({'file':os.path.relpath(ypath,REPO+'/ספרי יהודה טאוב/שיעורי יוטיוב'),'book':bpath.replace(REPO+'/',''),'title':spec['title'],'subtitle':spec['subtitle'],'parsha':spec['parsha'],'cards':r['cards'],'chapters':r['chapters'],'video':'https://youtu.be/'+spec['video'],'videos':['https://youtu.be/'+v for v in [spec['video']]+spec.get('extra_videos',[])],'folder':spec['folder'],'words':words})
    print(spec['title'],'| words',words,'| cards',len(r['cards']))
json.dump(out,open('/tmp/batch_out.json','w'),ensure_ascii=False)
