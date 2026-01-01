# REFINEMENT_2: Service Type Extraction Fix

This refinement addresses the issue where the agent incorrectly extracts service types (e.g., "installation" as "Maintenance"). It introduces "Installation" and "Reschedule" as distinct service types in the extraction logic and refines the keyword mapping to improve accuracy.

## Proposed Changes

### [Component Name] Agent Prompts

#### [MODIFY] [extract_system.txt](file:///home/chaschel/Documents/ibm/ai/PocketFlow-Template-Python-main/agent/prompts/extract_system.txt)
- Added `INSTALLATION` category with keywords: "install", "installation", "setup", "set up", "replace", "replacement".
- Removed "install", "installation", "setup", "set up" from `MAINTENANCE`.
- Added `RESCHEDULE` category with keywords: "reschedule", "move", "change date", "Friday instead" (contextual).
- Updated `service_type` allowed values to include "Maintenance", "Repair", "Installation", "Reschedule", or "Quote".
- Added explicit rule: If a user specifies a new installation, DO NOT use "Maintenance". Use "Installation".

## Verification Plan

### Automated Tests
- Run Scenario 7 (`gold_b7_thermostat.md`) and verify `service_type` is "Installation".
- Run Scenario 8 (`gold_b8_replacement.md`) and verify `service_type` is "Installation".
- Run Scenario 9 (`gold_c9_reschedule.md`) and verify `service_type` is "Reschedule".

### Manual Verification
- Verify the final Phase 2 script correctly uses the new service types (e.g., "Success! You're all set for your Installation visit").