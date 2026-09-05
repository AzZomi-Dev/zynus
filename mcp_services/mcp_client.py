from mcp import Client, StdioServerParameters
from mcp.client.stdio import stdio_client

server_params = StdioServerParameters(
    command="python",
    args=["-m", "mcp_services.mcp_server"]
)

async def call_mcp_tool(tool_name: str, arguments: str):
    async with Client(stdio_client(server_params)) as client:
        result = await client.call_tool(
            tool_name,
            arguments
        )
        return result