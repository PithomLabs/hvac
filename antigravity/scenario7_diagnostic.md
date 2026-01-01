# Scenario 7 Dry Run Failure - Diagnostic Report

## Summary
The Scenario 7 (thermostat installation) simulation process **hung at the very first agent turn** and never progressed beyond writing the initial human message to the output file.

## Root Cause Analysis

### Primary Issue: API Call Hang/Failure
The simulation got stuck on the **very first LLM API call** in the `DecideNode.exec()` method.

**Location**: `agent/nodes.py`, line ~57
```python
response = call_llm(prompt)  # ← HUNG HERE
```

**Evidence**:
- Output file `gold_b7_thermostat_multi_agent_v10.md` only contains the header and first human message (176 bytes)
- No agent response was ever written
- Process ID 27825 ran for 5+ minutes without progress
- File modification time stuck at 00:29:20

### Contributing Factors

#### 1. **Free Model Rate Limiting**
The simulation uses FREE tier models that are prone to rate limits:

**Agent Model**: `deepseek/deepseek-chat-v3.1`
- Set in `simulation_orchestrator.py` lines 113, 142
- Previous run (v9) showed repeated 429 errors from OpenRouter

**Human Simulator Model**: `nvidia/nemotron-nano-9b-v2:free`
- Set in `simulation_orchestrator.py` line 80  
- Also hit rate limits in v9

**Evidence from v9**:
```
Error: OpenRouter API error: 429 - {"error":{"message":"Provider returned error","code":429,...
Error: OpenRouter API error: 429 - {"error":{"message":"Rate limit exceeded: free-models-per-min."...
```

#### 2. **Timeout Configuration**
In `utils/call_llm.py` line 45:
```python
with urllib.request.urlopen(req, timeout=30) as response:
```

The 30-second timeout with 3 retries (max_retries=3) means:
- If API is slow/unresponsive → wait 30s, retry with backoff (2^0=1s, 2^1=2s, 2^2=4s)
- Total possible wait time: ~120+ seconds before final failure
- But v10 hung for 300+ seconds (5+ minutes), suggesting the exception wasn't even raised

#### 3. **Infinite Booking Loop (Secondary Issue)**
In v7, after the agent DID respond, it entered an infinite booking loop:
- Lines 15, 22, 29, 36: Agent kept booking the same appointment repeatedly
- The conversation never properly closed
- This is a **logic issue** in the DecideNode/BookingNode, separate from the API hang

**Root Cause**: Agent incorrectly books repeatedly instead of recognizing the booking is already confirmed and transitioning to "finish" action.

## Findings from Previous Runs

### v7 - Booking Loop
- Got past initial API call
- Agent booked 4+ times in a row without finishing
- Each turn: `(Action: book): [SYSTEM] Booking confirmed for Sarah Jenkins on 2026-01-03 14:00.`
- Human kept asking about technician experience but agent ignored and kept re-booking

### v8 - Early Termination
- Only 176 bytes (same as v10) - likely same API hang

### v9 - Rate Limit Hell
- Made some progress initially
- Hit cascading 429 errors from both Google Gemini and rate-limit-per-min quotas
- Human simulator started outputting meta-commentary instead of in-character responses
  - Example: `"Sarah, you're asking about hidden fees..."` (should just be Sarah speaking naturally)

### v10 - Complete Hang
- Process started at 00:29:20
- Never wrote anything beyond initial human message
- Killed at 00:34:26 (5+ minutes stuck)

## Recommended Fixes

### Immediate Actions

1. **Switch to Paid/Reliable Models**
   ```python
   # In simulation_orchestrator.py
   # Agent (line 113, 142):
   os.environ["LLM_MODEL"] = "openai/gpt-4o-mini"  # or anthropic/claude-3-5-haiku
   
   # Human simulator (line 80):
   os.environ["LLM_MODEL"] = "openai/gpt-4o-mini"
   ```

2. **Add Timeout Logging**
   ```python
   # In utils/call_llm.py, add logging before API call:
   import logging
   logging.info(f"Calling {model} with prompt length {len(str(messages))}")
   ```

3. **Fix Booking Loop Logic**
   - Review `DecideNode.exec()` decision priority rules
   - Ensure "finish" action is triggered when booking is already confirmed
   - Add check: if `booking_confirmed == True` and last action was "book", return `{"action": "finish"}`

4. **Add Better Error Handling**
   ```python
   # In DecideNode.exec(), current code swallows exceptions silently
   except Exception as e:
       pass  # ← BAD: silently returns "chat" action
       return {"action": "chat", "reasoning": f"Error: {e}"}
   
   # Should be:
   except Exception as e:
       logging.error(f"DecideNode LLM call failed: {e}")
       raise  # Let PocketFlow's retry mechanism handle it
   ```

### Long-term Improvements

1. **Circuit Breaker Pattern**: If API fails N times in a row, switch to fallback model
2. **Exponential Backoff**: Increase retry delays for 429 errors (already partially implemented)
3. **Model Health Check**: Test API availability before starting simulation
4. **Progress Checkpoints**: Save state after each turn so simulation can resume on failure

## Next Steps

1. ✅ Stop stuck process (DONE)
2. ✅ Document findings (DONE)
3. ⏭️ Switch to reliable models in `simulation_orchestrator.py`
4. ⏭️ Fix booking loop logic in `DecideNode`
5. ⏭️ Re-run scenario 7 dry run
6. ⏭️ Verify conversation reaches natural closure in 5-7 turns
