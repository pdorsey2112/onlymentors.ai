#!/usr/bin/env python3
"""
User Suspension Endpoint Testing
Focus: Identify the specific error causing "[object Object]" response
"""

import requests
import json
import sys
import traceback
from datetime import datetime

class UserSuspensionTester:
    def __init__(self, base_url="https://admin-console-4.preview.emergentagent.com"):
        self.base_url = base_url
        self.admin_token = None
        self.user_token = None
        self.test_user_id = None
        self.tests_run = 0
        self.tests_passed = 0

    def log(self, message, level="INFO"):
        """Enhanced logging with timestamps"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")

    def make_request(self, method, endpoint, data=None, token=None, expected_status=None):
        """Make HTTP request with detailed error handling"""
        url = f"{self.base_url}/api/{endpoint}" if not endpoint.startswith('http') else endpoint
        
        headers = {'Content-Type': 'application/json'}
        if token:
            headers['Authorization'] = f'Bearer {token}'
        
        self.log(f"Making {method} request to: {url}")
        if data:
            self.log(f"Request data: {json.dumps(data, indent=2)}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)
            
            self.log(f"Response Status: {response.status_code}")
            self.log(f"Response Headers: {dict(response.headers)}")
            
            # Try to parse response as JSON
            try:
                response_data = response.json()
                self.log(f"Response JSON: {json.dumps(response_data, indent=2)}")
            except:
                self.log(f"Response Text: {response.text}")
                response_data = {"raw_text": response.text}
            
            if expected_status and response.status_code != expected_status:
                self.log(f"❌ Expected status {expected_status}, got {response.status_code}", "ERROR")
                return False, response_data
            
            return True, response_data
            
        except Exception as e:
            self.log(f"❌ Request failed: {str(e)}", "ERROR")
            self.log(f"❌ Traceback: {traceback.format_exc()}", "ERROR")
            return False, {"error": str(e)}

    def test_admin_login(self):
        """Test admin authentication"""
        self.log("🔐 Testing admin login...")
        
        login_data = {
            "email": "admin@onlymentors.ai",
            "password": "SuperAdmin2024!"
        }
        
        success, response = self.make_request('POST', 'admin/login', login_data, expected_status=200)
        
        if success and 'token' in response:
            self.admin_token = response['token']
            self.log("✅ Admin login successful")
            self.tests_passed += 1
            return True
        else:
            self.log("❌ Admin login failed", "ERROR")
            return False
        
        self.tests_run += 1

    def create_test_user(self):
        """Create a test user for suspension testing"""
        self.log("👤 Creating test user...")
        
        # Generate unique email for testing
        timestamp = int(datetime.now().timestamp())
        test_email = f"testuser_suspension_{timestamp}@test.com"
        
        user_data = {
            "email": test_email,
            "password": "TestPassword123!",
            "full_name": "Test User for Suspension"
        }
        
        success, response = self.make_request('POST', 'auth/signup', user_data, expected_status=200)
        
        if success and 'user' in response:
            self.test_user_id = response['user']['user_id']
            self.user_token = response['token']
            self.log(f"✅ Test user created: {test_email} (ID: {self.test_user_id})")
            self.tests_passed += 1
            return True
        else:
            self.log("❌ Test user creation failed", "ERROR")
            return False
        
        self.tests_run += 1

    def test_user_suspension_endpoint(self):
        """Test the specific user suspension endpoint that's causing issues"""
        self.log("🚫 Testing user suspension endpoint...")
        
        if not self.admin_token or not self.test_user_id:
            self.log("❌ Missing admin token or test user ID", "ERROR")
            return False
        
        # Test suspension request
        suspension_data = {
            "user_id": self.test_user_id,
            "reason": "Policy violation",
            "suspend": True
        }
        
        endpoint = f"admin/users/{self.test_user_id}/suspend"
        success, response = self.make_request('PUT', endpoint, suspension_data, self.admin_token, expected_status=200)
        
        self.tests_run += 1
        
        if success:
            self.log("✅ User suspension endpoint working")
            self.tests_passed += 1
            return True
        else:
            self.log("❌ User suspension endpoint failed", "ERROR")
            self.log(f"❌ This might be the source of '[object Object]' error", "ERROR")
            return False

    def test_user_suspension_validation(self):
        """Test various validation scenarios for user suspension"""
        self.log("🔍 Testing user suspension validation scenarios...")
        
        if not self.admin_token:
            self.log("❌ Missing admin token", "ERROR")
            return False
        
        test_scenarios = [
            {
                "name": "Missing user_id in body",
                "data": {"reason": "Test", "suspend": True},
                "expected_status": 422  # Validation error
            },
            {
                "name": "Missing reason",
                "data": {"user_id": self.test_user_id, "suspend": True},
                "expected_status": 422  # Validation error
            },
            {
                "name": "Invalid user_id",
                "data": {"user_id": "invalid-user-id", "reason": "Test", "suspend": True},
                "expected_status": 404  # User not found
            },
            {
                "name": "Empty reason",
                "data": {"user_id": self.test_user_id, "reason": "", "suspend": True},
                "expected_status": 422  # Validation error
            }
        ]
        
        for scenario in test_scenarios:
            self.log(f"Testing scenario: {scenario['name']}")
            endpoint = f"admin/users/{self.test_user_id}/suspend"
            success, response = self.make_request('PUT', endpoint, scenario['data'], self.admin_token, scenario['expected_status'])
            self.tests_run += 1
            
            if success:
                self.log(f"✅ Validation scenario '{scenario['name']}' passed")
                self.tests_passed += 1
            else:
                self.log(f"❌ Validation scenario '{scenario['name']}' failed", "ERROR")

    def test_email_function_directly(self):
        """Test if the email sending function is causing issues"""
        self.log("📧 Testing email function behavior...")
        
        # This will help identify if the email sending is the issue
        # We'll check the server logs for any email-related errors
        
        if not self.admin_token or not self.test_user_id:
            self.log("❌ Missing admin token or test user ID", "ERROR")
            return False
        
        # Try suspension with detailed monitoring
        suspension_data = {
            "user_id": self.test_user_id,
            "reason": "Email function test",
            "suspend": True
        }
        
        self.log("Attempting suspension with email monitoring...")
        endpoint = f"admin/users/{self.test_user_id}/suspend"
        
        # Make request and capture all details
        success, response = self.make_request('PUT', endpoint, suspension_data, self.admin_token)
        
        self.tests_run += 1
        
        if success:
            self.log("✅ Email function test passed")
            self.tests_passed += 1
            return True
        else:
            self.log("❌ Email function test failed - this could be the root cause", "ERROR")
            return False

    def test_database_operations(self):
        """Test if database operations are working correctly"""
        self.log("🗄️ Testing database operations...")
        
        if not self.admin_token:
            self.log("❌ Missing admin token", "ERROR")
            return False
        
        # Test getting user list to verify database connectivity
        success, response = self.make_request('GET', 'admin/users', token=self.admin_token, expected_status=200)
        
        self.tests_run += 1
        
        if success:
            self.log("✅ Database operations working")
            self.tests_passed += 1
            return True
        else:
            self.log("❌ Database operations failed", "ERROR")
            return False

    def test_admin_permissions(self):
        """Test admin permissions for user management"""
        self.log("🔑 Testing admin permissions...")
        
        if not self.admin_token:
            self.log("❌ Missing admin token", "ERROR")
            return False
        
        # Test admin dashboard access
        success, response = self.make_request('GET', 'admin/dashboard', token=self.admin_token, expected_status=200)
        
        self.tests_run += 1
        
        if success:
            self.log("✅ Admin permissions working")
            self.tests_passed += 1
            return True
        else:
            self.log("❌ Admin permissions failed", "ERROR")
            return False

    def run_comprehensive_test(self):
        """Run comprehensive test suite to identify the suspension issue"""
        self.log("🚀 Starting comprehensive user suspension testing...")
        self.log("=" * 60)
        
        # Test sequence
        tests = [
            ("Admin Login", self.test_admin_login),
            ("Create Test User", self.create_test_user),
            ("Database Operations", self.test_database_operations),
            ("Admin Permissions", self.test_admin_permissions),
            ("User Suspension Validation", self.test_user_suspension_validation),
            ("Email Function Test", self.test_email_function_directly),
            ("User Suspension Endpoint", self.test_user_suspension_endpoint),
        ]
        
        for test_name, test_func in tests:
            self.log(f"\n📋 Running: {test_name}")
            self.log("-" * 40)
            
            try:
                result = test_func()
                if not result:
                    self.log(f"❌ {test_name} failed - stopping here for analysis", "ERROR")
                    break
            except Exception as e:
                self.log(f"❌ {test_name} crashed: {str(e)}", "ERROR")
                self.log(f"❌ Traceback: {traceback.format_exc()}", "ERROR")
                break
        
        # Final results
        self.log("\n" + "=" * 60)
        self.log("📊 FINAL TEST RESULTS")
        self.log("=" * 60)
        self.log(f"Tests Run: {self.tests_run}")
        self.log(f"Tests Passed: {self.tests_passed}")
        self.log(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "0%")
        
        if self.tests_passed == self.tests_run:
            self.log("🎉 All tests passed! User suspension endpoint is working correctly.")
        else:
            self.log("❌ Some tests failed. The '[object Object]' error likely stems from the failed components above.")

if __name__ == "__main__":
    tester = UserSuspensionTester()
    tester.run_comprehensive_test()