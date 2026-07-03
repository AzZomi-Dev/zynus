"""
LLM client for communicating with the Ollama server.

This module provides a reusable HTTP session with connection pooling,
automatic retry logic, streaming response handling, and Prometheus metrics.

Responsibilities:
- Send prompts to the configured LLM.
- Stream generated tokens.
- Measure request latency.
- Count total LLM requests.
- Retry transient network failures.
- Parse JSON responses when required.
"""

import json
import time

import requests
from requests.adapters import HTTPAdapter

from config import MODEL, OLLAMA_URL
from observability.metrics import llm_latency, llm_requests

# ---------------------------------------------------------------------
# Reusable HTTP session
#
# Using a single Session enables HTTP keep-alive and connection pooling,
# reducing latency and avoiding unnecessary TCP/TLS handshakes.
# ---------------------------------------------------------------------

session = requests.Session()

adapter = HTTPAdapter(
    pool_connections=20,
    pool_maxsize=100,
)

session.mount("http://", adapter)
session.mount("https://", adapter)


def ask_llm(prompt: str) -> str:
    """
    Send a prompt to the configured LLM and stream the generated response.

    Features:
    - HTTP connection pooling
    - Streaming token generation
    - Automatic retries with exponential backoff
    - Prometheus request counting
    - Prometheus latency measurement

    Args:
        prompt:
            Prompt sent to the language model.

    Returns:
        The complete generated response as a string.

    Raises:
        requests.RequestException:
            Raised after all retry attempts fail.
    """

    start = time.time()

    payload = {
        "prompt": prompt,
        "model": MODEL,
        "stream": True,
    }

    print(payload)

    llm_requests.inc()

    # Retry transient network failures.
    for attempt in range(4):
        try:
            with session.post(
                OLLAMA_URL,
                json=payload,
                stream=True,
                timeout=60,
            ) as response:

                response.raise_for_status()

                full = ""

                # Read streamed tokens as they arrive.
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

            # Exponential backoff:
            # 1s → 2s → 4s
            time.sleep(2 ** attempt)


def ask_llm_json(prompt: str):
    """
    Request structured JSON output from the LLM.

    Supports both:
    - Raw JSON
    - Markdown fenced JSON blocks (```json ... ```)

    Args:
        prompt:
            Prompt requesting JSON output.

    Returns:
        Parsed Python object.
    """

    response = ask_llm(prompt)

    if "```json" in response:
        obj, _ = json.JSONDecoder().raw_decode(response[8:])
        return obj

    try:
        return json.loads(response)
    except json.JSONDecodeError:
        return {}