import boto3

REGION = "us-east-1"
GUARDRAIL_ID = "dpjhotmmfkpw"
GUARDRAIL_VERSION = "DRAFT"
MODEL_ID = None  # set to a Claude model or inference profile ID once access works

bedrock = boto3.client("bedrock-runtime", region_name=REGION)

tickets = [
    {"id": 101, "type": "disconnect", "life_support": True, "days_past_due": 45,
     "text": "John Smith, 123 Oak Street, 504-555-0123, needs medical equipment powered."},
    {"id": 102, "type": "outage", "life_support": False, "customers_affected": 1200,
     "text": "Transformer down near Canal St, jane@example.com reported it."},
    {"id": 103, "type": "disconnect", "life_support": False, "days_past_due": 75,
     "text": "Bob Lee, 456 Pine Ave, account overdue."},
]

def apply_rules(t):
    if t["type"] == "disconnect" and t["life_support"]:
        return "HOLD: life-support customer, no disconnect allowed"
    if t["type"] == "disconnect" and t["days_past_due"] < 60:
        return "HOLD: under 60 days past due"
    if t["type"] == "outage" and t.get("customers_affected", 0) >= 1000:
        return "PRIORITY 1: large outage, dispatch crew"
    return "PROCEED: standard queue"

def guard(text, source="INPUT"):
    r = bedrock.apply_guardrail(
        guardrailIdentifier=GUARDRAIL_ID,
        guardrailVersion=GUARDRAIL_VERSION,
        source=source,
        content=[{"text": {"text": text}}],
    )
    if r["action"] == "GUARDRAIL_INTERVENED":
        return r["outputs"][0]["text"] if r["outputs"] else "[blocked]"
    return text

def summarize(text):
    if not MODEL_ID:
        return "(model summary skipped)"
    r = bedrock.converse(
        modelId=MODEL_ID,
        messages=[{"role": "user", "content": [{"text": "Summarize this utility ticket in one line: " + text}]}],
        guardrailConfig={"guardrailIdentifier": GUARDRAIL_ID, "guardrailVersion": GUARDRAIL_VERSION},
    )
    return r["output"]["message"]["content"][0]["text"]

for t in tickets:
    safe = guard(t["text"])
    print(f"Ticket {t['id']}: {apply_rules(t)}")
    print(f"  Masked: {safe}")
    print(f"  Summary: {summarize(safe)}")