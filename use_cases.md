# Entergy AI Triage: Use Case Ideas

## 1. Storm-Mode Outage Triage
- During hurricanes and major storms, outage tickets flood in.
- Agent groups reports by street, feeder line or substation.
- Detects likely single points of failure behind hundreds of calls.
- Ranks crew dispatch by customers affected and critical loads.
- Life-support and medical customers are always flagged first.
- Builds on: apply_rules (Priority 1 logic), Guardrail PII masking.

## 2. Disconnect Compliance Checker
- Every shutoff is checked against the rules before it goes out.
- Rules: medical certificates / life support, extreme heat or freeze moratoriums, active payment arrangements, minimum days past due, required notice periods.
- Blocks any disconnect that would break a rule and explains why.
- Strong fit for Bedrock Guardrails Automated Reasoning checks (provable policy compliance).
- Builds on: apply_rules (life-support hold, under-60-days hold).

## 3. Field Tech Notes to Work Orders
- Lineman dictates or types messy notes from the truck.
- Agent turns them into a structured work order: location, equipment, parts needed, hazards, follow-up tasks.
- Customer PII masked by the Guardrail before storage.
- Output as JSON for the work management system.

## 4. Regulatory Filing Assistant
- Pulls outage and reliability data (e.g. SAIDI / SAIFI, EIA open data).
- Drafts reliability reports for the Public Service Commission.
- Every number traced back to its source for auditability.
- Contextual grounding check in Guardrails to catch unsupported claims.

## Prototype Path (AWS)
- Lambda function + function URL: post a ticket as JSON, get decision + masked text.
- DynamoDB table: audit log of each ticket, decision and timestamp.
- Optional: liaison (Azure) calls the Lambda for a cross-cloud demo.

## Known Gap / Talking Point
- Phone filter missed "504-555-0123" format: add a regex filter to the Guardrail.
- Add a regex for customer account numbers.