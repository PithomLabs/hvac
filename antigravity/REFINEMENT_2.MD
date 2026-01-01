# Refinement 2: ExtractionNode Trigger Logic & Service Inference

**Date**: 2026-01-01  
**Trigger**: Scenario 7 (Thermostat Installation) - `gold_b7_thermostat_multi_agent_v3.md`  
**Status**: Identified, awaiting implementation  
**Dependency**: Blocks REFINEMENT_1 verification

---

## Problem Statement

The **ExtractionNode is never triggered** even when the user clearly provides service-related information, causing the booking flow to stall indefinitely. The DecideNode keeps selecting 'chat' instead of 'extract' or 'book', resulting in conversations that never reach booking confirmation.

### Observed Behavior (Scenario 7 v3):

```
Turn 1:
Human: I bought a Nest thermostat. Can you guys install it? How much?
AI Agent (Action: chat): [asks for name and address]
→ Service should be extracted as "Maintenance" but wasn't

All subsequent turns:
AI Agent (Action: chat): [keeps chatting]
→ Service remains "Missing"
→ BookingNode never executes
→ No Phase 2 handshake delivered
```

### Expected Behavior:

```
Turn 1:
Human: I bought a Nest thermostat. Can you guys install it?
AI Agent (Action: extract): [Service extracted as "Maintenance/Installation"]

Turn 2:
AI Agent (Action: chat): [asks for Name and Address]

Turn 3:
Human: [provides Name and Address]
AI Agent (Action: extract): [Name and Address extracted]

Turn 4:
AI Agent (Action: book): [SYSTEM] Booking confirmed...

Turn 5:
AI Agent (Action: chat): Success! HB-XXXX. Have a great day! Is there anything else?
```

---

## Root Cause Analysis

### 1. **Implicit Service Information Not Recognized**

**Problem**: The DecideNode doesn't recognize that "I bought a Nest thermostat. Can you guys install it?" contains **implicit service information**.

**Current DecideNode Logic (v12):**
```
1. 'extract': Use this if the user just provided a missing field.
```

**Issue**: This is too narrow. The user didn't explicitly say "I need installation service" but the intent is clear from context:
- "Can you guys install it?" = Installation request
- "Nest thermostat" = Type of installation

### 2. **ExtractionNode Mapping Incomplete**

**File**: `agent/prompts/extract_system.txt` (v12)

**Current SERVICE MAPPING:**
```
- If user mentions "spring cleaning", "tune-up", "check-up", "filter change", 
  "installation", or "setup", set service_type to "Maintenance".
```

**Problem**: The user said "install it" but the extraction prompt looks for specific keywords like "installation" or "setup". The variation "install" may not be caught.

### 3. **DecideNode Overly Favors 'chat'**

**Current Decision Priority (v12):**
```
1. If all data is present and Booking Confirmed is No → 'book'
2. After booking succeeds (Confirmed: Yes) → 'chat' (for Phase 2 delivery)
3. After Phase 2 delivery and user acknowledges → 'finish'
```

**Missing Rule**: When to pick 'extract' over 'chat'.

The DecideNode has no explicit logic for:
- "If the user's message contains service-related keywords, pick 'extract'"
- "If the user provides partial booking data, pick 'extract'"

---

## Heuristic Impact

| Heuristic | Expected | Actual (v3) | Impact |
|:---|:---|:---|:---|
| **ABC (Always Be Closing)** | 5/5 (booking achieved) | **1/5** (no booking) | ❌ CRITICAL |
| **Customer Experience** | 5/5 | **2/5** (repetitive questioning) | ❌ |
| **Phase 2 Handshake** | 5/5 (HB-XXXX delivered) | **0/5** (never reached Phase 2) | ❌ |

**Overall**: The conversation **failed to achieve its primary goal** (booking).

---

## Proposed Solution

### **Step 1: Enhance DecideNode with Extraction Priority**

**File**: `agent/prompts/decide_system.txt`

**Add EXTRACTION TRIGGER RULE:**
```
### EXTRACTION TRIGGER:
- Pick 'extract' if the LAST MESSAGE contains:
  - Service keywords: "install", "repair", "fix", "tune-up", "maintenance", "check", "replace"
  - Personal info: name, address, phone number, email
  - Urgency indicators: "urgent", "emergency", "ASAP", "broken", "dead"
- Even if the wording is informal, if booking-related info is present, use 'extract'.

### DECISION PRIORITY (UPDATED):
1. If LAST MESSAGE has extractable data → 'extract'
2. If all data (Name, Address, Service) is present and Confirmed is No → 'book'
3. After booking succeeds (Confirmed: Yes) → 'chat' (for Phase 2)
4. If data is missing and no new data in LAST MESSAGE → 'chat' (to ask for it)
5. After Phase 2 delivery and user acknowledges → 'finish'
```

