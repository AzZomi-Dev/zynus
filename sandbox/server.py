from fastapi import FastAPI
import subprocess
import tempfile
import os

app = FastAPI(title="zynus", version="1.0.1")

async def execute_code(code: str):
    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            suffix=".py",
            mode="w",
            delete=False,
            encoding="utf-8"
        ) as f:
            f.write(code)
            temp_path = f.name

        result = subprocess.run(
            ["python", temp_path], 
            capture_output=True, 
            text=True,
            timeout=10
        )
        return {
            "stdout": result.stdout, 
            "stderr": result.stderr
        }
    except subprocess.TimeoutExpired:
        return {
            "stdout": "",
            "stderr": "Execution timed out"
        }

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
    
@app.get("/")
async def home():
    return {"message": "zynus-sandbox is running"}

@app.post("/execute")
async def execute(payload: dict):
    result = await execute_code(payload["code"])
    return result