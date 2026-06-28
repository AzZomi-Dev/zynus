from agents.llm import ask_llm_json
from schemas.critic_schema import CriticResponse
from config import DEBUG_MODE, MODE

def critic_agent(query: str, code: str, error: str, retries):

    # ---------- Debugging Mode ----------
    if DEBUG_MODE:
        if MODE == "fixed":
            if retries == 0:
                return False, "Fail feedback test"
            if retries == 1:
                return True, "Success feedback test"
                
        if MODE == "fall":
            return False, error
    # ------------------------------------

    if error.strip():
        return False, f"Error: {error}"
    
    prompt = f"""
You are an evaluator.
The task was: {query}
And generated code: {code}

Return only valid JSON. Example:
{{
    "success": True,
    "feedback": "Why"
}}
Be strict and concise
"""
    response = ask_llm_json(prompt)
    parsed = CriticResponse(**response)

    success = parsed.success
    feedback = parsed.feedback
    
    return success, feedback