import requests, json
from config import OLLAMA_URL, MODEL

def ask_llm(prompt: str):
    payload = {
        "prompt": prompt,
        "model": MODEL,
        "stream": True
    }
    print(payload)
    response = requests.post(OLLAMA_URL, json=payload, stream=True)
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
    
    return full

def ask_llm_json(prompt: str):
    response = ask_llm(prompt)
    if "```json" in response:
        obj, _ = json.JSONDecoder().raw_decode(response[8:])
        return obj

    return json.loads(response)