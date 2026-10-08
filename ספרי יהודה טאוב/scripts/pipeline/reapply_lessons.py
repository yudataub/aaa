# After taking main's lessons.json (theirs), re-add every Kol Toda video-page entry that exists as a file but is missing.
import json,os,re,subprocess,datetime,sys
sys.path.insert(0,'/tmp/claude-0/-home-user-aaa/bf25bffc-af4e-5f9d-9c53-c58411494098/scratchpad/work')
REPO='/home/user/aaa'; LJ=REPO+'/ספרי יהודה טאוב/שיעורי יוטיוב/lessons.json'
mine=json.loads(subprocess.run(['git','show','HEAD:ספרי יהודה טאוב/שיעורי יוטיוב/lessons.json'],capture_output=True,text=True,cwd=REPO).stdout)
base=json.load(open(LJ,encoding='utf8'))
pref='קול תודה - פרשת השבוע/'
have={l['file']:l for l in base['lessons']}
# keep my version of every Kol Toda entry (they are authoritative), keep main's others
mykt={l['file']:l for l in mine['lessons'] if l['file'].startswith(pref)}
others=[l for l in base['lessons'] if not l['file'].startswith(pref)]
kt=list(mykt.values())
kt.sort(key=lambda l:(l['file'].split('/')[1],l['title']))
for i,l in enumerate(kt,1): l['series_order']=i
base['lessons']=kt+others
base['updated']=max(base['updated'],mine['updated'])
open(LJ,'w',encoding='utf8').write(json.dumps(base,ensure_ascii=False,indent=2))
print('reapplied',len(kt),'kol toda +',len(others),'others')
