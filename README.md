<p align="center">
  <img src="./logo.svg" alt="Zynus" width="420">
</p>

---

> **An AI backend that uses multiple AI agents to solve tasks, run code safely, and learn from previous work.**

Zynus receives a task, chooses the right AI agent, runs code in a secure sandbox, fixes errors if needed, and remembers successful solutions to improve future results.

---

# Features

* Retrieval-augmented-generation (RAG)
* Web search
* Redis cache
* Redis Queue (RQ)
* Qdrant vector database
* MySQL database
* Health checks
* Connection pooling
* Structured logging
* Rate limiting
* Alembic migrations
* Dockerized deployment
* Unit tests with Pytest
* Prometheus metrics
* Grafana dashboards


---

# How It Works

```text
                    ┌────────────────────────────────────┐
                    │          Client / Frontend         │
                    └─────────────────┬──────────────────┘
                                      │
                                      ▼
                        ┌─────────────────────────────┐
                        │        Router Agent         │
                        └─────────────┬───────────────┘
                                      │
             ┌────────────────────────┼────────────────────────┐
             │                        │                        │
             ▼                        ▼                        ▼
      General Question          Research Task            Coding Task
             │                        │                        │
             ▼                        ▼                        ▼
       Direct Response        Research Agent            Memory Retrieval
                                                               │
                                                               ▼
                                                     Redis Memory Cache
                                                               │
                          ┌────────────────────────────────────┴─────────────────────────────┐
                          │                                                                  │
                     Cache Hit                                                         Cache Miss
                          │                                                                  │
                          ▼                                                                  │
                 Return Cached Context                                                       │
                                                                                             │
                                                                                             │
                                                            ┌────────────────────────────────┘
                                                            │    
                                                            │
                                                  Generate Embedding
                                                            │
                                                            ▼
                                                       Query Qdrant
                                                            │
                                                            ▼
                                                  Top-K Similar Memories
                                                            │
                                                            ▼
                                                  Build Prompt Context
                                                            │
                                                            ▼
                                                     Code Generator
                                                            │
                                                            ▼
                                                      Ollama/Groq (LLM)
                                                            │
                                                            ▼
                                                     Generated Code
                                                            │
                                                            ▼
                                                    Sandbox Executor
                                                            │
                     ┌──────────────────────────────────────┼────────────────────────────────┐
                     │                                      │                                │
                     ▼                                      ▼                                ▼
                Execution Success                   Runtime / Syntax Er               Sandbox Timeout
                     │                                      │                                │
                     └──────────────────────────────────────┼────────────────────────────────┘
                                                            │
                                                            ▼
                                                       Critic Agent
                                                            │
                                   ┌────────────────────────┴──────────────────────────┐
                                   │                                                   │
                                   ▼                                                   ▼
                              Output Accepted                                   Needs Improvement
                                   │                                                   │
                                   ▼                                                   ▼
                              Final Response                                     Repair Agent
                                                                                       │
                                                                                       ▼
                                                                                 Ollama/Groq (LLM)
                                                                                       │
                                                                                       ▼
                                                                                  Updated Code
                                                                                       │
                                                                                       ▼
                                                                                  Retry Counter
                                                                                       │
                                   ┌─────────────────────────┬─────────────────────────┘
                                   │                         │
                                   ▼                         ▼
                              Retry Allowed             Retry Limit Reached
                                   │                         │
                                   ▼                         ▼
                              Sandbox Executor          Fallback Response
                                   │
                                   └─────────────────────────────┐
                                                                 ▼
                                                       Successful Execution
                                                                 │
                                                                 ▼
                                                     Return Response to Client
                                                                 │
                                                                 ▼
                                                   Background Memory Queue (RQ)
                                                                 │
                                                                 ▼
                                                       Redis Queue (Persistent)
                                                                 │
                                                                 ▼
                                                       Background Worker
                                                                 │
                                        ┌────────────────────────┴───────────────────┐
                                        │                                            │
                                        ▼                                            ▼
                              Save Memory Record                             Generate Embedding
                                        │                                            │
                                        ▼                                            ▼
                                   MySQL                                    SentenceTransformer
                                        │                                            │
                                        │                                            ▼
                                        │                                      Upsert Vector
                                        │
                                        └─────────────────────►Qdrant
                                                                 │
                                                                 ▼
                                                  Future Semantic Retrieval
```

---

# The Flow

## 1. Receive a Task

A user sends a request to the API.

```text
POST /run
```

Example:

```text
Write Python code that computes fibonacci(10)
```

---

## 2. Route the Task

The Router Agent decides where the request should go.

```text
           Task
             │
             ▼
      Router Agent
             │
   ┌─────────┼─────────┐
   ▼         ▼         ▼
  QA     Research    Coding
```

**Why?:** Different tasks require different agents. Routing avoids using the wrong workflow.

**Examples:**

- "What is Python?" → **QA** (general question)
- "What are today's top news headlines?" → **Research** (requires web search)
- "Write Python code to print 'Hello, World!'" → **Coding**

