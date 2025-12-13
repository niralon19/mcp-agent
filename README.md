# MCP Ops Agent 🤖  
Continuous Operations & Monitoring Agent

## 🎯 מטרת הפרויקט
Agent תפעולי חכם (Ops / NOC / SRE) שעובד 24/7 ומטפל בהתראות **כמו איש צוות אמיתי**:

- מקבל Alerts ממערכות ניטור
- בונה הקשר (context) רחב
- מחליט מה לעשות (LLM)
- מפעיל פעולות דרך MCP tools
- זוכר מה קרה ולומד לאורך זמן
- מסלים לאדם כשצריך

ה-Agent מחליף Tier-1 Engineer.

---

## 🧠 ארכיטקטורה כללית


---

## 📂 מבנה הפרויקט
mcp-server/
├── server.py # Entrypoint – מריץ את ה-Agent כ-daemon
├── tools/ # MCP Tools (יכולות ביצוע)
│ ├── get_alerts.py
│ ├── restart_service.py
│ ├── get_service_health.py
│ └── notify.py
├── agent/
│ ├── agent.py # הלולאה הראשית (Continuous Agent)
│ ├── context.py # בניית הקשר (מצב מערכת + זיכרון)
│ ├── decision.py # קבלת החלטות עם LLM
│ ├── policies.py # חוקים קשיחים (Guardrails)
│ ├── memory.py # זיכרון (State)
│ ├── learning.py # למידה מצטברת
│ └── prompts.py # פרומפטים ל-LLM
├── models.py # מודלים לוגיים (Alerts וכו')
└── requirements.txt

---

## 🔄 זרימת עבודה (Flow)

1. `server.py` מפעיל Agent רציף (Daemon)
2. `get_alerts` מחזיר התראות חדשות
3. נבדק האם ההתראה כבר טופלה (Memory)
4. נבנה Context:
   - מצב השירות
   - זיכרון עבר
   - דפוסים שנלמדו
5. Policies חוסמות פעולות מסוכנות
6. `decision.py` מפעיל LLM לקבלת החלטה
7. מתבצעת פעולה דרך MCP tool
8. הזיכרון מתעד את הטיפול

---

## 🧠 agent/agent.py – הלב של המערכת

- רץ בלולאה אינסופית
- Idempotent – לא מטפל באותה התראה פעמיים
- מתנהג כמו איש Ops במשמרת

זה **לא סקריפט**, זה עובד צוות.

---

## 🧩 Context – למה זה קריטי?

Agent טוב לא מגיב רק ל־Alert, אלא שואל:
- מה מצב השירות עכשיו?
- מה קרה בעבר?
- האם פעולות דומות עזרו?
- מה מותר לי לעשות?

הכול נבנה ב־`context.py`.

---

## 🚨 Policies – חוקים קשיחים

Policies הם Guardrails:
- התראות Critical → אדם
- שירותים רגישים → לא לגעת
- Prod ≠ Dev

גם אם ה־LLM “חושב אחרת” – policies מנצחים.

---

## 🧠 Decision (LLM)

`decision.py`:
- מקבל Alert + Context
- מחזיר JSON בלבד:
```json
{
  "action": "restart_service",
  "reason": "...",
  "confidence": 0.82
}

🧠 Memory

memory.py:

מונע טיפול כפול

שומר state פשוט (JSON)

בסיס ל־Human Override וללמידה עתידית

📈 Learning

learning.py:

מסכם היסטוריה

מאפשר להסיק דפוסים

שלב ראשון ל־Agent שממש משתפר עם הזמן

▶️ הרצה
pip install -r requirements.txt
export OPENAI_API_KEY=your_key
python server.py

🛣️ Roadmap מומלץ

Human Override (איש צוות משנה החלטה)

Confidence threshold + auto escalation

Incident objects

systemd service

חיבור n8n / PagerDuty / Slack

Vector memory (RAG)

🧠 עיקרון מנחה

לא להפוך את ה-Agent לאוטומציה עיוורת
אלא לעובד צוות זהיר, לומד, ושקוף

👷 למי זה מתאים

Ops / NOC

SRE

SOC

DevOps Teams

Teams שרוצים להוריד רעש ולא אחריות