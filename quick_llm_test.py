#!/usr/bin/env python3

import requests
import json
import sys

def test_llm_integration():
    """Quick test of LLM integration"""
    base_url = "https://mentor-marketplace.preview.emergentagent.com"
    
    # First, signup/login to get a token
    print("🔐 Signing up user...")
    signup_data = {
        "email": "quicktest@test.com",
        "password": "password123", 
        "full_name": "Quick Test User"
    }
    
    try:
        response = requests.post(f"{base_url}/api/auth/signup", json=signup_data, timeout=10)
        if response.status_code == 200:
            token = response.json()["token"]
            print("✅ Signup successful")
        else:
            # Try login instead
            login_data = {"email": "quicktest@test.com", "password": "password123"}
            response = requests.post(f"{base_url}/api/auth/login", json=login_data, timeout=10)
            if response.status_code == 200:
                token = response.json()["token"]
                print("✅ Login successful")
            else:
                print(f"❌ Auth failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Auth error: {e}")
        return False
    
    # Test LLM integration
    print("\n🤖 Testing LLM integration...")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    question_data = {
        "category": "business",
        "mentor_ids": ["warren_buffett"],
        "question": "How do I become successful in business?"
    }
    
    try:
        response = requests.post(f"{base_url}/api/questions/ask", json=question_data, headers=headers, timeout=45)
        
        if response.status_code == 200:
            data = response.json()
            if "responses" in data and len(data["responses"]) > 0:
                response_text = data["responses"][0]["response"]
                print(f"✅ LLM Response received ({len(response_text)} chars)")
                print(f"📝 Response: {response_text[:200]}...")
                
                # Check if it's a real LLM response or fallback
                fallback_indicators = [
                    "Thank you for your question about",
                    "Based on my experience in",
                    "While I'd love to provide a detailed response right now"
                ]
                
                is_fallback = any(indicator in response_text for indicator in fallback_indicators)
                if is_fallback:
                    print("⚠️  This appears to be a fallback response, not real LLM")
                    return False
                else:
                    print("✅ This appears to be a real LLM response!")
                    return True
            else:
                print("❌ No responses in data")
                return False
        else:
            print(f"❌ API call failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ LLM test error: {e}")
        return False

if __name__ == "__main__":
    success = test_llm_integration()
    sys.exit(0 if success else 1)