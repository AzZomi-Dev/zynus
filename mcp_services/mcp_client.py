import asyncio
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

server_params = StdioServerParameters(
    command="python",
    args=["-m", "mcp_services.mcp_server"]
)

_session: ClientSession | None = None
_exit_stack: AsyncExitStack | None = None
_lock = asyncio.Lock()


async def get_mcp_session() -> ClientSession:
    global _session, _exit_stack

    if _session is not None:
        return _session

    async with _lock:
        if _session is None:
            _exit_stack = AsyncExitStack()
            streams = await _exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            _session = await _exit_stack.enter_async_context(
                ClientSession(*streams)
            )
            await _session.initialize()

        return _session


async def get_available_tools() -> dict:
    session = await get_mcp_session()
    tools = await session.list_tools()
    return {
        tool.name: {"description": tool.description}
        for tool in tools.tools
    }


async def call_mcp_tool(tool_name: str, arguments: dict):
    session = await get_mcp_session()
    return await session.call_tool(tool_name, arguments)