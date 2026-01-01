# Refinement 3: DecideNode Extraction Loop \u0026 Message-Based Decision Logic

**Date**: 2026-01-02  
**Trigger**: Scenario 7 (Thermostat Installation) - Dry Run v10-v12  
**Status**: Identified, awaiting implementation  
**Dependency**: Blocks all scenario testing

---

## Problem Statement

The **DecideNode enters an infinite extraction loop**, repeatedly deciding "extract" on the same user message without ever progressing to chat or book actions, causing simulations to hang indefinitely with no agent response.

### Observed Behavior (Scenario 7 v12):

```
Debug Output:
[DEBUG] DecideNode calling LLM (model=deepseek/deepseek-chat-v3.1)
[DEBUG] DecideNode LLM returned
[DEBUG] DecideNode decided: extract
[DEBUG] DecideNode calling LLM (model=deepseek/deepseek-chat-v3.1)
[DEBUG] DecideNode LLM returned
[DEBUG] DecideNode decided: extract
[DEBUG] DecideNode calling LLM (model=deepseek/deepseek-chat-v3.1)
[DEBUG] DecideNode LLM returned
[DEBUG] DecideNode decided: extract
... (repeated 10+ times)

File Output (gold_b7_thermostat_multi_agent_v12.md):
# Multi-Agent Conversation Simulation (Single-Process)

**Scenario**: data/qa/gold_b7_thermostat.md

**Human**: I bought a Nest thermostat. Can you guys install it? How much?

[NO AGENT RESPONSE - file stuck at 176 bytes]
```

### Expected Behavior:

```
Turn 1:
Human: I bought a Nest thermostat. Can you guys install it? How much?
AI Agent (Action: extract): [Extracts Service: "Maintenance"]

Turn 2:
AI Agent (Action: chat): We can install your Nest thermostat! The installation is $129...
```

---

## Root Cause Analysis

### 1. **Flow Creates Infinite Loop**

**Current Flow** (`agent/flow.py`):
```python
decide - "extract" >> extract
extract >> decide  # ← LOOPS BACK without user interaction
```

**Execution Cycle:**
1. **Human says**: "I bought a Nest thermostat. Can you guys install it? How much?"
2. **DecideNode**: Sees extractable data ("install", "Nest") → decides **"extract"**
3. **ExtractionNode**: Processes message, extracts `service_type: "Maintenance"`
4. **Flow**: Returns to DecideNode (via `extract >> decide`)
5. **DecideNode**: Sees THE SAME MESSAGE again in history → decides **"extract"** again
6. **Loop repeats infinitely** - no new user message, no chat response, no progress

### 2. **Decision Logic Based on Message Content, Not Extraction State**

**Current Decision Priority** (`prompts/decide_system.txt`):
```
### DECISION PRIORITY:
1. If LAST MESSAGE has extractable data → **'extract'**
2. If all data (Name, Address, Service) present + Confirmed is No → **'book'**
```

**Problem**: The LAST MESSAGE never changes between extraction cycles, so:
- DecideNode sees "I bought a Nest thermostat. Can you guys install it?"
- Checks for extractable keywords → **ALWAYS TRUE** 
- Decides "extract" → **EVERY TIME**

### 3. **No Tracking of Extraction History**

The DecideNode has no awareness of:
- Which messages have already been extracted
- How many extraction attempts on the current message
- Whether extraction succeeded or failed

**Evidence** (`agent/nodes.py` DecideNode.exec): 
```python
last_msg = history[-1]["content"] if history else ""

# No hash/tracking of previously extracted messages
# No check if extraction already ran on this message
```

---

## Heuristic Impact

| Heuristic | Expected | Actual (v12) | Impact |
|:---|:---|:---|:---|
| **ABC (Always Be Closing)** | 5/5 (booking achieved) | **0/5** (stuck before first response) | ❌ CRITICAL |
| **Customer Experience** | 5/5 | **0/5** (no response delivered) | ❌ CRITICAL |
| **Phase 2 Handshake** | 5/5 | **0/5** (never reached) | ❌ |

**Overall**: Simulation **completely fails** - no conversation occurs.

---

## API Call Analysis (Pre-requisite Finding)

### v10-v11: API Timeout Issue
- **Problem**: Simulation hung for 5+ minutes on first API call
- **Cause**: Free-tier models (`nvidia/nemotron-nano-9b-v2:free`, `deepseek/deepseek-chat-v3.1`) hitting rate limits
- **Fix**: Switched human simulator to `openai/gpt-oss-20b`

### v12: API Working, Logic Broken
- ✅ DeepSeek API responding quickly (~1-2 seconds per call)
- ✅ Debug logging confirms LLM returns valid decisions
- ❌ Decision logic creates infinite loop (not API issue)

---

## Proposed Solution

### **Option 1: Track Extracted Messages (Recommended for Long-term)**

Track which messages have been extracted to prevent re-extraction.

**File**: `agent/nodes.py` (DecideNode.exec)

**Add before decision logic:**
```python
import hashlib

last_msg = history[-1]["content"] if history else ""
last_extraction_msg = shared.get("last_extracted_message_hash", "")
current_msg_hash = hashlib.md5(last_msg.encode()).hexdigest()

# Check if we already extracted from this message
already_extracted = (last_extraction_msg == current_msg_hash)
```

**File**: `agent/nodes.py` (ExtractionNode.post)

**Add after extraction:**
```python
# Mark this message as extracted
import hashlib
last_msg = shared["history"][-1]["content"] if shared["history"] else ""
shared["last_extracted_message_hash"] = hashlib.md5(last_msg.encode()).hexdigest()
```