---

### **Step 2: Expand ExtractionNode Service Mapping**

**File**: `agent/prompts/extract_system.txt`

**Current:**
```python
SERVICE MAPPING:
- If user mentions "spring cleaning", "tune-up", "check-up", "filter change", 
  "installation", or "setup", set service_type to "Maintenance".
- If user mentions "broken", "dead", "not working", "leak", or "noise", 
  set service_type to "Repair".
```

**Proposed (Add Variations):**
```python
SERVICE MAPPING:
- MAINTENANCE: "install", "installation", "setup", "set up", "tune-up", 
  "tune up", "check-up", "check up", "maintenance", "filter change", 
  "spring cleaning", "winterize", "annual service"
  
- REPAIR: "broken", "dead", "not working", "won't turn on", "leak", 
  "leaking", "noise", "noisy", "smell", "smells", "frozen", "freezing"
  
- If the user asks "Can you install?" or "Do you install?" → Maintenance
- If the user says "I bought [device]" + "install" → Maintenance
```

---

### **Step 3: Add Contextual Service Inference**

**Enhancement Concept**: If the user asks "Can you install my Nest thermostat?", the ExtractionNode should infer:
- **service_type**: "Maintenance"
- **issue**: "Nest thermostat installation"

**Add to `extract_system.txt`:**
```
CONTEXTUAL INFERENCE:
- If user mentions a device (e.g., "Nest thermostat", "new AC unit") followed by 
  "install", "setup", or "Can you install?", set:
  - service_type: "Maintenance"
  - issue: "[Device] installation"
```

---

## Implementation Checklist

- [ ] **Version prompts** (run `python3 agent/prompts/version_prompts.py`)
- [ ] **Update `agent/prompts/decide_system.txt`**: Add extraction trigger rule and priority
- [ ] **Update `agent/prompts/extract_system.txt`**: Expand service keyword mapping
- [ ] **Re-run Scenario 7 (v4)**: Verify extraction happens on Turn 1
- [ ] **Verify REFINEMENT_1**: Ensure Phase 2 handshake is delivered after successful booking
- [ ] **Heuristic Check**: Confirm ABC = 5/5, Phase 2 = 5/5

---

## Success Criteria

### **Scenario 7 (Thermostat Installation) v4 should show:**

```
Turn 1:
Human: I bought a Nest thermostat. Can you guys install it? How much?
AI Agent (Action: extract): [Extracts Service: "Maintenance", Issue: "Nest installation"]

Turn 2:
AI Agent (Action: chat): I can help with that! The installation is $119. 
May I have your name and address?

Turn 3:
Human: Sarah Jenkins, 345 Cedar Avenue, Denver, CO 80202.
AI Agent (Action: extract): [Extracts Name and Address]

Turn 4:
AI Agent (Action: book): [SYSTEM] Booking confirmed for Sarah Jenkins on 2026-01-02 14:00.

Turn 5:
AI Agent (Action: chat): Success! You're all set for your Maintenance visit. 
Your booking confirmation number is: HB-4721. Have a great day! 
Is there anything else I can help you with today?

Turn 6:
Human: No thanks.

Turn 7:
AI Agent (Action: finish): Have a great day! *END OF CONVERSATION*
```

### **Heuristic Scores (Target):**
- ABC (Always Be Closing): 5/5 ✅
- Customer Experience: 5/5 ✅
- Phase 2 Handshake: 5/5 ✅ (HB-XXXX + spiel delivered)

---

## Related Documents

- **Blocking**: REFINEMENT_1 (Silent BookingNode) - cannot verify until extraction works
- **Heuristic Framework**: `HEURISTIC_RANKING.MD`
- **Prompt Versions**: 
  - Current: `agent/prompts/*_v12.txt`
  - Next: `agent/prompts/*_v13.txt` (after this refinement)
- **Test Scenario**: `data/qa/gold_b7_thermostat.md`
- **Failed Run**: `data/qa/multi_agent/gold_b7_thermostat_multi_agent_v3.md`

---

## Critical Path

This refinement is **BLOCKING** all booking scenarios. Without proper extraction:
1. Service field stays "Missing"
2. BookingNode never executes
3. Phase 2 handshake never triggers
4. Conversations loop indefinitely or exit prematurely

**Priority**: HIGH - Must fix before continuing with other scenarios.
