import json
from openai import OpenAI
from agent.prompts import DECISION_PROMPT

client = OpenAI()

def decide(alert, context):
    prompt = DECISION_PROMPT.format(alert=alert, context=context)
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return json.loads(resp.choices[0].message.content)
