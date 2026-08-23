#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""בודק את הקטלוג "סיפורי התנאים והאמוראים" לפני העלאה.

    python3 scripts/check_catalog.py            # בדיקה מלאה
    python3 scripts/check_catalog.py --list     # הפרקים והדורות
    python3 scripts/check_catalog.py --links    # פילוח הקישורים לפי אתר יעד
"""
import html, json, re, sys, collections, urllib.parse
from html.parser import HTMLParser

CATALOG = 'tzadikim_catalog_with_52_learning_games.html'
BOOK = 'גדולי ישראל לדורותיהם.html'
BOOK_URL_TAIL = '%D7%9C%D7%93%D7%95%D7%A8%D7%95%D7%AA%D7%99%D7%94%D7%9D.html'
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
        sub = re.search(r'<div class="chapter-subtitle">(.*?)</div>', m.group(2))
        yield dict(anchor=m.group(1), title=strip_tags(title.group(1)),
                   subtitle=strip_tags(sub.group(1)),
                   cards=re.findall(r'<article class="story-card[^"]*" id="(story-\d+)"', m.group(2)))


def eras(doc):
    prefix, sep, tail = doc.partition('<section class="era-block"')
    for part in (sep + tail).split('<section class="era-block"'):
        m = re.match(r' id="([^"]+)"', part)
        if m:
            yield m.group(1), part


def main():
    doc = open(CATALOG, encoding='utf-8').read()
    chs = list(chapters(doc))
    ids = re.findall(r'<article class="story-card[^"]*" id="(story-\d+)"', doc)

    if '--list' in sys.argv:
        for key, part in eras(doc):
            title = re.search(r'<h2 class="era-banner-title">(.*?)</h2>', part, re.S)
            print('\n### %-12s %s' % (key, strip_tags(title.group(1))))
            for c in chapters(part):
                print('   %-34s %s' % (c['title'], c['subtitle']))
        print('\nסה"כ %d פרקים, %d כרטיסים.' % (len(chs), len(ids)))
        return

    if '--links' in sys.argv:
        by_host = collections.Counter()
        for href in re.findall(r'<a[^>]*href="(https?://[^"]+)"', doc):
            by_host[urllib.parse.urlparse(href).netloc] += 1
        for hostname, n in by_host.most_common():
            print('%5d  %s' % (n, hostname))
        labels = collections.Counter(re.findall(r'>([^<]*↗)</a>', doc))
        print('\nתוויות:')
        for label, n in labels.most_common(12):
            print('%5d  %s' % (n, label))
        return

    bad = []
    anchors = set(re.findall(r'id="([^"]+)"', doc))

    if len(ids) != len(set(ids)):
        bad.append('מזהים כפולים: %s' % ', '.join(sorted({i for i in ids if ids.count(i) > 1})))

    toc = doc[:doc.index('</aside>')]
    in_toc = set(re.findall(r'<li><a href="#(story-\d+)">', toc))
    missing = [i for i in ids if i not in in_toc]
    orphan = [i for i in in_toc if i not in ids]
    if missing:
        bad.append('כרטיסים שאינם בתוכן העניינים: %s' % ', '.join(missing[:8]))
    if orphan:
        bad.append('פריטי תוכן עניינים ללא כרטיס: %s' % ', '.join(sorted(orphan)[:8]))

    for c in chs:
        want = 'סיפור אחד' if len(c['cards']) == 1 else '%d סיפורים' % len(c['cards'])
        if c['subtitle'] != want:
            bad.append('הפרק "%s" מונה %s אך כתוב בו "%s"' % (c['title'], want, c['subtitle']))
        m = re.search(r'<a href="#%s" class="toc-sage-link">.*?<span class="toc-count">(.*?)</span>'
                      % re.escape(c['anchor']), toc, re.S)
        if not m:
            bad.append('הפרק "%s" חסר בסרגל' % c['title'])
        elif strip_tags(m.group(1)) != want:
            bad.append('בסרגל הפרק "%s" כתוב "%s" במקום "%s"'
                       % (c['title'], strip_tags(m.group(1)), want))

    for key, part in eras(doc):
        n = part.count('<article class="story-card')
        m = re.search(r'<div class="toc-era" id="toc-%s">.*?<span class="toc-era-count">(\d+)</span>'
                      % re.escape(key), doc, re.S)
        if not m:
            bad.append('הדור %s חסר בסרגל' % key)
        elif int(m.group(1)) != n:
            bad.append('בסרגל הדור %s מונה %s אך יש %d' % (key, m.group(1), n))
        b = re.search(r'<div class="era-banner-sub">(.*?)</div>', part)
        if b and ('%d סיפורים' % n) not in b.group(1) and not (n == 1 and 'סיפור אחד' in b.group(1)):
            bad.append('כותרת הדור %s אינה תואמת (%d כרטיסים): %s' % (key, n, strip_tags(b.group(1))))

    for i, sid in enumerate(ids):
        m = re.search(r'<article class="story-card[^"]*" id="%s".*?'
                      r'<div class="story-navigation">(.*?)</div>' % sid, doc, re.S)
        nav = re.findall(r'href="#(story-\d+)"', m.group(1))
        want = ([ids[i - 1]] if i else []) + ([ids[i + 1]] if i < len(ids) - 1 else [])
        if nav != want:
            bad.append('שרשרת הניווט שבורה אצל %s (מצאתי %s, ציפיתי ל-%s)' % (sid, nav, want))
            break

    data = json.loads(re.search(r'const searchData = (\[.*?\]);\n', doc, re.S).group(1))
    ghosts = [d['id'] for d in data if d['id'] not in anchors]
    unindexed = [i for i in ids if i not in {d['id'] for d in data}]
    if ghosts:
        bad.append('החיפוש מפנה לכרטיסים שאינם בעמוד: %s' % ', '.join(ghosts[:8]))
    if unindexed:
        bad.append('כרטיסים שאינם בחיפוש: %s' % ', '.join(unindexed[:8]))

    broken = [h for h in set(re.findall(r'href="#([^"]+)"', doc))
              if h not in anchors and '+' not in h]
    if broken:
        bad.append('קישורים פנימיים ללא יעד: %s' % ', '.join(sorted(broken)[:8]))

    for pat, actual, what in [(r'📚 (\d+) סיפורים', len(ids), 'כרטיסים'),
                              (r'👑 (\d+) דמויות', len(chs), 'פרקים')]:
        m = re.search(pat, doc)
        if m and int(m.group(1)) != actual:
            bad.append('בכותרת כתוב %s %s אך יש %d' % (m.group(1), what, actual))

    # כל כרטיס חייב שדות מלאים — כרטיס בלי תיאור או בלי קישור הוא כרטיס מת
    for m in re.finditer(r'<article class="story-card[^"]*" id="(story-\d+)"(.*?)</article>', doc, re.S):
        sid, card = m.group(1), m.group(2)
        for field, label in [(r'<span class="who">(.*?)</span>', 'שם דמות'),
                             (r'<h3 class="story-title">(.*?)</h3>', 'כותרת'),
                             (r'<p class="story-desc">(.*?)</p>', 'תיאור')]:
            f = re.search(field, card, re.S)
            if not f or not strip_tags(f.group(1)):
                bad.append('לכרטיס %s חסר %s' % (sid, label))
        if not re.search(r'<div class="story-links">\s*<a', card):
            bad.append('לכרטיס %s אין אף קישור' % sid)
        if 'copyStoryLink(\'%s\'' % sid not in card:
            bad.append('לכרטיס %s אין כפתור העתקת קישור תקין' % sid)

    # קישורים חיצוניים חייבים להיפתח בכרטיסייה חדשה, אחרת הקורא מאבד את הקטלוג
    for m in re.finditer(r'<a([^>]*)href="(https?://[^"]+)"([^>]*)>', doc):
        attrs = m.group(1) + m.group(3)
        if 'target="_blank"' not in attrs:
            bad.append('קישור חיצוני בלי target="_blank": %s' % m.group(2)[:70])
            break

    if '<meta charset="UTF-8">' not in doc:
        bad.append('חסר <meta charset="UTF-8">')

    p = Balance()
    p.feed(doc)
    if p.errors or p.stack:
        bad.append('HTML לא תקין: %s' % '; '.join(p.errors[:5] +
                                                  ['<%s> נשאר פתוח' % t for t in p.stack[:3]]))

    # קישורי הקריאה אל הספר — חייבים למצוא עוגן אמיתי שם
    try:
        book = open(BOOK, encoding='utf-8').read()
    except FileNotFoundError:
        book = None
    if book:
        book_anchors = set(re.findall(r'id="([^"]+)"', book))
        frags = re.findall(r'href="[^"]*%s#([^"]+)"' % re.escape(BOOK_URL_TAIL), doc)
        dead = sorted({f for f in frags if f not in book_anchors})
        print('קישורי קריאה אל הספר: %d, מהם %d מוצאים יעד.' % (len(frags), len(frags) - len(dead)))
        if dead:
            bad.append('קישורים אל הספר ללא יעד: %s' % ', '.join(dead[:8]))

    print('הקטלוג: %d כרטיסים ב-%d פרקים.' % (len(ids), len(chs)))
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
        sys.stderr.close()
