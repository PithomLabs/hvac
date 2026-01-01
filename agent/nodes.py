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

def load_prompt(filename):
    path = os.path.join(os.path.dirname(__file__), "prompts", filename)
    with open(path, "r") as f:
        return f.read().strip()

PERSONA = "Empathetic, professional, and efficient. No fluff, just direct help."



class DecideNode(Node):
    def prep(self, shared):
        return {
            "history": shared.get("history", []),
            "user_info": shared.get("user_info", {}),
            "booking_info": shared.get("booking_info", {}),
            "extraction_attempts": shared.get("extraction_attempts", 0),
            "confirmed": shared.get("booking_info", {}).get("confirmed", False)
        }

    def exec(self, prep_res):
        history = prep_res["history"]
        user = prep_res["user_info"]
        booking = prep_res["booking_info"]
        attempts = prep_res["extraction_attempts"]
        
        
        last_msg = history[-1]["content"] if history else ""

        system_prompt = load_prompt("decide_system.txt")
        prompt = f"""
        {system_prompt}

        CURRENT DATA:
        - Name: {user.get('name', 'Missing')}
        - Address: {user.get('address', 'Missing')}
        - Service: {booking.get('service_type', 'Missing')}
        - Booking Confirmed: {'Yes' if prep_res.get('confirmed') else 'No'}
        - Extraction Attempts: {attempts}

        LAST MESSAGE: "{last_msg}"

        Respond ONLY in JSON: {{"action": "chat|extract|book|finish", "reasoning": "..."}}
        """
        try:
            print(f"{BLUE}[DEBUG] DecideNode calling LLM (model={os.getenv('LLM_MODEL')}){RESET}", flush=True)
            response = call_llm(prompt)
            print(f"{GREEN}[DEBUG] DecideNode LLM returned{RESET}", flush=True)
            clean_response = response.replace("```json", "").replace("```", "").strip()
            result = json.loads(clean_response)
            print(f"{GREEN}[DEBUG] DecideNode decided: {result.get('action')}{RESET}", flush=True)
            return result
        except Exception as e:
            print(f"{YELLOW}[DEBUG] DecideNode ERROR: {e}{RESET}", flush=True)
            return {"action": "chat", "reasoning": f"Error: {e}"}

    def post(self, shared, prep_res, exec_res):
        shared["current_action"] = exec_res["action"]
        shared["action_reasoning"] = exec_res.get("reasoning", "N/A")
        if exec_res["action"] == "extract":
            shared["extraction_attempts"] = shared.get("extraction_attempts", 0) + 1
        if exec_res["action"] == "finish":
            shared["last_response"] = "*END OF CONVERSATION*"
        return exec_res["action"]

class ChatNode(Node):
    def prep(self, shared):
        return {
            "history": shared.get("history", []),
            "user_info": shared.get("user_info", {}),
            "booking_info": shared.get("booking_info", {}),
            "confirmed": shared.get("booking_info", {}).get("confirmed", False)
        }

    def exec(self, prep_res):
        history = prep_res["history"]
        user = prep_res["user_info"]
        booking = prep_res["booking_info"]
        confirmed = 'Yes' if prep_res["confirmed"] else 'No'
        
        system_main = load_prompt("chat_system.txt")
        examples = load_prompt("chat_examples.txt")
        
        context_block = f"""
        CURRENT BOOKING STATUS:
        - Booking Confirmed: {confirmed}
        - Customer Name: {user.get('name', 'Missing')}
        - Service Address: {user.get('address', 'Missing')}
        - Service Type: {booking.get('service_type', 'Missing')}
        """
        
        system_prompt = f"{system_main}\n\n{context_block}\n\n{examples}"
        try:
            response = call_llm(history, system_prompt=system_prompt)
            pass
            return response.strip()
        except Exception as e:
            pass
            traceback.print_exc()
            return f"I'm sorry, I'm having trouble connecting to my brain right now. Error: {e}"

    def post(self, shared, prep_res, exec_res):
        shared.setdefault("history", []).append({"role": "assistant", "content": exec_res})
        shared["last_response"] = exec_res
        shared["extraction_attempts"] = 0
        if "Success!" in exec_res:
            shared.setdefault("booking_info", {})["confirmed"] = True
        return "default"

