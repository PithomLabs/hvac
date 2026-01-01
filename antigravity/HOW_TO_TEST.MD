# Testing Guide: HVAC Booking AI Assistant

This guide explains how to test the HVAC Booking AI Assistant, both manually through the interactive CLI and automatically using the Gold Standard QA suite.

## 1. Environment Setup

The agent requires an **OpenRouter API Key** to function. Set it as an environment variable in your terminal:

```bash
# Required: Set your OpenRouter API Key
export OPENROUTER_API_KEY="your_api_key_here"

# Optional: Override the default model (defaults to openai/gpt-4o-mini)
export LLM_MODEL="openai/gpt-4o-mini"
```

---

## 2. Manual Interactive Testing

To experience the agent as a customer would, run the interactive CLI:

```bash
python3 main.py
```

### What to try:
- **Emergency Case**: "I have a baby at home and my AC just died in this heatwave!"
- **Safety Concern**: "I smell something like burning plastic coming from my furnace."
- **Technical Inquiry**: "Do I have a furnace or a heat pump? I see a big fan unit outside."
- **Logistics**: "I need to reschedule Jerry Seinfeld's appointment at 129 West 81st St."
- **Edge Case**: "$150 for a visit? Joe's HVAC does it for $75!"

---

## 3. Automated Gold Standard Verification

We have implemented **20 Gold Standard scenarios** that cover the most critical functional areas. You can run these using the `run_qa.py` script.

### Run all 20 Scenarios:
```bash
ls data/qa/gold_*.md | xargs -n 1 basename | xargs -n 1 python3 data/qa/run_qa.py
```

### Run a specific Scenario:
```bash
# Example: Testing the "Burning Smell" safety scenario
python3 data/qa/run_qa.py gold_a3_smell.md
```

### Scenario Categories:
- **A1-A4**: Emergencies (Heatwaves, Leaks, Smells, Frozen Coils)
- **B5-B8**: Routine/Sales (Tune-ups, Filters, Pricing, Replacements)
- **C9-C12**: Logistics (Rescheduling, Time Windows, Gate Codes, Billing)
- **D13-D16**: Edge Cases (Haggling, Vague Noises, Geofencing, Sentiment)
- **E17-E20**: Technical (Equipment Identification, Accessibility, Robustness)

---

## 4. Inspecting the Results

### Database Verification
All successful bookings and customer profiles are stored in the SQLite database. You can query it directly:

```bash
# View all bookings
sqlite3 agent/hvac_booking.db "SELECT * FROM bookings;"

# View all customers
sqlite3 agent/hvac_booking.db "SELECT * FROM customers;"
```

### QA Logs
The `run_qa.py` script provides real-time logs of the agent's internal `Decider`, `Extractor`, and `Booker` actions. If a scenario fails, the log will show exactly where the logic diverged from the expected behavior.


### Actual CLI Testing

chaschel@xia:~/Documents/ibm/ai/PocketFlow-Template-Python-main/agent$ python3 main.py
Database initialized at /home/chaschel/Documents/ibm/ai/PocketFlow-Template-Python-main/agent/../agent/hvac_booking.db
--- HVAC Booking Agent ---
Welcome! How can I help you today?

You: I just turned on the heat for the first time this season and it smells like burning plastic. What should I do?

You: ^Cchaschel@xia:~/Documents/ibm/ai/PocketFlow-Template-Python-main/agent$ python3 main.py
Database initialized at /home/chaschel/Documents/ibm/ai/PocketFlow-Template-Python-main/agent/../agent/hvac_booking.db
--- HVAC Booking Agent ---
Welcome! How can I help you today?

You: I just turned on the heat for the first time this season and it smells like burning plastic. What should I do?
  [DECIDER]: Analyzing state...
  [DECIDER]: Decision -> chat (User is asking a question about a burning plastic smell from their heater. This is an initial inquiry seeking advice/information. No booking details (name, address, service type) have been provided yet. Need to respond helpfully and guide toward booking if they need service.)
  [AGENT]: Thinking...

