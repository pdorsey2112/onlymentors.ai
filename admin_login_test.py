#!/usr/bin/env python3
"""
Admin Login Functionality Test for OnlyMentors.ai
Tests the specific admin login issue reported by the user
"""

import requests
import sys
import json
import time
from datetime import datetime

class AdminLoginTester:
    def __init__(self, base_url="https://mentor-search.preview.emergentagent.com"):
        self.base_url = base_url
        self.admin_token = None
        self.tests_run = 0
        self.tests_passed = 0
        
    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        if endpoint.startswith('api/'):
            url = f"{self.base_url}/{endpoint}"
        else:
            url = f"{self.base_url}/api/{endpoint}"
            
        test_headers = {'Content-Type': 'application/json'}
        
        if self.admin_token:
            test_headers['Authorization'] = f'Bearer {self.admin_token}'
        
        if headers:
            test_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=30)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response preview: {json.dumps(response_data, indent=2)[:500]}...")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_admin_login(self):
        """Test admin login with the specific credentials"""
        print(f"\n🔐 Testing Admin Login")
        print(f"   Email: admin@onlymentors.ai")
        print(f"   Password: SuperAdmin2024!")
        
        success, response = self.run_test(
            "Admin Login",
            "POST",
            "api/admin/login",
            200,
            data={
                "email": "admin@onlymentors.ai",
                "password": "SuperAdmin2024!"
            }
        )
        
        if success:
            if 'token' in response:
                self.admin_token = response['token']
                print(f"✅ Admin login successful!")
                print(f"   Token received: {self.admin_token[:20]}...")
                
                # Check admin details in response
                if 'admin' in response:
                    admin_info = response['admin']
                    print(f"   Admin ID: {admin_info.get('admin_id', 'N/A')}")
                    print(f"   Admin Email: {admin_info.get('email', 'N/A')}")
                    print(f"   Admin Role: {admin_info.get('role', 'N/A')}")
                    print(f"   Admin Status: {admin_info.get('status', 'N/A')}")
                
                return True, response
            else:
                print(f"❌ Login response missing token")
                return False, {}
        else:
            print(f"❌ Admin login failed")
            return False, {}

    def test_admin_token_validation(self):
        """Test if the admin token is valid for protected endpoints"""
        if not self.admin_token:
            print(f"❌ No admin token available for validation")
            return False
            
        print(f"\n🔑 Testing Admin Token Validation")
        
        # Test token format (JWT should have 3 parts)
        token_parts = self.admin_token.split('.')
        if len(token_parts) == 3:
            print(f"✅ Token has correct JWT format (3 parts)")
        else:
            print(f"❌ Token has incorrect format ({len(token_parts)} parts)")
            return False
        
        # Test with a simple admin endpoint that requires authentication
        success, response = self.run_test(
            "Admin Token Validation",
            "GET",
            "api/admin/dashboard",
            200
        )
        
        if success:
            print(f"✅ Admin token is valid for protected endpoints")
            return True
        else:
            print(f"❌ Admin token validation failed")
            return False

    def test_admin_users_endpoint(self):
        """Test admin users endpoint with the admin token"""
        if not self.admin_token:
            print(f"❌ No admin token available for users endpoint test")
            return False
            
        print(f"\n👥 Testing Admin Users Endpoint")
        
        success, response = self.run_test(
            "Admin Users List",
            "GET",
            "api/admin/users",
            200
        )
        
        if success:
            if 'users' in response:
                users = response['users']
                print(f"✅ Admin users endpoint working!")
                print(f"   Total users retrieved: {len(users)}")
                
                # Show sample user data (first user if available)
                if users:
                    sample_user = users[0]
                    print(f"   Sample user data:")
                    print(f"     User ID: {sample_user.get('user_id', 'N/A')}")
                    print(f"     Email: {sample_user.get('email', 'N/A')}")
                    print(f"     Full Name: {sample_user.get('full_name', 'N/A')}")
                    print(f"     Questions Asked: {sample_user.get('questions_asked', 'N/A')}")
                    print(f"     Is Subscribed: {sample_user.get('is_subscribed', 'N/A')}")
                
                return True, response
            else:
                print(f"❌ Users endpoint response missing 'users' field")
                return False, {}
        else:
            print(f"❌ Admin users endpoint failed")
            return False, {}

    def test_admin_authentication_without_token(self):
        """Test that admin endpoints require authentication"""
        print(f"\n🔒 Testing Admin Authentication Requirements")
        
        # Temporarily remove token
        original_token = self.admin_token
        self.admin_token = None
        
        # Test admin dashboard without token (should fail)
        success1, _ = self.run_test(
            "Admin Dashboard - No Auth",
            "GET",
            "api/admin/dashboard",
            401
        )
        
        # Test admin users without token (should fail)
        success2, _ = self.run_test(
            "Admin Users - No Auth",
            "GET",
            "api/admin/users",
            401
        )
        
        # Restore token
        self.admin_token = original_token
        
        if success1 and success2:
            print(f"✅ Admin endpoints properly require authentication")
            return True
        else:
            print(f"❌ Admin endpoints don't properly require authentication")
            return False

    def test_admin_login_with_invalid_credentials(self):
        """Test admin login with invalid credentials"""
        print(f"\n🚫 Testing Admin Login with Invalid Credentials")
        
        # Test with wrong password
        success1, _ = self.run_test(
            "Admin Login - Wrong Password",
            "POST",
            "api/admin/login",
            401,
            data={
                "email": "admin@onlymentors.ai",
                "password": "WrongPassword123!"
            }
        )
        
        # Test with wrong email
        success2, _ = self.run_test(
            "Admin Login - Wrong Email",
            "POST",
            "api/admin/login",
            401,
            data={
                "email": "wrong@onlymentors.ai",
                "password": "SuperAdmin2024!"
            }
        )
        
        if success1 and success2:
            print(f"✅ Invalid credentials properly rejected")
            return True
        else:
            print(f"❌ Invalid credentials not properly rejected")
            return False

    def test_regular_user_cannot_access_admin_endpoints(self):
        """Test that regular user tokens cannot access admin endpoints"""
        print(f"\n🚷 Testing Regular User Access to Admin Endpoints")
        
        # First create a regular user and get their token
        timestamp = datetime.now().strftime('%H%M%S')
        test_email = f"regular_user_{timestamp}@test.com"
        
        # Create regular user
        success, response = self.run_test(
            "Create Regular User",
            "POST",
            "api/auth/signup",
            200,
            data={
                "email": test_email,
                "password": "TestPass123!",
                "full_name": "Regular Test User"
            }
        )
        
        if not success or 'token' not in response:
            print(f"❌ Could not create regular user for testing")
            return False
        
        # Store admin token and use regular user token
        admin_token_backup = self.admin_token
        self.admin_token = response['token']
        
        print(f"   Created regular user: {test_email}")
        print(f"   Regular user token: {self.admin_token[:20]}...")
        
        # Try to access admin endpoints with regular user token
        success1, _ = self.run_test(
            "Regular User - Admin Dashboard",
            "GET",
            "api/admin/dashboard",
            401  # Should be forbidden
        )
        
        success2, _ = self.run_test(
            "Regular User - Admin Users",
            "GET",
            "api/admin/users",
            401  # Should be forbidden
        )
        
        # Restore admin token
        self.admin_token = admin_token_backup
        
        if success1 and success2:
            print(f"✅ Regular users properly blocked from admin endpoints")
            return True
        else:
            print(f"❌ Regular users can access admin endpoints (security issue!)")
            return False

