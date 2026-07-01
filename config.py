ENTRYPOINT = "router"
DEBUG_MODE = False
MODE = "fixed" # fall | fixed

MODEL = "gemma3:1b"
EMB_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
OLLAMA_URL = "http://localhost:11434/api/generate"

SANDBOX_URL = "http://localhost:7070/execute"
QDRANT_URL = "http://localhost:6333"
DATABASE_URL = "mysql+pymysql://root:123@localhost:3306/zynusdb"
REDIS_URL = "redis://localhost:6379/0"

REQUESTS_WINDOW = 60
REQUESTS_LIMIT = 4

GRAPH_RETRIES = 3