# Prompt Engineering Challenge: HVAC Service Booking Agent

## Objective

Design and refine a prompt for an AI-powered conversational agent that assists customers in booking HVAC (Heating, Ventilation, and Air Conditioning) services. The agent should guide users through a structured booking process, ensuring all necessary information is collected and service requirements are met.

## Tasks

**Initial Agent Implementation**

Implement an agent CLI in python using an LLM wrapper of your choice—eg. [https://openai.github.io/openai-agents-python/](https://openai.github.io/openai-agents-python/).

**Sample Conversation Generation**

Create a set of realistic conversation scenarios (at least 10\) that cover various customer needs, questions, and potential issues related to booking an HVAC service. Aim for diversity in problem types (e.g., AC repair, furnace maintenance, installation), property types, location, and customer interactions.

**Prompt Crafting and Documentation**

Develop an initial prompt for the agent that instructs it on how to guide the booking process.

Document your prompt design strategy. Explain the reasoning behind your prompt's structure, instructions, and any specific techniques used.

**Agent Execution and Analysis**

Run the generated sample conversations through the agent using your initial prompt.

Record and analyze the agent's output. Identify areas where the agent performs well and areas that need improvement.

**Prompt Refinement and Iteration**

Refine your prompt based on the analysis of the initial run.

Document the changes you made and explain the rationale behind them.

Repeat the execution and analysis process with the refined prompt.

Continue iterating until the agent demonstrates a significant improvement in its ability to handle the booking process effectively.

Visually represent the prompt refinement process (e.g., using diagrams, flowcharts) to illustrate the evolution of your approach.

## Deliverables

Github repository containing:

1) the Python code for the agent CLI.  
     
2) Readme containing:  
* The generated sample conversations.  
* The initial prompt and its design strategy.  
* The analysis of the initial agent run.  
* The refined prompts and their rationales.  
* The analysis of subsequent agent runs.  
* Visual representations of the prompt refinement process.  
* A final prompt that represents the best result of the refinement process.

# Preparation (NotebookLM)

## Input: Upload this doc to NotebookLM

## **Prompt**: what is the high level strategy in designing effective AI conversational agent per attached file? I want to focus first with design only (not implementation)

Based on the provided text, the high-level strategy for designing an effective AI conversational agent centers on an **iterative, scenario-driven approach** rather than a "set it and forget it" methodology. The design process is structured around creating diverse user simulations to test and refine the agent's instructions continuously.

Here is the high-level design strategy outlined in the source:

### **1\. Scenario-First Design**

Before or alongside drafting the actual prompt, the strategy requires the creation of **realistic conversation scenarios**. You are expected to generate at least 10 distinct scenarios that cover a wide range of variables to ensure robustness. These scenarios should include:

* **Diverse User Needs:** Issues such as AC repair, furnace maintenance, or new installations.  
* **Contextual Variations:** Different property types and locations.  
* **Interaction Styles:** Various questions, potential issues, and customer behaviors that might occur during a booking.

  ### **2\. Structured Prompt Crafting**

The core design involves developing a specific **prompt strategy** that instructs the agent on how to manage the interaction. The agent must be designed to **guide the user through a structured booking process**, ensuring that it collects all necessary information and validates service requirements. You must also document the **reasoning behind the structure**, instructions, and any specific prompt engineering techniques utilized to achieve these goals.

### **3\. Iterative Refinement Loop**

The design strategy emphasizes that the initial prompt is just a starting point. The effectiveness of the agent is achieved through a cycle of **execution, analysis, and refinement**:

* **Testing:** Run the pre-generated conversation scenarios through the agent using the initial prompt.  
* **Analysis:** Record the outputs to identify where the agent succeeds and where it fails to handle the booking process effectively.  
* **Modification:** Refine the prompt based on this analysis, documenting the rationale for every change made.  
* **Repetition:** Continue this cycle until the agent demonstrates "significant improvement" in handling the tasks.

  ### **4\. Visualization of Logic**

To ensure the design is logical and traceable, the strategy includes **visually representing the refinement process**. This involves using diagrams or flowcharts to map out how the prompt approach evolved over time, shifting from the initial design to the final, optimized version.

---

**Analogy:** Designing this agent is similar to **training a new employee through role-playing**. First, you write a script of difficult customer situations (the conversation scenarios). Then, you give the employee a rulebook (the initial prompt) and see how they handle those situations. When they make a mistake, you don't just hope they get better; you edit the rulebook to be clearer (refinement) and test them again on the same situations until they get it right every time.

## Input: Transcript of PocketFlow video from YouTube (https://www.youtube.com/watch?v=0Zr3NwcvpA0)

### Prompt 1: Upload transcript to NotebookLM

### **Prompt 2**: How do the core abstractions of node, shared store, and flow function?

Based on the provided sources, the **PocketFlow** framework is built on a minimalist philosophy that reduces LLM application development to three fundamental abstractions: the **Node**, the **Shared Store**, and the **Flow**,.

Here is how each component functions:

### **1\. The Node (The Worker)**

The Node is the "atom" of the system, acting as a single, hyper-focused worker responsible for a specific unit of work,. It operates on a strict three-step lifecycle designed to separate data fetching from core logic:

* **Prep (Pre-process):** This is the "get your ingredients" phase. The `prep` function reads from the Shared Store and selects only the specific data needed for the task, gathering the raw materials,.  
* **Exec (Execute):** This is the "cooking" phase where the core work happens, such as doing math, calling an API, or prompting an LLM,. Crucially, this step runs in an **isolated bubble**; it receives only the data handed to it by `prep` and cannot see the Shared Store directly. This isolation ensures the code remains clean and easy to test.  
* **Post (Post-process):** This is the cleanup phase. The `post` function takes the result from `exec`, writes it back to the Shared Store for future nodes to use, and returns a simple string called an **action**. This action string serves as a status update (e.g., "success" or "error") that tells the system where to go next.

**Reliability and Variations:**

* **Retries and Fallbacks:** Nodes have built-in resilience. You can configure `max_retries` and `wait` times so that if the `exec` step fails (e.g., an API is down), the node automatically retries. If it continues to fail, an `exec_fallback` function kicks in to handle the error gracefully without crashing the application.  
* **Batching:** There are specialized nodes for bulk processing. A **Batch Node** processes a list of items sequentially using a simple loop. An **Async Parallel Batch Node** processes items simultaneously by using `async` and `await` to turn the loop into a concurrent operation, significantly increasing speed,.

