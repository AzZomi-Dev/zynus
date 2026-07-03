import requests
from requests.adapters import HTTPAdapter
from config import OLLAMA_URL, MODEL
from observability.metrics import llm_latency, llm_requests
import json
import time

session = requests.Session()
adapter = HTTPAdapter(pool_connections=20, pool_maxsize=100)

session.mount("http://", adapter)
session.mount("https://", adapter)

def ask_llm(prompt: str):
    start = time.time()
    payload = {
        "prompt": prompt,
        "model": MODEL,
        "stream": True
    }
    print(payload)
    llm_requests.inc()
    for attempt in range(4):
        try:
            with session.post(
                OLLAMA_URL,
                json=payload,
                stream=True,
                timeout=60
            ) as response:
                response.raise_for_status()
                full = ""
                for line in response.iter_lines():
                    if not line:
                        continue
                    
                    data = json.loads(line.decode("utf-8"))
                    token = data.get("response", "")

                    print(token, end="", flush=True)
                    full += token
                    
                    if data.get("done"):
                        break
                
                llm_latency.observe(time.time() - start)
                return full
        except requests.RequestException:
            if attempt == 3:
                raise
            print(f"ERROR, Retrying .. Attempt: {attempt}")
            time.sleep(2 ** attempt)

def ask_llm_json(prompt: str):
    response = ask_llm(prompt)
    if "```json" in response:
        obj, _ = json.JSONDecoder().raw_decode(response[8:])
        return obj

    return json.loads(response)