"""
Benchmark the agent on a fixed evaluation dataset.

For each benchmark task, the evaluation pipeline:
1. Executes the graph.
2. Measures execution latency.
3. Checks whether the produced output matches the expected answer.
4. Computes Pass@k metrics (Pass@1, Pass@3, Pass@5), indicating whether
   the task was solved within the first k attempts.
5. Stores per-task metrics.

Finally, aggregate statistics are reported, including:
- Success rate
- Pass@1
- Pass@3
- Pass@5
- Average latency
- Average retries

Pass@k is used to evaluate the effectiveness of the retry mechanism. By
comparing Pass@k values, you can determine whether allowing additional
retries meaningfully improves performance or simply increases latency and
cost. This helps guide the choice of the retry budget (GRAPH_RETRIES).
"""

import json
import time
from main import graph_builder, build_initial_state
from evaluation.metrics import task_success, pass_at_k

with open(
    "evaluation/benchmark_tasks.json", 
    "r", 
    encoding="utf-8"
) as f:

    tasks = json.load(f)
    
results = []
for sample in tasks:

    task = sample["task"]
    expected = sample["expected"]

    start = time.time()
    state = graph_builder.invoke(build_initial_state(task))
    latency = time.time() - start

    passed = task_success(state["output"], expected)

    pass1 = pass_at_k(passed, state["retries"], 1)
    pass3 = pass_at_k(passed, state["retries"], 3)
    pass5 = pass_at_k(passed, state["retries"], 5)

    results.append({
        "task": task,
        "pass": passed,
        "pass@1": pass1,
        "pass@3": pass3,
        "pass@5": pass5,
        "latency": latency,
        "retries": state["retries"]
    })
    
total = len(results)
if total == 0:
    raise ValueError("No benchmark tasks found.")

passed_rate = (
    sum(r["pass"] for r in results) / total
)

pass1_rate = (
    sum(r["pass@1"] for r in results) / total
)

pass3_rate = (
    sum(r["pass@3"] for r in results) / total
)

pass5_rate = (
    sum(r["pass@5"] for r in results) / total
)

avg_latency = (
    sum(r["latency"] for r in results) / total
)

avg_retries = (
    sum(r["retries"] for r in results) / total
)

print("\n--- Benchmark ---\n")

print(f"Success rate: {passed_rate:.2%}")

print(f"Pass@1: {pass1_rate:.2%}")
print(f"Pass@3: {pass3_rate:.2%}")
print(f"Pass@5: {pass5_rate:.2%}")

print(f"Avg latency: {avg_latency:.2f}s")

print(f"Avg retries: {avg_retries:.2f}")