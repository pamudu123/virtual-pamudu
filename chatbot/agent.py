import os
from typing import Annotated, Literal, TypedDict, List
import operator

from langchain_core.tools import tool
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from curl_cffi import requests
from newspaper import Article
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Define the tools

MEDIUM_ARTICLES = {
    "LLMs in Practice": "https://medium.com/@pamudu1111/llms-in-practice-how-i-choose-the-right-model-f87a49f2b861",
    "Automated Election Vote Counting": "https://medium.com/@pamudu1111/automated-election-vote-counting-7b89900f7333",
    "Guess The Country": "https://medium.com/@pamudu1111/guess-the-country-4b983ff36616"
}

YOUTUBE_VIDEOS = {
    "Hybrid Transformers for Music Source Separation": "https://www.youtube.com/watch?v=OWMBehI2mLY&t=683s",
    "Hierarchical Attention Networks for Document Classification": "https://www.youtube.com/watch?v=JfgFRSjEucE&t=3s",
    "Fashion Trend Analyzer": "https://www.youtube.com/watch?v=obiv7TysnTQ"
}

@tool
def get_medium_article(topic: str) -> str:
    """
    Retrieves the content of a Medium article based on the topic.
    Available topics:
    - "LLMs in Practice"
    - "Automated Election Vote Counting"
    - "Guess The Country"
    """
    # Fuzzy matching
    url = None
    for key, link in MEDIUM_ARTICLES.items():
        if topic.lower() in key.lower():
            url = link
            break
    
    if not url:
        return f"Article not found for topic: {topic}. Available topics: {list(MEDIUM_ARTICLES.keys())}"

    try:
        # This bypasses the TLS Fingerprint check
        response = requests.get(url, impersonate="chrome")

        if response.status_code == 200:
            article = Article(url)
            article.download_state = 2 # Skip download, we already have the HTML
            article.set_html(response.text)
            article.parse()
            
            return f"Title: {article.title}\n\n{article.text}"
        else:
            return f"Failed to fetch article. Status code: {response.status_code}"

    except Exception as e:
        return f"Error fetching article: {e}"

@tool
def get_youtube_video_info(topic: str) -> str:
    """
    Retrieves the YouTube video link based on the topic.
    Available topics:
    - "Hybrid Transformers for Music Source Separation"
    - "Hierarchical Attention Networks for Document Classification"
    - "Fashion Trend Analyzer"
    """
    url = None
    for key, link in YOUTUBE_VIDEOS.items():
        if topic.lower() in key.lower():
            url = link
            break
            
    if not url:
        return f"Video not found for topic: {topic}. Available topics: {list(YOUTUBE_VIDEOS.keys())}"
    
    return f"Here is the video for '{topic}': {url}"

# Define the graph state
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]

# Initialize the model
# Ensure OPENAI_API_KEY is set in .env
model = ChatOpenAI(model="gpt-5.1-mini")
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

app = workflow.compile()

if __name__ == "__main__":
    # Example usage
    print("Starting Chatbot Agent...")
    while True:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            break
        
        inputs = {"messages": [HumanMessage(content=user_input)]}
        for output in app.stream(inputs):
            for key, value in output.items():
                print(f"Output from node '{key}':")
                print("---")
                # print(value)
                if 'messages' in value:
                    print(value['messages'][-1].content)
                print("\n---\n")
