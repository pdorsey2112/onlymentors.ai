#!/usr/bin/env python3
"""
Comprehensive Backend Test for OnlyMentors.ai Expanded Mentor Database
Testing the updated mentor counts and new mentor accessibility
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://enterprise-coach.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class ExpandedMentorsTest:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    async def setup_session(self):
        """Setup HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
            
    def log_test(self, test_name, passed, details=""):
        """Log test result"""
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
            
        result = f"{status}: {test_name}"
        if details:
            result += f" - {details}"
        
        self.test_results.append(result)
        print(result)
        
    async def authenticate_user(self):
        """Create test user and authenticate"""
        try:
            # Create unique test user
            timestamp = int(datetime.now().timestamp())
            test_email = f"expandedtest{timestamp}@onlymentors.ai"
            
            signup_data = {
                "email": test_email,
                "password": "TestPass123!",
                "full_name": "Expanded Test User"
            }
            
            async with self.session.post(f"{API_BASE}/auth/signup", json=signup_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.auth_token = data.get("token")
                    self.log_test("User Authentication", True, f"Created user: {test_email}")
                    return True
                else:
                    error_text = await response.text()
                    self.log_test("User Authentication", False, f"Status: {response.status}, Error: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("User Authentication", False, f"Exception: {str(e)}")
            return False
            
    async def test_updated_mentor_counts(self):
        """Test 1: Verify updated mentor counts per category"""
        try:
            async with self.session.get(f"{API_BASE}/categories") as response:
                if response.status == 200:
                    data = await response.json()
                    categories = data.get("categories", [])
                    
                    # Expected counts based on the review request
                    expected_counts = {
                        "business": 64,  # ~64 mentors
                        "sports": 37,    # ~37 mentors  
                        "health": 25,    # ~25 mentors
                        "science": 25,   # ~25 mentors
                        "relationships": 20  # 20 mentors
                    }
                    
                    total_expected = sum(expected_counts.values())  # ~171 mentors
                    
                    for category in categories:
                        cat_id = category.get("id")
                        actual_count = category.get("count", 0)
                        expected_count = expected_counts.get(cat_id, 0)
                        
                        if cat_id in expected_counts:
                            # Allow some flexibility in counts (±5)
                            if abs(actual_count - expected_count) <= 5:
                                self.log_test(f"Category Count - {cat_id.title()}", True, 
                                            f"Expected ~{expected_count}, Got {actual_count}")
                            else:
                                self.log_test(f"Category Count - {cat_id.title()}", False, 
                                            f"Expected ~{expected_count}, Got {actual_count}")
                    
                    # Test total mentor count
                    total_actual = data.get("total_mentors", 0)
                    if abs(total_actual - total_expected) <= 10:
                        self.log_test("Total Mentor Count", True, 
                                    f"Expected ~{total_expected}, Got {total_actual}")
                    else:
                        self.log_test("Total Mentor Count", False, 
                                    f"Expected ~{total_expected}, Got {total_actual}")
                        
                else:
                    self.log_test("Updated Mentor Counts", False, f"Status: {response.status}")
                    
        except Exception as e:
            self.log_test("Updated Mentor Counts", False, f"Exception: {str(e)}")
            
    async def test_new_mentors_accessibility(self):
        """Test 2: Verify new mentors are accessible in each category"""
        try:
            categories = ["business", "sports", "health", "science", "relationships"]
            
            for category in categories:
                async with self.session.get(f"{API_BASE}/categories/{category}/mentors") as response:
                    if response.status == 200:
                        data = await response.json()
                        mentors = data.get("mentors", [])
                        count = data.get("count", 0)
                        
                        if count > 0 and len(mentors) > 0:
                            self.log_test(f"Category Accessibility - {category.title()}", True, 
                                        f"Found {count} mentors")
                        else:
                            self.log_test(f"Category Accessibility - {category.title()}", False, 
                                        f"No mentors found")
                    else:
                        self.log_test(f"Category Accessibility - {category.title()}", False, 
                                    f"Status: {response.status}")
                        
        except Exception as e:
            self.log_test("New Mentors Accessibility", False, f"Exception: {str(e)}")
            
    async def test_search_functionality(self):
        """Test 3: Verify new mentors appear in search results"""
        try:
            # Test general search
            async with self.session.get(f"{API_BASE}/search/mentors?q=") as response:
                if response.status == 200:
                    data = await response.json()
                    total_results = data.get("count", 0)
                    
                    if total_results >= 150:  # Should have ~171 mentors
                        self.log_test("General Search", True, f"Found {total_results} mentors")
                    else:
                        self.log_test("General Search", False, f"Only found {total_results} mentors")
                else:
                    self.log_test("General Search", False, f"Status: {response.status}")
            
            # Test category-specific searches
            categories = ["business", "sports", "health", "science", "relationships"]
            for category in categories:
                async with self.session.get(f"{API_BASE}/search/mentors?category={category}") as response:
                    if response.status == 200:
                        data = await response.json()
                        results = data.get("results", [])
                        count = data.get("count", 0)
                        
                        if count > 0:
                            self.log_test(f"Category Search - {category.title()}", True, 
                                        f"Found {count} mentors")
                        else:
                            self.log_test(f"Category Search - {category.title()}", False, 
                                        "No mentors found")
                    else:
                        self.log_test(f"Category Search - {category.title()}", False, 
                                    f"Status: {response.status}")
                        
        except Exception as e:
            self.log_test("Search Functionality", False, f"Exception: {str(e)}")
            
    async def test_sample_new_mentors(self):
        """Test 4: Test specific new mentors mentioned in the review"""
        sample_mentors = {
            "business": ["jamie_dimon", "ray_dalio"],
            "sports": ["tom_brady", "lebron_james"], 
            "health": ["deepak_chopra", "mark_hyman"],
            "science": ["neil_degrasse_tyson", "michio_kaku"]
        }
        
        for category, mentor_ids in sample_mentors.items():
            for mentor_id in mentor_ids:
                try:
                    # Search for specific mentor
                    async with self.session.get(f"{API_BASE}/search/mentors?q={mentor_id.replace('_', ' ')}") as response:
                        if response.status == 200:
                            data = await response.json()
                            results = data.get("results", [])
                            
                            # Check if mentor is found
                            mentor_found = any(mentor.get("id") == mentor_id for mentor in results)
                            
                            if mentor_found:
                                self.log_test(f"Sample Mentor - {mentor_id}", True, 
                                            f"Found in {category} category")
                            else:
                                self.log_test(f"Sample Mentor - {mentor_id}", False, 
                                            "Not found in search results")
                        else:
                            self.log_test(f"Sample Mentor - {mentor_id}", False, 
                                        f"Search failed: {response.status}")
                            
                except Exception as e:
                    self.log_test(f"Sample Mentor - {mentor_id}", False, f"Exception: {str(e)}")
                    
    async def test_llm_integration_new_mentors(self):
        """Test 5: Test LLM integration with new mentors"""
        if not self.auth_token:
            self.log_test("LLM Integration Setup", False, "No auth token available")
            return
            
        # Test with a few sample new mentors
        test_cases = [
            {"category": "business", "mentor_id": "ray_dalio", "question": "What are your principles for successful investing?"},
            {"category": "sports", "mentor_id": "tom_brady", "question": "How do you maintain peak performance under pressure?"},
            {"category": "health", "mentor_id": "deepak_chopra", "question": "How can I improve my mind-body connection?"},
            {"category": "science", "mentor_id": "neil_degrasse_tyson", "question": "What fascinates you most about the universe?"}
        ]
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        for test_case in test_cases:
            try:
                question_data = {
                    "category": test_case["category"],
                    "mentor_ids": [test_case["mentor_id"]],
                    "question": test_case["question"]
                }
                
                async with self.session.post(f"{API_BASE}/questions/ask", 
                                           json=question_data, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        responses = data.get("responses", [])
                        
                        if responses and len(responses) > 0:
                            response_text = responses[0].get("response", "")
                            response_length = len(response_text)
                            
                            # Check for quality response (not just fallback)
                            if response_length > 500:  # Good quality response
                                self.log_test(f"LLM Integration - {test_case['mentor_id']}", True, 
                                            f"Response length: {response_length} chars")
                            else:
                                self.log_test(f"LLM Integration - {test_case['mentor_id']}", False, 
                                            f"Short response: {response_length} chars")
                        else:
                            self.log_test(f"LLM Integration - {test_case['mentor_id']}", False, 
                                        "No response received")
                    elif response.status == 404:
                        self.log_test(f"LLM Integration - {test_case['mentor_id']}", False, 
                                    "Mentor not found")
                    else:
                        error_text = await response.text()
                        self.log_test(f"LLM Integration - {test_case['mentor_id']}", False, 
                                    f"Status: {response.status}, Error: {error_text}")
                        
            except Exception as e:
                self.log_test(f"LLM Integration - {test_case['mentor_id']}", False, f"Exception: {str(e)}")
                
    async def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Expanded Mentors Database Testing...")
        print(f"🔗 Backend URL: {BACKEND_URL}")
        print("=" * 80)
        
        await self.setup_session()
        
        try:
            # Setup authentication
            if await self.authenticate_user():
                # Run all tests
                await self.test_updated_mentor_counts()
                await self.test_new_mentors_accessibility()
                await self.test_search_functionality()
                await self.test_sample_new_mentors()
                await self.test_llm_integration_new_mentors()
            else:
                print("❌ Authentication failed - skipping authenticated tests")
                
        finally:
            await self.cleanup_session()
            
        # Print summary
        print("=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        for result in self.test_results:
            print(result)
            
        print("=" * 80)
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        print(f"✅ PASSED: {self.passed_tests}/{self.total_tests} ({success_rate:.1f}%)")
        
        if success_rate >= 80:
            print("🎉 EXPANDED MENTORS DATABASE TESTING SUCCESSFUL!")
        elif success_rate >= 60:
            print("⚠️  EXPANDED MENTORS DATABASE TESTING PARTIALLY SUCCESSFUL")
        else:
            print("❌ EXPANDED MENTORS DATABASE TESTING FAILED")
            
        return success_rate >= 80

async def main():
    """Main test runner"""
    tester = ExpandedMentorsTest()
    success = await tester.run_all_tests()
    return success

if __name__ == "__main__":
    asyncio.run(main())