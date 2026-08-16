---
name: gamma-torah-presentation
description: >
  Use this skill when the user wants to create a Gamma AI presentation for a Torah lesson,
  Bible story, or Jewish values lesson for religious boys aged 6-12.
  Triggers: "צור מצגת גמה", "מצגת לשיעור על", "הכן מצגת תורנית", "create gamma presentation",
  "תבנה לי ישר בגמה". This skill generates complete slide-by-slide content: the full source
  story with sources for the teacher, Hebrew text, ready-to-paste AI image prompts for Gamma,
  teacher instructions, discussion questions, and follow-up activity — and can optionally build
  the presentation directly inside Gamma via the Gamma MCP tools.
allowed-tools: "Read, mcp__Gamma__generate, mcp__Gamma__generate_from_template, mcp__Gamma__generate_multi_page_gamma, mcp__Gamma__get_themes, mcp__Gamma__get_generation_status, mcp__Gamma__export_gamma, mcp__Gamma__get_export_status"
---

# יצירת מצגת תורנית ב-Gamma — לבנים בגילאי 6-12

## Overview
בונה מצגות תורניות ישירות בגמה (Gamma AI) באמצעות ה-MCP, ובמידת הצורך גם מייצר גרסת
טקסט + פרומפטים מוכנה להעתקה-הדבקה ידנית. כל מצגת: הסיפור המלא + מקורות למורה, טקסט עברי
מוכן לשקופיות, פרומפטים לתמונות, והוראות מלאות למורה.

---

## ⛔ כלל ברזל — דיוק פסוקים (קרא לפני הכל!)

**זהו הכלל הקריטי ביותר בכל המערכת. אין יוצא מהכלל.**

### האיסור המוחלט:
- **אסור להקליד פסוק מהזיכרון** — אפילו פסוק מוכר מאוד
- **אסור לקצר פסוק** — גם אם הוא ארוך
- **אסור להשמיט מילה אחת** — כל מילה בתורה קדושה
- **אסור להגיש מצגת** לפני ביצוע צ'קליסט הבדיקה

### חובת המקור:
כל פסוק חייב להיות מועתק **מילה במילה** מהטקסט שסיפק המשתמש בשיחה, או ממקור מקוונן מהימן
שאותרם ואומת (ראה Step 2 להלן). אם אין מקור זמין וודאי — **בקש אותו לפני שממשיכים.**

---

## Step 0: שאלות פתיחה חובה

**לפני כל דבר**, שאל את המשתמש את השאלות האלו (בבת אחת):

```
לפני שאתחיל, אני צריך כמה פרטים:

1. 📖 מה נושא/סיפור השיעור? (לדוגמה: "דוד וגולית", "הצלת פורים", "קריאת שמע")
2. 👦 גיל מדויק: 6-8 / 9-12?
3. 📊 כמה שקופיות? (מומלץ 12-15 לשיעור 45 דקות)
4. 🎭 האם יש בסיפור: קרב/עימות? ניסים? מנהיגות? (קובע את הסגנון הויזואלי)
5. 🛠️ איך תרצה לקבל את התוצאה? (א) שאבנה את המצגת ישירות בגמה עבורך (ברירת מחדל),
   או (ב) טקסט + פרומפטים להעתקה-הדבקה ידנית בגמה?
```

---

## Step 0.5: בדיקת ריבוי סיפורים ⚠️ חובה לבדוק

**לפני שממשיכים לבנייה**, בדוק אם הנושא שהמשתמש ביקש בעצם מכיל **שני סיפורים נפרדים** או
יותר (למשל: "מכירת יוסף ומפגש עם פרעה", "יציאת מצרים ומתן תורה", "חנוכה — המרד והנס").

**אם זוהו שני סיפורים נפרדים:**
- עצור לפני שמתחילים לבנות
- הצע למשתמש לפצל לשתי מצגות נפרדות, עם הסבר קצר: כל סיפור ראוי למצגת מלאה של 45 דקות,
  ושילוב שניהם יגרום לדילוג על פרטים חשובים ולמצגת עמוסה מדי
- המתן לאישור/הכרעה של המשתמש (מצגת אחת מצומצמת / שתי מצגות נפרדות) לפני שממשיכים

