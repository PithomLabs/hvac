import sys
import os
import json

# Add project root and PocketFlow to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "PocketFlow-main"))

from agent.nodes import DecideNode, ExtractionNode, BookingNode
from agent.database import init_db

def test_nodes():
    init_db()
    shared = {
        "history": [
            {"role": "user", "content": "Hello, I need help with my AC! It is blowing warm air."},
            {"role": "user", "content": "My name is John Doe, I live at 123 Cooling Lane. My phone is 555-0199."}
        ],
        "user_info": {},
        "booking_info": {},
        "current_action": None
    }

    print("--- Testing DecideNode ---")
    decider = DecideNode()
    action = decider.run(shared)
    print(f"Decided action: {action}")
    print(f"Shared current_action: {shared.get('current_action')}")

    print("\n--- Testing ExtractionNode ---")
    extractor = ExtractionNode()
    extractor.run(shared)
    print(f"Extracted User Info: {shared.get('user_info')}")
    print(f"Extracted Booking Info: {shared.get('booking_info')}")

    # Manually fulfill requirements for BookingNode if needed
    shared["user_info"]["address"] = "123 Cooling Lane"
    shared["booking_info"]["service_type"] = "AC Repair"

    print("\n--- Testing BookingNode ---")
    booker = BookingNode()
    result = booker.run(shared)
    print(f"Booking Result: {result}")

if __name__ == "__main__":
    test_nodes()
