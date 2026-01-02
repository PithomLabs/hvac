# BUG_1.3.MD: Handover Leak (Internal State Exposure)

**Bug ID**: BUG-001
**Update Version**: 1.3
**Status**: IDENTIFIED (Flow Termination Issue)
**Severity**: MEDIUM (Breaks immersion, unprofessional UI)
**Date**: 2026-01-02

---

## 1. Problem Statement
The user is seeing `[SYSTEM] Booking confirmed...` messages in the production environment. These were intended to be "silent" handovers for internal processing, but they are being printed to the CLI as the final response.

---

## 2. Technical Root Cause: Missing Graph Transition
The `BookingNode` in `agent/nodes.py` was designed to be "silent" (it doesn't produce human-friendly text), but the graph in `agent/flow.py` has no successor for the `book` node.

1. **Flow Execution**: `DecideNode` -> `BookingNode`.
2. **Termination**: Since `BookingNode` has no outgoing edges, `flow.run()` terminates.
3. **Leaked Response**: Because `BookingNode.post` sets `shared["last_response"]`, the `main.py` loop prints it.

### Why this happens now:
The "Aggressive Replying" fix (BUG_1.2) successfully aggregated the inputs, which allowed the conversation to reach the `book` node correctly. However, reaching the `book` node exposed the fact that it is a terminal node that doesn't "clean up" its own output.

---

## 3. Proposed Remediation (Handover-to-Handshake)

### A. Graph Update (`agent/flow.py`)
Connect `book >> chat`. This ensures that after a successful booking, the `ChatNode` is always called to deliver the professional Phase 2 handshake (HB-XXXX).

### B. Node Refinement (`agent/nodes.py`)
- Modify `BookingNode` to NOT set `shared["last_response"]` directly, or prefix it clearly as metadata.
- Ensure `ChatNode` detects `confirmed=True` and delivers the "Success!" spiel immediately.

---

## 4. Next Steps
- [ ] Connect `book >> chat` in `agent/flow.py`.
- [ ] Suppress `last_response` update in `BookingNode.post`.
- [ ] Verify closure with HB-XXXX number.

---
*Document Version: 1.3 | Reported by: USER / Antigravity*
