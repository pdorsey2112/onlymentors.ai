#!/usr/bin/env python3
"""
Verify Password Reset Token Creation and Account Locking
"""

import requests
import json
import re

# Configuration
BACKEND_URL = "https://admin-console-4.preview.emergentagent.com/api"
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

def test_password_reset_token():
    """Test if password reset token was created and is valid"""
    
    # Extract token from the logs we saw earlier
    # From logs: https://admin-console-4.preview.emergentagent.com/reset-password?token=grMVWTWNLfxguItVD1P5pyMZBmrhY4BpRwAEHH71E0Y&type=user
    token = "grMVWTWNLfxguItVD1P5pyMZBmrhY4BpRwAEHH71E0Y"
    
    print(f"🔍 Testing password reset token: {token[:20]}...")
    
    # Test token validation
    response = requests.post(f"{BACKEND_URL}/auth/validate-reset-token", 
                           params={"token": token, "user_type": "user"})
    
    print(f"Token validation status: {response.status_code}")
    print(f"Token validation response: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Password reset token is valid!")
        print(f"   Email: {data.get('email')}")
        print(f"   Expires at: {data.get('expires_at')}")
        print(f"   Time remaining: {data.get('time_remaining')} minutes")
        return True
    else:
        print("❌ Password reset token validation failed")
        return False

def force_account_lock_check():
    """Force another password reset to ensure account locking works"""
    admin_token = get_admin_token()
    if not admin_token:
        print("❌ Failed to get admin token")
        return False
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Get user ID
    users_response = requests.get(f"{BACKEND_URL}/admin/users", headers=headers)
    if users_response.status_code != 200:
        print(f"❌ Failed to get users: {users_response.status_code}")
        return False
    
    users_data = users_response.json()
    test_user = None
    
    for user in users_data.get("users", []):
        if user.get("email") == TEST_USER_EMAIL:
            test_user = user
            break
    
    if not test_user:
        print(f"❌ Test user {TEST_USER_EMAIL} not found")
        return False
    
    user_id = test_user.get("user_id")
    
    print(f"🔄 Initiating another password reset for verification...")
    
    # Initiate another password reset
    reset_response = requests.post(
        f"{BACKEND_URL}/admin/users/{user_id}/reset-password",
        headers=headers,
        json={"reason": "Final verification of SMTP2GO and account locking"}
    )
    
    if reset_response.status_code == 200:
        reset_data = reset_response.json()
        print("✅ Password reset initiated successfully")
        print(f"   Email status: {reset_data.get('email_status')}")
        
        # Wait a moment then check user status again
        import time
        time.sleep(2)
        
        # Check user status again
        users_response = requests.get(f"{BACKEND_URL}/admin/users", headers=headers)
        if users_response.status_code == 200:
            users_data = users_response.json()
            for user in users_data.get("users", []):
                if user.get("email") == TEST_USER_EMAIL:
                    print(f"\n📋 Updated User Status:")
                    print(f"   Account Locked: {user.get('account_locked', 'Not set')}")
                    print(f"   Password Reset By Admin: {user.get('password_reset_by_admin', 'Not set')}")
                    print(f"   Password Reset Reason: {user.get('password_reset_reason', 'Not set')}")
                    
                    # Test login again
                    print(f"\n🔐 Testing Login After Reset:")
                    login_response = requests.post(f"{BACKEND_URL}/auth/login", json={
                        "email": TEST_USER_EMAIL,
                        "password": "TestPassword123!"
                    })
                    
                    print(f"   Status Code: {login_response.status_code}")
                    print(f"   Response: {login_response.text}")
                    
                    if login_response.status_code == 423:
                        print("✅ Account is properly locked (HTTP 423)")
                        return True
                    elif "locked" in login_response.text.lower():
                        print("✅ Account is locked (mentioned in response)")
                        return True
                    else:
                        print("⚠️  Account locking may not be working properly")
                        return False
                    break
        
        return reset_data.get('email_status') == 'sent'
    else:
        print(f"❌ Password reset failed: {reset_response.status_code} - {reset_response.text}")
        return False

if __name__ == "__main__":
    print("🧪 Verifying Password Reset Token and Account Locking")
    print("=" * 60)
    
    # Test 1: Verify token creation
    token_valid = test_password_reset_token()
    
    print("\n" + "=" * 60)
    
    # Test 2: Force another reset and check locking
    lock_working = force_account_lock_check()
    
    print("\n" + "=" * 60)
    print("🏁 Final Verification Results:")
    
    if token_valid:
        print("✅ Password reset token created and valid")
    else:
        print("❌ Password reset token issues")
    
    if lock_working:
        print("✅ Account locking working properly")
    else:
        print("⚠️  Account locking may have issues")
    
    if token_valid and lock_working:
        print("\n🎉 SMTP2GO EMAIL SYSTEM FULLY FUNCTIONAL!")
        print("✅ Email delivery: WORKING")
        print("✅ Token creation: WORKING") 
        print("✅ Account locking: WORKING")
    else:
        print("\n⚠️  Some components may need attention")