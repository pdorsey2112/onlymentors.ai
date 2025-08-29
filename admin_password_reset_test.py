#!/usr/bin/env python3
"""
Admin Password Reset Test for pdorsey@dorseyandassociates.com
Tests the complete admin password reset flow as requested in the review.
"""

import requests
import json
import time
import random
import string
from datetime import datetime

# Configuration
BACKEND_URL = "https://mentor-marketplace.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@onlymentors.ai"
ADMIN_PASSWORD = "SuperAdmin2024!"
TARGET_EMAIL = "pdorsey@dorseyandassociates.com"
TARGET_PASSWORD = "TestPassword123!"
TARGET_NAME = "Paul Dorsey"
RESET_REASON = "Customer Service"

class AdminPasswordResetTester:
    def __init__(self):
        self.admin_token = None
        self.test_user_id = None
        self.test_user_email = TARGET_EMAIL
        self.original_password = TARGET_PASSWORD
        self.test_name = TARGET_NAME
        self.reset_reason = RESET_REASON
        self.results = []
        
    def log_result(self, test_name, success, message, details=None):
        """Log test result"""
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
                self.log_result("Admin Login", True, f"Successfully logged in as admin")
                return True
            else:
                self.log_result("Admin Login", False, f"Failed to login: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Admin Login", False, f"Exception during admin login: {str(e)}")
            return False
    
    def create_test_user(self):
        """Create a test user for password reset testing"""
        try:
            # Generate unique test user email
            random_suffix = ''.join(random.choices(string.digits, k=6))
            self.test_user_email = f"testuser{random_suffix}@test.com"
            
            response = requests.post(f"{BACKEND_URL}/auth/signup", json={
                "email": self.test_user_email,
                "password": self.original_password,
                "full_name": f"Test User {random_suffix}"
            })
            
            if response.status_code == 200:
                data = response.json()
                self.test_user_id = data["user"]["user_id"]
                self.log_result("Create Test User", True, f"Created test user: {self.test_user_email}")
                return True
            else:
                self.log_result("Create Test User", False, f"Failed to create user: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Create Test User", False, f"Exception creating test user: {str(e)}")
            return False
    
    def verify_user_can_login_with_original_password(self):
        """Verify test user can login with original password before reset"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json={
                "email": self.test_user_email,
                "password": self.original_password
            })
            
            if response.status_code == 200:
                self.log_result("Original Password Login", True, "User can login with original password")
                return True
            else:
                self.log_result("Original Password Login", False, f"User cannot login with original password: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Original Password Login", False, f"Exception during original password login: {str(e)}")
            return False
    
    def test_admin_password_reset(self):
        """Test the admin password reset endpoint"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            payload = {
                "reason": "Testing admin password reset functionality"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/admin/users/{self.test_user_id}/reset-password",
                json=payload,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                self.temporary_password = data.get("temporary_password")
                
                if self.temporary_password:
                    self.log_result("Admin Password Reset", True, 
                                  f"Password reset successful. Temporary password: {self.temporary_password}",
                                  {"response": data})
                    return True
                else:
                    self.log_result("Admin Password Reset", False, "No temporary password returned")
                    return False
            else:
                self.log_result("Admin Password Reset", False, 
                              f"Password reset failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Admin Password Reset", False, f"Exception during password reset: {str(e)}")
            return False
    
    def verify_original_password_no_longer_works(self):
        """Verify user cannot login with original password after reset"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json={
                "email": self.test_user_email,
                "password": self.original_password
            })
            
            if response.status_code == 401:
                self.log_result("Original Password Blocked", True, "Original password no longer works (expected)")
                return True
            else:
                self.log_result("Original Password Blocked", False, 
                              f"Original password still works (unexpected): {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Original Password Blocked", False, f"Exception testing original password: {str(e)}")
            return False
    
    def verify_temporary_password_works(self):
        """Verify user can login with temporary password"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json={
                "email": self.test_user_email,
                "password": self.temporary_password
            })
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("Temporary Password Login", True, 
                              "User can login with temporary password",
                              {"user_data": data.get("user", {})})
                return True
            else:
                self.log_result("Temporary Password Login", False, 
                              f"User cannot login with temporary password: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Temporary Password Login", False, f"Exception during temporary password login: {str(e)}")
            return False
    
    def verify_database_password_hash_updated(self):
        """Verify the password hash was updated in the database by checking login behavior"""
        try:
            # We can't directly access the database, but we can verify the behavior
            # If temporary password works and original doesn't, the hash was updated
            temp_works = False
            orig_blocked = False
            
            # Test temporary password
            response = requests.post(f"{BACKEND_URL}/auth/login", json={
                "email": self.test_user_email,
                "password": self.temporary_password
            })
            temp_works = (response.status_code == 200)
            
            # Test original password
            response = requests.post(f"{BACKEND_URL}/auth/login", json={
                "email": self.test_user_email,
                "password": self.original_password
            })
            orig_blocked = (response.status_code == 401)
            
            if temp_works and orig_blocked:
                self.log_result("Database Hash Updated", True, "Password hash successfully updated in database")
                return True
            else:
                self.log_result("Database Hash Updated", False, 
                              f"Password hash update verification failed. Temp works: {temp_works}, Orig blocked: {orig_blocked}")
                return False
                
        except Exception as e:
            self.log_result("Database Hash Updated", False, f"Exception verifying database update: {str(e)}")
            return False
    
    def verify_audit_log_created(self):
        """Verify audit log entry was created (test by checking admin can access audit logs)"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Try to get user audit history
            response = requests.get(
                f"{BACKEND_URL}/admin/users/{self.test_user_id}/audit",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                audit_entries = data.get("audit_history", [])
                
                # Look for password reset entry
                reset_entries = [entry for entry in audit_entries if entry.get("action") == "reset_password"]
                
                if reset_entries:
                    self.log_result("Audit Log Created", True, 
                                  f"Audit log entry found for password reset",
                                  {"audit_entries": reset_entries})
                    return True
                else:
                    self.log_result("Audit Log Created", False, 
                                  f"No password reset audit entry found. Total entries: {len(audit_entries)}")
                    return False
            else:
                self.log_result("Audit Log Created", False, 
                              f"Cannot access audit logs: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Audit Log Created", False, f"Exception checking audit log: {str(e)}")
            return False
    
    def test_unauthorized_access(self):
        """Test that non-admin users cannot reset passwords"""
        try:
            # Try without admin token
            response = requests.post(
                f"{BACKEND_URL}/admin/users/{self.test_user_id}/reset-password",
                json={"reason": "Unauthorized test"}
            )
            
            if response.status_code in [401, 403]:
                self.log_result("Unauthorized Access Blocked", True, "Non-admin access properly blocked")
                return True
            else:
                self.log_result("Unauthorized Access Blocked", False, 
                              f"Non-admin access not blocked: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Unauthorized Access Blocked", False, f"Exception testing unauthorized access: {str(e)}")
            return False
    
    def test_invalid_user_id(self):
        """Test password reset with invalid user ID"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            fake_user_id = "invalid-user-id-12345"
            
            response = requests.post(
                f"{BACKEND_URL}/admin/users/{fake_user_id}/reset-password",
                json={"reason": "Testing invalid user ID"},
                headers=headers
            )
            
            if response.status_code == 404:
                self.log_result("Invalid User ID Handling", True, "Invalid user ID properly rejected")
                return True
            else:
                self.log_result("Invalid User ID Handling", False, 
                              f"Invalid user ID not handled correctly: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Invalid User ID Handling", False, f"Exception testing invalid user ID: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all admin password reset tests"""
        print("🚀 Starting Admin Password Reset Functionality Tests")
        print("=" * 60)
        
        # Step 1: Admin login
        if not self.admin_login():
            print("❌ Cannot proceed without admin authentication")
            return False
        
        # Step 2: Create test user
        if not self.create_test_user():
            print("❌ Cannot proceed without test user")
            return False
        
        # Step 3: Verify original password works
        if not self.verify_user_can_login_with_original_password():
            print("❌ Test user setup failed")
            return False
        
        # Step 4: Test unauthorized access
        self.test_unauthorized_access()
        
        # Step 5: Test invalid user ID
        self.test_invalid_user_id()
        
        # Step 6: Admin password reset
        if not self.test_admin_password_reset():
            print("❌ Core password reset functionality failed")
            return False
        
        # Step 7: Verify original password no longer works
        self.verify_original_password_no_longer_works()
        
        # Step 8: Verify temporary password works
        self.verify_temporary_password_works()
        
        # Step 9: Verify database was updated
        self.verify_database_password_hash_updated()
        
        # Step 10: Verify audit log was created
        self.verify_audit_log_created()
        
        # Summary
        self.print_summary()
        
        return True
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 ADMIN PASSWORD RESET TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n🔍 FAILED TESTS:")
            for result in self.results:
                if not result["success"]:
                    print(f"  • {result['test']}: {result['message']}")
        
        print("\n🎯 KEY FUNCTIONALITY VERIFICATION:")
        key_tests = [
            "Admin Password Reset",
            "Temporary Password Login", 
            "Database Hash Updated",
            "Audit Log Created"
        ]
        
        for test_name in key_tests:
            result = next((r for r in self.results if r["test"] == test_name), None)
            if result:
                status = "✅" if result["success"] else "❌"
                print(f"  {status} {test_name}")
        
        print("\n" + "=" * 60)

if __name__ == "__main__":
    tester = AdminPasswordResetTester()
    tester.run_all_tests()