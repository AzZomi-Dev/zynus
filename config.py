import os
from dotenv import load_dotenv
load_dotenv(".env.local")

ENTRYPOINT = "router"
DEBUG_MODE = False
MODE = "fixed" # fall | fixed

MODEL = "gemma3:1b"
EMB_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

OLLAMA_URL = os.getenv("OLLAMA_URL")
SANDBOX_URL = os.getenv("SANDBOX_URL")
QDRANT_URL = os.getenv("QDRANT_URL")
DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_URL = os.getenv("REDIS_URL")

REQUESTS_WINDOW = 60
REQUESTS_LIMIT = 4

GRAPH_RETRIES = 3