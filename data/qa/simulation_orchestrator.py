import os
import sys
import re
import json

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from agent.flow import create_hvac_agent_flow
from agent.database import init_db
from utils.call_llm import call_llm

# ANSI Colors
CYAN = "\033[96m"
MAGENTA = "\033[95m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"
GREEN = "\033[92m"

def get_versioned_path(scenario_file):
    base_name = os.path.basename(scenario_file).replace(".md", "_multi_agent")
    output_dir = os.path.join(os.path.dirname(os.path.abspath(scenario_file)), "multi_agent")
    os.makedirs(output_dir, exist_ok=True)
    version = 1
    while True:
        path = os.path.join(output_dir, f"{base_name}_v{version}.md")
        if not os.path.exists(path): return path
        version += 1

def log_to_file(file_path, text, is_new=False):
    mode = 'w' if is_new else 'a'
    with open(file_path, mode) as f:
        if is_new:
            f.write("# Multi-Agent Conversation Simulation (Single-Process)\n\n")
        f.write(text + "\n\n")

def run_human_simulator(history, scenario_content):
    """Simulates the human side directly using LLM call."""
    human_intent_match = re.search(r'## Human Intent\n(.*?)\n##', scenario_content, re.DOTALL)
    human_intent = human_intent_match.group(1).strip() if human_intent_match else "You are a customer needing HVAC repair."
    
    formatted_history = ""
    for turn in history:
        role = "Agent" if turn["role"] == "assistant" else "Human"
        formatted_history += f"{role}: {turn['content']}\n"

    system_prompt = f"""
    You are a REAL PERSON (a customer) interacting with an HVAC booking agent.
    STRICT RULES:
    1. NEVER say "I am an AI". Respond naturally.
    2. Your goal: {human_intent}
    3. If the agent has confirmed the booking and you have no more questions, finish the conversation.
    4. If you are done, respond with exactly: [FINISHED]
    """
    
    prompt = f"Previous conversation:\n{formatted_history}\n\nAgent just spoke. What is your response? (Respond with [FINISHED] if done)"
    
    os.environ["LLM_MODEL"] = "nvidia/nemotron-nano-9b-v2:free"
    response = call_llm(prompt, system_prompt=system_prompt).strip()
    return response

def run_orchestration(scenario_file):
    init_db()
    output_path = get_versioned_path(scenario_file)
    log_to_file(output_path, f"**Scenario**: {scenario_file}", is_new=True)

    with open(scenario_file, 'r') as f:
        scenario_content = f.read()

    first_human_match = re.search(r'\*\*Human\*\*:\s*(.*)', scenario_content)
    first_msg = first_human_match.group(1).strip() if first_human_match else "Hi, I need help."

    shared = {
        "history": [], "user_info": {}, "booking_info": {},
        "current_action": None, "last_response": "", "extraction_attempts": 0
    }
    
    flow = create_hvac_agent_flow()

    print(f"{CYAN}--- Simulation Started: {output_path} ---{RESET}")
    
    # Human starts
    log_to_file(output_path, f"**Human**: {first_msg}")
    shared["history"].append({"role": "user", "content": first_msg})

    turn_count = 0
    while turn_count < 10: # Balanced turn limit
        # --- AGENT TURN ---
        os.environ["LLM_MODEL"] = "xiaomi/mimo-v2-flash:free"
        flow.run(shared)
        agent_msg = shared.get("last_response", "")
        
        if agent_msg:
            log_to_file(output_path, f"**AI Agent**: {agent_msg}")
            print(f"{BLUE}Agent responded. ({len(agent_msg)} chars){RESET}")
        
        if shared.get("current_action") == "finish":
            print(f"{GREEN}Agent ended simulation.{RESET}")
            break

        # --- HUMAN TURN ---
        human_msg = run_human_simulator(shared["history"], scenario_content)
        
        if "[FINISHED]" in human_msg:
            print(f"{GREEN}Human ended simulation.{RESET}")
            break
            
        if human_msg:
            log_to_file(output_path, f"**Human**: {human_msg}")
            shared["history"].append({"role": "user", "content": human_msg})
            print(f"{MAGENTA}Human responded.{RESET}")
        
        turn_count += 1

    print(f"\n{GREEN}{BOLD}Simulation finished.{RESET}")

if __name__ == "__main__":
    scenario = sys.argv[1] if len(sys.argv) > 1 else "data/qa/gold_a1_ac_dead.md"
    run_orchestration(scenario)
