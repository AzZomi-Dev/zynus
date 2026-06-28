FROM python:3.10-slim-bullseye

WORKDIR /app

RUN pip install fastapi uvicorn

COPY sandbox/server.py .

RUN useradd -m sandboxuser

USER sandboxuser

EXPOSE 7070

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "7070"]