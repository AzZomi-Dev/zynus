"""
Application entry point.

This module configures the FastAPI application, exposes the public API,
registers middleware, health checks, Prometheus metrics, and executes
the LangGraph workflow.

Responsibilities:
- Configure the FastAPI application.
- Expose REST endpoints.
- Perform dependency health checks.
- Execute workflow requests.
- Expose Prometheus metrics protected by Basic Authentication.
- Apply request rate limiting.
"""

import os
import secrets
import logging
import requests

from fastapi import FastAPI, Depends, HTTPException, status, Response
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.middleware.cors import CORSMiddleware
from main import graph_builder, build_initial_state
from pydantic import BaseModel
from config import OLLAMA_URL, SANDBOX_URL, LLM_PROVIDER
from database.db import SessionLocal
from sqlalchemy import text
from middleware.rate_limit import rate_limit_dependency
from redis_services.redis_client import redis_conn
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from providers.llms.groq import groq_client
from memory.qdrantClient import get_qdrant_client
from observability.metrics import workflow_runs, active_workflows
from api.routes.stream import router as stream_router

app = FastAPI(title="zynus", version="1.0.6")

# --- Basic Auth Security Setup ---
security = HTTPBasic()

METRICS_USER = os.getenv("METRICS_USER", "metrics_user")
METRICS_PASS = os.getenv("METRICS_PASS", "super_secret_password")

def verify_metrics_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    correct_user = secrets.compare_digest(credentials.username, METRICS_USER)
    correct_pass = secrets.compare_digest(credentials.password, METRICS_PASS)
    if not (correct_user and correct_pass):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid metrics credentials",
            headers={"WWW-Authenticate": "Basic"},
        )

class IgnoreMetricsFilter(logging.Filter):
    """
    Exclude Prometheus scrape requests from access logs.
    """    
    def filter(self, record):
        return "/metrics" not in record.getMessage()

class IgnoreStreamFilter(logging.Filter):
    def filter(self, record):
        return "/ask/stream" not in record.getMessage()

logging.getLogger("uvicorn.access").addFilter(IgnoreMetricsFilter())
logging.getLogger("uvicorn.access").addFilter(IgnoreStreamFilter())

app.include_router(stream_router)

class Query(BaseModel):
    """
    Request model for workflow execution.
    """

    query: str
    trace_id: str
    deep_thinking: bool = False

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    """
    Perform dependency health checks.

    Verifies connectivity to:
    - LLM
    - Sandbox service
    - Qdrant
    - Database
    - Redis

    Returns:
        Overall application health and the status of each dependency.
    """
    try:
        if LLM_PROVIDER == "ollama":
            response = requests.get(
                OLLAMA_URL.replace("/generate", "/tags"),
                timeout=3
            )
            llm_ok = response.status_code == 200
        elif LLM_PROVIDER == "groq":
            groq_client.models.list()
            llm_ok = True
        else:
            llm_ok = False
    except Exception:
        llm_ok = False

    try:
        response = requests.get(
            SANDBOX_URL.replace("/execute", "/"),
            timeout=3
        )
        sandbox_ok = response.status_code == 200
    except Exception:
        sandbox_ok = False

    try:
        qdrant_client = get_qdrant_client()
        qdrant_client.get_collections()
        qdrant_ok = True
    except Exception:
        qdrant_ok = False

    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        database_ok = True
    except Exception:
        database_ok = False
    finally:
        db.close()

    try:
        redis_conn.ping()
        redis_ok = True
    except Exception:
        redis_ok = False

    return {
        "status": "healthy" if llm_ok and sandbox_ok and qdrant_ok and database_ok and redis_ok else "degraded",
        "llm": "up" if llm_ok else "down",
        "sandbox": "up" if sandbox_ok else "down",
        "qdrant": "up" if qdrant_ok else "down",
        "database": "up" if database_ok else "down",
        "redis": "up" if redis_ok else "down"
    }

@app.get("/")
async def home():
    """
    Simple endpoint used to verify that the API is running.
    """
    return {"message": "Zynus is running"}

@app.get("/metrics", dependencies=[Depends(verify_metrics_credentials)])
async def metrics_endpoint():
    """
    Expose Prometheus metrics protected by Basic Authentication.
    """
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.post("/run")
async def ask(request: Query, _: None = Depends(rate_limit_dependency)):
    """
    Execute the multi-agent workflow.

    The request passes through the LangGraph workflow and returns the
    final workflow state.

    Metrics are collected for:
    - Total workflow executions.
    - Currently active workflows.
    """
    try:
        workflow_runs.inc()
        active_workflows.inc()
        query = request.query
        deepThinking = request.deep_thinking
        print("Deep thinking:", deepThinking)
        initial_state = build_initial_state(query, deepThinking)
        initial_state["trace_id"] = request.trace_id
        result = await graph_builder.ainvoke(initial_state)
        
        return {
            "trace_id": initial_state["trace_id"],
            "result": result
        }
    finally:
        active_workflows.dec()