# Gold Standard Gap Analysis: HVAC Booking Agent

This document audits the current implementation and QA suite against the 20 foundational "Gold Standard" scenarios defined in `CONTEXT_ENGINEERING.txt`.

## Status Summary

The current `agent/` logic and `data/qa/` test conversations cover approximately **50% (10/20)** of the Gold Standard variety. While basic booking and extraction are stable, specialized logic for edge cases, technical advice, and state modification (updates) are currently missing.

| Category | Scenario | Met? | Implementation Notes / Gaps |
| :--- | :--- | :---: | :--- |
| **A: Emergency** | 1. AC Dead | ✅ | Covered in `test_conv_01.md`. Needs "Urgent" flag logic. |
| | 2. Leaking Furnace | ✅ | Covered in `test_conv_03.md`. Needs property damage awareness. |
| | 3. Burning Smell | ✅ | Covered in `test_conv_05.md`. Logic needs to enforce "Urgent Safety Check" instead of standard booking. |
| | 4. Frozen Coil | ❌ | **GAP**: Agent must instruct user to thaw (turn off) before booking 24h later. |
| **B: Maintenance** | 5. Annual Tune-Up | ✅ | Covered in `test_conv_02.md`. |
| | 6. Filter Confusion | ⚠️ | Partially covered in `test_conv_07.md`. Needs info-retrieval vs booking logic. |
| | 7. Smart Thermostat | ⚠️ | Covered in `test_conv_07.md`. Gap: Pricing quote logic. |
| | 8. System Replacement| ✅ | Covered in `test_conv_04.md`. |
| **C: Logistics** | 9. Reschedule | ❌ | **GAP**: Database/Flow does not support modifying existing bookings. |
| | 10. Specific Window | ❌ | **GAP**: Decider/Booker logic picks first slot; needs constraint matching. |
| | 11. Gate Code | ❌ | **GAP**: Need `notes` field in `bookings` table and extraction logic. |
| | 12. Tenant/Landlord | ✅ | Covered in `test_conv_09.md`. Gap: Authorization securement. |
| **D: Edge Cases** | 13. Price Haggle | ❌ | **GAP**: Objection handling logic missing in `nodes.py`. |
| | 14. Vague Noise | ✅ | Covered in `test_conv_06.md`. |
| | 15. Wrong Area | ❌ | **GAP**: Geofencing / Service boundary check missing. |
| | 16. Callback/Angry | ❌ | **GAP**: Sentiment analysis and "Manager" flag logic missing. |
| **E: Technical** | 17. Heat Pump | ✅ | Covered in `test_conv_04.md`. |
| | 18. Duct Cleaning | ✅ | Covered in `test_conv_08.md`. |
| | 19. Commercial | ✅ | Covered in `test_conv_10.md`. Gap: Routing to different rates. |
| | 20. Warranty Check | ❌ | **GAP**: Serial number lookup logic missing. |

---

## Technical Recommendations

### 1. Hardening the `DecideNode`
The decider needs to distinguish between **"Actionable Bookings"** and **"Information/Support"** requests. 
- **Urgent Safety Escapes**: For smells/smoke, it should skip extraction and go straight to an "Urgent Protocol" chat or escalation.
- **Modification Mode**: Detect "reschedule" or "update info" intents to trigger a different database node.

### 2. Database Schema Expansion
The SQLite schema requires:
- `notes` and `gate_code` in `bookings`.
- `urgency_level` (Standard, Urgent, Emergency).
- `billing_contact` (for Tenant/Landlord scenarios).

### 3. Extraction Sensitivity
The `ExtractionNode` needs to be more robust for:
- Serial numbers (Warranty).
- Constraints (Time windows).
- Intent (Repair vs. Quote vs. Maintenance).

### 4. QA Logic Stabilization
The `data/qa/run_qa.py` runner is proving to be the right "lab" to fix these. It currently exposes that the agent often loops back to `extract` unnecessarily (Decider stabilization needed).

---
*Created by Antigravity on 2025-12-31*
