def task_success(output, expected) -> bool:
    """
    Return whether the agent's output contains the expected answer.

    A simple substring match is used as the task success criterion.
    """
    return str(expected) in str(output)


def pass_at_k(passed, retries, k) -> bool:
    """
    Return whether the task was solved within the first k attempts.

    Since `retries` counts failed attempts after the initial generation,
    a task succeeds within k attempts when it passes and:
        retries < k

    Examples:
        retries = 0 -> solved on the first attempt.
        retries = 1 -> solved on the second attempt.
        retries = 2 -> solved on the third attempt.
    """
    return passed and retries < k