#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""מוסיף סיפור אחד לספר "גדולי ישראל לדורותיהם".

הספר מחזיק שישה דברים שחייבים להסכים זה עם זה — מזהי הסיפורים, תוכן
העניינים בסרגל, מוני הסיפורים בפרק ובדור, שרשרת הקודם/הבא, ומדד החיפוש.
עריכה ידנית היא בדיוק המקום שבו הם נפרדים בשקט, ולכן ההוספה נעשית כאן.

    python3 scripts/add_story.py \
        --chapter "ר' יהושע בן לוי" \
        --title "מֵעַל חוֹמוֹת גַּן עֵדֶן" \
        --subtitle "בַּעֲלֵי רָאתָן וְהַסַּכִּין" \
        --body story.html

--chapter מקבל שם פרק, עוגן (chapter-...) או מזהה ישן (ch-1-23).
--body הוא קובץ HTML עם גוף הסיפור בלבד (בלי article/header).
"""
import argparse, html, json, re, sys

BOOK = 'גדולי ישראל לדורותיהם.html'


def plural(n):
    return 'סיפור אחד' if n == 1 else '%d סיפורים' % n


def strip_tags(t):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', t))).strip()


def fold(t):
    """שם פרק בלי ניקוד וסימני פיסוק, להשוואה סלחנית."""
    return re.sub(r'[^\w֐-׿]+', '', re.sub(r'[֑-ׇ]', '', strip_tags(t)))


def find_chapter(doc, wanted):
    """מחזיר (start, end) של ה-section של הפרק המבוקש."""
    for m in re.finditer(r'<section class="chapter-section" id="([^"]+)">(.*?)\n</section>',
                         doc, re.S):
        anchor, inner = m.group(1), m.group(2)
        legacy = re.search(r'<span class="legacy-anchor" id="([^"]+)">', inner)
        title = re.search(r'<h2 class="chapter-title">(.*?)</h2>', inner, re.S)
        names = {anchor, legacy.group(1) if legacy else '', fold(title.group(1))}
        if wanted in names or fold(wanted) in names:
            return m.start(), m.end(), anchor, strip_tags(title.group(1))
    sys.exit('לא נמצא פרק בשם %r. הריצו check_book.py --list כדי לראות את הפרקים.' % wanted)


def renumber_navigation(doc):
    """בונה מחדש את שרשרת הקודם/הבא לפי סדר הסיפורים במסמך."""
    order = re.findall(r'<article class="story-card" id="(story-\d+)"', doc)
    pos = {sid: i for i, sid in enumerate(order)}

    def one(m):
        i = pos[m.group(2)]
        nav = ['<a class="back-to-toc-nav" href="#toc">📚 חזרה לתוכן העניינים</a>']
        if i > 0:
            nav.append('<a href="#%s">→ הסיפור הקודם</a>' % order[i - 1])
        if i < len(order) - 1:
            nav.append('<a href="#%s">הסיפור הבא ←</a>' % order[i + 1])
        # group 1 already holds the whole card up to its navigation strip;
        # re-emit it untouched and replace only the strip.
        return '%s<div class="story-navigation">%s</div>' % (m.group(1), ''.join(nav))

    return re.sub(r'(<article class="story-card" id="(story-\d+)".*?)'
                  r'<div class="story-navigation">.*?</div>',
                  one, doc, flags=re.S)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--chapter', required=True)
    ap.add_argument('--title', required=True)
    ap.add_argument('--subtitle', default='')
    ap.add_argument('--body', required=True, help='קובץ HTML עם גוף הסיפור')
    ap.add_argument('--book', default=BOOK)
    a = ap.parse_args()

    doc = open(a.book, encoding='utf-8').read()
    body = open(a.body, encoding='utf-8').read().strip()

    start, end, anchor, chapter_name = find_chapter(doc, a.chapter)
    section = doc[start:end]

    # מספר חדש בהמשך לקיימים. אף מזהה קיים לא זז: מספר סיפור הוא הבטחה,
    # מישהו כבר החזיק קישור אליו בהודעה.
    new_id = 'story-%d' % (max(int(s) for s in
                               re.findall(r'id="story-(\d+)"', doc)) + 1)

    sibling = re.search(r'<article class="story-card" id="story-\d+" '
                        r'style="border-top:6px solid (#[0-9a-fA-F]{6})">\s*'
                        r'<div class="story-header" style="background:(#[0-9a-fA-F]{6})">',
                        section)
    if sibling:
        colour, tint = sibling.group(1), sibling.group(2)
    else:
        # פרק חדש שנפתח עם reorg.py --create, עדיין בלי אף סיפור: אין
        # כרטיס-אח לקרוא ממנו צבעים, אז נגזור אותם מכותרת הפרק עצמה —
        # הצבע החי מהגרדיאנט, וגוון בהיר שלו לרקע כותרת הסיפור.
        header = re.search(r'<div class="chapter-header" '
                           r'style="background:linear-gradient\(135deg,(#[0-9a-fA-F]{6}),',
                           section)
        if not header:
            sys.exit('לא הצלחתי לקרוא את צבעי הפרק %r.' % chapter_name)
        colour = header.group(1)
        r, g, b = (int(colour[i:i + 2], 16) for i in (1, 3, 5))
        blend = lambda c: round(c + (255 - c) * 0.88)
        tint = '#%02x%02x%02x' % (blend(r), blend(g), blend(b))

    card = (
        '<article class="story-card" id="{id}" style="border-top:6px solid {c}">\n'
        '<div class="story-header" style="background:{t}">\n'
        '<span class="story-num" style="background:{c}">#{n}</span>\n'
        '<h3 class="story-title">{title}</h3>\n'
        '<button class="copy-story-link" onclick="copyStoryLink(\'{id}\', this)">'
        '🔗 העתק קישור</button>\n'
        '</div>\n{sub}<div class="story-body">{body}</div>\n'
        '<div class="story-navigation"></div>\n'
        '</article>\n'
    ).format(id=new_id, c=colour, t=tint, n=new_id.split('-')[1],
             title=a.title, body=body,
             sub=('<div class="story-subtitle">%s</div>\n' % a.subtitle) if a.subtitle else '')

    section = section[:section.rindex('\n</section>')] + '\n' + card + '</section>'
    count = section.count('<article class="story-card"')
    section = re.sub(r'(<div class="chapter-subtitle">).*?(</div>)',
                     lambda m: m.group(1) + plural(count) + m.group(2), section, count=1)
    doc = doc[:start] + section + doc[end:]

    # תוכן העניינים: פריט חדש ומונה מעודכן, באותו בלוק פרק
    def toc_block(m):
        block = m.group(0)
        if 'href="#%s"' % anchor not in block:
            return block
        item = ('<li><a href="#{id}">{title}</a>'
                '<button class="toc-copy-link" onclick="event.preventDefault(); '
                'copyStoryLink(\'{id}\', this)" title="העתק קישור">🔗</button></li>\n'
                ).format(id=new_id, title=a.title)
        block = block.replace('</ul>', item + '</ul>', 1)
        return re.sub(r'(<span class="toc-count">).*?(</span>)',
                      lambda x: x.group(1) + plural(count) + x.group(2), block, count=1)

    doc = re.sub(r'<div class="toc-chapter"[^>]*>.*?</ul>\n</div>', toc_block, doc, flags=re.S)

    # מוני הדור בכותרת הדור, ומוני הכותרת הראשית
    # Era blocks nest chapter sections inside them, so a regex for "one block"
    # is easy to get subtly wrong. Split on the opening tag instead.
    head, sep, rest = doc.partition('<section class="era-block"')
    parts = (sep + rest).split('<section class="era-block"')
    era_stories = {}  # era id -> story count, for the sidebar counter pass below
    for i, part in enumerate(parts):
        if not part.strip():
            continue
        stories = part.count('<article class="story-card"')
        people = part.count('<section class="chapter-section"')
        era_id = re.match(r'\s*id="([^"]+)"', part)
        if era_id:
            era_stories[era_id.group(1)] = stories

        def counters(x):
            # keep whatever description the era already carries, and drop the
            # separator entirely when there is none — otherwise the line opens
            # with a stray "·".
            desc = x.group(2).split(' · ')[0].strip()
            bits = ([desc] if desc else []) + [
                plural(stories),
                '%d דמויות' % people if people != 1 else 'דמות אחת']
            return x.group(1) + ' · '.join(bits) + x.group(3)

        parts[i] = re.sub(r'(<div class="era-banner-sub">)(.*?)(</div>)',
                          counters, part, count=1)
    doc = head + '<section class="era-block"'.join(parts)

    # אותו מספר מופיע גם במונה הסרגל הצדדי, בלוק נפרד לגמרי מבאנר הדור —
    # שני מקומות שחייבים להסכים, וזו בדיוק הדריפט שהתגלה בעבר.
    for era_id, stories in era_stories.items():
        doc = re.sub(r'(id="toc-%s"[^>]*><span>.*?</span><span class="toc-era-count">)\d+(</span>)'
                     % re.escape(era_id), r'\g<1>%d\2' % stories, doc, count=1)

    total = doc.count('<article class="story-card"')
    chapters = doc.count('<section class="chapter-section"')
    doc = re.sub(r'(<div class="stat-bubble">📚 )\d+( סיפורים</div>)',
                 lambda m: '%s%d%s' % (m.group(1), total, m.group(2)), doc)
    doc = re.sub(r'(<div class="stat-bubble">👑 )\d+( דמויות ופרקים</div>)',
                 lambda m: '%s%d%s' % (m.group(1), chapters, m.group(2)), doc)

    doc = renumber_navigation(doc)

    # מדד החיפוש. הסיפורים מנוקדים ואיש אינו מקליד ניקוד, ולכן החיפוש עצמו
    # משווה טקסט מקופל — כאן די בכך שהערך יהיה במקומו ובסדר הקריאה.
    m = re.search(r'const searchData = (\[.*?\]);\n', doc, re.S)
    data = json.loads(m.group(1))
    entry = {'id': new_id,
             'title': strip_tags(a.title + (' — ' + a.subtitle if a.subtitle else '')),
             'body': (chapter_name + ' — ' + strip_tags(body))[:1200]}
    order = re.findall(r'<article class="story-card" id="(story-\d+)"', doc)
    rank = {sid: i for i, sid in enumerate(order)}
    data.append(entry)
    data.sort(key=lambda d: rank.get(d['id'], 10 ** 6))
    doc = doc[:m.start(1)] + json.dumps(data, ensure_ascii=False) + doc[m.end(1):]

    open(a.book, 'w', encoding='utf-8').write(doc)
    print('נוסף %s לפרק "%s" (%s בפרק, %d בספר).' % (new_id, chapter_name, plural(count), total))
    print('הריצו עכשיו:  python3 scripts/check_book.py')


if __name__ == '__main__':
    main()
