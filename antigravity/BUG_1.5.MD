# BUG-1.5: Late Service Area Rejection (UX Degradation)

**Status**: ✅ RESOLVED  
**Date**: 2026-01-02  
**Severity**: HIGH (Poor User Experience)  
**Resolution Date**: 2026-01-02

## Problem Statement

The service area validation is triggering **AFTER** the user has already:
1. Provided their full details (name, address, service type)
2. Answered follow-up questions
3. **Confirmed a specific time slot**

This creates a frustrating experience where users invest time in the booking process only to be rejected at the final step.

## Reproduction

```
User: I need to postpone my scheduled service appointment.
Agent: [Asks for name, address, service]

User: jose sanchez 134 workshire st new york
Agent: [Asks for service type]

User: aging hvac system
Agent: [Asks for preferred time]

User: sat 3pm
Agent: "Unfortunately, we are unable to accommodate... beyond a 30-mile radius"
```

## Root Cause Analysis

### Issue #1: LLM-Based Geographic Inference
- The system relies on the LLM to "infer" if an address is >30 miles away
- The LLM has **NO access to actual geographic data**
- "134 workshire st new york" was incorrectly flagged as out-of-area
- This creates **false positives** and **inconsistent behavior**

### Issue #2: Late Validation Timing
From `decide_system.txt` line 27:
```
0. **SERVICE AREA RULE**: If the location is explicitly stated/inferred as >30 miles away 
   (e.g., Springfield), pick 'chat' to decline. Do NOT pick 'book'.
```

The check happens in `DecideNode`, which means:
- ✅ Address extracted
- ✅ User asked for time slot
- ✅ User provides time slot
- ❌ **THEN** service area check fails → Rejection

### Issue #3: Ambiguous Prompt Guidance
The prompt says "explicitly stated/inferred" but provides no mechanism for the LLM to actually determine distance. The example "(e.g., Springfield)" is too vague - which Springfield?

## Impact

1. **User Frustration**: Users complete 3-4 conversation turns before rejection
2. **Wasted Time**: Both customer and AI agent resources wasted
3. **Poor Perception**: Makes the system appear incompetent
4. **Inconsistent Rejections**: Same addresses might be accepted/rejected randomly

## Proposed Solution

### Option A: Immediate Post-Extraction Validation (RECOMMENDED)

Add a validation step in `ExtractionNode.post()`:

```python
def post(self, shared, prep_res, exec_res):
    # ... existing extraction logic ...
    
    # IMMEDIATE SERVICE AREA CHECK
    if address:
        if is_out_of_service_area(address):  # Helper function
            shared["metadata"]["service_area_rejected"] = True
            return "service_area_reject"  # New action
```

Add a new `ServiceAreaRejectNode` that triggers IMMEDIATELY after extraction:
```python
class ServiceAreaRejectNode(Node):
    def exec(self, _):
        return "We only serve within a 30-mile radius. I recommend finding a local provider."
```

### Option B: Hardcoded Address Validation List

Create `utils/service_area.py`:
```python
# Known out-of-area cities/zips
OUT_OF_AREA = ["Springfield", "Malibu", "10880"]  # Explicit list

def is_out_of_service_area(address: str) -> bool:
    address_lower = address.lower()
    return any(blocked in address_lower for blocked in OUT_OF_AREA)
```

### Option C: Geographic API Integration (Most Robust)

Integrate with a geocoding API to calculate actual distance:
```python
def is_out_of_service_area(address: str) -> bool:
    # Use geocoding API to get lat/long
    # Calculate distance from office (haversine formula)
    # Return distance > 30 miles
```

## Recommended Fix (Hybrid Approach)

1. **Immediate**: Implement Option B (hardcoded list) for known test addresses
2. **Short-term**: Add explicit rejection in `ExtractionNode.post()` 
3. **Long-term**: Integrate Option C (geocoding API) for production

## Testing Strategy

After fix, verify:
- [ ] Out-of-area addresses rejected IMMEDIATELY after extraction
- [ ] User does NOT get asked for time slot if address is invalid
- [ ] Rejection message is clear and helpful
- [ ] In-area addresses proceed normally to booking

## Related Issues

- Connects to previous "Service Area Blindness" fix (Scenario 8, 13)
- Similar to "Context Blindness" bug where validation happened too late
