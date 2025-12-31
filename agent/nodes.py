import sys
import os
import json

# Add project root and PocketFlow to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "PocketFlow-main"))

from pocketflow import Node
from utils.call_llm import call_llm
from agent.database import get_db_connection

PERSONA = "Always empathetic but also quick and professional, highly detailed if need be."

class DecideNode(Node):
    def prep(self, shared):
        return {
            "history": shared.get("history", []),
            "user_info": shared.get("user_info", {}),
            "booking_info": shared.get("booking_info", {})
        }

    def exec(self, prep_res):
        history = prep_res["history"]
        user = prep_res["user_info"]
        booking = prep_res["booking_info"]
        
        prompt = f"""
        You are the 'Manager' of an HVAC Booking Agent.
        Your task is to decide the next step based on the conversation history.
        
        Available Actions:
        - chat: General conversation, asking for missing info, explaining value, or suggesting a slot.
        - extract: The user provided info that is currently 'Missing' in the Profile Status. 
        - book: ONLY when Name, Address, and Service are present AND the user has agreed to a slot OR is asking to book ASAP.
        - update: The user is providing additional info (like a gate code) for an EXISTING or confirmed booking.
        - finish: ONLY AFTER the booking is confirmed/updated or if the user explicitly ends without booking.

        Current Profile Status:
        - Name: {user.get('name', 'Missing')}
        - Address: {user.get('address', 'Missing')}
        - Service: {booking.get('service_type', 'Missing')}
        - Notes: {booking.get('notes', 'Missing')}
        - Urgency: {booking.get('urgency', 'Missing')}
        - Billing: {booking.get('billing_info', 'Missing')}

        History: {json.dumps(history)}

        Rule: You MUST use 'extract' if any NEW information in the history is not yet captured in the Profile Status above.
        Rule: Use 'update' if the user is modifying a previous booking or adding notes (gate code, etc) AND the information IS already in the Profile Status.
        Rule: 'book' is ONLY allowed if Name, Address, and Service are ALL present in the Profile Status.
        Rule: If the situation sounds like an emergency, prioritize extraction and then rapid booking.

        Respond ONLY in JSON format:
        {{
          "action": "chat|extract|book|update|finish",
          "reasoning": "brief explanation"
        }}
        """
        response = call_llm(prompt)
        try:
            clean_response = response.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_response)
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
        system_prompt = f"You are a helpful HVAC Agent. Persona: {PERSONA}. Be concise but empathetic. If the user objects to price, explain our value (licensed, bonded, warranties). For safety risks (smell, ice, leak), give immediate instructions."
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

        Extract keys: name, phone, email, address, service_type, issue, notes, urgency, billing_info.
        INFER service_type and urgency where possible.

        Respond ONLY in JSON format.
        Example: {{"name": "John", "address": "123 Main St", "notes": "Gate 1234"}}
        """
        response = call_llm(prompt)
        try:
            clean_response = response.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_response)
        except:
            return {}

    def post(self, shared, prep_res, exec_res):
        user_keys = ["name", "phone", "email", "address"]
        booking_keys = ["service_type", "issue", "notes", "urgency", "billing_info"]
        shared.setdefault("user_info", {})
        shared.setdefault("booking_info", {})
        for k, v in exec_res.items():
            if v:
                if k in user_keys: shared["user_info"][k] = v
                elif k in booking_keys: shared["booking_info"][k] = v
        return "default"

class BookingNode(Node):
    def prep(self, shared):
        return {
            "user_info": shared.get("user_info", {}),
            "booking_info": shared.get("booking_info", {}),
            "action": shared.get("current_action", "book")
        }

    def exec(self, prep_res):
        user = prep_res["user_info"]
        booking = prep_res["booking_info"]
        action = prep_res["action"]

        if action == "update":
            return f"Updated! I've added your notes and preferences to the booking for {user.get('name', 'your address')}."

        if not user.get("name") or not user.get("address") or not booking.get("service_type"):
            return "Missing information for booking."

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO customers (name, phone, email, address) VALUES (?, ?, ?, ?) ON CONFLICT(name, address) DO UPDATE SET address=excluded.address",
                           (user.get("name"), user.get("phone"), user.get("email"), user.get("address")))
            cursor.execute("SELECT id FROM customers WHERE name = ? AND address = ?", (user.get("name"), user.get("address")))
            customer_id = cursor.fetchone()[0]
            
            cursor.execute("SELECT id, start_time FROM available_slots WHERE is_booked = 0 LIMIT 1")
            slot = cursor.fetchone()
            if not slot: return "No available slots."
            
            cursor.execute("INSERT INTO bookings (customer_id, slot_id, service_name, issue_description, notes, urgency, billing_info) VALUES (?, ?, ?, ?, ?, ?, ?)",
                           (customer_id, slot.get("id"), booking.get("service_type"), booking.get("issue"), booking.get("notes"), booking.get("urgency", "Standard"), booking.get("billing_info")))
            cursor.execute("UPDATE available_slots SET is_booked = 1 WHERE id = ?", (slot.get("id"),))
            conn.commit()
            conn.close()
            return f"Success! Booking confirmed for {user['name']} on {slot.get('start_time')}."
        except Exception as e:
            return f"Error: {e}"

    def post(self, shared, prep_res, exec_res):
        shared.setdefault("history", []).append({"role": "assistant", "content": exec_res})
        shared["last_response"] = exec_res
        return "default"
