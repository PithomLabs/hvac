# Project Documentation: HVAC Booking Agent Evolution (v2)

This document updates the HVAC Booking Agent's progression, focusing on Transitioning from hardcoded logic to a **Prompt-Centric Architecture** and the refinement of **Natural Closure**.

## 1. Architectural Shift: Prompt Centralization

### The Challenge
In v1, system prompts were embedded directly in `agent/nodes.py`. This made logic-tuning difficult, as code changes and prompt refinements were coupled, leading to a messy development cycle.

### The Solution: `agent/prompts/`
We refactored the agent to load all primary reasoning from a centralized directory.
- **`decide_system.txt`**: Manages flow control and state-based action selection.
- **`chat_system.txt`**: Manages the agent's persona and closing handshake rules.
- **`extract_system.txt`**: Manages the structured data extraction schema.
- **`chat_examples.txt`**: Provides few-shot "Gold Standard" examples (inspired by successful v5/v6 simulations).

### Benefit
Decoupling reasoning from code allows for "Hot-Swapping" prompts. We can now tune the agent's empathy or decisiveness without a single line of Python change.

---

## 2. Perfecting the "Handshake" (Phase 2 Closure)

### The "Hallucination" Crisis (v5-v7)
Early Scenario 4 runs showed the `ChatNode` hallucinating booking confirmations before the `BookingNode` had actually processed the data. This led to "Dropped" status in simulations because the internal state didn't match the conversational output.

### The Fix: State Transparency and Handshake
We introduced a two-step confirmation protocol:
1.  **State Visibility**: The `confirmed: True` flag is now passed explicitly into the `ChatNode` context.
2.  **The Closing Spiel**: The agent is now REQUIRED to ask: *"Is there anything else I can help you with today?"*
3.  **The Handshake**: The simulation only closes (Status: PASS) if the user acknowledges they are finished.

---

## 3. Simulation Outcomes (Scenario 4 / v6)

| Metric | v1-v3 | v4-v5 | v6 (Current) |
| :--- | :--- | :--- | :--- |
| **Closure** | Partial / Dropped | Success (Hallucinated) | **Success (Verified State)** |
| **Tone** | Formal | Empathetic | **Professional + Closing Spiel** |
| **Reporting** | Manual Check | Basic PASS/FAIL | **Detailed Outcome Report** |

### Status
The agent is now highly optimized for **Speed-to-Closure** with a strict 10-turn cap, simulating real-world "drop-off" behavior while ensuring data integrity.
