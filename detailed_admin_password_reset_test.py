#!/usr/bin/env python3
"""
Detailed Admin Password Reset Test - Focused on Review Requirements
Tests specific requirements from the review request:
1. POST /api/admin/users/{user_id}/reset-password endpoint
2. Password_hash field gets updated in database
3. Temporary password is generated and returned
4. Audit log entry is created
5. User can login with new temporary password
6. Test with testuser1@test.com through testuser100@test.com
"""

import requests
import json
import time
import random
from datetime import datetime

# Configuration
BACKEND_URL = "https://enterprise-coach.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@onlymentors.ai"
ADMIN_PASSWORD = "SuperAdmin2024!"
ORIGINAL_TEST_PASSWORD = "TestUser123!"

class DetailedAdminPasswordResetTester:
    def __init__(self):
        self.admin_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, message, details=None):
        """Log detailed test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        print(f"    {message}")
        if details:
            print(f"    Details: {json.dumps(details, indent=2)}")
        print()
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def admin_login(self):
        """Get admin authentication token"""
        try:
            print("🔐 Authenticating as admin...")
            response = requests.post(f"{BACKEND_URL}/admin/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token")
                self.log_test("Admin Authentication", True, 
                            f"Successfully authenticated as {ADMIN_EMAIL}")
                return True
            else:
                self.log_test("Admin Authentication", False, 
                            f"Failed to authenticate: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def find_or_create_test_user(self):
        """Find existing test user or create one with the specified pattern"""
        try:
            # Try to find an existing test user (testuser1@test.com to testuser100@test.com)
            test_user_found = None
            test_user_id = None
            
            # Try a few common test user emails
            for i in range(1, 11):  # Try testuser1 through testuser10
                test_email = f"testuser{i}@test.com"
                
                # Try to login to see if user exists
                response = requests.post(f"{BACKEND_URL}/auth/login", json={
                    "email": test_email,
                    "password": ORIGINAL_TEST_PASSWORD
                })
                
                if response.status_code == 200:
                    data = response.json()
                    test_user_found = test_email
                    test_user_id = data["user"]["user_id"]
                    self.log_test("Find Test User", True, 
                                f"Found existing test user: {test_email} (ID: {test_user_id})")
                    return test_user_found, test_user_id
            
            # If no existing user found, create a new one
            test_number = random.randint(50, 99)
            test_email = f"testuser{test_number}@test.com"
            
            response = requests.post(f"{BACKEND_URL}/auth/signup", json={
                "email": test_email,
                "password": ORIGINAL_TEST_PASSWORD,
                "full_name": f"Test User {test_number}"
            })
            
            if response.status_code == 200:
                data = response.json()
                test_user_id = data["user"]["user_id"]
                self.log_test("Create Test User", True, 
                            f"Created new test user: {test_email} (ID: {test_user_id})")
                return test_email, test_user_id
            else:
                self.log_test("Create Test User", False, 
                            f"Failed to create test user: {response.status_code} - {response.text}")
                return None, None
                
        except Exception as e:
            self.log_test("Find/Create Test User", False, f"Exception: {str(e)}")
            return None, None
    
    def test_admin_password_reset_endpoint(self, user_id, user_email):
        """Test the specific POST /api/admin/users/{user_id}/reset-password endpoint"""
        try:
            print(f"🔄 Testing admin password reset for user: {user_email}")
            
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            payload = {
                "reason": "Testing admin password reset functionality as per review requirements"
            }
            
            # Make the API call
            response = requests.post(
                f"{BACKEND_URL}/admin/users/{user_id}/reset-password",
                json=payload,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                temp_password = data.get("temporary_password")
                
                self.log_test("Admin Password Reset Endpoint", True, 
                            "POST /api/admin/users/{user_id}/reset-password endpoint working correctly",
                            {
                                "endpoint": f"/api/admin/users/{user_id}/reset-password",
                                "response": data,
                                "temporary_password": temp_password
                            })
                return temp_password
            else:
                self.log_test("Admin Password Reset Endpoint", False, 
                            f"Endpoint failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Admin Password Reset Endpoint", False, f"Exception: {str(e)}")
            return None
    
    def verify_password_hash_updated(self, user_email, original_password, temp_password):
        """Verify that password_hash field gets updated in database"""
        try:
            print("🔍 Verifying password hash was updated in database...")
            
            # Test 1: Original password should no longer work
            response1 = requests.post(f"{BACKEND_URL}/auth/login", json={
                "email": user_email,
                "password": original_password
            })
            original_blocked = (response1.status_code == 401)
            
            # Test 2: New temporary password should work
            response2 = requests.post(f"{BACKEND_URL}/auth/login", json={
                "email": user_email,
                "password": temp_password
            })
            temp_works = (response2.status_code == 200)
            
            if original_blocked and temp_works:
                self.log_test("Password Hash Updated in Database", True, 
                            "Database password_hash field successfully updated",
                            {
                                "original_password_blocked": original_blocked,
                                "temporary_password_works": temp_works,
                                "verification_method": "Login behavior analysis"
                            })
                return True
            else:
                self.log_test("Password Hash Updated in Database", False, 
                            f"Password hash update verification failed",
                            {
                                "original_password_blocked": original_blocked,
                                "temporary_password_works": temp_works
                            })
                return False
                
        except Exception as e:
            self.log_test("Password Hash Updated in Database", False, f"Exception: {str(e)}")
            return False
    
    def verify_temporary_password_generated(self, temp_password):
        """Verify that a temporary password is generated and returned"""
        try:
            if temp_password and len(temp_password) >= 8:
                # Check if it contains alphanumeric characters
                has_letters = any(c.isalpha() for c in temp_password)
                has_numbers = any(c.isdigit() for c in temp_password)
                
                self.log_test("Temporary Password Generated", True, 
                            "Temporary password successfully generated and returned",
                            {
                                "password_length": len(temp_password),
                                "contains_letters": has_letters,
                                "contains_numbers": has_numbers,
                                "password_format": "Alphanumeric"
                            })
                return True
            else:
                self.log_test("Temporary Password Generated", False, 
                            f"Invalid temporary password: {temp_password}")
                return False
                
        except Exception as e:
            self.log_test("Temporary Password Generated", False, f"Exception: {str(e)}")
            return False
    
    def verify_audit_log_entry(self, user_id):
        """Verify that audit log entry is created"""
        try:
            print("📝 Verifying audit log entry creation...")
            
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Get user audit history
            response = requests.get(
                f"{BACKEND_URL}/admin/users/{user_id}/audit",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                audit_entries = data.get("audit_history", [])
                
                # Look for recent password reset entries
                reset_entries = [
                    entry for entry in audit_entries 
                    if entry.get("action") == "reset_password"
                ]
                
                if reset_entries:
                    latest_entry = reset_entries[0]  # Most recent
                    self.log_test("Audit Log Entry Created", True, 
                                "Audit log entry successfully created for password reset",
                                {
                                    "audit_entry": latest_entry,
                                    "total_reset_entries": len(reset_entries),
                                    "total_audit_entries": len(audit_entries)
                                })
                    return True
                else:
                    self.log_test("Audit Log Entry Created", False, 
                                f"No password reset audit entries found. Total entries: {len(audit_entries)}")
                    return False
            else:
                self.log_test("Audit Log Entry Created", False, 
                            f"Cannot access audit logs: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Audit Log Entry Created", False, f"Exception: {str(e)}")
            return False
    
    def verify_user_can_login_with_new_password(self, user_email, temp_password):
        """Verify user can login with the new temporary password"""
        try:
            print("🔑 Verifying user can login with new temporary password...")
            
            response = requests.post(f"{BACKEND_URL}/auth/login", json={
                "email": user_email,
                "password": temp_password
            })
            
            if response.status_code == 200:
                data = response.json()
                user_data = data.get("user", {})
                
                self.log_test("User Login with New Password", True, 
                            "User successfully logged in with temporary password",
                            {
                                "login_response": user_data,
                                "user_id": user_data.get("user_id"),
                                "email": user_data.get("email")
                            })
                return True
            else:
                self.log_test("User Login with New Password", False, 
                            f"User cannot login with temporary password: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_test("User Login with New Password", False, f"Exception: {str(e)}")
            return False
    
    def run_comprehensive_test(self):
        """Run comprehensive admin password reset test covering all review requirements"""
        print("🚀 DETAILED ADMIN PASSWORD RESET FUNCTIONALITY TEST")
        print("=" * 70)
        print("Testing all requirements from the review request:")
        print("1. POST /api/admin/users/{user_id}/reset-password endpoint")
        print("2. Password_hash field gets updated in database")
        print("3. Temporary password is generated and returned")
        print("4. Audit log entry is created")
        print("5. User can login with new temporary password")
        print("6. Test with testuser1@test.com through testuser100@test.com pattern")
        print("=" * 70)
        print()
        
        # Step 1: Admin authentication
        if not self.admin_login():
            print("❌ Cannot proceed without admin authentication")
            return False
        
        # Step 2: Find or create test user
        user_email, user_id = self.find_or_create_test_user()
        if not user_email or not user_id:
            print("❌ Cannot proceed without test user")
            return False
        
        # Step 3: Test the admin password reset endpoint
        temp_password = self.test_admin_password_reset_endpoint(user_id, user_email)
        if not temp_password:
            print("❌ Core password reset endpoint failed")
            return False
        
        # Step 4: Verify temporary password was generated
        self.verify_temporary_password_generated(temp_password)
        
        # Step 5: Verify password hash was updated in database
        self.verify_password_hash_updated(user_email, ORIGINAL_TEST_PASSWORD, temp_password)
        
        # Step 6: Verify audit log entry was created
        self.verify_audit_log_entry(user_id)
        
        # Step 7: Verify user can login with new password
        self.verify_user_can_login_with_new_password(user_email, temp_password)
        
        # Print final summary
        self.print_final_summary()
        
        return True
    
    def print_final_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 70)
        print("📊 DETAILED ADMIN PASSWORD RESET TEST RESULTS")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"📈 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Passed: {passed_tests}")
        print(f"   ❌ Failed: {failed_tests}")
        print(f"   Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        print("🎯 REVIEW REQUIREMENTS VERIFICATION:")
        requirements = [
            ("POST /api/admin/users/{user_id}/reset-password endpoint", "Admin Password Reset Endpoint"),
            ("Password_hash field gets updated in database", "Password Hash Updated in Database"),
            ("Temporary password is generated and returned", "Temporary Password Generated"),
            ("Audit log entry is created", "Audit Log Entry Created"),
            ("User can login with new temporary password", "User Login with New Password")
        ]
        
        for requirement, test_name in requirements:
            result = next((r for r in self.test_results if r["test"] == test_name), None)
            if result:
                status = "✅ VERIFIED" if result["success"] else "❌ FAILED"
                print(f"   {status}: {requirement}")
            else:
                print(f"   ❓ NOT TESTED: {requirement}")
        
        print()
        
        if failed_tests > 0:
            print("🔍 FAILED TESTS DETAILS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   ❌ {result['test']}: {result['message']}")
            print()
        
        print("🏆 CONCLUSION:")
        if failed_tests == 0:
            print("   ✅ ALL ADMIN PASSWORD RESET REQUIREMENTS SUCCESSFULLY VERIFIED!")
            print("   ✅ The admin password reset functionality is working correctly.")
            print("   ✅ Database updates, audit logging, and authentication all functional.")
        else:
            print(f"   ⚠️  {failed_tests} requirement(s) failed verification.")
            print("   🔧 Review failed tests above for specific issues.")
        
        print("=" * 70)

if __name__ == "__main__":
    tester = DetailedAdminPasswordResetTester()
    tester.run_comprehensive_test()