אם מדובר בסיפור אחד רציף (גם אם ארוך) — המשך כרגיל.

---

## Step 1: בחירת סגנון אמנותי

על בסיס תשובה לשאלה 4, בחר:

| תשובה | סגנון |
|-------|-------|
| קרב, עימות, גבורה | `epic biblical illustration` |
| ניסים, קסם, אלוקות | `dynamic adventure book style` |
| מנהיגות, חכמה, ערכים | `biblical children's book illustration` |

**כתוב למורה בתחילת המצגת:**
```
🎨 סגנון מומלץ למצגת זו: [הסגנון שנבחר]
📋 הנחיה: כנס ל-Theme Editor בגמה ← הזן את הסגנון פעם אחת בלבד
```
(שלב זה רלוונטי במסלול העתקה-הדבקה; במסלול בנייה ישירה — ראה Step 7.)

---

## Step 2: כתיבת הסיפור המלא למורה + אימות מקורות ⚠️ חובה, לפני בניית השקופיות

המורה לא תמיד מכיר את הסיפור לעומק — לכן **לפני** שבונים שקופיות, יש לכתוב את הסיפור השלם.

1. **כתוב את הסיפור המלא** ברצף כרונולוגי, כטקסט רציף (לא כשקופיות) — כולל כל הפרטים
   הרלוונטיים, גם אלו שלא ייכנסו לשקופיות עצמן.
2. **וודא נאמנות למקורות** ככל האפשר: היצמד לפסוקים, למדרשים ולמקורות חז"ל מוכרים ומהימנים.
   אל תמציא פרטים, אל תשלב אגדות עממיות שאינן מבוססות, ואל תערבב גרסאות סותרות בלי לציין זאת.
   אם יש מחלוקת בין מפרשים/מדרשים — ציין זאת בקצרה ובחר את הגרסה הרווחת והמתאימה לגיל.
3. **בסוף הסיפור המלא**, הוסף סעיף "מקורות" עם רשימת המקורות עליהם מבוסס הסיפור
   (פסוקים, מסכתות, מדרשים) — עם ציטוט מלא ומדויק היכן שניתן.
4. רק **לאחר** שלב זה עוברים לבניית השקופיות (Step 5), שבהן ייכתב רק חלק מהסיפור —
   הגרסה המקוצרת, המתאימה לגיל ולזמן השיעור.

**פורמט להצגה למשתמש:**
```
## 📖 הסיפור המלא (לידיעת המורה)

[טקסט רציף מלא של הסיפור, נאמן למקורות, כולל כל השלבים המרכזיים]

## 📚 מקורות
- [מקור 1, למשל: שמואל א׳ פרק יז]: "[ציטוט מדויק ומלא ככל האפשר]"
- [מקור 2, למשל: מדרש/גמרא רלוונטי]: "[ציטוט מדויק]"
```

---

## Step 3: בניית DNA לדמויות

קרא קודם: `references/character-dna.md`

**עבור כל דמות מרכזית בסיפור:**
- אם הדמות קיימת ב-character-dna.md — השתמש ב-DNA המוכן
- אם הדמות לא קיימת — צור DNA חדש לפי הפורמט:

```
[שם] DNA: [גיל ומין] Hebrew [תפקיד], [גיל מספרי] years old,
[תיאור עיניים], [תיאור שיער/זקן], [תיאור בגד מלא - tunic, belt, sandals],
[פריט אופייני - staff/sword/scroll], [תנוחה], kippah
```

**חשוב:** שמור את ה-DNA שיצרת — הוא יחזור מילה במילה בכל פרומפט.

---

## Step 4: הוראות מלאות למורה (במסלול העתקה-הדבקה)

קרא: `references/teacher-instructions.md` והצג בדיוק כפי שמופיע שם.

---

## Step 5: יצירת השקופיות

קרא תבנית: `assets/slide-template.md`

### מבנה חובה של כל מצגת:
- **שקופית 1:** כותרת + שאלת פתיחה מסקרנת
- **שקופיות 2-3:** הקשר/רקע לסיפור
- **שקופיות 4-11:** לב הסיפור (אירועים עיקריים)
- **שקופית 12-13:** שיא + פתרון
- **שקופית 14:** מסר ערכי מרכזי
- **שקופית 15:** סיכום + שאלה לבית

