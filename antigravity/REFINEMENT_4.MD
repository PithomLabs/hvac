# Refinement 4: Human Simulator Identity Consistency

**Date**: 2026-01-02  
**Trigger**: Scenario 9 (Reschedule) - `gold_c9_reschedule_multi_agent_v1.md`  
**Status**: Option 2 tested - Issue persists, implementing Option 1  
**Component**: Simulation Orchestrator (Human Simulator)

---

## Problem Statement

The **human simulator breaks character and contradicts its own identity** mid-conversation, causing context leaks that confuse the conversation flow.

### Observed Behavior (Scenario 9 v1):

```
Turn 1:
Human: I have a tech coming Tuesday, but I have to work. Can we do Friday instead? 
       My name is Jerry Seinfeld.

Turn 2:
AI Agent: Great, Jerry! To set up your maintenance visit for Friday...
[Agent books for Jerry Seinfeld]

Turn 3:
Human: Wait, who is Jerry Seinfeld? My name is Sarah Jenkins. 
       My address is 456 Oak Avenue, Springfield, IL 62701.
```

**Result**: Human simulator contradicts itself, claiming to be a different person than originally stated.

### Expected Behavior:

```
Turn 1:
Human: My name is Jerry Seinfeld.

Turn 3:
Human: [Provides address consistently as Jerry Seinfeld]
       My address is 129 West 81st St.
```

---

## Root Cause Analysis

### 1. **No Identity Locking**

**Current Code** (`data/qa/simulation_orchestrator.py`, `run_human_simulator`):

```python
# Lines 47-55
if not human_intent:
    # Fallback: look for specific name/address in the scenario text
    name_match = re.search(r'name is ([\\w\\s]+)', scenario_content, re.IGNORECASE)
    addr_match = re.search(r'at ([\\w\\s,]+)', scenario_content, re.IGNORECASE)
    name = name_match.group(1).strip() if name_match else "Sarah Jenkins"  # ← Fallback
    addr = addr_match.group(1).strip() if addr_match else "123 Main St"
    human_intent = f"You are {name} living at {addr}."
```

**Problem**: 
- Extracts name from scenario each time (can change if scenario has multiple names)
- Uses hardcoded fallback "Sarah Jenkins"
- No persistence of identity across turns

### 2. **Weak Identity Constraints in System Prompt**

**Current Prompt** (lines 62-73):

```python
system_prompt = f"""
You are {human_name}, a REAL customer needing HVAC help.
STRICT RULES:
1. NEVER say "I am an AI". Act 100% human.
2. Respond ONLY with what you would say to the agent.
3. NEVER prefix your response with ANY name or role (e.g., no "{human_name}:").
4. NEVER role-play OR describe what you are doing. Just SPEAK.
...
"""
```

**Missing**:
- No explicit rule preventing identity contradictions
- No reminder that identity was already established
- No validation of consistency

### 3. **LLM Confabulation**

The LLM (xiaomi/mimo-v2-flash:free) may:
- Second-guess the name it provided earlier
- See "Sarah Jenkins" in context (from fallback code) and switch
- Generate "natural-sounding" confusion questions like "Wait, who is Jerry Seinfeld?"

---

## Proposed Solutions

### Option 1: Lock in Identity from First Turn

**File**: `data/qa/simulation_orchestrator.py`

**Add identity tracking to shared store:**
```python
def run_orchestration(scenario_file):
    # ... existing init code ...
    
    shared = {
        "history": [], "user_info": {}, "booking_info": {},
        "current_action": None, "last_response": "", "extraction_attempts": 0,
        "human_identity": None  # ← NEW: Lock identity
    }
    
    # Extract and lock name from first human message
    first_human_match = re.search(r'\\*\\*Human\\*\\*:\\s*(.*)', scenario_content)
    first_msg = first_human_match.group(1).strip() if first_human_match else "Hi, I need help."
    
    name_match = re.search(r'[Mm]y name is ([\\w\\s]+)', first_msg)
    if name_match:
        shared["human_identity"] = name_match.group(1).strip()
```

**Pass locked identity to simulator:**
```python
def run_human_simulator(history, scenario_content, force_continue=False, locked_identity=None):
    """Simulates the human side directly using LLM call."""
    
    # Use locked identity if provided
    if locked_identity:
        human_name = locked_identity
    else:
        # ... existing fallback logic ...
```

**Rationale**: Identity is extracted once from gold standard and never changes.

---

### Option 2: Strengthen System Prompt (Simpler)

**File**: `data/qa/simulation_orchestrator.py` (lines 62-73)

