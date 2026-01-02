# BUG_1.4.MD: Context Blindness & Extraction Bypass

**Bug ID**: BUG-001
**Update Version**: 1.4
**Status**: IDENTIFIED
**Severity**: MEDIUM (Affects conversation efficiency)
**Date**: 2026-01-02

---

## 1. Problem Statement
The agent sometimes ignores details provided in long, high-context user messages (e.g., Address, ZIP, Issue) and proceeds with generic "chat" requests for the same information. This forces the user to repeat themselves.

---

## 2. Technical Root Cause

### A. Decision Priority Loophole
In `DecideNode`, if the model's first decision for a complex message is `chat` (perhaps due to the emotional frustration in the text), the `ExtractionNode` is bypassed entirely. The `ChatNode` then sees "Missing" fields and asks for them generically.

### B. "Ghost Turn" Buffer Interaction
If a multi-line message triggers the aggregator halfway through, Turn 1 might handle the frustration while Turn 2 (the rest of the data) arrives after the agent has already decided on Turn 1's action. This out-of-sync processing causes "Context Blindness."

---

## 3. Proposed Remediation (Eager Extraction)

### A. Force Extraction on First Turn
Modify `DecideNode` to MANDATE an `extract` action if `history` has only 1-2 messages and `user_info` is significantly empty, regardless of the prompt's reasoning.

### B. Aggregator Tuning
Increase `select.select` timeout from `0.5s` to `0.8s` to ensure slower pastes or network lags don't fragment messages into "Ghost Turns."

### C. Booking Handover Fix
Correct the `nodes.py` leak by properly silencing the `BookingNode.post` response.

---

## 4. Next Steps
- [ ] Implement Eager Extraction in `DecideNode.exec`.
- [ ] Tune aggregator in `main.py`.
- [ ] Re-apply `nodes.py` silence patch.

---
*Document Version: 1.4 | Reported by: USER / Antigravity*
