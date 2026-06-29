from fastapi import FastAPI
from main import graph_builder, build_initial_state
from pydantic import BaseModel
from config import OLLAMA_URL, SANDBOX_URL, QDRANT_URL
from database.db import SessionLocal
from sqlalchemy import text
import requests

app = FastAPI(title="zynus", version="1.0.1")

class Query(BaseModel):
    query: str

@app.get("/health")
async def health():

    try:
        response = requests.get(
            OLLAMA_URL.replace("/generate", "/tags"),
            timeout=3
        )
        ollama_ok = response.status_code == 200

    except Exception:
        ollama_ok = False

    try:
        response = requests.get(
            SANDBOX_URL.replace("/execute", "/"),
            timeout=3
        )
        sandbox_ok = response.status_code == 200
    except Exception:
        sandbox_ok = False

    try:
        response = requests.get(
            QDRANT_URL,
            timeout=3
        )
        qdrant_ok = response.status_code == 200
    except Exception:
        qdrant_ok = False

    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        mysql_ok = True
    except Exception:
        mysql_ok = False
    finally:
        db.close()

    return {
        "status": "healthy" if ollama_ok and sandbox_ok and qdrant_ok and mysql_ok else "degraded",
        "ollama": "up" if ollama_ok else "down",
        "sandbox": "up" if sandbox_ok else "down",
        "qdrant": "up" if qdrant_ok else "down",
        "mysql": "up" if mysql_ok else "down"
    }

@app.get("/")
async def home():
    return {"message": "Zynus is running"}

@app.post("/run")
async def ask(request: Query):
    
    query = request.query
    result = await graph_builder.ainvoke(build_initial_state(query))
    
    return result