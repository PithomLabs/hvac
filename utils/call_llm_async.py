import os
import json
import asyncio
import urllib.request
import urllib.error

async def call_llm_async(prompt: str, system_prompt: str = "", max_retries: int = 5) -> str:
    """Asynchronously calls OpenRouter using urllib and asyncio.to_thread with retries."""
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

    payload = json.dumps({
        "model": model,
        "messages": messages
    }).encode("utf-8")

    def _sync_call(attempt):
        req = urllib.request.Request(
            "https://openrouter.ai/api/v1/chat/completions",
            data=payload,
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
                return None # Signal retry
            raise Exception(f"OpenRouter API error: {e.code} - {error_body}")
        except Exception as e:
            if attempt < max_retries - 1:
                return None # Signal retry
            raise Exception(f"Network error: {e}")

    for i in range(max_retries):
        res = await asyncio.to_thread(_sync_call, i)
        if res is not None:
            return res
        await asyncio.sleep(2 ** i + 1) # Wait and retry
    
    raise Exception("Max retries exceeded for OpenRouter API")

if __name__ == "__main__":
    async def test():
        print("Testing dependency-free OpenRouter async call...")
        try:
            print(await call_llm_async("Hello, respond with 'HVAC Agent Async Ready'."))
        except Exception as e:
            print(f"Test failed: {e}")
    asyncio.run(test())
