import os
import subprocess
import glob

def run_batch():
    scenarios = sorted(glob.glob("data/qa/gold_*.md"))
    print(f"Found {len(scenarios)} scenarios to run.")
    
    for i, scenario in enumerate(scenarios):
        print(f"\n[{i+1}/{len(scenarios)}] Running simulation for: {scenario}")
        # Run the orchestrator as a subprocess for isolation
        # Using -u for unbuffered output
        subprocess.run(["python3", "data/qa/simulation_orchestrator.py", scenario], check=False)
        print(f"[{i+1}/{len(scenarios)}] Finished.")

if __name__ == "__main__":
    run_batch()