---

# Project Structure

```text
zynus/
├── agents/
│   ├── coder.py
│   ├── critic.py
│   ├── executor.py
│   ├── fallback.py
│   ├── llm.py
│   ├── memory_agent.py
│   ├── researcher.py
│   ├── responder.py
│   └── router.py
│
├── api/
│   └── server.py
│
├── database/
│   ├── db.py
│   ├── models.py
│   └── repository.py
│
├── qdrant/
│   ├── _ensure_collection.py
│   ├── memory_writer.py
│   └── vectorstore.py
│
├── middleware/
│   └── rate_limit.py
│
├── migrations/
│   ├── versions/
│   ├── env.py
│   ├── README
│   └── script.py.mako
│
├── observability/
│   ├── logger.py
│   └── tracing.py
│
├── redis_services/
│   ├── redis_cache.py
│   ├── redis_client.py
│   └── redis_queue.py
│
├── sandbox/
│   ├── Dockerfile
│   └── server.py
│
├── schemas/
│   ├── critic_schema.py
│   ├── researcher_schema.py
│   └── router_schema.py
│
├── tools/
│   ├── rag.py
│   ├── registry.py
│   ├── utils.py
│   └── web_search_tool.py
│
├── .dockerignore
├── .env
├── .env.local
├── alembic.ini
├── config.py
├── docker-compose.yml
├── Dockerfile
├── logo.svg
├── main.py
├── prometheus.yml
└── README.md
```

---

# Run Locally

Clone the repository:

```bash
git clone <repository-url>
cd zynus
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure the environment varibles by creating the following files in the project root.

### `.env`

```env
MYSQL_ROOT_PASSWORD=123
MYSQL_DATABASE=zynusdb
DATABASE_URL=mysql+pymysql://root:123@mysql:3306/zynusdb

ENTRYPOINT=router
LLM_PROVIDER=groq
MODEL=llama-3.1-8b-instant

EMB_MODEL_PROVIDER=google
EMB_MODEL=models/gemini-embedding-001

GEMINI_API_KEY=your_gemini_api_key
GROQ_API_KEY=your_groq_api_key
QDRANT_API_KEY=your_qdrant_api_key

OLLAMA_URL=None
SANDBOX_URL=http://sandbox:7070/execute
QDRANT_URL=http://qdrant:6333
REDIS_URL=redis://redis:6379/0
```

### `.env.local`

```env
MYSQL_ROOT_PASSWORD=123
MYSQL_DATABASE=zynusdb
DATABASE_URL=mysql+pymysql://root:123@localhost:3306/zynusdb

ENTRYPOINT=router
LLM_PROVIDER=ollama
MODEL=gemma3:1b

EMB_MODEL_PROVIDER=huggingface
EMB_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2

GEMINI_API_KEY=None
GROQ_API_KEY=None
QDRANT_API_KEY=None

OLLAMA_URL=http://localhost:11434/api/generate
SANDBOX_URL=http://localhost:7070/execute
QDRANT_URL=http://localhost:6333
REDIS_URL=redis://localhost:6379/0
```

> **Important:** These values are examples. Update them to match your setup.
>
> **Note:** Set `LLM_PROVIDER` to `groq` or `ollama`, and `EMB_MODEL_PROVIDER` to `google` or `huggingface` depending on the providers you want.
>
> - If using **Groq**, create an API key from https://console.groq.com/keys and set `GROQ_API_KEY`.
> - If using **Google Gemini embeddings**, create an API key from https://aistudio.google.com/app/apikey and set `GEMINI_API_KEY`.
> - If using **Qdrant Cloud**, create a cluster at https://cloud.qdrant.io, generate an API key, and set `QDRANT_URL` and `QDRANT_API_KEY`.
> - If using **Ollama**, **Hugging Face embeddings**, or a local **Qdrant** instance, no API keys are required.

Run with Docker

```bash
docker compose up -d
```

Run without Docker


```bash
uvicorn api.server:app --reload
```

Check health:

```http
http://localhost:8000/health
```

Open the interactive API documentation:

```
http://localhost:8000/docs
```

Example POST request for the `/run` endpoint:

```json
{
  "query": "Write a Python Fibonacci function."
}
```

---

# Testing

Run the tests to make sure the sandbox:

- Runs Python code correctly
- Stops code that runs forever
- Blocks internet access

```bash
pytest
```

---

# Benchmarking and Evaluation

Built-in evaluation suite measures:

- Success Rate
- Pass@k
- Latency
- Retry Count

Run benchmark:

```bash
python -m evals.evaluator
```

Run regression suite:

```bash
python -m evals.regression_suite
```

---

# Tech Stack

* Python
* FastAPI
* LangGraph
* Groq
* Ollama
* Docker
* Redis
* MySQL
* Qdrant
* SQLAlchemy
* RQ
* Prometheus
* Grafana
* Pytest

---

# Future Improvements

* Kubernetes
* Distributed agents

---