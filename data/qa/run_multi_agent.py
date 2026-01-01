import os
import sys
import json
import re

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from agent.nodes import DecideNode, ChatNode, ExtractionNode, BookingNode
from agent.database import init_db
from utils.call_llm import call_llm

def simulate_human(history, scenario_context):
    """Simulates a human response using the nvidia/nemotron-nano-9b-v2:free model."""
    system_prompt = f"""
    You are a customer in an HVAC service booking scenario. 
    Context: {scenario_context}
    
    Goal: Your goal is to get your HVAC issue resolved by interacting with the agent. 
    Stay in character. Do not provide all information at once unless asked.
    Respond as a human would in a chat. Keep it concise.
    """
    
    # Temporarily set model for human simulation
    os.environ["LLM_MODEL"] = "nvidia/nemotron-nano-9b-v2:free"
    response = call_llm(history, system_prompt=system_prompt)
    return response

def run_simulation(scenario_file):
    scenario_path = os.path.join(os.path.dirname(__file__), scenario_file)
    with open(scenario_path, 'r') as f:
        scenario_content = f.read()

    print(f"Starting simulation for: {scenario_file}")
    
    # Initialize DB
    init_db()

    shared = {
        "history": [],
        "user_info": {},
        "booking_info": {},
        "current_action": None,
        "last_response": "",
        "extraction_attempts": 0
    }

    # Extract initial human message from scenario if possible, or start with a prompt
    initial_match = re.search(r'\*\*Human\*\*:\s*(.*)', scenario_content)
    human_msg = initial_match.group(1) if initial_match else "Hi, I need help with my AC."

    decider = DecideNode()
    chat = ChatNode()
    extractor = ExtractionNode()
    booker = BookingNode()

    conversation_log = []

    # Simulation Loop
    for turn in range(15): # Max 15 turns
        print(f"Turn {turn + 1}: Human is speaking...")
        conversation_log.append(f"**Human**: {human_msg}")
        shared["history"].append({"role": "user", "content": human_msg})

        # Process Agent turns (Decide -> Extract/Chat/Book)
        print("Agent is thinking...")
        
        # We need to ensure the Agent uses its assigned model
        os.environ["LLM_MODEL"] = "xiaomi/mimo-v2-flash:free"
        
        max_internal_steps = 5
        for _ in range(max_internal_steps):
            action = decider.run(shared)
            if action == "chat":
                chat.run(shared)
                agent_res = shared["last_response"]
                break
            elif action == "extract":
                extractor.run(shared)
            elif action == "book" or action == "update":
                booker.run(shared)
                agent_res = shared["last_response"]
                break
            elif action == "finish":
                agent_res = "Thank you for contacting us. Goodbye!"
                shared["current_action"] = "finish"
                break
        else:
            agent_res = "How can I help you further?"

        conversation_log.append(f"\n**AI Agent**: {agent_res}\n")
        print(f"Agent responded: {agent_res[:50]}...")

        if shared.get("current_action") == "finish":
            break

        # Human Simulator Turn
        human_msg = simulate_human(shared["history"], scenario_content)
        
    # Save results
    output_filename = scenario_file.replace(".md", "_multi_agent.md")
    output_path = os.path.join(os.path.dirname(__file__), "multi_agent", output_filename)
    
    with open(output_path, 'w') as f:
        f.write("\n".join(conversation_log))
    
    print(f"Simulation completed. Saved to: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_simulation(sys.argv[1])
    else:
        run_simulation("gold_a1_ac_dead.md")
