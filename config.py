DEBUG_MODE = True
MODE = "fixed" # fall

MODEL = "gemma3:1b"
EMB_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
URL = "http://localhost:11434/api/generate"

SANDBOX_URL = "http://localhost:7070/execute"
QDRANT_URL = "http://localhost:6333"
DATABASE_URL = "mysql+pymysql://root:123@localhost:3306/zynusdb"

GRAPH_RETRIES = 3