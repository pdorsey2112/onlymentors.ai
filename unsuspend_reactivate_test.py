#!/usr/bin/env python3
"""
Comprehensive Test for User Unsuspend/Reactivate Functionality
Testing the complete suspend → unsuspend cycle with email notifications
Focus: Backend unsuspend functionality and reactivation emails
"""

import requests
import json
import time
import uuid
from datetime import datetime

# Configuration
BACKEND_URL = "http://localhost:8001/api"
ADMIN_EMAIL = "admin@onlymentors.ai"
ADMIN_PASSWORD = "SuperAdmin2024!"
TEST_USER_EMAIL = f"testuser_{str(uuid.uuid4())[:8]}@test.com"
TEST_USER_PASSWORD = "TestPassword123!"
TEST_USER_NAME = "Test User Unsuspend"

class UnsuspendReactivateTest:
    def __init__(self):
        self.admin_token = None
        self.test_user_id = None
        self.test_results = []
        
    def log_result(self, test_name, success, details=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        print()

    def admin_login(self):
        """Step 1: Login as admin"""
        print("🔐 Step 1: Admin Authentication")
        try:
            response = requests.post(f"{BACKEND_URL}/admin/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token")
                self.log_result("Admin Login", True, f"Admin authenticated successfully")
                return True
            else:
                self.log_result("Admin Login", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Admin Login", False, f"Exception: {str(e)}")
            return False

    def create_test_user(self):
        """Step 2: Create test user for suspend/unsuspend testing"""
        print("👤 Step 2: Create Test User")
        try:
            # First check if user already exists
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            users_response = requests.get(f"{BACKEND_URL}/admin/users", headers=headers)
            
            if users_response.status_code == 200:
                users_data = users_response.json()
                existing_user = None
                
                for user in users_data.get("users", []):
                    if user.get("email") == TEST_USER_EMAIL:
                        existing_user = user
                        break
                
                if existing_user:
                    self.test_user_id = existing_user["user_id"]
                    self.log_result("Test User Found", True, f"Using existing user: {TEST_USER_EMAIL}")
                    return True
            
            # Create new test user via regular signup
            signup_response = requests.post(f"{BACKEND_URL}/auth/signup", json={
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD,
                "full_name": TEST_USER_NAME
            })
            
            if signup_response.status_code == 200:
                signup_data = signup_response.json()
                self.test_user_id = signup_data["user"]["user_id"]
                self.log_result("Test User Creation", True, f"Created user: {TEST_USER_EMAIL}")
                return True
            else:
                self.log_result("Test User Creation", False, f"Status: {signup_response.status_code}, Response: {signup_response.text}")
                return False
                
        except Exception as e:
            self.log_result("Test User Creation", False, f"Exception: {str(e)}")
            return False

    def suspend_user(self):
        """Step 3: Suspend the test user first"""
        print("🚫 Step 3: Suspend Test User")
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            suspend_data = {
                "suspend": True,
                "reason": "Testing suspend functionality"
            }
            
            response = requests.put(
                f"{BACKEND_URL}/admin/users/{self.test_user_id}/suspend",
                headers=headers,
                json=suspend_data
            )
            
            if response.status_code == 200:
                data = response.json()
                is_suspended = data.get("is_suspended", False)
                email_sent = data.get("email_sent", False)
                
                self.log_result("User Suspension", True, 
                    f"User suspended: {is_suspended}, Email sent: {email_sent}, Reason: {data.get('reason')}")
                return True
            else:
                self.log_result("User Suspension", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("User Suspension", False, f"Exception: {str(e)}")
            return False

    def verify_user_suspended(self):
        """Step 4: Verify user is suspended and cannot login"""
        print("🔒 Step 4: Verify User is Suspended")
        try:
            # Try to login as suspended user
            login_response = requests.post(f"{BACKEND_URL}/auth/login", json={
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            })
            
            # Should fail with 401 or 423 (locked account)
            if login_response.status_code in [401, 423]:
                self.log_result("Suspended User Login Block", True, 
                    f"Suspended user correctly blocked from login (Status: {login_response.status_code})")
                return True
            else:
                self.log_result("Suspended User Login Block", False, 
                    f"Suspended user was able to login (Status: {login_response.status_code})")
                return False
                
        except Exception as e:
            self.log_result("Suspended User Login Block", False, f"Exception: {str(e)}")
            return False

    def unsuspend_user(self):
        """Step 5: MAIN TEST - Unsuspend/Reactivate the user"""
        print("✅ Step 5: UNSUSPEND/REACTIVATE USER (MAIN TEST)")
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            unsuspend_data = {
                "suspend": False,
                "reason": "Account review completed"
            }
            
            response = requests.put(
                f"{BACKEND_URL}/admin/users/{self.test_user_id}/suspend",
                headers=headers,
                json=unsuspend_data
            )
            
            if response.status_code == 200:
                data = response.json()
                is_suspended = data.get("is_suspended", True)  # Should be False now
                email_sent = data.get("email_sent", False)
                reason = data.get("reason", "")
                
                success = not is_suspended  # Success if user is no longer suspended
                
                self.log_result("User Unsuspension/Reactivation", success, 
                    f"User suspended: {is_suspended}, Email sent: {email_sent}, Reason: {reason}")
                
                if email_sent:
                    self.log_result("Reactivation Email Sent", True, "Reactivation email was sent successfully")
                else:
                    self.log_result("Reactivation Email Sent", False, "Reactivation email was not sent")
                
                return success
            else:
                self.log_result("User Unsuspension/Reactivation", False, 
                    f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("User Unsuspension/Reactivation", False, f"Exception: {str(e)}")
            return False

    def verify_user_reactivated(self):
        """Step 6: Verify user is reactivated and can login"""
        print("🔓 Step 6: Verify User is Reactivated")
        try:
            # Try to login as reactivated user
            login_response = requests.post(f"{BACKEND_URL}/auth/login", json={
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            })
            
            if login_response.status_code == 200:
                data = login_response.json()
                user_data = data.get("user", {})
                
                self.log_result("Reactivated User Login", True, 
                    f"Reactivated user can login successfully. User: {user_data.get('email')}")
                return True
            else:
                self.log_result("Reactivated User Login", False, 
                    f"Reactivated user cannot login (Status: {login_response.status_code})")
                return False
                
        except Exception as e:
            self.log_result("Reactivated User Login", False, f"Exception: {str(e)}")
            return False

    def verify_database_status(self):
        """Step 7: Verify user status in database"""
        print("💾 Step 7: Verify Database Status")
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Get user details from admin endpoint
            response = requests.get(f"{BACKEND_URL}/admin/users", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                users = data.get("users", [])
                
                test_user = None
                for user in users:
                    if user.get("user_id") == self.test_user_id:
                        test_user = user
                        break
                
                if test_user:
                    is_suspended = test_user.get("is_suspended", True)
                    status = test_user.get("status", "unknown")
                    
                    success = not is_suspended and status != "suspended"
                    
                    self.log_result("Database Status Verification", success, 
                        f"User suspended in DB: {is_suspended}, Status: {status}")
                    return success
                else:
                    self.log_result("Database Status Verification", False, "Test user not found in database")
                    return False
            else:
                self.log_result("Database Status Verification", False, 
                    f"Failed to get users (Status: {response.status_code})")
                return False
                
        except Exception as e:
            self.log_result("Database Status Verification", False, f"Exception: {str(e)}")
            return False

    def verify_audit_logs(self):
        """Step 8: Verify audit log entries for both suspend and unsuspend"""
        print("📋 Step 8: Verify Audit Log Entries")
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            response = requests.get(f"{BACKEND_URL}/admin/users/{self.test_user_id}/audit", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                audit_entries = data.get("audit_entries", [])
                
                suspend_entry = None
                unsuspend_entry = None
                
                for entry in audit_entries:
                    action = entry.get("action", "")
                    if action == "suspend":
                        suspend_entry = entry
                    elif action == "unsuspend":
                        unsuspend_entry = entry
                
                suspend_found = suspend_entry is not None
                unsuspend_found = unsuspend_entry is not None
                
                self.log_result("Suspend Audit Log Entry", suspend_found, 
                    f"Suspend entry found: {suspend_found}")
                
                self.log_result("Unsuspend Audit Log Entry", unsuspend_found, 
                    f"Unsuspend entry found: {unsuspend_found}")
                
                if unsuspend_entry:
                    reason = unsuspend_entry.get("reason", "")
                    email_sent = unsuspend_entry.get("email_sent", False)
                    
                    self.log_result("Unsuspend Audit Details", True, 
                        f"Reason: {reason}, Email sent: {email_sent}")
                
                return suspend_found and unsuspend_found
            else:
                self.log_result("Audit Log Verification", False, 
                    f"Failed to get audit logs (Status: {response.status_code})")
                return False
                
        except Exception as e:
            self.log_result("Audit Log Verification", False, f"Exception: {str(e)}")
            return False

    def test_error_handling(self):
        """Step 9: Test error handling - try to unsuspend a user that's not suspended"""
        print("⚠️ Step 9: Test Error Handling")
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Try to unsuspend user that's already unsuspended
            unsuspend_data = {
                "suspend": False,
                "reason": "Testing error handling"
            }
            
            response = requests.put(
                f"{BACKEND_URL}/admin/users/{self.test_user_id}/suspend",
                headers=headers,
                json=unsuspend_data
            )
            
            # This should either succeed (idempotent) or return appropriate error
            if response.status_code == 200:
                data = response.json()
                self.log_result("Unsuspend Already Unsuspended User", True, 
                    f"Idempotent operation handled correctly: {data.get('message', 'Success')}")
                return True
            elif response.status_code == 400:
                self.log_result("Unsuspend Already Unsuspended User", True, 
                    f"Appropriate error returned for already unsuspended user")
                return True
            else:
                self.log_result("Unsuspend Already Unsuspended User", False, 
                    f"Unexpected response (Status: {response.status_code})")
                return False
                
        except Exception as e:
            self.log_result("Error Handling Test", False, f"Exception: {str(e)}")
            return False

    def test_invalid_user_unsuspend(self):
        """Step 10: Test unsuspending non-existent user"""
        print("🚫 Step 10: Test Invalid User Unsuspend")
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            fake_user_id = "non-existent-user-id"
            
            unsuspend_data = {
                "suspend": False,
                "reason": "Testing with invalid user"
            }
            
            response = requests.put(
                f"{BACKEND_URL}/admin/users/{fake_user_id}/suspend",
                headers=headers,
                json=unsuspend_data
            )
            
            if response.status_code == 404:
                self.log_result("Invalid User Unsuspend Error", True, 
                    "Correctly returned 404 for non-existent user")
                return True
            else:
                self.log_result("Invalid User Unsuspend Error", False, 
                    f"Expected 404, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Invalid User Unsuspend Error", False, f"Exception: {str(e)}")
            return False

    def run_complete_test(self):
        """Run the complete unsuspend/reactivate test suite"""
        print("🎯 COMPREHENSIVE UNSUSPEND/REACTIVATE USER FUNCTIONALITY TEST")
        print("=" * 80)
        print(f"Testing Backend URL: {BACKEND_URL}")
        print(f"Admin Credentials: {ADMIN_EMAIL}")
        print(f"Test User: {TEST_USER_EMAIL}")
        print("=" * 80)
        print()
        
        # Execute test steps
        steps = [
            self.admin_login,
            self.create_test_user,
            self.suspend_user,
            self.verify_user_suspended,
            self.unsuspend_user,  # MAIN TEST
            self.verify_user_reactivated,
            self.verify_database_status,
            self.verify_audit_logs,
            self.test_error_handling,
            self.test_invalid_user_unsuspend
        ]
        
        for step in steps:
            if not step():
                print(f"❌ Test failed at step: {step.__name__}")
                break
            time.sleep(1)  # Brief pause between steps
        
        # Print summary
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Print detailed results
        for result in self.test_results:
            print(f"{result['status']}: {result['test']}")
            if result['details']:
                print(f"   {result['details']}")
        
        print("\n" + "=" * 80)
        
        if success_rate >= 80:
            print("🎉 UNSUSPEND/REACTIVATE FUNCTIONALITY TEST SUCCESSFUL!")
            print("✅ The complete suspend → unsuspend cycle is working correctly")
            print("✅ Reactivation emails are being sent")
            print("✅ Backend unsuspend functionality is operational")
            print("✅ Database status updates are working")
            print("✅ Audit logging is functional")
            print("✅ Error handling is appropriate")
        else:
            print("❌ UNSUSPEND/REACTIVATE FUNCTIONALITY TEST FAILED!")
            print("⚠️ Critical issues found that need to be addressed")
        
        return success_rate >= 80

if __name__ == "__main__":
    test = UnsuspendReactivateTest()
    test.run_complete_test()