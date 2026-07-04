def task_success(output, expected) -> bool:
    return str(expected) in str(output)

def pass_at_k(passed, retries, k) -> bool:
    return passed and retries < k