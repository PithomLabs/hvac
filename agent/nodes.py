import sys
import os
import json
import traceback

# Add project root and PocketFlow to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "PocketFlow-main"))

from pocketflow import Node
from utils.call_llm import call_llm
from agent.database import get_db_connection

# Premium CLI Look helpers
BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

PERSONA = "Always empathetic but also quick and professional, highly detailed if need be."

def debug_log(msg):
    print(f"  {YELLOW}{msg}{RESET}", flush=True)

class DecideNode(Node):
    def prep(self, shared):
        return {
            "history": shared.get("history", []),
            "user_info": shared.get("user_info", {}),
            "booking_info": shared.get("booking_info", {}),
            "extraction_attempts": shared.get("extraction_attempts", 0)
        }

    def exec(self, prep_res):
        history = prep_res["history"]
        user = prep_res["user_info"]
        booking = prep_res["booking_info"]
        attempts = prep_res["extraction_attempts"]
        
        debug_log(f"[DECIDER]: User Info: {user}")
        debug_log(f"[DECIDER]: Booking Info: {booking}")
        debug_log("[DECIDER]: Analyzing state...")
        
        last_msg = history[-1]["content"] if history else ""
        attempts = shared.get("extraction_attempts", 0)

        prompt = f"""
        You are the 'Manager' of an HVAC Booking Agent. Decide the NEXT ACTION.
        
        ACTIONS:
        - 'chat': Default action for conversation, giving advice, or asking for missing info.
        - 'extract': ONLY if the user just provided specific details in their LAST MESSAGE that are currently 'Missing'.
        - 'book': ONLY if Name, Address, and Service are all present.
        - 'finish': Select this IMMEDIATELY if the booking is confirmed AND the user is satisfied.

        CURRENT DATA:
        - Name: {user.get('name', 'Missing')}
        - Address: {user.get('address', 'Missing')}
        - Service: {booking.get('service_type', 'Missing')}
        - Extraction Attempts: {attempts}

        LAST MESSAGE: "{last_msg}"

        Rules:
        1. If 'Extraction Attempts' is >= 1, select 'chat' (the info is not in the message or already extracted).
        2. If Name or Address is 'Missing', you cannot 'book'.
        3. If the user is reporting a problem, select 'chat' first for advice.
        4. Be decisive. Prefer 'finish' if done.

        Respond ONLY in JSON: {{"action": "chat|extract|book|finish", "reasoning": "..."}}
        """
        try:
            response = call_llm(prompt)
            clean_response = response.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_response)
        except Exception as e:
            debug_log(f"[DECIDER ERROR]: {e}")
            return {"action": "chat", "reasoning": f"Error: {e}"}

    def post(self, shared, prep_res, exec_res):
        action = exec_res.get("action", "chat")
        shared["current_action"] = action
        shared["reasoning"] = exec_res.get("reasoning")
        debug_log(f"[DECIDER]: Selected Action -> {action}")
        return action

class ChatNode(Node):
    def prep(self, shared):
        return shared.get("history", [])

    def exec(self, history):
        debug_log("[CHAT]: Thinking...")
        system_prompt = f"You are a helpful HVAC Agent. Persona: {PERSONA}. If the user asks a technical question or reports a safety issue, give advice and guide to booking."
        try:
            response = call_llm(history, system_prompt=system_prompt)
            debug_log(f"[CHAT]: LLM Response received ({len(response)} chars)")
            return response
        except Exception as e:
            debug_log(f"[CHAT ERROR]: {e}")
            traceback.print_exc()
            return f"I'm sorry, I'm having trouble connecting to my brain right now. Error: {e}"

    def post(self, shared, prep_res, exec_res):
        shared.setdefault("history", []).append({"role": "assistant", "content": exec_res})
        shared["last_response"] = exec_res
        shared["extraction_attempts"] = 0
        debug_log("[CHAT]: Post-turn completed.")
        return "default"