### **2\. The Shared Store (The Memory)**

The Shared Store acts as the "assembly line" or communication channel between nodes.

* **Structure:** It is not a complex database or message queue; it is simply a global **Python dictionary**.  
* **Function:** It serves as the single source of truth for the workflow. One node writes a result (e.g., `result: 42`) to this "central whiteboard," and the next node reads that value to perform its own task.  
* **Simplicity:** Because it is just a dictionary, you can easily debug the application by printing the dictionary at any time to see the exact state of the workflow.

### **3\. The Flow (The Orchestrator)**

The Flow acts as the "master recipe" or "factory foreman" that dictates the sequence of operations,.

* **Transitions:** The Flow determines which node runs next based on the **action string** returned by the current node's `post` method.  
* **Routing Logic:**  
  * **Default Path:** A simple double arrow connection (`Node A >> Node B`) tells the flow to move sequentially from A to B.  
  * **Branching:** You can define named transitions. For example, if a "Review Node" returns the action "approved," the flow moves to the "Payment Node". Under the hood, this uses a "tiny address book" called `successors` to look up where to go based on the action received,.  
* **Nesting:** A powerful "meta idea" in PocketFlow is that **a Flow is also a Node**. This allows you to bundle a sequence of nodes into a single unit and treat it as one step in a larger assembly line, enabling the creation of complex applications from small, reusable parts.

### **Summary Analogy**

To visualize the system, you can think of it as a kitchen:

* The **Shared Store** is the kitchen countertop where ingredients and finished dishes are placed.  
* The **Nodes** are the chefs. They grab ingredients from the counter (`prep`), cook them at their station (`exec`), and place the finished dish back on the counter (`post`),.  
* The **Flow** is the recipe that tells the chefs the order in which they should cook.

By combining these simple elements—loops, branches, and memory—you can build everything from simple chatbots to complex, autonomous agents,.

## Prompt: How do I use pocketflow to design a conversational AI agent for HVAC booking process, what are the components that need to be used and how to train the agent effectively?

Based on the PocketFlow framework, designing a conversational AI agent for an HVAC booking process does not require complex libraries or massive dependencies. Instead, you build it using a "design pattern" where an agent is simply a flow with a loop and a branch.

Here is how you can use PocketFlow to design, componentize, and effectively "train" (guide) your HVAC agent.

### **1\. Designing the Agent (The Architecture)**

To create an HVAC booking agent, you need to structure your application as a **Directed Graph**. The core logic revolves around a central "brain" that decides whether to answer a general question (e.g., "How much is a tune-up?") or proceed with a booking task (e.g., "I need a repair Tuesday").

**The Core Components You Need:**

* **The Shared Store (The Memory):** You start with a simple Python dictionary. For an HVAC context, this dictionary should hold:

  1. `messages`: The history of the conversation (User and Assistant inputs).  
  2. `booking_details`: A dictionary to store extracted data (e.g., `{"customer_name": "...", "issue": "AC not cooling", "address": "..."}`).  
  3. `state`: To track if the booking is confirmed.  
* **The Nodes (The Workers):** You will need to implement specific nodes to handle different parts of the process.

  1. **The Decide/Router Node (The Brain):** This is the most critical component. Its `exec` step sends the conversation history to the LLM and asks, "Based on the user's last message, what should I do next?".  
     * It should return an action string like: `chat` (for general questions), `extract_info` (if the user provided details), or `book_appointment` (if all info is ready).  
  2. **The Chat Node:** If the action is `chat`, this node runs. It functions like a standard chatbot, taking the history and generating a helpful response.  
  3. **The Extraction Node (Structured Data):** If the user says, "My AC is broken, I live at 123 Main St," this node runs. Its job is to parse this messy text into clean data. You should use **YAML** for this output because it handles newlines and strings much better than JSON.  
  4. **The Booking Action Node (The Tool):** Once all data is collected, this node executes the "booking." In a real scenario, this node's `exec` function would call your calendar API. In PocketFlow, this is treated as a "tool" node that acts and then reports back.  
* **The Flow (The Wiring):** You connect these nodes in a loop. The *Decide Node* sits at the center. It branches out to the *Chat*, *Extraction*, or *Booking* nodes, which perform their task and then loop back to the *Decide Node* to await the next user input.

### **2\. How to "Train" the Agent Effectively**

In the PocketFlow philosophy, you do not technically "train" (fine-tune) the model in the traditional sense. Instead, you use **Prompt Engineering** and **Task Decomposition** within your nodes to guide the generic LLM (like GPT-4) to behave like an HVAC expert.

**Strategies for Effectiveness:**

* **Task Decomposition (The Assembly Line):** Do not ask one node to handle chatting, extracting address, and booking all at once. If you do, you will get a "rambling wall of text". Split the work: let the *Extraction Node* focus solely on getting the address and issue, while the *Chat Node* focuses on being polite. This makes the system reliable.  
* **Few-Shot Prompting:** In your *Decide Node* and *Extraction Node*, provide clear examples in the prompt (the `prep` or `exec` phase).  
  * *Example for Extraction:* explicitly show the LLM the input "My heater died" and the desired output `issue: heater failure`. This technique, known as "few-shot prompting," is highly effective for ensuring the LLM follows instructions.  
* **Speak YAML, Not JSON:** When asking the agent to verify booking details or extract addresses, explicitly ask for the output in **YAML format**. LLMs are trained on human language, and YAML is more "human-readable" and forgiving than JSON, preventing syntax errors that could crash your booking flow.  
* **Resilience via Retries:** HVAC booking APIs might fail, or the LLM might hallucinate a format. Use the `max_retries` and `exec_fallback` features in your nodes. If the extraction fails, the fallback can return a safe message like, "I didn't quite catch your address, could you repeat that?" ensuring the app never crashes.

### **3\. Implementation Summary**

To build this, you would write a script using the 100-line PocketFlow framework:

1. **Define your `call_LLM` function:** A simple wrapper for your preferred API (e.g., OpenAI).  
2. **Create your Nodes:** Implement the `prep`, `exec`, and `post` methods for the Decider, Chatter, and Extractor.

**Define the Flow:**  
 \# Conceptual Wiring  
decider \>\> \["chat", "extract", "book"\] \# Branching  
chat\_node \>\> decider                   \# Loop back  
extract\_node \>\> decider                \# Loop back  
book\_node \>\> decider                   \# Loop back

