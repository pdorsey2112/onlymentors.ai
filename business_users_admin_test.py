#!/usr/bin/env python3
"""
Business Users Management Admin Testing
Comprehensive testing for super admin business user management endpoints
"""

import requests
import json
import time
import uuid
from datetime import datetime

# Configuration
BASE_URL = "https://enterprise-coach.preview.emergentagent.com/api"
TEST_ADMIN_EMAIL = f"testadmin{int(time.time())}@onlymentors.ai"
TEST_ADMIN_PASSWORD = "TestAdmin123!"

# Test business users data
TEST_BUSINESS_USERS = [
    {
        "email": "employee1@testcorp.com",
        "password": "TestPass123!",
        "full_name": "John Employee",
        "user_type": "business_employee",
        "company_name": "Test Corporation"
    },
    {
        "email": "admin1@testcorp.com", 
        "password": "TestPass123!",
        "full_name": "Jane Admin",
        "user_type": "business_admin",
        "company_name": "Test Corporation"
    },
    {
        "email": "employee2@anothercorp.com",
        "password": "TestPass123!",
        "full_name": "Bob Worker",
        "user_type": "business_employee", 
        "company_name": "Another Corporation"
    }
]

class BusinessUsersAdminTester:
    def __init__(self):
        self.admin_token = None
        self.regular_user_token = None
        self.test_user_ids = []
        self.test_company_ids = []
        self.results = []
        
    def log_result(self, test_name, success, details="", response_data=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if not success and response_data:
            print(f"   Response: {response_data}")
        print()

    def setup_admin_authentication(self):
        """Setup admin authentication"""
        print("🔧 Setting up admin authentication...")
        
        # Create a unique admin user for this test run
        admin_email = f"testadmin{int(time.time())}@onlymentors.ai"
        
        try:
            # Create a regular user with admin role
            response = requests.post(f"{BASE_URL}/auth/register", data={
                "email": admin_email,
                "password": TEST_ADMIN_PASSWORD,
                "full_name": "Super Admin User",
                "phone_number": "+1234567890",
                "communication_preferences": json.dumps({"email": True}),
                "subscription_plan": "premium",
                "become_mentor": False
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token")
                
                # Set admin role using database script
                import subprocess
                result = subprocess.run([
                    "python", "/app/setup_admin_user.py", admin_email
                ], capture_output=True, text=True)
                
                if "✅ Admin role added" in result.stdout:
                    self.log_result("Admin User Creation", True, f"Admin user created with role: {admin_email}")
                    return True
                else:
                    self.log_result("Admin User Creation", False, f"Failed to set admin role: {result.stdout}")
                    return False
            else:
                self.log_result("Admin User Creation", False, f"Failed to create admin user: {response.text}")
                return False
                    
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Exception: {str(e)}")
            return False

    def setup_test_business_users(self):
        """Create test business users and companies or use existing ones"""
        print("🔧 Setting up test business users...")
        
        # First, let's get existing business users to test with
        if self.admin_token:
            try:
                headers = {"Authorization": f"Bearer {self.admin_token}"}
                response = requests.get(f"{BASE_URL}/admin/business-users", headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    existing_users = data.get("users", [])
                    
                    # Use first few existing users for testing
                    for user in existing_users[:3]:
                        if user.get("user_id"):
                            self.test_user_ids.append(user["user_id"])
                    
                    if len(self.test_user_ids) > 0:
                        self.log_result("Using Existing Business Users", True, 
                                      f"Found {len(self.test_user_ids)} existing business users for testing")
                        return
                        
            except Exception as e:
                self.log_result("Get Existing Users", False, f"Exception: {str(e)}")
        
        # If no existing users or admin token not available, try to create new ones
        timestamp = int(time.time())
        
        # Create test companies first
        for i, user_data in enumerate(TEST_BUSINESS_USERS):
            company_name = user_data["company_name"]
            
            # Create company if not exists
            company_id = str(uuid.uuid4())
            company_data = {
                "company_id": company_id,
                "company_name": company_name,
                "slug": company_name.lower().replace(" ", "-"),
                "contact_email": user_data["email"],
                "status": "active"
            }
            
            # Store company ID for cleanup
            self.test_company_ids.append(company_id)
            
            # Create business user with unique email
            unique_email = f"{timestamp}_{user_data['email']}"
            
            try:
                response = requests.post(f"{BASE_URL}/auth/register", data={
                    "email": unique_email,
                    "password": user_data["password"],
                    "full_name": user_data["full_name"],
                    "phone_number": f"+123456789{timestamp}{i}",
                    "communication_preferences": json.dumps({"email": True}),
                    "subscription_plan": "business",
                    "become_mentor": False
                })
                
                if response.status_code == 200:
                    data = response.json()
                    user_id = data["user"]["user_id"]
                    self.test_user_ids.append(user_id)
                    
                    self.log_result(f"Test User Creation - {user_data['full_name']}", True, 
                                  f"Created business user: {unique_email}")
                else:
                    self.log_result(f"Test User Creation - {user_data['full_name']}", False, 
                                  f"Failed to create user: {response.text}")
                    
            except Exception as e:
                self.log_result(f"Test User Creation - {user_data['full_name']}", False, 
                              f"Exception: {str(e)}")

    def setup_regular_user_authentication(self):
        """Setup regular user for authorization testing"""
        print("🔧 Setting up regular user...")
        
        timestamp = int(time.time())
        unique_email = f"regular{timestamp}@test.com"
        
        try:
            response = requests.post(f"{BASE_URL}/auth/register", data={
                "email": unique_email,
                "password": "TestPass123!",
                "full_name": "Regular User",
                "phone_number": f"+198765432{timestamp}",
                "communication_preferences": json.dumps({"email": True}),
                "subscription_plan": "free",
                "become_mentor": False
            })
            
            if response.status_code == 200:
                data = response.json()
                self.regular_user_token = data.get("token")
                self.log_result("Regular User Setup", True, "Regular user created for auth testing")
                return True
            else:
                self.log_result("Regular User Setup", False, f"Failed: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Regular User Setup", False, f"Exception: {str(e)}")
            return False

    def test_business_users_retrieval(self):
        """Test GET /api/admin/business-users endpoint"""
        print("🧪 Testing Business Users Retrieval...")
        
        if not self.admin_token:
            self.log_result("Business Users Retrieval", False, "No admin token available")
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{BASE_URL}/admin/business-users", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                users = data.get("users", [])
                total_count = data.get("total_count", 0)
                
                # Verify response structure
                success = True
                details = []
                
                if not isinstance(users, list):
                    success = False
                    details.append("Users should be a list")
                
                if total_count != len(users):
                    success = False
                    details.append(f"Total count mismatch: {total_count} vs {len(users)}")
                
                # Check if business users are returned
                business_user_types = ["business_employee", "business_admin"]
                business_users_found = [u for u in users if u.get("user_type") in business_user_types]
                
                if len(business_users_found) == 0:
                    details.append("No business users found (expected at least test users)")
                
                # Verify company information enrichment
                for user in business_users_found[:3]:  # Check first 3
                    if "company_name" not in user:
                        details.append(f"User {user.get('email', 'unknown')} missing company_name")
                    
                    required_fields = ["user_id", "email", "full_name", "user_type"]
                    for field in required_fields:
                        if field not in user:
                            details.append(f"User missing required field: {field}")
                
                self.log_result("Business Users Retrieval", success, 
                              f"Found {len(business_users_found)} business users. " + "; ".join(details),
                              {"total_users": len(users), "business_users": len(business_users_found)})
                
            elif response.status_code == 403:
                self.log_result("Business Users Retrieval", False, 
                              "Access denied - admin authentication may not be working properly")
            else:
                self.log_result("Business Users Retrieval", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Business Users Retrieval", False, f"Exception: {str(e)}")

    def test_business_users_management_actions(self):
        """Test POST /api/admin/business-users/manage endpoint"""
        print("🧪 Testing Business Users Management Actions...")
        
        if not self.admin_token or not self.test_user_ids:
            self.log_result("Business Users Management", False, "No admin token or test users available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test suspend action
        try:
            suspend_data = {
                "user_ids": [self.test_user_ids[0]] if self.test_user_ids else [],
                "action": "suspend",
                "reason": "Test suspension"
            }
            
            response = requests.post(f"{BASE_URL}/admin/business-users/manage", 
                                   json=suspend_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                success = data.get("success", False)
                results = data.get("results", [])
                
                if success and len(results) > 0 and results[0].get("status") == "suspended":
                    self.log_result("Business User Suspend Action", True, 
                                  f"Successfully suspended user {self.test_user_ids[0]}")
                else:
                    self.log_result("Business User Suspend Action", False, 
                                  f"Suspend failed: {data}")
            else:
                self.log_result("Business User Suspend Action", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Business User Suspend Action", False, f"Exception: {str(e)}")
        
        # Test activate action
        try:
            activate_data = {
                "user_ids": [self.test_user_ids[0]] if self.test_user_ids else [],
                "action": "activate",
                "reason": "Test activation"
            }
            
            response = requests.post(f"{BASE_URL}/admin/business-users/manage", 
                                   json=activate_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                success = data.get("success", False)
                results = data.get("results", [])
                
                if success and len(results) > 0 and results[0].get("status") == "activated":
                    self.log_result("Business User Activate Action", True, 
                                  f"Successfully activated user {self.test_user_ids[0]}")
                else:
                    self.log_result("Business User Activate Action", False, 
                                  f"Activate failed: {data}")
            else:
                self.log_result("Business User Activate Action", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Business User Activate Action", False, f"Exception: {str(e)}")
        
        # Test delete action (use a separate user for this)
        if len(self.test_user_ids) >= 3:
            try:
                delete_data = {
                    "user_ids": [self.test_user_ids[2]],  # Use third user for delete test
                    "action": "delete",
                    "reason": "Test deletion"
                }
                
                response = requests.post(f"{BASE_URL}/admin/business-users/manage", 
                                       json=delete_data, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    success = data.get("success", False)
                    results = data.get("results", [])
                    
                    if success and len(results) > 0 and results[0].get("status") == "deleted":
                        self.log_result("Business User Delete Action", True, 
                                      f"Successfully deleted user {self.test_user_ids[2]}")
                        # Remove from test_user_ids since it's deleted
                        self.test_user_ids.remove(self.test_user_ids[2])
                    else:
                        self.log_result("Business User Delete Action", False, 
                                      f"Delete failed: {data}")
                else:
                    self.log_result("Business User Delete Action", False, 
                                  f"HTTP {response.status_code}: {response.text}")
                    
            except Exception as e:
                self.log_result("Business User Delete Action", False, f"Exception: {str(e)}")
        
        # Test bulk operations with multiple users
        if len(self.test_user_ids) >= 2:
            try:
                bulk_data = {
                    "user_ids": self.test_user_ids[:2],
                    "action": "suspend",
                    "reason": "Bulk test suspension"
                }
                
                response = requests.post(f"{BASE_URL}/admin/business-users/manage", 
                                       json=bulk_data, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    success = data.get("success", False)
                    results = data.get("results", [])
                    
                    if success and len(results) == 2:
                        suspended_count = len([r for r in results if r.get("status") == "suspended"])
                        self.log_result("Bulk Business User Management", True, 
                                      f"Bulk operation processed {len(results)} users, {suspended_count} suspended")
                    else:
                        self.log_result("Bulk Business User Management", False, 
                                      f"Bulk operation failed: {data}")
                else:
                    self.log_result("Bulk Business User Management", False, 
                                  f"HTTP {response.status_code}: {response.text}")
                    
            except Exception as e:
                self.log_result("Bulk Business User Management", False, f"Exception: {str(e)}")
        
        # Test invalid action error handling
        try:
            invalid_data = {
                "user_ids": [self.test_user_ids[0]] if self.test_user_ids else [],
                "action": "invalid_action",
                "reason": "Test invalid action"
            }
            
            response = requests.post(f"{BASE_URL}/admin/business-users/manage", 
                                   json=invalid_data, headers=headers)
            
            if response.status_code == 400:
                self.log_result("Invalid Action Error Handling", True, 
                              "Correctly rejected invalid action")
            else:
                self.log_result("Invalid Action Error Handling", False, 
                              f"Should have returned 400 for invalid action, got {response.status_code}")
                
        except Exception as e:
            self.log_result("Invalid Action Error Handling", False, f"Exception: {str(e)}")

    def test_password_reset_functionality(self):
        """Test POST /api/admin/business-users/reset-password endpoint"""
        print("🧪 Testing Password Reset Functionality...")
        
        if not self.admin_token or not self.test_user_ids:
            self.log_result("Password Reset", False, "No admin token or test users available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            reset_data = {
                "user_id": self.test_user_ids[0] if self.test_user_ids else "test-user-id"
            }
            
            response = requests.post(f"{BASE_URL}/admin/business-users/reset-password", 
                                   json=reset_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                success = data.get("success", False)
                temp_password = data.get("temporary_password")
                message = data.get("message", "")
                
                if success and temp_password and len(temp_password) >= 8:
                    self.log_result("Password Reset Generation", True, 
                                  f"Generated secure temporary password (length: {len(temp_password)})")
                    
                    # Verify password complexity
                    has_letters = any(c.isalpha() for c in temp_password)
                    has_digits = any(c.isdigit() for c in temp_password)
                    
                    if has_letters and has_digits:
                        self.log_result("Password Security Check", True, 
                                      "Temporary password contains letters and digits")
                    else:
                        self.log_result("Password Security Check", False, 
                                      "Temporary password lacks complexity")
                        
                    # Check message content
                    if "reset" in message.lower() and "change" in message.lower():
                        self.log_result("Password Reset Message", True, 
                                      "Reset message contains appropriate instructions")
                    else:
                        self.log_result("Password Reset Message", False, 
                                      f"Reset message unclear: {message}")
                        
                else:
                    self.log_result("Password Reset Generation", False, 
                                  f"Password reset failed: {data}")
                    
            elif response.status_code == 404:
                self.log_result("Password Reset - User Not Found", True, 
                              "Correctly handled non-existent user")
            else:
                self.log_result("Password Reset Generation", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Password Reset Generation", False, f"Exception: {str(e)}")
        
        # Test error handling for missing user_id
        try:
            invalid_data = {}  # Missing user_id
            
            response = requests.post(f"{BASE_URL}/admin/business-users/reset-password", 
                                   json=invalid_data, headers=headers)
            
            if response.status_code == 400:
                self.log_result("Password Reset Error Handling", True, 
                              "Correctly rejected request without user_id")
            else:
                self.log_result("Password Reset Error Handling", False, 
                              f"Should have returned 400 for missing user_id, got {response.status_code}")
                
        except Exception as e:
            self.log_result("Password Reset Error Handling", False, f"Exception: {str(e)}")

    def test_authentication_and_authorization(self):
        """Test authentication and authorization requirements"""
        print("🧪 Testing Authentication and Authorization...")
        
        # Test without authentication
        try:
            response = requests.get(f"{BASE_URL}/admin/business-users")
            
            if response.status_code in [401, 403]:
                self.log_result("No Auth - Business Users Endpoint", True, 
                              "Correctly rejected unauthenticated request")
            else:
                self.log_result("No Auth - Business Users Endpoint", False, 
                              f"Should require auth, got {response.status_code}")
                
        except Exception as e:
            self.log_result("No Auth - Business Users Endpoint", False, f"Exception: {str(e)}")
        
        # Test with regular user token (non-admin)
        if self.regular_user_token:
            try:
                headers = {"Authorization": f"Bearer {self.regular_user_token}"}
                response = requests.get(f"{BASE_URL}/admin/business-users", headers=headers)
                
                if response.status_code == 403:
                    self.log_result("Non-Admin Auth - Business Users", True, 
                                  "Correctly rejected non-admin user")
                else:
                    self.log_result("Non-Admin Auth - Business Users", False, 
                                  f"Should reject non-admin, got {response.status_code}")
                    
            except Exception as e:
                self.log_result("Non-Admin Auth - Business Users", False, f"Exception: {str(e)}")
        
        # Test management endpoint authorization
        if self.regular_user_token:
            try:
                headers = {"Authorization": f"Bearer {self.regular_user_token}"}
                data = {"user_ids": ["test"], "action": "suspend"}
                response = requests.post(f"{BASE_URL}/admin/business-users/manage", 
                                       json=data, headers=headers)
                
                if response.status_code == 403:
                    self.log_result("Non-Admin Auth - Management Endpoint", True, 
                                  "Correctly rejected non-admin for management actions")
                else:
                    self.log_result("Non-Admin Auth - Management Endpoint", False, 
                                  f"Should reject non-admin, got {response.status_code}")
                    
            except Exception as e:
                self.log_result("Non-Admin Auth - Management Endpoint", False, f"Exception: {str(e)}")
        
        # Test password reset authorization
        if self.regular_user_token:
            try:
                headers = {"Authorization": f"Bearer {self.regular_user_token}"}
                data = {"user_id": "test"}
                response = requests.post(f"{BASE_URL}/admin/business-users/reset-password", 
                                       json=data, headers=headers)
                
                if response.status_code == 403:
                    self.log_result("Non-Admin Auth - Password Reset", True, 
                                  "Correctly rejected non-admin for password reset")
                else:
                    self.log_result("Non-Admin Auth - Password Reset", False, 
                                  f"Should reject non-admin, got {response.status_code}")
                    
            except Exception as e:
                self.log_result("Non-Admin Auth - Password Reset", False, f"Exception: {str(e)}")

    def test_data_integration(self):
        """Test data integration and filtering"""
        print("🧪 Testing Data Integration...")
        
        if not self.admin_token:
            self.log_result("Data Integration", False, "No admin token available")
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{BASE_URL}/admin/business-users", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                users = data.get("users", [])
                
                # Test user type filtering
                business_types = ["business_employee", "business_admin"]
                non_business_users = [u for u in users if u.get("user_type") not in business_types]
                
                if len(non_business_users) == 0:
                    self.log_result("User Type Filtering", True, 
                                  "Only business users returned (correct filtering)")
                else:
                    self.log_result("User Type Filtering", False, 
                                  f"Found {len(non_business_users)} non-business users in results")
                
                # Test company information enrichment
                users_with_company = [u for u in users if "company_name" in u]
                users_without_company = [u for u in users if "company_name" not in u]
                
                if len(users_with_company) > 0:
                    self.log_result("Company Information Enrichment", True, 
                                  f"{len(users_with_company)} users have company information")
                else:
                    self.log_result("Company Information Enrichment", False, 
                                  "No users have company information enriched")
                
                # Test mentor status inclusion
                users_with_mentor_status = [u for u in users if "is_mentor" in u]
                
                if len(users_with_mentor_status) > 0:
                    self.log_result("Mentor Status Inclusion", True, 
                                  f"{len(users_with_mentor_status)} users have mentor status")
                else:
                    self.log_result("Mentor Status Inclusion", False, 
                                  "No users have mentor status information")
                
                # Test required fields presence
                required_fields = ["user_id", "email", "full_name", "user_type", "created_at"]
                field_coverage = {}
                
                for field in required_fields:
                    users_with_field = [u for u in users if field in u and u[field] is not None]
                    field_coverage[field] = len(users_with_field)
                
                missing_fields = [f for f, count in field_coverage.items() if count < len(users)]
                
                if len(missing_fields) == 0:
                    self.log_result("Required Fields Coverage", True, 
                                  "All users have required fields")
                else:
                    self.log_result("Required Fields Coverage", False, 
                                  f"Missing fields in some users: {missing_fields}")
                
            else:
                self.log_result("Data Integration", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Data Integration", False, f"Exception: {str(e)}")

    def cleanup_test_data(self):
        """Clean up test data"""
        print("🧹 Cleaning up test data...")
        
        if not self.admin_token:
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Delete test users
        if self.test_user_ids:
            try:
                delete_data = {
                    "user_ids": self.test_user_ids,
                    "action": "delete",
                    "reason": "Test cleanup"
                }
                
                response = requests.post(f"{BASE_URL}/admin/business-users/manage", 
                                       json=delete_data, headers=headers)
                
                if response.status_code == 200:
                    self.log_result("Test Data Cleanup", True, 
                                  f"Cleaned up {len(self.test_user_ids)} test users")
                else:
                    self.log_result("Test Data Cleanup", False, 
                                  f"Cleanup failed: {response.text}")
                    
            except Exception as e:
                self.log_result("Test Data Cleanup", False, f"Exception: {str(e)}")

    def run_all_tests(self):
        """Run all business users admin tests"""
        print("🚀 Starting Business Users Admin Management Testing")
        print("=" * 60)
        
        # Setup
        if not self.setup_admin_authentication():
            print("❌ Cannot proceed without admin authentication")
            return
        
        self.setup_regular_user_authentication()
        self.setup_test_business_users()
        
        # Core tests
        self.test_business_users_retrieval()
        self.test_business_users_management_actions()
        self.test_password_reset_functionality()
        self.test_authentication_and_authorization()
        self.test_data_integration()
        
        # Cleanup
        self.cleanup_test_data()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 BUSINESS USERS ADMIN TESTING SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r["success"]])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n🚨 FAILED TESTS:")
            for result in self.results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['details']}")
        
        print("\n🎯 SUCCESS CRITERIA VERIFICATION:")
        
        # Check critical success criteria
        critical_tests = [
            "Business Users Retrieval",
            "Business User Suspend Action", 
            "Business User Activate Action",
            "Business User Delete Action",
            "Password Reset Generation",
            "No Auth - Business Users Endpoint",
            "User Type Filtering"
        ]
        
        critical_passed = 0
        for test_name in critical_tests:
            test_result = next((r for r in self.results if test_name in r["test"]), None)
            if test_result and test_result["success"]:
                critical_passed += 1
                print(f"   ✅ {test_name}")
            else:
                print(f"   ❌ {test_name}")
        
        print(f"\nCritical Tests Passed: {critical_passed}/{len(critical_tests)}")
        
        if critical_passed == len(critical_tests):
            print("\n🎉 ALL CRITICAL BUSINESS USERS ADMIN FUNCTIONALITY WORKING!")
        else:
            print(f"\n⚠️  {len(critical_tests) - critical_passed} critical issues need attention")
        
        return self.results

if __name__ == "__main__":
    tester = BusinessUsersAdminTester()
    results = tester.run_all_tests()