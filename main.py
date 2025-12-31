import sys
import os
import time

# Add root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent.flow import create_hvac_agent_flow
from agent.database import init_db

# ANSI Escape Codes for "Premium" CLI look
BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"

AGENT_DESCRIPTION = f"""
{BOLD}{BLUE}--- HVAC Booking AI Assistant ---{RESET}
Powered by {YELLOW}PocketFlow{RESET} and {YELLOW}OpenRouter{RESET}.

I am an AI-powered HVAC service assistant designed to help you book repairs, maintenance, 
and consultations with extreme professionalism and empathy. I can handle:
- {GREEN}Emergency Repairs{RESET} (leaks, smells, extreme weather outages)
- {GREEN}Maintenance Tune-ups{RESET}
- {GREEN}New System Estimates{RESET}
- {GREEN}Booking Modifications{RESET} (rescheduling, gate codes)

{BOLD}Initial Prompt:{RESET} What is the issue you're facing, and how urgent is it?
"""

def main():
    # Ensure database is initialized
    init_db()

    shared = {
        "history": [],
        "user_info": {},
        "booking_info": {},
        "current_action": None,
        "last_response": "",
        "extraction_attempts": 0
    }

    flow = create_hvac_agent_flow()

    print(AGENT_DESCRIPTION)
    
    while True:
        try:
            user_input = input(f"\n{BOLD}You:{RESET} ")
            if not user_input.strip():
                continue
                
            if user_input.lower() in ["exit", "quit", "bye"]:
                print(f"\n{BLUE}Agent:{RESET} It was a pleasure assisting you. Have a wonderful and comfortable day! Goodbye.")
                break
            
            # Add user message to history
            shared["history"].append({"role": "user", "content": user_input})
            shared["last_response"] = "" # Reset for this turn
            
            # Run the flow
            flow.run(shared)
            
            response = shared.get("last_response")
            if response:
                print(f"\n{BLUE}Agent:{RESET} {response}")
            else:
                print(f"\n{BLUE}Agent:{RESET} I'm processing your request. Could you please tell me more about the heating issue?")
            
            if shared.get("current_action") == "finish":
                print(f"\n{BOLD}(Closing session...){RESET}")
                break
                
        except KeyboardInterrupt:
            print(f"\n\n{RED}Session interrupted.{RESET} Goodbye.")
            break
        except Exception as e:
            import traceback
            print(f"\n{RED}CRITICAL SYSTEM ERROR:{RESET}")
            traceback.print_exc()
            print(f"{RED}Error Details: {e}{RESET}")
            break

if __name__ == "__main__":
    main()
