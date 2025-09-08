#!/usr/bin/env python3

import requests
import json

def test_llm_quality():
    """Test LLM response quality and personality differences"""
    base_url = "https://enterprise-coach.preview.emergentagent.com"
    
    # Login
    login_data = {"email": "test@test.com", "password": "password123"}
    response = requests.post(f"{base_url}/api/auth/login", json=login_data)
    if response.status_code != 200:
        # Try signup
        signup_data = {"email": "test@test.com", "password": "password123", "full_name": "Test User"}
        response = requests.post(f"{base_url}/api/auth/signup", json=signup_data)
    
    token = response.json()["token"]
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Test different mentors with same question
    question = "How do I become successful in business?"
    mentors = ["warren_buffett", "steve_jobs"]
    
    print("🧪 Testing LLM Response Quality and Personality Differences")
    print("=" * 70)
    
    responses = {}
    for mentor in mentors:
        print(f"\n🤖 Testing {mentor}...")
        
        question_data = {
            "category": "business",
            "mentor_ids": [mentor],
            "question": question
        }
        
        response = requests.post(f"{base_url}/api/questions/ask", json=question_data, headers=headers, timeout=45)
        
        if response.status_code == 200:
            data = response.json()
            response_text = data["responses"][0]["response"]
            mentor_name = data["responses"][0]["mentor"]["name"]
            
            responses[mentor] = response_text
            
            print(f"✅ {mentor_name} Response ({len(response_text)} chars):")
            print(f"   {response_text[:150]}...")
            
            # Check for personality indicators
            personality_indicators = {
                "warren_buffett": ["invest", "value", "long-term", "berkshire", "omaha"],
                "steve_jobs": ["design", "innovation", "apple", "think different", "simplicity"]
            }
            
            found_indicators = []
            for indicator in personality_indicators.get(mentor, []):
                if indicator.lower() in response_text.lower():
                    found_indicators.append(indicator)
            
            if found_indicators:
                print(f"   🎯 Personality indicators found: {found_indicators}")
            else:
                print(f"   ⚠️  No specific personality indicators detected")
        else:
            print(f"❌ Failed to get response from {mentor}")
    
    # Compare responses
    if len(responses) >= 2:
        response_texts = list(responses.values())
        similarity = len(set(response_texts))
        
        print(f"\n📊 Response Analysis:")
        print(f"   Unique responses: {similarity}/{len(responses)}")
        print(f"   Average length: {sum(len(r) for r in response_texts) / len(response_texts):.0f} chars")
        
        if similarity == len(responses):
            print("✅ All responses are unique - personalities are working!")
        else:
            print("⚠️  Some responses are identical")
        
        # Check if responses are substantive (not fallback)
        fallback_count = 0
        for response_text in response_texts:
            if "Thank you for your question about" in response_text:
                fallback_count += 1
        
        if fallback_count == 0:
            print("✅ All responses are authentic LLM responses (no fallbacks)")
            return True
        else:
            print(f"❌ {fallback_count} responses are fallbacks")
            return False
    
    return False

if __name__ == "__main__":
    success = test_llm_quality()
    print(f"\n🎯 Final Result: {'✅ LLM INTEGRATION WORKING' if success else '❌ LLM INTEGRATION ISSUES'}")