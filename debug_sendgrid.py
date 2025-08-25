#!/usr/bin/env python3
"""
Debug SendGrid API Key
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

def debug_sendgrid():
    """Debug SendGrid API key"""
    print("🔍 Debugging SendGrid API key...")
    
    api_key = os.getenv("SENDGRID_API_KEY")
    print(f"🔑 Full API Key: {api_key}")
    
    if not api_key:
        print("❌ No API key found")
        return
        
    # Test with simple API call
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Try to get API key info
    try:
        print("📡 Testing API key with SendGrid API...")
        response = requests.get("https://api.sendgrid.com/v3/user/profile", headers=headers)
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ API key is valid!")
        elif response.status_code == 401:
            print("❌ API key is invalid or expired")
        else:
            print(f"⚠️  Unexpected response: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing API key: {str(e)}")

if __name__ == "__main__":
    debug_sendgrid()