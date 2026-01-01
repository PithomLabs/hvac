import os
import sys
import re

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.call_llm import call_llm

# ANSI Escape Codes for "Human" look
MAGENTA = "\033[95m"
BOLD = "\033[1m"
RESET = "\033[0m"

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 human_simulator.py <scenario_file>")
        sys.exit(1)

    scenario_file = sys.argv[1]
    with open(scenario_file, 'r') as f:
        scenario_content = f.read()

    # Filter scenario content to only show human intent/lines to avoid role-reversal
    human_lines = re.findall(r'\*\*Human\*\*:\s*(.*)', scenario_content)
    human_intent = "\n".join(human_lines)

    system_prompt = f"""
    You are a REAL PERSON (a customer) in a chat with an HVAC company. 
    YOUR STORY/SITUATION:
    {human_intent}
    
    CRITICAL INSTRUCTIONS:
    1. You are NOT an AI. You are a human customer who is feeling the emotions of the situation (e.g., stressed about the heat/baby, relieved to get help, etc.).
    2. SPEAK LIKE A HUMAN: Use natural, conversational language. Avoid robotic lists or overly formal structures. 
    3. Respond ONLY with your chat message. Never prefix with "Human:" or your name.
    4. Stay focused on your intent: {human_intent[:100]}...
    5. Do not give all your info (phone, address) until asked by the agent.
    """
    
    history = []
    
    # We wait for the bridge to send us the first message via stdin if it wants us to know it was sent,
    # OR we just wait for the Agent's response.
    # To keep history in sync, the bridge will send the Agent's first response.
    
    while True:
        try:
            # Wait for Agent's response from stdin (could be multi-line)
            lines = []
            while True:
                line = sys.stdin.readline()
                if not line or line.strip() == "---END_OF_TURN---":
                    break
                lines.append(line)
            
            if not lines:
                if not line: # EOF
                    break
                continue
            
            agent_input = "".join(lines).strip()
            if not agent_input:
                continue

            # Check for goodbye or exit
            if any(word in agent_input.lower() for word in ["goodbye", "have a wonderful day", "closing session"]):
                break

            history.append({"role": "user", "content": agent_input})
            
            # Generate Human Simulator Response
            os.environ["LLM_MODEL"] = "nvidia/nemotron-nano-9b-v2:free"
            human_response = call_llm(history, system_prompt=system_prompt)
            
            print(human_response, flush=True)
            history.append({"role": "assistant", "content": human_response})
            
        except EOFError:
            break
        except Exception as e:
            # Don't print to stdout to avoid confusing the bridge
            sys.stderr.write(f"Error in human simulator: {e}\n")
            break

if __name__ == "__main__":
    main()
