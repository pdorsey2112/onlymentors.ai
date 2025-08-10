#!/usr/bin/env python3
import asyncio
import os
from emergentintegrations.llm.chat import LlmChat, UserMessage

async def test_llm_connection():
    """Test the LLM API connection directly"""
    print("🔍 Testing LLM API connection...")
    
    # Get API key from environment
    api_key = os.getenv("EMERGENT_LLM_KEY", "sk-emergent-281F003Ed3fEf9c052")
    print(f"Using API key: {api_key[:20]}...")
    
    try:
        # Create a simple chat session
        chat = LlmChat(
            api_key=api_key,
            session_id="test-session",
            system_message="You are Warren Buffett. Respond in character."
        ).with_model("openai", "gpt-4o-mini")
        
        # Test message
        user_message = UserMessage(
            text="What's your best investment advice?"
        )
        
        print("📤 Sending test message...")
        response = await chat.send_message(user_message)
        print(f"✅ Success! Response: {response[:200]}...")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print(f"Error type: {type(e)}")
        return False

if __name__ == "__main__":
    asyncio.run(test_llm_connection())