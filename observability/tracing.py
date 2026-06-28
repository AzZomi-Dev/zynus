import uuid

def create_trace_id() -> str:
    return str(uuid.uuid4())