You: ^Cchaschel@xia:~/Documents/ibm/ai/PocketFlow-Template-Python-main/agent$ python3 main.py
Database initialized at /home/chaschel/Documents/ibm/ai/PocketFlow-Template-Python-main/agent/../agent/hvac_booking.db
--- HVAC Booking Agent ---
Welcome! How can I help you today?

You: I just turned on the heat for the first time this season and it smells like burning plastic. What should I do?
  [DECIDER]: Analyzing state...
  [DECIDER]: Selected Action -> chat
  [CHAT]: Thinking...
  [CHAT]: LLM Response received (1625 chars)
  [CHAT]: Post-turn completed.

You: ^Cchaschel@xia:~/Documents/ibm/ai/PocketFlow-Template-Python-main/agent$ python3 main.py
Database initialized at /home/chaschel/Documents/ibm/ai/PocketFlow-Template-Python-main/agent/hvac_booking.db

--- HVAC Booking AI Assistant ---
Powered by PocketFlow and OpenRouter.

I am an AI-powered HVAC service assistant designed to help you book repairs, maintenance, 
and consultations with extreme professionalism and empathy. I can handle:
- Emergency Repairs (leaks, smells, extreme weather outages)
- Maintenance Tune-ups
- New System Estimates
- Booking Modifications (rescheduling, gate codes)

Initial Prompt: What is the issue you're facing, and how urgent is it?


You: Help! My AC is barely blowing any air and I see actual ice on the copper pipe outside near the unit. 
  [DECIDER]: Analyzing state...
  [DECIDER]: Selected Action -> chat
  [CHAT]: Thinking...
  [CHAT]: LLM Response received (1470 chars)
  [CHAT]: Post-turn completed.

Agent: I understand how concerning that must be! Ice forming on your AC is actually a common issue, but it does need immediate attention. Here's what's happening and what you need to do:

**What's going on:**
Ice on the copper pipes (specifically the larger suction line) means your evaporator coil is freezing up. When airflow is restricted or refrigerant levels are off, the coil gets too cold and freezes.

**Immediate steps - RIGHT NOW:**

1. **Turn OFF your AC at the thermostat** - Running it frozen can damage the compressor (expensive!)
2. **Turn your fan to "ON" mode** (not auto) to help melt the ice
3. **Don't try to chip or scrape the ice off** - let it melt naturally (2-4 hours typically)

**Common causes:**
- Dirty/clogged air filter (check this first!)
- Blocked return vents
- Low refrigerant from a leak
- Dirty evaporator coil
- Failing blower motor

**What you can check safely:**
- Replace your air filter if it's dirty/clogged
- Make sure all your vents and returns are open and unblocked
- Check that your outdoor unit isn't covered in debris

**You'll need professional service because:**
This issue often requires checking refrigerant levels, cleaning coils, or diagnosing airflow problems - all things that need a technician's tools and expertise.

Would you like help booking a service call? A technician can diagnose the exact cause and prevent this from happening again. This really shouldn't wait, as continued freezing can cause serious damage!

You: Yes
  [DECIDER]: Analyzing state...
  [DECIDER]: Selected Action -> extract
  [EXTRACTOR]: Processing message...
  [EXTRACTOR]: Finished. info_added=False
  [DECIDER]: Analyzing state...
  [DECIDER]: Selected Action -> extract
  [EXTRACTOR]: Processing message...
  [EXTRACTOR]: Finished. info_added=False
  [DECIDER]: Analyzing state...
  [DECIDER]: Extraction stalled, forcing chat.
  [DECIDER]: Selected Action -> chat
  [CHAT]: Thinking...
  [CHAT]: LLM Response received (912 chars)
  [CHAT]: Post-turn completed.

Agent: Great! I'm glad you're getting this taken care of quickly. Let me help you get a technician scheduled.

