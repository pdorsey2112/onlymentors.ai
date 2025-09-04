#!/usr/bin/env python3
"""
Debug 422 Errors in User Suspension
Focus: Identify what causes 422 Unprocessable Entity errors
"""

import requests
import json

def test_422_scenarios():
    base_url = "https://multi-tenant-ai.preview.emergentagent.com"
    
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
    
    # Get a test user
    users_response = requests.get(f"{base_url}/api/admin/users", headers={
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    })
    
    test_user = users_response.json()["users"][0]  # Get first user
    user_id = test_user["user_id"]
    
    print(f"Using test user: {test_user['email']} (ID: {user_id})")
    
    # Test scenarios that might cause 422 errors
    test_cases = [
        {
            "name": "Valid request",
            "data": {"user_id": user_id, "reason": "Test", "suspend": True}
        },
        {
            "name": "Missing user_id field",
            "data": {"reason": "Test", "suspend": True}
        },
        {
            "name": "Missing reason field", 
            "data": {"user_id": user_id, "suspend": True}
        },
        {
            "name": "Missing suspend field",
            "data": {"user_id": user_id, "reason": "Test"}
        },
        {
            "name": "Empty reason",
            "data": {"user_id": user_id, "reason": "", "suspend": True}
        },
        {
            "name": "Null reason",
            "data": {"user_id": user_id, "reason": None, "suspend": True}
        },
        {
            "name": "Wrong data type for suspend",
            "data": {"user_id": user_id, "reason": "Test", "suspend": "true"}
        },
        {
            "name": "Extra fields",
            "data": {"user_id": user_id, "reason": "Test", "suspend": True, "extra_field": "value"}
        },
        {
            "name": "Empty request body",
            "data": {}
        },
        {
            "name": "Malformed JSON (will be sent as string)",
            "data": "not json"
        }
    ]
    
    for i, test_case in enumerate(test_cases):
        print(f"\n🔍 Test {i+1}: {test_case['name']}")
        
        try:
            if test_case['name'] == "Malformed JSON (will be sent as string)":
                # Send malformed data
                response = requests.put(
                    f"{base_url}/api/admin/users/{user_id}/suspend",
                    data=test_case['data'],  # Send as string, not JSON
                    headers={
                        "Authorization": f"Bearer {admin_token}",
                        "Content-Type": "application/json"
                    },
                    timeout=10
                )
            else:
                response = requests.put(
                    f"{base_url}/api/admin/users/{user_id}/suspend",
                    json=test_case['data'],
                    headers={
                        "Authorization": f"Bearer {admin_token}",
                        "Content-Type": "application/json"
                    },
                    timeout=10
                )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 422:
                print("   🎯 FOUND 422 ERROR!")
                try:
                    error_detail = response.json()
                    print(f"   Error details: {json.dumps(error_detail, indent=4)}")
                except:
                    print(f"   Raw response: {response.text}")
            elif response.status_code == 200:
                print("   ✅ Request successful")
                try:
                    success_data = response.json()
                    print(f"   Response: {json.dumps(success_data, indent=4)}")
                except:
                    print(f"   Raw response: {response.text}")
            else:
                print(f"   ❓ Unexpected status: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Request failed: {e}")

if __name__ == "__main__":
    test_422_scenarios()