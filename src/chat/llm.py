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
        model="openai/gpt-oss-120b", 
        temperature=0,
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
        extra_body={
            "provider": {
                "order": ["DeepInfra"],
                "allow_fallbacks": True
            }
        }
    )