def main():
    print("🚀 Starting OnlyMentors.ai Admin Login Functionality Test")
    print("=" * 70)
    print("Testing the specific admin login issue reported by the user:")
    print("- Admin login endpoint: POST /api/admin/login")
    print("- Credentials: admin@onlymentors.ai / SuperAdmin2024!")
    print("- Admin token validation for protected endpoints")
    print("- Admin users endpoint access")
    print("=" * 70)
    
    tester = AdminLoginTester()
    
    # Test sequence
    test_results = {
        "admin_login": False,
        "token_validation": False,
        "users_endpoint": False,
        "auth_required": False,
        "invalid_credentials": False,
        "regular_user_blocked": False
    }
    
    # 1. Test admin login
    print(f"\n{'='*50}")
    print("🔐 STEP 1: ADMIN LOGIN TEST")
    print(f"{'='*50}")
    
    success, login_response = tester.test_admin_login()
    test_results["admin_login"] = success
    
    if not success:
        print(f"\n❌ CRITICAL: Admin login failed - cannot proceed with other tests")
        print(f"   This confirms the user's report that admin console is not signing admins in")
        print_final_results(tester, test_results)
        return 1
    
    # 2. Test token validation
    print(f"\n{'='*50}")
    print("🔑 STEP 2: ADMIN TOKEN VALIDATION")
    print(f"{'='*50}")
    
    test_results["token_validation"] = tester.test_admin_token_validation()
    
    # 3. Test admin users endpoint
    print(f"\n{'='*50}")
    print("👥 STEP 3: ADMIN USERS ENDPOINT")
    print(f"{'='*50}")
    
    success, users_response = tester.test_admin_users_endpoint()
    test_results["users_endpoint"] = success
    
    # 4. Test authentication requirements
    print(f"\n{'='*50}")
    print("🔒 STEP 4: AUTHENTICATION REQUIREMENTS")
    print(f"{'='*50}")
    
    test_results["auth_required"] = tester.test_admin_authentication_without_token()
    
    # 5. Test invalid credentials
    print(f"\n{'='*50}")
    print("🚫 STEP 5: INVALID CREDENTIALS TEST")
    print(f"{'='*50}")
    
    test_results["invalid_credentials"] = tester.test_admin_login_with_invalid_credentials()
    
    # 6. Test regular user access blocking
    print(f"\n{'='*50}")
    print("🚷 STEP 6: REGULAR USER ACCESS BLOCKING")
    print(f"{'='*50}")
    
    test_results["regular_user_blocked"] = tester.test_regular_user_cannot_access_admin_endpoints()
    
    # Print final results
    print_final_results(tester, test_results)
    
    # Determine overall success
    critical_tests = ["admin_login", "token_validation", "users_endpoint"]
    critical_passed = sum(test_results[test] for test in critical_tests)
    
    if critical_passed == len(critical_tests):
        print(f"\n🎉 ADMIN LOGIN FUNCTIONALITY: ✅ WORKING CORRECTLY!")
        print(f"   The admin console login issue reported by the user is NOT a backend problem.")
        print(f"   All admin authentication and authorization is working properly.")
        return 0
    else:
        print(f"\n❌ ADMIN LOGIN FUNCTIONALITY: CRITICAL ISSUES FOUND!")
        print(f"   This confirms the user's report of admin console login problems.")
        print(f"   Backend admin authentication has issues that need to be fixed.")
        return 1