3.  This creates the "infinite loop" required for a conversational agent, controlled by the logic in your *Decide Node*.

### **Analogy**

Think of your HVAC agent like a **front desk team** rather than a single receptionist.

* **The Shared Store** is the appointment book on the counter.  
* **The Decide Node** is the Manager who listens to the customer and points to the right specialist.  
* **The Chat Node** is the Greeter who answers general questions.  
* **The Extraction Node** is the Scribe who writes down the address and issue in the book.  
* **The Booking Node** is the Scheduler who actually blocks the time slot.

By separating these roles (Nodes) and coordinating them via the Manager (Flow), you create a reliable system that avoids confusion.

## Input: Repomix output of PocketFlow GitHub repo ([https://github.com/The-Pocket/PocketFlow](https://github.com/The-Pocket/PocketFlow))

## Prompt: How do I use pocketflow to design a conversational AI agent for HVAC booking process, what are the components that need to be used and how to train the agent effectively?

Based on the PocketFlow framework principles and design patterns, designing a conversational AI agent for an HVAC booking process involves orchestrating a graph of **Nodes** that communicate via a **Shared Store**.

Here is a guide on how to design, build, and "train" (optimize) this agent using PocketFlow components.

### **1\. Core Architecture & Components**

You should utilize the **Agent Design Pattern**, which relies on a central decision-making node to direct the flow based on conversation context.

**The Components:**

1. **Shared Store (Memory):** A dictionary to hold the state.

   * *Why:* It allows all nodes to read/write data like conversation history, user details, and booking status.

*Structure:*  
 shared \= {  
    "history": \[\],             \# Chat log  
    "user\_intent": None,       \# 'book', 'cancel', 'inquiry'  
    "booking\_slots": \[\],       \# Available times found  
    "booking\_details": {       \# Extracted entities  
        "service\_type": None,  
        "date": None,  
        "address": None  
    }  
}

*   
2. **Intent Classifier Node (The "Brain"):**

   * *Type:* Regular `Node`.  
   * *Function:* Analyzes the user's input to decide the next action (e.g., `extract_info`, `check_availability`, `finalize_booking`, or `ask_clarification`).  
   * *Logic:* Uses an LLM prompt to classify the user's latest message based on the `history` in the shared store.  
3. **Slot Extractor Node (Structured Output):**

   * *Type:* Regular `Node`.  
   * *Function:* Extracts specific HVAC details (e.g., "AC Repair", "Next Tuesday") from the text.  
   * *Technique:* Use **Structured Output** via YAML prompting. This is more reliable for LLMs than JSON to ensure you get machine-readable dates and service types.  
4. **Availability Checker Node (Async I/O):**

   * *Type:* `AsyncNode`.  
   * *Function:* Queries your backend/calendar API to check if the requested slot is open.  
   * *Why Async:* API calls are I/O bound; using `AsyncNode` prevents blocking the application while waiting for the database response.  
5. **Response Generator Node:**

   * *Type:* Regular `Node`.  
   * *Function:* Formats the final response to the user (e.g., "I have booked your AC repair for Tuesday at 2 PM.").

### **2\. Designing the Flow**

You connect these nodes using Actions to create a cyclic graph (a state machine).

graph TD  
    Start \--\> Intent\[Intent Classifier\]  
    Intent \--\>|"extract"| Extractor\[Slot Extractor\]  
    Intent \--\>|"check\_availability"| Check\[Availability Checker\]  
    Intent \--\>|"respond"| Responder\[Response Generator\]

    Extractor \--\> Intent  
    Check \--\> Intent  
    Responder \--\> Intent

**Implementation Strategy:**

* **Prep Step:** Read `history` from the shared store.  
* **Exec Step:** Call the LLM to process the input. For the *Extractor Node*, prompt the LLM to output YAML containing keys like `date` and `service_type`.  
* **Post Step:** Update `shared["booking_details"]` and return an action string (e.g., `"check_availability"` if all details are present, or `"respond"` if information is missing).

### **3\. How to "Train" the Agent Effectively**

In PocketFlow, "training" primarily refers to **Prompt Engineering** and **In-Context Learning**, as the framework orchestrates pre-trained LLMs (like GPT-4 or Claude).

* **Few-Shot Prompting:** In your `IntentClassifier` and `SlotExtractor` nodes, provide specific examples in the `exec()` prompt. For example, show the LLM how to handle ambiguous dates like "next weekend" within the prompt itself.

* **Structured Output Enforcement:** Use YAML format constraints in your prompts. This "trains" the agent to behave deterministically. If the LLM fails to output valid YAML, PocketFlow's built-in **Retry Mechanism** (`max_retries`) will automatically re-run the node, improving reliability without manual intervention.

* **Human-in-the-Loop (HITL):** For high-stakes actions like finalizing a booking charge, utilize the HITL pattern. Design a node that pauses execution and waits for a specific "approve" signal (e.g., via a web interface or specific user confirmation phrasing) before transitioning to the final booking API call.

### **4\. Code Skeleton**

Here is a simplified example based on the **Agent Pattern** documentation:

from pocketflow import Node, Flow

class DecideAction(Node):  
    def prep(self, shared):  
        return shared\["history"\]\[-1\]\["content"\] \# Last user message

    def exec(self, user\_msg):  
        \# Prompt LLM to decide next step  
        \# Return "extract\_info", "check\_db", or "reply"  
        return call\_llm\_classifier(user\_msg)

    def post(self, shared, prep\_res, exec\_res):  
        return exec\_res \# This action directs the Flow

class ExtractInfo(Node):  
    def exec(self, user\_msg):  
        \# Prompt LLM for YAML output of date/service  
        return call\_llm\_extractor(user\_msg)

    def post(self, shared, prep\_res, exec\_res):  
        shared\["booking\_details"\].update(exec\_res)  
        return "decide" \# Loop back to decider

\# Define Nodes  
decider \= DecideAction()  
extractor \= ExtractInfo()

\# Define Connections  
decider \- "extract\_info" \>\> extractor  
extractor \- "decide" \>\> decider

\# Start Flow  
flow \= Flow(start=decider)

## Prompt: What are the dos and donts while using pocketflow framework for effective design of AI conversational chat agents?

### Per YouTube transcript

