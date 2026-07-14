from config import MODEL, GROQ_API_KEY
from observability.metrics import llm_latency, llm_requests
from groq import Groq
import time

groq_client = Groq(api_key=GROQ_API_KEY)

def ask_groq(prompt: str) -> str:
    """
    Send a prompt to Groq and stream the generated response.

    Features:
    - Streaming token generation
    - Automatic retries with exponential backoff
    - Prometheus request counting
    - Prometheus latency measurement
    """
    start = time.time()
    
    llm_requests.inc()

    payload = {
        "model": MODEL,
        "messages": [{
            "role": "user",
            "content": prompt
        }],
        "stream": True
    }
    print(payload)
    
    for attempt in range(4):
        try:
            stream = groq_client.chat.completions.create(**payload)
            full = ""

            for chunk in stream:

                token = chunk.choices[0].delta.content or ""

                print(token, end="", flush=True)

                full += token

            llm_latency.observe(time.time() - start)

            return full

        except Exception:

            if attempt == 3:
                raise

            print(f"ERROR, Retrying .. Attempt: {attempt}")

            time.sleep(2 ** attempt)

