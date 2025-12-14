# mcp-agent-slim — Agent NOC רזה עם LLM + Playbook + Diagnostics

הפרויקט הזה הוא גרסה **פשוטה מאוד** של “איש NOC אוטומטי”:

- מקבל **Alert** (קובץ JSON)
- ה‑**LLM מחליט** מה לעשות (כמו בגרסה הראשונה שלך)
- שכבת **Playbook רזה** חוסמת רק מקרים בעייתיים (Guardrail עדין)
- שכבת **Diagnostics רזה** מתעדת “מה קרה ולמה” עם `trace_id`

## למה זה עדין ורזה?
- אין מנוע פלייבוקים כבד
- אין DB / שירותים נוספים
- אין Web UI
- אין “workflow engine”
- רק שתי תוספות שמעלות אמינות ושקיפות

---

## התקנה

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

הגדרת מפתח API:

```bash
export OPENAI_API_KEY="..."
```

אופציונלי: לבחור מודל

```bash
export OPENAI_MODEL="gpt-4o-mini"
```

אופציונלי: לשמור דיאגנוסטיקה לקובץ JSONL

```bash
export DIAGNOSTICS_JSONL="./data/diagnostics.jsonl"
```

---

## הרצה

```bash
python main.py examples/alert_cpu.json
```

או התראת דיסק:

```bash
python main.py examples/alert_disk.json
```

הפלט הוא אובייקט JSON של הדיאגנוסטיקה, כולל `trace_id`, צעדים, ושגיאות אם היו.

---

## איך Playbook עובד פה?

`agent/playbook.py` כולל מילון פשוט:

- אם `alert.metric == "cpu"` → מותר `restart_service`
- אם `alert.metric == "disk"` → **לא** מותר `restart_service`

אם אין התאמה לפלייבוק — **לא חוסמים** (כדי לשמור על ההתנהגות הדיפולטית של הגרסה הראשונה).

---

## איך Diagnostics עובד פה?

לכל Alert נוצר `Diagnostics` עם:
- `trace_id` ייחודי
- `steps[]` (רשומות זמן+שלב+דאטה)
- `error` (אם היתה חריגה)

Diagnostics מוחזר כפלט, ובנוסף אפשר לשמור ל‑JSONL עם `DIAGNOSTICS_JSONL`.

---

## החזרת LLM (כמו בגרסה הראשונה)

החלטה מתבצעת ב־`agent/decision.py` בעזרת OpenAI **Responses API**.  
המודל מחזיר JSON קצר בפורמט:

```json
{"action":"restart_service","confidence":0.7,"notes":"short"}
```

אם המודל מחזיר טקסט לא-JSON, יש fallback רזה שמנסה לזהות `restart`/`ignore`.

---

## איפה מחברים MCP אמיתי?

כרגע `agent/tools.py` כולל stub שמדמה הצלחה.  
כדי לחבר MCP:
1. החלף את `restart_service` בקריאה ל‑MCP tool שלך (fastmcp server).
2. שמור על אותו signature כדי לא לשנות את agent.

---

## מה "קריטי" שתוקן/הוסף בגרסה הזו?
- ✅ ה‑LLM חזר להיות מקור ההחלטה
- ✅ Playbook כ‑Guardrail (מותר/אסור)
- ✅ Trace דיאגנוסטי לכל אירוע
- ✅ Retry מינימלי לכלי, כדי לא ליפול על תקלות זמינות רגעיות

---

## קבצים חשובים
- `agent/agent.py` — זרימת הטיפול ב‑Alert
- `agent/decision.py` — החלטת LLM
- `agent/playbook.py` — Guardrails
- `agent/diagnostics.py` — Trace
- `agent/tools.py` — Tools (כרגע stubs)
- `ARCHITECTURE.md` — ארכיטקטורה בעברית


## שדרוגים קטנים שנוספו (בלי לסרבל)

- **Confidence Gate**: אם `confidence < 0.6` → הסלמה אוטומטית (`CONFIDENCE_MIN`).
- **Timeout + Max Tokens ל-LLM**: מונע תקיעות ועלויות.
- **Incident Summary**: שורת סיכום קצרה לכל אירוע (עם `trace_id`).
