import time
import subprocess
import sys

print("Running regression suite..")

start = time.time()

result = subprocess.run(
    [sys.executable, "-m", "evaluation.evaluator"],
    capture_output=True,
    text=True
)

end = time.time()

print(result.stdout)

if result.stderr:
    print(f"ERRORS:\n{result.stderr}")

print(f"Regression suite finished in {end-start:.2f}s")