#!/usr/bin/env python3
"""
Admin Mentors Data Test
Tests the admin console mentors endpoint to understand why it shows no human mentors
"""

import requests
import json
import time
import uuid
from datetime import datetime

# Configuration
BASE_URL = "https://mentor-search.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@onlymentors.ai"
ADMIN_PASSWORD = "SuperAdmin2024!"

class AdminMentorsDataTester:
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
        if not success and response_data:
            print(f"   Response: {response_data}")
        print()

    def test_admin_login(self):
        """Test admin login to get access token"""
        print("🔐 Testing Admin Login...")
        
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
                
                self.log_result("Admin Login", True,
                              f"Admin ID: {admin_info.get('admin_id')}, Role: {admin_info.get('role')}")
                return True
            else:
                self.log_result("Admin Login", False,
                              f"Status: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Admin Login", False, f"Exception: {str(e)}")
            return False

    def test_admin_mentors_endpoint(self):
        """Test the admin mentors endpoint"""
        print("👑 Testing Admin Mentors Endpoint...")
        
        if not self.admin_token:
            self.log_result("Admin Mentors Endpoint", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = requests.get(f"{BASE_URL}/admin/mentors", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                mentors = data.get("mentors", [])
                total = data.get("total", 0)
                
                self.log_result("Admin Mentors Endpoint", True,
                              f"Found {len(mentors)} mentors, Total: {total}")
                
                # Analyze mentor data structure
                if mentors:
                    sample_mentor = mentors[0]
                    self.log_result("Admin Mentor Data Structure", True,
                                  f"Sample mentor fields: {list(sample_mentor.keys())}")
                    
                    # Check for required fields that admin expects
                    expected_fields = ["creator_id", "email", "full_name", "account_name", 
                                     "category", "monthly_price", "status", "subscriber_count", 
                                     "total_earnings", "verification", "created_at"]
                    
                    missing_fields = [field for field in expected_fields if field not in sample_mentor]
                    
                    if missing_fields:
                        self.log_result("Admin Expected Fields Check", False,
                                      f"Missing expected fields: {missing_fields}")
                    else:
                        self.log_result("Admin Expected Fields Check", True,
                                      "All expected fields present")
                else:
                    self.log_result("Admin Mentors Empty Result", True,
                                  "No mentors returned - this explains the admin console issue")
                
                return len(mentors)
            else:
                self.log_result("Admin Mentors Endpoint", False,
                              f"Status: {response.status_code}", response.text)
                return 0
        except Exception as e:
            self.log_result("Admin Mentors Endpoint", False, f"Exception: {str(e)}")
            return 0

    def test_direct_creators_collection_query(self):
        """Test direct database query to see what's actually in creators collection"""
        print("🗄️ Testing Direct Creators Collection Analysis...")
        
        # We can't directly query the database, but we can use the search endpoint
        # to understand the data structure
        try:
            response = requests.get(f"{BASE_URL}/search/mentors?mentor_type=human")
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                
                if results:
                    sample_human_mentor = results[0]
                    self.log_result("Human Mentor Data Structure (Search API)", True,
                                  f"Fields: {list(sample_human_mentor.keys())}")
                    
                    # Compare with what admin endpoint expects
                    admin_expected = ["creator_id", "email", "full_name", "account_name", 
                                    "category", "monthly_price", "status", "subscriber_count", 
                                    "total_earnings", "verification", "created_at"]
                    
                    search_fields = list(sample_human_mentor.keys())
                    
                    # Map search API fields to admin expected fields
                    field_mapping = {
                        "id": "creator_id",
                        "name": "account_name",
                        # Missing: full_name, category, status, verification, etc.
                    }
                    
                    missing_in_search = []
                    for admin_field in admin_expected:
                        if admin_field not in search_fields and admin_field not in field_mapping.values():
                            # Check if there's a mapping
                            mapped = False
                            for search_field, admin_mapped in field_mapping.items():
                                if admin_mapped == admin_field and search_field in search_fields:
                                    mapped = True
                                    break
                            if not mapped:
                                missing_in_search.append(admin_field)
                    
                    if missing_in_search:
                        self.log_result("Data Structure Mismatch Analysis", False,
                                      f"Admin expects but search API doesn't have: {missing_in_search}")
                    else:
                        self.log_result("Data Structure Mismatch Analysis", True,
                                      "Search API has all fields admin expects")
                    
                    return len(results)
                else:
                    self.log_result("Human Mentor Data Structure (Search API)", False,
                                  "No human mentors found in search API")
                    return 0
            else:
                self.log_result("Human Mentor Data Structure (Search API)", False,
                              f"Status: {response.status_code}", response.text)
                return 0
        except Exception as e:
            self.log_result("Human Mentor Data Structure (Search API)", False, f"Exception: {str(e)}")
            return 0

    def test_admin_database_collections(self):
        """Test admin database collections endpoint to see what's in creators collection"""
        print("🗄️ Testing Admin Database Collections...")
        
        if not self.admin_token:
            self.log_result("Admin Database Collections", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            # Test creators collection
            response = requests.get(f"{BASE_URL}/admin/database/collections/creators", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                documents = data.get("documents", [])
                total = data.get("total", 0)
                
                self.log_result("Admin Database - Creators Collection", True,
                              f"Found {len(documents)} creators, Total: {total}")
                
                if documents:
                    sample_creator = documents[0]
                    self.log_result("Creator Document Structure", True,
                                  f"Fields: {list(sample_creator.keys())}")
                    
                    # Check if this creator has the fields admin endpoint expects
                    admin_expected = ["creator_id", "email", "full_name", "account_name", 
                                    "category", "monthly_price", "status", "subscriber_count", 
                                    "total_earnings", "verification", "created_at"]
                    
                    present_fields = []
                    missing_fields = []
                    
                    for field in admin_expected:
                        if field in sample_creator:
                            present_fields.append(field)
                        else:
                            # Check nested fields
                            if field == "subscriber_count" and "stats" in sample_creator:
                                if "subscriber_count" in sample_creator["stats"]:
                                    present_fields.append(field + " (in stats)")
                                else:
                                    missing_fields.append(field)
                            elif field == "total_earnings" and "stats" in sample_creator:
                                if "total_earnings" in sample_creator["stats"]:
                                    present_fields.append(field + " (in stats)")
                                else:
                                    missing_fields.append(field)
                            else:
                                missing_fields.append(field)
                    
                    if missing_fields:
                        self.log_result("Creator Document vs Admin Expected Fields", False,
                                      f"Missing: {missing_fields}, Present: {present_fields}")
                    else:
                        self.log_result("Creator Document vs Admin Expected Fields", True,
                                      f"All expected fields present: {present_fields}")
                
                return len(documents)
            else:
                self.log_result("Admin Database - Creators Collection", False,
                              f"Status: {response.status_code}", response.text)
                return 0
        except Exception as e:
            self.log_result("Admin Database - Creators Collection", False, f"Exception: {str(e)}")
            return 0

    def test_admin_users_endpoint(self):
        """Test admin users endpoint to see if mentors appear there"""
        print("👥 Testing Admin Users Endpoint...")
        
        if not self.admin_token:
            self.log_result("Admin Users Endpoint", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = requests.get(f"{BASE_URL}/admin/users", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                users = data.get("users", [])
                total = data.get("total", 0)
                
                self.log_result("Admin Users Endpoint", True,
                              f"Found {len(users)} users, Total: {total}")
                
                # Check if any users are marked as mentors
                mentor_users = [user for user in users if user.get("is_mentor", False)]
                
                if mentor_users:
                    self.log_result("Users Marked as Mentors", True,
                                  f"Found {len(mentor_users)} users marked as mentors")
                else:
                    self.log_result("Users Marked as Mentors", False,
                                  "No users marked as mentors in users collection")
                
                return len(users)
            else:
                self.log_result("Admin Users Endpoint", False,
                              f"Status: {response.status_code}", response.text)
                return 0
        except Exception as e:
            self.log_result("Admin Users Endpoint", False, f"Exception: {str(e)}")
            return 0

    def diagnose_admin_console_issue(self):
        """Provide diagnosis of why admin console shows no human mentors"""
        print("🔍 Diagnosing Admin Console Issue...")
        
        # Analyze the test results to provide diagnosis
        admin_mentors_results = [r for r in self.results if "Admin Mentors Endpoint" in r["test"]]
        search_api_results = [r for r in self.results if "Human Mentor Data Structure (Search API)" in r["test"]]
        database_results = [r for r in self.results if "Creator Document vs Admin Expected Fields" in r["test"]]
        
        diagnosis = []
        
        # Check if admin endpoint returns mentors
        admin_mentor_count = 0
        if admin_mentors_results:
            result = admin_mentors_results[0]
            if result["success"] and "Found" in result["details"]:
                try:
                    admin_mentor_count = int(result["details"].split("Found ")[1].split(" mentors")[0])
                except:
                    pass
        
        # Check if search API returns mentors
        search_mentor_count = 0
        if search_api_results:
            result = search_api_results[0]
            if result["success"]:
                try:
                    # This would be from the return value, but we need to track it differently
                    pass
                except:
                    pass
        
        if admin_mentor_count == 0:
            diagnosis.append("❌ CRITICAL: Admin mentors endpoint returns 0 mentors")
            diagnosis.append("   This explains why admin console shows no human mentors")
            
            # Check for data structure issues
            if database_results:
                result = database_results[0]
                if not result["success"] and "Missing" in result["details"]:
                    diagnosis.append("❌ ROOT CAUSE: Data structure mismatch between creator documents and admin endpoint expectations")
                    diagnosis.append(f"   {result['details']}")
                    diagnosis.append("   SOLUTION: Update mentor signup to create all required fields OR update admin endpoint to handle current data structure")
        else:
            diagnosis.append(f"✅ Admin mentors endpoint returns {admin_mentor_count} mentors")
            diagnosis.append("   Issue may be in frontend admin console implementation")
        
        self.log_result("Admin Console Issue Diagnosis", True, "\n".join(diagnosis))

    def run_investigation(self):
        """Run complete admin mentors investigation"""
        print("🚀 Starting Admin Mentors Data Investigation")
        print("=" * 60)
        
        # Phase 1: Admin authentication
        print("\n📋 PHASE 1: ADMIN AUTHENTICATION")
        print("-" * 40)
        
        if not self.test_admin_login():
            print("❌ Cannot proceed without admin access")
            return
        
        # Phase 2: Admin endpoints testing
        print("\n📋 PHASE 2: ADMIN ENDPOINTS TESTING")
        print("-" * 40)
        
        self.test_admin_mentors_endpoint()
        self.test_admin_users_endpoint()
        
        # Phase 3: Data structure analysis
        print("\n📋 PHASE 3: DATA STRUCTURE ANALYSIS")
        print("-" * 40)
        
        self.test_direct_creators_collection_query()
        self.test_admin_database_collections()
        
        # Phase 4: Diagnosis
        print("\n📋 PHASE 4: ISSUE DIAGNOSIS")
        print("-" * 40)
        
        self.diagnose_admin_console_issue()
        
        # Summary
        self.print_investigation_summary()

    def print_investigation_summary(self):
        """Print investigation summary"""
        print("\n" + "=" * 60)
        print("🔍 ADMIN MENTORS INVESTIGATION SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        print()
        
        # Key findings
        print("🔍 KEY FINDINGS:")
        print("-" * 20)
        
        for result in self.results:
            if not result["success"]:
                print(f"❌ {result['test']}: {result['details']}")
        
        print("\n💡 NEXT STEPS:")
        print("-" * 20)
        print("1. Fix data structure mismatch between mentor signup and admin endpoint")
        print("2. Ensure all required fields are created during mentor registration")
        print("3. Update admin endpoint to handle current creator document structure")
        print("4. Test admin console frontend to ensure it uses correct API endpoints")
        
        print("\n" + "=" * 60)

if __name__ == "__main__":
    tester = AdminMentorsDataTester()
    tester.run_investigation()