**To book your service appointment, I'll need a few details:**

1. **Your location** (city/zip code)
2. **Your preferred timeframe** - Given the ice buildup, I'd recommend:
   - Emergency/same-day service (if available)
   - Next available appointment
   - Or a specific day that works for you

3. **Your contact information:**
   - Name
   - Phone number
   - Email address

4. **Property details:**
   - Is this a home or business?
   - Do you know the age/brand of your AC unit? (helpful but not required)

**Remember while you wait:**
- Keep the AC OFF
- Keep the fan running to melt the ice
- Don't use the system until the technician arrives

Once you provide those details, I can get you scheduled with a qualified HVAC technician who can diagnose and fix the issue properly.

What works best for you?

You: aizen hill 408-159-2587 san jose ca
  [DECIDER]: Analyzing state...
  [DECIDER]: Selected Action -> extract
  [EXTRACTOR]: Processing message...
  [EXTRACTOR]: Finished. info_added=True
  [DECIDER]: Analyzing state...
  [DECIDER]: Selected Action -> extract
  [EXTRACTOR]: Processing message...
  [EXTRACTOR]: Finished. info_added=False
  [DECIDER]: Analyzing state...
  [DECIDER]: Selected Action -> extract
  [EXTRACTOR]: Processing message...
  [EXTRACTOR]: Finished. info_added=False
  [DECIDER]: Analyzing state...
  [DECIDER]: Extraction stalled, forcing chat.
  [DECIDER]: Selected Action -> chat
  [CHAT]: Thinking...
  [CHAT]: LLM Response received (740 chars)
  [CHAT]: Post-turn completed.

Agent: Perfect! Thank you, Aizen.

Let me confirm your information:
- **Name:** Aizen Hill
- **Phone:** 408-159-2587
- **Location:** San Jose, CA

Just a couple more quick questions:

1. **What timeframe works best for you?**
   - Today (emergency service)
   - Tomorrow
   - Next available appointment
   - Specific day/time preference?

2. **Email address?** (for appointment confirmation)

3. **Is this for a home or business?**

4. **Any additional access information** the technician should know? (gate code, preferred entrance, etc.)

Since your AC is frozen and not cooling, I'd strongly recommend getting someone out today or tomorrow if possible. The sooner we address this, the less risk of compressor damage.

What timing works for you?

You: tomorrow 9am
  [DECIDER]: Analyzing state...
  [DECIDER]: Selected Action -> extract
  [EXTRACTOR]: Processing message...
  [EXTRACTOR]: Finished. info_added=False
  [DECIDER]: Analyzing state...
  [DECIDER]: Selected Action -> extract
  [EXTRACTOR]: Processing message...
  [EXTRACTOR]: Finished. info_added=False
  [DECIDER]: Analyzing state...
  [DECIDER]: Extraction stalled, forcing chat.
  [DECIDER]: Selected Action -> chat
  [CHAT]: Thinking...
  [CHAT]: LLM Response received (857 chars)
  [CHAT]: Post-turn completed.

Agent: Excellent! Tomorrow at 9am works well.

**Let me confirm your appointment details:**
- **Date/Time:** Tomorrow at 9:00 AM
- **Name:** Aizen Hill
- **Phone:** 408-159-2587
- **Location:** San Jose, CA
- **Issue:** AC frozen/icing on copper lines, minimal airflow

**I still need:**
- **Email address** (for confirmation)
- **Home or business?**
- **Street address** (for the technician)

**What to expect:**
- The technician will call 15-30 minutes before arrival
- Plan for 1-2 hours for diagnosis and potential repair
- They'll have the tools to check refrigerant, airflow, and identify the root cause

**Reminder before tomorrow:**
- Keep AC OFF
- Fan can stay on "ON" mode to melt ice
- Make sure the area around both indoor and outdoor units is accessible

Once you provide those last few details, I'll get this appointment confirmed for you right away!

You: 
