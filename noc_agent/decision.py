import json
from openai import OpenAI
from noc_agent.models import Decision, Action

client = OpenAI()

SYSTEM = """
אתה איש NOC מנוסה.
החזר החלטה תפעולית בפורמט JSON בלבד.

אם לא בטוח → escalate
פעולה אוטומטית רק אם risk=low וביטחון גבוה.
"""

def decide(alert: dict, context: dict, allowed_tools):
    payload = {
        "alert": alert,
        "context": context,
        "allowed_tools": allowed_tools
    }

    resp = client.responses.create(
        model="gpt-4.1",
        input=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False)}
        ]
    )

    data = json.loads(resp.output_text)
    actions = [Action(**a) for a in data.get("actions", [])]

    return Decision(
        recommendation=data["recommendation"],
        confidence=data["confidence"],
        actions=actions,
        close_message=data["close_message"]
    )
