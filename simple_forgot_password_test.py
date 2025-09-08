#!/usr/bin/env python3
"""
OnlyMentors.ai - Focused Forgot Password System Testing
Tests the core forgot password functionality
"""

import asyncio
import aiohttp
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SimpleForgotPasswordTester:
    def __init__(self):
        # Get backend URL from environment
        self.backend_url = os.getenv("REACT_APP_BACKEND_URL", "https://enterprise-coach.preview.emergentagent.com")
        self.api_base = f"{self.backend_url}/api"
        
        # Test results
        self.results = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "test_details": []
        }

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

    async def make_request(self, method: str, endpoint: str, data: dict = None) -> tuple[int, dict]:
        """Make HTTP request to API"""
        url = f"{self.api_base}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        try:
            async with aiohttp.ClientSession() as session:
                if method.upper() == "POST":
                    async with session.post(url, json=data, headers=headers) as response:
                        try:
                            response_data = await response.json()
                        except:
                            response_data = {"error": "Invalid JSON response"}
                        return response.status, response_data
                elif method.upper() == "GET":
                    async with session.get(url, headers=headers) as response:
                        try:
                            response_data = await response.json()
                        except:
                            response_data = {"error": "Invalid JSON response"}
                        return response.status, response_data
        except Exception as e:
            return 500, {"error": str(e)}

    async def test_forgot_password_endpoints(self):
        """Test forgot password API endpoints"""
        print("\n🔐 Testing Forgot Password API Endpoints...")
        
        # Test 1: Valid user forgot password request
        user_request = {
            "email": "testuser@example.com",
            "user_type": "user"
        }
        
        status, response = await self.make_request("POST", "/auth/forgot-password", user_request)
        if status == 200 and "message" in response:
            await self.log_test("User Forgot Password Request", True, 
                              f"Response: {response.get('message', '')}")
        else:
            await self.log_test("User Forgot Password Request", False, "", 
                              f"Status: {status}, Response: {response}")
        
        # Test 2: Valid mentor forgot password request
        mentor_request = {
            "email": "testmentor@example.com",
            "user_type": "mentor"
        }
        
        status, response = await self.make_request("POST", "/auth/forgot-password", mentor_request)
        if status == 200 and "message" in response:
            await self.log_test("Mentor Forgot Password Request", True, 
                              f"Response: {response.get('message', '')}")
        else:
            await self.log_test("Mentor Forgot Password Request", False, "", 
                              f"Status: {status}, Response: {response}")
        
        # Test 3: Invalid user type
        invalid_request = {
            "email": "test@example.com",
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

    async def test_sendgrid_configuration(self):
        """Test SendGrid configuration"""
        print("\n📧 Testing SendGrid Configuration...")
        
        # Load from backend .env file
        from dotenv import load_dotenv
        load_dotenv('/app/backend/.env')
        
        # Check environment variables
        sendgrid_api_key = os.getenv("SENDGRID_API_KEY")
        from_email = os.getenv("FROM_EMAIL")
        
        if sendgrid_api_key and from_email:
            await self.log_test("SendGrid Configuration", True, 
                              f"API key and from_email configured")
        else:
            await self.log_test("SendGrid Configuration", False, "", 
                              f"Missing SendGrid configuration - API Key: {bool(sendgrid_api_key)}, From Email: {bool(from_email)}")

    async def test_password_reset_endpoints(self):
        """Test password reset endpoints"""
        print("\n🔄 Testing Password Reset Endpoints...")
        
        # Test 1: Invalid token
        reset_request = {
            "token": "invalid_token_123",
            "new_password": "NewPassword123!",
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

    async def test_token_validation_endpoint(self):
        """Test token validation endpoint"""
        print("\n🔑 Testing Token Validation Endpoint...")
        
        # Test with invalid token using query parameters
        url = f"{self.api_base}/auth/validate-reset-token?token=invalid_token&user_type=user"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url) as response:
                    status = response.status
                    try:
                        response_data = await response.json()
                    except:
                        response_data = {"error": "Invalid JSON response"}
        except Exception as e:
            status = 500
            response_data = {"error": str(e)}
        
        if status == 400:
            await self.log_test("Token Validation Endpoint", True, 
                              f"Correctly rejected invalid token")
        else:
            await self.log_test("Token Validation Endpoint", False, "", 
                              f"Should reject invalid token, got status: {status}")

    async def test_security_features(self):
        """Test security features"""
        print("\n🛡️ Testing Security Features...")
        
        # Test password strength validation function
        try:
            import sys
            sys.path.append('/app/backend')
            from forgot_password_system import validate_password_strength
            
            test_passwords = [
                ("weak", False, "Too short"),
                ("weakpassword", False, "No uppercase, numbers, or special chars"),
                ("WeakPassword", False, "No numbers or special chars"),
                ("WeakPassword123", False, "No special chars"),
                ("WeakPassword123!", True, "Strong password")
            ]
            
            for password, should_be_strong, description in test_passwords:
                is_strong, message = validate_password_strength(password)
                
                if is_strong == should_be_strong:
                    await self.log_test(f"Password Strength: {description}", True, 
                                      f"Validation result: {message}")
                else:
                    await self.log_test(f"Password Strength: {description}", False, "", 
                                      f"Expected {should_be_strong}, got {is_strong}: {message}")
        except ImportError as e:
            await self.log_test("Password Strength Function Import", False, "", 
                              f"Could not import validation function: {str(e)}")

    async def run_tests(self):
        """Run all forgot password system tests"""
        print("🧠 OnlyMentors.ai - Focused Forgot Password System Testing")
        print("=" * 70)
        
        # Run test suites
        await self.test_forgot_password_endpoints()
        await self.test_sendgrid_configuration()
        await self.test_password_reset_endpoints()
        await self.test_token_validation_endpoint()
        await self.test_security_features()
        
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
    tester = SimpleForgotPasswordTester()
    results = await tester.run_tests()
    
    # Return appropriate exit code
    if results["failed_tests"] == 0:
        exit(0)
    else:
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())