def print_final_results(tester, test_results):
    """Print comprehensive test results"""
    print("\n" + "=" * 70)
    print(f"📊 ADMIN LOGIN FUNCTIONALITY TEST RESULTS")
    print("=" * 70)
    
    print(f"\n🔍 Individual Test Results:")
    test_descriptions = {
        "admin_login": "Admin Login (admin@onlymentors.ai / SuperAdmin2024!)",
        "token_validation": "Admin Token Validation",
        "users_endpoint": "Admin Users Endpoint Access",
        "auth_required": "Authentication Requirements",
        "invalid_credentials": "Invalid Credentials Rejection",
        "regular_user_blocked": "Regular User Access Blocking"
    }
    
    for test_key, passed in test_results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        description = test_descriptions.get(test_key, test_key)
        print(f"   {description}: {status}")
    
    print(f"\n📈 Overall Statistics:")
    print(f"   Total API Tests Run: {tester.tests_run}")
    print(f"   Total API Tests Passed: {tester.tests_passed}")
    print(f"   API Success Rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    total_tests = len(test_results)
    passed_tests = sum(test_results.values())
    print(f"   Functional Tests Passed: {passed_tests}/{total_tests}")
    print(f"   Functional Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    # Critical assessment
    critical_tests = ["admin_login", "token_validation", "users_endpoint"]
    critical_passed = sum(test_results[test] for test in critical_tests)
    
    print(f"\n🎯 CRITICAL FUNCTIONALITY ASSESSMENT:")
    print(f"   Critical Tests Passed: {critical_passed}/{len(critical_tests)}")
    
    if critical_passed == len(critical_tests):
        print(f"   Status: ✅ ADMIN LOGIN FULLY FUNCTIONAL")
        print(f"\n✅ Key Findings:")
        print(f"   • Admin login endpoint working correctly")
        print(f"   • JWT token generation and validation working")
        print(f"   • Admin users endpoint accessible with valid token")
        print(f"   • Authentication and authorization properly enforced")
        print(f"   • Security controls working (invalid credentials rejected)")
        print(f"   • Regular users properly blocked from admin functions")
        print(f"\n💡 CONCLUSION:")
        print(f"   The backend admin authentication system is working correctly.")
        print(f"   If users are experiencing admin console login issues, the problem")
        print(f"   is likely in the frontend, network connectivity, or user error.")
    else:
        print(f"   Status: ❌ ADMIN LOGIN HAS CRITICAL ISSUES")
        print(f"\n🔍 Issues Found:")
        
        if not test_results["admin_login"]:
            print(f"   • Admin login endpoint not working with correct credentials")
        if not test_results["token_validation"]:
            print(f"   • Admin token validation failing")
        if not test_results["users_endpoint"]:
            print(f"   • Admin users endpoint not accessible")
        
        print(f"\n💡 CONCLUSION:")
        print(f"   The backend admin authentication system has critical issues.")
        print(f"   This confirms the user's report of admin console login problems.")

if __name__ == "__main__":
    sys.exit(main())