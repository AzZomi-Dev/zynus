from agents.llm import ask_llm

def responder_agent(query: str):
    return ask_llm(query)