Based on the PocketFlow framework's minimalist philosophy, designing effective conversational AI agents requires adhering to specific structural and strict operational principles.

Here are the **Dos and Don'ts** for effective design using PocketFlow.

### **The Dos**

**1\. Do Decompose Tasks into Specialized Nodes** Instead of using one massive prompt to handle everything, break your workflow into smaller, focused steps. For example, if you are building an article writer, use one node to outline, a separate node to draft sections, and a final node to combine them. This approach prevents the "rambling wall of text" often produced when asking an LLM to be an outliner, drafter, and proofer all at once.

**2\. Do Use YAML for Structured Data (Not JSON)** When you need your agent to extract data (like an email or address), explicitly ask the LLM to output in **YAML format**,.

* **Why:** LLMs often fail to properly escape quotes or newlines in JSON, making the output brittle and liable to crash your code.  
* **Benefit:** YAML is cleaner, human-readable, and much more forgiving regarding strings, ensuring your agent can reliably parse the output,.

**3\. Do Implement "Few-Shot Prompting"** In your `exec` method, provide a perfect example of the desired output format within the prompt itself. By explicitly showing the LLM the exact keys and structure you expect (e.g., `name`, `email`, `experience`), you significantly increase the reliability of the structured data returned.

**4\. Do Use Fallbacks and Retries** Design your nodes to be resilient. Configure `max_retries` and `wait` times so the system automatically retries if an API call fails. Furthermore, always implement an `exec_fallback` method to handle total failures gracefully—such as returning a default message—so your application never crashes mid-conversation,.

**5\. Do Isolate Your Logic** Strictly follow the **Prep-Exec-Post** lifecycle. Ensure your `exec` function works in a "clean, isolated bubble" where it only receives specific data from `prep` and returns a raw result. This separation makes your core computation logic clean, testable, and independent of the global state.

**6\. Do Write Your Own LLM Wrappers** Write your own simple utility function (e.g., `call_LLM`) to handle API calls rather than relying on framework-specific wrappers. This prevents "vendor lock-in" and ensures you aren't fighting the framework when APIs change or new models are released.

**7\. Do Use Async for Parallel Tasks** If your agent needs to perform multiple independent tasks (like searching several sources or processing batch files), use the **Async Parallel Batch Node**. By using `async` and `await`, you can turn a slow sequential process into a fast parallel one, reducing total wait time to that of the single longest task,.

### **The Don'ts**

**1\. Don't Let `Exec` Touch the Shared Store** Never allow the `exec` function to access or modify the Shared Store directly.

* **Risk:** This violates the isolation principle. Only the `prep` function should read from the store, and only the `post` function should write back to it,. This discipline ensures the store remains the "single source of truth" and makes debugging as simple as printing the dictionary.

**2\. Don't Use Complex Dependency Injection** Avoid frameworks or patterns that require "spiderweb diagrams" or massive dependencies to manage state. PocketFlow relies on a simple Python dictionary as the Shared Store; do not overcomplicate this by adding databases or message queues unless absolutely necessary.

**3\. Don't "Train" via massive Context Windows** Do not try to cram every instruction into a single chat context. Instead, use the **Flow** to manage state. An agent is simply a flow with a loop and a branch: a "Decide Node" determines the next step (action) based on history, rather than a single LLM trying to manage the whole process implicitly.

**4\. Don't Block the Main Thread** When building high-performance agents, avoid using standard sequential loops for API calls. This results in "pure wasted time" where the program sits idle waiting for a response. Always prefer the "smart chef" approach (asynchronous execution) to utilize waiting time for other tasks.

### **Analogy for Success**

To visualize the perfect PocketFlow agent, think of it as a **professional kitchen brigade**, not a single overwhelmed cook.

* **The Don't:** Do not be the cook who tries to chop vegetables, sauté the steak, and plate the dessert simultaneously (Single Node with a massive prompt). They will inevitably burn the steak or drop the plate.  
* **The Do:** Be the **Head Chef (The Flow)**. You assign the chopping to the **Prep Cook (Prep Node)**, the grilling to the **Line Cook (Exec Node)**, and the plating to the **Sous Chef (Post Node)**. If the Line Cook drops the steak, they immediately grab another one (`max_retries`) without stopping the rest of the kitchen.

### Per Repomix Output

Based on the PocketFlow documentation and design patterns, here are the effective **Dos and Don'ts** for designing AI conversational agents.

### **Core Architecture & Node Design**

**Do:**

* **Follow the Node Lifecycle:** Strictly adhere to the `prep` (read/preprocess), `exec` (compute/LLM call), and `post` (write/decide) structure to enforce separation of concerns.  
* **Keep `exec()` Pure:** Ensure the `exec()` method contains only compute logic (like LLM calls) and does **not** access the shared store directly.  
* **Fail Fast & Retry:** Utilize the built-in `max_retries` and `wait` parameters in Nodes to handle transient API failures, and implement `exec_fallback` to handle persistent failures gracefully,.  
* **Start Simple:** Begin with a simple solution and high-level design before implementation, iterating frequently based on feedback,.

**Don't:**

* **Make Tasks Too Coarse or Granular:** Avoid making a single node do too much (it becomes too complex for the LLM) or too little (context is lost and results become inconsistent).  
* **Handle Exceptions in Utilities:** Do not use `try...except` blocks within utility functions called by a Node's `exec()`; let the Node's built-in retry mechanism manage failures.

### **Data Management & Communication**

**Do:**

* **Use the Shared Store:** Use the Shared Store (typically an in-memory dictionary) for almost all communication between nodes to separate data schema from compute logic,.  
* **Design Data First:** Decide on your shared store data structure (or database schema) before implementing the flow logic,.  
* **Manage Context Carefully:** Provide relevant, minimal context to agents to avoid the "lost in the middle" phenomenon where LLMs overlook content in the middle of large prompts.

**Don't:**

* **Misuse `Params`:** Do not use `Params` for general data passing. They should remain immutable identifiers (e.g., filenames or IDs) primarily used for Batch operations,.  
* **Access Shared Store in `exec`:** Never read or write to the shared store within the `exec` method; strictly use `prep` for reading and `post` for writing.

### **Flow Orchestration**

**Do:**

* **Use Actions for Branching:** Use the return string from the `post()` method to determine the next node in the flow (e.g., `return "retry"` or `return "success"`),.  
* **Run Flows, Not Nodes:** In production, always use `flow.run(shared)` rather than `node.run(shared)` to ensure the full pipeline and transitions execute correctly.  
* **Use Batch Processing for Large Data:** Use `BatchNode` or `BatchFlow` when processing large inputs (like chunking texts) or iterating over lists of items,.

