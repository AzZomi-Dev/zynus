from mcp.server.mcpserver import MCPServer
from tools.web_search_tool import web_search_tool
from tools.rag_tool import retriever_tool

mcp = MCPServer("Zynus Tools")

@mcp.tool()
def web_search(query: str):
    """Search the web for up-to-date information"""
    return web_search_tool(query)

@mcp.tool()
def retriever(query: str):
    """Retrieve information from the knowledge base"""
    return retriever_tool(query, my_collection="faq")

if __name__ == "__main__":
    mcp.run("stdio")