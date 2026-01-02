# Refinement 7: Service Context & Booking Decision Alignment

**Date**: 2026-01-02  
**Trigger**: Scenario 18 (Duct Cleaning) - `gold_e18_ducts.md`  
**Status**: Planning  
**Component**: Decide Node, Booking Node

---

## Problem Statement

The agent handles specialized services like "Duct Cleaning" well, but the **`DecideNode` occasionally attempts to transition to `book` prematurely**, leading to a "double-book" attempt or a confusing second verification turn.

### Observed Behavior (Scenario 18 v1):

```
Turn 1:
AI Agent (Action: chat): [Asks for name and address]

Turn 2:
AI Agent (Action: book): "I'm almost ready to book that for you. I just need your name and your address to finish up."
```

**Result**: In Turn 2, the `DecideNode` chose `book` despite the `BookingNode` (internal logic) knowing that fields were still missing. This results in the `BookingNode` returning a "Missing data" message, which the `DecideNode` has to react to in the next turn.

### Expected Behavior:

The `DecideNode` should only pick `book` when it is 100% confident all mandatory fields (Name, Address, Service) are present in the `shared` store. If fields are missing, it should pick `chat` to request them directly, rather than relying on the `BookingNode`'s internal validation to speak to the user.

---

## Root Cause Analysis

### 1. **Decision Priority Logic**
The `decide_system.txt` instructions (Priority 1) tell the agent to book if data is "present". If the LLM *perceives* the data is present (even if the `ExtractionNode` hasn't successfully committed it to the `shared` store yet), it may trigger `book` too early.

### 2. **Verification Loop**
The `BookingNode` has its own "safety net" logic that returns a help message if fields are missing. While this prevents a database error, it creates a non-optimal "Action: book" turn that looks like a "Action: chat" turn to the user.

---

## Proposed Solutions

### Step 1: Strengthen DecideNode Guards
Update `decide_system.txt` to emphasize that 'book' should ONLY be picked if the **CURRENT DATA** section of the prompt explicitly shows Name and Address as provided, not just because they appear in the LAST MESSAGE.

### Step 2: Extraction Reliability
Modify `extract_system.txt` to ensure "Duct Cleaning" is explicitly mapped as a `service_type: "Maintenance"` or a new `service_type: "Duct Cleaning"` if we want more granularity.

---

## Heuristic Impact

| Heuristic | Expected | Current (v1) | Goal |
|:---|:---|:---|:---|
| **Workflow Efficiency** | 5/5 | 4/5 | **5/5** |
| **Logic Consistency** | 5/5 | 3/5 | **5/5** |
| **User Clarity** | 5/5 | 5/5 | 5/5 |

---

## Implementation Checklist

- [ ] **Prompt Hardening**: Update `decide_system.txt` to prevent premature `book` actions.
- [ ] **Data Mapping**: Ensure `Duct Cleaning` is consistently extracted.
- [ ] **Verification**: Re-run Scenario 18 v2 and ensure the transition to `book` only happens when `CURRENT DATA` is complete.

---

## Success Criteria

### **Scenario 18 should demonstrate:**
1. Direct transition from `chat` (request info) to `book` (perform booking) without an intermediate "Missing data" turn.
2. Accurate pricing disclosure ($299) as per the script.
3. Clean closure with confirmation ID.

---

## Related Documents

- **Scenario**: `data/qa/gold_e18_ducts.md`
- **Baseline**: `data/qa/multi_agent/gold_e18_ducts_multi_agent_v1.md`
- **Prompts**: `agent/prompts/`