**Add explicit identity rules:**
```python
system_prompt = f"""
You are {human_name}, a REAL customer needing HVAC help.

CRITICAL IDENTITY RULES:
- Your name is {human_name}. This is FIXED and UNCHANGEABLE.
- You already introduced yourself as {human_name} in your first message.
- NEVER question who {human_name} is or claim to be someone else.
- NEVER say things like "Wait, who is {human_name}?" or "My name is [different name]".
- Stay 100% in character as {human_name} throughout the entire conversation.

STRICT RULES:
1. NEVER say "I am an AI". Act 100% human.
2. Respond ONLY with what you would say to the agent.
3. NEVER prefix your response with ANY name or role.
4. NEVER role-play OR describe what you are doing. Just SPEAK.
5. You are NOT an expert. You are just a stressed customer.
6. Respond in SHORT, natural sentences.
7. If asked for information, PROVIDE IT CONSISTENTLY with your identity as {human_name}.
8. If the agent confirmed your booking and you are satisfied, say thanks/goodbye and add [FINISHED].
"""
```

**Rationale**: Direct instruction to LLM to maintain consistency.

---

### Option 3: Post-Processing Validation (Belt and Suspenders)

**File**: `data/qa/simulation_orchestrator.py`

**Add validation after LLM response:**
```python
def run_human_simulator(history, scenario_content, force_continue=False, locked_identity=None):
    # ... existing code to get response ...
    
    response = call_llm(prompt, system_prompt=system_prompt).strip()
    
    # Validate no identity contradiction
    if locked_identity:
        # Check if response claims a different name
        other_name_match = re.search(r'[Mm]y name is ([\\w\\s]+)', response)
        if other_name_match and other_name_match.group(1).strip() != locked_identity:
            print(f"{YELLOW}[WARN] Identity contradiction detected: {other_name_match.group(1)} != {locked_identity}. Retrying...{RESET}")
            
            # Retry with stronger reminder
            system_prompt += f"\n\nREMINDER: You are {locked_identity}. Do NOT claim to be anyone else!"
            response = call_llm(prompt, system_prompt=system_prompt).strip()
    
    return response
```

**Rationale**: Catches and corrects identity contradictions automatically.

---

## Heuristic Impact

| Heuristic | Expected | Actual (v1) | Impact |
|:---|:---|:---|:---|
| **Customer Experience** | 5/5 | **2/5** (confusing identity flip) | ❌ |
| **Conversation Coherence** | N/A | **1/5** (breaks character) | ❌ |

**Note**: This is a **simulation quality** issue, not an agent bug. However, it pollutes test results and makes it hard to verify agent behavior.

---

## Implementation Checklist

- [ ] **Choose approach**: Option 1, 2, or 3 (or combination)
- [ ] **Update `simulation_orchestrator.py`**: Implement chosen fix
- [ ] **Re-run Scenario 9 (v2)**: Verify identity stays consistent
- [ ] **Test with Scenarios 7-8**: Ensure no regression
- [ ] **Document**: Update this file with FIXED status

---

## Success Criteria

### **Scenario 9 (Reschedule) v2 should show:**

```
Turn 1:
Human: I have a tech coming Tuesday, but I have to work. Can we do Friday instead? 
       My name is Jerry Seinfeld.

Turn 2:
AI Agent: Great, Jerry! [asks for address]

Turn 3:
Human: [Provides address consistently as Jerry Seinfeld]
       129 West 81st St. [Continues conversation in character]
       
Turn 4-8:
Human: [Maintains Jerry Seinfeld identity throughout]
```

**No identity contradictions or context leaks.**

---

## Verification Results (Option 2)

### Implementation
**File**: `data/qa/simulation_orchestrator.py` (lines 62-81)  
**Change**: Added CRITICAL IDENTITY RULES to system prompt

### Test: Scenario 9 v2

**Result**: ❌ **Identity leak STILL occurred**

```
Turn 1:
Human: My name is Jerry Seinfeld.

Turn 3:
Human: Oh, I think there might be some confusion. My name is Sarah Jenkins, not Jerry Seinfeld.
```

**Analysis**:
- Strengthened prompt reduced severity (6 turns vs 8 turns in v1)
- LLM (xiaomi/mimo-v2-flash:free) still contradicted identity despite explicit rules
- Prompt-only approach insufficient for this model

**Conclusion**: Option 2 alone is **NOT sufficient**. Proceeding with Option 1 (Lock in Identity).

---

## Recommended Approach

**Start with Option 2** (Strengthen System Prompt):
- ✅ Simplest to implement (single prompt change)
- ✅ No new state tracking needed
- ✅ Addresses root cause directly

**If insufficient, add Option 1** (Lock Identity):
- Bulletproof consistency via state tracking
- Extracted once from gold standard

**Option 3** only if persistent issues remain after Options 1+2.

---

## Related Issues

This issue is separate from agent logic bugs (REFINEMENT_1-3). It affects:
- **Simulation quality**: Makes it hard to verify agent behavior
- **Test validity**: Identity leaks pollute conversation logs
- **Future scenarios**: Any scenario with named customers at risk

**Priority**: MEDIUM - Doesn't block agent development but reduces test reliability.

---

## Related Documents

- **Test Scenario**: `data/qa/gold_c9_reschedule.md`
- **Failed Run**: `data/qa/multi_agent/gold_c9_reschedule_multi_agent_v1.md`
- **Simulation Code**: `data/qa/simulation_orchestrator.py` (run_human_simulator)
