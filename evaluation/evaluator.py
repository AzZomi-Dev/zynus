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