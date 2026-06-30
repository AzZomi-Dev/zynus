from agents.llm import ask_llm_json
from schemas.router_schema import RouterResponse

def router_agent(query: str):
    prompt = f"""
You are a router agent.
Choose the best route based on the query type:
- qa:
For simple question and answer queries

- code:
For queries requires writing code like Python

Return only valid JSON. Example:
{{
    "route": "qa"
}}
The query is: {query}

"""
    response = ask_llm_json(prompt)
    parsed = RouterResponse(**response)

    route = parsed.route
    allowed_routes = {"qa", "code"}

    if route not in allowed_routes:
        return "qa"
    
    return route