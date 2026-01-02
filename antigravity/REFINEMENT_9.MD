# Refinement 9: Intent Validation & Proper Nonsense Handling

**Date**: 2026-01-02  
**Trigger**: Scenario 20 (Garbage/Trolling) - `gold_e20_garbage.md`  
**Status**: Planning  
**Component**: Decide Node, Chat Node

---

## Problem Statement

The agent **lacks basic intent validation**, causing it to take "garbage" or nonsensical inputs (e.g., "giant marshmallow singing opera") literally as valid HVAC repair requests. This results in the agent attempting to book services for non-existent problems, failing the Gold Standard behavior for troll/garbage handling.

### Observed Behavior (Scenario 20 v1):

```
Human: My AC has turned into a giant marshmallow and is singing opera! Help!

AI Agent (Action: chat): "Don’t worry—we’ll get that fixed! Could you share your name and address..."
```

**Result**: The agent accepted the "marshmallow" input as a legitimate repair request and proceeded to the intake phase.

### Expected Behavior (Gold Standard):

```
AI Agent: While that would certainly be a sight to see, I'm here to help with actual HVAC service and repairs. 
         If you have a legitimate issue... please let me know...
```

---

## Root Cause Analysis

### 1. **Over-Empathetic Defaults**
The agent's persona is tuned to be "Empathetic and efficient," which currently manifests as "Accept all claims as true and fix them." It lacks a "Skeptical/Validation" layer for obvious nonsense.

### 2. **Extraction Failure for Nonsense**
The `ExtractionNode` likely tried to map the input to a `service_type: "Repair"` despite the "issue" being nonsensical. The `DecideNode` then saw a "Repair" intent and moved forward with the booking flow.

### 3. **Missing "Garbage" Intent in Decider**
The `DecideNode` does not have an explicit instruction to detect "nonsensical," "inappropriate," or "non-HVAC" topics and respond with a polite but firm redirection.

---

## Proposed Solutions

### Step 1: Add Intent Validation to DecideNode
Update `decide_system.txt` with a new priority (Priority -1: Legitimacy Check):
- "Check if the input relates to actual HVAC issues (hearing, cooling, ductwork, etc.)."
- "If the input is nonsense, trolling, or completely unrelated (e.g., marshmallows, singing), pick 'chat' to politely redirect the user back to HVAC services."

### Step 2: Extraction Node Filtering
Update `extract_system.txt` to return `null` for `service_type` if the input is clearly nonsensical, rather than trying to force-fit it into a category.

---

## Heuristic Impact

| Heuristic | Expected | Current (v1) | Goal |
|:---|:---|:---|:---|
| **Professionalism** | 5/5 | 2/5 | **5/5** |
| **Logic Integrity** | 5/5 | 1/5 | **5/5** |
| **Resource Efficiency** | 5/5 | 3/5 | **5/5** (prevents booking fake techs) |

---

## Implementation Checklist

- [ ] **Prompt Hardening**: Update `decide_system.txt` with a "Legitimacy Check" priority.
- [ ] **Data Sanitization**: Update `extract_system.txt` to handle non-HVAC garbage.
- [ ] **Verification**: Re-run Scenario 20 v2 and ensure the agent redirects instead of booking.

---

## Success Criteria

### **Scenario 20 should demonstrate:**
1. **Immediate identification** of nonsense/garbage input.
2. **Polite redirection** to HVAC services as per the Gold Standard script.
3. **Escalation to closure** if the user continues nonsensical input (Action 8 in scenario).

---

## Related Documents

- **Scenario**: `data/qa/gold_e20_garbage.md`
- **Baseline**: `data/qa/multi_agent/gold_e20_garbage_multi_agent_v1.md`
- **Prompts**: `agent/prompts/`