**Don't:**

* **Parallelize Dependent Tasks:** Do not use parallel execution if an item depends on the output of a previous item.  
* **Ignore Rate Limits:** Be cautious when using `AsyncParallelBatchNode` as parallel calls can quickly trigger LLM provider rate limits; consider throttling or batch APIs.

### **LLM Interaction & Prompting**

**Do:**

* **Use YAML for Structured Output:** Prefer YAML over JSON when prompting LLMs for structured data, as it handles strings and newlines more reliably without strict escaping requirements,.  
* **Define Clear Action Spaces:** When building Agents, provide well-structured, unambiguous sets of actions (e.g., `search`, `answer`).  
* **Implement Memory Strategies:** For chat agents, use techniques like sliding windows (keeping only recent messages) or RAG (retrieving relevant past conversations via embeddings) to manage context limits,.

**Don't:**

* **Rely on Hardcoded Utilities:** Avoid using built-in, vendor-specific API wrappers within the framework; implement your own lightweight utility functions (e.g., `call_llm`) to maintain flexibility and avoid vendor lock-in.

## Prompt: You are AI-powered conversational agent that assists customers in booking HVAC services

Create a set of realistic conversation scenarios (at least 100\) that cover various customer needs, questions, and potential issues related to booking an HVAC service. Aim for diversity in problem types (e.g., AC repair, furnace maintenance, installation), property types, location, and customer interactions.

The purpose of this is to serve as foundational input for AI conversational agent  implementation later

### Per YouTube transcript

This request is a perfect candidate for a **Synthetic Data Generation Workflow** using PocketFlow. Writing 100 full scripts manually is slow and rigid; instead, we can define the *archetypes* (core patterns) and use a **Batch Node** to generate the full 100+ variations programmatically.

Below is a curated list of **20 foundational "Gold Standard" scenarios** covering your required categories. Following that, I will outline the **PocketFlow Batch Workflow** you should use to expand these 20 seeds into 100+ unique training examples using the framework's parallel processing capabilities.

### **Part 1: The "Gold Set" Scenarios (Foundational Input)**

*These scenarios serve as your "Few-Shot" examples for the agent's `exec` step.*

#### **Category A: Emergency Repairs (High Urgency)**

**1\. The "AC Dead in Heatwave"**

* **Customer:** "It's 95 degrees and my AC just stopped making noise. I have a baby in the house."  
* **Complexity:** High urgency, vulnerable occupant.  
* **Goal:** Prioritize dispatch, express empathy, book "Emergency Diagnostic."

**2\. The "Leaking Furnace"**

* **Customer:** "There is water pooling around the bottom of my furnace in the basement."  
* **Complexity:** Potential property damage.  
* **Goal:** Identify if active leak, advise turning off water if possible, book repair.

**3\. The "Burning Smell"**

* **Customer:** "I turned on the heat and it smells like burning plastic."  
* **Complexity:** Safety hazard.  
* **Goal:** Advise shutting down system immediately. Do not book normal slot; escalate to urgent safety check.

**4\. The "Frozen Coil"**

* **Customer:** "There is actual ice on the pipe outside near the fan."  
* **Complexity:** User error vs. system failure.  
* **Goal:** Instruct customer to turn off AC (to thaw) before a tech can even arrive. Book for 24 hours later.

#### **Category B: Routine Maintenance & Sales**

**5\. The "Annual Tune-Up"**

* **Customer:** "I just want to schedule my spring cleaning for the AC."  
* **Complexity:** Low urgency, flexible scheduling.  
* **Goal:** Offer mid-week slots, upsell "Maintenance Club" membership.

**6\. The "Filter Confusion"**

* **Customer:** "My thermostat says 'change filter' but I don't know which size I need."  
* **Complexity:** Information retrieval (not a booking).  
* **Goal:** Guide user to check unit model number or offer a tech visit to measure and replace.

**7\. The "Smart Thermostat Quote"**

* **Customer:** "I bought a Nest thermostat. Can you guys install it? How much?"  
* **Complexity:** Pricing query.  
* **Goal:** Quote standard installation rate, check for C-wire compatibility.

**8\. The "Full System Replacement"**

* **Customer:** "My system is 20 years old. I think it's time for a new one."  
* **Complexity:** High revenue, requires "Sales Consultant" not "Service Tech."  
* **Goal:** Book a free estimate/consultation, not a repair window.

#### **Category C: Scheduling & Logistics**

**9\. The "Reschedule"**

* **Customer:** "I have a tech coming Tuesday, but I have to work. Can we do Friday?"  
* **Complexity:** Modifying existing state in Shared Store.  
* **Goal:** Verify identity, find new slot, update booking.

**10\. The "Specific Window"**

* **Customer:** "I can only be home between 12:00 PM and 2:00 PM on Thursdays."  
* **Complexity:** Constraint management.  
* **Goal:** Check availability against strict constraints.

**11\. The "Gate Code / Access"**

* **Customer:** "I booked for tomorrow, but I forgot to tell you the gate code is 1234."  
* **Complexity:** Updating notes field.  
* **Goal:** Append data to existing booking entity.

**12\. The "Tenant/Landlord"**

* **Customer:** "I am the tenant, but my landlord pays for repairs. Can you bill him?"  
* **Complexity:** Billing logic.  
* **Goal:** Secure landlord authorization/contact info before booking.

#### **Category D: Edge Cases & Issues**

**13\. The "Price Haggle"**

* **Customer:** "$89 for a diagnostic? Joe's HVAC does it for $50."  
* **Complexity:** Objection handling.  
* **Goal:** Explain value proposition (licensed, bonded, warranties), stand firm on price.

**14\. The "Vague Noise"**

* **Customer:** "It's making a weird 'thump' sound at night."  
* **Complexity:** Ambiguity.  
* **Goal:** Categorize as "Diagnostic," add detailed notes for the tech.

**15\. The "Wrong Service Area"**

* **Customer:** "I'm in \[City 50 miles away\]."  
* **Complexity:** Geofencing.  
* **Goal:** Politely decline service or refer to a partner.

**16\. The "Callback / Angry Customer"**

