"""
LLM client for communicating with the Ollama/Groq server.

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

from providers.llms.ollama import ask_ollama
from providers.llms.groq import ask_groq

import json
from config import LLM_PROVIDER

# ---------------------------------------------------------------------
# Reusable HTTP session
#
# Using a single Session enables HTTP keep-alive and connection pooling,
# reducing latency and avoiding unnecessary TCP/TLS handshakes.
# ---------------------------------------------------------------------

def ask_llm(prompt: str):
    if LLM_PROVIDER == "ollama":
        return ask_ollama(prompt)
    
    if LLM_PROVIDER == "groq":
        return ask_groq(prompt)

    raise ValueError(f"Unsupported LLM provider: {LLM_PROVIDER}")

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