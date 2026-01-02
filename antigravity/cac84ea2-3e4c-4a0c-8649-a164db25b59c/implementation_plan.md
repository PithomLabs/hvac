# Scenario 16: Angry Customer and Manager Escalation Support

This plan implements sentiment analysis and manager escalation logic to address Scenario 16 (Angry Customer/Callback).

## Proposed Changes

### Prompts

#### [MODIFY] [extract_system.txt](file:///home/chaschel/Documents/ibm/ai/PocketFlow-Template-Python-main/agent/prompts/extract_system.txt)
- Add `sentiment` ("Angry", "Neutral") to output JSON.
- Add `is_callback` (boolean) to output JSON.
- Update instructions to detect "angry" tone or mentions of "previous visit", "broken again".

#### [MODIFY] [decide_system.txt](file:///home/chaschel/Documents/ibm/ai/PocketFlow-Template-Python-main/agent/prompts/decide_system.txt)
- Add rule to prioritize `chat` if sentiment is "Angry" to ensure the agent acknowledges the frustration immediately before asking for data.

#### [MODIFY] [chat_system.txt](file:///home/chaschel/Documents/ibm/ai/PocketFlow-Template-Python-main/agent/prompts/chat_system.txt)
- Update with instructions to include:
  - Empathetic apology for "Repeat Issues".
  - "Flagged for service manager" script.
  - "Priority lead technician" script.

### Agent Logic

#### [MODIFY] [nodes.py](file:///home/chaschel/Documents/ibm/ai/PocketFlow-Template-Python-main/agent/nodes.py)
- **`ExtractionNode`**: Update `post` to store `sentiment` and `is_callback` into `shared["booking_info"]`.
- **`DecideNode`**: Pass `sentiment` and `is_callback` from `shared` to the LLM prompt.
- **`ChatNode`**: Pass `sentiment` and `is_callback` from `shared` to the LLM prompt to ensure the response reflects the escalation.

## Verification Plan

### Automated Tests
- Run simulation: `python3 data/qa/simulation_orchestrator.py data/qa/gold_d16_angry.md`
- Verify the output `v4` (or latest) includes:
  - Sentiment-aware acknowledgment.
  - Mention of "service manager" or "priority".
  - Proper closure with `*END OF CONVERSATION*`.

### Manual Verification
- Review the generated simulation log to ensure natural and empathetic tone throughout the turns.
- Check that the agent doesn't loop unnecessarily if the customer remains angry but provides info.
