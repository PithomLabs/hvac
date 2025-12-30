import sys
import os
import yaml
import json

# Add PocketFlow to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "PocketFlow-main"))

from pocketflow import Node
from utils.call_llm import call_llm
from agent.database import get_db_connection

PERSONA = "Always empathetic but also quick and professional, highly detailed if need be."

class DecideNode(Node):
    def prep(self, shared):
        return shared.get("history", [])

    def exec(self, history):
        prompt = f"""
        You are the 'Manager' of an HVAC Booking Agent.
        Your task is to decide the next step based on the conversation history.
        
        Available Actions:
        - chat: The user asked a general question or just said hello.
        - extract: The user provided some info (name, address, issue) that needs to be recorded.
        - book: All info (Customer details and Slot) is present, and user wants to finalize.
        - finish: The conversation is naturally over.

        History: {json.dumps(history)}

        Respond ONLY in YAML format:
        action: <chat|extract|book|finish>
        reasoning: <brief explanation>
        """
        response = call_llm(prompt)
        try:
            # Clean response from markdown if present
            clean_response = response.replace("```yaml", "").replace("```", "").strip()
            return yaml.safe_load(clean_response)
        except Exception as e:
            return {"action": "chat", "reasoning": f"Error parsing decision: {e}"}

    def post(self, shared, prep_res, exec_res):
        action = exec_res.get("action", "chat")
        shared["current_action"] = action
        return action

class ChatNode(Node):
    def prep(self, shared):
        return shared.get("history", [])

    def exec(self, history):
        system_prompt = f"You are a helpful HVAC Agent. Persona: {PERSONA}. Be concise but empathetic."
        response = call_llm(history, system_prompt=system_prompt)
        return response

    def post(self, shared, prep_res, exec_res):
        shared.setdefault("history", []).append({"role": "assistant", "content": exec_res})
        shared["last_response"] = exec_res
        return "default"

class ExtractionNode(Node):
    def prep(self, shared):
        return {
            "last_message": shared["history"][-1]["content"] if shared["history"] else "",
            "current_user_info": shared.get("user_info", {}),
            "current_booking_info": shared.get("booking_info", {})
        }

    def exec(self, prep_res):
        prompt = f"""
        Extract HVAC booking details from the user's message.
        
        Last Message: {prep_res['last_message']}
        Existing User Info: {prep_res['current_user_info']}
        Existing Booking Info: {prep_res['current_booking_info']}

        Extract the following keys if present:
        - name
        - phone
        - email
        - address
        - service_type (e.g. AC Repair, Furnace Maintenance)
        - issue (description of the problem)

        Respond ONLY in YAML format. If a value is unknown, keep it as null.
        """
        response = call_llm(prompt)
        try:
            clean_response = response.replace("```yaml", "").replace("```", "").strip()
            return yaml.safe_load(clean_response)
        except:
            return {}

    def post(self, shared, prep_res, exec_res):
        # Update shared store with new info
        user_keys = ["name", "phone", "email", "address"]
        booking_keys = ["service_type", "issue"]
        
        shared.setdefault("user_info", {})
        shared.setdefault("booking_info", {})

        for k, v in exec_res.items():
            if v:
                if k in user_keys:
                    shared["user_info"][k] = v
                elif k in booking_keys:
                    shared["booking_info"][k] = v
        
        return "default"

class BookingNode(Node):
    def prep(self, shared):
        return {
            "user_info": shared.get("user_info", {}),
            "booking_info": shared.get("booking_info", {})
        }

    def exec(self, prep_res):
        user = prep_res["user_info"]
        booking = prep_res["booking_info"]
        
        # Check if we have enough info
        required_user = ["name", "address"]
        required_booking = ["service_type"]
        
        if not all(user.get(k) for k in required_user) or not all(booking.get(k) for k in required_booking):
            return "Missing information to complete booking. Need name, address, and service type."

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # 1. Ensure customer exists or create
            cursor.execute("INSERT INTO customers (name, phone, email, address) VALUES (?, ?, ?, ?)",
                           (user.get("name"), user.get("phone"), user.get("email"), user.get("address")))
            customer_id = cursor.lastrowid
            
            # 2. Find a slot (simplified: pick first available)
            cursor.execute("SELECT id, start_time FROM available_slots WHERE is_booked = 0 LIMIT 1")
            slot = cursor.fetchone()
            
            if not slot:
                return "No available slots found in the database."
            
            slot_id = slot["id"]
            start_time = slot["start_time"]
            
            # 3. Create booking
            cursor.execute("INSERT INTO bookings (customer_id, slot_id, service_name, issue_description) VALUES (?, ?, ?, ?)",
                           (customer_id, slot_id, booking.get("service_type"), booking.get("issue")))
            
            # 4. Mark slot as booked
            cursor.execute("UPDATE available_slots SET is_booked = 1 WHERE id = ?", (slot_id,))
            
            conn.commit()
            conn.close()
            return f"Success! Booking confirmed for {user['name']} on {start_time}. Service: {booking['service_type']}."
        except Exception as e:
            return f"Error database operation: {e}"

    def post(self, shared, prep_res, exec_res):
        shared.setdefault("history", []).append({"role": "assistant", "content": exec_res})
        shared["last_response"] = exec_res
        return "default"
