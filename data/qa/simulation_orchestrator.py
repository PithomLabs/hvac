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

def run_human_simulator(history, scenario_content, force_continue=False):
    """Simulates the human side directly using LLM call."""
    human_intent_match = re.search(r'## Human Intent\n(.*?)\n##', scenario_content, re.DOTALL)
    human_intent = human_intent_match.group(1).strip() if human_intent_match else "You are a customer needing HVAC repair."
    
    formatted_history = ""
    for turn in history:
        role = "Agent" if turn["role"] == "assistant" else "Human"
        formatted_history += f"{role}: {turn['content']}\n"

    human_name = human_intent.split('is ')[-1] if 'is ' in human_intent else 'Sarah Jenkins'
    system_prompt = f"""
    You are {human_name}, a REAL customer needing HVAC help.
    STRICT RULES:
    1. NEVER say "I am an AI". Act 100% human.
    2. Respond ONLY with what you would say to the agent.
    3. NEVER prefix your response with "{human_name}:", "Human:", or any role.
    4. NEVER role-play as the agent or summarize the chat.
    5. You are NOT an expert. You are just a stressed customer.
    6. Respond in SHORT, natural sentences (1-2 sentences).
    7. If the agent confirmed your booking and you are satisfied, say thanks/goodbye and add [FINISHED].
    """
    
    if force_continue:
        system_prompt += "\n7. IMPORTANT: We need more information. Ask a question about the technician's experience, the potential repair cost, or some other detail to keep things moving."

    prompt = f"### CONVERSATION HISTORY\n{formatted_history}\n\nAJENT JUST SPOKE. {human_name}, what is your reply to the agent?"
    
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
    min_turns = 5
    while turn_count < 15: # Max turns
        # --- AGENT TURN ---
        os.environ["LLM_MODEL"] = "xiaomi/mimo-v2-flash:free"
        flow.run(shared)
        agent_msg = shared.get("last_response", "")
        
        if agent_msg:
            log_to_file(output_path, f"**AI Agent**: {agent_msg}")
            print(f"{BLUE}Agent responded. ({len(agent_msg)} chars){RESET}")
        
        if shared.get("current_action") == "finish" and turn_count >= min_turns:
            print(f"{GREEN}Agent ended simulation (Turn {turn_count+1}).{RESET}")
            break

        # --- HUMAN TURN ---
        force_continue = turn_count < min_turns
        human_msg = run_human_simulator(shared["history"], scenario_content, force_continue=force_continue)
        
        is_finished = "[FINISHED]" in human_msg
        clean_msg = human_msg.replace("[FINISHED]", "").strip()
        
        if clean_msg:
            log_to_file(output_path, f"**Human**: {clean_msg}")
            shared["history"].append({"role": "user", "content": clean_msg})
            print(f"{MAGENTA}Human responded. (Turn {turn_count+1}){RESET}")
        
        if is_finished and not force_continue:
            print(f"{GREEN}Human ended simulation (Turn {turn_count+1}).{RESET}")
            break
        
        turn_count += 1

    print(f"\n{GREEN}{BOLD}Simulation finished.{RESET}")

if __name__ == "__main__":
    scenario = sys.argv[1] if len(sys.argv) > 1 else "data/qa/gold_a1_ac_dead.md"
    run_orchestration(scenario)
