# MCP Ops Agent – Agent תפעולי (NOC/SRE) עם Playbooks + Diagnostics

פרויקט זה הוא **Agent תפעולי רציף (daemon)** שמדמה “איש NOC”:
> קיבלתי התראה → בדקתי → אבחנתי → טיפלתי → וידאתי → תיעדתי

הדגש כאן הוא על:
- **Playbooks** (טיפול עקבי ומובנה לפי סוג התראה)
- **Diagnostics** (שקיפות מלאה: למה האג'נט עשה/לא עשה משהו)

---

## מה קיים בפרויקט (בגדול)

### ✅ Agent רציף
- רץ בלולאה (`agent/agent.py`)
- מושך התראות דרך `get_alerts`
- שומר **Idempotency**: לא מטפל באותו `alert.id` פעמיים (`agent/memory.py`)

### ✅ Playbooks (מועדף לפני LLM)
- קבצי YAML בתיקיית `playbooks/`
- התאמה לפי `alert.name`
- מנגנון הרצה פשוט וברור (`agent/playbook_engine.py`)
- מאפשר "תפעול כמו בן אדם": בדיקה → החלטה → פעולה → אימות

### ✅ Diagnostics (Trace מקצה-לקצה)
- לכל alert נוצר `trace_id`
- כל שלב מתועד (`DiagnosticsContext`)
- API מקומי לצפייה ב-traces (FastAPI):
  - `GET /health`
  - `GET /diagnostics?limit=10`
  - `GET /diagnostics/{trace_id}`

---

## התקנה והרצה

### 1) התקנת תלויות
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) משתני סביבה מומלצים
צור קובץ `.env` (אופציונלי) או export ידני:

```bash
export OPENAI_API_KEY="..."
export OPENAI_MODEL="gpt-4.1"

# לולאה
export POLL_SECONDS=5

# Diagnostics API
export DIAG_HOST=0.0.0.0
export DIAG_PORT=8088

# דמו
export DEMO_MODE=1
export DEMO_ALERT_NAME=ServiceDown
export DEMO_SERVICE=nginx
export DEMO_SEVERITY=warning
export ENV=dev   # dev|prod
```

### 3) הרצה
```bash
python server.py
```

---

## איך לראות Diagnostics בזמן אמת

### רשימת Traces אחרונים
```bash
curl "http://localhost:8088/diagnostics?limit=10"
```

### Trace מלא (כולל steps + errors)
```bash
curl "http://localhost:8088/diagnostics/<TRACE_ID>"
```

✅ זה נותן לך תשובה מיידית ל:
- “למה האג'נט החליט X?”
- “איפה זה נתקע?”
- “איזה tool הופעל ומה החזיר?”

---

## איך עובד ה-Playbook Engine

### מבנה Playbook (YAML)
דוגמה: `playbooks/service_down.yaml`

- `match.alert_name` – התאמה להתראה
- `steps` – רשימת פעולות
  - `check` – קריאה ל-tool לאיסוף מידע
  - `decide` – תנאי פשוט (equals) שמחליט על then/else
  - `action` – פעולה (tool)
  - `verify` – אימות לאחר פעולה

**המטרה:** טיפול עקבי ושקוף, בלי להמציא Flow כל פעם מחדש.

---

## מה קורה אם אין Playbook?

במקרה שאין Playbook מתאים, או ש-Playbook נכשל:
- האג'נט בונה `context` (`agent/context.py`)
- קורא ל-LLM (`agent/decision.py`)
- מקבל JSON עם:
  - action
  - action_input
  - confidence
  - reason

### Safety ב-PROD
אם `ENV=prod` והפעולה היא `restart_service`:
- חייב confidence >= 0.85 (ברירת מחדל)
- אחרת האג'נט יחסום restart ויעשה notify (Human-in-the-loop)

---

## מבנה תיקיות

```text
.
├── server.py
├── models.py
├── requirements.txt
├── agent/
│   ├── agent.py
│   ├── context.py
│   ├── decision.py
│   ├── learning.py
│   ├── memory.py
│   ├── playbook_engine.py
│   ├── policies.py
│   └── prompts.py
├── diagnostics/
│   ├── api.py
│   ├── context.py
│   ├── logging.py
│   └── store.py
├── tools/
│   ├── registry.py
│   ├── get_alerts.py
│   ├── get_service_health.py
│   ├── restart_service.py
│   └── notify.py
└── playbooks/
    ├── service_down.yaml
    └── high_cpu.yaml
```

---

## התאמה ל-MCP אמיתי (אצלך בפרודקשן)
כיום `ToolRegistry` הוא Registry מקומי.

בפועל, אצלך אפשר:
- להחליף `tools.call()` לקריאה ל-**MCP Server** (stdio / http / sse)
- או לעטוף כל tool ב-client שמדבר עם `fastmcp`

הארכיטקטורה כאן בנויה כך שהשינוי יהיה נקודתי – בעיקר בשכבת `tools/`.

---

## Roadmap מומלץ (השלב הבא)
1. **חיבור אמיתי ל-Grafana/Alertmanager**
2. **Retry/Backoff** לכל tool + timeouts
3. **Policies עשירים יותר** (רשימות שירותים/סביבות/חלונות תחזוקה)
4. **Playbooks נוספים** (DiskFull, MemoryLeak, Latency)
5. **Approval אנושי** (Slack button / PagerDuty notes)
6. **Metrics** (Prometheus / OpenTelemetry)

---

## עיקרון מנחה
לא “אוטומציה עיוורת”, אלא:
> עובד צוות זהיר, שקוף, וניתן לביקורת (Diagnostics + Playbooks).
