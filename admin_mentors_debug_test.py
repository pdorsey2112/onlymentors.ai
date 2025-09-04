#!/usr/bin/env python3
"""
Admin Console Mentors Endpoint Debug Test
Debug why admin console still shows 0 mentors after fix
"""

import requests
import json
import time
import uuid
from datetime import datetime

# Configuration
BASE_URL = "https://multi-tenant-ai.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@onlymentors.ai"
ADMIN_PASSWORD = "SuperAdmin2024!"

class AdminMentorsDebugTester:
    def __init__(self):
        self.admin_token = None
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
        if response_data and not success:
            print(f"   Response: {response_data}")
        print()

    def test_admin_authentication(self):
        """Test admin authentication"""
        print("🔐 Testing Admin Authentication...")
        
        login_data = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        
        try:
            response = requests.post(f"{BASE_URL}/admin/login", json=login_data)
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token")
                admin_info = data.get("admin", {})
                self.log_result("Admin Authentication", True, 
                              f"Admin ID: {admin_info.get('admin_id')}, Role: {admin_info.get('role')}")
                return True
            else:
                self.log_result("Admin Authentication", False, 
                              f"Status: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Exception: {str(e)}")
            return False

    def test_backend_service_status(self):
        """Test if backend service is running properly"""
        print("🔧 Testing Backend Service Status...")
        
        try:
            # Test basic API health
            response = requests.get(f"{BASE_URL.replace('/api', '')}")
            if response.status_code == 200:
                data = response.json()
                self.log_result("Backend Service Health", True, 
                              f"API Version: {data.get('version')}, Total Mentors: {data.get('total_mentors')}")
            else:
                self.log_result("Backend Service Health", False, 
                              f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Backend Service Health", False, f"Exception: {str(e)}")

    def test_database_mentor_count(self):
        """Test how many mentors exist in the database via search API"""
        print("📊 Testing Database Mentor Count...")
        
        try:
            # Test search API to see total mentors
            response = requests.get(f"{BASE_URL}/search/mentors?mentor_type=all")
            if response.status_code == 200:
                data = response.json()
                total_count = data.get("count", 0)
                ai_count = data.get("ai_count", 0)
                human_count = data.get("human_count", 0)
                
                self.log_result("Database Mentor Count", True, 
                              f"Total: {total_count}, AI: {ai_count}, Human: {human_count}")
                
                # Test human mentors specifically
                human_response = requests.get(f"{BASE_URL}/search/mentors?mentor_type=human")
                if human_response.status_code == 200:
                    human_data = human_response.json()
                    human_mentors = human_data.get("results", [])
                    self.log_result("Human Mentors in Search", True, 
                                  f"Found {len(human_mentors)} human mentors")
                    
                    # Show first few human mentors for debugging
                    if human_mentors:
                        for i, mentor in enumerate(human_mentors[:3]):
                            print(f"   Human Mentor {i+1}: {mentor.get('name')} (ID: {mentor.get('id')})")
                else:
                    self.log_result("Human Mentors in Search", False, 
                                  f"Status: {human_response.status_code}")
            else:
                self.log_result("Database Mentor Count", False, 
                              f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Database Mentor Count", False, f"Exception: {str(e)}")

    def test_admin_mentors_endpoint_direct(self):
        """Test admin mentors endpoint directly"""
        print("🎯 Testing Admin Mentors Endpoint Directly...")
        
        if not self.admin_token:
            self.log_result("Admin Mentors Endpoint - No Token", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            # Test without parameters
            response = requests.get(f"{BASE_URL}/admin/mentors", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                mentors = data.get("mentors", [])
                total_count = data.get("total", 0)
                
                self.log_result("Admin Mentors Endpoint - Basic Call", True, 
                              f"Returned {len(mentors)} mentors, Total: {total_count}")
                
                # Show first few mentors for debugging
                if mentors:
                    print("   First few mentors:")
                    for i, mentor in enumerate(mentors[:3]):
                        print(f"   Mentor {i+1}: {mentor.get('full_name', 'N/A')} (ID: {mentor.get('creator_id', 'N/A')})")
                        print(f"      Email: {mentor.get('email', 'N/A')}")
                        print(f"      Category: {mentor.get('category', 'N/A')}")
                        print(f"      Status: {mentor.get('status', 'N/A')}")
                        print(f"      Verification: {mentor.get('verification', 'N/A')}")
                else:
                    print("   ⚠️ No mentors returned!")
                    
            else:
                self.log_result("Admin Mentors Endpoint - Basic Call", False, 
                              f"Status: {response.status_code}", response.text)
                
        except Exception as e:
            self.log_result("Admin Mentors Endpoint - Basic Call", False, f"Exception: {str(e)}")

    def test_admin_mentors_with_pagination(self):
        """Test admin mentors endpoint with pagination"""
        print("📄 Testing Admin Mentors Endpoint with Pagination...")
        
        if not self.admin_token:
            self.log_result("Admin Mentors Pagination - No Token", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            # Test with pagination parameters
            response = requests.get(f"{BASE_URL}/admin/mentors?page=1&limit=10", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                mentors = data.get("mentors", [])
                total_count = data.get("total", 0)
                page = data.get("page", 0)
                limit = data.get("limit", 0)
                
                self.log_result("Admin Mentors Pagination", True, 
                              f"Page {page}, Limit {limit}, Returned {len(mentors)}, Total: {total_count}")
            else:
                self.log_result("Admin Mentors Pagination", False, 
                              f"Status: {response.status_code}", response.text)
                
        except Exception as e:
            self.log_result("Admin Mentors Pagination", False, f"Exception: {str(e)}")

    def test_admin_mentors_with_search(self):
        """Test admin mentors endpoint with search"""
        print("🔍 Testing Admin Mentors Endpoint with Search...")
        
        if not self.admin_token:
            self.log_result("Admin Mentors Search - No Token", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            # Test with search parameter
            response = requests.get(f"{BASE_URL}/admin/mentors?search=mentor", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                mentors = data.get("mentors", [])
                total_count = data.get("total", 0)
                
                self.log_result("Admin Mentors Search", True, 
                              f"Search 'mentor' returned {len(mentors)} mentors, Total: {total_count}")
            else:
                self.log_result("Admin Mentors Search", False, 
                              f"Status: {response.status_code}", response.text)
                
        except Exception as e:
            self.log_result("Admin Mentors Search", False, f"Exception: {str(e)}")

    def test_response_format_validation(self):
        """Test if admin mentors response format matches frontend expectations"""
        print("📋 Testing Response Format Validation...")
        
        if not self.admin_token:
            self.log_result("Response Format Validation - No Token", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = requests.get(f"{BASE_URL}/admin/mentors", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check required fields in response
                required_fields = ["mentors", "total", "page", "limit"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    mentors = data.get("mentors", [])
                    if mentors:
                        # Check required fields in mentor objects
                        mentor_required_fields = ["creator_id", "full_name", "email", "category", "status", "verification"]
                        first_mentor = mentors[0]
                        missing_mentor_fields = [field for field in mentor_required_fields if field not in first_mentor]
                        
                        if not missing_mentor_fields:
                            self.log_result("Response Format Validation", True, 
                                          f"Response format is correct. Sample mentor has all required fields.")
                        else:
                            self.log_result("Response Format Validation", False, 
                                          f"Mentor objects missing fields: {missing_mentor_fields}")
                    else:
                        self.log_result("Response Format Validation", True, 
                                      "Response format is correct but no mentors returned")
                else:
                    self.log_result("Response Format Validation", False, 
                                  f"Response missing required fields: {missing_fields}")
            else:
                self.log_result("Response Format Validation", False, 
                              f"Status: {response.status_code}", response.text)
                
        except Exception as e:
            self.log_result("Response Format Validation", False, f"Exception: {str(e)}")

    def test_create_test_mentor(self):
        """Create a test mentor to ensure there's at least one mentor in the system"""
        print("👤 Creating Test Mentor...")
        
        # First try to register a new user who becomes a mentor
        test_user_data = {
            "email": f"testmentor_{int(time.time())}@test.com",
            "password": "TestPass123!",
            "full_name": "Test Mentor User",
            "phone_number": "+1234567890",
            "communication_preferences": '{"email": true}',
            "subscription_plan": "free",
            "become_mentor": True
        }
        
        try:
            response = requests.post(f"{BASE_URL}/auth/register", data=test_user_data)
            
            if response.status_code == 200:
                data = response.json()
                user_info = data.get("user", {})
                is_mentor = user_info.get("is_mentor", False)
                
                self.log_result("Create Test Mentor", True, 
                              f"Created user-mentor: {user_info.get('full_name')}, Is Mentor: {is_mentor}")
                
                # Wait a moment for database consistency
                time.sleep(2)
                
                # Now test if this mentor appears in admin console
                if self.admin_token:
                    headers = {"Authorization": f"Bearer {self.admin_token}"}
                    admin_response = requests.get(f"{BASE_URL}/admin/mentors", headers=headers)
                    
                    if admin_response.status_code == 200:
                        admin_data = admin_response.json()
                        mentors = admin_data.get("mentors", [])
                        
                        # Look for our test mentor
                        test_mentor_found = any(
                            mentor.get("email") == test_user_data["email"] 
                            for mentor in mentors
                        )
                        
                        if test_mentor_found:
                            self.log_result("Test Mentor in Admin Console", True, 
                                          "Newly created mentor appears in admin console")
                        else:
                            self.log_result("Test Mentor in Admin Console", False, 
                                          f"Newly created mentor NOT found in admin console. Total mentors: {len(mentors)}")
                
            else:
                self.log_result("Create Test Mentor", False, 
                              f"Status: {response.status_code}", response.text)
                
        except Exception as e:
            self.log_result("Create Test Mentor", False, f"Exception: {str(e)}")

    def run_debug_tests(self):
        """Run all debug tests for admin mentors endpoint"""
        print("🚀 Starting Admin Console Mentors Endpoint Debug Testing")
        print("=" * 70)
        
        # Test sequence
        self.test_backend_service_status()
        self.test_admin_authentication()
        self.test_database_mentor_count()
        self.test_admin_mentors_endpoint_direct()
        self.test_admin_mentors_with_pagination()
        self.test_admin_mentors_with_search()
        self.test_response_format_validation()
        self.test_create_test_mentor()
        
        # Summary
        self.print_debug_summary()

    def print_debug_summary(self):
        """Print debug test summary"""
        print("\n" + "=" * 70)
        print("🔍 ADMIN MENTORS ENDPOINT DEBUG SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print()
        
        # Show all results
        for result in self.results:
            print(f"{result['status']}: {result['test']}")
            if result['details']:
                print(f"   {result['details']}")
        print()
        
        # Critical findings
        critical_issues = []
        
        # Check for authentication issues
        auth_failed = any(not r["success"] and "Authentication" in r["test"] for r in self.results)
        if auth_failed:
            critical_issues.append("❌ Admin authentication is failing")
        
        # Check for endpoint issues
        endpoint_failed = any(not r["success"] and "Admin Mentors Endpoint" in r["test"] for r in self.results)
        if endpoint_failed:
            critical_issues.append("❌ Admin mentors endpoint is returning errors")
        
        # Check for data issues
        no_mentors = any("0 mentors" in r["details"] or "No mentors returned" in r["details"] for r in self.results)
        if no_mentors:
            critical_issues.append("⚠️ Admin console shows 0 mentors despite mentors existing in search")
        
        if critical_issues:
            print("🚨 CRITICAL FINDINGS:")
            for issue in critical_issues:
                print(f"   {issue}")
            print()
        
        # Recommendations
        print("💡 RECOMMENDATIONS:")
        
        if auth_failed:
            print("   1. Check admin credentials and JWT token generation")
        
        if endpoint_failed:
            print("   2. Check admin mentors endpoint implementation for errors")
            print("   3. Verify database connection and query logic")
        
        if no_mentors:
            print("   4. Check data structure mismatch between search API and admin API")
            print("   5. Verify admin endpoint is querying the correct collection (creators)")
            print("   6. Check if admin endpoint has different filtering logic than search API")
        
        print("   7. Check backend logs for detailed error messages")
        print("   8. Verify service restart completed successfully")
        
        print("=" * 70)

if __name__ == "__main__":
    tester = AdminMentorsDebugTester()
    tester.run_debug_tests()