#!/usr/bin/env python3
"""
Expanded Mentor Database Testing for OnlyMentors.ai
Testing Option 1 completion: Mentor Data & Photos Enhancement

This test verifies:
1. Expanded mentor counts across all categories
2. Wikipedia image integration
3. API endpoint functionality with larger database
4. Access to newly added mentors
5. Image URL availability
"""

import requests
import sys
import json
import time
from datetime import datetime

class ExpandedMentorDatabaseTester:
    def __init__(self, base_url="https://mentor-hub-11.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.user_data = None
        self.tests_run = 0
        self.tests_passed = 0
        self.mentor_counts = {}
        self.image_stats = {"with_images": 0, "without_images": 0}
        
        # Expected mentor counts based on review request
        self.expected_counts = {
            "business": {"min": 70, "target": 77},
            "sports": {"min": 40, "target": 48},
            "health": {"min": 25, "target": 30},
            "science": {"min": 30, "target": 35},
            "relationships": {"min": 15, "target": 20}
        }
        self.expected_total = {"min": 200, "target": 210}

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'
        
        if headers:
            test_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=30)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_expanded_mentor_counts(self):
        """Test 1: Verify expanded mentor counts across all categories"""
        print("\n" + "="*60)
        print("🔍 TESTING EXPANDED MENTOR COUNTS")
        print("="*60)
        
        success, response = self.run_test("Categories with Expanded Counts", "GET", "api/categories", 200)
        if not success:
            return False
            
        categories = response.get('categories', [])
        total_mentors = response.get('total_mentors', 0)
        
        print(f"\n📊 MENTOR COUNT ANALYSIS:")
        print(f"   Total mentors reported: {total_mentors}")
        
        all_counts_good = True
        actual_total = 0
        
        for category in categories:
            cat_id = category['id']
            count = category['count']
            actual_total += count
            self.mentor_counts[cat_id] = count
            
            if cat_id in self.expected_counts:
                expected = self.expected_counts[cat_id]
                status = "✅" if count >= expected['min'] else "❌"
                print(f"   {cat_id.capitalize()}: {count} mentors {status}")
                print(f"      Expected: {expected['min']}-{expected['target']}, Got: {count}")
                
                if count < expected['min']:
                    all_counts_good = False
            else:
                print(f"   {cat_id.capitalize()}: {count} mentors ✅")
        
        print(f"\n   Calculated Total: {actual_total}")
        print(f"   Expected Total: {self.expected_total['min']}-{self.expected_total['target']}")
        
        if actual_total >= self.expected_total['min']:
            print(f"✅ Total mentor count meets expectations ({actual_total} >= {self.expected_total['min']})")
        else:
            print(f"❌ Total mentor count below expectations ({actual_total} < {self.expected_total['min']})")
            all_counts_good = False
            
        return all_counts_good

    def test_wikipedia_image_integration(self):
        """Test 2: Check Wikipedia image integration across mentors"""
        print("\n" + "="*60)
        print("🔍 TESTING WIKIPEDIA IMAGE INTEGRATION")
        print("="*60)
        
        success, response = self.run_test("Categories for Image Analysis", "GET", "api/categories", 200)
        if not success:
            return False
            
        categories = response.get('categories', [])
        
        for category in categories:
            cat_id = category['id']
            mentors = category.get('mentors', [])
            
            print(f"\n📸 Analyzing images in {cat_id.capitalize()} category ({len(mentors)} mentors):")
            
            with_images = 0
            without_images = 0
            sample_images = []
            
            for mentor in mentors[:10]:  # Check first 10 mentors per category
                image_url = mentor.get('image_url')
                if image_url and image_url != "None" and image_url.strip():
                    with_images += 1
                    if len(sample_images) < 3:
                        sample_images.append(f"{mentor['name']}: {image_url[:50]}...")
                else:
                    without_images += 1
            
            self.image_stats['with_images'] += with_images
            self.image_stats['without_images'] += without_images
            
            print(f"   With images: {with_images}/{len(mentors[:10])}")
            print(f"   Without images: {without_images}/{len(mentors[:10])}")
            
            if sample_images:
                print(f"   Sample image URLs:")
                for sample in sample_images:
                    print(f"      {sample}")
        
        total_checked = self.image_stats['with_images'] + self.image_stats['without_images']
        image_percentage = (self.image_stats['with_images'] / total_checked * 100) if total_checked > 0 else 0
        
        print(f"\n📊 OVERALL IMAGE STATISTICS:")
        print(f"   Total mentors checked: {total_checked}")
        print(f"   With images: {self.image_stats['with_images']} ({image_percentage:.1f}%)")
        print(f"   Without images: {self.image_stats['without_images']}")
        
        # Consider test passed if at least some mentors have images
        return self.image_stats['with_images'] > 0

    def test_api_endpoints_with_expanded_database(self):
        """Test 3: Verify all mentor-related endpoints work with expanded database"""
        print("\n" + "="*60)
        print("🔍 TESTING API ENDPOINTS WITH EXPANDED DATABASE")
        print("="*60)
        
        all_passed = True
        
        # Test 3.1: Categories endpoint
        success, response = self.run_test("GET /api/categories", "GET", "api/categories", 200)
        if success:
            categories = response.get('categories', [])
            print(f"   ✅ Categories endpoint returns {len(categories)} categories")
        else:
            all_passed = False
        
        # Test 3.2: Category-specific mentor endpoints
        for cat_id in ['business', 'sports', 'health', 'science', 'relationships']:
            success, response = self.run_test(
                f"GET /api/categories/{cat_id}/mentors", 
                "GET", 
                f"api/categories/{cat_id}/mentors", 
                200
            )
            if success:
                mentors = response.get('mentors', [])
                count = response.get('count', 0)
                print(f"   ✅ {cat_id.capitalize()} category returns {count} mentors")
            else:
                all_passed = False
        
        # Test 3.3: Search endpoint with expanded database
        success, response = self.run_test("Search All Mentors", "GET", "api/search/mentors", 200)
        if success:
            results = response.get('results', [])
            count = response.get('count', 0)
            print(f"   ✅ Search returns {count} total mentors")
            
            if count >= self.expected_total['min']:
                print(f"   ✅ Search count meets expectations ({count} >= {self.expected_total['min']})")
            else:
                print(f"   ❌ Search count below expectations ({count} < {self.expected_total['min']})")
                all_passed = False
        else:
            all_passed = False
        
        # Test 3.4: Category-filtered search
        for cat_id in ['business', 'sports']:
            success, response = self.run_test(
                f"Search {cat_id.capitalize()} Mentors", 
                "GET", 
                f"api/search/mentors?category={cat_id}", 
                200
            )
            if success:
                results = response.get('results', [])
                count = response.get('count', 0)
                print(f"   ✅ {cat_id.capitalize()} search returns {count} mentors")
            else:
                all_passed = False
        
        return all_passed

    def test_new_mentor_access(self):
        """Test 4: Verify access to newly added mentors"""
        print("\n" + "="*60)
        print("🔍 TESTING ACCESS TO NEWLY ADDED MENTORS")
        print("="*60)
        
        # Test specific mentors mentioned in the review request
        test_mentors = {
            "business": ["tony_robbins", "simon_sinek", "seth_godin", "jamie_dimon", "ray_dalio"],
            "sports": ["tom_brady", "kobe_bryant", "wayne_gretzky", "lebron_james"],
            "health": ["joe_dispenza", "wim_hof", "ben_greenfield", "deepak_chopra", "mark_hyman"],
            "science": ["nikola_tesla", "alan_turing", "tim_berners_lee", "neil_degrasse_tyson", "michio_kaku"]
        }
        
        all_found = True
        found_mentors = []
        missing_mentors = []
        
        for category, mentor_ids in test_mentors.items():
            print(f"\n🔍 Checking {category.capitalize()} mentors:")
            
            success, response = self.run_test(
                f"Get {category.capitalize()} Mentors", 
                "GET", 
                f"api/categories/{category}/mentors", 
                200
            )
            
            if success:
                mentors = response.get('mentors', [])
                mentor_id_list = [m['id'] for m in mentors]
                
                for mentor_id in mentor_ids:
                    if mentor_id in mentor_id_list:
                        mentor_data = next(m for m in mentors if m['id'] == mentor_id)
                        found_mentors.append(f"{mentor_data['name']} ({category})")
                        print(f"   ✅ Found: {mentor_data['name']}")
                    else:
                        missing_mentors.append(f"{mentor_id} ({category})")
                        print(f"   ❌ Missing: {mentor_id}")
                        all_found = False
            else:
                all_found = False
        
        print(f"\n📊 NEW MENTOR ACCESS SUMMARY:")
        print(f"   Found mentors: {len(found_mentors)}")
        print(f"   Missing mentors: {len(missing_mentors)}")
        
        if found_mentors:
            print(f"   ✅ Successfully found:")
            for mentor in found_mentors[:10]:  # Show first 10
                print(f"      {mentor}")
        
        if missing_mentors:
            print(f"   ❌ Missing mentors:")
            for mentor in missing_mentors:
                print(f"      {mentor}")
        
        return len(found_mentors) > len(missing_mentors)  # Pass if more found than missing

    def test_mentor_search_functionality(self):
        """Test 5: Test search functionality with specific mentor names"""
        print("\n" + "="*60)
        print("🔍 TESTING MENTOR SEARCH FUNCTIONALITY")
        print("="*60)
        
        search_tests = [
            ("Warren Buffett", "warren_buffett"),
            ("Tony Robbins", "tony_robbins"),
            ("Tom Brady", "tom_brady"),
            ("Neil deGrasse Tyson", "neil_degrasse_tyson"),
            ("Deepak Chopra", "deepak_chopra")
        ]
        
        all_passed = True
        
        for search_term, expected_id in search_tests:
            success, response = self.run_test(
                f"Search for '{search_term}'", 
                "GET", 
                f"api/search/mentors?q={search_term.replace(' ', '%20')}", 
                200
            )
            
            if success:
                results = response.get('results', [])
                found = any(mentor['id'] == expected_id for mentor in results)
                
                if found:
                    mentor = next(m for m in results if m['id'] == expected_id)
                    print(f"   ✅ Found {mentor['name']} in {mentor.get('category', 'unknown')} category")
                else:
                    print(f"   ❌ Could not find {search_term} (expected ID: {expected_id})")
                    all_passed = False
            else:
                all_passed = False
        
        return all_passed

    def test_image_url_quality(self):
        """Test 6: Check quality and validity of image URLs"""
        print("\n" + "="*60)
        print("🔍 TESTING IMAGE URL QUALITY")
        print("="*60)
        
        success, response = self.run_test("Get Categories for Image Testing", "GET", "api/categories", 200)
        if not success:
            return False
        
        categories = response.get('categories', [])
        valid_urls = 0
        invalid_urls = 0
        wikipedia_urls = 0
        
        for category in categories:
            mentors = category.get('mentors', [])
            
            for mentor in mentors[:5]:  # Check first 5 per category
                image_url = mentor.get('image_url')
                
                if image_url and image_url != "None" and image_url.strip():
                    # Check if it's a valid URL format
                    if image_url.startswith(('http://', 'https://')):
                        valid_urls += 1
                        
                        # Check if it's from Wikipedia
                        if 'wikipedia' in image_url.lower() or 'wikimedia' in image_url.lower():
                            wikipedia_urls += 1
                            print(f"   ✅ Wikipedia image: {mentor['name']}")
                    else:
                        invalid_urls += 1
                        print(f"   ❌ Invalid URL format: {mentor['name']} - {image_url}")
        
        total_checked = valid_urls + invalid_urls
        
        print(f"\n📊 IMAGE URL QUALITY SUMMARY:")
        print(f"   Total URLs checked: {total_checked}")
        print(f"   Valid URLs: {valid_urls}")
        print(f"   Invalid URLs: {invalid_urls}")
        print(f"   Wikipedia/Wikimedia URLs: {wikipedia_urls}")
        
        if wikipedia_urls > 0:
            print(f"   ✅ Wikipedia integration working - found {wikipedia_urls} Wikipedia images")
        
        return valid_urls > invalid_urls

    def signup_test_user(self):
        """Create a test user for authenticated endpoints"""
        test_email = f"expanded_test_{int(time.time())}@onlymentors.ai"
        test_password = "ExpandedTest123!"
        test_name = "Expanded Database Tester"
        
        success, response = self.run_test(
            "Create Test User",
            "POST",
            "api/auth/signup",
            200,
            data={"email": test_email, "password": test_password, "full_name": test_name}
        )
        
        if success and 'token' in response:
            self.token = response['token']
            self.user_data = response['user']
            print(f"✅ Test user created: {test_email}")
            return True
        else:
            print(f"❌ Failed to create test user")
            return False

    def test_question_asking_with_new_mentors(self):
        """Test 7: Test asking questions to newly added mentors"""
        print("\n" + "="*60)
        print("🔍 TESTING QUESTION ASKING WITH NEW MENTORS")
        print("="*60)
        
        if not self.token:
            if not self.signup_test_user():
                return False
        
        # Test asking questions to some new mentors
        test_questions = [
            {
                "category": "business",
                "mentor_ids": ["tony_robbins"],
                "question": "What are the key principles for achieving peak performance in business?"
            },
            {
                "category": "sports", 
                "mentor_ids": ["tom_brady"],
                "question": "How do you maintain excellence and longevity in competitive sports?"
            },
            {
                "category": "health",
                "mentor_ids": ["joe_dispenza"],
                "question": "How can meditation and mindfulness transform our health and well-being?"
            }
        ]
        
        all_passed = True
        
        for i, test_q in enumerate(test_questions):
            success, response = self.run_test(
                f"Ask Question to {test_q['mentor_ids'][0]}",
                "POST",
                "api/questions/ask",
                200,
                data=test_q
            )
            
            if success:
                responses = response.get('responses', [])
                if responses:
                    mentor_response = responses[0]
                    mentor_name = mentor_response['mentor']['name']
                    response_text = mentor_response['response']
                    print(f"   ✅ Got response from {mentor_name} ({len(response_text)} chars)")
                    
                    # Check if response seems authentic (not just fallback)
                    if len(response_text) > 200:
                        print(f"   ✅ Response appears substantial and authentic")
                    else:
                        print(f"   ⚠️  Response seems short, might be fallback")
                else:
                    print(f"   ❌ No response received")
                    all_passed = False
            else:
                all_passed = False
            
            # Small delay between requests
            time.sleep(1)
        
        return all_passed

    def run_all_tests(self):
        """Run all expanded mentor database tests"""
        print("🚀 STARTING EXPANDED MENTOR DATABASE TESTING")
        print("="*80)
        print(f"Testing against: {self.base_url}")
        print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        test_results = []
        
        # Test 1: Expanded Mentor Counts
        result1 = self.test_expanded_mentor_counts()
        test_results.append(("Expanded Mentor Counts", result1))
        
        # Test 2: Wikipedia Image Integration
        result2 = self.test_wikipedia_image_integration()
        test_results.append(("Wikipedia Image Integration", result2))
        
        # Test 3: API Endpoints with Expanded Database
        result3 = self.test_api_endpoints_with_expanded_database()
        test_results.append(("API Endpoints with Expanded Database", result3))
        
        # Test 4: New Mentor Access
        result4 = self.test_new_mentor_access()
        test_results.append(("New Mentor Access", result4))
        
        # Test 5: Mentor Search Functionality
        result5 = self.test_mentor_search_functionality()
        test_results.append(("Mentor Search Functionality", result5))
        
        # Test 6: Image URL Quality
        result6 = self.test_image_url_quality()
        test_results.append(("Image URL Quality", result6))
        
        # Test 7: Question Asking with New Mentors
        result7 = self.test_question_asking_with_new_mentors()
        test_results.append(("Question Asking with New Mentors", result7))
        
        # Print final results
        print("\n" + "="*80)
        print("🏁 EXPANDED MENTOR DATABASE TEST RESULTS")
        print("="*80)
        
        passed_tests = sum(1 for _, result in test_results if result)
        total_tests = len(test_results)
        
        for test_name, result in test_results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{status} - {test_name}")
        
        print(f"\n📊 OVERALL RESULTS:")
        print(f"   Tests Passed: {passed_tests}/{total_tests} ({passed_tests/total_tests*100:.1f}%)")
        print(f"   API Calls Made: {self.tests_run}")
        print(f"   API Calls Successful: {self.tests_passed}")
        
        print(f"\n📈 MENTOR DATABASE STATISTICS:")
        for category, count in self.mentor_counts.items():
            expected = self.expected_counts.get(category, {})
            target = expected.get('target', 'N/A')
            print(f"   {category.capitalize()}: {count} mentors (target: {target})")
        
        total_actual = sum(self.mentor_counts.values())
        print(f"   Total: {total_actual} mentors (target: {self.expected_total['target']})")
        
        if self.image_stats['with_images'] > 0:
            print(f"\n🖼️  IMAGE INTEGRATION:")
            print(f"   Mentors with images: {self.image_stats['with_images']}")
            print(f"   Mentors without images: {self.image_stats['without_images']}")
        
        print(f"\n⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Return overall success
        return passed_tests >= (total_tests * 0.7)  # 70% pass rate required

if __name__ == "__main__":
    tester = ExpandedMentorDatabaseTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 EXPANDED MENTOR DATABASE TESTING COMPLETED SUCCESSFULLY!")
        sys.exit(0)
    else:
        print("\n❌ EXPANDED MENTOR DATABASE TESTING FAILED!")
        sys.exit(1)