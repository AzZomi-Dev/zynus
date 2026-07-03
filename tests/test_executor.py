"""
Tests for the sandbox execution agent.

These tests verify that generated code executes correctly inside the
sandbox and that security restrictions are enforced.
"""
from agents.executor import executor_agent

def test_safe_code():
    """
    Verify that valid Python code executes successfully.
    """
    stdout, stderr = executor_agent("""print(41)""")

    assert stdout.strip() == "41"
    assert stderr == ""

def test_timeout():
    """
    Verify that long-running code is terminated by the sandbox timeout.
    """
    stdout, stderr = executor_agent("""
while True:
    pass
""")

    assert "execution timed out" in stderr.lower()
    
def test_network_blocked():
    """
    Verify that outbound network access is blocked inside the sandbox.
    """
    stdout, stderr = executor_agent("""
import urllib.request

print(urllib.request.urlopen("https://google.com").read())
""")
    
    assert stderr != ""