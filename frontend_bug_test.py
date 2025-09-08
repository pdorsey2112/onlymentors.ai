#!/usr/bin/env python3
"""
Test Frontend Bug - Missing user_id in request body
This reproduces the exact issue from the frontend code
"""

import requests
import json

def test_frontend_bug():
    base_url = "https://enterprise-coach.preview.emergentagent.com"
    
    # Get admin token
    login_response = requests.post(f"{base_url}/api/admin/login", json={
        "email": "admin@onlymentors.ai",
        "password": "SuperAdmin2024!"
    })
    
    if login_response.status_code != 200:
        print("❌ Admin login failed")
        return
    
    admin_token = login_response.json()["token"]
    print("✅ Admin login successful")
    
    # Find testuser1@test.com
    users_response = requests.get(f"{base_url}/api/admin/users", headers={
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    })
    
    testuser1 = None
    for user in users_response.json()["users"]:
        if user["email"] == "testuser1@test.com":
            testuser1 = user
            break
    
    if not testuser1:
        print("❌ testuser1@test.com not found")
        return
    
    user_id = testuser1["user_id"]
    print(f"✅ Found testuser1@test.com (ID: {user_id})")
    
    print("\n🐛 Testing Frontend Bug - Missing user_id in request body")
    
    # This is exactly what the frontend sends (missing user_id in body)
    frontend_request_data = {
        "suspend": True,
        "reason": "Policy violation"
    }
    
    print(f"Frontend sends: {json.dumps(frontend_request_data, indent=2)}")
    print(f"To endpoint: PUT /api/admin/users/{user_id}/suspend")
    
    try:
        response = requests.put(
            f"{base_url}/api/admin/users/{user_id}/suspend",
            json=frontend_request_data,
            headers={
                "Authorization": f"Bearer {admin_token}",
                "Content-Type": "application/json"
            },
            timeout=30
        )
        
        print(f"\n📊 Response Status: {response.status_code}")
        
        if response.status_code == 422:
            print("🎯 FOUND THE BUG! 422 Unprocessable Entity")
            error_data = response.json()
            print(f"Error details: {json.dumps(error_data, indent=2)}")
            
            # Check if this could cause "[object Object]" in frontend
            if "detail" in error_data and isinstance(error_data["detail"], list):
                print("\n🔍 This 422 error could cause '[object Object]' if frontend doesn't handle it properly")
                print("The frontend might be trying to display the error object directly")
                
        elif response.status_code == 200:
            print("✅ Request succeeded (unexpected)")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"❓ Unexpected status: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    print("\n🔧 Testing Correct Request (with user_id in body)")
    
    # This is what the backend expects
    correct_request_data = {
        "user_id": user_id,
        "suspend": True,
        "reason": "Policy violation"
    }
    
    print(f"Correct request: {json.dumps(correct_request_data, indent=2)}")
    
    try:
        response = requests.put(
            f"{base_url}/api/admin/users/{user_id}/suspend",
            json=correct_request_data,
            headers={
                "Authorization": f"Bearer {admin_token}",
                "Content-Type": "application/json"
            },
            timeout=30
        )
        
        print(f"\n📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Correct request succeeded")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"❌ Correct request failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Correct request failed: {e}")

if __name__ == "__main__":
    test_frontend_bug()