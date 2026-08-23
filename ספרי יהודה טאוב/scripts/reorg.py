#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""מעביר סיפורים בין פרקים, פותח פרק חדש וסוגר פרק שהתרוקן.

הספר מחזיק שישה דברים שחייבים להסכים זה עם זה, ורובם נגזרים מן המבנה
עצמו. לכן הסקריפט מזיז רק שני דברים ביד — כרטיס הסיפור ופריט תוכן
העניינים שלו — ואת כל השאר (מוני הפרק, מוני הדור, מוני הכותרת, שרשרת
הקודם/הבא וסדר מדד החיפוש) הוא בונה מחדש מן המסמך שאחרי ההזזה.

מזהי הסיפורים אינם משתנים לעולם, גם כשהסיפור עובר פרק.

    python3 scripts/reorg.py \
        --create "מעשי צדיקים|📜|#a29bfe|#efeaff|מר זוטרא" \
        --move "122|מעשי צדיקים" \
        --retitle "122|כותרת חדשה|כותרת משנה" \
        --prune
"""
import argparse, html, json, re, sys

BOOK = 'gdolei_yisrael_ledorotam.html'


def plural(n):
    return 'סיפור אחד' if n == 1 else '%d סיפורים' % n


def strip_tags(t):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', t))).strip()


def fold(t):
    return re.sub(r'[^\w֐-׿]+', '', re.sub(r'[֑-ׇ]', '', strip_tags(t)))


def chapter_span(doc, wanted):
    """(start, end, anchor, title) של הפרק המבוקש — לפי שם, עוגן או מזהה ישן."""
    for m in re.finditer(r'<section class="chapter-section" id="([^"]+)">(.*?)\n</section>',
                         doc, re.S):
        anchor, inner = m.group(1), m.group(2)
        legacy = re.search(r'<span class="legacy-anchor" id="([^"]+)">', inner)
        title = re.search(r'<h2 class="chapter-title">(.*?)</h2>', inner, re.S)
        names = {anchor, legacy.group(1) if legacy else '', fold(title.group(1))}
        if wanted in names or fold(wanted) in names:
            return m.start(), m.end(), anchor, strip_tags(title.group(1))
    sys.exit('לא נמצא פרק בשם %r.' % wanted)


def chapter_colours(doc, anchor):
    s, e, _, _ = chapter_span(doc, anchor)
    m = re.search(r'border-top:6px solid (#[0-9a-fA-F]{6})">\s*'
                  r'<div class="story-header" style="background:(#[0-9a-fA-F]{6})">',
                  doc[s:e])
    return (m.group(1), m.group(2)) if m else ('#a29bfe', '#efeaff')


def cut_card(doc, sid):
    m = re.search(r'\n?<article class="story-card" id="story-%s".*?</article>\n?' % sid,
                  doc, re.S)
    if not m:
        sys.exit('הסיפור story-%s אינו בספר.' % sid)
    return doc[:m.start()] + '\n' + doc[m.end():], m.group(0).strip('\n')


def cut_toc_item(doc, sid):
    m = re.search(r'<li><a href="#story-%s">.*?</li>\n?' % sid, doc, re.S)
    if not m:
        sys.exit('פריט תוכן העניינים של story-%s חסר.' % sid)
    return doc[:m.start()] + doc[m.end():], m.group(0).rstrip('\n')


def create_chapter(doc, spec):
    title, icon, colour, tint, after = [x.strip() for x in spec.split('|')]
    anchor = 'chapter-' + re.sub(r'\s+', '-', re.sub(r'[^\w֐-׿ ]', '', title)).strip('-')
    if 'id="%s"' % anchor in doc:
        sys.exit('כבר קיים פרק בעוגן %s.' % anchor)
    dark = colour.replace('#', '#')
    section = (
        '<section class="chapter-section" id="{a}">\n'
        '<div class="chapter-header" style="background:linear-gradient(135deg,{c},{c})">'
        '<div class="chapter-icon">{i}</div><div><h2 class="chapter-title">{t}</h2>'
        '<div class="chapter-subtitle">אין סיפורים</div></div></div>\n'
        '</section>\n'
    ).format(a=anchor, c=dark, i=icon, t=title)
    s, e, prev_anchor, _ = chapter_span(doc, after)
    doc = doc[:e] + '\n' + section + doc[e:]

    toc = (
        '<div class="toc-chapter" style="border-color:{c}">\n'
        '<div class="toc-chapter-title" style="background:{c}" onclick="toggleTocChapter(this)">'
        '<span class="toc-icon">{i}</span><a href="#{a}" class="toc-sage-link">{t}</a>'
        '<span class="toc-count">אין סיפורים</span><span class="toc-arrow">▼</span></div>\n'
        '<ul class="toc-stories">\n</ul>\n</div>\n'
    ).format(a=anchor, c=colour, i=icon, t=title)
    pm = re.search(r'<div class="toc-chapter"[^>]*>(?:(?!</div>\n</div>).)*?'
                   r'href="#%s"(?:(?!</ul>\n</div>).)*?</ul>\n</div>\n?' % re.escape(prev_anchor),
                   doc, re.S)
    if not pm:
        sys.exit('לא נמצא בלוק תוכן עניינים של הפרק %r.' % after)
    doc = doc[:pm.end()] + toc + doc[pm.end():]
    return doc, anchor, title


def move_story(doc, sid, target):
    doc, card = cut_card(doc, sid)
    doc, item = cut_toc_item(doc, sid)
    s, e, anchor, title = chapter_span(doc, target)
    colour, tint = chapter_colours(doc, anchor)
    card = re.sub(r'border-top:6px solid #[0-9a-fA-F]{6}',
                  'border-top:6px solid ' + colour, card, count=1)
    card = re.sub(r'(<div class="story-header" style="background:)#[0-9a-fA-F]{6}',
                  r'\1' + tint, card, count=1)
    card = re.sub(r'(<span class="story-num" style="background:)#[0-9a-fA-F]{6}',
                  r'\1' + colour, card, count=1)
    section = doc[s:e]
    section = section[:section.rindex('\n</section>')] + '\n' + card + '\n</section>'
    doc = doc[:s] + section + doc[e:]

    tm = re.search(r'(<div class="toc-chapter"[^>]*>(?:(?!</ul>\n</div>).)*?'
                   r'href="#%s"(?:(?!</ul>\n</div>).)*?)</ul>' % re.escape(anchor), doc, re.S)
    if not tm:
        sys.exit('לא נמצא בלוק תוכן עניינים של %r.' % title)
    doc = doc[:tm.end(1)] + item + '\n</ul>' + doc[tm.end():]
    return doc, title


def retitle(doc, sid, title, subtitle):
    m = re.search(r'<article class="story-card" id="story-%s".*?</article>' % sid, doc, re.S)
    card = m.group(0)
    card = re.sub(r'(<h3 class="story-title">).*?(</h3>)',
                  lambda x: x.group(1) + title + x.group(2), card, count=1)
    if subtitle:
        if '<div class="story-subtitle">' in card:
            card = re.sub(r'(<div class="story-subtitle">).*?(</div>)',
                          lambda x: x.group(1) + subtitle + x.group(2), card, count=1)
        else:
            card = card.replace('</div>\n<div class="story-body">',
                                '</div>\n<div class="story-subtitle">%s</div>\n'
                                '<div class="story-body">' % subtitle, 1)
    doc = doc[:m.start()] + card + doc[m.end():]
    return re.sub(r'(<li><a href="#story-%s">).*?(</a>)' % sid,
                  lambda x: x.group(1) + title + x.group(2), doc, count=1)


def prune(doc):
    dropped = []
    while True:
        for m in re.finditer(r'<section class="chapter-section" id="([^"]+)">(.*?)\n</section>\n?',
                             doc, re.S):
            if '<article class="story-card"' in m.group(2):
                continue
            anchor = m.group(1)
            dropped.append(strip_tags(re.search(r'<h2 class="chapter-title">(.*?)</h2>',
                                                m.group(2), re.S).group(1)))
            doc = doc[:m.start()] + doc[m.end():]
            tm = re.search(r'<div class="toc-chapter"[^>]*>(?:(?!</ul>\n</div>).)*?'
                           r'href="#%s"(?:(?!</ul>\n</div>).)*?</ul>\n</div>\n?'
                           % re.escape(anchor), doc, re.S)
            if tm:
                doc = doc[:tm.start()] + doc[tm.end():]
            break
        else:
            return doc, dropped


def rebuild(doc):
    """בונה מחדש כל מה שנגזר מן המבנה."""
    # מוני הפרקים — בעמוד ובסרגל
    def per_chapter(m):
        inner = m.group(2)
        want = plural(inner.count('<article class="story-card"'))
        return m.group(0).replace(
            re.search(r'<div class="chapter-subtitle">.*?</div>', inner, re.S).group(0),
            '<div class="chapter-subtitle">%s</div>' % want, 1)
    doc = re.sub(r'<section class="chapter-section" id="([^"]+)">(.*?)\n</section>',
                 per_chapter, doc, flags=re.S)

    counts = {a: b.count('<article class="story-card"') for a, b in
              re.findall(r'<section class="chapter-section" id="([^"]+)">(.*?)\n</section>',
                         doc, re.S)}

    def toc_count(m):
        block = m.group(0)
        a = re.search(r'href="#(chapter-[^"]+)"', block)
        if not a or a.group(1) not in counts:
            return block
        return re.sub(r'(<span class="toc-count">).*?(</span>)',
                      lambda x: x.group(1) + plural(counts[a.group(1)]) + x.group(2),
                      block, count=1)
    doc = re.sub(r'<div class="toc-chapter"[^>]*>.*?</ul>\n</div>', toc_count, doc, flags=re.S)

    # מוני הדורות
    head, sep, rest = doc.partition('<section class="era-block"')
    parts = (sep + rest).split('<section class="era-block"')
    for i, part in enumerate(parts):
        if not part.strip():
            continue
        stories = part.count('<article class="story-card"')
        people = part.count('<section class="chapter-section"')

        def counters(x):
            desc = [d for d in x.group(2).split(' · ') if d.strip()
                    and 'סיפור' not in d and 'דמו' not in d]
            bits = desc + [plural(stories),
                           '%d דמויות' % people if people != 1 else 'דמות אחת']
            return x.group(1) + ' · '.join(bits) + x.group(3)
        parts[i] = re.sub(r'(<div class="era-banner-sub">)(.*?)(</div>)',
                          counters, part, count=1)
    doc = head + '<section class="era-block"'.join(parts)

    # מוני הכותרת הראשית
    total = doc.count('<article class="story-card"')
    chapters = doc.count('<section class="chapter-section"')
    doc = re.sub(r'(<div class="stat-bubble">📚 )\d+( סיפורים</div>)',
                 lambda m: '%s%d%s' % (m.group(1), total, m.group(2)), doc)
    doc = re.sub(r'(<div class="stat-bubble">👑 )\d+( דמויות ופרקים</div>)',
                 lambda m: '%s%d%s' % (m.group(1), chapters, m.group(2)), doc)

    # שרשרת הקודם/הבא
    order = re.findall(r'<article class="story-card" id="(story-\d+)"', doc)
    pos = {sid: i for i, sid in enumerate(order)}

    def nav(m):
        i = pos[m.group(2)]
        bits = ['<a class="back-to-toc-nav" href="#toc">📚 חזרה לתוכן העניינים</a>']
        if i > 0:
            bits.append('<a href="#%s">→ הסיפור הקודם</a>' % order[i - 1])
        if i < len(order) - 1:
            bits.append('<a href="#%s">הסיפור הבא ←</a>' % order[i + 1])
        return '%s<div class="story-navigation">%s</div>' % (m.group(1), ''.join(bits))
    doc = re.sub(r'(<article class="story-card" id="(story-\d+)".*?)'
                 r'<div class="story-navigation">.*?</div>', nav, doc, flags=re.S)

    # סדר מדד החיפוש, וכותרות שהשתנו
    m = re.search(r'const searchData = (\[.*?\]);\n', doc, re.S)
    data = json.loads(m.group(1))
    titles = dict(re.findall(r'<article class="story-card" id="(story-\d+)".*?'
                             r'<h3 class="story-title">(.*?)</h3>', doc, re.S))
    for d in data:
        if d['id'] in titles:
            d['title'] = strip_tags(titles[d['id']])
    data.sort(key=lambda d: pos.get(d['id'], 10 ** 6))
    return doc[:m.start(1)] + json.dumps(data, ensure_ascii=False) + doc[m.end(1):]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--create', action='append', default=[],
                    help='"כותרת|אייקון|צבע|גוון|אחרי-פרק"')
    ap.add_argument('--move', action='append', default=[], help='"מספר|פרק-יעד"')
    ap.add_argument('--retitle', action='append', default=[],
                    help='"מספר|כותרת|כותרת-משנה"')
    ap.add_argument('--prune', action='store_true', help='סגירת פרקים שהתרוקנו')
    ap.add_argument('--book', default=BOOK)
    a = ap.parse_args()

    doc = open(a.book, encoding='utf-8').read()
    for spec in a.create:
        doc, anchor, title = create_chapter(doc, spec)
        print('נפתח פרק "%s" (%s).' % (title, anchor))
    for spec in a.move:
        sid, target = [x.strip() for x in spec.split('|')]
        doc, title = move_story(doc, sid, target)
        print('story-%s הועבר לפרק "%s".' % (sid, title))
    for spec in a.retitle:
        parts = [x.strip() for x in spec.split('|')]
        doc = retitle(doc, parts[0], parts[1], parts[2] if len(parts) > 2 else '')
        print('story-%s שוּנתה כותרתו.' % parts[0])
    if a.prune:
        doc, dropped = prune(doc)
        for t in dropped:
            print('נסגר פרק ריק: "%s".' % t)
    doc = rebuild(doc)
    open(a.book, 'w', encoding='utf-8').write(doc)
    print('נכתב. הריצו עכשיו: python3 scripts/check_book.py')


if __name__ == '__main__':
    main()
