# REFINEMENT_2: Service Type Extraction Logic Fix

## Problem Description

The AI agent was incorrectly classifying service types during the extraction phase. Specifically, keywords like **"install"**, **"installation"**, and **"setup"** were being hard-mapped to the `Maintenance` category in `extract_system.txt`. 

This led to inaccurate Phase 2 confirmation scripts, where a customer requesting a system installation would be told: *"Success! You're all set for your Maintenance visit."*, which is confusing and unprofessional.

Additionally, there was no dedicated category for **Rescheduling**, which is a common user intent in several Gold Standard scenarios.

## Solution: Specific Categorization

I refined the service mapping in [`extract_system.txt`](file:///home/chaschel/Documents/ibm/ai/PocketFlow-Template-Python-main/agent/prompts/extract_system.txt) to introduce distinct categories and better keyword isolation.

### Changes:
1. **New Category: INSTALLATION**
   - Moved "install", "installation", "setup", "set up", "replace", and "replacement" from `MAINTENANCE` to `INSTALLATION`.
   - Added contextual rules to handle "new system" requests.
2. **New Category: RESCHEDULE**
   - Added specific keywords: "reschedule", "move", "change date", "Friday instead", etc.
3. **Updated Schema**
   - Updated the allowed values for `service_type` to: `"Maintenance", "Repair", "Installation", "Reschedule", or "Quote"`.

## Verification Results

The fix was verified across three Gold Standard scenarios using stable models (`nvidia/nemotron-nano-9b-v2:free` for human, `openai/gpt-oss-120b` for agent) to ensure logic accuracy.

### 🟢 Scenario 7: Thermostat (v17)
- **Human Intent**: "I bought a Nest thermostat. Can you guys install it?"
- **Result**: `service_type: "Installation"` extracted correctly.
- **Confirmation**: *"Success! You're all set for your Installation visit."*

### 🟢 Scenario 8: System Replacement (v6)
- **Human Intent**: "My system is 20 years old... I think it's time for a new one."
- **Result**: `service_type: "Installation"` extracted correctly.
- **Confirmation**: *"Success! You're all set for your Installation visit."*

### 🟢 Scenario 9: Reschedule (v9)
- **Human Intent**: "I have a tech coming Tuesday... Can we do Friday instead?"
- **Result**: `service_type: "Reschedule"` extracted correctly.
- **Confirmation**: *"Success! You're all set for your Reschedule visit."*

## Evidence (Log Snippet - Scenario 9)

```markdown
**AI Agent** (Action: chat): Success! You're all set for your Reschedule visit. Your booking confirmation number is: HB-5273.
```

## Conclusion

**REFINEMENT_2** is **SUCCESSFUL**. The agent now accurately distinguishes between different HVAC service requests, leading to more professional and relevant customer interactions.

---
**Status**: ✅ VERIFIED AND CLOSED
**Date**: 2026-01-02
