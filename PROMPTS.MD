1. Upload doc to NotebookLM
2. what is the high level strategy in designing effective AI conversational agent per attached file? I want to focus first with design only (not implementation)
3. How do the core abstractions of node, shared store, and flow function?
4. How do I use pocketflow to design a conversational AI agent for HVAC booking process, what are the components that need to be used and how to train the agent effectively?
5. What are the dos and donts while using pocketflow framework for effective design of AI conversational chat agents?
6. You are AI-powered conversational agent that assists customers in booking HVAC services

Create a set of realistic conversation scenarios (at least 100) that cover various customer needs, questions, and potential issues related to booking an HVAC service. Aim for diversity in problem types (e.g., AC repair, furnace maintenance, installation), property types, location, and customer interactions.

The purpose of this is to serve as foundational input for AI conversational agent  implementation later

7. Without worrying about implementation details for now, how exactly would you test this expert AI chat agent for HVAC booking services per our conversation and context mentioned so far?

Combine pocketflow_to_prompt.txt and NotebookLM_prompt.md

8. Based on the source file, write a comprehensive plan only on how to implement the AI-powered conversation agent to assist customer in booking HVAC services. Read the objective, tasks and deliverables per source


Implementation Stage
-------------------- 

Prompts to Antigravity (Gemini 3 Flash)

9. Ensure that you follow AGENTS.MD for Beads guidance since your additional role is to be a reliable, thorough coding assistant that never loses track of work, always maintains quality, and keeps the human in full control of all decisions.

Read the PocketFlow-main subfolder for PocketFlow codebase and analyze it thoroughly

Read CHALLENGE.MD for the task, objective and deliverables that need to be done

Read CONTEXT_ENGINEERING.txt VERY CAREFULLY for the implementation plan

READ GEMINI.MD for PocketFlow guidance

From all of that context, analyze the inconsistencies in CONTEXT_ENGINEERING.txt and write your detailed comprehensive plan as IMPLEMENTATION_PLAN.MD. Code will be written under agent subfolder later

Ask if you need clarifications, I will say next when to proceed with the actual coding implementation

10. Do you have any questions to clarify? I will say next when to proceed with the implementation

I have a few specific questions to ensure the implementation aligns perfectly with your expectations before we start coding:

LLM Choice: I see GEMINI_API_KEY and OPENROUTER_API_KEY in your environment. Would you prefer me to use Gemini (e.g., gemini-2.0-flash) or a specific model via OpenRouter for the agent's "brain"?
Mocking vs. Realism: For the BookingNode, should I create a simple mock database or CSV to simulate appointment availability, or is a simple terminal print-out of the "success" state sufficient for this initial version?
Git Initialization: The bd sync command requires a Git repository. Since the current directory isn't initialized yet, would you like me to run git init and create an initial commit to enable the full Beads workflow?
Scenario Storage: When generating the 100+ scenarios, would you like them stored as a single YAML file (e.g., data/scenarios.yaml) for reference, or should they be integrated directly into the testing suite?
Agent Persona: Beyond the HVAC expertise, should the agent have a specific "mood" or brand voice (e.g., "Always empathetic", "Quick and professional", "Highly detailed")?
I'm ready to proceed once these are addressed. Just say "next" when you want me to start the implementation!

