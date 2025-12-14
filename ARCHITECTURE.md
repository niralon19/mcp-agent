# ארכיטקטורה – MCP Ops Agent עם Playbooks ו-Diagnostics

## מטרת המערכת
להריץ Agent תפעולי רציף שמטפל בהתראות בצורה עקבית ושקופה:

1. קבלת Alert
2. בניית הקשר (Context)
3. בחירת Playbook והפעלתו
4. אם אין Playbook/כשל → החלטה עם LLM
5. ביצוע פעולות דרך Tools (MCP בעתיד)
6. תיעוד מלא של כל שלב (Diagnostics)
7. שמירה על Idempotency (Memory)

---

## רכיבים עיקריים

### 1) OpsAgent (`agent/agent.py`)
- מנהל לולאה רציפה
- מבצע “טיפול” ב-alert אחד בכל פעם
- אחראי על סדר הפעולות:
  - Memory → Policies → Playbook → LLM → Action → Save

### 2) Tools (`tools/*`)
שכבת הביצוע.
כיום זו הדמיה מקומית (`ToolRegistry`), אבל בפרודקשן זו תהיה מעטפת לקריאה ל-MCP tools.

דוגמאות:
- `get_alerts`: משיכה ממערכת ניטור
- `get_service_health`: בדיקת מצב שירות
- `restart_service`: פעולה מתקנת
- `notify`: הודעה/הסלמה

### 3) Policies (`agent/policies.py`)
Guardrails קשיחים:
- חוסם פעולות מסוכנות
- מסלים לאדם כשצריך (notify)
- policies תמיד מנצחים (גם אם LLM “רוצה אחרת”)

### 4) Playbooks (`playbooks/*.yaml` + `agent/playbook_engine.py`)
מנגנון טיפול מובנה לפי סוג התראה:
- התאמה לפי `alert.name`
- Steps: check → decide → action → verify

יתרון:
- עקביות
- שקיפות
- פחות “המצאות” של LLM
- קל לתחזק ולהוסיף

### 5) LLM Decision (`agent/decision.py`)
Fallback/Router כשה-Playbook לא קיים או נכשל.
מחזיר JSON מוגדר בלבד:
- `action`
- `action_input`
- `reason`
- `confidence`

מנגנון safety ל-PROD:
- restart רק מעל confidence threshold

### 6) Memory (`agent/memory.py`)
Idempotency + state:
- מונע טיפול כפול באותו alert
- נשמר ל-`state/memory.json`

### 7) Diagnostics (`diagnostics/*`)
Trace per alert:
- `trace_id`
- steps
- errors (כולל stacktrace קצר)
- API לצפייה:
  - `/diagnostics`
  - `/diagnostics/{trace_id}`

---

## זרימת נתונים (Flow)

```text
                ┌──────────────────────┐
                │   get_alerts (Tool)  │
                └──────────┬───────────┘
                           │ alerts[]
                           v
┌────────────────────────────────────────────────────────┐
│                     OpsAgent                            │
│                                                        │
│  1) Memory: already_handled? -> skip                    │
│  2) Policies: allow/block + escalation                  │
│  3) Playbook match -> run steps (check/action/verify)   │
│  4) else: build_context -> LLM decide -> action         │
│  5) mark handled + save                                 │
└───────────────┬────────────────────────────────────────┘
                │
                │ trace steps/errors
                v
     ┌───────────────────────────┐
     │ DiagnosticsStore (buffer) │
     └──────────┬────────────────┘
                │
                v
     ┌───────────────────────────┐
     │  FastAPI Diagnostics API   │
     │  /diagnostics /health      │
     └───────────────────────────┘
```

---

## נקודת חיבור ל-MCP (בעתיד הקרוב)
החלפה נקודתית:
- במקום `ToolRegistry.call(name, **kwargs)`
- לממש `MCPClient.call_tool(name, args)` שמדבר עם `fastmcp`/MCP server

היתרון:
- הארכיטקטורה נשארת זהה
- רק שכבת tools משתנה

---

## למה זה “Production-friendly”
- Playbooks → יציבות ועקביות
- Policies → בטיחות
- Diagnostics → שקיפות ודיבוג מהיר
- Memory → מניעת הצפה כפולה
- Separation → אפשר להחליף MCP/LLM בלי לשבור את הכל
