#!/usr/bin/env python3
"""
OnlyMentors.ai - Comprehensive Forgot Password System Testing
Tests complete password reset lifecycle for both users and mentors
"""

import asyncio
import aiohttp
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ForgotPasswordTester:
    def __init__(self):
        # Get backend URL from environment
        self.backend_url = os.getenv("REACT_APP_BACKEND_URL", "https://onlymentors-debug.preview.emergentagent.com")
        self.api_base = f"{self.backend_url}/api"
        
        # Test data
        self.test_user_email = "testuser.forgotpw@onlymentors.ai"
        self.test_mentor_email = "testmentor.forgotpw@onlymentors.ai"
        self.test_password = "TestPassword123!"
        self.new_password = "NewPassword456@"
        
        # Test results
        self.results = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "test_details": []
        }
        
        # Store tokens and user data for testing
        self.test_user_token = None
        self.test_mentor_token = None
        self.reset_tokens = {}

    async def log_test(self, test_name: str, success: bool, details: str = "", error: str = ""):
        """Log test results"""
        self.results["total_tests"] += 1
        if success:
            self.results["passed_tests"] += 1
            status = "✅ PASS"
        else:
            self.results["failed_tests"] += 1
            status = "❌ FAIL"
        
        self.results["test_details"].append({
            "test": test_name,
            "status": status,
            "details": details,
            "error": error
        })
        
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if error:
            print(f"   Error: {error}")

    async def make_request(self, method: str, endpoint: str, data: Dict = None, headers: Dict = None) -> tuple[int, Dict]:
        """Make HTTP request to API"""
        url = f"{self.api_base}{endpoint}"
        
        default_headers = {"Content-Type": "application/json"}
        if headers:
            default_headers.update(headers)
        
        try:
            async with aiohttp.ClientSession() as session:
                if method.upper() == "GET":
                    async with session.get(url, headers=default_headers) as response:
                        return response.status, await response.json()
                elif method.upper() == "POST":
                    async with session.post(url, json=data, headers=default_headers) as response:
                        return response.status, await response.json()
                elif method.upper() == "PUT":
                    async with session.put(url, json=data, headers=default_headers) as response:
                        return response.status, await response.json()
                elif method.upper() == "DELETE":
                    async with session.delete(url, headers=default_headers) as response:
                        return response.status, await response.json()
        except Exception as e:
            return 500, {"error": str(e)}

    async def setup_test_accounts(self):
        """Create test user and mentor accounts for testing"""
        print("\n🔧 Setting up test accounts...")
        
        # Create test user
        user_data = {
            "email": self.test_user_email,
            "password": self.test_password,
            "full_name": "Test User ForgotPW"
        }
        
        status, response = await self.make_request("POST", "/auth/signup", user_data)
        if status == 200:
            self.test_user_token = response.get("token")
            await self.log_test("Setup Test User Account", True, f"User created: {self.test_user_email}")
        elif status == 400 and "already registered" in response.get("detail", ""):
            # User already exists, try to login
            login_data = {"email": self.test_user_email, "password": self.test_password}
            status, response = await self.make_request("POST", "/auth/login", login_data)
            if status == 200:
                self.test_user_token = response.get("token")
                await self.log_test("Setup Test User Account", True, f"User logged in: {self.test_user_email}")
            else:
                await self.log_test("Setup Test User Account", False, "", f"Login failed: {response}")
        else:
            await self.log_test("Setup Test User Account", False, "", f"Signup failed: {response}")
        
        # Create test mentor account
        mentor_data = {
            "email": self.test_mentor_email,
            "password": self.test_password,
            "full_name": "Test Mentor ForgotPW",
            "account_name": "testmentor_forgotpw",
            "description": "Test mentor for forgot password testing",
            "monthly_price": 29.99,
            "category": "business",
            "expertise_areas": ["testing", "password_reset"]
        }
        
        status, response = await self.make_request("POST", "/creators/signup", mentor_data)
        if status == 200:
            self.test_mentor_token = response.get("token")
            await self.log_test("Setup Test Mentor Account", True, f"Mentor created: {self.test_mentor_email}")
        elif status == 400 and "already registered" in response.get("detail", ""):
            # Mentor already exists, try to login
            login_data = {"email": self.test_mentor_email, "password": self.test_password}
            status, response = await self.make_request("POST", "/creators/login", login_data)
            if status == 200:
                self.test_mentor_token = response.get("token")
                await self.log_test("Setup Test Mentor Account", True, f"Mentor logged in: {self.test_mentor_email}")
            else:
                await self.log_test("Setup Test Mentor Account", False, "", f"Login failed: {response}")
        else:
            await self.log_test("Setup Test Mentor Account", False, "", f"Signup failed: {response}")

    async def test_forgot_password_endpoints(self):
        """Test forgot password API endpoints"""
        print("\n🔐 Testing Forgot Password API Endpoints...")
        
        # Test 1: Valid user forgot password request
        user_request = {
            "email": self.test_user_email,
            "user_type": "user"
        }
        
        status, response = await self.make_request("POST", "/auth/forgot-password", user_request)
        if status == 200:
            await self.log_test("User Forgot Password Request", True, 
                              f"Response: {response.get('message', '')}")
        else:
            await self.log_test("User Forgot Password Request", False, "", 
                              f"Status: {status}, Response: {response}")
        
        # Test 2: Valid mentor forgot password request
        mentor_request = {
            "email": self.test_mentor_email,
            "user_type": "mentor"
        }
        
        status, response = await self.make_request("POST", "/auth/forgot-password", mentor_request)
        if status == 200:
            await self.log_test("Mentor Forgot Password Request", True, 
                              f"Response: {response.get('message', '')}")
        else:
            await self.log_test("Mentor Forgot Password Request", False, "", 
                              f"Status: {status}, Response: {response}")
        
        # Test 3: Invalid user type
        invalid_request = {
            "email": self.test_user_email,
            "user_type": "invalid"
        }
        
        status, response = await self.make_request("POST", "/auth/forgot-password", invalid_request)
        if status == 400:
            await self.log_test("Invalid User Type Validation", True, 
                              f"Correctly rejected invalid user_type")
        else:
            await self.log_test("Invalid User Type Validation", False, "", 
                              f"Should reject invalid user_type, got status: {status}")
        
        # Test 4: Non-existent email (should still return success for security)
        nonexistent_request = {
            "email": "nonexistent@example.com",
            "user_type": "user"
        }
        
        status, response = await self.make_request("POST", "/auth/forgot-password", nonexistent_request)
        if status == 200:
            await self.log_test("Non-existent Email Security", True, 
                              f"Correctly returns success for non-existent email")
        else:
            await self.log_test("Non-existent Email Security", False, "", 
                              f"Should return success for security, got status: {status}")

    async def test_rate_limiting(self):
        """Test rate limiting functionality"""
        print("\n⏱️ Testing Rate Limiting...")
        
        # Make multiple requests quickly to test rate limiting
        test_email = "ratelimit.test@example.com"
        request_data = {
            "email": test_email,
            "user_type": "user"
        }
        
        # Make 4 requests (should hit rate limit on 4th)
        rate_limit_hit = False
        for i in range(4):
            status, response = await self.make_request("POST", "/auth/forgot-password", request_data)
            if status == 429:  # Too Many Requests
                rate_limit_hit = True
                break
            await asyncio.sleep(0.1)  # Small delay between requests
        
        if rate_limit_hit:
            await self.log_test("Rate Limiting", True, 
                              f"Rate limiting activated after multiple requests")
        else:
            await self.log_test("Rate Limiting", False, "", 
                              f"Rate limiting should activate after 3 requests per hour")

    async def test_sendgrid_integration(self):
        """Test SendGrid email integration"""
        print("\n📧 Testing SendGrid Email Integration...")
        
        # Test SendGrid configuration
        sendgrid_api_key = os.getenv("SENDGRID_API_KEY")
        from_email = os.getenv("FROM_EMAIL")
        
        if sendgrid_api_key and from_email:
            await self.log_test("SendGrid Configuration", True, 
                              f"API key and from_email configured")
        else:
            await self.log_test("SendGrid Configuration", False, "", 
                              f"Missing SendGrid configuration")
        
        # Test email sending by making forgot password request
        # (We can't directly test email delivery without access to the inbox)
        test_request = {
            "email": self.test_user_email,
            "user_type": "user"
        }
        
        status, response = await self.make_request("POST", "/auth/forgot-password", test_request)
        if status == 200:
            await self.log_test("Email Sending Integration", True, 
                              f"Forgot password request processed (email should be sent)")
        else:
            await self.log_test("Email Sending Integration", False, "", 
                              f"Failed to process forgot password request: {response}")

    async def test_token_validation(self):
        """Test password reset token validation"""
        print("\n🔑 Testing Token Validation...")
        
        # Test 1: Invalid token - using query parameters
        status, response = await self.make_request("POST", "/auth/validate-reset-token?token=invalid_token_123&user_type=user")
        
        if status == 400:
            await self.log_test("Invalid Token Validation", True, 
                              f"Correctly rejected invalid token")
        else:
            await self.log_test("Invalid Token Validation", False, "", 
                              f"Should reject invalid token, got status: {status}")
        
        # Test 2: Invalid user type - using query parameters
        status, response = await self.make_request("POST", "/auth/validate-reset-token?token=some_token&user_type=invalid")
        
        if status == 400:
            await self.log_test("Token Validation User Type", True, 
                              f"Correctly rejected invalid user_type")
        else:
            await self.log_test("Token Validation User Type", False, "", 
                              f"Should reject invalid user_type, got status: {status}")

    async def test_password_reset_flow(self):
        """Test complete password reset flow"""
        print("\n🔄 Testing Complete Password Reset Flow...")
        
        # Since we can't access the actual email to get the reset token,
        # we'll test the reset password endpoint with various scenarios
        
        # Test 1: Invalid token
        reset_request = {
            "token": "invalid_token_123",
            "new_password": self.new_password,
            "user_type": "user"
        }
        
        status, response = await self.make_request("POST", "/auth/reset-password", reset_request)
        if status == 400:
            await self.log_test("Reset with Invalid Token", True, 
                              f"Correctly rejected invalid token")
        else:
            await self.log_test("Reset with Invalid Token", False, "", 
                              f"Should reject invalid token, got status: {status}")
        
        # Test 2: Weak password
        weak_reset_request = {
            "token": "some_token",
            "new_password": "weak",
            "user_type": "user"
        }
        
        status, response = await self.make_request("POST", "/auth/reset-password", weak_reset_request)
        if status == 400 and "password" in response.get("detail", "").lower():
            await self.log_test("Password Strength Validation", True, 
                              f"Correctly rejected weak password")
        else:
            await self.log_test("Password Strength Validation", False, "", 
                              f"Should reject weak password, got: {response}")
        
        # Test 3: Missing required fields
        incomplete_request = {
            "token": "",
            "new_password": "",
            "user_type": "user"
        }
        
        status, response = await self.make_request("POST", "/auth/reset-password", incomplete_request)
        if status == 400:
            await self.log_test("Required Fields Validation", True, 
                              f"Correctly rejected incomplete request")
        else:
            await self.log_test("Required Fields Validation", False, "", 
                              f"Should reject incomplete request, got status: {status}")

    async def test_security_features(self):
        """Test security features"""
        print("\n🛡️ Testing Security Features...")
        
        # Test password strength validation
        test_passwords = [
            ("weak", False, "Too short"),
            ("weakpassword", False, "No uppercase, numbers, or special chars"),
            ("WeakPassword", False, "No numbers or special chars"),
            ("WeakPassword123", False, "No special chars"),
            ("WeakPassword123!", True, "Strong password")
        ]
        
        for password, should_be_strong, description in test_passwords:
            # Import password validation function
            try:
                from backend.forgot_password_system import validate_password_strength
                is_strong, message = validate_password_strength(password)
                
                if is_strong == should_be_strong:
                    await self.log_test(f"Password Strength: {description}", True, 
                                      f"Validation result: {message}")
                else:
                    await self.log_test(f"Password Strength: {description}", False, "", 
                                      f"Expected {should_be_strong}, got {is_strong}: {message}")
            except ImportError:
                await self.log_test(f"Password Strength: {description}", False, "", 
                                  f"Could not import validation function")

    async def test_database_operations(self):
        """Test database operations"""
        print("\n🗄️ Testing Database Operations...")
        
        # Test that forgot password requests don't break existing authentication
        if self.test_user_token:
            headers = {"Authorization": f"Bearer {self.test_user_token}"}
            status, response = await self.make_request("GET", "/auth/me", headers=headers)
            
            if status == 200:
                await self.log_test("Existing Auth After Reset Request", True, 
                                  f"User authentication still works")
            else:
                await self.log_test("Existing Auth After Reset Request", False, "", 
                                  f"User auth broken after reset request: {response}")
        
        if self.test_mentor_token:
            headers = {"Authorization": f"Bearer {self.test_mentor_token}"}
            # Test mentor-specific endpoint (we'll use creators login as a proxy)
            status, response = await self.make_request("POST", "/creators/login", {
                "email": self.test_mentor_email,
                "password": self.test_password
            })
            
            if status == 200:
                await self.log_test("Existing Mentor Auth After Reset Request", True, 
                                  f"Mentor authentication still works")
            else:
                await self.log_test("Existing Mentor Auth After Reset Request", False, "", 
                                  f"Mentor auth broken after reset request: {response}")

    async def test_integration_with_existing_system(self):
        """Test integration with existing authentication system"""
        print("\n🔗 Testing Integration with Existing System...")
        
        # Test that regular login still works after forgot password requests
        user_login = {
            "email": self.test_user_email,
            "password": self.test_password
        }
        
        status, response = await self.make_request("POST", "/auth/login", user_login)
        if status == 200:
            await self.log_test("User Login After Reset Request", True, 
                              f"Regular user login still functional")
        else:
            await self.log_test("User Login After Reset Request", False, "", 
                              f"User login broken: {response}")
        
        mentor_login = {
            "email": self.test_mentor_email,
            "password": self.test_password
        }
        
        status, response = await self.make_request("POST", "/creators/login", mentor_login)
        if status == 200:
            await self.log_test("Mentor Login After Reset Request", True, 
                              f"Regular mentor login still functional")
        else:
            await self.log_test("Mentor Login After Reset Request", False, "", 
                              f"Mentor login broken: {response}")

    async def run_comprehensive_tests(self):
        """Run all forgot password system tests"""
        print("🧠 OnlyMentors.ai - Comprehensive Forgot Password System Testing")
        print("=" * 70)
        
        # Setup test accounts
        await self.setup_test_accounts()
        
        # Run all test suites
        await self.test_forgot_password_endpoints()
        await self.test_rate_limiting()
        await self.test_sendgrid_integration()
        await self.test_token_validation()
        await self.test_password_reset_flow()
        await self.test_security_features()
        await self.test_database_operations()
        await self.test_integration_with_existing_system()
        
        # Print final results
        print("\n" + "=" * 70)
        print("📊 FORGOT PASSWORD SYSTEM TEST RESULTS")
        print("=" * 70)
        
        success_rate = (self.results["passed_tests"] / self.results["total_tests"]) * 100 if self.results["total_tests"] > 0 else 0
        
        print(f"Total Tests: {self.results['total_tests']}")
        print(f"Passed: {self.results['passed_tests']} ✅")
        print(f"Failed: {self.results['failed_tests']} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("\n🎉 FORGOT PASSWORD SYSTEM IS FUNCTIONAL!")
            if success_rate >= 95:
                print("💯 EXCELLENT - System is production-ready!")
            elif success_rate >= 90:
                print("✨ VERY GOOD - Minor issues may exist")
            else:
                print("👍 GOOD - Some improvements needed")
        else:
            print("\n⚠️ FORGOT PASSWORD SYSTEM NEEDS ATTENTION")
            print("🔧 Multiple issues found that require fixing")
        
        print("\n📋 DETAILED TEST RESULTS:")
        print("-" * 50)
        for test in self.results["test_details"]:
            print(f"{test['status']}: {test['test']}")
            if test["details"]:
                print(f"   📝 {test['details']}")
            if test["error"]:
                print(f"   ❌ {test['error']}")
        
        return self.results

async def main():
    """Main test execution"""
    tester = ForgotPasswordTester()
    results = await tester.run_comprehensive_tests()
    
    # Return appropriate exit code
    if results["failed_tests"] == 0:
        exit(0)
    else:
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())