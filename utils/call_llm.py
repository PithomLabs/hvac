import os
import json
import urllib.request
import urllib.error
import time

def call_llm(prompt: str, system_prompt: str = "", max_retries: int = 3) -> str:
    """Calls OpenRouter using only standard libraries with retries."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY is not set")

    model = os.getenv("LLM_MODEL", "openai/gpt-4o-mini")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://pockflow-hvac-agent.local",
        "X-Title": "PocketFlow HVAC Agent"
    }

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    
    if isinstance(prompt, str):
        messages.append({"role": "user", "content": prompt})
    elif isinstance(prompt, list):
        messages.extend(prompt)

    data = json.dumps({
        "model": model,
        "messages": messages
    }).encode("utf-8")

    for attempt in range(max_retries):
        req = urllib.request.Request(
            "https://openrouter.ai/api/v1/chat/completions",
            data=data,
            headers=headers,
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode("utf-8"))
                return result['choices'][0]['message']['content']
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")
            if e.code == 429 and attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            raise Exception(f"OpenRouter API error: {e.code} - {error_body}")
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            raise Exception(f"Network error: {e}")

if __name__ == "__main__":
    print("Testing dependency-free OpenRouter call...")
    try:
        print(call_llm("Hello, respond with 'HVAC Agent Standard Ready'."))
    except Exception as e:
        print(f"Test failed: {e}")
