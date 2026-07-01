from schemas.researcher_schema import ResearcherResponse
from agents.llm import ask_llm_json
from tools.registry import TOOLS
import json

def call_tool(tool_name: str, tool_input: str):
    tool_fn = TOOLS[tool_name]["function"](tool_input)
    return tool_fn

def researcher_agent(query: str):

    available_tools = {
        tool_name: {
            "description": TOOLS[tool_name]["description"]
        } for tool_name in TOOLS
    }

    scratchpad = ""
    prompt = f"""
You are a researcher agent.
Available tools:
{json.dumps(available_tools, indent=2)}

Return only valid JSON. Example:
{{
    "tool_name": "retriever_tool",
    "tool_input: "what is Python?"
}}

The query is: {query}
"""
    for _ in range(2):
        if scratchpad:
            prompt += f"Scratchpad: {scratchpad}"
            
        response = ask_llm_json(prompt)
        parsed = ResearcherResponse(**response)
        
        tool_name = parsed.tool_name
        tool_input = parsed.tool_input
        observation = call_tool(tool_name, tool_input)
        
        scratchpad += f"""
Tool name: {tool_name}
Tool input: {tool_input}
Observation: {observation}
"""
    
    return scratchpad