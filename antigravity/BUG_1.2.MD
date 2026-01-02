# BUG_1.2.MD: Newline Fragmentation & Buffer Flooding

**Bug ID**: BUG-001
**Update Version**: 1.2
**Status**: IDENTIFIED (Root Cause Confirmed)
**Severity**: CRITICAL (Breaks conversational flow)
**Date**: 2026-01-02

---

## 1. Problem Statement
Despite the "Stop-Turn" protocol and pacing delays, the agent continues to "double-reply" or interrupt multi-line inputs. The user reports that the agent is "replying aggressively even though I still have to reply yet."

---

## 2. Technical Root Cause: Newline Fragmentation
The core issue is NOT the `DecideNode` loop, but the **Interaction Loop in `main.py`**:

1. **Fragmentation**: The CLI `input()` function reads one line at a time. If a user pastes a multi-line message (e.g., Name, Address, and Urgency separated by newlines), the OS treats each newline as a "Submit" event.
2. **Buffer Flooding**: 
   - Line 1 is consumed by `input()`.
   - `flow.run()` starts (takes 3-5s).
   - Lines 2 and 3 stay in the `stdin` buffer.
   - Once the agent finishes L1, the `input()` call for the "next turn" *immediately* consumes L2 from the buffer without waiting for human typing.
3. **Ghost Turns**: This creates the appearance of the agent "interrupting" the user or "answering twice."

---

## 3. Proposed Remediation (threshold timer)

### A. Threshold-Based Aggregator
Implement a `Threshold Timer` in `main.py` using non-blocking input (e.g., `select.select` or `termios`).
- **Wait Window**: After the first newline is received, the agent will wait **2 seconds** for additional input before proceeding to `flow.run()`.
- **Merge**: Any lines received during this window are aggregated into a single turn message.

### B. UI Cleanup
Suppress the `You: ` prompt if the turn was triggered by buffer consumption rather than fresh human interaction.

---

## 4. Next Steps
- [ ] Implement `MultiLineManager` class in `main.py`.
- [ ] Test with a pasted 3-line scenario.
- [ ] Verify that empty turns are still ignored.

---
*Document Version: 1.2 | Reported by: USER / Antigravity*
