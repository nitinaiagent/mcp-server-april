from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import HumanMessage, BaseMessage
from langgraph.graph.message import add_messages
from langchain_mcp_adapters.client import MultiServerMCPClient
from typing import TypedDict, Annotated
import asyncio
from dotenv import load_dotenv
load_dotenv()

llm = ChatOpenAI(model = "gpt-4o-mini")

class AgentState(TypedDict):
    messages:Annotated[list[BaseMessage], add_messages]
    
async def get_tools():
    client = MultiServerMCPClient(
        {
        "market":{
            "transport":"streamable_http",
            "url":"http://3.110.196.154:8000/mcp"
        }
        }
    )
    
    tools = await client.get_tools()
    
    return tools


async def create_agent():
    tools = await get_tools()
    llm_with_tools = llm.bind_tools(tools)
    
    async def agent_node(state:AgentState):
        response = await llm_with_tools.ainvoke(state["messages"])
        return {"messages":[response]}
        
    builder = StateGraph(AgentState)
    builder.add_node("agent",agent_node)
    builder.add_node("tools", ToolNode(tools))
    
    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", tools_condition)
    builder.add_edge("tools","agent")
    
    graph = builder.compile()
    
    return graph

async def chat_loop():
    agent = await create_agent()
    messages = []
    
    while True:
        query = input("\n What is your query (type 'quit' to exit)").strip()
        
        if query.lower() in ("quit", "exit","q"):
            print("Good Bye")
            break
        
        if not query:
            continue
        
        messages.append(HumanMessage(query))
        result = await agent.ainvoke({"messages":messages})
        
        messages = result["messages"]
        print(messages[-1].content)
        
if __name__=="__main__":
    asyncio.run(chat_loop())
          

