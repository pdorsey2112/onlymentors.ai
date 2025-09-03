#!/usr/bin/env python3
"""
Mentor Type Filtering API Testing
Critical test for mentor sort dropdown reversal issue
Tests if backend API is handling mentor_type parameters correctly
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "https://mentor-search.preview.emergentagent.com/api"

class MentorTypeFilteringTester:
    def __init__(self):
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

    def test_ai_mentors_api_call(self):
        """Test AI Mentors API Call - Should return ONLY AI mentors"""
        print("🤖 Testing AI Mentors API Call...")
        
        try:
            # Test with business category and mentor_type=ai
            response = requests.get(f"{BASE_URL}/search/mentors?category=business&mentor_type=ai")
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                ai_count = data.get("ai_count", 0)
                human_count = data.get("human_count", 0)
                mentor_type_filter = data.get("mentor_type_filter")
                
                # Verify response structure
                if mentor_type_filter != "ai":
                    self.log_result("AI Mentors API - Filter Parameter", False, 
                                  f"mentor_type_filter should be 'ai', got '{mentor_type_filter}'")
                    return
                
                # Count actual AI vs Human mentors in results
                actual_ai_count = sum(1 for mentor in results if mentor.get("mentor_type") == "ai")
                actual_human_count = sum(1 for mentor in results if mentor.get("mentor_type") == "human")
                
                # Verify counts match reported counts
                if ai_count != actual_ai_count:
                    self.log_result("AI Mentors API - Count Consistency", False,
                                  f"Reported ai_count ({ai_count}) doesn't match actual AI mentors ({actual_ai_count})")
                    return
                
                if human_count != actual_human_count:
                    self.log_result("AI Mentors API - Count Consistency", False,
                                  f"Reported human_count ({human_count}) doesn't match actual human mentors ({actual_human_count})")
                    return
                
                # CRITICAL TEST: Should return ONLY AI mentors
                if actual_human_count > 0:
                    self.log_result("AI Mentors API - CRITICAL BUG DETECTED", False,
                                  f"🚨 API RETURNING HUMAN MENTORS WHEN mentor_type=ai! AI: {actual_ai_count}, Human: {actual_human_count}")
                    return
                
                if actual_ai_count == 0:
                    self.log_result("AI Mentors API - No Results", False,
                                  "No AI mentors returned - this might indicate a data issue")
                    return
                
                # Verify all mentors have correct fields
                for mentor in results:
                    if mentor.get("mentor_type") != "ai":
                        self.log_result("AI Mentors API - Mentor Type Field", False,
                                      f"Mentor {mentor.get('name')} has mentor_type='{mentor.get('mentor_type')}', expected 'ai'")
                        return
                    
                    if not mentor.get("is_ai_mentor", False):
                        self.log_result("AI Mentors API - AI Mentor Flag", False,
                                      f"Mentor {mentor.get('name')} has is_ai_mentor=False, expected True")
                        return
                
                self.log_result("AI Mentors API Call", True,
                              f"✅ CORRECT: Returns {actual_ai_count} AI mentors, 0 human mentors")
                
            else:
                self.log_result("AI Mentors API Call", False,
                              f"API call failed with status {response.status_code}", response.text)
                
        except Exception as e:
            self.log_result("AI Mentors API Call", False, f"Exception: {str(e)}")

    def test_human_mentors_api_call(self):
        """Test Human Mentors API Call - Should return ONLY Human mentors"""
        print("👥 Testing Human Mentors API Call...")
        
        try:
            # Test with business category and mentor_type=human
            response = requests.get(f"{BASE_URL}/search/mentors?category=business&mentor_type=human")
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                ai_count = data.get("ai_count", 0)
                human_count = data.get("human_count", 0)
                mentor_type_filter = data.get("mentor_type_filter")
                
                # Verify response structure
                if mentor_type_filter != "human":
                    self.log_result("Human Mentors API - Filter Parameter", False,
                                  f"mentor_type_filter should be 'human', got '{mentor_type_filter}'")
                    return
                
                # Count actual AI vs Human mentors in results
                actual_ai_count = sum(1 for mentor in results if mentor.get("mentor_type") == "ai")
                actual_human_count = sum(1 for mentor in results if mentor.get("mentor_type") == "human")
                
                # Verify counts match reported counts
                if ai_count != actual_ai_count:
                    self.log_result("Human Mentors API - Count Consistency", False,
                                  f"Reported ai_count ({ai_count}) doesn't match actual AI mentors ({actual_ai_count})")
                    return
                
                if human_count != actual_human_count:
                    self.log_result("Human Mentors API - Count Consistency", False,
                                  f"Reported human_count ({human_count}) doesn't match actual human mentors ({actual_human_count})")
                    return
                
                # CRITICAL TEST: Should return ONLY Human mentors
                if actual_ai_count > 0:
                    self.log_result("Human Mentors API - CRITICAL BUG DETECTED", False,
                                  f"🚨 API RETURNING AI MENTORS WHEN mentor_type=human! AI: {actual_ai_count}, Human: {actual_human_count}")
                    return
                
                # Note: It's OK if human_count is 0 (no human mentors exist)
                if actual_human_count == 0:
                    self.log_result("Human Mentors API Call", True,
                                  "✅ CORRECT: Returns 0 human mentors (none exist), 0 AI mentors")
                else:
                    # Verify all mentors have correct fields
                    for mentor in results:
                        if mentor.get("mentor_type") != "human":
                            self.log_result("Human Mentors API - Mentor Type Field", False,
                                          f"Mentor {mentor.get('name')} has mentor_type='{mentor.get('mentor_type')}', expected 'human'")
                            return
                        
                        if mentor.get("is_ai_mentor", True):
                            self.log_result("Human Mentors API - AI Mentor Flag", False,
                                          f"Mentor {mentor.get('name')} has is_ai_mentor=True, expected False")
                            return
                    
                    self.log_result("Human Mentors API Call", True,
                                  f"✅ CORRECT: Returns 0 AI mentors, {actual_human_count} human mentors")
                
            else:
                self.log_result("Human Mentors API Call", False,
                              f"API call failed with status {response.status_code}", response.text)
                
        except Exception as e:
            self.log_result("Human Mentors API Call", False, f"Exception: {str(e)}")

    def test_all_mentors_api_call(self):
        """Test All Mentors API Call - Should return BOTH AI and Human mentors"""
        print("🌟 Testing All Mentors API Call...")
        
        try:
            # Test with business category and mentor_type=all
            response = requests.get(f"{BASE_URL}/search/mentors?category=business&mentor_type=all")
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                ai_count = data.get("ai_count", 0)
                human_count = data.get("human_count", 0)
                mentor_type_filter = data.get("mentor_type_filter")
                
                # Verify response structure
                if mentor_type_filter != "all":
                    self.log_result("All Mentors API - Filter Parameter", False,
                                  f"mentor_type_filter should be 'all', got '{mentor_type_filter}'")
                    return
                
                # Count actual AI vs Human mentors in results
                actual_ai_count = sum(1 for mentor in results if mentor.get("mentor_type") == "ai")
                actual_human_count = sum(1 for mentor in results if mentor.get("mentor_type") == "human")
                
                # Verify counts match reported counts
                if ai_count != actual_ai_count:
                    self.log_result("All Mentors API - Count Consistency", False,
                                  f"Reported ai_count ({ai_count}) doesn't match actual AI mentors ({actual_ai_count})")
                    return
                
                if human_count != actual_human_count:
                    self.log_result("All Mentors API - Count Consistency", False,
                                  f"Reported human_count ({human_count}) doesn't match actual human mentors ({actual_human_count})")
                    return
                
                # Verify total count
                total_count = data.get("count", 0)
                expected_total = actual_ai_count + actual_human_count
                if total_count != expected_total:
                    self.log_result("All Mentors API - Total Count", False,
                                  f"Total count ({total_count}) doesn't match AI + Human ({expected_total})")
                    return
                
                # Should have AI mentors (at minimum)
                if actual_ai_count == 0:
                    self.log_result("All Mentors API - AI Mentors Missing", False,
                                  "No AI mentors returned - this indicates a data issue")
                    return
                
                # Verify mentor type fields are correct
                for mentor in results:
                    mentor_type = mentor.get("mentor_type")
                    is_ai_mentor = mentor.get("is_ai_mentor")
                    
                    if mentor_type == "ai" and not is_ai_mentor:
                        self.log_result("All Mentors API - AI Mentor Flag Mismatch", False,
                                      f"AI mentor {mentor.get('name')} has is_ai_mentor=False")
                        return
                    
                    if mentor_type == "human" and is_ai_mentor:
                        self.log_result("All Mentors API - Human Mentor Flag Mismatch", False,
                                      f"Human mentor {mentor.get('name')} has is_ai_mentor=True")
                        return
                
                self.log_result("All Mentors API Call", True,
                              f"✅ CORRECT: Returns {actual_ai_count} AI mentors + {actual_human_count} human mentors = {expected_total} total")
                
            else:
                self.log_result("All Mentors API Call", False,
                              f"API call failed with status {response.status_code}", response.text)
                
        except Exception as e:
            self.log_result("All Mentors API Call", False, f"Exception: {str(e)}")

    def test_default_behavior(self):
        """Test Default Behavior (no mentor_type parameter) - Should return all mentors"""
        print("🔄 Testing Default Behavior (no mentor_type parameter)...")
        
        try:
            # Test with business category but no mentor_type parameter
            response = requests.get(f"{BASE_URL}/search/mentors?category=business")
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                ai_count = data.get("ai_count", 0)
                human_count = data.get("human_count", 0)
                mentor_type_filter = data.get("mentor_type_filter")
                
                # Count actual AI vs Human mentors in results
                actual_ai_count = sum(1 for mentor in results if mentor.get("mentor_type") == "ai")
                actual_human_count = sum(1 for mentor in results if mentor.get("mentor_type") == "human")
                
                # Should behave like "all" mentors
                if actual_ai_count == 0:
                    self.log_result("Default Behavior - AI Mentors Missing", False,
                                  "No AI mentors returned in default behavior")
                    return
                
                # Verify counts match
                if ai_count != actual_ai_count or human_count != actual_human_count:
                    self.log_result("Default Behavior - Count Mismatch", False,
                                  f"Count mismatch. Reported: AI={ai_count}, Human={human_count}. Actual: AI={actual_ai_count}, Human={actual_human_count}")
                    return
                
                self.log_result("Default Behavior", True,
                              f"✅ CORRECT: Default returns {actual_ai_count} AI + {actual_human_count} human mentors")
                
            else:
                self.log_result("Default Behavior", False,
                              f"API call failed with status {response.status_code}", response.text)
                
        except Exception as e:
            self.log_result("Default Behavior", False, f"Exception: {str(e)}")

    def test_cross_category_consistency(self):
        """Test mentor type filtering across different categories"""
        print("📊 Testing Cross-Category Consistency...")
        
        categories = ["business", "sports", "health", "science", "relationships"]
        
        for category in categories:
            try:
                # Test AI mentors for this category
                ai_response = requests.get(f"{BASE_URL}/search/mentors?category={category}&mentor_type=ai")
                
                if ai_response.status_code == 200:
                    ai_data = ai_response.json()
                    ai_results = ai_data.get("results", [])
                    
                    # Verify all results are AI mentors
                    non_ai_mentors = [m for m in ai_results if m.get("mentor_type") != "ai"]
                    if non_ai_mentors:
                        self.log_result(f"Cross-Category Consistency - {category.title()} AI Filter", False,
                                      f"Found {len(non_ai_mentors)} non-AI mentors in AI filter")
                        continue
                    
                    self.log_result(f"Cross-Category Consistency - {category.title()} AI Filter", True,
                                  f"✅ {len(ai_results)} AI mentors, 0 non-AI mentors")
                else:
                    self.log_result(f"Cross-Category Consistency - {category.title()} AI Filter", False,
                                  f"API call failed with status {ai_response.status_code}")
                
                # Small delay between requests
                time.sleep(0.1)
                
            except Exception as e:
                self.log_result(f"Cross-Category Consistency - {category.title()}", False, f"Exception: {str(e)}")

    def test_search_with_mentor_type(self):
        """Test search functionality combined with mentor type filtering"""
        print("🔍 Testing Search + Mentor Type Filtering...")
        
        try:
            # Test search for "steve" with AI mentor filter
            response = requests.get(f"{BASE_URL}/search/mentors?q=steve&mentor_type=ai")
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                
                # Verify all results contain "steve" and are AI mentors
                for mentor in results:
                    name = mentor.get("name", "").lower()
                    mentor_type = mentor.get("mentor_type")
                    
                    if "steve" not in name:
                        self.log_result("Search + Mentor Type - Name Match", False,
                                      f"Mentor '{mentor.get('name')}' doesn't contain 'steve'")
                        return
                    
                    if mentor_type != "ai":
                        self.log_result("Search + Mentor Type - Type Filter", False,
                                      f"Mentor '{mentor.get('name')}' has type '{mentor_type}', expected 'ai'")
                        return
                
                self.log_result("Search + Mentor Type Filtering", True,
                              f"✅ Found {len(results)} AI mentors matching 'steve'")
                
            else:
                self.log_result("Search + Mentor Type Filtering", False,
                              f"API call failed with status {response.status_code}", response.text)
                
        except Exception as e:
            self.log_result("Search + Mentor Type Filtering", False, f"Exception: {str(e)}")

    def run_all_tests(self):
        """Run all mentor type filtering tests"""
        print("🚀 Starting Mentor Type Filtering API Testing")
        print("🎯 CRITICAL: Testing for mentor sort dropdown reversal issue")
        print("=" * 70)
        
        # Core tests for the reported bug
        self.test_ai_mentors_api_call()
        self.test_human_mentors_api_call()
        self.test_all_mentors_api_call()
        self.test_default_behavior()
        
        # Additional comprehensive tests
        self.test_cross_category_consistency()
        self.test_search_with_mentor_type()
        
        # Summary
        self.print_summary()





    def print_summary(self):
        """Print test summary with focus on critical bug detection"""
        print("\n" + "=" * 70)
        print("🎯 MENTOR TYPE FILTERING API TESTING SUMMARY")
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
        
        # Check for critical bug indicators
        critical_bugs = [r for r in self.results if not r["success"] and "CRITICAL BUG DETECTED" in r["test"]]
        
        if critical_bugs:
            print("🚨 CRITICAL BUG DETECTED IN BACKEND API!")
            print("=" * 50)
            for bug in critical_bugs:
                print(f"❌ {bug['test']}")
                print(f"   {bug['details']}")
            print()
            print("🔧 DIAGNOSIS: The backend API is returning incorrect mentor types!")
            print("   - This explains why the frontend dropdown appears 'reversed'")
            print("   - The issue is in the backend logic, not the frontend")
            print()
        else:
            print("✅ NO CRITICAL BACKEND BUGS DETECTED")
            print("   - Backend API is correctly filtering mentor types")
            print("   - If frontend still shows reversed results, the issue is in frontend logic")
            print()
        
        # Detailed results
        print("📋 DETAILED TEST RESULTS:")
        for result in self.results:
            print(f"   {result['status']}: {result['test']}")
            if result['details']:
                print(f"      └─ {result['details']}")
        print()
        
        # Final assessment
        if critical_bugs:
            print("🚨 CONCLUSION: BACKEND API BUG CONFIRMED")
            print("   The mentor type filtering logic in the backend is reversed or incorrect.")
            print("   This is causing the frontend dropdown to show wrong mentors.")
        elif success_rate >= 90:
            print("✅ CONCLUSION: BACKEND API IS WORKING CORRECTLY")
            print("   If users still see reversed results, the issue is in frontend display logic.")
        else:
            print("⚠️ CONCLUSION: BACKEND API HAS SOME ISSUES")
            print("   Multiple test failures detected. Review individual test results above.")
        
        print("=" * 70)

if __name__ == "__main__":
    tester = MentorTypeFilteringTester()
    tester.run_all_tests()