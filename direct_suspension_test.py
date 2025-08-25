#!/usr/bin/env python3
"""
Direct User Suspension Test
Focus: Test the exact scenario from the review request
"""

import requests
import json
import sys
from datetime import datetime

def test_user_suspension():
    base_url = "https://admin-console-4.preview.emergentagent.com"
    
    print("🔐 Step 1: Admin Login")
    login_response = requests.post(f"{base_url}/api/admin/login", json={
        "email": "admin@onlymentors.ai",
        "password": "SuperAdmin2024!"
    })
    
    if login_response.status_code != 200:
        print(f"❌ Admin login failed: {login_response.status_code}")
        print(f"Response: {login_response.text}")
        return
    
    admin_token = login_response.json()["token"]
    print("✅ Admin login successful")
    
    print("\n👤 Step 2: Find testuser1@test.com")
    users_response = requests.get(f"{base_url}/api/admin/users", headers={
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    })
    
    if users_response.status_code != 200:
        print(f"❌ Failed to get users: {users_response.status_code}")
        return
    
    users_data = users_response.json()
    testuser1 = None
    
    for user in users_data["users"]:
        if user["email"] == "testuser1@test.com":
            testuser1 = user
            break
    
    if not testuser1:
        print("❌ testuser1@test.com not found")
        return
    
    print(f"✅ Found testuser1@test.com (ID: {testuser1['user_id']})")
    print(f"   Current status: {testuser1.get('status', 'unknown')}")
    print(f"   Is suspended: {testuser1.get('is_suspended', False)}")
    
    print("\n🚫 Step 3: Test User Suspension Endpoint")
    suspension_data = {
        "user_id": testuser1["user_id"],
        "reason": "Policy violation",
        "suspend": True
    }
    
    print(f"Making PUT request to: {base_url}/api/admin/users/{testuser1['user_id']}/suspend")
    print(f"Request data: {json.dumps(suspension_data, indent=2)}")
    
    try:
        suspension_response = requests.put(
            f"{base_url}/api/admin/users/{testuser1['user_id']}/suspend",
            json=suspension_data,
            headers={
                "Authorization": f"Bearer {admin_token}",
                "Content-Type": "application/json"
            },
            timeout=30
        )
        
        print(f"\n📊 Response Status: {suspension_response.status_code}")
        print(f"Response Headers: {dict(suspension_response.headers)}")
        
        # Try to parse as JSON
        try:
            response_json = suspension_response.json()
            print(f"Response JSON: {json.dumps(response_json, indent=2)}")
        except Exception as e:
            print(f"❌ Failed to parse JSON: {e}")
            print(f"Raw response text: {suspension_response.text}")
            
            # Check if this is the "[object Object]" issue
            if "[object Object]" in suspension_response.text:
                print("🎯 FOUND THE ISSUE: Response contains '[object Object]'")
                print("This suggests the backend is returning a JavaScript object instead of JSON")
            
        if suspension_response.status_code == 200:
            print("✅ Suspension endpoint returned 200 OK")
        else:
            print(f"❌ Suspension endpoint failed with status {suspension_response.status_code}")
            
    except Exception as e:
        print(f"❌ Request failed with exception: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
    
    print("\n🔍 Step 4: Verify User Status After Suspension")
    try:
        verify_response = requests.get(f"{base_url}/api/admin/users", headers={
            "Authorization": f"Bearer {admin_token}",
            "Content-Type": "application/json"
        })
        
        if verify_response.status_code == 200:
            users_data = verify_response.json()
            for user in users_data["users"]:
                if user["email"] == "testuser1@test.com":
                    print(f"✅ User status after suspension:")
                    print(f"   Status: {user.get('status', 'unknown')}")
                    print(f"   Is suspended: {user.get('is_suspended', False)}")
                    print(f"   Suspension reason: {user.get('suspension_reason', 'None')}")
                    print(f"   Suspended by: {user.get('suspended_by', 'None')}")
                    break
        else:
            print(f"❌ Failed to verify user status: {verify_response.status_code}")
            
    except Exception as e:
        print(f"❌ Verification failed: {e}")

if __name__ == "__main__":
    test_user_suspension()