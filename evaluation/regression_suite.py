"""
Regression test runner.

This script executes the regression evaluation suite, reports its output,
and measures the total execution time. It is intended as a convenience
wrapper for running the project's automated regression tests.
"""

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