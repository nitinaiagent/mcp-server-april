from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import HumanMessage, BaseMessage
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict, Annotated

from langchain_mcp_adapters.client import MultiServerMCPClient

import asyncio
import sys
import os
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini")


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


# -------------------------------------------------------
# async means this function can pause while waiting
# without blocking the entire Python program.
# -------------------------------------------------------
async def get_tools():

    client = MultiServerMCPClient(
        {
            "airbnb": {
                "command": "npx",
                "args": [
                    "-y",
                    "@openbnb/mcp-server-airbnb",
                    "--ignore-robots-txt"
                ],
                "transport": "stdio"
            },
            "FinanceServer": {
                "transport": "stdio",
                "command": sys.executable,
                "args": [
                    "E:\\Maven-AI-Agent-Mastery\\MCP2026\\mcp-servers\\crypto_stock.py"
                ]
            }
        }
    )

    # -------------------------------------------------------
    # await means:
    #
    # "Pause THIS function until MCP servers return the tools."
    #
    # During this waiting time Python's event loop is free to
    # execute other async tasks.
    # -------------------------------------------------------
    tools = await client.get_tools()

    print(f"Loaded {len(tools)} tools")

    return tools


# -------------------------------------------------------
# async because this function makes an async LLM call
# -------------------------------------------------------
async def create_agent():

    # Load MCP tools ONLY ONCE
    tools = await get_tools()

    llm_with_tools = llm.bind_tools(tools)

    # -------------------------------------------------------
    # Inner Agent Node
    # -------------------------------------------------------
    async def agent_node(state: AgentState):

        # ---------------------------------------------
        # OpenAI API call
        #
        # While GPT is generating a response,
        # Python is NOT blocked.
        #
        # agent_node pauses here.
        # Once OpenAI responds,
        # execution resumes from the next line.
        # ---------------------------------------------
        response = await llm_with_tools.ainvoke(
            state["messages"]
        )

        return {"messages": [response]}

    builder = StateGraph(AgentState)

    builder.add_node("agent", agent_node)
    builder.add_node("tools", ToolNode(tools))

    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", tools_condition)
    builder.add_edge("tools", "agent")

    graph = builder.compile()

    return graph


# -------------------------------------------------------
# Main Search Function
# -------------------------------------------------------
async def search(query: str):

    # ---------------------------------------------
    # Wait until graph is created.
    #
    # If graph creation needs to wait for MCP,
    # this coroutine pauses here.
    # ---------------------------------------------
    agent = await create_agent()

    # ---------------------------------------------
    # Execute the LangGraph asynchronously.
    #
    # During execution:
    #
    # User
    #   ↓
    # LLM
    #   ↓
    # Tool Calls
    #   ↓
    # LLM
    #
    # Every network call can pause without blocking
    # the event loop.
    # ---------------------------------------------
    result = await agent.ainvoke(
        {
            "messages": [HumanMessage(query)]
        }
    )

    response = result["messages"][-1].content

    print("\nAnswer:\n")
    print(response)

    return response


if __name__ == "__main__":

    query = input("What is your query: ")

    # -------------------------------------------------------
    # asyncio.run()
    #
    # Starts Python's Event Loop.
    #
    # Think of it as the manager that runs all async
    # functions.
    #
    # Flow:
    #
    # asyncio.run()
    #      ↓
    # search()
    #      ↓
    # create_agent()
    #      ↓
    # get_tools()
    #      ↓
    # OpenAI
    #      ↓
    # Return Response
    # -------------------------------------------------------
    asyncio.run(search(query))