from fastapi import FastAPI
from main import graph_builder, build_initial_state
from pydantic import BaseModel

app = FastAPI(title="zynus", version="1.0.1")

class Query(BaseModel):
    query: str

@app.get("/")
async def home():
    return {"message": "Zynus is running"}

@app.post("/run")
async def ask(request: Query):
    
    query = request.query
    result = await graph_builder.ainvoke(build_initial_state(query))
    
    return result