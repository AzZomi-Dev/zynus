from prometheus_client import Counter, Gauge, Histogram

workflow_runs = Counter(
    "workflow_runs_total",
    "Total workflow runs"
)

active_workflows = Gauge(
    "active_workflows_total",
    "Total active users"
)

llm_requests = Counter(
    "llm_requests_total",
    "Total LLM requests"
)

llm_latency = Histogram(
    "llm_latency_seconds",
    "LLM latency"
)