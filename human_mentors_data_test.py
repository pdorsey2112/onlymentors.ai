#!/usr/bin/env python3
"""
Human Mentors Data Investigation Test
Investigates the reported issue where admin console shows no human mentors
and human mentor filtering is not working correctly.
"""

import requests
import json
import time
import uuid
from datetime import datetime

# Configuration
BASE_URL = "https://mentor-search.preview.emergentagent.com/api"
TEST_USER_EMAIL = "human.mentor.test@example.com"
TEST_USER_PASSWORD = "TestPass123!"
TEST_USER_NAME = "Human Mentor Test User"

class HumanMentorsDataTester:
    def __init__(self):
        self.user_token = None
        self.user_id = None
        self.creator_id = None
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

    def test_creators_collection_direct_query(self):
        """Test 1: Direct query to creators collection to see what data exists"""
        print("🔍 Testing Direct Creators Collection Query...")
        
        try:
            # Try to get all creators (this might not be a public endpoint, but let's test)
            response = requests.get(f"{BASE_URL}/creators")
            
            if response.status_code == 200:
                data = response.json()
                creators = data.get("creators", [])
                verified_creators = [c for c in creators if c.get("is_verified", False)]
                
                self.log_result("Direct Creators Collection Query", True,
                              f"Found {len(creators)} total creators, {len(verified_creators)} verified")
                
                # Analyze creator data structure
                if creators:
                    sample_creator = creators[0]
                    required_fields = ["creator_id", "account_name", "bio", "expertise", "is_verified"]
                    missing_fields = [field for field in required_fields if field not in sample_creator]
                    
                    if missing_fields:
                        self.log_result("Creator Data Structure Analysis", False,
                                      f"Missing required fields: {missing_fields}")
                    else:
                        self.log_result("Creator Data Structure Analysis", True,
                                      "All required fields present in creator data")
                
                return len(verified_creators)
            else:
                self.log_result("Direct Creators Collection Query", False,
                              f"Status: {response.status_code}", response.text)
                return 0
        except Exception as e:
            self.log_result("Direct Creators Collection Query", False, f"Exception: {str(e)}")
            return 0

    def test_mentor_search_api_human_filter(self):
        """Test 2: Test /api/search/mentors endpoint with mentor_type=human"""
        print("🔍 Testing Mentor Search API - Human Filter...")
        
        try:
            # Test mentor_type=human
            response = requests.get(f"{BASE_URL}/search/mentors?mentor_type=human")
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                human_count = data.get("human_count", 0)
                
                self.log_result("Mentor Search API - Human Filter", True,
                              f"Found {len(results)} human mentors, reported count: {human_count}")
                
                # Verify all results are actually human mentors
                if results:
                    all_human = all(mentor.get("mentor_type") == "human" and 
                                  mentor.get("is_ai_mentor") == False for mentor in results)
                    
                    if all_human:
                        self.log_result("Human Mentor Type Verification", True,
                                      "All returned mentors are correctly marked as human")
                    else:
                        self.log_result("Human Mentor Type Verification", False,
                                      "Some returned mentors are not properly marked as human")
                        
                    # Check data structure
                    sample_mentor = results[0]
                    required_fields = ["id", "name", "bio", "expertise", "mentor_type", "is_ai_mentor"]
                    missing_fields = [field for field in required_fields if field not in sample_mentor]
                    
                    if missing_fields:
                        self.log_result("Human Mentor Data Structure", False,
                                      f"Missing fields: {missing_fields}")
                    else:
                        self.log_result("Human Mentor Data Structure", True,
                                      "Human mentor data structure is complete")
                
                return len(results)
            else:
                self.log_result("Mentor Search API - Human Filter", False,
                              f"Status: {response.status_code}", response.text)
                return 0
        except Exception as e:
            self.log_result("Mentor Search API - Human Filter", False, f"Exception: {str(e)}")
            return 0

    def test_mentor_search_api_ai_filter(self):
        """Test 3: Test /api/search/mentors endpoint with mentor_type=ai for comparison"""
        print("🔍 Testing Mentor Search API - AI Filter...")
        
        try:
            response = requests.get(f"{BASE_URL}/search/mentors?mentor_type=ai")
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                ai_count = data.get("ai_count", 0)
                
                self.log_result("Mentor Search API - AI Filter", True,
                              f"Found {len(results)} AI mentors, reported count: {ai_count}")
                
                # Verify all results are actually AI mentors
                if results:
                    all_ai = all(mentor.get("mentor_type") == "ai" and 
                               mentor.get("is_ai_mentor") == True for mentor in results)
                    
                    if all_ai:
                        self.log_result("AI Mentor Type Verification", True,
                                      "All returned mentors are correctly marked as AI")
                    else:
                        self.log_result("AI Mentor Type Verification", False,
                                      "Some returned mentors are not properly marked as AI")
                
                return len(results)
            else:
                self.log_result("Mentor Search API - AI Filter", False,
                              f"Status: {response.status_code}", response.text)
                return 0
        except Exception as e:
            self.log_result("Mentor Search API - AI Filter", False, f"Exception: {str(e)}")
            return 0

    def test_mentor_search_api_all_filter(self):
        """Test 4: Test /api/search/mentors endpoint with mentor_type=all"""
        print("🔍 Testing Mentor Search API - All Filter...")
        
        try:
            response = requests.get(f"{BASE_URL}/search/mentors?mentor_type=all")
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                ai_count = data.get("ai_count", 0)
                human_count = data.get("human_count", 0)
                total_count = data.get("count", 0)
                
                self.log_result("Mentor Search API - All Filter", True,
                              f"Total: {len(results)}, AI: {ai_count}, Human: {human_count}, Reported total: {total_count}")
                
                # Verify counts match
                actual_ai = len([m for m in results if m.get("mentor_type") == "ai"])
                actual_human = len([m for m in results if m.get("mentor_type") == "human"])
                
                if actual_ai == ai_count and actual_human == human_count:
                    self.log_result("Mentor Count Verification", True,
                                  "Reported counts match actual counts")
                else:
                    self.log_result("Mentor Count Verification", False,
                                  f"Count mismatch - Actual AI: {actual_ai}, Human: {actual_human}")
                
                return {"total": len(results), "ai": actual_ai, "human": actual_human}
            else:
                self.log_result("Mentor Search API - All Filter", False,
                              f"Status: {response.status_code}", response.text)
                return {"total": 0, "ai": 0, "human": 0}
        except Exception as e:
            self.log_result("Mentor Search API - All Filter", False, f"Exception: {str(e)}")
            return {"total": 0, "ai": 0, "human": 0}

    def create_test_human_mentor(self):
        """Test 5: Create a test human mentor to verify the signup process"""
        print("👤 Creating Test Human Mentor...")
        
        # First, register as a user with mentor option
        signup_data = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD,
            "full_name": TEST_USER_NAME,
            "phone_number": "+1234567890",
            "communication_preferences": json.dumps({"email": True, "text": False}),
            "subscription_plan": "free",
            "become_mentor": True
        }
        
        try:
            response = requests.post(f"{BASE_URL}/auth/register", data=signup_data)
            
            if response.status_code in [200, 201]:
                data = response.json()
                self.user_token = data.get("token")
                self.user_id = data.get("user", {}).get("user_id")
                is_mentor = data.get("user", {}).get("is_mentor", False)
                
                self.log_result("Test Human Mentor Registration", True,
                              f"User ID: {self.user_id}, Is Mentor: {is_mentor}")
                return True
            elif response.status_code == 400 and "already registered" in response.text.lower():
                # Try to login instead
                return self.login_test_user()
            else:
                self.log_result("Test Human Mentor Registration", False,
                              f"Status: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Test Human Mentor Registration", False, f"Exception: {str(e)}")
            return False

    def login_test_user(self):
        """Login existing test user"""
        login_data = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }
        
        try:
            response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
            if response.status_code == 200:
                data = response.json()
                self.user_token = data.get("token")
                self.user_id = data.get("user", {}).get("user_id")
                self.log_result("Test User Login", True, f"User ID: {self.user_id}")
                return True
            else:
                self.log_result("Test User Login", False, f"Status: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Test User Login", False, f"Exception: {str(e)}")
            return False

    def test_become_mentor_endpoint(self):
        """Test 6: Test the /api/users/become-mentor endpoint"""
        print("🎓 Testing Become Mentor Endpoint...")
        
        if not self.user_token:
            self.log_result("Become Mentor Endpoint", False, "No user token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.user_token}"}
        
        try:
            response = requests.post(f"{BASE_URL}/users/become-mentor", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                success = data.get("success", False)
                message = data.get("message", "")
                self.creator_id = data.get("creator_id")
                
                self.log_result("Become Mentor Endpoint", True,
                              f"Success: {success}, Message: {message}, Creator ID: {self.creator_id}")
                return True
            else:
                self.log_result("Become Mentor Endpoint", False,
                              f"Status: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Become Mentor Endpoint", False, f"Exception: {str(e)}")
            return False

    def verify_mentor_appears_in_search(self):
        """Test 7: Verify the newly created mentor appears in human mentor search"""
        print("🔍 Verifying New Mentor Appears in Search...")
        
        if not self.creator_id:
            self.log_result("Verify Mentor in Search", False, "No creator ID available")
            return False
        
        try:
            # Wait a moment for database consistency
            time.sleep(2)
            
            response = requests.get(f"{BASE_URL}/search/mentors?mentor_type=human")
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                
                # Look for our mentor
                our_mentor = None
                for mentor in results:
                    if mentor.get("id") == self.creator_id or mentor.get("name") == TEST_USER_NAME:
                        our_mentor = mentor
                        break
                
                if our_mentor:
                    self.log_result("Verify Mentor in Search", True,
                                  f"Mentor found in search: {our_mentor.get('name')} (ID: {our_mentor.get('id')})")
                    
                    # Verify mentor data structure
                    required_fields = ["id", "name", "bio", "expertise", "mentor_type", "is_ai_mentor"]
                    missing_fields = [field for field in required_fields if field not in our_mentor]
                    
                    if missing_fields:
                        self.log_result("New Mentor Data Structure", False,
                                      f"Missing fields: {missing_fields}")
                    else:
                        self.log_result("New Mentor Data Structure", True,
                                      "New mentor has complete data structure")
                    
                    # Verify mentor type
                    if (our_mentor.get("mentor_type") == "human" and 
                        our_mentor.get("is_ai_mentor") == False):
                        self.log_result("New Mentor Type Verification", True,
                                      "Mentor correctly marked as human")
                    else:
                        self.log_result("New Mentor Type Verification", False,
                                      f"Mentor type incorrect: {our_mentor.get('mentor_type')}, is_ai: {our_mentor.get('is_ai_mentor')}")
                    
                    return True
                else:
                    self.log_result("Verify Mentor in Search", False,
                                  f"Mentor not found in search results. Total human mentors: {len(results)}")
                    return False
            else:
                self.log_result("Verify Mentor in Search", False,
                              f"Status: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Verify Mentor in Search", False, f"Exception: {str(e)}")
            return False

    def test_admin_endpoints(self):
        """Test 8: Test admin endpoints that might show mentors (if accessible)"""
        print("👑 Testing Admin Endpoints...")
        
        # Test various admin endpoints that might exist
        admin_endpoints = [
            "/admin/mentors",
            "/admin/creators", 
            "/admin/users",
            "/admin/dashboard",
            "/creators/all",
            "/mentors/all"
        ]
        
        for endpoint in admin_endpoints:
            try:
                response = requests.get(f"{BASE_URL}{endpoint}")
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_result(f"Admin Endpoint {endpoint}", True,
                                  f"Accessible - Response keys: {list(data.keys()) if isinstance(data, dict) else 'Non-dict response'}")
                elif response.status_code in [401, 403]:
                    self.log_result(f"Admin Endpoint {endpoint}", True,
                                  "Properly protected (requires authentication)")
                elif response.status_code == 404:
                    self.log_result(f"Admin Endpoint {endpoint}", True,
                                  "Endpoint not found (expected)")
                else:
                    self.log_result(f"Admin Endpoint {endpoint}", False,
                                  f"Unexpected status: {response.status_code}")
            except Exception as e:
                self.log_result(f"Admin Endpoint {endpoint}", False, f"Exception: {str(e)}")

    def test_database_consistency(self):
        """Test 9: Check for database consistency issues"""
        print("🗄️ Testing Database Consistency...")
        
        try:
            # Get human mentors count from different endpoints
            human_search_response = requests.get(f"{BASE_URL}/search/mentors?mentor_type=human")
            all_search_response = requests.get(f"{BASE_URL}/search/mentors?mentor_type=all")
            
            if human_search_response.status_code == 200 and all_search_response.status_code == 200:
                human_data = human_search_response.json()
                all_data = all_search_response.json()
                
                human_count_from_human_search = len(human_data.get("results", []))
                human_count_from_all_search = all_data.get("human_count", 0)
                
                if human_count_from_human_search == human_count_from_all_search:
                    self.log_result("Database Consistency - Human Count", True,
                                  f"Consistent human mentor count: {human_count_from_human_search}")
                else:
                    self.log_result("Database Consistency - Human Count", False,
                                  f"Inconsistent counts - Human search: {human_count_from_human_search}, All search: {human_count_from_all_search}")
                
                # Check AI count consistency
                ai_search_response = requests.get(f"{BASE_URL}/search/mentors?mentor_type=ai")
                if ai_search_response.status_code == 200:
                    ai_data = ai_search_response.json()
                    ai_count_from_ai_search = len(ai_data.get("results", []))
                    ai_count_from_all_search = all_data.get("ai_count", 0)
                    
                    if ai_count_from_ai_search == ai_count_from_all_search:
                        self.log_result("Database Consistency - AI Count", True,
                                      f"Consistent AI mentor count: {ai_count_from_ai_search}")
                    else:
                        self.log_result("Database Consistency - AI Count", False,
                                      f"Inconsistent counts - AI search: {ai_count_from_ai_search}, All search: {ai_count_from_all_search}")
            else:
                self.log_result("Database Consistency", False,
                              "Could not retrieve data for consistency check")
        except Exception as e:
            self.log_result("Database Consistency", False, f"Exception: {str(e)}")

    def run_investigation(self):
        """Run complete human mentors data investigation"""
        print("🚀 Starting Human Mentors Data Investigation")
        print("=" * 60)
        
        # Phase 1: Check current state
        print("\n📋 PHASE 1: CURRENT STATE ANALYSIS")
        print("-" * 40)
        
        creators_count = self.test_creators_collection_direct_query()
        human_mentors_count = self.test_mentor_search_api_human_filter()
        ai_mentors_count = self.test_mentor_search_api_ai_filter()
        all_mentors_data = self.test_mentor_search_api_all_filter()
        
        # Phase 2: Test mentor creation process
        print("\n📋 PHASE 2: MENTOR CREATION TESTING")
        print("-" * 40)
        
        if self.create_test_human_mentor():
            self.test_become_mentor_endpoint()
            self.verify_mentor_appears_in_search()
        
        # Phase 3: System consistency checks
        print("\n📋 PHASE 3: SYSTEM CONSISTENCY CHECKS")
        print("-" * 40)
        
        self.test_admin_endpoints()
        self.test_database_consistency()
        
        # Summary
        self.print_investigation_summary()

    def print_investigation_summary(self):
        """Print investigation summary with diagnosis"""
        print("\n" + "=" * 60)
        print("🔍 HUMAN MENTORS DATA INVESTIGATION SUMMARY")
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
        
        # Find human mentor counts from results
        human_mentor_results = [r for r in self.results if "Human Filter" in r["test"]]
        if human_mentor_results:
            human_count = 0
            for result in human_mentor_results:
                if "Found" in result["details"]:
                    try:
                        human_count = int(result["details"].split("Found ")[1].split(" human")[0])
                        break
                    except:
                        pass
            
            if human_count == 0:
                print("❌ CRITICAL ISSUE: No human mentors found in search results")
                print("   This confirms the user's report about admin console showing no human mentors")
            else:
                print(f"✅ Human mentors found: {human_count}")
        
        # Check for failed tests
        critical_failures = [r for r in self.results if not r["success"]]
        if critical_failures:
            print("\n🚨 CRITICAL ISSUES:")
            for failure in critical_failures:
                print(f"   ❌ {failure['test']}: {failure['details']}")
        
        # Recommendations
        print("\n💡 RECOMMENDATIONS:")
        print("-" * 20)
        
        if failed_tests > 0:
            print("1. Investigate database schema for creators collection")
            print("2. Verify mentor signup process creates proper creator records")
            print("3. Check if is_verified flag is being set correctly")
            print("4. Ensure mentor search API queries creators collection properly")
            print("5. Verify admin console is using correct API endpoints")
        else:
            print("✅ All tests passed - system appears to be working correctly")
            print("   If admin console still shows no mentors, check frontend implementation")
        
        print("\n" + "=" * 60)

if __name__ == "__main__":
    tester = HumanMentorsDataTester()
    tester.run_investigation()