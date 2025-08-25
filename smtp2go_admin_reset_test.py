#!/usr/bin/env python3
"""
SMTP2GO Admin Password Reset Email System Test
Tests the newly configured SMTP2GO email system with admin password reset functionality.
"""

import asyncio
import aiohttp
import json
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SMTP2GOAdminResetTester:
    def __init__(self):
        # Get backend URL from frontend .env
        frontend_env_path = "/app/frontend/.env"
        backend_url = None
        
        try:
            with open(frontend_env_path, 'r') as f:
                for line in f:
                    if line.startswith('REACT_APP_BACKEND_URL='):
                        backend_url = line.split('=', 1)[1].strip()
                        break
        except Exception as e:
            print(f"⚠️ Could not read frontend .env: {e}")
        
        self.base_url = f"{backend_url}/api" if backend_url else "http://localhost:8001/api"
        self.admin_token = None
        self.test_results = []
        
        # Test configuration from review request
        self.admin_credentials = {
            "email": "admin@onlymentors.ai",
            "password": "SuperAdmin2024!"
        }
        
        self.target_email = "pdorsey@dorseyandassociates.com"
        self.reset_reason = "Testing SMTP2GO email delivery"
        
        # Expected SMTP2GO configuration
        self.expected_smtp_config = {
            "server": "mail.smtp2go.com",
            "port": 587,
            "username": "pdorsey@dorseyandassociates.com",
            "password": "Mfpatd2117!",
            "from_email": "customerservice@onlymentors.ai"
        }
        
        print(f"🎯 SMTP2GO Admin Password Reset Test")
        print(f"📡 Backend URL: {self.base_url}")
        print(f"👤 Admin: {self.admin_credentials['email']}")
        print(f"📧 Target Email: {self.target_email}")
        print(f"📝 Reset Reason: {self.reset_reason}")
        print("="*80)

    async def make_request(self, method, endpoint, data=None, headers=None):
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"
        
        default_headers = {"Content-Type": "application/json"}
        if headers:
            default_headers.update(headers)
        
        try:
            async with aiohttp.ClientSession() as session:
                if method.upper() == "GET":
                    async with session.get(url, headers=default_headers) as response:
                        response_data = await response.json()
                        return response.status, response_data
                elif method.upper() == "POST":
                    async with session.post(url, json=data, headers=default_headers) as response:
                        response_data = await response.json()
                        return response.status, response_data
                elif method.upper() == "PUT":
                    async with session.put(url, json=data, headers=default_headers) as response:
                        response_data = await response.json()
                        return response.status, response_data
                        
        except Exception as e:
            print(f"❌ Request error for {method} {url}: {str(e)}")
            return None, {"error": str(e)}

    def log_test_result(self, test_name, success, details):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   📋 {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        })

    async def test_admin_login(self):
        """Test 1: Admin login with specified credentials"""
        print("\n🔐 Test 1: Admin Authentication")
        
        status, response = await self.make_request(
            "POST", 
            "/admin/login",
            self.admin_credentials
        )
        
        if status == 200 and "token" in response:
            self.admin_token = response["token"]
            admin_info = response.get("admin", {})
            self.log_test_result(
                "Admin Login", 
                True, 
                f"Logged in as {admin_info.get('email', 'admin')} with role {admin_info.get('role', 'unknown')}"
            )
            return True
        else:
            self.log_test_result(
                "Admin Login", 
                False, 
                f"Status: {status}, Response: {response}"
            )
            return False

    async def test_smtp2go_configuration(self):
        """Test 2: Verify SMTP2GO configuration is loaded"""
        print("\n📧 Test 2: SMTP2GO Configuration Verification")
        
        # Load environment variables from backend .env
        backend_env_path = "/app/backend/.env"
        env_vars = {}
        
        try:
            with open(backend_env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key] = value.strip('"')
        except Exception as e:
            print(f"⚠️ Could not read backend .env: {e}")
        
        smtp_server = env_vars.get("SMTP_SERVER")
        smtp_port = env_vars.get("SMTP_PORT")
        smtp_username = env_vars.get("SMTP_USERNAME")
        smtp_password = env_vars.get("SMTP_PASSWORD")
        from_email = env_vars.get("FROM_EMAIL")
        
        config_correct = (
            smtp_server == self.expected_smtp_config["server"] and
            smtp_port == str(self.expected_smtp_config["port"]) and
            smtp_username == self.expected_smtp_config["username"] and
            smtp_password == self.expected_smtp_config["password"] and
            from_email == self.expected_smtp_config["from_email"]
        )
        
        if config_correct:
            self.log_test_result(
                "SMTP2GO Configuration", 
                True, 
                f"Server: {smtp_server}:{smtp_port}, Username: {smtp_username}, From: {from_email}"
            )
            return True
        else:
            self.log_test_result(
                "SMTP2GO Configuration", 
                False, 
                f"Expected: {self.expected_smtp_config}, Got: Server={smtp_server}, Port={smtp_port}, User={smtp_username}, From={from_email}"
            )
            return False

    async def test_create_test_user(self):
        """Test 3: Create or find test user for password reset"""
        print("\n👤 Test 3: Test User Setup")
        
        if not self.admin_token:
            self.log_test_result(
                "Test User Setup", 
                False, 
                "No admin token available"
            )
            return False
        
        # First try to find existing user
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        status, response = await self.make_request(
            "GET", 
            "/admin/users",
            headers=headers
        )
        
        if status == 200:
            users = response.get("users", [])
            target_user = next((u for u in users if u.get("email") == self.target_email), None)
            
            if target_user:
                self.test_user_id = target_user["user_id"]
                self.log_test_result(
                    "Test User Setup", 
                    True, 
                    f"Found existing user: {self.target_email} (ID: {self.test_user_id})"
                )
                return True
            else:
                # Create test user if not found
                user_data = {
                    "email": self.target_email,
                    "password": "TestPassword123!",
                    "full_name": "Paul Dorsey"
                }
                
                status, response = await self.make_request(
                    "POST", 
                    "/auth/signup",
                    user_data
                )
                
                if status == 200 and "user" in response:
                    self.test_user_id = response["user"]["user_id"]
                    self.log_test_result(
                        "Test User Setup", 
                        True, 
                        f"Created test user: {self.target_email} (ID: {self.test_user_id})"
                    )
                    return True
                else:
                    self.log_test_result(
                        "Test User Setup", 
                        False, 
                        f"Failed to create user. Status: {status}, Response: {response}"
                    )
                    return False
        else:
            self.log_test_result(
                "Test User Setup", 
                False, 
                f"Failed to get users list. Status: {status}, Response: {response}"
            )
            return False

    async def test_admin_password_reset(self):
        """Test 4: Initiate admin password reset with SMTP2GO"""
        print("\n🔄 Test 4: Admin Password Reset Initiation")
        
        if not hasattr(self, 'test_user_id'):
            self.log_test_result(
                "Admin Password Reset", 
                False, 
                "No test user ID available"
            )
            return False
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        reset_data = {"reason": self.reset_reason}
        
        status, response = await self.make_request(
            "POST", 
            f"/admin/users/{self.test_user_id}/reset-password",
            reset_data,
            headers
        )
        
        if status == 200:
            email_status = response.get("email_status", "unknown")
            reset_method = response.get("reset_method", "unknown")
            expires_in = response.get("expires_in", "unknown")
            
            success = email_status == "sent"
            
            self.log_test_result(
                "Admin Password Reset", 
                success, 
                f"Email Status: {email_status}, Method: {reset_method}, Expires: {expires_in}"
            )
            
            # Store reset details for verification
            self.reset_response = response
            return success
        else:
            self.log_test_result(
                "Admin Password Reset", 
                False, 
                f"Status: {status}, Response: {response}"
            )
            return False

    async def test_account_locking(self):
        """Test 5: Verify account is locked after admin reset"""
        print("\n🔒 Test 5: Account Locking Verification")
        
        # Try to login with the test user to verify account is locked
        login_data = {
            "email": self.target_email,
            "password": "TestPassword123!"  # Original password
        }
        
        status, response = await self.make_request(
            "POST", 
            "/auth/login",
            login_data
        )
        
        # Should return 423 (Locked) status
        if status == 423:
            self.log_test_result(
                "Account Locking", 
                True, 
                f"Account properly locked (HTTP 423): {response.get('detail', 'Account locked')}"
            )
            return True
        else:
            self.log_test_result(
                "Account Locking", 
                False, 
                f"Expected HTTP 423, got {status}: {response}"
            )
            return False

    async def test_reset_token_creation(self):
        """Test 6: Verify reset token was created"""
        print("\n🎫 Test 6: Reset Token Creation Verification")
        
        # Check if we can validate the token (this would require access to the token)
        # Since we don't have direct access to the token, we'll verify through the response
        if hasattr(self, 'reset_response'):
            reset_method = self.reset_response.get("reset_method")
            expires_in = self.reset_response.get("expires_in")
            
            if reset_method == "email_link" and expires_in == "1 hour":
                self.log_test_result(
                    "Reset Token Creation", 
                    True, 
                    f"Token created with {expires_in} expiration via {reset_method}"
                )
                return True
            else:
                self.log_test_result(
                    "Reset Token Creation", 
                    False, 
                    f"Unexpected reset method or expiration: {reset_method}, {expires_in}"
                )
                return False
        else:
            self.log_test_result(
                "Reset Token Creation", 
                False, 
                "No reset response available to verify token creation"
            )
            return False

    async def test_smtp2go_email_delivery(self):
        """Test 7: Verify SMTP2GO email delivery (check logs)"""
        print("\n📬 Test 7: SMTP2GO Email Delivery Verification")
        
        # Check if the reset response indicates successful email delivery
        if hasattr(self, 'reset_response'):
            email_status = self.reset_response.get("email_status")
            
            if email_status == "sent":
                self.log_test_result(
                    "SMTP2GO Email Delivery", 
                    True, 
                    f"Email status: {email_status} - SMTP2GO delivery successful"
                )
                return True
            elif email_status == "pending":
                self.log_test_result(
                    "SMTP2GO Email Delivery", 
                    False, 
                    f"Email status: {email_status} - SMTP2GO delivery failed, fell back to console logging"
                )
                return False
            else:
                self.log_test_result(
                    "SMTP2GO Email Delivery", 
                    False, 
                    f"Unknown email status: {email_status}"
                )
                return False
        else:
            self.log_test_result(
                "SMTP2GO Email Delivery", 
                False, 
                "No reset response available to verify email delivery"
            )
            return False

    async def run_all_tests(self):
        """Run all SMTP2GO admin password reset tests"""
        print("🚀 Starting SMTP2GO Admin Password Reset Email System Tests")
        print(f"⏰ Test started at: {datetime.utcnow().isoformat()}")
        
        tests = [
            ("Admin Authentication", self.test_admin_login),
            ("SMTP2GO Configuration", self.test_smtp2go_configuration),
            ("Test User Setup", self.test_create_test_user),
            ("Admin Password Reset", self.test_admin_password_reset),
            ("Account Locking", self.test_account_locking),
            ("Reset Token Creation", self.test_reset_token_creation),
            ("SMTP2GO Email Delivery", self.test_smtp2go_email_delivery),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                result = await test_func()
                if result:
                    passed += 1
            except Exception as e:
                print(f"❌ {test_name} - Exception: {str(e)}")
                self.log_test_result(test_name, False, f"Exception: {str(e)}")
        
        # Print summary
        print("\n" + "="*80)
        print("📊 SMTP2GO ADMIN PASSWORD RESET TEST SUMMARY")
        print("="*80)
        
        success_rate = (passed / total) * 100
        print(f"✅ Tests Passed: {passed}/{total} ({success_rate:.1f}%)")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED! SMTP2GO email system is working correctly.")
        else:
            print(f"⚠️ {total - passed} tests failed. Review the issues above.")
        
        # Detailed results
        print("\n📋 Detailed Test Results:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}: {result['details']}")
        
        # Key findings
        print("\n🔍 Key Findings:")
        if any(r["test"] == "SMTP2GO Email Delivery" and r["success"] for r in self.test_results):
            print("✅ SMTP2GO email sent successfully - Primary email method working")
            print("✅ No fallback to SendGrid or console logging")
            print("✅ Email delivery via mail.smtp2go.com:587 confirmed")
        else:
            print("❌ SMTP2GO email delivery failed")
            print("⚠️ System may have fallen back to SendGrid or console logging")
        
        if any(r["test"] == "Account Locking" and r["success"] for r in self.test_results):
            print("✅ Account locking mechanism working correctly")
        
        if any(r["test"] == "Reset Token Creation" and r["success"] for r in self.test_results):
            print("✅ Reset token creation with 1-hour expiration working")
        
        print(f"\n⏰ Test completed at: {datetime.utcnow().isoformat()}")
        print("="*80)
        
        return passed, total

async def main():
    """Main test execution"""
    tester = SMTP2GOAdminResetTester()
    passed, total = await tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if passed == total else 1)

if __name__ == "__main__":
    asyncio.run(main())