import sys
import os
import json
import random
import asyncio

# Add project root and PocketFlow to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "PocketFlow-main"))

from pocketflow import AsyncParallelBatchNode, AsyncFlow
from utils.call_llm_async import call_llm_async

class ScenarioGeneratorNode(AsyncParallelBatchNode):
    async def prep_async(self, shared):
        # Base templates/variables
        problems = [
            "AC blowing warm air", 
            "Furnace making banging noise", 
            "Thermostat screen is blank", 
            "Water leaking from indoor unit", 
            "Strange burning smell when heater turns on",
            "Want to schedule annual maintenance",
            "Interest in new heat pump installation"
        ]
        moods = ["Normal", "Frustrated", "Urgent", "Polite", "Skeptical"]
        locations = ["Residential Home", "Apartment", "Small Office", "Rental Property"]

        tasks = []
        # Generate 105 tasks
        for problem in problems:
            for mood in moods:
                for location in random.sample(locations, 3):
                    tasks.append({
                        "problem": problem,
                        "mood": mood,
                        "location": location
                    })
        return tasks

    async def exec_async(self, task):
        prompt = f"""
        Generate a realistic, single-turn user request for an HVAC booking agent.
        
        Context:
        - Problem: {task['problem']}
        - Mood: {task['mood']}
        - Property Type: {task['location']}

        The output should be a single user message. Make it diverse and natural.
        
        Output ONLY the user message text.
        """
        message = await call_llm_async(prompt)
        return {
            "prompt_vars": task,
            "user_message": message.strip().strip('"')
        }

    async def post_async(self, shared, prep_res, exec_res_list):
        shared["generated_scenarios"] = exec_res_list
        return "default"

async def main():
    os.makedirs("data", exist_ok=True)
    shared = {"generated_scenarios": []}
    
    generator = ScenarioGeneratorNode()
    flow = AsyncFlow(start=generator)
    
    print("Generating 100+ scenarios in parallel...")
    await flow.run_async(shared)
    
    output_path = "data/scenarios.json"
    with open(output_path, "w") as f:
        json.dump(shared["generated_scenarios"], f, indent=2)
    
    print(f"Successfully generated {len(shared['generated_scenarios'])} scenarios in {output_path}")

if __name__ == "__main__":
    asyncio.run(main())
