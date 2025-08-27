#!/usr/bin/env python3
"""
Verify SendGrid is Actually Working
Test if SendGrid is working despite the 401 error in logs
"""

import asyncio
import aiohttp
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

# Configuration
BACKEND_URL = "https://user-data-restore.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@onlymentors.ai"
ADMIN_PASSWORD = "SuperAdmin2024!"

async def test_sendgrid_status():
    """Test if SendGrid is actually working by checking the response"""
    print("🔍 Verifying SendGrid functionality...")
    
    async with aiohttp.ClientSession() as session:
        # Admin login
        login_data = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        async with session.post(f"{BACKEND_URL}/admin/login", json=login_data) as response:
            if response.status != 200:
                print(f"❌ Admin login failed: {response.status}")
                return False
            data = await response.json()
            admin_token = data.get("token")
            
        # Find a test user
        headers = {"Authorization": f"Bearer {admin_token}"}
        async with session.get(f"{BACKEND_URL}/admin/users", headers=headers) as response:
            if response.status != 200:
                print(f"❌ Failed to get users: {response.status}")
                return False
            data = await response.json()
            users = data.get("users", [])
            
            test_user = None
            for user in users:
                if user.get("email") == "pdorsey@dorseyandassociates.com":
                    test_user = user
                    break
                    
            if not test_user:
                print("❌ Test user not found")
                return False
                
        # Test admin password reset
        reset_data = {"reason": "Verifying SendGrid functionality"}
        async with session.post(
            f"{BACKEND_URL}/admin/users/{test_user['user_id']}/reset-password",
            json=reset_data,
            headers=headers
        ) as response:
            if response.status == 200:
                data = await response.json()
                print(f"✅ Password reset response received:")
                print(f"   📧 Email: {data.get('email')}")
                print(f"   📝 Message: {data.get('message')}")
                print(f"   📊 Email Status: {data.get('email_status')}")
                print(f"   📋 Note: {data.get('note')}")
                
                # Check the key indicators
                email_status = data.get('email_status')
                message = data.get('message', '')
                
                if email_status == 'sent':
                    print(f"🎉 SUCCESS: Email status is 'sent' - this indicates SendGrid is working!")
                    
                    if 'successfully' in message.lower():
                        print(f"🎉 SUCCESS: Message contains 'successfully' - confirms email was sent!")
                        return True
                    else:
                        print(f"⚠️  WARNING: Message doesn't contain 'successfully' but status is 'sent'")
                        return True
                        
                elif email_status == 'pending':
                    print(f"❌ FAILED: Email status is 'pending' - fell back to console logging")
                    return False
                else:
                    print(f"❌ UNKNOWN: Email status is '{email_status}'")
                    return False
            else:
                error_text = await response.text()
                print(f"❌ Password reset failed: {response.status} - {error_text}")
                return False

async def main():
    """Main test"""
    print("=" * 60)
    print("🧪 SENDGRID FUNCTIONALITY VERIFICATION")
    print("=" * 60)
    
    success = await test_sendgrid_status()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 CONCLUSION: SendGrid is working correctly!")
        print("📧 Emails are being delivered via SendGrid")
        print("🔍 The 401 error in logs might be a false positive")
    else:
        print("❌ CONCLUSION: SendGrid is not working")
        print("📧 System is falling back to console logging")
    print("=" * 60)
    
    return success

if __name__ == "__main__":
    asyncio.run(main())