# BUG-1.6: Post-Booking Context Loss (Phase 3 Memory Issue)

**Status**: ✅ RESOLVED  
**Date**: 2026-01-02  
**Resolution Date**: 2026-01-02  
**Severity**: MEDIUM (Poor UX, but not blocking)

## Problem Statement

After successfully completing a booking and delivering the Phase 2 confirmation script, the agent **forgets customer details** when handling follow-up questions. This creates a poor user experience where customers must re-provide information they've already given.

## Reproduction

```
User: My heating stopped working... does my home have a furnace or heat pump?
Agent: [Provides technical advice] Please provide your name and address for booking.

User: chaschel kurumi 2 Commercial Pkwy Branford, CT 06405
[Service Area] → 34.7 miles from Hartford, CT → IN
Agent: Thank you, Chaschel Kurumi. When are you available?

User: monday 10am
Agent: Does that work for you?

User: yes
Agent: Could you confirm the service type?

User: heating stopped working
Agent: Booking confirmed! HB-XXXX. Is there anything else I can help you with?

User: Do you provide duct cleaning services?
Agent: We do offer duct cleaning. Would you like to schedule? 
       ❌ PLEASE LET ME KNOW YOUR NAME AND ADDRESS IF YOU'RE INTERESTED.
```

## Root Cause

The agent enters **Phase 3** (Post-Booking) after delivering the confirmation script, but the system is treating follow-up questions as **new conversations** rather than continuation of the same customer session.

### Expected Data Flow
```
Phase 1 → Extract & Store → Phase 2 (Booking) → Phase 3 (Follow-up)
          ✓ Name           ✓ Booking #         ❌ CONTEXT RETAINED?
          ✓ Address        ✓ Confirmed
```

### Actual Data Flow
```
Phase 1 → Extract & Store → Phase 2 (Booking) → Phase 3 (Follow-up)
          ✓ Name           ✓ Booking #         ❌ CONTEXT LOST!
          ✓ Address        ✓ Confirmed         ❌ Re-asks for name/address
```

## Impact

1. **Poor UX**: Customer must repeat information they already provided
2. **Wasted Time**: Extra conversation turns for data collection
3. **Unprofessional**: System appears to "forget" what customer just said
4. **Lost Upsell Opportunity**: Harder to book follow-up services if user frustrated

## Current Behavior

**Phase 2 Confirmation Script:**
```
"Your booking confirmation number is: HB-XXXX. Have a great day! 
 Is there anything else I can help you with today?"
```

**Follow-up Question Handling:**
- Agent responds to technical questions ✓
- Agent offers to schedule additional services ✓
- **Agent re-asks for name and address** ❌

## Expected Behavior

**Better Follow-up Response:**
```
Agent: "We do offer duct cleaning services, which can help reduce dust and allergens. 
        Would you like me to schedule a duct cleaning service for the same address 
        (2 Commercial Pkwy Branford, CT) after your heating repair on Monday?"
```

**Key Improvements:**
1. ✅ **Remember customer name** - Address them by name
2. ✅ **Remember address** - Reference existing address, don't re-ask
3. ✅ **Suggest coordination** - Offer to schedule around existing booking
4. ✅ **Maintain context** - Acknowledge this is a follow-up, not new conversation

## Proposed Solution

### Option A: Persistent Customer Context (RECOMMENDED)

Modify `ChatNode` to preserve customer information even after booking:

```python
# In ChatNode.prep()
context_block = f"""
CURRENT BOOKING STATUS:
- Booking Confirmed: {confirmed}
- Phase 2 Delivered: {'Yes' if prep_res.get('phase2_delivered') else 'No'}
- Customer Name: {user.get('name', 'Missing')}
- Service Address: {user.get('address', 'Missing')}
- Previous Booking: {prep_res.get('hb_number', 'None')}

POST-BOOKING CONTEXT:
If a previous booking exists AND the user asks about additional services:
1. Acknowledge them by name
2. Reference the existing address (don't re-ask)
3. Offer to coordinate with existing booking if relevant
4. Only ask for DIFFERENT information (e.g., new service type, different date)
"""
```

### Option B: Multi-Service Booking Flag

Add a `multi_service` flag to track when customer wants additional services:

```python
if confirmed and user.get('name') and user.get('address'):
    shared['multi_service_mode'] = True
```

Then in `ChatNode` prompt:
```
MULTI-SERVICE MODE: Customer already provided name/address. 
DO NOT re-ask for these. Reference existing info.
```

### Option C: Explicit Context Reminder

Add to `chat_system.txt`:
```
POST-BOOKING FOLLOW-UP RULES:
- After booking confirmation, if customer asks about OTHER services:
  * DO use their name from the previous booking
  * DO reference their existing address
  * DO NOT ask for name/address again
  * DO ask for: service type, preferred date/time, any special requirements
```

## Recommended Fix (Hybrid A + C)

1. **Update `chat_system.txt`** with explicit post-booking context rules
2. **Modify `ChatNode.prep()`** to include previous booking context in prompt
3. **Add `last_booking` field** to track most recent HB number and details

## Testing Strategy

After fix, verify:
- [ ] Agent remembers customer name in follow-up questions
- [ ] Agent doesn't re-ask for address if already validated
- [ ] Agent can book multiple services for same customer
- [ ] Agent handles new customer (different name) correctly

## Related Issues

- Similar to BUG-1.4 (Premature Termination) - both involve Phase 2/3 transitions
- Connects to service area validation - address should be reused for follow-up services
