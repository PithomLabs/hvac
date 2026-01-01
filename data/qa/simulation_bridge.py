import subprocess
import os
import sys
import time
import select

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

# ANSI Escape Codes for Bridge output
CYAN = "\033[96m"
YELLOW = "\033[93m"
MAGENTA = "\033[95m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"
GREEN = "\033[92m"

def get_versioned_path(scenario_file):
    """Returns the next versioned path for the output file."""
    base_name = os.path.basename(scenario_file).replace(".md", "_multi_agent")
    output_dir = os.path.join(os.path.dirname(os.path.abspath(scenario_file)), "multi_agent")
    os.makedirs(output_dir, exist_ok=True)
    
    version = 1
    while True:
        path = os.path.join(output_dir, f"{base_name}_v{version}.md")
        if not os.path.exists(path):
            return path
        version += 1

def log_to_file(file_path, text, is_new=False):
    """Appends text to the markdown file in real-time."""
    mode = 'w' if is_new else 'a'
    with open(file_path, mode) as f:
        if is_new:
            f.write("# Multi-Agent Conversation Simulation\n\n")
        f.write(text + "\n\n")

def run_simulation(scenario_file):
    # If scenario_file is already an absolute path or relative from root, use it directly
    if os.path.exists(scenario_file):
        scenario_path = os.path.abspath(scenario_file)
    else:
        # Try relative to the script's directory (old logic)
        scenario_path = os.path.join(os.path.dirname(__file__), scenario_file)

    if not os.path.exists(scenario_path):
        print(f"Error: Scenario file {scenario_file} was not found (checked {scenario_path})")
        return

    print(f"{CYAN}{BOLD}--- Starting Multi-Agent Bridge ---{RESET}")
    print(f"{CYAN}Scenario: {scenario_file}{RESET}\n")

    # Environment for HVAC Agent (Mimo)
    agent_env = os.environ.copy()
    agent_env["LLM_MODEL"] = "xiaomi/mimo-v2-flash:free"
    agent_env["PYTHONUNBUFFERED"] = "1"

    # Environment for Human Simulator (Nemotron)
    human_env = os.environ.copy()
    human_env["LLM_MODEL"] = "nvidia/nemotron-nano-9b-v2:free"
    human_env["PYTHONUNBUFFERED"] = "1"

    # Spawn processes
    # agent/main.py is the production HVAC agent
    agent_proc = subprocess.Popen(
        [sys.executable, "agent/main.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=agent_env,
        text=True,
        bufsize=1,
        cwd=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    )

    # agent/human_simulator.py is the customer simulation
    human_proc = subprocess.Popen(
        [sys.executable, "agent/human_simulator.py", scenario_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=human_env,
        text=True,
        bufsize=1,
        cwd=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    )

    def clean_agent_output(line):
        """Removes the 'Agent: ' prefix and ANSI codes if necessary."""
        # Simple cleanup for the bridge logic
        line = re.sub(r'\x1b\[[0-9;]*m', '', line) # Strip ANSI codes
        if "Agent:" in line:
            return line.split("Agent:", 1)[1].strip()
        return ""

    import re
    output_path = get_versioned_path(scenario_path)
    log_to_file(output_path, f"**Scenario**: {scenario_file}", is_new=True)

    # Read scenario content for first line extraction
    with open(scenario_path, 'r') as f:
        scenario_content = f.read()
    
    # Extract first line marked as **Human**
    first_human_match = re.search(r'\*\*Human\*\*:\s*(.*)', scenario_content)
    if first_human_match:
        first_msg = first_human_match.group(1).strip()
    else:
        first_msg = "Hi, I need help."

    try:
        # Step 1: Wait for Initial Agent Prompt
        current_line = ""
        print(f"{CYAN}[BRIDGE]: Waiting for Agent to initialize...{RESET}")
        while True:
            char = agent_proc.stdout.read(1)
            if not char: break
            print(char, end="", flush=True) if char != "\n" else print(f"\n{BLUE}[TERMINAL 1 - AGENT]:{RESET} ", end="", flush=True)
            current_line += char
            if "You:" in current_line:
                break
            if char == "\n": current_line = ""

        # Step 2: Initiate with First Message from Scenario
        print(f"{MAGENTA}{BOLD}[TERMINAL 2 - HUMAN]:{RESET} {first_msg}")
        log_to_file(output_path, f"**Human**: {first_msg}")
        
        # Pass to Agent
        agent_proc.stdin.write(first_msg + "\n")
        agent_proc.stdin.flush()
        
        # Main Relay Loop
        while True:
            # --- Read from Agent ---
            agent_response_full = []
            current_line = ""
            is_collecting_agent_msg = False
            
            while True:
                char = agent_proc.stdout.read(1)
                if not char: break
                
                # Print everything in real-time
                print(char, end="", flush=True) if char != "\n" else print(f"\n{BLUE}[TERMINAL 1 - AGENT]:{RESET} ", end="", flush=True)
                
                current_line += char
                if char == "\n":
                    if "Agent:" in current_line:
                        is_collecting_agent_msg = True
                        agent_response_full.append(clean_agent_output(current_line))
                    elif is_collecting_agent_msg and "You:" not in current_line:
                        clean_l = re.sub(r'\x1b\[[0-9;]*m', '', current_line).strip()
                        if clean_l: agent_response_full.append(clean_l)
                    current_line = ""
                
                if "You:" in current_line:
                    # End of agent turn
                    agent_msg = "\n".join(agent_response_full).strip()
                    if agent_msg:
                        log_to_file(output_path, f"**AI Agent**: {agent_msg}")
                        # Relay to human
                        try:
                            human_proc.stdin.write(agent_msg + "\n")
                            human_proc.stdin.write("---END_OF_TURN---\n")
                            human_proc.stdin.flush()
                        except BrokenPipeError:
                            break
                    break
            
            if agent_proc.poll() is not None or human_proc.poll() is not None:
                break

            # --- Read from Human ---
            human_response_acc = []
            while True:
                human_line = human_proc.stdout.readline()
                if not human_line: break
                
                msg = human_line.strip()
                if msg:
                    print(f"{MAGENTA}{BOLD}[TERMINAL 2 - HUMAN]:{RESET} {msg}")
                    log_to_file(output_path, f"**Human**: {msg}")
                    # Relay to agent
                    try:
                        agent_proc.stdin.write(msg + "\n")
                        agent_proc.stdin.flush()
                    except BrokenPipeError:
                        break
                    break # Single turn from human
            
            if agent_proc.poll() is not None or human_proc.poll() is not None:
                break

    except KeyboardInterrupt:
        print(f"\n{YELLOW}Simulation interrupted by user.{RESET}")
    finally:
        agent_proc.terminate()
        human_proc.terminate()
        
        print(f"\n{GREEN}{BOLD}Conversation logged to: {output_path}{RESET}")
        print(f"{CYAN}{BOLD}--- Simulation Finished ---{RESET}")

if __name__ == "__main__":
    scenario = sys.argv[1] if len(sys.argv) > 1 else "data/qa/gold_a1_ac_dead.md"
    run_simulation(scenario)
