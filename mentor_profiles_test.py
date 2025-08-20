import requests
import sys
import json
import time
from datetime import datetime

class MentorProfilesAPITester:
    def __init__(self, base_url="https://admin-role-system.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.user_data = None
        self.tests_run = 0
        self.tests_passed = 0
        self.mentor_data_issues = []
        self.backend_errors = []

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        if endpoint == "":
            url = self.base_url
        elif endpoint.startswith('api/'):
            url = f"{self.base_url}/{endpoint}"
        else:
            url = f"{self.base_url}/api/{endpoint}"
            
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
                    self.backend_errors.append({
                        'test': name,
                        'status_code': response.status_code,
                        'error': error_data
                    })
                except:
                    print(f"   Error: {response.text}")
                    self.backend_errors.append({
                        'test': name,
                        'status_code': response.status_code,
                        'error': response.text
                    })
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.backend_errors.append({
                'test': name,
                'error': str(e)
            })
            return False, {}

    def test_categories_endpoint(self):
        """Test GET /api/categories endpoint - should return all mentor categories"""
        print(f"\n🏷️ TESTING CATEGORIES ENDPOINT")
        print("=" * 60)
        
        success, response = self.run_test("GET /api/categories", "GET", "api/categories", 200)
        
        if not success:
            print("❌ CRITICAL: Categories endpoint is not accessible")
            return False, {}
        
        # Validate response structure
        if 'categories' not in response:
            print("❌ CRITICAL: Response missing 'categories' field")
            self.mentor_data_issues.append("Categories endpoint missing 'categories' field")
            return False, response
        
        categories = response['categories']
        print(f"✅ Categories endpoint accessible - Found {len(categories)} categories")
        
        # Check for expected categories
        expected_categories = ['business', 'sports', 'health', 'science', 'relationships']
        found_category_ids = [cat.get('id', '') for cat in categories]
        
        print(f"   Expected categories: {expected_categories}")
        print(f"   Found categories: {found_category_ids}")
        
        missing_categories = [cat for cat in expected_categories if cat not in found_category_ids]
        if missing_categories:
            print(f"⚠️  Missing categories: {missing_categories}")
            self.mentor_data_issues.append(f"Missing categories: {missing_categories}")
        else:
            print("✅ All expected categories found")
        
        # Validate total mentors count
        total_mentors = response.get('total_mentors', 0)
        print(f"   Total mentors reported: {total_mentors}")
        
        if total_mentors == 0:
            print("❌ CRITICAL: Total mentors count is 0")
            self.mentor_data_issues.append("Total mentors count is 0")
        elif total_mentors < 50:
            print(f"⚠️  Low mentor count: {total_mentors}")
            self.mentor_data_issues.append(f"Low mentor count: {total_mentors}")
        else:
            print(f"✅ Good mentor count: {total_mentors}")
        
        return True, response

    def validate_mentor_data_structure(self, mentor, category_name):
        """Validate that mentor has all required fields for profile display"""
        required_fields = ['id', 'name', 'expertise', 'bio']
        recommended_fields = ['title', 'image_url', 'wiki_description', 'achievements']
        
        issues = []
        
        # Check required fields
        for field in required_fields:
            if field not in mentor or not mentor[field]:
                issues.append(f"Missing required field: {field}")
        
        # Check recommended fields
        missing_recommended = []
        for field in recommended_fields:
            if field not in mentor or not mentor[field]:
                missing_recommended.append(field)
        
        if missing_recommended:
            issues.append(f"Missing recommended fields: {missing_recommended}")
        
        # Validate field content quality
        if 'name' in mentor and mentor['name']:
            if len(mentor['name']) < 3:
                issues.append("Name too short")
        
        if 'bio' in mentor and mentor['bio']:
            if len(mentor['bio']) < 50:
                issues.append("Bio too short (less than 50 chars)")
        
        if 'expertise' in mentor and mentor['expertise']:
            if len(mentor['expertise']) < 10:
                issues.append("Expertise description too short")
        
        return issues

    def test_mentor_data_quality(self, categories_response):
        """Test that mentors have proper data for profile viewing"""
        print(f"\n👥 TESTING MENTOR DATA QUALITY")
        print("=" * 60)
        
        if not categories_response or 'categories' not in categories_response:
            print("❌ No categories data to test")
            return False
        
        categories = categories_response['categories']
        total_mentors_tested = 0
        mentors_with_issues = 0
        critical_issues = []
        
        for category in categories:
            category_name = category.get('name', 'Unknown')
            category_id = category.get('id', 'unknown')
            mentors = category.get('mentors', [])
            
            print(f"\n📂 Testing {category_name} category ({len(mentors)} mentors)")
            
            if not mentors:
                critical_issues.append(f"{category_name} category has no mentors")
                continue
            
            # Test first 5 mentors in each category for data quality
            sample_mentors = mentors[:5]
            
            for i, mentor in enumerate(sample_mentors):
                total_mentors_tested += 1
                mentor_name = mentor.get('name', f'Mentor {i+1}')
                
                # Validate mentor data structure
                issues = self.validate_mentor_data_structure(mentor, category_name)
                
                if issues:
                    mentors_with_issues += 1
                    print(f"   ⚠️  {mentor_name}: {len(issues)} issues")
                    for issue in issues[:3]:  # Show first 3 issues
                        print(f"      - {issue}")
                    
                    self.mentor_data_issues.extend([f"{mentor_name}: {issue}" for issue in issues])
                else:
                    print(f"   ✅ {mentor_name}: Data complete")
        
        print(f"\n📊 Mentor Data Quality Summary:")
        print(f"   Total mentors tested: {total_mentors_tested}")
        print(f"   Mentors with data issues: {mentors_with_issues}")
        print(f"   Data quality rate: {((total_mentors_tested - mentors_with_issues) / total_mentors_tested * 100):.1f}%")
        
        if critical_issues:
            print(f"   ❌ Critical issues: {len(critical_issues)}")
            for issue in critical_issues:
                print(f"      - {issue}")
        
        # Determine if mentor data quality is acceptable
        data_quality_acceptable = (
            total_mentors_tested > 0 and
            mentors_with_issues / total_mentors_tested < 0.5 and  # Less than 50% have issues
            len(critical_issues) == 0
        )
        
        if data_quality_acceptable:
            print("✅ Mentor data quality is acceptable for profile display")
        else:
            print("❌ Mentor data quality has significant issues")
        
        return data_quality_acceptable

    def test_specific_mentor_endpoints(self, categories_response):
        """Test specific mentor-related endpoints"""
        print(f"\n🔍 TESTING SPECIFIC MENTOR ENDPOINTS")
        print("=" * 60)
        
        if not categories_response or 'categories' not in categories_response:
            print("❌ No categories data to test specific endpoints")
            return False
        
        endpoints_tested = 0
        endpoints_passed = 0
        
        # Test category-specific mentor endpoints
        for category in categories_response['categories']:
            category_id = category.get('id', '')
            if not category_id:
                continue
                
            endpoints_tested += 1
            success, response = self.run_test(
                f"GET /api/categories/{category_id}/mentors",
                "GET",
                f"api/categories/{category_id}/mentors",
                200
            )
            
            if success:
                endpoints_passed += 1
                mentors = response.get('mentors', [])
                print(f"   ✅ {category_id}: {len(mentors)} mentors")
            else:
                print(f"   ❌ {category_id}: Endpoint failed")
        
        # Test mentor search endpoint
        endpoints_tested += 1
        success, response = self.run_test(
            "GET /api/search/mentors",
            "GET",
            "api/search/mentors",
            200
        )
        
        if success:
            endpoints_passed += 1
            results = response.get('results', [])
            print(f"   ✅ Search mentors: {len(results)} results")
        else:
            print(f"   ❌ Search mentors: Endpoint failed")
        
        # Test mentor search with query
        endpoints_tested += 1
        success, response = self.run_test(
            "GET /api/search/mentors?q=warren",
            "GET",
            "api/search/mentors?q=warren",
            200
        )
        
        if success:
            endpoints_passed += 1
            results = response.get('results', [])
            print(f"   ✅ Search 'warren': {len(results)} results")
            
            # Check if Warren Buffett is found
            warren_found = any('warren' in mentor.get('name', '').lower() for mentor in results)
            if warren_found:
                print(f"      ✅ Warren Buffett found in search results")
            else:
                print(f"      ⚠️  Warren Buffett not found in search results")
                self.mentor_data_issues.append("Warren Buffett not found in search")
        else:
            print(f"   ❌ Search 'warren': Endpoint failed")
        
        print(f"\n📊 Mentor Endpoints Summary:")
        print(f"   Endpoints tested: {endpoints_tested}")
        print(f"   Endpoints passed: {endpoints_passed}")
        print(f"   Success rate: {(endpoints_passed / endpoints_tested * 100):.1f}%")
        
        return endpoints_passed == endpoints_tested

    def test_backend_error_handling(self):
        """Test for backend errors that might prevent mentor data from being served"""
        print(f"\n🚨 TESTING BACKEND ERROR HANDLING")
        print("=" * 60)
        
        error_tests_passed = 0
        error_tests_total = 0
        
        # Test invalid category
        error_tests_total += 1
        success, response = self.run_test(
            "Invalid Category Test",
            "GET",
            "api/categories/invalid_category/mentors",
            404
        )
        if success:
            error_tests_passed += 1
            print("   ✅ Invalid category properly returns 404")
        
        # Test malformed search query
        error_tests_total += 1
        success, response = self.run_test(
            "Search with special characters",
            "GET",
            "api/search/mentors?q=%20%21%40%23",
            200  # Should handle gracefully
        )
        if success:
            error_tests_passed += 1
            print("   ✅ Search handles special characters gracefully")
        
        print(f"\n📊 Error Handling Summary:")
        print(f"   Error tests passed: {error_tests_passed}/{error_tests_total}")
        
        return error_tests_passed >= error_tests_total * 0.5  # At least 50% should pass

    def create_test_user_for_mentor_testing(self):
        """Create a test user to test mentor-related functionality that requires auth"""
        print(f"\n👤 CREATING TEST USER FOR MENTOR TESTING")
        print("=" * 60)
        
        timestamp = datetime.now().strftime('%H%M%S')
        test_email = f"mentor_test_{timestamp}@example.com"
        test_password = "MentorTest123!"
        test_name = "Mentor Test User"
        
        success, response = self.run_test(
            "Create Test User",
            "POST",
            "api/auth/signup",
            200,
            data={
                "email": test_email,
                "password": test_password,
                "full_name": test_name
            }
        )
        
        if success and 'token' in response:
            self.token = response['token']
            self.user_data = response['user']
            print(f"✅ Test user created successfully")
            print(f"   Email: {test_email}")
            print(f"   User ID: {self.user_data.get('user_id', 'N/A')}")
            return True
        else:
            print(f"❌ Failed to create test user")
            return False

    def test_mentor_question_functionality(self):
        """Test asking questions to mentors to verify backend integration"""
        print(f"\n💬 TESTING MENTOR QUESTION FUNCTIONALITY")
        print("=" * 60)
        
        if not self.token:
            print("❌ No authentication token - cannot test question functionality")
            return False
        
        # Test asking a question to Warren Buffett
        success, response = self.run_test(
            "Ask Question to Warren Buffett",
            "POST",
            "api/questions/ask",
            200,
            data={
                "category": "business",
                "mentor_ids": ["warren_buffett"],
                "question": "What is your best investment advice for beginners?"
            }
        )
        
        if success:
            if 'responses' in response and len(response['responses']) > 0:
                mentor_response = response['responses'][0]
                response_text = mentor_response.get('response', '')
                mentor_info = mentor_response.get('mentor', {})
                
                print(f"✅ Question successfully processed")
                print(f"   Mentor: {mentor_info.get('name', 'Unknown')}")
                print(f"   Response length: {len(response_text)} characters")
                print(f"   Response preview: {response_text[:200]}...")
                
                # Check if response looks authentic (not just error message)
                if len(response_text) > 100 and 'error' not in response_text.lower():
                    print("✅ Response appears to be authentic mentor response")
                    return True
                else:
                    print("⚠️  Response might be error or fallback message")
                    self.mentor_data_issues.append("Mentor responses may not be working properly")
            else:
                print("❌ No responses received from mentor")
                self.mentor_data_issues.append("No responses received from mentor question")
        else:
            print("❌ Failed to ask question to mentor")
        
        return success

    def run_comprehensive_mentor_profiles_test(self):
        """Run comprehensive test of mentor profiles API functionality"""
        print(f"\n{'='*80}")
        print("🧠 COMPREHENSIVE MENTOR PROFILES API TEST")
        print("Testing mentor profiles functionality for OnlyMentors.ai platform")
        print(f"{'='*80}")
        
        test_results = {
            'categories_endpoint': False,
            'mentor_data_quality': False,
            'specific_endpoints': False,
            'error_handling': False,
            'question_functionality': False
        }
        
        # Test 1: Categories endpoint
        print(f"\n🔍 TEST 1: Categories Endpoint Accessibility")
        success, categories_response = self.test_categories_endpoint()
        test_results['categories_endpoint'] = success
        
        if not success:
            print("❌ CRITICAL FAILURE: Cannot proceed without categories endpoint")
            return test_results
        
        # Test 2: Mentor data quality
        print(f"\n🔍 TEST 2: Mentor Data Structure and Quality")
        test_results['mentor_data_quality'] = self.test_mentor_data_quality(categories_response)
        
        # Test 3: Specific mentor endpoints
        print(f"\n🔍 TEST 3: Specific Mentor Endpoints")
        test_results['specific_endpoints'] = self.test_specific_mentor_endpoints(categories_response)
        
        # Test 4: Backend error handling
        print(f"\n🔍 TEST 4: Backend Error Handling")
        test_results['error_handling'] = self.test_backend_error_handling()
        
        # Test 5: Create test user and test question functionality
        print(f"\n🔍 TEST 5: Mentor Question Functionality")
        if self.create_test_user_for_mentor_testing():
            test_results['question_functionality'] = self.test_mentor_question_functionality()
        
        return test_results

    def generate_comprehensive_report(self, test_results):
        """Generate comprehensive report of mentor profiles testing"""
        print(f"\n{'='*80}")
        print("📊 MENTOR PROFILES API TEST REPORT")
        print(f"{'='*80}")
        
        # Test results summary
        print(f"\n🔍 Test Results Summary:")
        for test_name, passed in test_results.items():
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"   {test_name.replace('_', ' ').title()}: {status}")
        
        # Overall statistics
        total_tests = len(test_results)
        passed_tests = sum(test_results.values())
        success_rate = (passed_tests / total_tests) * 100
        
        print(f"\n📈 Overall Statistics:")
        print(f"   Total API Tests Run: {self.tests_run}")
        print(f"   Total API Tests Passed: {self.tests_passed}")
        print(f"   API Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        print(f"   Major Test Areas Passed: {passed_tests}/{total_tests}")
        print(f"   Major Test Success Rate: {success_rate:.1f}%")
        
        # Issues found
        if self.mentor_data_issues:
            print(f"\n⚠️  Mentor Data Issues Found ({len(self.mentor_data_issues)}):")
            for i, issue in enumerate(self.mentor_data_issues[:10], 1):  # Show first 10
                print(f"   {i}. {issue}")
            if len(self.mentor_data_issues) > 10:
                print(f"   ... and {len(self.mentor_data_issues) - 10} more issues")
        
        if self.backend_errors:
            print(f"\n🚨 Backend Errors Found ({len(self.backend_errors)}):")
            for i, error in enumerate(self.backend_errors[:5], 1):  # Show first 5
                print(f"   {i}. {error.get('test', 'Unknown')}: {error.get('error', 'Unknown error')}")
            if len(self.backend_errors) > 5:
                print(f"   ... and {len(self.backend_errors) - 5} more errors")
        
        # Final assessment
        critical_tests = ['categories_endpoint', 'mentor_data_quality']
        critical_passed = sum(test_results.get(test, False) for test in critical_tests)
        
        overall_success = (
            critical_passed == len(critical_tests) and  # All critical tests must pass
            passed_tests >= 3 and  # At least 3/5 tests must pass
            len(self.backend_errors) == 0  # No backend errors
        )
        
        print(f"\n🎯 FINAL ASSESSMENT:")
        if overall_success:
            print("🎉 MENTOR PROFILES API: ✅ WORKING CORRECTLY!")
            print("\n✅ Key Findings:")
            print("   • Categories endpoint accessible and returning data")
            print("   • Mentor data structure includes required fields")
            print("   • Mentors have proper data for profile display")
            print("   • No critical backend errors preventing data serving")
            print("   • Mentor-related endpoints functioning properly")
            
            if test_results.get('question_functionality'):
                print("   • Mentor question functionality working")
            
            print(f"\n🚀 The mentor profiles API is working correctly!")
            print("   Frontend Avatar errors are likely not caused by backend issues.")
            return True
        else:
            print("❌ MENTOR PROFILES API HAS ISSUES!")
            print("\n🔍 Critical Issues Found:")
            
            if not test_results.get('categories_endpoint'):
                print("   • Categories endpoint not accessible or returning invalid data")
            
            if not test_results.get('mentor_data_quality'):
                print("   • Mentor data quality issues - missing required fields")
            
            if self.backend_errors:
                print(f"   • {len(self.backend_errors)} backend errors detected")
            
            if len(self.mentor_data_issues) > 10:
                print(f"   • {len(self.mentor_data_issues)} mentor data issues found")
            
            print(f"\n⚠️  Backend issues may be contributing to frontend problems.")
            return False

def main():
    print("🚀 Starting OnlyMentors.ai Mentor Profiles API Test")
    print("Testing if mentor profiles API is working properly")
    print("=" * 80)
    
    # Setup
    tester = MentorProfilesAPITester()
    
    # Run comprehensive mentor profiles test
    test_results = tester.run_comprehensive_mentor_profiles_test()
    
    # Generate comprehensive report
    overall_success = tester.generate_comprehensive_report(test_results)
    
    # Return appropriate exit code
    return 0 if overall_success else 1

if __name__ == "__main__":
    sys.exit(main())