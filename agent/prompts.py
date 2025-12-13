DECISION_PROMPT = '''
You are a senior SRE.

Alert:
{alert}

Context:
{context}

Choose ONE action from:
restart_service, notify, escalate

Respond ONLY in JSON:
{
  "action": "...",
  "reason": "...",
  "confidence": 0.0
}
'''
