# BUG_1.6.MD: Premature Termination (Trigger-Happy Finisher)

**Bug ID**: BUG-001
**Update Version**: 1.6
**Status**: IDENTIFIED
**Severity**: MEDIUM (Affects user satisfaction and completeness)
**Date**: 2026-01-02

---

## 1. Problem Statement
The agent terminates the conversation (`*END OF CONVERSATION*`) while the user is still asking critical follow-up questions (e.g., billing details, preparation instructions).

---

## 2. Technical Root Cause

### A. Decision Node Aggression
The `DecideNode` (Manager) is likely interpreting "Okay, that works" as a sign of closure, ignoring the subsequent "Just to be totally clear though..." follow-up questions.

### B. Phase 2/3 Ambiguity
The prompts for `DecideNode` and `ChatNode` prioritize "Moving to closure" once the booking is confirmed, leading to a "mission accomplished" bias that ignores secondary user needs.

---

## 3. Proposed Remediation

### A. "Negative Acknowledgement" Rule
Update `decide_system.txt` to explicitely check for **question marks** or **uncertainty** in the user's last message. 
- **Rule**: "If the user suggests closure BUT includes a question mark or a new concern, you MUST pick 'chat', NOT 'finish'."

### B. Chat Node Persistence
Update `chat_system.txt` to reinforce that in Phase 2, the agent must stay in the loop until a "clean" goodbye is received (e.g., "That's all", "No thanks").

---

## 4. Next Steps
- [ ] Refine `decide_system.txt` logic.
- [ ] Update `chat_system.txt` termination rules.
- [ ] Verify with Scenario 12 (Tenant/Landlord).

---
*Document Version: 1.6 | Reported by: USER / Antigravity*
