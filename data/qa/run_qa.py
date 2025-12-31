import sys
import os
import re
import json
import sqlite3

# Add project root and PocketFlow to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "PocketFlow-main"))

from agent.nodes import DecideNode, ChatNode, ExtractionNode, BookingNode
from agent.database import init_db

def parse_markdown_conv(file_path):
    """Parses a markdown conversation file into a list of messages."""
    messages = []
    if not os.path.exists(file_path):
        return []
    with open(file_path, 'r') as f:
        content = f.read()
    
    parts = re.split(r'\*\*(Human|AI Agent)\*\*:', content)
    for i in range(1, len(parts), 2):
        role = "user" if parts[i] == "Human" else "assistant"
        text = parts[i+1].strip()
        messages.append({"role": role, "content": text})
    
    return messages

def log_to_db(db_file, query, params=()):
    """Helper to run a query and immediately close connection to avoid locking."""
    conn = sqlite3.connect(db_file, timeout=30)
    cursor = conn.cursor()
    cursor.execute(query, params)
    res = None
    if query.strip().upper().startswith("INSERT"):
        res = cursor.lastrowid
    elif query.strip().upper().startswith("SELECT"):
        res = cursor.fetchall()
    conn.commit()
    conn.close()
    return res

def run_test_scenario(file_name, db_file):
    print(f"\n--- Running QA Scenario: {file_name} ---")
    file_path = os.path.join(os.path.dirname(__file__), file_name)
    history = parse_markdown_conv(file_path)
    
    if not history:
        print(f"Skipping {file_name}: No conversation found.")
        return

    user_inputs = [m['content'] for m in history if m['role'] == "user"]
    
    init_db()
    shared = {
        "history": [],
        "user_info": {},
        "booking_info": {},
        "current_action": None,
        "last_response": ""
    }

    decider = DecideNode()
    chat = ChatNode()
    extractor = ExtractionNode()
    booker = BookingNode()

    # Create QA Run record
    run_id = log_to_db(db_file, "INSERT INTO qa_test_runs (scenario_file) VALUES (?)", (file_name,))

    scenario_logs = []
    status = "FAIL"

    try:
        for user_msg in user_inputs:
            log_entry = f"[USER]: {user_msg}"
            print(log_entry)
            scenario_logs.append(log_entry)
            shared["history"].append({"role": "user", "content": user_msg})
            
            # Action Loop
            max_steps = 5
            for _ in range(max_steps):
                action = decider.run(shared)
                log_entry = f"  [DECIDER]: {action}"
                print(log_entry)
                scenario_logs.append(log_entry)
                
                # Log step details
                details = json.dumps({"shared": shared}, default=lambda o: "<non-serializable>")
                log_to_db(db_file, "INSERT INTO qa_test_results (run_id, node_name, action, details) VALUES (?, ?, ?, ?)",
                          (run_id, "DecideNode", action, details))
                
                if action == "chat":
                    chat.run(shared)
                    log_entry = f"  [AGENT]: {shared['last_response']}"
                    print(log_entry)
                    scenario_logs.append(log_entry)
                    break
                elif action == "extract":
                    extractor.run(shared)
                    log_entry = f"  [EXTRACTOR]: User={shared['user_info']}, Booking={shared['booking_info']}"
                    print(log_entry)
                    scenario_logs.append(log_entry)
                    continue 
                elif action == "book":
                    booker.run(shared)
                    log_entry = f"  [BOOKER]: {shared['last_response']}"
                    print(log_entry)
                    scenario_logs.append(log_entry)
                    if "Success!" in shared['last_response']:
                        status = "PASS"
                    continue
                elif action == "finish":
                    print("  [SYSTEM]: Scenario Finished.")
                    break
            
            if shared.get("current_action") == "finish":
                break
        
        # Final update
        log_to_db(db_file, "UPDATE qa_test_runs SET status = ?, logs = ? WHERE id = ?",
                  (status, "\n".join(scenario_logs), run_id))
    except Exception as e:
        print(f"Error during scenario run: {e}")
        log_to_db(db_file, "UPDATE qa_test_runs SET status = 'ERROR', logs = ? WHERE id = ?",
                  (f"Exception: {e}\n" + "\n".join(scenario_logs), run_id))
    
    print(f"\n[VERIFICATION]: Result={status}")

if __name__ == "__main__":
    db_file = os.path.join(os.path.dirname(__file__), "..", "..", "agent", "hvac_booking.db")
    
    if len(sys.argv) > 1:
        # Run specific files provided as arguments
        for arg in sys.argv[1:]:
            if os.path.exists(os.path.join(os.path.dirname(__file__), arg)):
                run_test_scenario(arg, db_file)
            else:
                print(f"Error: File {arg} not found.")
    else:
        # Default: Test with scenarios 1 to 10
        for i in range(1, 11):
            file_name = f"test_conv_{i:02d}.md"
            if os.path.exists(os.path.join(os.path.dirname(__file__), file_name)):
                run_test_scenario(file_name, db_file)
