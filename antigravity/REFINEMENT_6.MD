# Refinement 6: Technical Advice & Booking Alignment

**Date**: 2026-01-02  
**Trigger**: Scenario 17 (Heat Pump) - `gold_e17_heatpump.md`  
**Status**: Planning  
**Component**: Chat Node, Decide Node

---

## Problem Statement

The agent successfully identifies HVAC system types (Furnace vs. Heat Pump) and provides helpful advice, but **prematurely uses the booking placeholder `HB-XXXX`** before the `BookingNode` has actually executed. This creates a confusing experience where the user sees a "confirmation" that hasn't been finalized in the system.

### Observed Behavior (Scenario 17 v1):

```
Turn 4:
AI Agent (Action: chat): "Perfect, Sarah! ... I’ll schedule your diagnostic visit today. Your confirmation number is HB-XXXX..."

Turn 5:
AI Agent (Action: book): [SYSTEM] Booking confirmed for Sarah Jenkins on 2026-01-03 14:00.
```

**Result**: The agent "confirmed" the booking in Turn 4 using a placeholder, only for the system to actually perform the booking in Turn 5.

### Expected Behavior:

The agent should only provide a confirmation number *after* the `BookingNode` has confirmed the slot and generated a real ID (e.g., `HB-3886`).

---

## Root Cause Analysis

### 1. **Placeholder Hallucination in ChatNode**
The `ChatNode` is provided with `HB-XXXX` as a default in its `prep` method when no real number exists yet. The persona instructions likely encourage the agent to "deliver Phase 2" (which includes the ID) as soon as data is complete, even if the `DecideNode` hasn't transitioned to `book` yet.

### 2. **Decision Overlap**
In Turn 4, the `DecideNode` chose `chat` because the user just confirmed the system type, but the agent's response attempted to "close" the loop partially. The `DecideNode` and `ChatNode` need better distinction between "Technical Advice" and "Booking Confirmation".

---

## Proposed Solutions

### Step 1: Hide Placeholder from ChatNode
Modify `ChatNode.prep` in `nodes.py` to only pass `hb_number` if it does NOT equal `HB-XXXX` or if `booking_info["confirmed"]` is `True`.

**Impact**: Prevents the LLM from seeing and using the placeholder prematurely.

### Step 2: Prompt Instruction Alignment
Update `chat_system.txt` to explicitly state:
- "Only provide a Booking Confirmation Number (HB-XXXX) once the booking is confirmed in our system."
- "If the booking is not yet confirmed, focus on confirming the details with the user first."

---

## Heuristic Impact

| Heuristic | Expected | Current (v1) | Goal |
|:---|:---|:---|:---|
| **Technical Accuracy** | 5/5 | 5/5 | 5/5 |
| **Workflow Integrity** | 5/5 | 3/5 | **5/5** |
| **Trust & Transparency** | 5/5 | 4/5 | **5/5** |

---

## Implementation Checklist

- [ ] **Node State Check**: Update `ChatNode.prep` to filter out placeholder IDs.
- [ ] **Prompt Guardrails**: Update `chat_system.txt` to prevent premature confirmation.
- [ ] **Verification**: Re-run Scenario 17 v2 and ensure the ID only appears *after* the `[SYSTEM] Booking confirmed` turn.

---

## Success Criteria

### **Scenario 17 should demonstrate:**
1. Accurate identification of Heat Pump via fan unit description.
2. Clear explanation of why system type matters.
3. **No mention** of confirmation numbers until the system actually books the slot.
4. Correct final confirmation with a real numeric ID.

---

## Related Documents

- **Scenario**: `data/qa/gold_e17_heatpump.md`
- **Baseline**: `data/qa/multi_agent/gold_e17_heatpump_multi_agent_v1.md`
- **Nodes**: `agent/nodes.py`
