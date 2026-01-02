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
RED = "\033[91m"
RESET = "\033[0m"

def load_prompt(filename):
    path = os.path.join(os.path.dirname(__file__), "prompts", filename)
    with open(path, "r") as f:
        return f.read().strip()

PERSONA = "Empathetic, professional, and efficient. No fluff, just direct help."

def log_debug(msg, color=RESET):
    """Prints debug information only if APP_ENV is set to 'qa'."""
    if os.getenv("APP_ENV", "prod").lower() == "qa":
        print(f"{color}{msg}{RESET}", flush=True)




class DecideNode(Node):
    def prep(self, shared):
        # CONTEXT FILTER: Strip system noise from history before LLM sees it
        raw_history = shared.get("history", [])
        filtered_history = [m for m in raw_history if not m["content"].startswith("[SYSTEM]")]
        
        return {
            "history": filtered_history,
            "user_info": shared.get("user_info", {}),
            "booking_info": shared.get("booking_info", {}),
            "extraction_attempts": shared.get("extraction_attempts", 0),
            "confirmed": shared.get("booking_info", {}).get("confirmed", False),
            "phase2_delivered": shared.get("booking_info", {}).get("phase2_delivered", False)
        }

    def exec(self, prep_res):
        history = prep_res["history"]
        user = prep_res["user_info"]
        booking = prep_res["booking_info"]
        attempts = prep_res["extraction_attempts"]
        
        log_debug(f"[DEBUG] DecideNode.exec start: attempts={attempts}, history_len={len(history)}", BLUE)
        
        # STOP-TURN GUARDRAIL: Prevent infinite extraction loops
        MAX_EXTRACTION_ATTEMPTS = 3
        if attempts >= MAX_EXTRACTION_ATTEMPTS:
            # Force chat if stalled on extraction
            shared["extraction_attempts"] = 0
            return "chat"

        # PACING DELAY: Give the UI a beat to breathe
        import time
        # EAGER EXTRACTION: If we have new data in its first attempt, force extract
        if attempts == 0 and len(history) > 0:
            last_msg = history[-1]["content"].lower()
            log_debug(f"[DEBUG] DecideNode: Eager Eval on '{last_msg[:30]}...'", BLUE)
            # Match common address suffixes as whole words
            import re
            suffixes = ["st", "ave", "dr", "rd", "drive", "way", "zip", "code", "street", "avenue", "road", "court", "ct"]
            keyword_match = any(re.search(fr"\b{k}\b", last_msg) for k in suffixes)
            log_debug(f"[DEBUG] DecideNode: Keyword match={keyword_match}, No Addr={not user.get('address')}", BLUE)
            if keyword_match:
                if not user.get("address"):
                    log_debug("[DEBUG] DecideNode: Eagerly picking 'extract' for suspected address", BLUE)
                    return {"action": "extract", "reasoning": f"Detected address keyword in '{last_msg[:30]}...'"}
        
        time.sleep(1)
        
        last_msg = history[-1]["content"] if history else ""

        system_prompt = load_prompt("decide_system.txt")
        prompt = f"""
        {system_prompt}

        CURRENT DATA:
        - Name: {user.get('name', 'Missing')}
        - Address: {user.get('address', 'Missing')}
        - Service: {booking.get('service_type', 'Missing')}
        - Booking Confirmed: {'Yes' if prep_res.get('confirmed') else 'No'}
        - Phase 2 Delivered: {'Yes' if prep_res.get('phase2_delivered') else 'No'}
        - Extraction Attempts: {attempts}

        LAST MESSAGE: "{last_msg}"

        Respond ONLY in JSON: {{"action": "chat|extract|book|finish", "reasoning": "..."}}
        """
        
        # LOG DATA FOR DEBUGGING
        log_debug(f"[DEBUG] DecideNode Status: Confirmed={prep_res.get('confirmed')}, P2Delivered={prep_res.get('phase2_delivered')}, Name={user.get('name')}, Addr={user.get('address')}", BLUE)
        try:
            log_debug(f"[DEBUG] DecideNode calling LLM (model={os.getenv('LLM_MODEL')})", BLUE)
            response = call_llm(prompt)
            log_debug("[DEBUG] DecideNode LLM returned", GREEN)
            clean_response = response.replace("```json", "").replace("```", "").strip()
            result = json.loads(clean_response)
            log_debug(f"[DEBUG] DecideNode decided: {result.get('action')}", GREEN)
            
            # CLOSURE SENTRY (Refined): Force 'chat' if there's a question mark OR uncertainty keyword
            closure_keywords = ["?", "wait", "hold", "but", "actually", "just to be clear", "one more thing"]
            if result.get("action") == "finish":
                if any(kw in last_msg.lower() for kw in closure_keywords):
                    log_debug(f"[DEBUG] DecideNode: Overriding 'finish' due to closure keywords: {last_msg[:30]}...", YELLOW)
                    result["action"] = "chat"
                    result["reasoning"] = f"Detected unresolved user concern: {last_msg[:50]}"
                
            return result
        except Exception as e:
            log_debug(f"[DEBUG] DecideNode ERROR: {e}", YELLOW)
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
            "confirmed": shared.get("booking_info", {}).get("confirmed", False),
            "phase2_delivered": shared.get("booking_info", {}).get("phase2_delivered", False),
            "hb_number": shared.get("booking_info", {}).get("hb_number", "HB-XXXX")
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
    - Phase 2 (Confirmation) Delivered: {'Yes' if prep_res.get('phase2_delivered') else 'No'}
    - Customer Name: {user.get('name', 'Missing')}
    - Service Address: {user.get('address', 'Missing')}
    - Service Type: {booking.get('service_type', 'Missing')}
    - Confirmation Number: {prep_res.get('hb_number')}
    """
        
        system_prompt = f"{system_main}\n\n{context_block}\n\n{examples}"
        try:
            # THINKING PATTERN: First, check for safety questions in a "thought" block
            thought_prompt = f"Analyze the conversation. Did the user ask a safety or technical question (e.g. 'Should I turn it off?')? If so, provide the answer. Then, determine if we are in Phase 2 (Confirmation). Respond ONLY with the combined final text for the customer."
            
            # We use the system prompt as the primary guide, and the thought_prompt to nudge specific behavior
            full_system = f"{system_prompt}\n\nCRITICAL: {thought_prompt}"
            
            response = call_llm(history, system_prompt=full_system)
            return response.strip()
        except Exception as e:
            traceback.print_exc()
            return f"I'm sorry, I'm having trouble connecting to my brain right now. Error: {e}"

    def post(self, shared, prep_res, exec_res):
        shared.setdefault("history", []).append({"role": "assistant", "content": exec_res})
        shared["last_response"] = exec_res
        shared["extraction_attempts"] = 0
        
        # If agent delivers the confirmation script, mark as delivered
        confirmation_keywords = ["Success!", "HB-", "confirmation number", "booked for", "confirmed for", "appointment is set"]
        if any(kw in exec_res for kw in confirmation_keywords):
            shared.setdefault("booking_info", {})["confirmed"] = True
            shared["booking_info"]["phase2_delivered"] = True
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
            log_debug(f"[DEBUG] ExtractionNode calling LLM. Last message: {prep_res['last_message'][:20]}...", BLUE)
            response = call_llm(prompt)
            log_debug(f"[DEBUG] ExtractionNode LLM raw response: {response[:100]}...", GREEN)
            clean_response = response.replace("```json", "").replace("```", "").strip()
            result = json.loads(clean_response)
            log_debug(f"[DEBUG] ExtractionNode extracted: {result}", GREEN)
            return result
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
        
        # BUG-1.5 FIX: Immediate service area validation
        # Check IMMEDIATELY after address extraction, BEFORE asking for time slots
        address = shared["user_info"].get("address")
        if address and not shared.get("service_area_checked"):
            from utils.service_area import is_in_service_area
            
            if not is_in_service_area(address):
                log_debug(f"[DEBUG] ExtractionNode: Address '{address}' is OUT of service area", RED)
                shared["service_area_rejected"] = True
                shared["service_area_checked"] = True
                return "service_area_reject"  # New action for immediate rejection
            else:
                log_debug(f"[DEBUG] ExtractionNode: Address '{address}' is IN service area", GREEN)
                shared["service_area_checked"] = True
            
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
        confirmation_keywords = ["Success!", "HB-", "confirmation number", "booked for", "confirmed for", "appointment is set"]
        if any(kw in exec_res for kw in confirmation_keywords):
            booking = shared.setdefault("booking_info", {})
            booking["confirmed"] = True
            
            # PERSISTENT HB NUMBER: Generate once at booking time
            import random
            if "hb_number" not in booking:
                booking["hb_number"] = f"HB-{random.randint(1000, 9999)}"
                
        return "default"

class ServiceAreaRejectNode(Node):
    """
    BUG-1.5 FIX: Immediate service area rejection node.
    Triggers when address is detected as out-of-area during extraction.
    Prevents asking for time slots before rejecting.
    """
    def exec(self, _):
        from utils.service_area import get_service_area_message
        return get_service_area_message()
    
    def post(self, shared, prep_res, exec_res):
        # Append the rejection message to history
        shared["history"].append({
            "role": "assistant",
            "content": exec_res
        })
        # Terminal response - no further action needed
        shared["last_response"] = exec_res
        return "finish"  # Move to finish node

class SupervisorNode(Node):
    """
    SUPERVISOR PATTERN: A final gatekeeper that silences system messages 
    and handles clean flow termination.
    """
    def prep(self, shared):
        return {
            "last_response": shared.get("last_response", ""),
            "action": shared.get("current_action", "")
        }

    def exec(self, prep_res):
        msg = prep_res["last_response"]
        action = prep_res["action"]

        # SILENCE LEAKS: Use regex to strip any bracketed system tags
        import re
        msg = re.sub(r"\[SYSTEM\].*?(\n|$)", "", msg).strip()
        msg = re.sub(r"\[DEBUG\].*?(\n|$)", "", msg).strip()
        
        # If the entire message was system tags, silence it
        if not msg and "[SYSTEM]" in prep_res["last_response"]:
            log_debug(f"[DEBUG] Supervisor: Silencing handover leak entirely.", YELLOW)
            return ""
        
        # TERMINATION: Ensure *END OF CONVERSATION* exists if we are finishing
        if action == "finish" and "*END OF CONVERSATION*" not in msg:
            return f"{msg}\n\n*END OF CONVERSATION*" if msg else "*END OF CONVERSATION*"
            
        return msg

    def post(self, shared, prep_res, exec_res):
        shared["last_response"] = exec_res
        # Stop everything: Supervisor is the absolute end of a functional turn
        return "default"
