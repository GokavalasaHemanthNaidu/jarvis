import httpx
import json

class Content:
    def __init__(self, text):
        self.text = text

class Response:
    def __init__(self, text):
        self.content = [Content(text)]

class Messages:
    def __init__(self, api_key=None, base_url="http://localhost:11434"):
        self.base_url = base_url
        self.api_key = api_key

    async def create(self, model=None, max_tokens=None, system=None, messages=None, **kwargs):
        ollama_messages = []
        if system:
            ollama_messages.append({"role": "system", "content": system})
        if messages:
            ollama_messages.extend(messages)
            
        # The user has an 8GB RAM laptop with low free memory. 
        # Using a 1B parameter model (llama3.2:1b) which only requires ~1.3GB of RAM.
        ollama_model = "llama3.2:1b"

        try:
            async with httpx.AsyncClient(timeout=120) as client:
                resp = await client.post(
                    f"{self.base_url}/api/chat",
                    json={
                        "model": ollama_model,
                        "messages": ollama_messages,
                        "stream": False
                    }
                )
                if resp.status_code == 200:
                    data = resp.json()
                    text = data.get("message", {}).get("content", "")
                    return Response(text)
                else:
                    return Response(f"Ollama Error {resp.status_code}: {resp.text}")
        except Exception as e:
            return Response(f"Ollama connection error: {str(e)}. Make sure Ollama is running.")

class AsyncAnthropic:
    def __init__(self, api_key=None):
        self.messages = Messages(api_key=api_key)
