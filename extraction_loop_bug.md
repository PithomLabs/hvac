# Scenario 7 - Infinite Extraction Loop Analysis

## Problem Summary
The v12 simulation succeeded in making API calls but entered an **infinite extraction loop**, repeatedly extracting data from the same user message without ever responding.

## Evidence
From debug logs:
```
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
```

**Result**: File remained at 176 bytes (only header + first human message, NO agent response written)

## Root Cause

### The Flow Design
```python
# From agent/flow.py
decide - "extract" >> extract
extract >> decide  # ← LOOPS BACK without user interaction
```

### The Execution Cycle
1. **Human says**: "I bought a Nest thermostat. Can you guys install it? How much?"
2. **DecideNode**: Sees extractable data ("install", "Nest thermostat") → decides "extract"
3. **ExtractionNode**: Processes the message, extracts service_type
4. **Flow**: Returns to DecideNode (no chat node, no new user message)
5. **DecideNode**: Sees THE SAME MESSAGE again in history → decides "extract" again
6. **Loop repeats infinitely**

###The Bug
The DecideNode prompt says (from `prompts/decide_system.txt`):

```
### DECISION PRIORITY:
1. If LAST MESSAGE has extractable data → **'extract'**
2. If all data (Name, Address, Service) present + Confirmed is No → **'book'**
```

Since the LAST MESSAGE never changes (no new user input), it ALWAYS has extractable data, so DecideNode ALWAYS chooses "extract".

## Why This Happens

### Flow Misunderstanding
The flow expects:
- After `extract`, the ExtractionNode adds data to shared store
- Then loops back to `decide`
- DecideNode should see data is now complete → choose "book" or "chat"

### But Reality
- DecideNode decision is based on "does LAST MESSAGE have extractable data?"
- The LAST MESSAGE hasn't changed, so answer is always "yes"
- Even though data was already extracted, DecideNode keeps trying to extract from the same message

## The Fix

### Option 1: Track what's been extracted (Recommended)
Add logic to DecideNode to check if extraction already happened on this message:

```python
# In DecideNode.exec(), before decision logic:
last_extraction_msg = shared.get("last_extracted_message_hash", "")
current_msg_hash = hashlib.md5(last_msg.encode()).hexdigest()

if last_extraction_msg == current_msg_hash:
    # Already extracted from this message - don't extract again
    has_extractable_data = False
else:
    # New message - check for extractable data
    has_extractable_data = check_for_extractable_data(last_msg)
```

Then in ExtractionNode.post(), save the hash:
```python
shared["last_extracted_message_hash"] = hashlib.md5(last_msg.encode()).hexdigest()
```

### Option 2: Change decision priority (Simpler)
Modify the decision priority in `prompts/decide_system.txt`:

```
### DECISION PRIORITY:
1. If all data (Name, Address, Service) present + Confirmed is No → **'book'**  ← MOVED TO TOP
2. If LAST MESSAGE has new/unextracted data → **'extract'**
3. If missing data and no new data in LAST MESSAGE → **'chat'** (ask for it)
```

This way, once data is complete, it books immediately instead of extracting again.

### Option 3: Extract should NOT loop to Decide
Change the flow so extraction triggers a response:

```python
# In flow.py
extract >> chat  # ← Changed from extract >> decide
```

After extracting, immediately ask for missing info or proceed to book.

## Recommended Solution
Use **Option 2** (simplest) combined with extraction attempt tracking (already in place).

The `decide_system.txt` already mentions `Extraction Attempts` in the prompt, so we can add:

```
### DECISION PRIORITY  (UPDATED):
1. If all data (Name, Address, Service) present + Confirmed is No → **'book'**
2. If Extraction Attempts >= 2 for same message → **'chat'** (move conversation forward)
3. If LAST MESSAGE has extractable data AND Extraction Attempts < 2 → **'extract'**
4. If missing data → **'chat'** (ask for it)
5. After Phase 2 delivery + user acknowledges → **'finish'**
```

This prevents infinite extraction AND prioritizes booking once data is ready.

## Status

- ✅ API calls working (openai/gpt-oss-20b for human, deepseek/deepseek-chat-v3.1 for agent)
- ✅ Debug logging in place
- ❌ Infinite extraction loop (flow design bug)
- ⏭️ Need to fix decision priority logic
