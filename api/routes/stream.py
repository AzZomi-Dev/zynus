import asyncio
import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

router = APIRouter()

event_queue = asyncio.Queue()

async def event_generator(trace_id: str):
    while True:
        event = await event_queue.get()

        if event.get("trace_id") != trace_id:
            continue

        yield f"data: {json.dumps(event)}\n\n"

@router.get("/run/stream")
async def stream(trace_id: str):

    return StreamingResponse(
        event_generator(trace_id),
        media_type="text/event-stream"
    )