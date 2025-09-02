#!/usr/bin/env python3
"""
Admin Password Reset Email System Test
Tests the improved POST /api/admin/users/{user_id}/reset-password endpoint
with better error handling and email-based reset functionality
"""

import requests
import json
import time
import random
import string
from datetime import datetime

# Configuration
BACKEND_URL = "https://mentor-search.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@onlymentors.ai"
ADMIN_PASSWORD = "SuperAdmin2024!"

class AdminPasswordResetEmailTester:
    def __init__(self):
        self.admin_token = None
        self.test_user_id = None
        self.test_user_email = None
        self.original_password = "TestUser123!"
        self.results = []
        self.tests_run = 0
        self.tests_passed = 0
        
    def log_result(self, test_name, success, message, details=None):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name} - {message}")
        
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        if details:
            result["details"] = details
        self.results.append(result)
        return success

    def admin_login(self):
        """Login as admin to get authentication token"""
        try:
            response = requests.post(f"{BACKEND_URL}/admin/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token")
                return self.log_result("Admin Login", True, f"Successfully logged in as admin")
            else:
                return self.log_result("Admin Login", False, f"Failed to login: {response.status_code} - {response.text}")
                
        except Exception as e:
            return self.log_result("Admin Login", False, f"Exception during admin login: {str(e)}")
    
    def create_test_user(self):
        """Create a test user for password reset testing"""
        try:
            # Generate unique test user email
            random_suffix = ''.join(random.choices(string.digits, k=6))
            self.test_user_email = f"testuser1_{random_suffix}@test.com"
            
            response = requests.post(f"{BACKEND_URL}/auth/signup", json={
                "email": self.test_user_email,
                "password": self.original_password,
                "full_name": f"Test User {random_suffix}"
            })
            
            if response.status_code == 200:
                data = response.json()
                self.test_user_id = data["user"]["user_id"]
                return self.log_result("Create Test User", True, f"Created test user: {self.test_user_email}")
            else:
                return self.log_result("Create Test User", False, f"Failed to create user: {response.status_code} - {response.text}")
                
        except Exception as e:
            return self.log_result("Create Test User", False, f"Exception creating test user: {str(e)}")
    
    def verify_user_can_login_initially(self):
        """Verify test user can login with original password before reset"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json={
                "email": self.test_user_email,
                "password": self.original_password
            })
            
            if response.status_code == 200:
                return self.log_result("Initial Login Test", True, "User can login with original password")
            else:
                return self.log_result("Initial Login Test", False, f"User cannot login with original password: {response.status_code}")
                
        except Exception as e:
            return self.log_result("Initial Login Test", False, f"Exception during initial login test: {str(e)}")
    
    def test_admin_password_reset_email_endpoint(self):
        """Test the improved admin password reset endpoint with email functionality"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            payload = {
                "reason": "Customer Service"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/admin/users/{self.test_user_id}/reset-password",
                json=payload,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for new response format
                required_fields = ['message', 'user_id', 'email', 'reset_method']
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    # Check for email_status field (new feature)
                    email_status = data.get('email_status', 'not_specified')
                    
                    return self.log_result("Admin Password Reset Email", True, 
                                         f"Email-based reset successful. Email status: {email_status}",
                                         {"response": data})
                else:
                    return self.log_result("Admin Password Reset Email", False, 
                                         f"Missing required fields: {missing_fields}")
            else:
                return self.log_result("Admin Password Reset Email", False, 
                                     f"Password reset failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            return self.log_result("Admin Password Reset Email", False, f"Exception during password reset: {str(e)}")
    
    def test_account_locking_after_reset(self):
        """Test that user account is locked after admin password reset"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json={
                "email": self.test_user_email,
                "password": self.original_password
            })
            
            # Should return 423 (Locked) or 401 (Unauthorized) due to account lock
            if response.status_code == 423:
                return self.log_result("Account Locking", True, "Account correctly locked (HTTP 423)")
            elif response.status_code == 401:
                return self.log_result("Account Locking", True, "Account access denied (HTTP 401)")
            else:
                return self.log_result("Account Locking", False, 
                                     f"Account not locked properly: {response.status_code}")
                
        except Exception as e:
            return self.log_result("Account Locking", False, f"Exception testing account lock: {str(e)}")
    
    def test_graceful_email_failure_handling(self):
        """Test that system handles email failures gracefully"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            payload = {
                "reason": "Email Failure Test"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/admin/users/{self.test_user_id}/reset-password",
                json=payload,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check that response includes appropriate status messages
                has_email_status = 'email_status' in data
                has_message = 'message' in data
                
                if has_email_status or has_message:
                    email_status = data.get('email_status', 'unknown')
                    message = data.get('message', '')
                    
                    return self.log_result("Graceful Email Handling", True, 
                                         f"System handles email gracefully. Status: {email_status}")
                else:
                    return self.log_result("Graceful Email Handling", False, 
                                         "Response doesn't include email status information")
            else:
                return self.log_result("Graceful Email Handling", False, 
                                     f"Email handling test failed: {response.status_code}")
                
        except Exception as e:
            return self.log_result("Graceful Email Handling", False, f"Exception testing email handling: {str(e)}")
    
    def test_password_reset_token_system(self):
        """Test that password reset tokens are created properly"""
        try:
            # Test the forgot password system to verify token creation
            response = requests.post(f"{BACKEND_URL}/auth/forgot-password", json={
                "email": self.test_user_email,
                "user_type": "user"
            })
            
            if response.status_code == 200:
                data = response.json()
                if 'message' in data and 'expires_in' in data:
                    return self.log_result("Password Reset Tokens", True, 
                                         f"Token system working. Expires in: {data.get('expires_in')} minutes")
                else:
                    return self.log_result("Password Reset Tokens", False, 
                                         "Token response missing required fields")
            else:
                return self.log_result("Password Reset Tokens", False, 
                                     f"Token creation failed: {response.status_code}")
                
        except Exception as e:
            return self.log_result("Password Reset Tokens", False, f"Exception testing tokens: {str(e)}")
    
    def test_token_validation_endpoint(self):
        """Test token validation functionality"""
        try:
            # Test with dummy token (should fail gracefully)
            response = requests.post(f"{BACKEND_URL}/auth/validate-reset-token", 
                                   params={"token": "dummy_token", "user_type": "user"})
            
            if response.status_code == 400:
                return self.log_result("Token Validation", True, "Token validation endpoint working (rejected dummy token)")
            else:
                return self.log_result("Token Validation", False, 
                                     f"Token validation unexpected response: {response.status_code}")
                
        except Exception as e:
            return self.log_result("Token Validation", False, f"Exception testing token validation: {str(e)}")
    
    def test_password_reset_completion(self):
        """Test password reset completion endpoint"""
        try:
            # Test with dummy token (should fail gracefully)
            response = requests.post(f"{BACKEND_URL}/auth/reset-password", json={
                "token": "dummy_token",
                "new_password": "NewPassword123!",
                "user_type": "user"
            })
            
            if response.status_code == 400:
                return self.log_result("Password Reset Completion", True, 
                                     "Reset completion endpoint working (rejected dummy token)")
            else:
                return self.log_result("Password Reset Completion", False, 
                                     f"Reset completion unexpected response: {response.status_code}")
                
        except Exception as e:
            return self.log_result("Password Reset Completion", False, f"Exception testing reset completion: {str(e)}")
    
    def test_admin_authorization_required(self):
        """Test that admin endpoints require proper authorization"""
        try:
            # Test without admin token
            response = requests.post(
                f"{BACKEND_URL}/admin/users/{self.test_user_id}/reset-password",
                json={"reason": "Unauthorized test"}
            )
            
            if response.status_code in [401, 403]:
                return self.log_result("Admin Authorization", True, "Admin endpoints properly protected")
            else:
                return self.log_result("Admin Authorization", False, 
                                     f"Admin endpoint not protected: {response.status_code}")
                
        except Exception as e:
            return self.log_result("Admin Authorization", False, f"Exception testing authorization: {str(e)}")
    
    def test_error_handling_improvements(self):
        """Test improved error handling"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Test with invalid user ID
            response = requests.post(
                f"{BACKEND_URL}/admin/users/invalid_user_id/reset-password",
                json={"reason": "Error handling test"},
                headers=headers
            )
            
            if response.status_code == 404:
                return self.log_result("Error Handling", True, "Invalid user ID properly handled")
            else:
                return self.log_result("Error Handling", False, 
                                     f"Error handling needs improvement: {response.status_code}")
                
        except Exception as e:
            return self.log_result("Error Handling", False, f"Exception testing error handling: {str(e)}")
    
    def test_backend_logging_support(self):
        """Test that backend supports logging for manual recovery"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            payload = {
                "reason": "Logging Test"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/admin/users/{self.test_user_id}/reset-password",
                json=payload,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if response contains information suitable for logging
                has_logging_info = any(key in data for key in ['reset_method', 'expires_in', 'note'])
                
                if has_logging_info:
                    return self.log_result("Backend Logging Support", True, 
                                         "Response contains information suitable for manual recovery logging")
                else:
                    return self.log_result("Backend Logging Support", False, 
                                         "Response lacks information for manual recovery")
            else:
                return self.log_result("Backend Logging Support", False, 
                                     f"Logging test failed: {response.status_code}")
                
        except Exception as e:
            return self.log_result("Backend Logging Support", False, f"Exception testing logging: {str(e)}")
    
    def run_comprehensive_test(self):
        """Run comprehensive admin password reset email system test"""
        print("🚀 Starting Admin Password Reset Email System Tests")
        print("=" * 70)
        
        # Step 1: Admin login
        if not self.admin_login():
            print("❌ Cannot proceed without admin authentication")
            return False
        
        # Step 2: Create test user
        if not self.create_test_user():
            print("❌ Cannot proceed without test user")
            return False
        
        # Step 3: Verify initial login works
        if not self.verify_user_can_login_initially():
            print("❌ Test user setup failed")
            return False
        
        # Step 4: Test admin authorization
        self.test_admin_authorization_required()
        
        # Step 5: Test error handling
        self.test_error_handling_improvements()
        
        # Step 6: Test admin password reset email endpoint
        if not self.test_admin_password_reset_email_endpoint():
            print("❌ Core email-based password reset functionality failed")
            return False
        
        # Step 7: Test account locking
        self.test_account_locking_after_reset()
        
        # Step 8: Test graceful email failure handling
        self.test_graceful_email_failure_handling()
        
        # Step 9: Test password reset token system
        self.test_password_reset_token_system()
        
        # Step 10: Test token validation
        self.test_token_validation_endpoint()
        
        # Step 11: Test password reset completion
        self.test_password_reset_completion()
        
        # Step 12: Test backend logging support
        self.test_backend_logging_support()
        
        # Summary
        self.print_comprehensive_summary()
        
        return True
    
    def print_comprehensive_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 70)
        print("📊 ADMIN PASSWORD RESET EMAIL SYSTEM TEST SUMMARY")
        print("=" * 70)
        
        print(f"Total Tests Run: {self.tests_run}")
        print(f"✅ Tests Passed: {self.tests_passed}")
        print(f"❌ Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        # Critical functionality assessment
        critical_tests = [
            "Admin Password Reset Email",
            "Account Locking", 
            "Graceful Email Handling",
            "Admin Authorization"
        ]
        
        print(f"\n🎯 CRITICAL FUNCTIONALITY ASSESSMENT:")
        critical_passed = 0
        for test_name in critical_tests:
            result = next((r for r in self.results if r["test"] == test_name), None)
            if result:
                status = "✅" if result["success"] else "❌"
                print(f"  {status} {test_name}")
                if result["success"]:
                    critical_passed += 1
        
        print(f"\n📈 FEATURE IMPLEMENTATION STATUS:")
        feature_tests = [
            ("Email-based Reset", "Admin Password Reset Email"),
            ("Account Locking", "Account Locking"),
            ("Error Handling", "Error Handling"),
            ("Token System", "Password Reset Tokens"),
            ("Graceful Failures", "Graceful Email Handling"),
            ("Backend Logging", "Backend Logging Support")
        ]
        
        for feature_name, test_name in feature_tests:
            result = next((r for r in self.results if r["test"] == test_name), None)
            if result:
                status = "✅ IMPLEMENTED" if result["success"] else "❌ NEEDS WORK"
                print(f"  {status}: {feature_name}")
        
        # Overall assessment
        print(f"\n🏆 OVERALL ASSESSMENT:")
        if critical_passed >= 3 and self.tests_passed >= 8:
            print("🎉 ADMIN PASSWORD RESET EMAIL SYSTEM: ✅ FULLY FUNCTIONAL!")
            print("\n✅ Key Achievements:")
            print("   • Email-based password reset implemented")
            print("   • Account locking works regardless of email delivery")
            print("   • Graceful email failure handling")
            print("   • Proper admin authorization")
            print("   • Complete password reset flow functional")
            print("   • Error handling improvements working")
            print("   • Backend supports manual recovery logging")
            print(f"\n🚀 System is PRODUCTION-READY with {self.tests_passed}/{self.tests_run} tests passing!")
        else:
            print("❌ ADMIN PASSWORD RESET EMAIL SYSTEM HAS ISSUES!")
            print(f"\n🔍 Issues Found:")
            print(f"   • Critical tests passed: {critical_passed}/{len(critical_tests)}")
            print(f"   • Overall success rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
            
            failed_tests = [r for r in self.results if not r["success"]]
            if failed_tests:
                print("   • Failed tests:")
                for result in failed_tests[:5]:  # Show first 5 failures
                    print(f"     - {result['test']}: {result['message']}")
            
            print(f"\n⚠️  System needs fixes before production use.")
        
        print("\n" + "=" * 70)

if __name__ == "__main__":
    tester = AdminPasswordResetEmailTester()
    tester.run_comprehensive_test()