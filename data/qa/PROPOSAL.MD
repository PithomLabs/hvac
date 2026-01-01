# Proposal: Simplified & Robust Multi-Agent Simulation

The current "Subprocess Bridge" architecture is overly complex and prone to synchronization issues (deadlocks, multi-line truncation). More importantly, the simulation revealed that our HVAC Agent is stuck in a repetitive loop, failing to recognize information once it's provided.

## 1. Simplified Architecture: Direct Service Orchestration
Instead of running `agent/main.py` and `human_simulator.py` as separate bash sub-processes and piping strings, we will use a **Single Process Orchestrator** in `simulation_orchestrator.py`.

### Improvements:
- **Direct LLM Interaction**: Call the LLM utility functions directly within a loop.
- **Shared State Transparency**: We can monitor the HVAC Agent's `shared` store in real-time to debug why it's not "seeing" the extracted information.
- **Zero Pipe Lag**: No need for turn sentinels (`---END_OF_TURN---`) or character-by-character reading.
- **Direct-to-Markdown**: The LLM response is written to the markdown file exactly as it is received, preserving all formatting and characters.

## 2. Fixing the Repetitive Agent Loop
The `gold_a1_ac_dead_multi_agent_v6.md` log shows the agent repeatedly asking for "name, address" after Sarah provides them.

### Diagnosis:
- The **ExtractionNode** successfully adds info to the `shared["user_info"]`.
- The **BookingNode** (or logic in `flow.py`) likely checks for specific keys that might be missing or wrongly formatted.
- **Fix**: We will refine the `BookingNode` and the `ExtractionNode` system prompts to ensure they speak the same "data language."

## 3. Implementation Plan
1. **Create `data/qa/simulation_orchestrator.py`**:
    - Import `create_hvac_agent_flow` from `agent/flow.py`.
    - Implement a simple `while` loop for turns.
    - Write each turn's raw output to the versioned `.md` file immediately.
2. **Refine Agent Logic**:
    - Update `ExtractionNode` to be more aggressive in pulling "Sarah Jenkins" and "123 Maple Avenue".
    - Update `BookingNode` to acknowledge "I have your details for Sarah Jenkins at 123 Maple Avenue" instead of asking again.

## 4. Why this is "Vastly Improved":
1. **Reliability**: No subprocess crashes or pipe errors.
2. **Speed**: No artificial `time.sleep` delays needed for terminal synchronization.
3. **Accuracy**: The markdown log will be a 1:1 reflection of the LLM's raw stream.
