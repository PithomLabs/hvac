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

def main():
    # Ensure database is initialized
    init_db()

    model = os.environ.get("LLM_MODEL")
    if not model:
        model = "openai/gpt-4o-mini"
    
    agent_description = f"""
{BOLD}{BLUE}--- HVAC Booking AI Assistant ---{RESET}
Powered by {YELLOW}PocketFlow{RESET} and {YELLOW}OpenRouter{RESET} {YELLOW}{model}{RESET}.

I am an AI-powered HVAC service assistant designed to help you book repairs, maintenance, 
and consultations with extreme professionalism and empathy. I can handle:
- {GREEN}Emergency Repairs{RESET} (leaks, smells, extreme weather outages)
- {GREEN}Maintenance Tune-ups{RESET}
- {GREEN}New System Estimates{RESET}
- {GREEN}Booking Modifications{RESET} (rescheduling, gate codes)

{BOLD}Initial Prompt:{RESET} What is the issue you're facing, and how urgent is it?
"""
    print(agent_description)

    shared = {
        "history": [],
        "user_info": {},
        "booking_info": {},
        "current_action": None,
        "last_response": "",
        "extraction_attempts": 0
    }

    flow = create_hvac_agent_flow()

    
    import select
    
    while True:
        try:
            # PACING & BUFFER FLUSH: Ensure the user is ready
            import sys
            sys.stdout.flush()
            time.sleep(0.5)
            
            print(f"\n{BOLD}You:{RESET} ", end="", flush=True)
            
            lines = []
            while True:
                # Wait for input with timeout (0.8s threshold)
                ready, _, _ = select.select([sys.stdin], [], [], 0.8 if lines else None)
                if ready:
                    line = sys.stdin.readline()
                    if not line: # EOF
                        break
                    stripped = line.strip()
                    if stripped:
                        lines.append(stripped)
                    if not lines: continue
                else:
                    if lines:
                        break
            
            if not lines:
                continue
                
            user_input = " ".join(lines)
            
            if user_input.upper() in ["STOP", "HALT", "EXIT", "QUIT", "BYE"]:
                print(f"\n{BLUE}Agent:{RESET} Session terminated as requested. Have a wonderful and comfortable day! Goodbye.")
                break
            
            # Add user message to history
            shared["history"].append({"role": "user", "content": user_input})
            shared["last_response"] = "" # Reset for this turn
            shared["extraction_attempts"] = 0 # Reset attempts for new fresh input
            
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