### כלל ברזל — גוון את זווית הצילום:
לעולם אל תכתוב שתי שקופיות עוקבות עם אותה זווית צילום.
סדר מומלץ: wide shot ← medium shot ← close-up ← wide shot...

### כלל ברזל — פסוקים:
- **העתק בלבד** מהמקור שאומת ב-Step 2 — אל תקליד מהזיכרון
- **פסוק שלם** — עד הסיום (׃) בלי השמטות
- **אם פסוק ארוך** — פצל לשתי שקופיות, אל תקצר

---

## Step 6: צ'קליסט בדיקה לפני הגשה ⛔ חובה!

**לפני שמגישים את המצגת — עבור על כל שקופית לפי הסדר:**

```
✅ צ'קליסט בדיקת פסוקים — חובה לפני הגשה:

עבור כל שקופית שמכילה פסוק:
□ פתחתי את טקסט המקור שאומת ב-Step 2
□ השוויתי מילה במילה בין הפסוק שכתבתי לבין המקור
□ וידאתי שהפסוק שלם עד הסיום (׃)
□ לא הסתמכתי על זיכרון — העתקתי מהמקור בלבד

⛔ המצגת לא מוגשת לפני שכל הריבועים מסומנים!
```

**שגיאות נפוצות לבדוק במיוחד:**
- פסוק שנחתך באמצע (הכי שכיח!)
- מילת קישור שנשמטה (וְ / אֶת / אֲשֶׁר)
- סיום פסוק חסר (׃)
- שני פסוקים שמוצגים כאחד

---

## Step 7: בנייה ישירה בגמה (Direct Build) — ברירת מחדל, אלא אם המשתמש ביקש אחרת ב-Step 0

אם המשתמש לא ביקש במפורש את מסלול העתקה-הדבקה הידני (ראה Step 4), בנה את המצגת ישירות בגמה:

0. ⛔ **ניקוד — חובה בכל שקופית.** כל הטקסט העברי שנשלח ב-`inputText` (כותרות ותוכן) חייב
   להיות **מנוקד במלואו**, בדיוק כפי שהמורה מצפה שהילדים יקראו. בנוסף, יש להוסיף ל-
   `additionalInstructions` שורה מפורשת כמו: *"Keep all Hebrew text exactly as provided,
   including full niqqud (vowel points) on every word. Do not strip or regenerate the Hebrew
   text — preserve the nikud character-for-character."* — אחרת גמה עלולה להשמיט את הניקוד
   או לשכתב את הטקסט בלעדיו. זו הייתה תקלה אמיתית בעבר — אל תחזור עליה.
1. השתמש ב-`mcp__Gamma__generate` (או `mcp__Gamma__generate_from_template` אם קיימת תבנית
   מתאימה מוגדרת מראש) כדי לבנות את המצגת מכל התוכן שנוצר בשלבים הקודמים — כותרות, טקסט
   עברי לכל שקופית, ופרומפטים לתמונות.
