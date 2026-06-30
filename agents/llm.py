import requests, json
from config import OLLAMA_URL, MODEL

def ask_llm(prompt: str):
    payload = {
        "prompt": prompt,
        "model": MODEL,
        "stream": False
    }
    print(payload)
    response = requests.post(OLLAMA_URL, json=payload)
    cleaned_response = response.json()["response"]

    print(cleaned_response)

    return cleaned_response

def ask_llm_json(prompt: str):
    response = ask_llm(prompt)
    if "```json" in response:
        obj, _ = json.JSONDecoder().raw_decode(response[8:])
        return obj

    return json.loads(response)