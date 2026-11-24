import boto3
from collections import defaultdict

REGION = "us-east-1"
GUARDRAIL_ID = "dpjhotmmfkpw"
GUARDRAIL_VERSION = "DRAFT"

bedrock = boto3.client("bedrock-runtime", region_name=REGION)

TICKETS = [
    {"id": 201, "feeder": "F-12", "substation": "Metairie North", "customers": 1, "life_support": False, "text": "John Smith at 12 Oak St, power out since 3am, call 504-555-0101."},
    {"id": 202, "feeder": "F-12", "substation": "Metairie North", "customers": 1, "life_support": True, "text": "Mary Jones at 14 Oak St, oxygen concentrator needs power, mary@example.com."},
    {"id": 203, "feeder": "F-12", "substation": "Metairie North", "customers": 1, "life_support": False, "text": "Tree on line near 20 Oak St, sparking."},
    {"id": 204, "feeder": "F-07", "substation": "Kenner East", "customers": 1200, "life_support": False, "text": "Transformer blew near Kenner East substation, whole area dark."},
    {"id": 205, "feeder": "F-07", "substation": "Kenner East", "customers": 1, "life_support": False, "text": "Lights out at 88 Pine Ave, Bob Lee 504-555-0199."},
    {"id": 206, "feeder": "F-31", "substation": "Harahan", "customers": 1, "life_support": False, "text": "Flickering lights at 5 River Rd."},
]

def mask(text):
    resp = bedrock.apply_guardrail(
        guardrailIdentifier=GUARDRAIL_ID,
        guardrailVersion=GUARDRAIL_VERSION,
        source="INPUT",
        content=[{"text": {"text": text}}],
    )
    if resp.get("action") == "GUARDRAIL_INTERVENED" and resp.get("outputs"):
        return resp["outputs"][0]["text"]
    return text

def group_by_feeder(tickets):
    groups = defaultdict(list)
    for t in tickets:
        groups[t["feeder"]].append(t)
    return groups

def score(feeder_tickets):
    customers = sum(t["customers"] for t in feeder_tickets)
    life = any(t["life_support"] for t in feeder_tickets)
    calls = len(feeder_tickets)
    likely_single_failure = calls >= 3 or customers >= 1000
    return {
        "customers": customers,
        "calls": calls,
        "life_support": life,
        "single_failure": likely_single_failure,
        "rank_key": (life, customers, calls),
    }

def main():
    groups = group_by_feeder(TICKETS)
    ranked = sorted(groups.items(), key=lambda kv: score(kv[1])["rank_key"], reverse=True)
    print("=== STORM DISPATCH QUEUE ===")
    for i, (feeder, tix) in enumerate(ranked, 1):
        s = score(tix)
        flags = []
        if s["life_support"]:
            flags.append("LIFE-SUPPORT")
        if s["single_failure"]:
            flags.append("LIKELY SINGLE FAILURE")
        print(f"\n#{i} Feeder {feeder} ({tix[0]['substation']}): {s['customers']} customers, {s['calls']} calls {' | '.join(flags)}")
        for t in tix:
            print(f"   Ticket {t['id']}: {mask(t['text'])}")

if __name__ == "__main__":
    main()