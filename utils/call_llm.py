import os
import requests
import json

def call_llm(prompt: str, system_prompt: str = "") -> str:
    """Calls OpenRouter with the given prompt and system_prompt."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY is not set")

    # default to a fast and capable model
    model = os.getenv("LLM_MODEL", "google/gemini-flash-1.5")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://pockflow-hvac-agent.local", # Optional
        "X-Title": "PocketFlow HVAC Agent" # Optional
    }

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    
    # Handle both string prompt and list of messages (for chat)
    if isinstance(prompt, str):
        messages.append({"role": "user", "content": prompt})
    elif isinstance(prompt, list):
        messages.extend(prompt)

    data = {
        "model": model,
        "messages": messages
    }

    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        data=json.dumps(data)
    )

    if response.status_code != 200:
        raise Exception(f"OpenRouter API error: {response.status_code} - {response.text}")

    result = response.json()
    return result['choices'][0]['message']['content']

if __name__ == "__main__":
    # Test call
    try:
        print("Testing OpenRouter call...")
        response = call_llm("Hello, respond with 'HVAC Agent Ready' if you can hear me.")
        print(f"Response: {response}")
    except Exception as e:
        print(f"Test failed: {e}")
