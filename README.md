<p align="center">
  <img src="./logo.svg" alt="Zynus" width="420">
</p>

# A multi-agent AI system
## Built with **LangGraph**, **FastAPI**, **Ollama**, **Qdrant**, **MySQL**, and **Docker**

---

# Architecture

```text
                         ┌────────────┐
                         │   Router   │
                         └─────┬──────┘
                               │
         ┌─────────────────────┼─────────────────────┐
         │                     │                     │
         ▼                     ▼                     ▼
      QA Route           Research Route        Coding Route
         │                     │                     │
         │                     ▼                     ▼
         │                Researcher          Memory Retriever
         │                     │                     │
         │                     ▼                     ▼
         │                 Responder               Coder
         │                                           │
         │                                           ▼
         │                                        Sandbox
         │                                           │
         │                                           ▼
         │                                        Critic
         │                                           │
         │                    ┌──────────────────────┴───────────────┐
         │                    │                                      │
         ▼                    ▼                                      ▼
        END                Success                                Failure
                               │                                      │
                               ▼                                      ▼
                          MySQL + Qdrant                     Retry with feedback
                                                                      │
                                                                      ▼
                                                               Re-execution
                                                                      │
                                                                      ▼
                                                                   Critic
```

---

# Enterprise Features

* Multi-agent orchestration using LangGraph
* Autonomous task routing
* Self-repairing execution loop
* Secure sandboxed code execution
* Long-term semantic memory
* Qdrant vector database
* Health monitoring endpoints
* Redis-based rate limiting
* Connection pooling
* Structured logging
* Request correlation IDs
* Alembic database migrations
* Dockerized deployment

---

# Secure Code Execution

Generated code executes inside an isolated sandbox.

Security mechanisms include:

* Docker isolation
* Non-root execution
* Read-only filesystem
* CPU limits
* Memory limits
* Process limits
* Execution timeout
* Temporary filesystem cleanup

```text
Generated Code
      │
      ▼
 Sandbox API
      │
      ▼
 Python Runtime
      │
      ▼
 stdout / stderr
```

# Health Monitoring

The API exposes health endpoints that verify:

* API availability
* Database connectivity
* Sandbox availability
* LLM availability

Example response:

```json
{
  "status": "healthy",
  "database": "up",
  "sandbox": "up",
  "ollama": "up"
}
```

---

# Technology Stack

## AI Framework

* LangGraph

## LLM

* Ollama

## Backend

* FastAPI

## Database

* MySQL
* SQLAlchemy
* Alembic

## Vector Database

* Qdrant