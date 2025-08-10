#!/usr/bin/env python3
import asyncio
import os
import sys
from emergentintegrations.llm.chat import LlmChat, UserMessage

async def debug_llm():
    """Debug the LLM connection with more details"""
    print("🔍 Debugging LLM connection...")
    
    # Check environment
    api_key = os.getenv("EMERGENT_LLM_KEY", "sk-emergent-281F003Ed3fEf9c052")
    print(f"API Key: {api_key[:20]}...")
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    
    # Check imports
    try:
        import litellm
        print(f"✅ LiteLLM version: {litellm.__version__ if hasattr(litellm, '__version__') else 'unknown'}")
    except ImportError as e:
        print(f"❌ LiteLLM import error: {e}")
    
    # Test connection with debug mode
    try:
        import litellm
        litellm._turn_on_debug()
        
        chat = LlmChat(
            api_key=api_key,
            session_id="debug-session",
            system_message="You are a test assistant."
        ).with_model("openai", "gpt-4o-mini")
        
        user_message = UserMessage(text="Say hello")
        response = await chat.send_message(user_message)
        print(f"✅ Success: {response}")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(debug_llm())