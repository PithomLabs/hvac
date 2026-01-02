# Long-Form Multi-Scenario Conversation Test

**Date**: 2026-01-02  
**Purpose**: Stress-test agent's ability to handle multiple scenarios in one conversation  
**Test Duration**: ~15-20 turns  
**Scenarios Combined**: 3 randomized from Gold Standard (Emergency + Maintenance + Follow-up)

---

## Test Objectives

This test validates the agent's ability to:

1. **Handle emergency situations** with safety prioritization
2. **Book multiple services** for the same customer (context preservation)
3. **Provide technical advice** while maintaining booking flow
4. **Remember customer details** across service requests (BUG-1.6 verification)
5. **Validate service area** correctly (multi-office coverage)
6. **Maintain professional tone** throughout extended conversation

---

## Selected Scenarios

### Scenario A: Burning Smell (Emergency - Gold Standard #3)
**Category**: Emergency (Safety-Critical)  
**Expected Behavior**: 
- Immediate safety advice (turn off system)
- Urgent scheduling
- High priority handling

### Scenario B: Annual Tune-Up (Maintenance - Gold Standard #5)  
**Category**: Maintenance (Non-Emergency)  
**Expected Behavior**:
- Professional scheduling
- Service explanation ($89 diagnostic)
- Confirmation workflow

### Scenario C: Filter Question (Follow-up - Gold Standard #6)
**Category**: Technical Advice + Upsell  
**Expected Behavior**:
- Technical advice about filter types
- Context retention (same customer, same address)
- Offer additional service WITHOUT re-asking for details

---

## Test Script

### TURN 1: Initial Emergency Contact
**Human**: 
```
"There's a burning smell coming from my furnace and I'm worried. Should I turn it off? 
I'm in Sacramento, CA."
```

**Expected Agent Behavior**:
- ✅ Provide immediate safety advice (turn off furnace)
- ✅ Express urgency and concern
- ✅ Request name and address for emergency booking
- ✅ Acknowledge Sacramento (verify service area)

**Success Criteria**:
- Agent prioritizes safety before booking details
- Agent recognizes urgency level
- Professional and calming tone

---

### TURN 2: Provide Details
**Human**:
```
"Bruce Wayne, 1007 Mountain Dr, Gotham... wait, sorry, I meant 1500 J St, Sacramento, CA 95814."
```

**Expected Agent Behavior**:
- ✅ Extract corrected address (1500 J St, Sacramento)
- ✅ Validate service area (Sacramento ~0 miles from Sacramento, CA capital)
- ✅ Ask for preferred time slot
- ✅ Maintain urgency awareness

**Success Criteria**:
- Address correction handled smoothly
- Service area IN-AREA confirmed
- No confusion from joke/mistake

---

### TURN 3: Schedule Emergency Visit
**Human**:
```
"As soon as possible. Today if you can."
```

**Expected Agent Behavior**:
- ✅ Confirm emergency slot availability
- ✅ Provide booking confirmation (HB-XXXX)
- ✅ Deliver Phase 2 confirmation script
- ✅ Ask "Is there anything else?"

**Success Criteria**:
- Booking completed successfully
- HB number provided
- Phase 2 transition smooth

---

### TURN 4: Request Additional Service (Testing BUG-1.6 Fix)
**Human**:
```
"Actually yes, while you're here - I also need my annual furnace tune-up done. 
Can you schedule that too?"
```

**Expected Agent Behavior**:
- ✅ Acknowledge request (annual tune-up)
- ✅ **USE CUSTOMER NAME** ("Bruce" or "Mr. Wayne")
- ✅ **REFERENCE EXISTING ADDRESS** ("at the same address" or "at 1500 J St")
- ✅ **DO NOT re-ask for name/address**
- ✅ Offer to coordinate with emergency visit or schedule separately
- ✅ Ask for preferred date/time ONLY

**Success Criteria** (BUG-1.6 Verification):
- ❌ Agent does NOT say: "Please provide your name and address"
- ✅ Agent DOES say: "at the same address" or similar
- ✅ Agent DOES use customer's name
- ✅ Professional multi-service handling

---

### TURN 5: Confirm Tune-Up Timing
**Human**:
```
"Can you do the tune-up on Monday at 10 AM?"
```

**Expected Agent Behavior**:
- ✅ Confirm availability
- ✅ Create second booking (new HB-XXXX number)
- ✅ Deliver confirmation for tune-up service
- ✅ Ask if there's anything else

**Success Criteria**:
- Second booking confirmed
- Different HB number from first booking
- Clear separation of services

---

### TURN 6: Technical Question (Testing Technical Advice)
**Human**:
```
"One more thing - I'm confused about air filters. Do I really need to change them every month, 
or can I wait longer? And what's the difference between MERV ratings?"
```

**Expected Agent Behavior**:
- ✅ Provide clear technical explanation about filter change frequency
- ✅ Explain MERV ratings (higher = better filtration)
- ✅ Maintain context (still addressing Bruce)
- ✅ Offer filter replacement service if applicable
- ✅ Still reference existing address if offering service

**Success Criteria**:
- Accurate technical information
- Professional explanation (not too technical)
- Context maintained throughout
- No re-asking for details if offering service

---

### TURN 7: Graceful Closure
**Human**:
```
"That's all I needed. Thanks for your help!"
```

**Expected Agent Behavior**:
- ✅ Professional closing
- ✅ *END OF CONVERSATION* marker
- ✅ Summary of bookings (optional but nice)

**Success Criteria**:
- Clean conversation termination
- Professional closure

---

## Verification Checklist

### Safety & Emergency Handling
- [ ] Safety advice delivered immediately (before booking)
- [ ] Urgent tone and prioritization
- [ ] Emergency slot offered

### Service Area Validation
- [ ] Sacramento, CA correctly identified as IN-AREA
- [ ] Address validated via geocoding
- [ ] Multi-office coverage working

### Context Preservation (BUG-1.6)
- [ ] Customer name remembered in follow-up
- [ ] Address NOT re-requested for second service
- [ ] Professional reference to existing info
- [ ] Smooth multi-service booking

### Technical Advice
- [ ] Accurate filter information
- [ ] Professional explanation
- [ ] Context maintained during advice

### Booking Workflow
- [ ] Two separate bookings confirmed
- [ ] Two different HB numbers
- [ ] Phase 2 delivery for each booking
- [ ] Clean closure

---

## Expected Output Format

Document in multi-agent style with:
```markdown
**Human**: [User message]

**AI Agent** (Action: [extract/chat/book/finish]): [Agent response]

> Reasoning: [Why the agent did this, what patterns were triggered]
```

---

## Success Metrics

**PASS Criteria**:
- ✅ All 7 turns completed successfully
- ✅ No re-asking for customer details after first booking
- ✅ Safety advice delivered appropriately
- ✅ Technical advice accurate
- ✅ Both bookings confirmed with separate HB numbers
- ✅ Service area validated correctly

**FAIL Criteria**:
- ❌ Agent re-asks for name/address during second service request
- ❌ Safety advice not prioritized
- ❌ Service area incorrectly validated
- ❌ Inaccurate technical information
- ❌ Booking confirmation issues

---

## Notes

This test combines:
1. **Emergency handling** (Burning Smell scenario)
2. **Multi-service booking** (Annual Tune-Up)
3. **Technical advice** (Filter Question)
4. **Context preservation** (BUG-1.6 verification)
5. **Service area validation** (Sacramento, CA)

Running time: ~15-20 conversation turns  
Real-world simulation: High (combines common customer patterns)
