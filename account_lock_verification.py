#!/usr/bin/env python3
"""
Account Locking Verification - Check if user account is properly locked after admin reset
"""

import requests
import json

# Configuration
BACKEND_URL = "https://mentor-search.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@onlymentors.ai"
ADMIN_PASSWORD = "SuperAdmin2024!"
TEST_USER_EMAIL = "pdorsey@dorseyandassociates.com"

def get_admin_token():
    """Get admin authentication token"""
    response = requests.post(f"{BACKEND_URL}/admin/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    
    if response.status_code == 200:
        return response.json().get("token")
    return None

def check_user_status():
    """Check the user's account status directly"""
    admin_token = get_admin_token()
    if not admin_token:
        print("❌ Failed to get admin token")
        return
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Get users list
    users_response = requests.get(f"{BACKEND_URL}/admin/users", headers=headers)
    
    if users_response.status_code != 200:
        print(f"❌ Failed to get users: {users_response.status_code}")
        return
    
    users_data = users_response.json()
    test_user = None
    
    for user in users_data.get("users", []):
        if user.get("email") == TEST_USER_EMAIL:
            test_user = user
            break
    
    if not test_user:
        print(f"❌ Test user {TEST_USER_EMAIL} not found")
        return
    
    print(f"📋 User Status for {TEST_USER_EMAIL}:")
    print(f"   User ID: {test_user.get('user_id')}")
    print(f"   Email: {test_user.get('email')}")
    print(f"   Account Locked: {test_user.get('account_locked', 'Not set')}")
    print(f"   Password Reset By Admin: {test_user.get('password_reset_by_admin', 'Not set')}")
    print(f"   Password Reset Reason: {test_user.get('password_reset_reason', 'Not set')}")
    
    # Test login attempt
    print(f"\n🔐 Testing Login Attempt:")
    login_response = requests.post(f"{BACKEND_URL}/auth/login", json={
        "email": TEST_USER_EMAIL,
        "password": "TestPassword123!"
    })
    
    print(f"   Status Code: {login_response.status_code}")
    print(f"   Response: {login_response.text}")
    
    if login_response.status_code == 423:
        print("✅ Account is properly locked (HTTP 423)")
    elif login_response.status_code == 401:
        response_text = login_response.text.lower()
        if "locked" in response_text:
            print("✅ Account is locked (mentioned in error message)")
        else:
            print("⚠️  Account may not be locked - got 401 but no lock message")
    else:
        print("❌ Account does not appear to be locked")

if __name__ == "__main__":
    check_user_status()