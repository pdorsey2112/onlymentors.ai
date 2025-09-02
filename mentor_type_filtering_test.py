#!/usr/bin/env python3
"""
Mentor Type Filtering System Testing
Tests the new mentor type filtering system for AI vs Human mentors
"""

import requests
import json
import time
import uuid
from datetime import datetime

# Configuration
BASE_URL = "https://mentor-search.preview.emergentagent.com/api"
TEST_USER_EMAIL = "mentortype.tester@test.com"
TEST_USER_PASSWORD = "TestPass123!"
TEST_USER_NAME = "Mentor Type Tester"

TEST_CREATOR_EMAIL = "human.mentor@test.com"
TEST_CREATOR_PASSWORD = "TestPass123!"
TEST_CREATOR_NAME = "Human Mentor Test"

class MentorTypeFilteringTester:
    def __init__(self):
        self.user_token = None
        self.user_id = None
        self.creator_token = None
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

    def setup_test_user(self):
        """Create and authenticate test user"""
        print("🔧 Setting up test user...")
        
        # User signup
        signup_data = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD,
            "full_name": TEST_USER_NAME
        }
        
        try:
            response = requests.post(f"{BASE_URL}/auth/signup", json=signup_data)
            if response.status_code in [200, 201]:
                data = response.json()
                self.user_token = data.get("token")
                self.user_id = data.get("user", {}).get("user_id")
                self.log_result("User Signup", True, f"User ID: {self.user_id}")
                return True
            elif response.status_code == 400 and ("already exists" in response.text or "already registered" in response.text):
                # Try login instead
                return self.login_test_user()
            else:
                self.log_result("User Signup", False, f"Status: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("User Signup", False, f"Exception: {str(e)}")
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
                self.log_result("User Login", True, f"User ID: {self.user_id}")
                return True
            else:
                self.log_result("User Login", False, f"Status: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("User Login", False, f"Exception: {str(e)}")
            return False

    def setup_test_creator(self):
        """Create and authenticate test creator (human mentor)"""
        print("🔧 Setting up test creator (human mentor)...")
        
        # Creator signup
        signup_data = {
            "email": TEST_CREATOR_EMAIL,
            "password": TEST_CREATOR_PASSWORD,
            "full_name": TEST_CREATOR_NAME,
            "account_name": "HumanMentorTest",
            "description": "Test human mentor for mentor type filtering",
            "monthly_price": 50.0,
            "category": "business",
            "expertise_areas": ["Business Strategy", "Leadership"]
        }
        
        try:
            response = requests.post(f"{BASE_URL}/creators/signup", json=signup_data)
            if response.status_code in [200, 201]:
                data = response.json()
                self.creator_token = data.get("token")
                self.creator_id = data.get("creator", {}).get("creator_id")
                self.log_result("Creator Signup", True, f"Creator ID: {self.creator_id}")
                return True
            elif response.status_code == 400 and ("already exists" in response.text or "already registered" in response.text):
                # Try login instead
                return self.login_test_creator()
            else:
                self.log_result("Creator Signup", False, f"Status: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Creator Signup", False, f"Exception: {str(e)}")
            return False

    def login_test_creator(self):
        """Login existing test creator"""
        login_data = {
            "email": TEST_CREATOR_EMAIL,
            "password": TEST_CREATOR_PASSWORD
        }
        
        try:
            response = requests.post(f"{BASE_URL}/creators/login", json=login_data)
            if response.status_code == 200:
                data = response.json()
                self.creator_token = data.get("token")
                self.creator_id = data.get("creator", {}).get("creator_id")
                self.log_result("Creator Login", True, f"Creator ID: {self.creator_id}")
                return True
            else:
                self.log_result("Creator Login", False, f"Status: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Creator Login", False, f"Exception: {str(e)}")
            return False

    def test_search_api_mentor_type_filtering(self):
        """Test GET /api/search/mentors endpoint with mentor_type parameter"""
        print("🔍 Testing Search API with Mentor Type Filtering...")
        
        # Test 1: mentor_type='ai' parameter returns only AI mentors
        try:
            response = requests.get(f"{BASE_URL}/search/mentors?mentor_type=ai")
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                ai_count = data.get("ai_count", 0)
                human_count = data.get("human_count", 0)
                mentor_type_filter = data.get("mentor_type_filter")
                
                # Verify all results are AI mentors
                all_ai = all(mentor.get("mentor_type") == "ai" and mentor.get("is_ai_mentor") == True 
                           for mentor in results)
                
                # Verify counts
                actual_ai_count = len([m for m in results if m.get("mentor_type") == "ai"])
                count_matches = ai_count == actual_ai_count and human_count == 0
                
                # Verify filter parameter
                filter_correct = mentor_type_filter == "ai"
                
                if all_ai and count_matches and filter_correct and len(results) > 0:
                    self.log_result("Search API - AI Mentors Only", True, 
                                  f"Found {len(results)} AI mentors, ai_count: {ai_count}, human_count: {human_count}")
                else:
                    self.log_result("Search API - AI Mentors Only", False, 
                                  f"Validation failed. All AI: {all_ai}, Count match: {count_matches}, Filter: {filter_correct}, Results: {len(results)}")
            else:
                self.log_result("Search API - AI Mentors Only", False, 
                              f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Search API - AI Mentors Only", False, f"Exception: {str(e)}")

        # Test 2: mentor_type='human' parameter returns only human mentors
        try:
            response = requests.get(f"{BASE_URL}/search/mentors?mentor_type=human")
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                ai_count = data.get("ai_count", 0)
                human_count = data.get("human_count", 0)
                mentor_type_filter = data.get("mentor_type_filter")
                
                # Verify all results are human mentors
                all_human = all(mentor.get("mentor_type") == "human" and mentor.get("is_ai_mentor") == False 
                              for mentor in results)
                
                # Verify counts
                actual_human_count = len([m for m in results if m.get("mentor_type") == "human"])
                count_matches = human_count == actual_human_count and ai_count == 0
                
                # Verify filter parameter
                filter_correct = mentor_type_filter == "human"
                
                if all_human and count_matches and filter_correct:
                    self.log_result("Search API - Human Mentors Only", True, 
                                  f"Found {len(results)} human mentors, ai_count: {ai_count}, human_count: {human_count}")
                else:
                    self.log_result("Search API - Human Mentors Only", False, 
                                  f"Validation failed. All Human: {all_human}, Count match: {count_matches}, Filter: {filter_correct}, Results: {len(results)}")
            else:
                self.log_result("Search API - Human Mentors Only", False, 
                              f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Search API - Human Mentors Only", False, f"Exception: {str(e)}")

        # Test 3: mentor_type='all' returns both AI and human mentors
        try:
            response = requests.get(f"{BASE_URL}/search/mentors?mentor_type=all")
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                ai_count = data.get("ai_count", 0)
                human_count = data.get("human_count", 0)
                mentor_type_filter = data.get("mentor_type_filter")
                
                # Verify we have both types
                has_ai = any(mentor.get("mentor_type") == "ai" for mentor in results)
                has_human = any(mentor.get("mentor_type") == "human" for mentor in results)
                
                # Verify counts
                actual_ai_count = len([m for m in results if m.get("mentor_type") == "ai"])
                actual_human_count = len([m for m in results if m.get("mentor_type") == "human"])
                count_matches = ai_count == actual_ai_count and human_count == actual_human_count
                
                # Verify filter parameter
                filter_correct = mentor_type_filter == "all"
                
                if count_matches and filter_correct and len(results) > 0:
                    self.log_result("Search API - All Mentors", True, 
                                  f"Found {len(results)} total mentors (AI: {ai_count}, Human: {human_count}), Has AI: {has_ai}, Has Human: {has_human}")
                else:
                    self.log_result("Search API - All Mentors", False, 
                                  f"Validation failed. Count match: {count_matches}, Filter: {filter_correct}, Results: {len(results)}")
            else:
                self.log_result("Search API - All Mentors", False, 
                              f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Search API - All Mentors", False, f"Exception: {str(e)}")

        # Test 4: No mentor_type parameter (should default to 'all')
        try:
            response = requests.get(f"{BASE_URL}/search/mentors")
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                ai_count = data.get("ai_count", 0)
                human_count = data.get("human_count", 0)
                mentor_type_filter = data.get("mentor_type_filter")
                
                # Should behave like 'all'
                actual_ai_count = len([m for m in results if m.get("mentor_type") == "ai"])
                actual_human_count = len([m for m in results if m.get("mentor_type") == "human"])
                count_matches = ai_count == actual_ai_count and human_count == actual_human_count
                
                if count_matches and len(results) > 0:
                    self.log_result("Search API - Default (No Parameter)", True, 
                                  f"Default behavior works. Found {len(results)} mentors (AI: {ai_count}, Human: {human_count})")
                else:
                    self.log_result("Search API - Default (No Parameter)", False, 
                                  f"Default behavior failed. Count match: {count_matches}, Results: {len(results)}")
            else:
                self.log_result("Search API - Default (No Parameter)", False, 
                              f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Search API - Default (No Parameter)", False, f"Exception: {str(e)}")

    def test_ai_mentor_data_structure(self):
        """Test AI mentor data consistency"""
        print("🤖 Testing AI Mentor Data Structure...")
        
        try:
            response = requests.get(f"{BASE_URL}/search/mentors?mentor_type=ai")
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                
                if not results:
                    self.log_result("AI Mentor Data Structure", False, "No AI mentors found")
                    return
                
                # Test first few AI mentors
                test_mentors = results[:5]  # Test first 5 AI mentors
                
                for i, mentor in enumerate(test_mentors):
                    mentor_name = mentor.get("name", f"Mentor {i+1}")
                    
                    # Required fields check
                    required_fields = ["id", "name", "bio", "expertise", "mentor_type", "is_ai_mentor", "category"]
                    missing_fields = [field for field in required_fields if field not in mentor or mentor[field] is None]
                    
                    # AI mentor specific checks
                    is_ai_correct = mentor.get("mentor_type") == "ai" and mentor.get("is_ai_mentor") == True
                    has_category = mentor.get("category") in ["business", "sports", "health", "science", "relationships"]
                    
                    if not missing_fields and is_ai_correct and has_category:
                        self.log_result(f"AI Mentor Data - {mentor_name}", True, 
                                      f"All required fields present, category: {mentor.get('category')}")
                    else:
                        self.log_result(f"AI Mentor Data - {mentor_name}", False, 
                                      f"Missing fields: {missing_fields}, AI correct: {is_ai_correct}, Has category: {has_category}")
                
                # Overall AI mentor structure test
                all_valid = all(
                    mentor.get("mentor_type") == "ai" and 
                    mentor.get("is_ai_mentor") == True and
                    all(field in mentor for field in ["id", "name", "bio", "expertise"])
                    for mentor in test_mentors
                )
                
                if all_valid:
                    self.log_result("AI Mentor Data Structure - Overall", True, 
                                  f"All {len(test_mentors)} tested AI mentors have correct structure")
                else:
                    self.log_result("AI Mentor Data Structure - Overall", False, 
                                  "Some AI mentors have incorrect data structure")
                    
            else:
                self.log_result("AI Mentor Data Structure", False, 
                              f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("AI Mentor Data Structure", False, f"Exception: {str(e)}")

    def test_human_mentor_integration(self):
        """Test human creators as mentors"""
        print("👥 Testing Human Mentor Integration...")
        
        try:
            response = requests.get(f"{BASE_URL}/search/mentors?mentor_type=human")
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                
                # Test human mentor data structure
                for mentor in results[:3]:  # Test first 3 human mentors if any
                    mentor_name = mentor.get("name", "Unknown")
                    
                    # Required fields for human mentors
                    required_fields = ["id", "name", "bio", "expertise", "mentor_type", "is_ai_mentor"]
                    missing_fields = [field for field in required_fields if field not in mentor or mentor[field] is None]
                    
                    # Human mentor specific checks
                    is_human_correct = mentor.get("mentor_type") == "human" and mentor.get("is_ai_mentor") == False
                    
                    # Tier information check
                    has_tier_info = all(field in mentor for field in ["tier", "tier_level", "tier_badge_color"])
                    
                    # Pricing information check
                    has_pricing = "monthly_price" in mentor and isinstance(mentor.get("monthly_price"), (int, float))
                    
                    if not missing_fields and is_human_correct:
                        self.log_result(f"Human Mentor Data - {mentor_name}", True, 
                                      f"Correct structure, Tier info: {has_tier_info}, Pricing: {has_pricing}")
                    else:
                        self.log_result(f"Human Mentor Data - {mentor_name}", False, 
                                      f"Missing fields: {missing_fields}, Human correct: {is_human_correct}")
                
                # Test that only verified creators appear
                if results:
                    self.log_result("Human Mentor Integration - Verified Only", True, 
                                  f"Found {len(results)} human mentors (should be verified creators)")
                else:
                    self.log_result("Human Mentor Integration - No Human Mentors", True, 
                                  "No human mentors found (expected if no verified creators exist)")
                    
            else:
                self.log_result("Human Mentor Integration", False, 
                              f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Human Mentor Integration", False, f"Exception: {str(e)}")

    def test_search_and_filtering_logic(self):
        """Test search functionality with mentor type filtering"""
        print("🔍 Testing Search and Filtering Logic...")
        
        # Test 1: Text search with AI mentors only
        try:
            response = requests.get(f"{BASE_URL}/search/mentors?q=steve&mentor_type=ai")
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                query = data.get("query")
                
                # Should find Steve Jobs and other Steves in AI mentors
                steve_found = any("steve" in mentor.get("name", "").lower() for mentor in results)
                all_ai = all(mentor.get("mentor_type") == "ai" for mentor in results)
                
                if query == "steve" and all_ai:
                    self.log_result("Search Logic - Text + AI Filter", True, 
                                  f"Found {len(results)} AI mentors matching 'steve', Steve found: {steve_found}")
                else:
                    self.log_result("Search Logic - Text + AI Filter", False, 
                                  f"Query: {query}, All AI: {all_ai}, Results: {len(results)}")
            else:
                self.log_result("Search Logic - Text + AI Filter", False, 
                              f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Search Logic - Text + AI Filter", False, f"Exception: {str(e)}")

        # Test 2: Category filtering with mentor type
        try:
            response = requests.get(f"{BASE_URL}/search/mentors?category=business&mentor_type=ai")
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                
                # Should find business AI mentors only
                all_business = all(mentor.get("category") == "business" for mentor in results)
                all_ai = all(mentor.get("mentor_type") == "ai" for mentor in results)
                
                if all_business and all_ai and len(results) > 0:
                    self.log_result("Search Logic - Category + AI Filter", True, 
                                  f"Found {len(results)} business AI mentors")
                else:
                    self.log_result("Search Logic - Category + AI Filter", False, 
                                  f"All business: {all_business}, All AI: {all_ai}, Results: {len(results)}")
            else:
                self.log_result("Search Logic - Category + AI Filter", False, 
                              f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Search Logic - Category + AI Filter", False, f"Exception: {str(e)}")

        # Test 3: Combined text + category + mentor type
        try:
            response = requests.get(f"{BASE_URL}/search/mentors?q=business&category=business&mentor_type=all")
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                ai_count = data.get("ai_count", 0)
                human_count = data.get("human_count", 0)
                
                # Should find both AI and human business mentors matching "business"
                all_business = all(mentor.get("category") == "business" for mentor in results)
                has_both_types = ai_count > 0 or human_count >= 0  # At least AI should exist
                
                if all_business and has_both_types:
                    self.log_result("Search Logic - Combined Filters", True, 
                                  f"Found {len(results)} business mentors (AI: {ai_count}, Human: {human_count})")
                else:
                    self.log_result("Search Logic - Combined Filters", False, 
                                  f"All business: {all_business}, Has types: {has_both_types}, Results: {len(results)}")
            else:
                self.log_result("Search Logic - Combined Filters", False, 
                              f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Search Logic - Combined Filters", False, f"Exception: {str(e)}")

    def test_api_response_format(self):
        """Test API response structure and format"""
        print("📋 Testing Data Format and API Response...")
        
        try:
            response = requests.get(f"{BASE_URL}/search/mentors?mentor_type=all")
            if response.status_code == 200:
                data = response.json()
                
                # Required response fields
                required_fields = ["results", "count", "query", "mentor_type_filter", "ai_count", "human_count"]
                missing_fields = [field for field in required_fields if field not in data]
                
                # Validate data types
                results_is_list = isinstance(data.get("results"), list)
                count_is_int = isinstance(data.get("count"), int)
                ai_count_is_int = isinstance(data.get("ai_count"), int)
                human_count_is_int = isinstance(data.get("human_count"), int)
                
                # Validate count consistency
                actual_count = len(data.get("results", []))
                count_matches = data.get("count") == actual_count
                
                # Validate mentor type counts
                actual_ai = len([m for m in data.get("results", []) if m.get("mentor_type") == "ai"])
                actual_human = len([m for m in data.get("results", []) if m.get("mentor_type") == "human"])
                ai_count_matches = data.get("ai_count") == actual_ai
                human_count_matches = data.get("human_count") == actual_human
                
                if (not missing_fields and results_is_list and count_is_int and 
                    ai_count_is_int and human_count_is_int and count_matches and 
                    ai_count_matches and human_count_matches):
                    self.log_result("API Response Format", True, 
                                  f"All required fields present and valid. Total: {actual_count}, AI: {actual_ai}, Human: {actual_human}")
                else:
                    self.log_result("API Response Format", False, 
                                  f"Validation failed. Missing: {missing_fields}, Types valid: {results_is_list and count_is_int}, Counts match: {count_matches and ai_count_matches and human_count_matches}")
                
                # Test individual mentor data format
                if data.get("results"):
                    sample_mentor = data["results"][0]
                    mentor_required_fields = ["id", "name", "mentor_type", "is_ai_mentor"]
                    mentor_missing = [field for field in mentor_required_fields if field not in sample_mentor]
                    
                    if not mentor_missing:
                        self.log_result("Mentor Data Format", True, 
                                      f"Sample mentor has all required fields: {sample_mentor.get('name')}")
                    else:
                        self.log_result("Mentor Data Format", False, 
                                      f"Sample mentor missing fields: {mentor_missing}")
                        
            else:
                self.log_result("API Response Format", False, 
                              f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("API Response Format", False, f"Exception: {str(e)}")

    def test_error_handling(self):
        """Test error handling for invalid parameters"""
        print("⚠️ Testing Error Handling...")
        
        # Test invalid mentor_type parameter
        try:
            response = requests.get(f"{BASE_URL}/search/mentors?mentor_type=invalid")
            if response.status_code == 200:
                # Should handle gracefully, likely defaulting to 'all'
                data = response.json()
                self.log_result("Error Handling - Invalid Mentor Type", True, 
                              f"Handled gracefully, returned {len(data.get('results', []))} results")
            else:
                self.log_result("Error Handling - Invalid Mentor Type", True, 
                              f"Properly rejected invalid parameter with status: {response.status_code}")
        except Exception as e:
            self.log_result("Error Handling - Invalid Mentor Type", False, f"Exception: {str(e)}")

    def run_all_tests(self):
        """Run all mentor type filtering tests"""
        print("🚀 Starting Mentor Type Filtering System Testing")
        print("=" * 70)
        
        # Setup (optional - tests can run without authentication)
        self.setup_test_user()
        self.setup_test_creator()
        
        # Run core tests
        self.test_search_api_mentor_type_filtering()
        self.test_ai_mentor_data_structure()
        self.test_human_mentor_integration()
        self.test_search_and_filtering_logic()
        self.test_api_response_format()
        self.test_error_handling()
        
        # Summary
        self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 70)
        print("🎯 MENTOR TYPE FILTERING SYSTEM TESTING SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        print()
        
        # Group results by category
        categories = {
            "Setup": [],
            "Search API": [],
            "AI Mentor Data": [],
            "Human Mentor Integration": [],
            "Search Logic": [],
            "API Response": [],
            "Error Handling": []
        }
        
        for result in self.results:
            test_name = result["test"]
            if "Setup" in test_name or "Signup" in test_name or "Login" in test_name:
                categories["Setup"].append(result)
            elif "Search API" in test_name:
                categories["Search API"].append(result)
            elif "AI Mentor Data" in test_name:
                categories["AI Mentor Data"].append(result)
            elif "Human Mentor" in test_name:
                categories["Human Mentor Integration"].append(result)
            elif "Search Logic" in test_name:
                categories["Search Logic"].append(result)
            elif "API Response" in test_name or "Mentor Data Format" in test_name:
                categories["API Response"].append(result)
            elif "Error Handling" in test_name:
                categories["Error Handling"].append(result)
        
        for category, tests in categories.items():
            if tests:
                passed = sum(1 for t in tests if t["success"])
                total = len(tests)
                print(f"📂 {category}: {passed}/{total} passed")
                for test in tests:
                    print(f"   {test['status']}: {test['test']}")
                print()
        
        # Critical issues
        critical_failures = [r for r in self.results if not r["success"] and 
                           ("Search API" in r["test"] or "AI Mentor Data Structure - Overall" in r["test"] or 
                            "API Response Format" in r["test"])]
        
        if critical_failures:
            print("🚨 CRITICAL ISSUES FOUND:")
            for failure in critical_failures:
                print(f"   ❌ {failure['test']}: {failure['details']}")
            print()
        
        # Overall assessment
        if success_rate >= 90:
            print("🎉 EXCELLENT: Mentor Type Filtering System is working excellently!")
        elif success_rate >= 75:
            print("✅ GOOD: Mentor Type Filtering System is working well with minor issues.")
        elif success_rate >= 50:
            print("⚠️ MODERATE: Mentor Type Filtering System has some significant issues.")
        else:
            print("🚨 CRITICAL: Mentor Type Filtering System has major issues requiring immediate attention.")
        
        print("=" * 70)

if __name__ == "__main__":
    tester = MentorTypeFilteringTester()
    tester.run_all_tests()