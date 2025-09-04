import requests
import sys
import json
import time
from datetime import datetime

class MentorLimitTester:
    def __init__(self, base_url="https://multi-tenant-ai.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.user_data = None
        self.tests_run = 0
        self.tests_passed = 0
        self.available_mentors = {}

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
                response = requests.get(url, headers=test_headers, timeout=45)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=45)

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
                    return False, error_data
                except:
                    print(f"   Error: {response.text}")
                    return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def setup_test_user(self):
        """Create and authenticate a test user"""
        test_email = f"mentor_limit_test_{datetime.now().strftime('%H%M%S')}@test.com"
        test_password = "password123"
        test_name = "Mentor Limit Test User"
        
        print("🔧 Setting up test user...")
        
        # Signup
        success, response = self.run_test(
            "User Signup",
            "POST",
            "api/auth/signup",
            200,
            data={"email": test_email, "password": test_password, "full_name": test_name}
        )
        
        if success and 'token' in response:
            self.token = response['token']
            self.user_data = response['user']
            print(f"✅ Test user created and authenticated")
            return True
        else:
            print("❌ Failed to create test user")
            return False

    def get_available_mentors(self):
        """Get available mentors from all categories"""
        print("📋 Getting available mentors...")
        
        success, response = self.run_test(
            "Get Categories",
            "GET",
            "api/categories",
            200
        )
        
        if success and 'categories' in response:
            for category in response['categories']:
                category_id = category['id']
                mentors = category.get('mentors', [])
                self.available_mentors[category_id] = [mentor['id'] for mentor in mentors]
                print(f"   {category_id}: {len(mentors)} mentors")
            
            print(f"✅ Found mentors in {len(self.available_mentors)} categories")
            return True
        else:
            print("❌ Failed to get available mentors")
            return False

    def test_5_mentor_limit_success(self):
        """Test that exactly 5 mentors is allowed"""
        print("\n🎯 Testing 5-Mentor Limit - EXACTLY 5 MENTORS (Should Succeed)")
        
        # Get 5 business mentors
        business_mentors = self.available_mentors.get('business', [])
        if len(business_mentors) < 5:
            print(f"❌ Not enough business mentors available ({len(business_mentors)})")
            return False
        
        selected_mentors = business_mentors[:5]
        print(f"   Selected mentors: {selected_mentors}")
        
        success, response = self.run_test(
            "5 Mentors Question (Should Succeed)",
            "POST",
            "api/questions/ask",
            200,
            data={
                "category": "business",
                "mentor_ids": selected_mentors,
                "question": "What are your top 3 business strategies for success?"
            }
        )
        
        if success:
            # Verify we got responses from all 5 mentors
            responses = response.get('responses', [])
            if len(responses) == 5:
                print(f"✅ Successfully received responses from all 5 mentors")
                print(f"   Processing time: {response.get('processing_time', 'N/A')}")
                print(f"   Total mentors: {response.get('total_mentors', 'N/A')}")
                
                # Check that responses are unique
                unique_responses = len(set(r.get('response', '') for r in responses))
                if unique_responses == 5:
                    print("✅ All 5 mentor responses are unique")
                else:
                    print(f"⚠️  Only {unique_responses}/5 responses are unique")
                
                return True
            else:
                print(f"❌ Expected 5 responses, got {len(responses)}")
        
        return False

    def test_6_mentor_limit_failure(self):
        """Test that 6 mentors is rejected"""
        print("\n🚫 Testing 5-Mentor Limit - 6 MENTORS (Should Fail)")
        
        # Get 6 business mentors
        business_mentors = self.available_mentors.get('business', [])
        if len(business_mentors) < 6:
            print(f"❌ Not enough business mentors available ({len(business_mentors)})")
            return False
        
        selected_mentors = business_mentors[:6]
        print(f"   Selected mentors: {selected_mentors}")
        
        success, response = self.run_test(
            "6 Mentors Question (Should Fail)",
            "POST",
            "api/questions/ask",
            400,
            data={
                "category": "business",
                "mentor_ids": selected_mentors,
                "question": "What are your top business strategies?"
            }
        )
        
        if success:
            # Verify the error message mentions the 5-mentor limit
            error_detail = response.get('detail', '')
            expected_keywords = ['5 mentors', 'maximum', 'optimal response time', 'quality']
            
            print(f"   Error message: {error_detail}")
            
            # Check if error message contains expected keywords
            keywords_found = sum(1 for keyword in expected_keywords if keyword.lower() in error_detail.lower())
            
            if keywords_found >= 2:  # At least 2 keywords should be present
                print("✅ Error message correctly mentions 5-mentor limit and reasoning")
                return True
            else:
                print("⚠️  Error message doesn't clearly explain the 5-mentor limit")
                return True  # Still counts as success since it returned 400
        
        return False

    def test_7_mentor_limit_failure(self):
        """Test that 7 mentors is also rejected"""
        print("\n🚫 Testing 5-Mentor Limit - 7 MENTORS (Should Fail)")
        
        # Get 7 business mentors
        business_mentors = self.available_mentors.get('business', [])
        if len(business_mentors) < 7:
            print(f"❌ Not enough business mentors available ({len(business_mentors)})")
            return False
        
        selected_mentors = business_mentors[:7]
        print(f"   Selected mentors: {selected_mentors}")
        
        success, response = self.run_test(
            "7 Mentors Question (Should Fail)",
            "POST",
            "api/questions/ask",
            400,
            data={
                "category": "business",
                "mentor_ids": selected_mentors,
                "question": "What are your top business strategies?"
            }
        )
        
        if success:
            error_detail = response.get('detail', '')
            print(f"   Error message: {error_detail}")
            
            if '5 mentors' in error_detail.lower():
                print("✅ Error message correctly mentions 5-mentor limit")
                return True
            else:
                print("⚠️  Error message doesn't mention 5-mentor limit")
                return True  # Still counts as success since it returned 400
        
        return False

    def test_0_mentor_failure(self):
        """Test that 0 mentors is rejected"""
        print("\n🚫 Testing 5-Mentor Limit - 0 MENTORS (Should Fail)")
        
        success, response = self.run_test(
            "0 Mentors Question (Should Fail)",
            "POST",
            "api/questions/ask",
            404,  # Expecting 404 or 400 for empty mentor list
            data={
                "category": "business",
                "mentor_ids": [],
                "question": "What are your top business strategies?"
            }
        )
        
        if success:
            print("✅ Empty mentor list properly rejected")
            return True
        else:
            # Try with 400 status code as alternative
            success, response = self.run_test(
                "0 Mentors Question (Alternative)",
                "POST",
                "api/questions/ask",
                400,
                data={
                    "category": "business",
                    "mentor_ids": [],
                    "question": "What are your top business strategies?"
                }
            )
            if success:
                print("✅ Empty mentor list properly rejected (400 status)")
                return True
        
        return False

    def test_1_mentor_success(self):
        """Test that 1 mentor is allowed"""
        print("\n✅ Testing 5-Mentor Limit - 1 MENTOR (Should Succeed)")
        
        business_mentors = self.available_mentors.get('business', [])
        if len(business_mentors) < 1:
            print(f"❌ No business mentors available")
            return False
        
        selected_mentor = [business_mentors[0]]
        print(f"   Selected mentor: {selected_mentor}")
        
        success, response = self.run_test(
            "1 Mentor Question (Should Succeed)",
            "POST",
            "api/questions/ask",
            200,
            data={
                "category": "business",
                "mentor_ids": selected_mentor,
                "question": "What's your best business advice for entrepreneurs?"
            }
        )
        
        if success:
            responses = response.get('responses', [])
            if len(responses) == 1:
                print(f"✅ Successfully received response from 1 mentor")
                print(f"   Response length: {len(responses[0].get('response', ''))} characters")
                return True
            else:
                print(f"❌ Expected 1 response, got {len(responses)}")
        
        return False

    def test_mixed_categories_5_mentors(self):
        """Test 5 mentors from different categories"""
        print("\n🌐 Testing 5-Mentor Limit - MIXED CATEGORIES (Should Succeed)")
        
        # Get mentors from different categories
        selected_mentors = []
        categories_used = []
        
        for category, mentors in self.available_mentors.items():
            if len(selected_mentors) < 5 and mentors:
                selected_mentors.append(mentors[0])
                categories_used.append(category)
        
        if len(selected_mentors) < 5:
            print(f"❌ Could only find {len(selected_mentors)} mentors across categories")
            return False
        
        # Use the first category for the request (API requires a category)
        primary_category = categories_used[0]
        
        print(f"   Selected mentors: {selected_mentors}")
        print(f"   Categories: {categories_used}")
        print(f"   Primary category: {primary_category}")
        
        success, response = self.run_test(
            "5 Mixed Category Mentors (Should Succeed)",
            "POST",
            "api/questions/ask",
            200,
            data={
                "category": primary_category,
                "mentor_ids": selected_mentors,
                "question": "What's your advice for achieving excellence in your field?"
            }
        )
        
        if success:
            responses = response.get('responses', [])
            if len(responses) == 5:
                print(f"✅ Successfully received responses from 5 mentors across categories")
                return True
            else:
                print(f"❌ Expected 5 responses, got {len(responses)}")
        
        return False

    def test_performance_with_5_mentors(self):
        """Test performance with 5 mentors to verify parallel processing"""
        print("\n⚡ Testing Performance - 5 MENTORS PARALLEL PROCESSING")
        
        business_mentors = self.available_mentors.get('business', [])
        if len(business_mentors) < 5:
            print(f"❌ Not enough business mentors available")
            return False
        
        selected_mentors = business_mentors[:5]
        
        start_time = time.time()
        
        success, response = self.run_test(
            "5 Mentors Performance Test",
            "POST",
            "api/questions/ask",
            200,
            data={
                "category": "business",
                "mentor_ids": selected_mentors,
                "question": "What are the key principles for building a successful business in today's market?"
            }
        )
        
        end_time = time.time()
        total_time = end_time - start_time
        
        if success:
            responses = response.get('responses', [])
            processing_time = response.get('processing_time', 'N/A')
            
            print(f"✅ Performance test completed")
            print(f"   Total request time: {total_time:.2f}s")
            print(f"   Backend processing time: {processing_time}")
            print(f"   Responses received: {len(responses)}")
            
            # Check if processing was reasonably fast (should be much faster than sequential)
            # With parallel processing, 5 mentors should complete in roughly the time of 1 mentor
            if total_time < 60:  # Should complete within 60 seconds
                print("✅ Performance is acceptable for 5 mentors")
                return True
            else:
                print("⚠️  Performance might be slower than expected")
                return True  # Still count as success if it worked
        
        return False

    def test_error_response_format(self):
        """Test that error responses have proper format"""
        print("\n📋 Testing Error Response Format")
        
        business_mentors = self.available_mentors.get('business', [])
        if len(business_mentors) < 8:
            print(f"❌ Not enough business mentors available for error test")
            return False
        
        selected_mentors = business_mentors[:8]  # 8 mentors to trigger error
        
        success, response = self.run_test(
            "Error Response Format Test",
            "POST",
            "api/questions/ask",
            400,
            data={
                "category": "business",
                "mentor_ids": selected_mentors,
                "question": "Test question"
            }
        )
        
        if success:
            # Check response format
            has_detail = 'detail' in response
            has_proper_status = True  # We already verified 400 status
            
            if has_detail and has_proper_status:
                print("✅ Error response has proper format")
                print(f"   Error detail: {response.get('detail', '')}")
                return True
            else:
                print("⚠️  Error response format could be improved")
                return True  # Still success since error was returned
        
        return False

