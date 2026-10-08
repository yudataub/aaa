import re, json, html, subprocess, sys
REPO='/home/user/aaa'
TPL_PATH='ספרי יהודה טאוב/פרשת שבוע וחגים/שיעורי קול תודה -  פרשת השבוע/008 וישלח/מדת הרחמים.html'
def esc(s): return html.escape(s, quote=False)
def inline(s):
    s=esc(s)
    return re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
def template():
    return subprocess.run(['git','-C',REPO,'show','origin/main:'+TPL_PATH],capture_output=True,text=True).stdout
def block(b):
    k=b[0]; t=b[1]
    if k=='p': return '    <p>'+inline(t)+'</p>'
    if k=='box': return '    <div class="highlight-box">\n        <p>'+inline(t)+'</p>\n    </div>'
    if k=='verse': return '    <div class="verse-box">\n        <p>'+inline(t)+'</p>\n    </div>'
    if k=='story':  # (story, title, [paras])
        ps='\n'.join('        <p>'+inline(x)+'</p>' for x in b[2])
        return '    <div class="story-box">\n        <span class="story-title">'+esc(t)+'</span>\n'+ps+'\n    </div>'
    raise ValueError(k)
def build(spec, video_id, out_path):
    t=template()
    pre=t[:t.index('<div class="container">')]
    pre=re.sub(r'<title>.*?</title>','<title>'+esc(spec['title'])+'</title>',pre,count=1,flags=re.S)
    pre=re.sub(r'(<meta name="description" content=")[^"]*(")',lambda m:m.group(1)+esc(spec['description'])+m.group(2),pre,count=1)
    listen=t[t.index('<div class="listen-bar">'):t.index('<nav class="chapter-grid"')]
    post=t[t.index('<div class="footer">'):]
    chips=['        <a class="chapter-chip is-front" href="#intro"><span class="n">◆</span>הקדמה</a>']
    toc=[]
    body=['    <h2 id="intro">הקדמה</h2>']
    for b in spec['intro']: body.append(block(b))
    letters='אבגדהוזחטי'
    for ci,ch in enumerate(spec['chapters'],1):
        chips.append(f'        <a class="chapter-chip" href="#section{ci}"><span class="n">{ci}</span>{esc(ch["name"])}</a>')
        subs='<span>·</span>'.join(f'<a href="#sec{ci}{chr(96+si)}">{esc(s["title"])}</a>' for si,s in enumerate(ch['sections'],1))
        toc.append(f'            <li>\n                <a class="toc-chapter" href="#section{ci}">{esc(ch["name"])}</a>\n                <span class="toc-subs">\n                    {subs}\n                </span>\n            </li>')
        body.append(f'    <span class="chapter-label">פרק {letters[ci-1]}</span>\n    <h2 id="section{ci}">{esc(ch["name"])}</h2>')
        body.append('    <div class="in-this-chapter">\n        <h4>📖 בפרק זה:</h4>\n        <ul>\n'+'\n'.join('            <li>'+esc(s['title'])+'</li>' for s in ch['sections'])+'\n        </ul>\n    </div>')
        for si,s in enumerate(ch['sections'],1):
            body.append(f'    <h3 id="sec{ci}{chr(96+si)}">{esc(s["title"])}</h3>')
            for b in s['blocks']: body.append(block(b))
        if ci<len(spec['chapters']):
            nxt=spec['chapters'][ci]
            body.append(f'    <div class="chapter-card">\n        <span class="num">{letters[ci]}</span>\n        <span class="name">{esc(nxt["name"])}</span>\n    </div>\n    <div class="chapter-divider">✡</div>')
    if spec.get('closing'): body.append(block(('box',spec['closing'])))
    src=''
    if spec.get('sources'):
        src='    <div class="sources">\n        <h3>📚 מקורות ומראי מקומות</h3>\n        <ol>\n'+'\n'.join('            <li>'+inline(x)+'</li>' for x in spec['sources'])+'\n        </ol>\n    </div>\n\n'
    head=f'''<div class="container">

    <h1 class="main-title" id="top">{esc(spec['title'])}</h1>
    <div class="subtitle">{esc(spec['subtitle'])}</div>
    <div class="author">{esc(spec['author'])}</div>

    <!-- קישור לצפייה בשיעור המקורי -->
    <div class="highlight-box" style="text-align:center;">
        <p>🎧 לצפייה בשיעור המקורי ביוטיוב: <a href="https://www.youtube.com/watch?v={video_id}" target="_blank" rel="noopener">לחצו כאן</a></p>
    </div>

    '''
    nav='    <nav class="chapter-grid" aria-label="מבט על פרקי הספר">\n        <h2 class="grid-title">פִּרְקֵי הַסֵּפֶר</h2>\n'+'\n'.join(chips)+'\n    </nav>\n\n    <div class="toc">\n        <h3>📑 תוכן העניינים</h3>\n        <ul>\n'+'\n'.join(toc)+'\n        </ul>\n    </div>\n\n'
    doc=pre+head+listen+nav+'\n\n'.join(body)+'\n\n'+src+'    '+post
    open(out_path,'w',encoding='utf8').write(doc)
    return doc
