from tools.rag import retriever_tool
from tools.web_search_tool import web_search_tool

TOOLS = {
    "retriever_tool": {
        "function": retriever_tool,
        "description": "retrieve relevant documents"
    },
    "web_search_tool": {
        "function": web_search_tool,
        "description": "search the web for relevant information"
    }
}