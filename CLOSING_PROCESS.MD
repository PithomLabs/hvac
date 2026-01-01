# Closing Process Refinement: Standardized Handshake

This plan outlines the enhancements to the AI agent's closing protocol to ensure a consistent, concise, and professional termination of the conversation.

## 1. Objective
Standardize the final interaction turn to include a confirmation number and a proactive check for further assistance, followed by a clean termination signal.

## 2. Proposed Changes

### AI Agent Prompts

#### [MODIFY] [chat_system.txt](file:///home/chaschel/Documents/ibm/ai/PocketFlow-Template-Python-main/agent/prompts/chat_system.txt)
- **New Rule: Always Be Closing (ABC)**: If the conversation involves general questions or advice (e.g., filter sizes), provide the information but always find a way to offer a professional booking/maintenance visit for the business's sake.
- **Rule: The "Anything Else?" Spiel**: 
    - You MUST ask *"Is there anything else I can help you with today?"* at least once (and up to twice maximum) if the conversation has not reached a booking confirmation.
    - NEVER end a non-booking conversation abruptly without this spiel.
- **Simplified Booking Closure**: 
    1. Once a booking is confirmed, state: *"This is your booking confirmation number: HB-XXXX."*
    2. Add: *"Have a great day!"*
    3. **Immediate Termination**: End with `*END OF CONVERSATION*`. (No need for the spiel here as the task is finished).

#### [MODIFY] [decide_system.txt](file:///home/chaschel/Documents/ibm/ai/PocketFlow-Template-Python-main/agent/prompts/decide_system.txt)
- **Closure Awareness**: 
    - Pick `finish` ONLY after the final booking confirmation has been delivered OR if the user has said "I'm all set/No thanks" in response to the "Anything else?" spiel.
    - Do NOT pick `finish` just because the user seems done; ensure the agent has provided the required closing service/spiel.

## 3. Revised Handshake Examples

### Case A: Successful Booking (Immediate Closure)
> **Agent**: ...Success! You're all set for Thursday. This is your booking confirmation number: **HB-4821**. Have a great day!
> 
> **Agent**: *END OF CONVERSATION*

### Case B: Advice/DIY Path (The ABC + Spiel Closure)
> **User**: I'll just check the filter myself. Thanks.
> 
> **Agent**: No problem! If you'd like, I can still send a tech out just to measure it for you and ensure the unit is running efficiently for $89. Otherwise, is there anything else I can help you with today? (ABC + Spiel)
> 
> **User**: No, I'm good.
> 
> **Agent**: Have a great day! *END OF CONVERSATION* (Detection of "I'm good" leads to finish)

## 4. Verification Plan
- **Target**: Dry run Scenario 6 (`gold_b6_filters.md`).
- **Pass Criteria**:
    1. Agent provides filter size PLUS an offer for service (ABC).
    2. Agent asks "Is there anything else?" at least once.
    3. Proper HB-XXXX number provided if booked.
    4. Clean termination on acknowledgement.
