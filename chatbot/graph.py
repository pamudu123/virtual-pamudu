from typing import Literal
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

from state import AgentState
from tools import get_medium_article, get_youtube_video_info

# Load environment variables
load_dotenv()

# Initialize the model
model = ChatOpenAI(model="gpt-5-mini-2025-08-07")
tools = [get_medium_article, get_youtube_video_info]
model = model.bind_tools(tools)

# Define nodes
def should_continue(state: AgentState) -> Literal["tools", "__end__"]:
    messages = state['messages']
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return "__end__"

def call_model(state: AgentState):
    messages = state['messages']
    response = model.invoke(messages)
    return {"messages": [response]}

# Build the graph
workflow = StateGraph(AgentState)

workflow.add_node("agent", call_model)
workflow.add_node("tools", ToolNode(tools))

workflow.set_entry_point("agent")

workflow.add_conditional_edges(
    "agent",
    should_continue,
)

workflow.add_edge("tools", "agent")

# Add memory
memory = MemorySaver()

# Compile the graph with memory
app = workflow.compile(checkpointer=memory)
