import sys
import os

# Add root to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from agent.flow import create_hvac_agent_flow
from agent.database import init_db

def main():
    # Ensure database is initialized
    init_db()

    shared = {
        "history": [],
        "user_info": {},
        "booking_info": {},
        "current_action": None,
        "last_response": ""
    }

    flow = create_hvac_agent_flow()

    print("--- HVAC Booking Agent ---")
    print("Welcome! How can I help you today?")
    
    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.lower() in ["exit", "quit", "bye"]:
                print("Agent: Goodbye! Have a great day.")
                break
            
            # Add user message to history
            shared["history"].append({"role": "user", "content": user_input})
            
            # Run one iteration of the flow
            # Note: The flow runs until it hits a node with no successor or an action with no transition.
            # In our case, the nodes loop back to DecideNode. 
            # We want the flow to run until it has produced a response to the user.
            
            # Since Decider routes to Chat/Extract/Book which all produce a response or loop,
            # we need to be careful not to enter an infinite loop in a single .run() call if we don't handle termination.
            
            # Actually, standard PocketFlow Flow.run() will continue until it reaches a node without a valid successor for its action.
            # Our nodes loop back. We might want to run the flow for a specific number of steps or until a 'response' is generated.
            
            # For a CLI, it's often better to run the flow until it reaches a 'wait for input' logic.
            # In PocketFlow, we can run the flow and it will traverse nodes.
            
            # Let's adjust the nodes to return "finish" or something if they want to stop.
            # For this simple CLI, we'll let the flow run one cycle.
            
            flow.run(shared)
            
            if shared.get("current_action") == "finish":
                print("\nAgent: It was a pleasure assisting you. Goodbye!")
                break
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