class ExtractionNode(Node):
    def prep(self, shared):
        return {
            "last_message": shared["history"][-1]["content"] if shared["history"] else "",
            "current_user_info": shared.get("user_info", {}),
            "current_booking_info": shared.get("booking_info", {})
        }

    def exec(self, prep_res):
        system_prompt = load_prompt("extract_system.txt")
        prompt = f"""
        {system_prompt}

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
            pass
            return {}

    def post(self, shared, prep_res, exec_res):
        user_keys = ["name", "phone", "email", "address"]
        booking_keys = ["service_type", "issue", "notes", "urgency"]
        shared.setdefault("user_info", {})
        shared.setdefault("booking_info", {})
        
        info_added = False
        for k, v in exec_res.items():
            if v and v != "null":
                if k in user_keys:
                    if shared["user_info"].get(k) != v:
                        shared["user_info"][k] = v
                        info_added = True
                elif k in booking_keys:
                    if shared["booking_info"].get(k) != v:
                        shared["booking_info"][k] = v
                        info_added = True
        
        if not info_added:
            shared["extraction_attempts"] = shared.get("extraction_attempts", 0) + 1
        else:
            shared["extraction_attempts"] = 0
            
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

        # MOCK BOOKING (SQLite disabled due to locking issues)
        import random
        import datetime
        
        # Generate mock booking details
        tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        slot_time = f"{tomorrow} 14:00"
        
        # SILENT BOOKING - return system flag, not user-facing text
        # The ChatNode will handle the user-facing Phase 2 confirmation
        return f"[SYSTEM] Booking confirmed for {user['name']} on {slot_time}."
        
        # ORIGINAL SQLITE CODE (DISABLED - keeping for reference)
        # try:
        #     conn = get_db_connection()
        #     cursor = conn.cursor()
        #     cursor.execute("INSERT INTO customers (name, phone, email, address) VALUES (?, ?, ?, ?) ON CONFLICT DO NOTHING",
        #                    (user.get("name"), user.get("phone"), user.get("email"), user.get("address")))
        #     cursor.execute("SELECT id FROM customers WHERE name = ? AND address = ?", (user.get("name"), user.get("address")))
        #     row = cursor.fetchone()
        #     if row:
        #         customer_id = row[0]
        #         cursor.execute("SELECT id, start_time FROM available_slots WHERE is_booked = 0 LIMIT 1")
        #         slot = cursor.fetchone()
        #         if slot:
        #             cursor.execute("INSERT INTO bookings (customer_id, slot_id, service_name, issue_description, urgency) VALUES (?, ?, ?, ?, ?)",
        #                            (customer_id, slot[0], booking.get("service_type"), booking.get("issue"), booking.get("urgency", "Standard")))
        #             cursor.execute("UPDATE available_slots SET is_booked = 1 WHERE id = ?", (slot[0],))
        #             conn.commit()
        #             conn.close()
        #             return f"Success! Verified and booked for {user['name']} on {slot[1]}."
        #     conn.close()
        #     return "Booking system confirmed the details, but I'm finalizing the slot. One moment."
        # except Exception as e:
        #     return f"Error finalizing: {e}"

    def post(self, shared, prep_res, exec_res):
        shared.setdefault("history", []).append({"role": "assistant", "content": exec_res})
        shared["last_response"] = exec_res
        shared["extraction_attempts"] = 0
        # Update confirmation status when booking succeeds
        # Check for both old format ("Success!") and new format ("[SYSTEM]")
        if "Success!" in exec_res or "[SYSTEM] Booking confirmed" in exec_res:
            shared.setdefault("booking_info", {})["confirmed"] = True
        return "default"
