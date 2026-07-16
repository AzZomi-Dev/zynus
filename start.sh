#!/bin/sh
rq worker memory-write &
exec uvicorn api.server:app --host 0.0.0.0 --port 8000