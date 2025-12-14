# ארכיטקטורה — mcp-agent-slim

## מטרות
1. לשמור על **פשטות** והתנהגות קרובה לגרסה הראשונה (LLM->Action).
2. להוסיף רק שני רכיבים “שקטים”:
   - **Diagnostics**: שקיפות מלאה של מה קרה ולמה.
   - **Playbook**: Guardrail דק שמונע פעולות אוטומטיות מסוכנות.
3. לא לנעול למימוש מסוים: Tools יכולים להיות מקומיים או MCP.

---

## תרשים זרימה

```
Alert (JSON)
   |
   v
Diagnostics(trace_id)
   |
   v
LLM Decision (action)
   |
   v
Playbook Guardrail (allowed?)
   |            |
   | yes        | no
   v            v
Execute Tool     Notify(blocked)
   |
   v
Return Diagnostics (+ optional JSONL)
```

---

## רכיבים

### 1) Agent Orchestrator — `agent/agent.py`
אחראי על:
- פתיחת `Diagnostics` לכל Alert
- קריאה ל־`decide()` (LLM)
- בדיקת הרשאה מול `is_action_allowed()` (Playbook)
- הרצת כלי (`restart_service`)
- Notify על escalations/שגיאות
- שמירה אופציונלית של Diagnostics ל‑JSONL

עקרון: ה‑Orchestrator **לא חושב** — הוא מנהל סדר פעולות.

---

### 2) LLM Decision — `agent/decision.py`
ה‑LLM מחזיר החלטה קצרה:
- `action`: restart_service / escalate / ignore
- `confidence`: 0..1
- `notes`: הערה קצרה

למה JSON?
- יציב לאוטומציה
- קל לפרסור
- פחות “דיבורים”

יש fallback אם המודל חזר לא‑JSON.

---

### 3) Playbook Guardrail — `agent/playbook.py`
זה intentionally קטן:
- לא Workflow engine
- לא Step-by-step
- רק “מותר/אסור” לפי `metric/alert_name`

אם אין התאמה — לא חוסמים (שומר דמיון לגרסה הראשונה).

---

### 4) Diagnostics — `agent/diagnostics.py`
לכל Alert:
- `trace_id`
- `steps[]` מסודר בזמן
- `error` אם היתה חריגה

זה מאפשר:
- דיבוג (“איפה נתקע”)
- Auditing (“למה עשית restart?”)
- שיפור Playbooks/Prompts בעתיד

---

### 5) Tools — `agent/tools.py`
כרגע stubs:
- `restart_service()` מדמה הצלחה
- `notify()` מדפיס למסך

בגרסת production:
- `restart_service` יקרא ל‑MCP tool שלך
- `notify` יתחבר ל‑Slack/PagerDuty

---

## נקודות הרחבה (בלי להפוך לכבד)
1. **MCP Integration**: החלפת stubs ב‑MCP client.
2. **Policies**: שכבת חוקים קשיחים נוספת, אם תרצה.
3. **Observability**: metrics בהמשך (לא חובה בשלב הזה).
4. **Human-in-the-loop**: approval לפעולות מסוכנות.
