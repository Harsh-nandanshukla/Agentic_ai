
from langgraph.graph import StateGraph, START
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun
from typing import TypedDict, Annotated, List
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.tools import tool
import asyncio

load_dotenv()

# LLM
llm = ChatOpenAI(model="gpt-5")


@tool
def calculator(first_num: float, second_num: float, operation: str) -> dict:
    """
    Perform a basic arithmetic operation on two numbers.
    Supported operations: add, sub, mul, div
    """
    try:
        if operation == "add":
            result = first_num + second_num

        elif operation == "sub":
            result = first_num - second_num

        elif operation == "mul":
            result = first_num * second_num

        elif operation == "div":
            result = first_num / second_num

        else:
            return {"error": f"Unsupported operation '{operation}'"}

        return {
            "first_num": first_num,
            "second_num": second_num,
            "operation": operation,
            "result": result,
        }

    except Exception as e:
        return {"error": str(e)}


tools = [calculator]

# Bind tools to LLM
llm_with_tools = llm.bind_tools(tools)

class ChatState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]


def build_graph():

    async def chat_node(state: ChatState):
        messages = state["messages"]
        response =await llm_with_tools.ainvoke(messages)
        return {"messages": [response]}

    tool_node = ToolNode(tools)

  
    graph = StateGraph(ChatState)

    graph.add_node("chat_node", chat_node)
    graph.add_node("tools", tool_node)

    graph.add_edge(START, "chat_node")

    graph.add_conditional_edges(
        "chat_node",
        tools_condition
    )

    graph.add_edge("tools", "chat_node")

    chatbot = graph.compile()

    return chatbot

async def main():
    chatbot=build_graph()
    result = chatbot.ainvoke({"messages": [HumanMessage(content="Find the modulus of 132354 and 13 and give answer like a cricket commentator.")]})
    print(result["messages"][-1].content)

if __name__ =='__main__':
      asyncio.run(main())  