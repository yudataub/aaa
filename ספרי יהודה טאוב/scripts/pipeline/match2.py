import re,json,difflib,collections,sys
NIK=re.compile(r'[֑-ׇ]')
def norm(s):
    s=NIK.sub('',s); s=s.replace('_',' ').replace('"','').replace("'",'').replace('׳','').replace('״','').replace('-',' ').replace('—',' ').replace('–',' ')
    s=re.sub(r'[🔶📜📚🏜️🕍\*\.,:;!?()\[\]]',' ',s); return re.sub(r'\s+',' ',s).strip()
def core(t):
    t=re.split(r'[,،]\s*פרשת',t)[0]; t=re.sub(r'\s+[-–]\s*פרשת.*$','',t)
    t=re.sub(r'^[\d\s\-]+','',t.strip()); t=re.sub(r' (קול תודה|גברים).*$','',t)
    return norm(t)
UP='/root/.claude/uploads/bf25bffc-af4e-5f9d-9c53-c58411494098/'
vids=[]
for p in ['7426a9d7-______________.txt','32397a4f-__________2.txt']:
    L=open(UP+p,encoding='utf8').read().split('\n')
    for i,l in enumerate(L):
        m=re.match(r'https://www.youtube.com/watch\?v=([\w-]{11})',l)
        if m and i>0 and L[i-1].strip(): vids.append((L[i-1].strip(),m.group(1)))
seen=set();V=[]
for t,i in vids:
    if i not in seen: seen.add(i); V.append((t,i))
used=set()
L=json.load(open('/home/user/aaa/ספרי יהודה טאוב/שיעורי יוטיוב/lessons.json',encoding='utf8'))['lessons']
for l in L:
    for u in [l.get('video')]+(l.get('videos') or []):
        if u: used.add(u.rsplit('/',1)[-1].replace('watch?v=',''))
paths=[x for x in open('/tmp/kt3.txt',encoding='utf8').read().split('\n') if x.endswith('.html') and not x.endswith('index.html') and 'ספר דיגיטלי' not in x]
def bnorm(n):
    n=norm(n); n=re.sub(r'^מאמר ','',n); n=re.sub(r' הרב יהודה טאוב.*$','',n); n=re.sub(r' פרשת [א-ת ]+$','',n); return n.strip()
B={}
for p in paths: B.setdefault(bnorm(p.rsplit('/',1)[1][:-5]),[]).append(p)
keys=list(B)
rows=[]
for t,i in V:
    if i in used: continue
    c=re.sub(r' פרשת [א-ת ]+$','',core(t))
    best=max(keys,key=lambda b:difflib.SequenceMatcher(None,c,b).ratio())
    r=difflib.SequenceMatcher(None,c,best).ratio()
    rows.append((t,i,c,best,round(r,3)))
json.dump({'rows':rows,'used':sorted(used)},open('/tmp/match2.json','w'),ensure_ascii=False)
print('videos',len(V),'already used',len(used&{i for _,i in V}),'remaining',len(rows),'books',len(paths))
buck=collections.Counter('>=0.97' if r>=0.97 else '0.85-0.97' if r>=0.85 else '<0.85' for *_,r in rows); print(buck)
