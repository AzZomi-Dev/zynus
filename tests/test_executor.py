from agents.executor import executor_agent

def test_safe_code():

    stdout, stderr = executor_agent("""print(41)""")

    assert stdout.strip() == "41"
    assert stderr == ""

def test_timeout():

    stdout, stderr = executor_agent("""
while True:
    pass
""")

    assert "execution timed out" in stderr.lower()
    
def test_network_blocked():
    stdout, stderr = executor_agent("""
import urllib.request

print(urllib.request.urlopen("https://google.com").read())
""")
    
    assert stderr != ""