"""
LLM configuration for the chat agent.
"""

import os

from langchain_openai import ChatOpenAI


def get_llm():
    """
    Lazy initialization of the LLM using OpenRouter.
    
    Returns:
        ChatOpenAI instance configured for OpenRouter.
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    return ChatOpenAI(
        model="x-ai/grok-4.1-fast", 
        temperature=0,
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1"
    )