2. ⛔ **`imageOptions.stylePreset` חייב להיות `"custom"`** — ורק אז `imageOptions.style` נקרא.
   אם מעבירים preset בעל שם (`illustration`, `photorealistic` וכו') — גמה **מתעלמת לחלוטין**
   מ-`style` וזורקת את כל תיאור הסגנון. זו הייתה תקלה אמיתית בעבר.
3. **הסגנון המומלץ כברירת מחדל** — ציור ריאליסטי-פיינטרלי עשיר (לא וקטור שטוח / קריקטורה):
   ```
   stylePreset: "custom"
   model: "flux-2-klein"   (ברירת מחדל — זול ואיכותי, ~5 קרדיטים לשקופית / ~15 ל-3 שקופיות,
                             נבדק ואושר על ידי המשתמש כתוצאה מעולה)
   style: "Richly rendered near-photorealistic painterly digital artwork in the style of a
   premium illustrated biblical storybook. Highly detailed lifelike human faces with real skin
   texture, expressive eyes, individual beard and hair strands. Realistic woven wool and linen
   fabric with visible weave and natural folds. Warm cinematic golden-hour lighting with soft
   god rays, atmospheric haze and gentle depth of field. Ancient Judean landscape: olive groves,
   terraced stone hillsides, wildflowers, dusty paths. Deep saturated natural earth tones.
   Painterly brushwork over photoreal detail, luminous and reverent, no flat vector shapes,
   no cartoon simplification, no line art. Modest full-length biblical clothing covering arms
   and ankles, head coverings and kippot for all men, married women with hair modestly covered,
   no exposed skin, dignified expressions, family-friendly and appropriate for children."
   ```
   חלופות באיכות גבוהה יותר (יקרות משמעותית): `gemini-3-pro-image` (~1000 קרדיטים למצגת),
   `gemini-3.1-flash-image`, `flux-2-pro`.
4. **בדוק תמיד את שדה ה-`warnings` בתשובת `generate`** — אם גמה מדווחת שפרמטר כלשהו
   הוזנח (ignored), עצור, תקן את הקריאה והרץ מחדש. אל תמשיך הלאה עם אזהרה פתוחה.
5. אם ב-workspace של המשתמש שמורה הוראה שמכריחה סגנון איור לדמויות אדם
   (`IMAGE STYLE REQUIREMENT ... photorealistic images of humans are NOT allowed`) — היא
   תדרוס את בקשת הריאליזם. נטרל אותה דרך `additionalInstructions`, והודע למשתמש לבדוק
   את Gamma → Settings → Custom Instructions.
6. עקוב אחר הסטטוס עם `mcp__Gamma__get_generation_status` עד לסיום.
7. בסיום, מסור למשתמש קישור ישיר למצגת שנוצרה בגמה, וציין כמה קרדיטים נוצלו.
8. **הזכר למשתמש במפורש**: גם בבנייה ישירה, יש לעבור על כל תמונה שנוצרה ולוודא צניעות לפני
   השימוש בפועל בכיתה — לא לסמוך אוטומטית על הפלט.

אם המשתמש מבקש במפורש טקסט + פרומפטים להעתקה-הדבקה הידנית — עבור למסלול הקיים (Step 4-6),
שנותן למורה שליטה מלאה ובדיקה ידנית של כל תמונה לפני שהיא נכנסת למצגת.

---

## Step 8: סיום מקצועי

קרא: `references/closing-template.md` והצג בסוף כל מצגת.

---

## דוגמת פלט מלאה — שקופית לדוגמה

להלן שקופית מוגמרת לחלוטין לסיפור "דוד וגולית". **זהו הפורמט המדויק לכל שקופית:**

---

#### **שקופית 6: הצעד הנועז**

**טקסט לשקופית (עברית):**
דוד לא פחד. הוא ידע שה' עמו.
"אני בא אליך בשם ה'!" קרא בקול.
האמונה שלו הייתה חזקה מכל חרב.

**פרומפט AI למחולל Gamma (מוכן לשימוש):**
Young David DNA: teenage Hebrew shepherd boy, 15-16 years old, bright determined eyes, curly brown hair, simple beige wool tunic with rope belt, brown leather sandals, wooden sling held ready in right hand, small kippah, fearless confident posture — running forward on dry golden hillside, ancient Judean valley battlefield setting, afternoon golden light casting long shadows, low angle shot looking up at David making him appear heroic, distant Philistine army blurred in background, dramatic dust clouds, epic biblical illustration style, modest biblical clothing fully covered, no exposed skin, warm earth tones, family-friendly

**הגדרות Gamma:**
מקור: AI Generated | איכות: High Quality

**אנימציה מומלצת:** zoom-in (מדגיש את הנחישות)

---

## עקרונות שחייבים להופיע בכל פרומפט

קרא: `references/style-guide.md` — חובה לפני כתיבת כל פרומפט.

הכלל הכי חשוב: **טקסט עברי לקריאה תמיד בתיבת הטקסט של השקופית, לא בפרומפט התמונה** —
טקסט דקורטיבי בתמונה (על מגילה/שלט) מותר בזהירות, ראה `references/style-guide.md`.