* **Customer:** "You guys were here yesterday and it's broken again\!"  
* **Complexity:** Sentiment analysis (Negative).  
* **Goal:** De-escalate, book "Warranty/Callback" (usually free), flag for manager.

#### **Category E: Technical Specifics**

**17\. The "Heat Pump vs. Furnace"**

* **Customer:** "I want to switch from gas to electric heat pump."  
* **Complexity:** Technical sales.  
* **Goal:** Book "Electrification Consultation."

**18\. The "Duct Cleaning"**

* **Customer:** "Do you guys clean air ducts?"  
* **Complexity:** Service menu verification.  
* **Goal:** Confirm if offered; if not, cross-sell filter services.

**19\. The "Commercial Property"**

* **Customer:** "I need service for my restaurant's walk-in cooler and rooftop unit."  
* **Complexity:** Commercial vs. Residential.  
* **Goal:** Route to Commercial Division (different rates/techs).

**20\. The "Warranty Check"**

* **Customer:** "Is my unit still under warranty?"  
* **Complexity:** Data lookup.  
* **Goal:** Ask for serial number or address to check internal records.

---

### **Part 2: How to Generate 100+ Scenarios using PocketFlow**

You cannot manually write 100 quality scenarios without fatigue. Instead, use the **Batch Node** concept to generate them. This ensures your data is clean and structured (YAML) for the agent to use later.

#### **The "Scenario Generator" Flow**

You will build a flow that takes a list of *variables* and generates the full dialogue.

**1\. Define the Variables (The "Prep" Step)** Create a list of variable combinations.

* *Problems:* \[AC not cooling, Furnace clicking, Thermostat blank, Strange smell, Water leak\]  
* *Customer Moods:* \[Frustrated, Confused, Urgent, Friendly, Skeptical\]  
* *Locations:* \[House, Condo, Rental Property, Mobile Home\]

**2\. The Async Batch Node (The "Exec" Step)** Use the `AsyncParallelBatchNode`, to process these combinations simultaneously. This will generate 100 scenarios in seconds rather than hours.

**The Prompt for the Node:** You must ask the LLM to output the data in **YAML** to avoid parsing errors,.

"Generate a realistic dialogue between a User and an HVAC Booking Assistant. **Context:** Customer has a {problem}, lives in a {location}, and is acting {mood}. **Output format:** YAML only. **Structure:**

\- summary: "Short description of scenario"  
  tags: \["{problem}", "{mood}"\]  
  dialogue:  
    \- role: user  
      text: "..."  
    \- role: assistant  
      text: "..."

**3\. The Result (The Shared Store)** The `post` step will collect all 100 dialogues into a list. You now have a dataset to:

1. Test your agent (run the "User" lines against your agent and check if the "Assistant" response matches the intent).  
2. Use as "Few-Shot" examples in your agent's prompts.

### **Summary of Implementation**

To get your 100 scenarios:

1. Take the **20 Gold Standards** above.  
2. Create a **Scenario Generation Flow** in PocketFlow.  
3. Feed the flow a list of mixed variables (e.g., "Problem: Leaking, Mood: Angry").  
4. Run the **Async Parallel Batch Node**.  
5. Save the output to a YAML file in your **Shared Store**.

This approach transforms the task from a manual writing exercise into an architectural design task, perfectly aligning with the PocketFlow philosophy of using flows to manage complexity.

### Per Repomix Ouput

Based on the PocketFlow framework and our previous discussion regarding the HVAC booking agent, creating a robust dataset is the first step in "training" (optimizing) your Intent Classifier and Slot Extractor nodes.

While the provided sources do not contain pre-written HVAC dialogues, they provide the **Batch Processing** and **Agentic Coding** patterns necessary to generate them efficiently.

Below is a curated set of **15 distinct "seed" scenarios** covering the requested diversity, followed by a **PocketFlow implementation script** to synthetically generate the full 100+ dataset using an LLM.

### **Part 1: Representative Conversation Scenarios (Seed Data)**

These scenarios are categorized to train the **Intent Classifier Node** defined in our previous turn.

#### **Category A: AC Repair (Urgent & Standard)**

1. **The "No Cool" Crisis**  
   * **User:** "It's 95 degrees and my AC is blowing warm air. I have a baby at home, can someone come today?"  
   * **Intent:** `book_repair` (Urgency: High)  
   * **Entities:** Service: AC Repair, Timing: Today/Emergency.  
2. **The Weird Noise**  
   * **User:** "My outside unit is making a loud grinding noise when it starts up. It's cooling okay, but I'm worried."  
   * **Intent:** `book_repair`  
   * **Entities:** Service: Inspection/Repair, Symptom: Noise.  
3. \*\*The Leaky Unit (Cond) \*\*  
   * **User:** "Hi, I noticed water pooling around my furnace in the basement. I think the AC coil is leaking."  
   * **Intent:** `book_repair`  
   * **Entities:** Location: Basement, Symptom: Leak.

#### **Category B: Furnace & Heating**

4. **The Pilot Light Issue**  
   * **User:** "My furnace keeps clicking but won't ignite. I think the pilot light is out."  
   * **Intent:** `book_repair`  
   * **Entities:** System: Furnace, Symptom: Ignition failure.  
5. **General Maintenance (Routine)**  
   * **User:** "I'd like to schedule my annual fall tune-up for the heating system before it gets cold."  
   * **Intent:** `book_maintenance`  
   * **Entities:** Service: Maintenance/Tune-up.

#### **Category C: Installation & Quotes**

6. **New Home Install**  
   * **User:** "We are building a new extension and need a quote for a ductless mini-split system."  
   * **Intent:** `request_quote`  
   * **Entities:** Type: Ductless Mini-split, Action: Install.  
7. **System Replacement**  
   * **User:** "My AC is 15 years old and finally died. I need an estimate for a whole new central air system."  
   * **Intent:** `request_quote`  
   * **Entities:** Type: Central Air, Context: Replacement.

#### **Category D: Scheduling Edge Cases**

8. **Rescheduling**  
   * **User:** "I have an appointment for Tuesday at 2 PM for Smith at 123 Main St. I need to push it to Thursday."  
   * **Intent:** `reschedule`  
   * **Entities:** Original Time: Tuesday 2 PM, New Time: Thursday.  
9. **Cancellation**  
   * **User:** "Something came up, please cancel my appointment for tomorrow morning."  
   * **Intent:** `cancel_booking`  
   * **Entities:** Time: Tomorrow morning.

