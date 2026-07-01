def retriever_tool(query):
    return f"retriever_tool is underdevelopment, we can't answer the query: {query}"

def web_search_tool(query):
    return f"web_serach_tool is underdevelopment, we can't answer the query: {query}"

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