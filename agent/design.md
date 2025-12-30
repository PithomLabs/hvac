# HVAC Agent Design: Nodes and Flow

## Shared Store Structure
```python
shared = {
    "history": [],             # Chat history: [{"role": "user/assistant", "content": "..."}]
    "user_info": {},           # Extracted info: name, address, phone
    "booking_info": {},        # Extracted info: service_type, issue, slot_id
    "current_action": None,    # Action to take (chat, extract, book)
    "last_response": ""        # Last assistant message
}
```

## Node Definitions

### 1. DecideNode (Regular)
- **Purpose**: "The Brain". Analyzes history to decide next action.
- **Prep**: Reads `history`.
- **Exec**: Prompt LLM with history and available actions (chat, extract, book, finish). Returns YAML with `action` and `reasoning`.
- **Post**:
    - If `action == "chat"`, return "chat".
    - If `action == "extract"`, return "extract".
    - If `action == "book"`, return "book".
    - Else return "finish".

### 2. ChatNode (Regular)
- **Purpose**: Empathetic & Professional communication.
- **Prep**: Reads `history`.
- **Exec**: Prompt LLM to generate a response in the defined persona.
- **Post**: Appends response to `history`, sets `last_response`, returns "default".

### 3. ExtractionNode (Regular)
- **Purpose**: Structured data extraction.
- **Prep**: Reads last user message and current `user_info`/`booking_info`.
- **Exec**: Prompt LLM to extract/update details into YAML.
- **Post**: Updates `user_info` and `booking_info`, returns "default".

### 4. BookingNode (Regular)
- **Purpose**: Database interaction.
- **Prep**: Reads `user_info` and `booking_info`.
- **Exec**: 
    - Check service existence in DB.
    - Check slot availability.
    - If all OK, create booking record.
- **Post**: Sets status in shared store, returns "default".

## Flow Transitions
```mermaid
flowchart TD
    Start --> Decide
    Decide - "chat" >> Chat
    Decide - "extract" >> Extraction
    Decide - "book" >> Booking
    Decide - "finish" >> End
    
    Chat >> Decide
    Extraction >> Decide
    Booking >> Decide
```