#### **Category E: Ambiguous/Clarification Needed**

10. **Vague Request**  
    * **User:** "My air isn't working right."  
    * **Intent:** `inquiry` (Needs clarification)  
    * **Action:** Agent must ask: "Is this for your heating or cooling system?"  
11. **Pricing Inquiry**  
    * **User:** "How much do you charge for a freon refill?"  
    * **Intent:** `inquiry_pricing`  
    * **Action:** Agent provides rate or explains it depends on the unit size.

### **Part 2: Generating the Full 100+ Dataset with PocketFlow**

Instead of writing 100 scenarios by hand, we can use the **Batch Processing** pattern found in the sources to generate synthetic data. This aligns with the "Agentic Coding" philosophy where agents help build agents.

We will use a `BatchNode` to take the seed scenarios above and generate variations (different phrasings, tones, and locations).

import os  
from pocketflow import BatchNode, Flow  
\# Assuming you have a utility to call your LLM  
from utils import call\_llm

class ScenarioGenerator(BatchNode):  
    def prep(self, shared):  
        \# We define base scenarios (the seeds from Part 1\)  
        \# In a real app, these could be loaded from a file  
        seeds \= \[  
            {"type": "AC Repair", "context": "Blowing warm air", "tone": "Frustrated"},  
            {"type": "Furnace", "context": "Won't turn on", "tone": "Worried"},  
            {"type": "Maintenance", "context": "Annual checkup", "tone": "Casual"},  
            {"type": "Installation", "context": "New Mini-split", "tone": "Professional"},  
            {"type": "Reschedule", "context": "Conflict with work", "tone": "Apologetic"}  
        \]

        \# We want 20 variations for EACH seed to get 100 total  
        tasks \= \[\]  
        for seed in seeds:  
            for i in range(20):  
                tasks.append(seed)  
        return tasks

    def exec(self, seed\_data):  
        \# We prompt the LLM to generate a unique dialogue based on the seed  
        prompt \= f"""  
        Generate a realistic, single-turn user message for an HVAC booking chatbot.

        Scenario Type: {seed\_data\['type'\]}  
        Context: {seed\_data\['context'\]}  
        Customer Tone: {seed\_data\['tone'\]}

        Ensure the location and specific details vary.  
        Output ONLY the user message text.  
        """  
        return call\_llm(prompt)

    def post(self, shared, prep\_res, exec\_res\_list):  
        \# Store the generated 100 scenarios  
        shared\["generated\_scenarios"\] \= exec\_res\_list  
        print(f"Successfully generated {len(exec\_res\_list)} scenarios.")  
        return "save\_data"

\# Define the flow  
generator \= ScenarioGenerator()  
flow \= Flow(start=generator)

\# Run the generation  
shared\_store \= {}  
flow.run(shared\_store)

\# The result is now in shared\_store\["generated\_scenarios"\]  
\# You can save this to a CSV or JSON file to use for testing/training.

### **Part 3: Structuring the Data for the Agent**

To use this data effectively in the **Shared Store** of your actual agent (as discussed in the previous turn), you should structure the output. PocketFlow encourages separating data schema from logic.

Format your 100+ scenarios into a JSON structure like this to simulate `history` in the shared store:

\[  
  {  
    "id": "scenario\_001",  
    "user\_input": "My AC is leaking water all over the attic floor\!",  
    "expected\_intent": "book\_repair",  
    "expected\_slots": {  
      "service": "AC Repair",  
      "symptom": "Water Leak",  
      "location": "Attic"  
    }  
  },  
  {  
    "id": "scenario\_002",  
    "user\_input": "I need to move my maintenance appointment from Monday to Friday.",  
    "expected\_intent": "reschedule",  
    "expected\_slots": {  
      "original\_day": "Monday",  
      "new\_day": "Friday"  
    }  
  }  
\]

### **Summary of Next Steps**

1. **Run the Generator:** Use the `ScenarioGenerator` code above (using the `BatchNode` pattern) to create your volume of data.  
2. **Validate:** Manually review a sample of the generated scenarios to ensure diversity.  
3. **Implement:** Feed these inputs into your `IntentClassifier` node (from the previous conversation) to test if it correctly identifies the `expected_intent`. Use the `Structured Output` pattern (YAML) to ensure the agent extracts the correct entities.

## Prompt: Without worrying about implementation details for now, how exactly would you test this expert AI chat agent for HVAC booking services per our conversation and context mentioned so far?

### Per YouTube transcript

Based on the PocketFlow philosophy and our conversation history, testing your HVAC agent does not require complex external testing frameworks or "spiderweb diagrams". Because the system is built on isolated components (`Nodes`) and a visible state (`Shared Store`), you can test it by building a **"Test Flow"** that uses the framework itself.

Here is exactly how you would test the agent using the 100 scenarios we generated previously.

### **1\. Unit Test the "Brain" (The Decide Node)**

The most critical part of your agent is the **Decide Node**, which routes traffic (e.g., determining if a user is asking a general question or trying to book). Since the `exec` function works in a "clean, isolated bubble", you can test this node in isolation without running the full conversational loop.

* **The Test:** Create a simple script that feeds specific inputs to the Decide Node and asserts the output `action` string.  
* **Example Inputs:**  
  * Input: "My AC is broken." $\\rightarrow$ Expected Action: `extract_info` or `book`  
  * Input: "How much is a tune-up?" $\\rightarrow$ Expected Action: `chat`  
  * Input: "Stop messaging me." $\\rightarrow$ Expected Action: `end_conversation`  
* **Why this works:** You are validating the routing logic (`self.successors`) ensures the "factory foreman" sends the worker to the right station every time,.

### **2\. High-Volume Simulation (The "Batch" Test)**

This is where you utilize the 100+ scenarios generated in our previous step. Instead of manually chatting 100 times, you use the **Async Parallel Batch Node** to run all simulations simultaneously,.

* **The Setup:** You create a "Simulator Node." Its `prep` step loads your 100 synthetic scenarios (the YAML file created earlier).  
* **The Execution:** The `exec` step runs your HVAC Agent's logic against the "User" lines from those scenarios.  
* **The Speed:** Because you use the `AsyncParallelBatchNode`, you can test all 100 scenarios in the time it takes to run just the longest one. You will know in seconds, not hours, if your agent handles the "Leaking Furnace" and "Price Haggle" scenarios correctly.  
* **The Verification:** You compare the Agent's actual response against the "Gold Standard" assistant response generated in the synthetic data set.

