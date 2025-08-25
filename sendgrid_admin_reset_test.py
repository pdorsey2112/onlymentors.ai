#!/usr/bin/env python3
"""
SendGrid Admin Password Reset Testing
Tests the newly configured SendGrid email system with admin password reset
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

# Configuration
BACKEND_URL = "https://admin-console-4.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@onlymentors.ai"
ADMIN_PASSWORD = "SuperAdmin2024!"
TEST_USER_EMAIL = "pdorsey@dorseyandassociates.com"
TEST_USER_NAME = "Paul Dorsey"
RESET_REASON = "Testing SendGrid email delivery"

class SendGridAdminResetTester:
    def __init__(self):
        self.session = None
        self.admin_token = None
        self.test_user_id = None
        
    async def setup_session(self):
        """Setup HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
            
    async def admin_login(self):
        """Test admin login"""
        print(f"🔐 Testing admin login with {ADMIN_EMAIL}...")
        
        login_data = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        
        async with self.session.post(f"{BACKEND_URL}/admin/auth/login", json=login_data) as response:
            if response.status == 200:
                data = await response.json()
                self.admin_token = data.get("token")
                print(f"✅ Admin login successful! Token: {self.admin_token[:20]}...")
                return True
            else:
                error_text = await response.text()
                print(f"❌ Admin login failed: {response.status} - {error_text}")
                return False
                
    async def create_test_user(self):
        """Create test user if not exists"""
        print(f"👤 Creating test user {TEST_USER_EMAIL}...")
        
        # First check if user exists
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        async with self.session.get(f"{BACKEND_URL}/admin/users", headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                users = data.get("users", [])
                
                # Look for existing user
                for user in users:
                    if user.get("email") == TEST_USER_EMAIL:
                        self.test_user_id = user.get("user_id")
                        print(f"✅ Test user already exists: {self.test_user_id}")
                        return True
        
        # Create new test user via regular signup
        signup_data = {
            "email": TEST_USER_EMAIL,
            "password": "TempPassword123!",
            "full_name": TEST_USER_NAME
        }
        
        async with self.session.post(f"{BACKEND_URL}/auth/signup", json=signup_data) as response:
            if response.status == 200:
                data = await response.json()
                self.test_user_id = data.get("user", {}).get("user_id")
                print(f"✅ Test user created successfully: {self.test_user_id}")
                return True
            else:
                error_text = await response.text()
                print(f"❌ Failed to create test user: {response.status} - {error_text}")
                return False
                
    async def test_admin_password_reset(self):
        """Test admin-initiated password reset with SendGrid"""
        print(f"📧 Testing admin password reset for {TEST_USER_EMAIL}...")
        
        if not self.test_user_id:
            print("❌ No test user ID available")
            return False
            
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        reset_data = {"reason": RESET_REASON}
        
        async with self.session.post(
            f"{BACKEND_URL}/admin/users/{self.test_user_id}/reset-password", 
            json=reset_data, 
            headers=headers
        ) as response:
            if response.status == 200:
                data = await response.json()
                print(f"✅ Admin password reset initiated successfully!")
                print(f"   📧 Email: {data.get('email')}")
                print(f"   📝 Message: {data.get('message')}")
                print(f"   🔗 Reset Method: {data.get('reset_method')}")
                print(f"   ⏰ Expires In: {data.get('expires_in')}")
                print(f"   📊 Email Status: {data.get('email_status')}")
                print(f"   📋 Note: {data.get('note')}")
                
                # Check if SendGrid was used successfully
                email_status = data.get('email_status')
                if email_status == 'sent':
                    print(f"🎉 SUCCESS: Email status is 'sent' - SendGrid delivery confirmed!")
                    return True
                elif email_status == 'pending':
                    print(f"⚠️  WARNING: Email status is 'pending' - may have fallen back to console logging")
                    return False
                else:
                    print(f"❌ UNEXPECTED: Email status is '{email_status}'")
                    return False
            else:
                error_text = await response.text()
                print(f"❌ Admin password reset failed: {response.status} - {error_text}")
                return False
                
    async def verify_account_locked(self):
        """Verify that the user account is locked after reset"""
        print(f"🔒 Verifying account lock for {TEST_USER_EMAIL}...")
        
        # Try to login with old password
        login_data = {
            "email": TEST_USER_EMAIL,
            "password": "TempPassword123!"
        }
        
        async with self.session.post(f"{BACKEND_URL}/auth/login", json=login_data) as response:
            if response.status == 423:  # HTTP 423 Locked
                data = await response.json()
                print(f"✅ Account correctly locked! Status: {response.status}")
                print(f"   📝 Message: {data.get('detail')}")
                return True
            elif response.status == 401:
                print(f"✅ Account locked (401 Unauthorized - expected)")
                return True
            else:
                error_text = await response.text()
                print(f"❌ Unexpected login response: {response.status} - {error_text}")
                return False
                
    async def check_sendgrid_configuration(self):
        """Check SendGrid configuration"""
        print(f"⚙️  Checking SendGrid configuration...")
        
        # Check environment variables
        sendgrid_key = os.getenv("SENDGRID_API_KEY")
        from_email = os.getenv("FROM_EMAIL")
        
        if sendgrid_key:
            print(f"✅ SENDGRID_API_KEY found: {sendgrid_key[:20]}...")
            if sendgrid_key == "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":
                print(f"✅ SendGrid API key matches expected value")
            else:
                print(f"⚠️  SendGrid API key differs from expected")
        else:
            print(f"❌ SENDGRID_API_KEY not found in environment")
            
        if from_email:
            print(f"✅ FROM_EMAIL found: {from_email}")
            if from_email == "noreply@onlymentors.ai":
                print(f"✅ From email matches expected value")
            else:
                print(f"⚠️  From email differs from expected")
        else:
            print(f"❌ FROM_EMAIL not found in environment")
            
        return bool(sendgrid_key and from_email)
        
    async def run_comprehensive_test(self):
        """Run comprehensive SendGrid admin reset test"""
        print("=" * 80)
        print("🧪 SENDGRID ADMIN PASSWORD RESET COMPREHENSIVE TEST")
        print("=" * 80)
        print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🎯 Target User: {TEST_USER_EMAIL}")
        print(f"📝 Reset Reason: {RESET_REASON}")
        print(f"🔑 Expected API Key: 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")
        print(f"📧 Expected From Email: noreply@onlymentors.ai")
        print("=" * 80)
        
        try:
            await self.setup_session()
            
            # Test 1: Check SendGrid Configuration
            print(f"\n📋 TEST 1: SendGrid Configuration Check")
            config_ok = await self.check_sendgrid_configuration()
            if not config_ok:
                print(f"❌ SendGrid configuration issues detected")
                return False
                
            # Test 2: Admin Login
            print(f"\n📋 TEST 2: Admin Authentication")
            if not await self.admin_login():
                print(f"❌ Admin login failed - cannot proceed")
                return False
                
            # Test 3: Create/Find Test User
            print(f"\n📋 TEST 3: Test User Setup")
            if not await self.create_test_user():
                print(f"❌ Test user setup failed - cannot proceed")
                return False
                
            # Test 4: Admin Password Reset with SendGrid
            print(f"\n📋 TEST 4: Admin Password Reset (SendGrid)")
            reset_success = await self.test_admin_password_reset()
            
            # Test 5: Verify Account Lock
            print(f"\n📋 TEST 5: Account Lock Verification")
            lock_success = await self.verify_account_locked()
            
            # Final Results
            print(f"\n" + "=" * 80)
            print(f"🏁 FINAL TEST RESULTS")
            print(f"=" * 80)
            print(f"✅ Admin Login: PASSED")
            print(f"✅ Test User Setup: PASSED")
            print(f"{'✅' if reset_success else '❌'} SendGrid Email Delivery: {'PASSED' if reset_success else 'FAILED'}")
            print(f"{'✅' if lock_success else '❌'} Account Locking: {'PASSED' if lock_success else 'FAILED'}")
            
            overall_success = reset_success and lock_success
            print(f"\n🎯 OVERALL RESULT: {'✅ SUCCESS' if overall_success else '❌ FAILED'}")
            
            if overall_success:
                print(f"🎉 SendGrid admin password reset system is working correctly!")
                print(f"📧 Email should be delivered to {TEST_USER_EMAIL}")
                print(f"🔒 Account is properly locked until password reset")
            else:
                print(f"⚠️  Issues detected with SendGrid admin password reset system")
                
            print(f"=" * 80)
            return overall_success
            
        except Exception as e:
            print(f"❌ Test execution error: {str(e)}")
            return False
        finally:
            await self.cleanup_session()

async def main():
    """Main test execution"""
    tester = SendGridAdminResetTester()
    success = await tester.run_comprehensive_test()
    
    if success:
        print(f"\n🎊 ALL TESTS PASSED! SendGrid admin password reset is working correctly.")
        exit(0)
    else:
        print(f"\n💥 SOME TESTS FAILED! Please check the SendGrid configuration.")
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())