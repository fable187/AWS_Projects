ComTec / Entergy AI Developer interview prep summary
Interview: Tuesday 24 Nov, 9:00 to 9:30 AM Central, Teams, with Srinivas (Senior Technical Delivery Manager)

WHAT I BUILT (AWS, us-east-1)
1. Bedrock Guardrail "utility-customer-assistant" (ID dpjhotmmfkpw)
   - Harmful content and prompt attack filters set to Block at High, Standard tier, cross-Region inference
   - Denied topic: Investment (tested: "invest my refund in Entergy stock or crypto" gets blocked)
   - Profanity filter on
   - PII masking for Name, Phone, Email and Address
   - Tested with the ApplyGuardrail API and confirmed in the trace
2. Local Python project (VS Code, .venv, boto3, AWS CLI, IAM user bedrock-dev)
   - agent.py: applies business rules (life support means no disconnect, under 60 days means hold, 1000+ customers means Priority 1)
   - storm_triage.py: groups fake outage tickets by feeder, ranks life-support feeders first, masks PII through the guardrail
3. Lambda "storm_triage" (Python)
   - Execution role stormtriage-role with an inline least-privilege policy: only bedrock:ApplyGuardrail, on the guardrail plus the us.guardrail.v1:0 guardrail-profile
   - Test returned 200, F-12 ranked first (life support), PII masked
   - Function URL: auth AWS IAM, Buffered invoke mode, CORS off

TALKING POINTS
- Least privilege: the first Lambda run failed because cross-Region guardrails also need the guardrail-profile resource. I read the error and scoped the policy rather than granting full access.
- Business rules are deterministic code, and the LLM/guardrail handles the language and the PII. Safety-critical decisions (life support) never depend on the model.
- F-12 ranks above F-07 even though it has fewer customers, because life-support customers come first by design. Customer safety beats raw outage size.
- Gap I found: the Phone filter missed 504-555-0123. The fix is a regex filter, and the same goes for account numbers. That's why you test guardrails with real-looking data.
- Function URL is IAM-protected, so there's no public endpoint and no surprise guardrail charges.
- Automated Reasoning checks could formally verify policy rules like the medical-certification no-disconnect rule.
- Path to production: Lambda plus function URL, then DynamoDB for tickets, then Converse (Claude) summaries once model access is approved, then an Azure front end (liaison) calling it.

NEXT STEPS (not done)
- Give bedrock-dev lambda:InvokeFunctionUrl and call the URL with a SigV4-signed Python request
- Add regex filters for phone numbers and account numbers to the guardrail
- Sort out Claude model access (Anthropic use case form)
- Hook up the liaison Azure app