class ExtractionNode(Node):
    def prep(self, shared):
        return {
            "last_message": shared["history"][-1]["content"] if shared["history"] else "",
            "current_user_info": shared.get("user_info", {}),
            "current_booking_info": shared.get("booking_info", {})
        }

    def exec(self, prep_res):
        debug_log("[EXTRACTOR]: Processing message...")
        prompt = f"""
        Extract HVAC-related information from the user's last message.
        Use ONLY the following keys in your JSON response:
        - name: Full name of the customer
        - address: Full service address
        - phone: Phone number
        - email: Email address
        - service_type: Type of service (e.g., Repair, Maintenance, Quote)
        - issue: Description of the problem
        - urgency: (High, Medium, Low)

        Last message: {prep_res['last_message']}
        Current User Info: {json.dumps(prep_res['current_user_info'])}
        Current Booking Info: {json.dumps(prep_res['current_booking_info'])}

        JSON format only. If information is missing, use null.
        """
        try:
            response = call_llm(prompt)
            clean_response = response.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_response)
        except Exception as e:
            debug_log(f"[EXTRACTOR ERROR]: {e}")
            return {}

    def post(self, shared, prep_res, exec_res):
        user_keys = ["name", "phone", "email", "address"]
        booking_keys = ["service_type", "issue", "notes", "urgency"]
        shared.setdefault("user_info", {})
        shared.setdefault("booking_info", {})
        
        debug_log(f"[EXTRACTOR]: LLM Output: {exec_res}")
        info_added = False
        for k, v in exec_res.items():
            if v and v != "null":
                if k in user_keys:
                    if shared["user_info"].get(k) != v:
                        shared["user_info"][k] = v
                        info_added = True
                        debug_log(f"[EXTRACTOR]: Added USER info: {k}={v}")
                elif k in booking_keys:
                    if shared["booking_info"].get(k) != v:
                        shared["booking_info"][k] = v
                        info_added = True
                        debug_log(f"[EXTRACTOR]: Added BOOKING info: {k}={v}")
        
        if not info_added:
            shared["extraction_attempts"] = shared.get("extraction_attempts", 0) + 1
        else:
            shared["extraction_attempts"] = 0
            
        debug_log(f"[EXTRACTOR]: Finished. info_added={info_added}")
        debug_log(f"[EXTRACTOR]: Current user_info: {shared['user_info']}")
        return "default"

class BookingNode(Node):
    def prep(self, shared):
        return {
            "user_info": shared.get("user_info", {}),
            "booking_info": shared.get("booking_info", {}),
            "action": shared.get("current_action", "book")
        }

    def exec(self, prep_res):
        debug_log("[BOOKER]: Finalizing...")
        user = prep_res["user_info"]
        booking = prep_res["booking_info"]
        action = prep_res["action"]

        if action == "update":
            return f"Updated! I've added those details to your file for {user.get('name', 'your property')}."

        missing = []
        if not user.get("name"): missing.append("your name")
        if not user.get("address"): missing.append("your address")
        if not booking.get("service_type"): missing.append("the service type")

        if missing:
            already_have = []
            if user.get("name"): already_have.append(f"name as {user['name']}")
            if user.get("address"): already_have.append(f"address as {user['address']}")
            
            msg = f"I'm almost ready to book that for you."
            if already_have:
                msg += f" I have your " + " and ".join(already_have) + "."
            msg += f" I just need " + " and ".join(missing) + " to finish up."
            return msg

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO customers (name, phone, email, address) VALUES (?, ?, ?, ?) ON CONFLICT DO NOTHING",
                           (user.get("name"), user.get("phone"), user.get("email"), user.get("address")))
            cursor.execute("SELECT id FROM customers WHERE name = ? AND address = ?", (user.get("name"), user.get("address")))
            row = cursor.fetchone()
            if row:
                customer_id = row[0]
                cursor.execute("SELECT id, start_time FROM available_slots WHERE is_booked = 0 LIMIT 1")
                slot = cursor.fetchone()
                if slot:
                    cursor.execute("INSERT INTO bookings (customer_id, slot_id, service_name, issue_description, urgency) VALUES (?, ?, ?, ?, ?)",
                                   (customer_id, slot[0], booking.get("service_type"), booking.get("issue"), booking.get("urgency", "Standard")))
                    cursor.execute("UPDATE available_slots SET is_booked = 1 WHERE id = ?", (slot[0],))
                    conn.commit()
                    conn.close()
                    return f"Success! Verified and booked for {user['name']} on {slot[1]}."
            conn.close()
            return "Booking system confirmed the details, but I'm finalizing the slot. One moment."
        except Exception as e:
            debug_log(f"[BOOKER ERROR]: {e}")
            return f"Error finalizing: {e}"

    def post(self, shared, prep_res, exec_res):
        shared.setdefault("history", []).append({"role": "assistant", "content": exec_res})
        shared["last_response"] = exec_res
        shared["extraction_attempts"] = 0
        debug_log("[BOOKER]: Done.")
        return "default"
