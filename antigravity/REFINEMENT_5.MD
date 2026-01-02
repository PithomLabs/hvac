# Refinement 5: Angry Customer Sentiment & Manager Escalation

**Date**: 2026-01-02  
**Trigger**: Scenario 16 (Angry Customer) - `gold_d16_angry.md`  
**Status**: Planning  
**Component**: Extraction Node, Decide Node, Chat Node

---

## Problem Statement

The **agent lacks specialized handling for angry customers and repeat service failures**, leading to a generic response that can feel dismissive or unhelpful in high-tension situations.

### Observed Behavior (Scenario 16 v3):

```
Human: You guys were here yesterday and it's broken again! I paid $300 and my house is still freezing! This is unacceptable!

AI Agent (Action: chat): "I'm truly sorry to hear about the ongoing issue... could you share your name and address..."
```

**Result**: While empathetic, the agent treats it as a standard new intake rather than a **critical warranty callback**. It doesn't trigger "manager escalation" or "priority tech" protocols defined in the Gold Standard.

### Expected Behavior (Gold Standard):

```
Human: You guys were here yesterday and it's broken again!

AI Agent: I am incredibly sorry... Let's get this fixed immediately at no additional cost. 
         I've flagged this for our service manager, and I'm sending a lead technician...
```

---

## Root Cause Analysis

### 1. **Sentiment Blindness**
The `ExtractionNode` does not currently extract sentiment or "callback" status, meaning the downstream `DecideNode` cannot differentiate between a routine repair and a frustrated repeat customer.

### 2. **Generic Decision Logic**
The `DecideNode` logic prioritizes data extraction over relationship management. For an angry customer, asking for "Name and Address" immediately (Action 4) can escalate frustration if not preceded by a stronger commitment to resolution.

### 3. **Missing Escalation Scripts**
The `ChatNode` uses a general persona that doesn't have explicit instructions to "Flag for Manager" or mention "Lead Technicians" when repeat issues occur.

---

## Proposed Solutions

### Step 1: Sentiment & Callback Extraction
Modify `extract_system.txt` to include `sentiment` and `is_callback` fields.

**Impact**: Enables the agent to "know" it's dealing with a high-priority/escalated situation.

### Step 2: Escalation-Aware Decision Rule
Update `decide_system.txt` to include a Priority turn for high-tension sentiment.

**Proposed Rule**:
```
If sentiment is "Angry" and Confirmed is "No", pick 'chat' even if data is missing to ensure a high-empathy commitment turn occurs first.
```

### Step 3: Manager Escalation Persona
Update `chat_system.txt` to handle the `is_callback` and `sentiment` flags by injecting specific manager-escalation scripts.

---

## Heuristic Impact

| Heuristic | Expected | Current (v3) | Goal |
|:---|:---|:---|:---|
| **Empathy & Tone** | 5/5 | 3/5 | **5/5** |
| **Escalation Accuracy** | 5/5 | 0/5 | **5/5** |
| **Customer Retention** | 5/5 | 2/5 | **5/5** |

---

## Implementation Checklist

- [ ] **Extraction Refinement**: Update `extract_system.txt` with sentiment/callback keys.
- [ ] **Decision Hardening**: Update `decide_system.txt` with escalation priority.
- [ ] **Persona Update**: Update `chat_system.txt` with manager escalation logic.
- [ ] **Node Logic**: Update `nodes.py` to pass these new flags through the flow.
- [ ] **Verification**: Run Scenario 16 v4 and verify "Flagged for Manager" script.

---

## Success Criteria

### **Scenario 16 should demonstrate:**
1. **Empathetic commitment** to "make it right" at no cost.
2. **Explicit mention** of "Service Manager" escalation.
3. **Promise** of a "Lead Technician" or priority windows.
4. **Natural closure** once the customer is reassured.

---

## Related Documents

- **Scenario**: `data/qa/gold_d16_angry.md`
- **Baseline**: `data/qa/multi_agent/gold_d16_angry_multi_agent_v3.md`
- **Prompts**: `agent/prompts/`
