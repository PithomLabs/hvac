# Project Documentation: HVAC Booking Agent Evolution (v1)

This document traces the development of the HVAC Booking Agent from initial conception to high-fidelity multi-agent simulations.

## 1. Agent Design and Implementation

### Concept
A specialized AI agent designed to handle customer inquiries for HVAC services, provide basic diagnostic advice, and automate the booking process using a professional and empathetic persona.

### Architecture: PocketFlow Graph
The agent is built using the **PocketFlow** framework, employing a Graph + Shared Store abstraction.

- **[DecideNode](file:///home/chaschel/Documents/ibm/ai/PocketFlow-Template-Python-main/agent/nodes.py#L24-L80)**: The "Manager" node that analyzes conversation history and determines the next action (chat, extract, book, or finish).
- **[ChatNode](file:///home/chaschel/Documents/ibm/ai/PocketFlow-Template-Python-main/agent/nodes.py#L81-L109)**: The "Communicator" node responsible for generating customer-facing responses.
- **[ExtractionNode](file:///home/chaschel/Documents/ibm/ai/PocketFlow-Template-Python-main/agent/nodes.py#L110-L168)**: Extracts structured data (Name, Address, Zip, Issue) from raw text.
- **[BookingNode](file:///home/chaschel/Documents/ibm/ai/PocketFlow-Template-Python-main/agent/nodes.py#L169-L229)**: Interfaces with the SQLite database to solidify appointments.

### Initial Prompt Strategy
- **Persona**: "Empathetic, professional, and efficient. No fluff, just direct help."
- **Manager-Worker Pattern**: Separating decision-making (Decide) from execution (Chat/Extract) to minimize hallucinations and improve state management.

---

## 2. Quality Assurance: "Gold Standard" Scenarios

To verify the agent's effectiveness, we established a **Gold Standard** benchmark in the `data/qa/` directory.

### Sample Scenarios
We generated 20 distinct scenarios (A1-E20) representing the most common and critical HVAC issues:
- **Scenario A1 (AC Dead)**: High-urgency cooling failure with a baby at home.
- **Scenario A3 (Burning Smell)**: Immediate safety concern requiring urgent intervention.
- **Scenario C12 (Billing)**: Handling pricing disputes and transparency.

### Analysis of Initial Runs
Early testing revealed that while the agent followed the logical flow (e.g., it knew it needed an address), the **conversation quality** was sometimes lacking:
- **Formalism**: The agent sounded overly "robotic" and occasionally ignored the customer's specific anxieties (e.g., hidden fees).
- **Dead Ends**: Conversations would end abruptly without confirming the final booking details.

---

## 3. Multi-Agent Simulation: The Breakthrough

Recognizing that static QA wasn't enough, we implemented a **Multi-Agent Simulation** environment to stress-test the agent in dynamic, multi-turn conversations.

### The Orchestrator
The [simulation_orchestrator.py](file:///home/chaschel/Documents/ibm/ai/PocketFlow-Template-Python-main/data/qa/simulation_orchestrator.py) pits two LLMs against each other:
1.  **AI Agent**: Running the core business logic (Mimo-v2-flash).
2.  **Human Simulator**: Acting as a stressed, non-expert customer (Nemotron-nano).

### Iterative Improvements and Prompt Rationales

| Iteration | Issue Identified | Rationale for Refinement | Result |
| :--- | :--- | :--- | :--- |
| **v1-v2** | Human Simulator "role-played" (e.g., "Human: Hello"). | Simulation logs should look like real chat transcripts, not scripts. | Strictly prohibited name/role prefixes in simulator prompts. |
| **v3-v4** | Loops and Vague Responses. Human said "I will provide it" instead of providing it. | Efficiency is key. We need to test the agent's ability to process real data. | Added rules to "PROVIDE INFO IMMEDIATELY" and make up data if necessary. |
| **v5** | Lack of Closure. Conversation ended as soon as the human gave the info. | In real life, a booking isn't complete until the agent confirms the date/time. | Forced a final agent turn after the human finishes to ensure confirmation. |

### Final State (v5 Run)
The latest runs (e.g., `gold_a3_smell_multi_agent_v5.md`) demonstrate high-quality, 6-turn conversations that reach successful booking with natural language and no meta-talk.
