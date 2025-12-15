# NOC AI Agent – Ultra Slim + Policy + Memory

גרסה **רזה מאוד** של סוכן NOC, עם שתי תוספות קריטיות בלבד:
- **Policy** – שליטה מתי *אסור* להריץ אוטומציה
- **Memory (TTL)** – מניעת לופים / flapping

עדיין:
- ❌ אין MCP
- ❌ אין Normalize
- ❌ אין UI
- ❌ אין ריבוי סוכנים

---

## מודל עבודה

**קיבלתי → בדקתי → החלטתי → פוליסי → טיפלתי → זכרתי → סגרתי**

---

## מבנה הפרויקט

```
noc_agent/
├── app.py
├── decision.py
├── tools.py
├── guardrails.py
├── policy.py          # חוקים תפעוליים
├── memory.py          # זיכרון קצר (TTL)
├── models.py
├── logging_utils.py
└── examples/
    └── run_demo.py
```

---

## Policy – למה זה חשוב?

פוליסי מאפשר להגיד:
- "בלילה לא מבצעים restart"
- "לשירות X אין autorun"
- "Critical תמיד escalate"

בלי לגעת ב-LLM.

---

## Memory – למה זה חשוב?

מונע מצבים כמו:
- restart → עולה → נופל → restart → לופ
- אותה פעולה רצה 5 פעמים בדקה

הזיכרון **לא חכם** – הוא פשוט, עם TTL.

---

## מתי Autorun?

רק אם **הכול** מתקיים:
- LLM המליץ `run_action`
- confidence ≥ 0.75
- risk = low
- Policy מאשרת
- Memory מאשרת (לא בוצע לאחרונה)

---

## הערה חשובה

ה-LLM:
- לא זוכר
- לא יודע חוקים
- לא יודע זמן

המערכת:
- כן.

זה ההבדל בין צעצוע לפרודקשן.
