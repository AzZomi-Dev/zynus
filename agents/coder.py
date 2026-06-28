from agents.llm import ask_llm
from config import DEBUG_MODE

def coder_agent(
        query: str, 
        code: str, 
        feedback: str
    ):

    # ---------- Debugging Mode ----------
    if DEBUG_MODE:
        return "```print('Hello World')```"
    # ------------------------------------

    prompt = f"Without explanation, using Python, solve this: {query}"

    if feedback:
        prompt += f"""
Your previous code was:
{code}

Feedback:
{feedback}
"""
    
    return ask_llm(prompt)