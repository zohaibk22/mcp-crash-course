import asyncio

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_openai import ChatOpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_core.messages import HumanMessage
import json
import time


load_dotenv()

llm = ChatOpenAI()

math_params = StdioServerParameters(
    command="python",
    args=["/Users/zohaibkhan/dev/langchain_mcp/mcp-crash-course/servers/math_server.py"],
)
weather_params = StdioServerParameters(
    command="python",
    args=["/Users/zohaibkhan/dev/langchain_mcp/mcp-crash-course/servers/weather_server.py"],
)

DEBUG_LOG_PATH = "/Users/zohaibkhan/dev/langchain_mcp/mcp-crash-course/.cursor/debug-564d6f.log"


async def main():
    print("Hello from mcp-crash-course!")

    async with stdio_client(math_params) as (math_read, math_write):
        async with ClientSession(math_read, math_write) as math_session:
            await math_session.initialize()
            math_tools = await load_mcp_tools(math_session)

            async with stdio_client(weather_params) as (weather_read, weather_write):
                async with ClientSession(weather_read, weather_write) as weather_session:
                    await weather_session.initialize()
                    weather_tools = await load_mcp_tools(weather_session)

                    all_tools = [*math_tools, *weather_tools]

                    # region agent log
                    pre_invoke_payload = {
                        "sessionId": "564d6f",
                        "runId": "pre-fix",
                        "hypothesisId": "H_session_lifecycle",
                        "location": "main.py:48",
                        "message": "Before agent.ainvoke with open MCP sessions",
                        "data": {"math_tool_count": len(math_tools), "weather_tool_count": len(weather_tools)},
                        "timestamp": int(time.time() * 1000),
                    }
                    with open(DEBUG_LOG_PATH, "a") as f:
                        f.write(json.dumps(pre_invoke_payload) + "\n")
                    # endregion

                    agent = create_agent(llm, all_tools)
                    result = await agent.ainvoke(
                        {"messages": [HumanMessage(content="What is 54 / 2?")]}
                    )

                    # region agent log
                    post_invoke_payload = {
                        "sessionId": "564d6f",
                        "runId": "pre-fix",
                        "hypothesisId": "H_session_lifecycle",
                        "location": "main.py:60",
                        "message": "After agent.ainvoke completed",
                        "data": {},
                        "timestamp": int(time.time() * 1000),
                    }
                    with open(DEBUG_LOG_PATH, "a") as f:
                        f.write(json.dumps(post_invoke_payload) + "\n")
                    # endregion

                    print(result['messages'][-1].content)


if __name__ == "__main__":
    asyncio.run(main())
