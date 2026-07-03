"""
Research agent.

This agent performs tool-assisted reasoning using a simple ReAct
(Reason + Act) workflow.

Workflow:
1. Present the available tools to the LLM.
2. Ask the LLM to select the appropriate tool.
3. Execute the selected tool.
4. Record the observation.
5. Repeat for a fixed number of reasoning steps.
6. Return the accumulated scratchpad.

Responsibilities:
- Tool selection.
- Tool execution.
- Observation collection.
- Multi-step reasoning.
"""

import json

from agents.llm import ask_llm_json
from schemas.researcher_schema import ResearcherResponse
from tools.registry import TOOLS


def call_tool(tool_name: str, tool_input: str):
    """
    Execute a registered tool.

    Args:
        tool_name:
            Name of the tool selected by the LLM.

        tool_input:
            Input passed to the selected tool.

    Returns:
        Tool execution result.
    """

    return TOOLS[tool_name]["function"](tool_input)


def researcher_agent(query: str) -> str:
    """
    Perform tool-assisted research for a user query.

    The agent repeatedly asks the LLM to choose the most appropriate
    tool, executes it, and records the observation in a scratchpad.
    The accumulated scratchpad can later be injected into prompts
    to provide grounded information.

    Args:
        query:
            User research request.

    Returns:
        Scratchpad containing all tool calls and observations.
    """

    available_tools = {
        tool_name: {
            "description": TOOLS[tool_name]["description"]
        }
        for tool_name in TOOLS
    }

    scratchpad = ""

    prompt = f"""
You are a researcher agent.

Available tools:
{json.dumps(available_tools, indent=2)}

Return only valid JSON.

Example:
{{
    "tool_name": "retriever_tool",
    "tool_input": "what is Python?"
}}

The query is:
{query}
"""

    # Perform a fixed number of reasoning iterations.
    for _ in range(2):

        if scratchpad:
            prompt += f"\nScratchpad:\n{scratchpad}"

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