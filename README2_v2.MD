# Project Documentation: Evolution of Prompt Strategy (v2)

This document details the transition from **Static Rules** to **Context-Aware Reasoning** in the HVAC Booking Agent prompts.

## 1. Phase 1 Recap
- ** मैनेजर (Manager)**: JSON-based flow control.
- **कम्युनिकेटर (Communicator)**: "Empathetic, professional" persona.
- **सिमुलेटर (Simulator)**: Solved "polite stalling" by forcing immediate data provision.

## 2. Phase 2: Solving State Hallucinations

### The "Hallucination" Trap
In early multi-agent tests, the agent would say *"You're all set!"* because the Chat LLM felt the conversation had reached a logical conclusion. However, because the `DecideNode` hadn't yet selected `book`, and the `BookingNode` hadn't inserting into DB, the system state remained "Not Booked".

### Refined Logic: Contextual Guardrails
We updated `chat_system.txt` with a strict **Data-to-Confirmation** dependency:
> "If 'Booking Confirmed' is 'No', you are NOT allowed to confirm the booking."

### Few-Shot Benchmark
We added `chat_examples.txt` containing a success log where the agent explicitly requests missing Name/Address before offering a slot. This "Grounds" the LLM in real examples of correct data gathering.

---

## 3. Phase 2: Natural Closure (The "Handshake")

### The Rationale
A task-based conversation that ends at "Success!" feels like an automated script. Real human assistants check for further needs. 

### Prompt Updates:
- **`decide_system.txt`**: Added a rule to prioritize the `finish` action ONLY after the closing spiel has been acknowledged.
- **`chat_system.txt`**: Added Rule 5: *"ALWAYS include a closing spiel: 'Is there anything else I can help you with today?'"*

---

## 4. Current Prompt Rationale (Summary)

| Node | New Instruction | Rationale |
| :--- | :--- | :--- |
| **Decide** | "ALWAYS prioritize 'extract' if last message has new data." | Prevent the agent from "chatting" past the extraction point and wasting turns. |
| **Chat** | "DO NOT confirm until 'Booking Confirmed' is 'Yes'." | Force alignment between the conversational layer and the database layer. |
| **Chat** | "Repeat closing spiel until user says they are all set." | Ensure closure is mutually agreed upon, not just agent-terminated. |
