# Refinement 8: Simplified Inputs & Location Constraint Validation

**Date**: 2026-01-02  
**Trigger**: Scenario 19 (Language/Simplified) - `gold_e19_language.md`  
**Status**: Planning  
**Component**: Decide Node, Service Area Check

---

## Problem Statement

The agent handles simplified/broken English inputs well but continues to exhibit a **misalignment between the `DecideNode` and the `shared` store state**, leading to premature `book` actions that fail internal validation. Additionally, the **Service Area Rule** correctly blocks out-of-area bookings, but the feedback loop could be improved to prevent a "book -> fail -> chat" sequence.

### Observed Behavior (Scenario 19 v1):

```
Turn 2:
Human: Sarah. 123 Maple Lane, Springfield...
DecideNode (Action: book): [Triggers BookingNode]
BookingNode: "I'm almost ready... I just need your name and your address..."

Turn 3:
DecideNode (Action: chat): "Sorry, Sarah, but our service doesn’t include Springfield..."
```

**Result**: The agent attempted to book in Turn 2 (incorrectly thinking it had enough info or ignoring the location constraint), which was rejected by the `BookingNode` for missing fields. Then, once the data was presumably processed, it correctly identified the location constraint in Turn 3.

### Expected Behavior:

The `DecideNode` should:
1.  **Block 'book' if the location is out-of-area** immediately, before reaching the `BookingNode`.
2.  **Ensure all fields are actually in the store** before picking `book`.

---

## Root Cause Analysis

### 1. **Location Check Latency**
The `SERVICE AREA RULE` is defined in `decide_system.txt`, but in Turn 2, the LLM may have prioritized the "All data present -> book" rule over the "Springfield -> decline" rule, possibly because it was still extracting the address.

### 2. **State Sync Lag**
The "Double-Book" attempt (seen in Refinement 7) persists. The `DecideNode` sees the data in the `LAST MESSAGE` and picks `book`, but the `shared` store hasn't been updated by the `ExtractionNode` yet (or they are running in the same flow cycle where the Decider still sees the "before" state).

---

## Proposed Solutions

### Step 1: Elevate Geofencing in Decision Logic
Move the `SERVICE AREA RULE` to be explicitly Checked in every turn, including extraction turns.

### Step 2: Fix Data Dependency in Decider
(Repeat from Refinement 7) Ensure `DecideNode` only uses `CURRENT DATA` for its booking decision, not the `LAST MESSAGE`.

---

## Heuristic Impact

| Heuristic | Expected | Current (v1) | Goal |
|:---|:---|:---|:---|
| **Geofencing Reliability** | 5/5 | 4/5 | **5/5** |
| **Logic Sequencing** | 5/5 | 3/5 | **5/5** |
| **Resilience to Slang** | 5/5 | 5/5 | 5/5 |

---

## Implementation Checklist

- [ ] **Geofence Isolation**: Update `decide_system.txt` to strictly prioritize out-of-area declines.
- [ ] **Status Mapping**: Confirm "Juan/Springfield" patterns are correctly identified as "Juan" (Name) and "Springfield" (Address).
- [ ] **Verification**: Re-run Scenario 19 v2 and ensure the Springfield decline happens as soon as "Springfield" is mentioned, without a `book` turn.

---

## Success Criteria

### **Scenario 19 should demonstrate:**
1. High empathy for simplified language ("Heat no work").
2. **Immediate decline** for out-of-area locations (Springfield) without attempting to book.
3. Clean closure after decline.

---

## Related Documents

- **Scenario**: `data/qa/gold_e19_language.md`
- **Baseline**: `data/qa/multi_agent/gold_e19_language_multi_agent_v1.md`
- **Refinement 7**: (Related "Double-Book" issue)