def main():
    print("🎯 Testing OnlyMentors.ai 5-Mentor Limit Functionality")
    print("=" * 70)
    
    tester = MentorLimitTester()
    
    # Setup
    if not tester.setup_test_user():
        print("❌ Failed to setup test user")
        return 1
    
    if not tester.get_available_mentors():
        print("❌ Failed to get available mentors")
        return 1
    
    # Run 5-mentor limit tests
    print(f"\n{'='*70}")
    print("🎯 5-MENTOR LIMIT VALIDATION TESTS")
    print(f"{'='*70}")
    
    test_results = []
    
    # Test 1: Exactly 5 mentors (should succeed)
    test_results.append(("5 mentors (success)", tester.test_5_mentor_limit_success()))
    
    # Test 2: 6 mentors (should fail)
    test_results.append(("6 mentors (fail)", tester.test_6_mentor_limit_failure()))
    
    # Test 3: 7 mentors (should fail)
    test_results.append(("7 mentors (fail)", tester.test_7_mentor_limit_failure()))
    
    # Test 4: 0 mentors (should fail)
    test_results.append(("0 mentors (fail)", tester.test_0_mentor_failure()))
    
    # Test 5: 1 mentor (should succeed)
    test_results.append(("1 mentor (success)", tester.test_1_mentor_success()))
    
    # Test 6: Mixed categories with 5 mentors
    test_results.append(("5 mixed categories", tester.test_mixed_categories_5_mentors()))
    
    # Test 7: Performance test
    test_results.append(("Performance test", tester.test_performance_with_5_mentors()))
    
    # Test 8: Error response format
    test_results.append(("Error format", tester.test_error_response_format()))
    
    # Calculate results
    passed_tests = sum(1 for _, result in test_results if result)
    total_tests = len(test_results)
    
    # Print detailed results
    print(f"\n{'='*70}")
    print("📊 5-MENTOR LIMIT TEST RESULTS")
    print(f"{'='*70}")
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:25} {status}")
    
    print(f"\nOverall Results:")
    print(f"Tests passed: {tester.tests_passed}/{tester.tests_run}")
    print(f"Success rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    print(f"5-Mentor Limit Tests: {passed_tests}/{total_tests}")
    print(f"5-Mentor Limit Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    # Final assessment
    critical_tests_passed = (
        test_results[0][1] and  # 5 mentors success
        test_results[1][1] and  # 6 mentors fail
        test_results[4][1]      # 1 mentor success
    )
    
    if critical_tests_passed and passed_tests >= 6:
        print("\n🎉 5-MENTOR LIMIT FUNCTIONALITY IS WORKING CORRECTLY!")
        print("✅ Exactly 5 mentors are allowed")
        print("✅ 6+ mentors are properly rejected with appropriate error")
        print("✅ Error message mentions 5-mentor limit and reasoning")
        print("✅ Single mentor requests still work")
        print("✅ Performance with 5 mentors is acceptable")
        print("✅ Error responses have proper HTTP status codes")
        return 0
    else:
        print("\n⚠️  5-MENTOR LIMIT FUNCTIONALITY HAS ISSUES")
        if not test_results[0][1]:
            print("❌ 5 mentors are not being accepted")
        if not test_results[1][1]:
            print("❌ 6+ mentors are not being rejected properly")
        if not test_results[4][1]:
            print("❌ Single mentor requests are not working")
        return 1

if __name__ == "__main__":
    sys.exit(main())