**Update**: `prompts/decide_system.txt`
```
### EXTRACTION TRIGGER:
Pick 'extract' if:
- LAST MESSAGE contains extractable data (service keywords, personal info)
- AND this message has NOT been extracted yet (check extraction attempts)
- AND extraction attempts < 2 for this message
```

---

### **Option 2: Reorder Decision Priority (Simpler, Immediate Fix)**

Prioritize booking over extraction when data is complete.

**File**: `prompts/decide_system.txt`

**Current:**
```
### DECISION PRIORITY:
1. If LAST MESSAGE has extractable data → **'extract'**
2. If all data (Name, Address, Service) present + Confirmed is No → **'book'**
```

**Proposed:**
```
### DECISION PRIORITY:
1. If all data (Name, Address, Service) present + Confirmed is No → **'book'**
2. If Extraction Attempts >= 2 for same message → **'chat'** (stop extracting, move forward)
3. If LAST MESSAGE has extractable data AND Extraction Attempts < 2 → **'extract'**
4. If missing data and no new data in LAST MESSAGE → **'chat'** (ask for it)
5. After Phase 2 delivery + user acknowledges → **'finish'**
```

**Rationale**:
- Booking has highest priority (prevents infinite extraction when data is ready)
- Extraction attempts counter prevents loops (already exists in shared store)
- Falls back to chat after 2 failed extractions (moves conversation forward)

---

### **Option 3: Change Flow Routing**

Route extraction directly to chat instead of back to decide.

**File**: `agent/flow.py`

**Current:**
```python
extract >> decide  # ← Creates loop
```

**Proposed:**
```python
extract >> chat  # After extraction, respond to user
```

**Issue**: This breaks the design pattern where DecideNode controls all routing.

---

## Recommended Approach

**Implement Option 2** (simplest and fastest):
1. Update `prompts/decide_system.txt` with new decision priority
2. Leverage existing `extraction_attempts` counter in shared store
3. No code changes needed, only prompt refinement

**Then add Option 1** (long-term):
- Implement message hash tracking for robustness
- Prevents edge cases where same info appears in multiple messages

---

## Implementation Checklist

- [ ] **Version prompts** (backup current decide_system.txt)
- [ ] **Update `agent/prompts/decide_system.txt`**: Reorder decision priority
- [ ] **Add extraction attempt guard**: Max 2 attempts per message
- [ ] **Re-run Scenario 7 (v13)**: Verify extraction happens once, then moves to chat/book
- [ ] **Verify no loops**: Confirm file progresses beyond 176 bytes
- [ ] **Heuristic Check**: Ensure conversation reaches natural closure

---

## Success Criteria

### **Scenario 7 (Thermostat Installation) v13 should show:**

```
Turn 1:
Human: I bought a Nest thermostat. Can you guys install it? How much?
AI Agent (Action: extract): [Extracts Service: "Maintenance", attempts=1]

Turn 2:
AI Agent (Action: chat): We can install your Nest thermostat! The installation is $129. 
May I have your name and address?

Turn 3:
Human: Cosmo Kramer, 129 West 81st St.
AI Agent (Action: extract): [Extracts Name and Address, attempts=2]

Turn 4:
AI Agent (Action: book): [SYSTEM] Booking confirmed for Cosmo Kramer on 2026-01-03 14:00.

Turn 5:
AI Agent (Action: chat): Success! You're all set for your Maintenance visit. 
Your booking confirmation number is: HB-4721. Have a great day! 
Is there anything else I can help you with today?

Turn 6:
Human: No thanks.

Turn 7:
AI Agent (Action: finish): *END OF CONVERSATION*
```

### **Debug Output Should Show:**
```
[DEBUG] DecideNode decided: extract  ← Only once per message
[DEBUG] DecideNode decided: chat     ← Progresses to response
[DEBUG] DecideNode decided: extract  ← On new user message
[DEBUG] DecideNode decided: book     ← When data complete
[DEBUG] DecideNode decided: chat     ← Phase 2 delivery
[DEBUG] DecideNode decided: finish   ← Clean exit
```

### **File Output:**
- File size > 176 bytes (agent responses written)
- Conversation reaches natural closure
- No infinite loops

---

## Related Documents

- **Diagnostic Report**: `.gemini/antigravity/brain/.../scenario7_diagnostic.md`
- **Extraction Loop Analysis**: `.gemini/antigravity/brain/.../extraction_loop_bug.md`
- **Blocking**: REFINEMENT_1, REFINEMENT_2 (cannot verify until loop is fixed)
- **Heuristic Framework**: `HEURISTIC_RANKING.MD`
- **Test Scenario**: `data/qa/gold_b7_thermostat.md`
- **Failed Runs**: 
  - `data/qa/multi_agent/gold_b7_thermostat_multi_agent_v10.md` (API timeout)
  - `data/qa/multi_agent/gold_b7_thermostat_multi_agent_v11.md` (API timeout)
  - `data/qa/multi_agent/gold_b7_thermostat_multi_agent_v12.md` (infinite extraction loop)

---

## Critical Path

This refinement is **BLOCKING ALL SCENARIO TESTING**. Without fixing the extraction loop:
1. DecideNode cycles infinitely on first extractable message
2. No agent responses are ever written to file
3. Simulations appear to hang indefinitely
4. Cannot verify any previous refinements (0, 1, 2)

**Priority**: **CRITICAL** - Must fix immediately before any further testing.

---

## Notes

**Post-v12 Discovery**: The API calls are working correctly (1-2 second response times), but the decision logic creates an architectural issue. This demonstrates the importance of:
1. **Message-based state tracking** (not just shared data tracking)
2. **Extraction attempt limiting** (prevent infinite loops)
3. **Priority ordering** (booking should override extraction when data is ready)

The fix is prompt-only (no code changes), making it low-risk and fast to implement.
