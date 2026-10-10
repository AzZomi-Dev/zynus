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
from mcp import StdioServerParameters

from agents.llm import ask_llm_json
from schemas.researcher_schema import ResearcherResponse
from mcp_services.mcp_client import call_mcp_tool, get_available_tools
from observability.logger import logger
from pydantic import ValidationError

server_params = StdioServerParameters(
    command="python",
    args=["-m", "mcp_services.mcp_server"]
)

async def researcher_agent(query: str) -> str:
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
        Observations.
    """

    available_tools = await get_available_tools()
    scratchpad = ""
    observations = []

    prompt = f"""
You are a researcher agent.

Available tools:
{json.dumps(available_tools, indent=2)}

Return only valid JSON.

Schema:
{{
"tool_name": "retriever",
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

        try:
            parsed = ResearcherResponse(**response)
        except ValidationError as e:
            logger.warning(
                "Invalid researcher response. Retrying: %s",
                e
            )
            continue
        
        tool_name = parsed.tool_name
        tool_input = parsed.tool_input

        result = await call_mcp_tool(
            tool_name,
            {"query": tool_input}
        )
        if not result.content:
            logger.info("No faqs found in the collection")
            return ""

        observation = result.content[0].text
        observations.append(observation)

        scratchpad += f"""
Tool name: {tool_name}
Tool input: {tool_input}
Observation: {observation}
"""

    return observations