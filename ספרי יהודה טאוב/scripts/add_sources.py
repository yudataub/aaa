#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""מוסיף לראש כל סיפור את מקורו בחז"ל, עם ציטוט מלא מתוך ספריא.

המקורות שמורים ב‑`scripts/sources.json` — מפתח לכל סיפור, ובו מראה המקום
בעברית, קישור לספריא, והציטוט עצמו כפי שנשלף משם. הסקריפט אינו ממציא
מקורות ואינו פונה לרשת: הוא מזריק לספר את מה שכבר אומת ונשמר בקובץ.

הרצה חוזרת מחליפה בלוקים קיימים במקום לשכפל אותם.

    python3 scripts/add_sources.py            # הזרקה
    python3 scripts/add_sources.py --check    # רק דיווח, בלי לכתוב
"""
import html, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BOOK = os.path.join(os.path.dirname(HERE), 'גדולי ישראל לדורותיהם.html')
DATA = os.path.join(HERE, 'sources.json')

CSS = """
/* ═══ בלוק המקור בראש הסיפור ═══════════════════════════════════════════ */
.source-box {
  background: linear-gradient(135deg, #fff8e1 0%, #fff3f8 100%);
  border: 2px dashed #ffb74d;
  border-radius: 16px;
  padding: 1rem 1.2rem;
  margin: 0 0 1.4rem;
}
.source-ref {
  font-weight: 900; color: #b26a00; font-size: 1.02rem;
  margin-bottom: .55rem; line-height: 1.5;
}
.source-quote {
  font-size: 1.05rem; line-height: 2; color: #3d2b00;
  border-right: 4px solid #ffb74d; padding-right: .9rem; margin: 0;
}
.source-link { margin-top: .6rem; font-size: .9rem; }
.source-link a { color: #b26a00; font-weight: 700; }
@media print { .source-box { break-inside: avoid; } .source-link { display: none; } }
"""

BLOCK = ('<div class="source-box">\n'
         '<div class="source-ref">📜 הַמָּקוֹר: {label}</div>\n'
         '<blockquote class="source-quote">{text}</blockquote>\n'
         '<div class="source-link"><a href="{url}" target="_blank" rel="noopener">'
         'לַמָּקוֹר הַמָּלֵא בְּסֶפָרְיָא ↗</a></div>\n'
         '</div>\n')

EXISTING = re.compile(r'<div class="source-box">.*?</div>\n</div>\n', re.S)


def main():
    check = '--check' in sys.argv
    doc = open(BOOK, encoding='utf-8').read()
    src = json.load(open(DATA, encoding='utf-8'))

    if '.source-box' not in doc:
        doc = doc.replace('\n/* ═══ CONFETTI', CSS + '\n/* ═══ CONFETTI', 1)
        if '.source-box' not in doc:
            sys.exit('לא נמצא מקום לשתול בו את ה‑CSS')

    added = replaced = 0
    for sid, s in src.items():
        head = '<article class="story-card" id="story-%s"' % sid
        i = doc.find(head)
        if i < 0:
            sys.exit('הסיפור story-%s אינו בספר' % sid)
        j = doc.index('<div class="story-body">', i) + len('<div class="story-body">')
        rest = doc[j:]
        m = EXISTING.match(rest.lstrip('\n'))
        if m:
            lead = len(rest) - len(rest.lstrip('\n'))
            doc = doc[:j + lead] + doc[j + lead + m.end():]
            replaced += 1
        else:
            added += 1
        block = BLOCK.format(label=html.escape(s['label']),
                             text=html.escape(s['text']),
                             url=html.escape(s['url'], quote=True))
        doc = doc[:j] + '\n' + block + doc[j:]

    print('בלוקי מקור: %d נוספו, %d הוחלפו. סיפורים ללא מקור: %d.'
          % (added, replaced, doc.count('<article class="story-card"') - len(src)))
    if check:
        print('(--check: הקובץ לא נכתב)')
        return
    open(BOOK, 'w', encoding='utf-8').write(doc)
    print('נכתב. הרץ עכשיו: python3 scripts/check_book.py')


if __name__ == '__main__':
    main()
