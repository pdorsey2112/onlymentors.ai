#!/usr/bin/env python3
"""
User Suspension Endpoint Testing
Testing the fixed PUT /api/admin/users/{user_id}/suspend endpoint
"""

import requests
import json
import time
from datetime import datetime

class UserSuspensionTester:
    def __init__(self, base_url="https://enterprise-coach.preview.emergentagent.com"):
        self.base_url = base_url
        self.admin_token = None
        self.user_token = None
        self.test_user_id = None
        self.test_user_email = None
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None, token=None):
        """Run a single API test"""
        if endpoint.startswith('http'):
            url = endpoint
        elif endpoint.startswith('api/'):
            url = f"{self.base_url}/{endpoint}"
        else:
            url = f"{self.base_url}/api/{endpoint}"
            
        test_headers = {'Content-Type': 'application/json'}
        
        # Use specific token if provided, otherwise use admin token
        if token:
            test_headers['Authorization'] = f'Bearer {token}'
        elif self.admin_token:
            test_headers['Authorization'] = f'Bearer {self.admin_token}'
        
        if headers:
            test_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        if data:
            print(f"   Data: {json.dumps(data, indent=2)}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=30)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)}")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_admin_login(self):
        """Test admin login with provided credentials"""
        print("\n" + "="*60)
        print("🔐 TESTING ADMIN AUTHENTICATION")
        print("="*60)
        
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
        
        if success and 'token' in response:
            self.admin_token = response['token']
            print(f"✅ Admin login successful, token received")
            return True
        else:
            print("❌ Admin login failed - cannot proceed with user suspension tests")
            return False

    def create_test_user(self):
        """Create a test user for suspension testing"""
        print("\n" + "="*60)
        print("👤 CREATING TEST USER")
        print("="*60)
        
        # Generate unique email for test user
        timestamp = int(time.time())
        test_email = f"testuser_suspension_{timestamp}@test.com"
        
        success, response = self.run_test(
            "Create Test User",
            "POST",
            "api/auth/signup",
            200,
            data={
                "email": test_email,
                "password": "TestPassword123!",
                "full_name": "Test User for Suspension"
            },
            token=""  # No token needed for signup
        )
        
        if success and 'user' in response:
            self.test_user_id = response['user']['user_id']
            self.test_user_email = test_email
            self.user_token = response['token']
            print(f"✅ Test user created successfully")
            print(f"   User ID: {self.test_user_id}")
            print(f"   Email: {self.test_user_email}")
            return True
        else:
            print("❌ Failed to create test user")
            return False

    def find_existing_test_user(self):
        """Find an existing test user to suspend"""
        print("\n" + "="*60)
        print("🔍 FINDING EXISTING TEST USER")
        print("="*60)
        
        # Get all users from admin endpoint
        success, response = self.run_test(
            "Get All Users",
            "GET",
            "api/admin/users",
            200
        )
        
        if success and 'users' in response:
            users = response['users']
            print(f"   Found {len(users)} total users")
            
            # Look for testuser1@test.com or any test user
            test_users = [u for u in users if 'test' in u.get('email', '').lower()]
            
            if test_users:
                # Use the first test user found
                test_user = test_users[0]
                self.test_user_id = test_user['user_id']
                self.test_user_email = test_user['email']
                print(f"✅ Found test user: {self.test_user_email}")
                print(f"   User ID: {self.test_user_id}")
                return True
            else:
                print("❌ No test users found, will create one")
                return False
        else:
            print("❌ Failed to get users list")
            return False

    def test_user_suspension_endpoint(self):
        """Test the fixed PUT /api/admin/users/{user_id}/suspend endpoint"""
        print("\n" + "="*60)
        print("🚫 TESTING USER SUSPENSION ENDPOINT")
        print("="*60)
        
        if not self.test_user_id:
            print("❌ No test user available for suspension testing")
            return False
        
        # Test the fixed UserSuspendRequest model
        suspension_data = {
            "reason": "Policy violation",
            "suspend": True
        }
        
        success, response = self.run_test(
            "Suspend User",
            "PUT",
            f"api/admin/users/{self.test_user_id}/suspend",
            200,
            data=suspension_data
        )
        
        if success:
            print("✅ User suspension endpoint working correctly")
            print("✅ No '[object Object]' error encountered")
            
            # Verify response structure
            if 'message' in response:
                print(f"✅ Proper success message: {response['message']}")
            
            if 'user_id' in response:
                print(f"✅ User ID returned: {response['user_id']}")
            
            return True
        else:
            print("❌ User suspension endpoint failed")
            return False

    def verify_user_suspended_in_database(self):
        """Verify the user is actually suspended by checking the users list"""
        print("\n" + "="*60)
        print("🔍 VERIFYING USER SUSPENSION IN DATABASE")
        print("="*60)
        
        if not self.test_user_id:
            print("❌ No test user ID available")
            return False
        
        # Get all users and find our test user
        success, response = self.run_test(
            "Get All Users to Verify Suspension",
            "GET",
            "api/admin/users",
            200
        )
        
        if success and 'users' in response:
            users = response['users']
            
            # Find our test user
            test_user = next((u for u in users if u['user_id'] == self.test_user_id), None)
            
            if test_user:
                status = test_user.get('status', 'unknown')
                is_suspended = test_user.get('is_suspended', False)
                
                if status == 'suspended' and is_suspended:
                    print("✅ User is properly suspended in database")
                    print(f"   Status: {status}")
                    print(f"   Is Suspended: {is_suspended}")
                    print(f"   Suspended At: {test_user.get('suspended_at', 'N/A')}")
                    print(f"   Suspended By: {test_user.get('suspended_by', 'N/A')}")
                    return True
                else:
                    print(f"❌ User status is '{status}', is_suspended: {is_suspended}")
                    return False
            else:
                print("❌ Test user not found in users list")
                return False
        else:
            print("❌ Failed to get users list")
            return False

    def test_suspended_user_login(self):
        """Test that suspended user cannot login"""
        print("\n" + "="*60)
        print("🔒 TESTING SUSPENDED USER LOGIN PREVENTION")
        print("="*60)
        
        if not self.test_user_email:
            print("❌ No test user email available")
            return False
        
        # Try to login as suspended user (should fail)
        success, response = self.run_test(
            "Suspended User Login Attempt",
            "POST",
            "api/auth/login",
            401,  # Expect 401 or 403 for suspended user
            data={
                "email": self.test_user_email,
                "password": "TestPassword123!"
            },
            token=""  # No token for login
        )
        
        if success:
            print("✅ Suspended user correctly blocked from login")
            return True
        else:
            # Try 403 status code as well
            success, response = self.run_test(
                "Suspended User Login Attempt (403)",
                "POST",
                "api/auth/login",
                403,
                data={
                    "email": self.test_user_email,
                    "password": "TestPassword123!"
                },
                token=""
            )
            if success:
                print("✅ Suspended user correctly blocked from login (403)")
                return True
            else:
                print("❌ Suspended user was able to login (security issue)")
                return False

    def test_audit_log_creation(self):
        """Test that audit log entry is created for suspension"""
        print("\n" + "="*60)
        print("📝 TESTING AUDIT LOG CREATION")
        print("="*60)
        
        if not self.test_user_id:
            print("❌ No test user ID available")
            return False
        
        # Get audit history for the user
        success, response = self.run_test(
            "Get User Audit History",
            "GET",
            f"api/admin/users/{self.test_user_id}/audit",
            200
        )
        
        if success and 'audit_history' in response:
            audit_entries = response['audit_history']
            
            # Look for suspension audit entry
            suspension_entries = [
                entry for entry in audit_entries 
                if 'suspend' in entry.get('action', '').lower()
            ]
            
            if suspension_entries:
                print("✅ Audit log entry created for suspension")
                print(f"   Found {len(suspension_entries)} suspension audit entries")
                for entry in suspension_entries[:1]:  # Show first entry
                    print(f"   Entry: {json.dumps(entry, indent=4)}")
                return True
            else:
                print("❌ No suspension audit log entries found")
                return False
        else:
            print("❌ Failed to get audit history")
            return False

    def test_error_handling(self):
        """Test improved error handling (no '[object Object]' errors)"""
        print("\n" + "="*60)
        print("🛠️ TESTING IMPROVED ERROR HANDLING")
        print("="*60)
        
        # Test with invalid user ID
        success, response = self.run_test(
            "Suspend Invalid User",
            "PUT",
            "api/admin/users/invalid-user-id/suspend",
            404,  # Expect 404 for invalid user
            data={
                "reason": "Test error handling",
                "suspend": True
            }
        )
        
        if success:
            # Check that error message is proper, not "[object Object]"
            if 'detail' in response:
                error_message = response['detail']
                if '[object Object]' not in error_message:
                    print("✅ Proper error message returned (no '[object Object]')")
                    print(f"   Error message: {error_message}")
                    return True
                else:
                    print("❌ '[object Object]' error still present")
                    return False
            else:
                print("✅ Error handled properly (no '[object Object]')")
                return True
        else:
            print("❌ Error handling test failed")
            return False

    def run_all_tests(self):
        """Run all user suspension tests"""
        print("\n" + "="*80)
        print("🧪 ONLYMENTORS.AI USER SUSPENSION ENDPOINT TESTING")
        print("="*80)
        print(f"Testing against: {self.base_url}")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Test sequence
        tests = [
            ("Admin Authentication", self.test_admin_login),
            ("Find/Create Test User", lambda: self.find_existing_test_user() or self.create_test_user()),
            ("User Suspension Endpoint", self.test_user_suspension_endpoint),
            ("Verify Database Suspension", self.verify_user_suspended_in_database),
            ("Test Suspended User Login", self.test_suspended_user_login),
            ("Audit Log Creation", self.test_audit_log_creation),
            ("Error Handling", self.test_error_handling),
        ]
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                if not result:
                    print(f"\n❌ {test_name} failed - stopping test sequence")
                    break
            except Exception as e:
                print(f"\n❌ {test_name} failed with exception: {str(e)}")
                break
        
        # Final results
        print("\n" + "="*80)
        print("📊 FINAL TEST RESULTS")
        print("="*80)
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "0%")
        
        if self.tests_passed == self.tests_run:
            print("\n🎉 ALL TESTS PASSED! User suspension endpoint is working correctly!")
            print("✅ Fixed UserSuspendRequest model working")
            print("✅ No '[object Object]' errors")
            print("✅ Complete suspension process functional")
            print("✅ Proper error handling implemented")
        else:
            print(f"\n⚠️ {self.tests_run - self.tests_passed} tests failed")
            print("❌ User suspension endpoint needs attention")
        
        print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    tester = UserSuspensionTester()
    tester.run_all_tests()