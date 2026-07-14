"""
Application configuration.

This module centralizes application settings loaded from environment
variables and defines runtime constants shared across the project.

Configuration includes:
- Workflow settings
- Model configuration
- Service endpoints
- Cache settings
- Rate limiting
- Retry limits
"""

import os
from dotenv import load_dotenv
load_dotenv(".env.local", override=False)

ENTRYPOINT = "router"
DEBUG_MODE = False
MODE = "fixed" # fall | fixed

EMB_MODEL = os.getenv("EMB_MODEL")
EMB_MODEL_PROVIDER = os.getenv("EMB_MODEL_PROVIDER") # google | huggingface

MODEL = os.getenv("MODEL")
LLM_PROVIDER = os.getenv("LLM_PROVIDER") # ollama | groq
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OLLAMA_URL = os.getenv("OLLAMA_URL")
SANDBOX_URL = os.getenv("SANDBOX_URL")

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_URL = os.getenv("REDIS_URL")

TTL = 300
REQUESTS_WINDOW = 60
REQUESTS_LIMIT = 4

GRAPH_RETRIES = 3