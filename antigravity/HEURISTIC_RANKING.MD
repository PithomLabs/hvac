# Heuristic Ranking & Implementation Plan

This document outlines the evaluation of the AI Agent's performance against core business and service heuristics, and defines the "Phase-Based Closure" logic to resolve current inconsistencies.

## 1. Heuristic Evaluation (Scenario 6 v4)

| Rule | Status | Rank | Corrective Action |
| :--- | :--- | :--- | :--- |
| **1. Service Accuracy** | Pass | 5/5 | None. Maintain technical depth. |
| **2. Always Be Closing (ABC)** | Pass | 5/5 | None. Lead generation is working. |
| **3. Customer Experience** | Partial | 3/5 | Remove repetitive "robotic" spiel timing. |
| **4. End-Stage Spiel Only** | Fail | 1/5 | Implement "Phase 2" trigger logic. |
| **5. Great Day Closing** | Pass | 5/5 | Maintain "HB-XXXX + Have a great day" signal. |

## 2. Phase-Based Conversation Management

To prevent the agent from being "too aggressive" with the closing spiel, we will split the conversation logic into two distinct phases.

### Phase 1: Inquiry & Solutioning
*   **Goal**: Answer technical questions, provide advice, and attempt to book (ABC).
*   **Spiel Rule**: **FORBIDDEN.** The agent must NEVER ask "Is there anything else?" while it is still waiting for Name, Address, or Service details, or while the user is actively asking technical questions.

### Phase 2: Handover or Final Refusal (The Handshake)
*   **Goal**: Cleanly exit the conversation.
*   **Trigger (Strict Trigger Logic)**: This phase is only entered when:
    1.  A booking is confirmed (HB-XXXX shared).
    2.  **OR** the user's technical questions appear answered AND they indicate they do not want a booking (e.g., "I'll do it myself").
*   **Spiel Rule**: The agent asks *"Is there anything else I can help you with today?"* to ensure no loose ends remain.
*   **Limit**: This spiel is used a maximum of 2 times.

## 3. Strict Trigger Logic Clarification

The "Anything Else" spiel is currently used as a **Suffix** (added to every message). This is incorrect. 

**Strict Trigger Logic** means the spiel is treated as a **Closing Transition**:
- It should only be issued when the agent believes the **primary intent** (Booking or Information) has been satisfied.
- If the agent is currently asking for an Address to complete a booking, it is **Phase 1** and the spiel must be omitted.
- If the agent has provided the filter size and the user says "Thanks!", the agent enters **Phase 2**, asks the spiel, and waits for a final "Bye" before hitting `*END OF CONVERSATION*`.

## 4. Implementation Steps

1.  **Update `chat_system.txt`**: Add explicit "Phase 1 vs Phase 2" rules and negative constraints on the spiel.
2.  **Update `decide_system.txt`**: Guide the 'Manager' to stay in `chat` (Phase 1) until technical inquiries are ceased.
3.  **Simulation Verification**: Execute Scenario 6 v5 to verify the spiel only appears at the very end.
