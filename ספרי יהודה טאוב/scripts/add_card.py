#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""מוסיף כרטיס אחד לקטלוג "סיפורי התנאים והאמוראים".

הקטלוג, כמו הספר, מחזיק שישה דברים שחייבים להסכים זה עם זה — מזהי הכרטיסים,
תוכן העניינים בסרגל, מוני הפרק והדור, שרשרת הקודם/הבא, ומדד החיפוש. לכן
ההוספה נעשית כאן ולא ביד.

    python3 scripts/add_card.py \
        --chapter "רבי עקיבא" \
        --title "הַגָּמָל" \
        --desc "משפט או שניים שמספרים במה הסיפור עוסק." \
        --link "פתיחת המצגת ↗|https://drive.google.com/..." \
        --link "📖 קריאת הסיפור ↗|https://yudataub.github.io/...#story-42"

--chapter מקבל שם פרק או עוגן (chapter-...). אם הדמות עדיין אין לה פרק,
השתמשו ב---new-chapter יחד עם --era ו---icon.
"""
import argparse, html, json, re, sys

CATALOG = 'tzadikim_catalog_with_52_learning_games.html'
ERAS = ['tanaim-a', 'tanaim-b', 'amoraim', 'mashal', 'extra']
PALETTE = ['#ff6b9d', '#4ec9f0', '#a29bfe', '#ffd93d', '#7bed9f', '#ff4757',
           '#00b894', '#ff9f43', '#5f27cd', '#ff6348']
DARK = {'#ff6b9d': '#c62b6b', '#4ec9f0': '#1a7fa0', '#a29bfe': '#5f4bb6',
        '#ffd93d': '#c99a00', '#7bed9f': '#2e9e5b', '#ff4757': '#a51824',
        '#00b894': '#006b56', '#ff9f43': '#c26a00', '#5f27cd': '#3a1580',
        '#ff6348': '#b32d17'}
TINT = {'#ff6b9d': '#ffe6f0', '#4ec9f0': '#e2f7ff', '#a29bfe': '#eeebff',
        '#ffd93d': '#fff8d6', '#7bed9f': '#e4fdec', '#ff4757': '#ffe6e8',
        '#00b894': '#d9f8f0', '#ff9f43': '#fff0dd', '#5f27cd': '#ece4ff',
        '#ff6348': '#ffe8e3'}


def plural(n):
    return 'סיפור אחד' if n == 1 else '%d סיפורים' % n


def strip_tags(t):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', t))).strip()


def fold(t):
    return re.sub(r'[^\w֐-׿]+', '', re.sub(r'[֑-ׇ]', '', strip_tags(t)))


def slug(name):
    return 'chapter-' + re.sub(r'[^\w֐-׿]+', '-', re.sub(r'[֑-ׇ]', '', name)).strip('-')


def find_chapter(doc, wanted):
    for m in re.finditer(r'<section class="chapter-section" id="([^"]+)">(.*?)\n</section>',
                         doc, re.S):
        title = re.search(r'<h2 class="chapter-title">(.*?)</h2>', m.group(2), re.S)
        if wanted == m.group(1) or fold(wanted) == fold(title.group(1)):
            return m.start(), m.end(), m.group(1), strip_tags(title.group(1))
    return None


def renumber_navigation(doc):
    order = re.findall(r'<article class="story-card[^"]*" id="(story-\d+)"', doc)
    pos = {sid: i for i, sid in enumerate(order)}

    def one(m):
        i = pos[m.group(2)]
        nav = ['<a class="back-to-toc-nav" href="#toc">📚 חזרה לתוכן העניינים</a>']
        if i > 0:
            nav.append('<a href="#%s">→ הקודם</a>' % order[i - 1])
        if i < len(order) - 1:
            nav.append('<a href="#%s">הבא ←</a>' % order[i + 1])
        return '%s<div class="story-navigation">%s</div>' % (m.group(1), ''.join(nav))

    return re.sub(r'(<article class="story-card[^"]*" id="(story-\d+)".*?)'
                  r'<div class="story-navigation">.*?</div>', one, doc, flags=re.S)


def refresh_counters(doc):
    """מוני הפרק, מוני הדור ומוני הכותרת — מחושבים מחדש מן המסמך עצמו."""
    def chapter(m):
        n = m.group(0).count('<article class="story-card')
        return re.sub(r'(<div class="chapter-subtitle">).*?(</div>)',
                      lambda x: x.group(1) + plural(n) + x.group(2), m.group(0), count=1)

    doc = re.sub(r'<section class="chapter-section" id="[^"]+">.*?\n</section>',
                 chapter, doc, flags=re.S)

    def toc_chapter(m):
        anchor = re.search(r'href="#(chapter-[^"]+)"', m.group(0))
        if not anchor:
            return m.group(0)
        sec = re.search(r'<section class="chapter-section" id="%s">.*?\n</section>'
                        % re.escape(anchor.group(1)), doc, re.S)
        n = sec.group(0).count('<article class="story-card') if sec else 0
        return re.sub(r'(<span class="toc-count">).*?(</span>)',
                      lambda x: x.group(1) + plural(n) + x.group(2), m.group(0), count=1)

    head, _, rest = doc.partition('</aside>')
    doc = re.sub(r'<div class="toc-chapter"[^>]*>.*?</ul>\n</div>', toc_chapter,
                 head, flags=re.S) + '</aside>' + rest

    # כותרות הדורות: פיצול על תג הפתיחה, כי בלוקי דור מכילים פרקים בתוכם
    prefix, sep, tail = doc.partition('<section class="era-block"')
    parts = (sep + tail).split('<section class="era-block"')
    for i, part in enumerate(parts):
        if not part.strip():
            continue
        stories = part.count('<article class="story-card')
        people = part.count('<section class="chapter-section"')
        key = re.match(r' id="([^"]+)"', part)
        if key:
            part = re.sub(r'(<div class="toc-era" id="toc-%s">.*?<span class="toc-era-count">)'
                          r'\d+(</span>)' % re.escape(key.group(1)),
                          lambda x: '%s%d%s' % (x.group(1), stories, x.group(2)),
                          part, flags=re.S)
        parts[i] = re.sub(
            r'(<div class="era-banner-sub">)(.*?)(</div>)',
            lambda x: '%s%s%s' % (
                x.group(1),
                ' · '.join([b for b in [x.group(2).split(' · ')[0].strip(), plural(stories),
                                        '%d דמויות' % people if people != 1 else 'דמות אחת'] if b]),
                x.group(3)), part, count=1)
    doc = prefix + '<section class="era-block"'.join(parts)

    # מוני הדור בסרגל יושבים מחוץ לבלוקי הדור, אז מעדכנים אותם בנפרד
    for key in ERAS:
        sec = re.search(r'<section class="era-block" id="%s">.*?\n</section>\n(?=<section class="era-block"|  </main>)'
                        % re.escape(key), doc, re.S)
        if not sec:
            continue
        n = sec.group(0).count('<article class="story-card')
        doc = re.sub(r'(<div class="toc-era" id="toc-%s">.*?<span class="toc-era-count">)\d+(</span>)'
                     % re.escape(key),
                     lambda x: '%s%d%s' % (x.group(1), n, x.group(2)), doc, flags=re.S)

    total = doc.count('<article class="story-card')
    people = doc.count('<section class="chapter-section"')
    doc = re.sub(r'(<div class="stat-bubble">📚 )\d+( סיפורים</div>)',
                 lambda m: '%s%d%s' % (m.group(1), total, m.group(2)), doc)
    doc = re.sub(r'(<div class="stat-bubble">👑 )\d+( דמויות</div>)',
                 lambda m: '%s%d%s' % (m.group(1), people, m.group(2)), doc)
    return doc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--chapter', required=True, help='שם הדמות או עוגן הפרק')
    ap.add_argument('--title', required=True)
    ap.add_argument('--desc', required=True, help='משפט או שניים על הסיפור')
    ap.add_argument('--who', default='', help='שם הדמות שעל הכרטיס (ברירת מחדל: שם הפרק)')
    ap.add_argument('--img', default='', help='כתובת תמונה (רשות)')
    ap.add_argument('--src-tag', default='', help='תגית מקור, למשל "🌐 Gamma"')
    ap.add_argument('--link', action='append', default=[],
                    metavar='"תווית|כתובת[|מחלקה]"',
                    help='קישור. אפשר לחזור על הדגל. מחלקות: game-link, study-link, adult-story-link')
    ap.add_argument('--adult', action='store_true', help='סמן כסיפור למבוגרים')
    ap.add_argument('--new-chapter', action='store_true', help='פתח פרק חדש לדמות')
    ap.add_argument('--era', choices=ERAS, help='הדור, נדרש עם --new-chapter')
    ap.add_argument('--icon', default='📜', help='אימוג׳י לפרק חדש')
    ap.add_argument('--catalog', default=CATALOG)
    a = ap.parse_args()

    doc = open(a.catalog, encoding='utf-8').read()
    found = find_chapter(doc, a.chapter)

    if found and a.new_chapter:
        sys.exit('הפרק %r כבר קיים — הסירו את --new-chapter.' % a.chapter)
    if not found and not a.new_chapter:
        sys.exit('לא נמצא פרק %r. הריצו check_catalog.py --list, או הוסיפו '
                 '--new-chapter --era <דור>.' % a.chapter)
    if a.new_chapter and not a.era:
        sys.exit('--new-chapter דורש גם --era (%s).' % ', '.join(ERAS))

    new_id = 'story-%d' % (max(int(s) for s in re.findall(r'id="story-(\d+)"', doc)) + 1)

    if a.new_chapter:
        # צבע חדש לפי מספר הפרקים הקיימים, כדי שלא ייצא צבע זהה לשכן
        colour = PALETTE[doc.count('<section class="chapter-section"') % len(PALETTE)]
        anchor, chapter_name = slug(a.chapter), a.chapter
        header = ('<section class="chapter-section" id="%s">\n'
                  '<div class="chapter-header" style="background:linear-gradient(135deg,%s,%s)">'
                  '<div class="chapter-icon">%s</div><div>'
                  '<h2 class="chapter-title">%s</h2>'
                  '<div class="chapter-subtitle">סיפור אחד</div></div></div>\n'
                  '<div class="card-grid">\n'
                  % (anchor, colour, DARK[colour], a.icon, html.escape(chapter_name)))
    else:
        start, end, anchor, chapter_name = found
        sib = re.search(r'<article class="story-card[^"]*" id="story-\d+" '
                        r'style="border-top:6px solid (#[0-9a-fA-F]{6})">.*?'
                        r'<div class="story-header" style="background:(#[0-9a-fA-F]{6})">',
                        doc[start:end], re.S)
        if not sib:
            sys.exit('לא הצלחתי לקרוא את צבעי הפרק %r.' % chapter_name)
        colour, tint = sib.group(1), sib.group(2)

    if a.new_chapter:
        tint = TINT[colour]

    links = []
    for spec in a.link:
        bits = spec.split('|')
        if len(bits) < 2:
            sys.exit('קישור לא תקין: %r. הפורמט הוא "תווית|כתובת[|מחלקה]".' % spec)
        label, url, cls = bits[0], bits[1], (bits[2] if len(bits) > 2 else '')
        links.append('<a %shref="%s" target="_blank" rel="noopener">%s</a>'
                     % ('class="%s" ' % cls if cls else '', html.escape(url, quote=True), label))

    card = ('<article class="story-card%s" id="%s" style="border-top:6px solid %s"%s>\n'
            % (' adult-story' if a.adult else '', new_id, colour,
               ' data-audience="adults"' if a.adult else ''))
    if a.img:
        card += ('<img class="card-img" src="%s" alt="%s" loading="lazy" decoding="async">\n'
                 % (html.escape(a.img, quote=True), html.escape(a.title, quote=True)))
    card += '<div class="story-header" style="background:%s">\n' % tint
    card += '<span class="story-num" style="background:%s">#%s</span>\n' % (colour, new_id.split('-')[1])
    if a.src_tag:
        card += '<span class="src-tag">%s</span>\n' % a.src_tag
    if a.adult:
        card += ('<span class="adult-story-tag" title="סיפור המיועד לקהל מבוגר">'
                 '🧑‍🎓 סיפור למבוגרים</span>\n')
    card += ('<button class="copy-story-link" onclick="copyStoryLink(\'%s\', this)">'
             '🔗 העתק קישור</button>\n</div>\n' % new_id)
    card += ('<div class="story-body">\n<span class="who">%s</span>\n'
             '<h3 class="story-title">%s</h3>\n<p class="story-desc">%s</p>\n'
             '<div class="story-links">%s</div>\n</div>\n'
             % (html.escape(a.who or chapter_name), a.title, a.desc, ' '.join(links)))
    card += '<div class="story-navigation"></div>\n</article>\n'

    if a.new_chapter:
        # An era block ends with the last "</section>" before the next era opens —
        # a non-greedy match stops at the first *chapter's* closer instead, which
        # silently nests the new chapter inside its neighbour.
        at = doc.index('<section class="era-block" id="%s">' % a.era)
        nxt = doc.find('<section class="era-block"', at + 1)
        if nxt < 0:
            nxt = doc.index('  </main>')
        era_end = doc.rindex('\n</section>', at, nxt)
        doc = doc[:era_end] + '\n' + header + card + '</div>\n</section>' + doc[era_end:]
        toc_item = ('<div class="toc-chapter" style="border-color:%s">\n'
                    '<div class="toc-chapter-title" style="background:%s" onclick="toggleTocChapter(this)">'
                    '<span class="toc-icon">%s</span>'
                    '<a href="#%s" class="toc-sage-link">%s</a>'
                    '<span class="toc-count">סיפור אחד</span><span class="toc-arrow">▼</span></div>\n'
                    '<ul class="toc-stories">\n'
                    '<li><a href="#%s">%s</a><button class="toc-copy-link" '
                    'onclick="event.preventDefault(); copyStoryLink(\'%s\', this)" '
                    'title="העתק קישור">🔗</button></li>\n</ul>\n</div>\n'
                    % (colour, colour, a.icon, anchor, html.escape(chapter_name),
                       new_id, a.title, new_id))
        # הפריט נכנס בסוף רשימת הפרקים של אותו דור בסרגל
        nxt = ERAS.index(a.era) + 1
        marker = ('<div class="toc-era" id="toc-%s">' % ERAS[nxt]) if nxt < len(ERAS) else '</aside>'
        at = doc.index(marker)
        doc = doc[:at] + toc_item + doc[at:]
    else:
        grid_end = doc.rindex('</div>\n</section>', start, end)
        doc = doc[:grid_end] + card + doc[grid_end:]

        def toc_block(m):
            if 'href="#%s"' % anchor not in m.group(0):
                return m.group(0)
            item = ('<li><a href="#%s">%s</a><button class="toc-copy-link" '
                    'onclick="event.preventDefault(); copyStoryLink(\'%s\', this)" '
                    'title="העתק קישור">🔗</button></li>\n' % (new_id, a.title, new_id))
            return m.group(0).replace('</ul>', item + '</ul>', 1)

        doc = re.sub(r'<div class="toc-chapter"[^>]*>.*?</ul>\n</div>', toc_block, doc, flags=re.S)

    doc = refresh_counters(doc)
    doc = renumber_navigation(doc)

    m = re.search(r'const searchData = (\[.*?\]);\n', doc, re.S)
    data = json.loads(m.group(1))
    data.append({'id': new_id, 'title': strip_tags(a.title),
                 'body': ((a.who or chapter_name) + ' — ' + strip_tags(a.desc))[:600]})
    rank = {sid: i for i, sid in
            enumerate(re.findall(r'<article class="story-card[^"]*" id="(story-\d+)"', doc))}
    data.sort(key=lambda d: rank.get(d['id'], 10 ** 6))
    doc = doc[:m.start(1)] + json.dumps(data, ensure_ascii=False) + doc[m.end(1):]

    open(a.catalog, 'w', encoding='utf-8').write(doc)
    print('נוסף %s לפרק "%s".' % (new_id, chapter_name))
    print('הריצו עכשיו:  python3 scripts/check_catalog.py')


if __name__ == '__main__':
    main()
