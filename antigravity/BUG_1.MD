# BUG_1.MD: Aggressive Replying & Extraction Loops

**Bug ID**: BUG-001
**Status**: IDENTIFIED / DRAFTING REMEDIATION
**Severity**: HIGH (Degrades UX, wastes LLM tokens)
**Date**: 2026-01-02

---

## 1. Problem Statement
The AI agent exhibits "aggressive" behavior by responding multiple times or entering internal decision loops without waiting for a new user message. In certain conditions, the agent appears to trigger its own `flow.run()` even when the user has provided no new input or is still in the process of typing.

### Observed Symptoms
- Multiple `[DEBUG] DecideNode calling LLM` logs appearing for a single turn.
- Agent delivery of multiple "Agent:" responses in a row.
- Unintended transitions between `extract` and `chat` nodes that do not reach a terminal state or reach it too quickly.

---

## 2. Technical Root Cause Analysis

### A. Technical Cycle in `flow.py`
The current graph structure includes a cycle:
`ExtractionNode >> DecideNode`
and
`DecideNode - "extract" >> ExtractionNode`

While this is intended for message refinement, if `DecideNode` fails to decisively transition to `chat` or `book`, the flow can loop indefinitely (or until LLM context limits are hit) inside a single `flow.run()` call.

### B. Decision Drift in `DecideNode`
When the model (e.g., `openai/gpt-oss-120b`) is used, it may generate subtle variations in reasoning that lead the `DecideNode` to cycle through extraction attempts repeatedly. If the state is ambiguous, the node might trigger `extract` even if no new information is present.

### C. Interaction Loop Synchronization (`main.py`)
In `main.py`, the `while True` loop relies on `input()`. If `input()` returns an empty string or is bypassed (e.g., due to newline characters in the buffer), the `flow.run(shared)` is called again with the *same* history, causing the agent to repeat its last thought process.

---

## 3. Proposed Remediation (STOP-TURN Protocol)

### A. Maximum Extraction Guardrail
Implement a `MAX_EXTRACTION_ATTEMPTS` constant (recommended: 3). If `DecideNode` detects it has stalled on extraction, it MUST force a `chat` or `finish` action to break the loop.

### B. Turn-Based Stop Flag
Introduce a `shared["stop_flow"]` flag. 
- When `ChatNode` or `BookingNode` finishes, they set a terminal state.
- `main.py` should explicitly reset all transition history between turns.

### C. Input Hardening
```python
user_input = input(f"\nYou: ").strip()
if not user_input:
    continue # Strictly ignore empty inputs
```

### D. STOP Keyword Implementation
Allow the user to type `STOP` or `HALT` to manually set the `stop_flow` flag, giving the human absolute control over the conversation pacing.

---

## 4. Verification Criteria
- [ ] No more than 3 `extract` calls per human message.
- [ ] Agent strictly waits for `input()` after every `Agent:` response.
- [ ] "STOP" keyword terminates the agent's current thought loop immediately.

---
*Document Version: 1.0 | Reported by: USER / Antigravity*
