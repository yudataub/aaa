# -*- coding: utf-8 -*-
import sys; sys.path.insert(0,'/tmp/pres')
from deck import *
BASE='/home/user/aaa/ספרי יהודה טאוב/פרשת שבוע וחגים/שיעורי קול תודה -  פרשת השבוע/001 בראשית/'
def P(t,c=''): return f'<p class="{c}">{t}</p>'
def H(t): return f'<span class="hl">{t}</span>'
def T(theme,title,*parts): return content(theme,title,''.join(parts))
def G(n,title,sub): return gate(title,sub)
def li(items): return '<ul class="pts">'+''.join(f'<li>{x}</li>' for x in items)+'</ul>'
def save(book, ttl, slides):
    return build(ttl, slides, BASE+f'מצגת - {book}.html')

_q=quiz
def quiz(n,question,options,correct,ok,bad):
    # rotate so the correct answer's position varies between questions
    pos=[2,0,3,1,2,3,0,1][(sum(map(ord,question)))%8]
    opts=list(options); c=opts.pop(correct); opts.insert(pos,c)
    return _q(n,question,opts,pos,ok,bad)
