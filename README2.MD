# Project Documentation: Evolution of Prompt Strategy (v1)

This document provides a detailed account of how the prompts for both the AI Agent and the Human Simulator were iteratively enhanced to achieve high-fidelity conversation logs.

## 1. Phase 1: The AI Agent's Foundation

The initial prompt strategy for the HVAC Agent focused on **modularization** via the PocketFlow framework.

### The "Manager" (DecideNode)
- **Strategy**: Explicit JSON formatting and strict state-based rules.
- **Goal**: Prevent the agent from getting ahead of itself (e.g., trying to book before it has a name).
- **Key Prompt Element**: 
  > "If Name or Address is 'Missing', you cannot 'book'."
- **Rationale**: By enforcing constraints at the "manager" level, the "worker" nodes (Chat/Extract) can focus on their specific tasks without worrying about broader flow control.

### The "Communicator" (ChatNode)
- **Strategy**: Persona-driven response generation.
- **Rationale**: HVAC issues are often high-stress (e.g., no heat in winter). A purely technical agent feels cold; an overly chatty one feels inefficient.
- **Key Prompt Element**: 
  > "Persona: Empathetic, professional, and efficient. No fluff, just direct help."

---

## 2. Phase 2: Solving Human Simulation Artifacts

When we introduced the Multi-Agent Simulation, our biggest challenge wasn't the agent, but the **Human Simulator**.

### The "Role-Play" Crisis (v1 - v2)
- **Symptom**: The Human Simulator would prefix its lines with `Human:` or `Sarah Jenkins:`.
- **Diagnosis**: The LLM was treating the simulation like a screenplay script rather than a live chat.
- **Refinement**: 
  - **Negative Constraint**: "NEVER prefix your response with ANY name or role."
  - **Contextual Anchoring**: "Respond ONLY with what you would say... Just SPEAK."

### The "Infinite Promise" Loop (v3 - v4)
- **Symptom**: The agent would ask for a ZIP code, and the human would respond: "Sure, let me find that ZIP code for you and pick a time." (But never provided the data).
- **Diagnosis**: The simulator was being *too* helpful in spirit but *useless* in data provision. It was describing its intent to help rather than helping.
- **Refinement**:
  - **Imperative Action**: "If asked for info (Zip, Name, Address), PROVIDE IT IMMEDIATELY. Do NOT say 'I will provide it'. Make it up if you don't have it."

---

## 3. Phase 3: Perfecting Closure (v5)

### The "Abrupt End" Issue
- **Symptom**: As soon as the human provided the last bit of info, they would say "Thanks [FINISHED]", and the simulation script would exit.
- **Effect**: The agent never got to say "I've booked you for tomorrow at 3 PM," leaving the simulation log incomplete.
- **Solution**: 
  - **Process-Level Logic**: Modified the orchestration loop in `simulation_orchestrator.py` to force one final `agent_turn` after detecting the `[FINISHED]` token.
  - **Rationale**: High-quality interactions require a "Handshake" at the end to confirm the transaction was successful.

## 4. Summary of Prompt Rationale Evolution

| Issue | Old Prompt | New Prompt | Rationale |
| :--- | :--- | :--- | :--- |
| **Prefixing** | "NEVER prefix your response with your name." | "NEVER prefix... do NOT describe your actions. Just SPEAK." | Force the LLM into "Chat Mode" instead of "Writing Mode." |
| **Data Looping** | (No specific rule for data provision) | "PROVIDE IT IMMEDIATELY... Make it up if needed." | Prevent the "polite stalling" behavior common in RLHF-trained models. |
| **Persona** | "You are Sarah Jenkins." | (Dynamic extraction from scenario file) | Ensure the simulator's personality is grounded in the specific test case (e.g., a stressed parent). |

---

## Current Status
As of v5, the prompt strategy has stabilized. The human simulator provides specific data, avoids role-play markers, and the agent provides final confirmation, resulting in "Gold Standard" logs that can be used for training or as few-shot examples.