### **3\. Verify Structured Data Extraction**

For the HVAC context, getting the address and issue correct is vital. You must verify that the **Extraction Node** properly parses messy text into clean YAML.

* **The Test:** Feed the node "messy" inputs from your scenarios (e.g., "I'm at 123 Main, no wait, 124 Main St, and the heater is dying").  
* **The Check:** Verify that the `exec` function returns a valid Python dictionary (via YAML parsing) with the correct keys (`address: "124 Main St"`, `issue: "heater failure"`).  
* **Resilience Check:** If the LLM generates invalid YAML, verify that the node's `max_retries` triggers a retry, and if it fails, that `exec_fallback` returns a safe error message rather than crashing the app,.

### **4\. Inspect the "Memory" (State Inspection)**

Because the **Shared Store** is "just a Python dictionary", debugging is transparent. You don't need database queries to see what went wrong.

* **The Strategy:** During your batch tests, if a specific scenario fails, print the Shared Store dictionary for that specific run.  
* **What to look for:**  
  * Did the `messages` list update correctly with the user/assistant history?  
  * Did the `booking_details` key get populated?  
  * Did the state transition from "browsing" to "booked"?  
* This allows you to see the exact state of the "whiteboard" at the moment of failure.

### **5\. Stress Test the "Tools"**

Finally, you must test the **Booking Action Node**. In a test environment, you likely don't want to actually write to your real calendar.

* **Mocking:** Since `exec` is just a python function, you can swap the real API call for a mock function during testing.  
* **Failure Simulation:** Deliberately force the mock to "fail" (simulate the Calendar API being down).  
* **Goal:** Verify that the node's `exec_fallback` catches the error and the agent politely tells the user, "I'm having trouble accessing the calendar right now," instead of the conversation simply dying.

### **Summary Analogy**

Testing your agent this way is like being a **Restaurant Inspector**:

1. **Unit Test:** You taste the sauce alone (Decide Node) to ensure it's not spoiled.  
2. **Batch Test:** You hire 100 mystery diners (The Scenarios) to eat at once (Async Batch) and report back.  
3. **State Inspection:** You walk into the kitchen and look at the order tickets on the counter (Shared Store) to ensure nothing was lost.  
4. **Resilience:** You unplug the stove (API Failure) to ensure the chefs have a backup plan (Fallback) and don't just walk out.

### Per Repomix Output

Based on the PocketFlow framework principles and the components we discussed (Intent Classifier, Slot Extractor, Shared Store), here is exactly how you would test the HVAC booking agent.

Testing in PocketFlow is best approached by isolating the **Nodes** (unit testing), verifying the **Flow logic** (integration testing), and using **Batch Processing** for quantitative evaluation.

### **1\. Unit Testing: Node Isolation**

PocketFlow nodes are designed to be tested in isolation because they follow a strict `prep -> exec -> post` lifecycle. You do not need to run the full chat application to test if the "Brain" works.

* **Intent Classifier Test:** You would feed the `IntentClassifier` node raw string inputs (e.g., "My furnace is making a banging noise") and assert that the return action is exactly `"book_repair"`.  
* **Slot Extractor Test:** You would input complex phrases like "I need someone next Tuesday at 2 PM" and assert that the node extracts `{"date": "next Tuesday", "time": "2:00 PM"}` into the shared store.

**PocketFlow Approach:** You can instantiate a Node class directly and call `.run(shared)` with a mock shared dictionary to verify state updates without triggering the rest of the flow.

### **2\. Batch Evaluation (Accuracy Testing)**

Using the 100+ scenarios we generated in the previous conversation, you should perform **Batch Evaluation** to measure the agent's accuracy before going live.

* **The Setup:** Use a `BatchNode` or `BatchFlow`.  
* **The Process:**  
  1. Load the 100 generated scenarios (User Input \+ Expected Intent/Slots).  
  2. Feed the "User Input" into your `IntentClassifier` node using a `BatchFlow`.  
  3. Compare the node's output against the "Expected Intent".  
* **The Goal:** Calculate an accuracy percentage (e.g., "The model correctly identified 'Emergency Repair' 95% of the time"). This allows you to optimize your prompt instructions based on hard data rather than guessing,.

### **3\. Integration Testing: Flow Topology**

You need to verify that the **Actions** returned by nodes correctly trigger the next step in the graph.

* **Branching Logic:** Test that if the `IntentClassifier` returns `"incomplete_info"`, the flow actually transitions to the `ResponseGenerator` (to ask a question) rather than the `AvailabilityChecker`.  
* **Cycle Detection:** Ensure the agent doesn't get stuck in a loop (e.g., asking for the same date repeatedly). You can test this by pre-populating the `Shared Store` with specific history states and running the flow to see if it exits the loop correctly,.

### **4\. Multi-Agent Simulation (Stress Testing)**

To test how the agent handles long, back-and-forth conversations without doing it manually, you can use the **Multi-Agent Pattern**.

* **Concept:** Create a "User Simulator Agent" (a simple Node with a persona prompt like "You are a frustrated customer with a broken AC").  
* **Execution:** Connect the "User Simulator" flow to your "HVAC Booking" flow using an async message queue. Let them talk to each other for 10 turns.  
* **Why:** This reveals edge cases where the agent might lose context or fail to update the shared store correctly over a long session,.

### **5\. Tracing and Debugging**

For every test run, you should enable **Tracing** (using the integration with tools like Langfuse).

* **Why:** Because PocketFlow nodes operate in isolation, it can be hard to see *why* a specific extraction failed inside a batch of 100\.  
* **How:** Use the `@trace_flow` decorator. This captures the input, output, and latency of every node execution, allowing you to pinpoint exactly which user phrasing caused the `SlotExtractor` to fail,.

### **Summary of Test Suite**

| Test Component | PocketFlow Feature Used | Goal |
| ----- | ----- | ----- |
| **Logic Check** | `node.run(shared)` | Verify `prep/exec/post` logic handles data correctly. |
| **Accuracy** | `BatchNode` | Validate 100+ scenarios against expected outputs. |
| **Navigation** | `Flow` transitions | Ensure "Action" strings (`"retry"`, `"success"`) route correctly. |
| **Robustness** | Multi-Agent Queues | Simulate long conversations to check memory retention. |

