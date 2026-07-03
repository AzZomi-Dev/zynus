"""
Tool registry.

This module defines all tools that can be invoked by the researcher
agent. Each registered tool exposes:

- function: Callable executed by the agent.
- description: Natural-language description presented to the LLM for
  tool selection.

To add a new tool, register it in the TOOLS dictionary.
"""

from tools.rag import retriever_tool
from tools.web_search_tool import web_search_tool

TOOLS = {
    "retriever_tool": {
        "function": retriever_tool,
        "description": "Retrieve relevant FAQ documents.",
    },
    "web_search_tool": {
        "function": web_search_tool,
        "description": "Search the web for relevant information.",
    },
}