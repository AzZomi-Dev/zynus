from agents.llm import ask_llm

def responder_agent(query: str, research: str):

    prompt = f"""
Query: {query}
Research: {research}
"""
    
    return ask_llm(prompt)