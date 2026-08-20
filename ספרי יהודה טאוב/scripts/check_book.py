#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""בודק את ספר "גדולי ישראל לדורותיהם" לפני העלאה.

כל בדיקה כאן מתאימה לתקלה שכבר קרתה פעם, ורובן בלתי־נראות במבט מהיר —
סיפור שהגיע למדד החיפוש אבל לא לעמוד נראה מושלם עד שקורא לוחץ על תוצאה
ונוחת בשום מקום.

    python3 scripts/check_book.py          # בדיקה מלאה
    python3 scripts/check_book.py --list   # רשימת הפרקים ומספריהם
"""
import html, json, re, sys
from html.parser import HTMLParser

BOOK = 'גדולי ישראל לדורותיהם.html'
CATALOG = 'tzadikim_catalog_with_52_learning_games.html'
VOID = {'meta', 'link', 'img', 'br', 'hr', 'input', 'source', 'area',
        'base', 'col', 'embed', 'param', 'track', 'wbr'}


def strip_tags(t):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', t))).strip()


class Balance(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.errors = [], []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack:
            self.errors.append('סגירה מיותרת של <%s>' % tag)
        elif self.stack[-1] != tag:
            if tag in self.stack:
                while self.stack[-1] != tag:
                    self.errors.append('תג <%s> לא נסגר' % self.stack.pop())
                self.stack.pop()
            else:
                self.errors.append('סגירה תלושה של <%s>' % tag)
        else:
            self.stack.pop()


def chapters(doc):
    for m in re.finditer(r'<section class="chapter-section" id="([^"]+)">(.*?)\n</section>',
                         doc, re.S):
        title = re.search(r'<h2 class="chapter-title">(.*?)</h2>', m.group(2), re.S)
        legacy = re.search(r'<span class="legacy-anchor" id="(ch-[\d-]+)">', m.group(2))
        yield dict(anchor=m.group(1), title=strip_tags(title.group(1)),
                   legacy=legacy.group(1) if legacy else None,
                   stories=re.findall(r'<article class="story-card" id="(story-\d+)"', m.group(2)),
                   subtitle=strip_tags(re.search(r'<div class="chapter-subtitle">(.*?)</div>',
                                                 m.group(2)).group(1)))


def main():
    doc = open(BOOK, encoding='utf-8').read()
    chs = list(chapters(doc))

    if '--list' in sys.argv:
        for c in chs:
            print('%-4s %-34s %s' % (c['legacy'] or '', c['title'], c['subtitle']))
        print('\nסה"כ %d פרקים, %d סיפורים.'
              % (len(chs), doc.count('<article class="story-card"')))
        return

    bad = []
    ids = re.findall(r'<article class="story-card" id="(story-\d+)"', doc)
    anchors = set(re.findall(r'id="([^"]+)"', doc))

    if len(ids) != len(set(ids)):
        dupes = {i for i in ids if ids.count(i) > 1}
        bad.append('מזהי סיפורים כפולים: %s' % ', '.join(sorted(dupes)))

    # כל סיפור בעמוד חייב להופיע בתוכן העניינים, ולהיפך
    toc = doc[:doc.index('</aside>')]
    in_toc = set(re.findall(r'<li><a href="#(story-\d+)">', toc))
    missing = [i for i in ids if i not in in_toc]
    orphan = [i for i in in_toc if i not in ids]
    if missing:
        bad.append('סיפורים שאינם בתוכן העניינים: %s' % ', '.join(missing[:8]))
    if orphan:
        bad.append('פריטי תוכן עניינים ללא סיפור בעמוד: %s' % ', '.join(sorted(orphan)[:8]))

    # מוני הפרקים — בעמוד ובסרגל
    for c in chs:
        want = 'סיפור אחד' if len(c['stories']) == 1 else '%d סיפורים' % len(c['stories'])
        if c['subtitle'] != want:
            bad.append('הפרק "%s" מונה %s אך כתוב בו "%s"' % (c['title'], want, c['subtitle']))
        m = re.search(r'<a href="#%s" class="toc-sage-link">.*?<span class="toc-count">(.*?)</span>'
                      % re.escape(c['anchor']), toc, re.S)
        if not m:
            bad.append('הפרק "%s" חסר בסרגל תוכן העניינים' % c['title'])
        elif strip_tags(m.group(1)) != want:
            bad.append('בסרגל הפרק "%s" כתוב "%s" במקום "%s"'
                       % (c['title'], strip_tags(m.group(1)), want))

    # שרשרת הקודם/הבא לפי סדר הקריאה
    for i, sid in enumerate(ids):
        m = re.search(r'<article class="story-card" id="%s".*?'
                      r'<div class="story-navigation">(.*?)</div>' % sid, doc, re.S)
        nav = re.findall(r'href="#(story-\d+)"', m.group(1))
        want = ([ids[i - 1]] if i else []) + ([ids[i + 1]] if i < len(ids) - 1 else [])
        if nav != want:
            bad.append('שרשרת הניווט שבורה אצל %s (מצאתי %s, ציפיתי ל-%s)' % (sid, nav, want))
            break

    # מדד החיפוש
    data = json.loads(re.search(r'const searchData = (\[.*?\]);\n', doc, re.S).group(1))
    ghosts = [d['id'] for d in data if d['id'] not in anchors]
    unindexed = [i for i in ids if i not in {d['id'] for d in data}]
    if ghosts:
        bad.append('החיפוש מפנה לסיפורים שאינם בעמוד: %s' % ', '.join(ghosts[:8]))
    if unindexed:
        bad.append('סיפורים שאינם בחיפוש: %s' % ', '.join(unindexed[:8]))

    # עוגנים פנימיים
    broken = [h for h in set(re.findall(r'href="#([^"]+)"', doc))
              if h not in anchors and '+' not in h]
    if broken:
        bad.append('קישורים פנימיים ללא יעד: %s' % ', '.join(sorted(broken)[:8]))

    # מוני הכותרת הראשית
    for pat, actual, what in [(r'📚 (\d+) סיפורים', len(ids), 'הסיפורים'),
                              (r'👑 (\d+) דמויות ופרקים', len(chs), 'הפרקים')]:
        m = re.search(pat, doc)
        if m and int(m.group(1)) != actual:
            bad.append('בכותרת כתוב %s %s אך יש %d' % (m.group(1), what, actual))

    if '<meta charset="UTF-8">' not in doc:
        bad.append('חסר <meta charset="UTF-8"> — בלעדיו העברית תישבר אצל חלק מהשרתים')

    p = Balance()
    p.feed(doc)
    if p.errors or p.stack:
        bad.append('HTML לא תקין: %s' % '; '.join(p.errors[:5] + ['<%s> נשאר פתוח' % t
                                                                 for t in p.stack[:3]]))

    # הקטלוג, אם הוא לצד הספר: כל קישורי הקריאה חייבים למצוא יעד
    try:
        cat = open(CATALOG, encoding='utf-8').read()
    except FileNotFoundError:
        cat = None
    if cat:
        frags = re.findall(r'href="[^"]*%s#([^"]+)"'
                           % re.escape('%D7%9C%D7%93%D7%95%D7%A8%D7%95%D7%AA%D7%99%D7%94%D7%9D.html'),
                           cat)
        dead = sorted({f for f in frags if f not in anchors})
        print('הקטלוג: %d קישורי קריאה, %d מוצאים יעד.' % (len(frags), len(frags) - len(dead)))
        if dead:
            bad.append('קישורים בקטלוג ללא יעד בספר: %s' % ', '.join(dead[:8]))

    print('הספר: %d סיפורים ב-%d פרקים.' % (len(ids), len(chs)))
    if bad:
        print('\nנמצאו %d תקלות:' % len(bad))
        for b in bad:
            print('  ✗ ' + b)
        sys.exit(1)
    print('כל הבדיקות עברו. אפשר להעלות.')


if __name__ == '__main__':
    try:
        main()
    except BrokenPipeError:
        # ‏הפלט נחתך על ידי head או less — לא תקלה בספר
        sys.stderr.close()
