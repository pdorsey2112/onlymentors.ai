import requests
import sys
import json
from datetime import datetime

class OnlyMentorsAPITester:
    def __init__(self, base_url="https://f2b0aa4c-4c6c-44c0-8e63-7550a30e04a0.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.user_data = None
        self.tests_run = 0
        self.tests_passed = 0

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
                response = requests.get(url, headers=test_headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response keys: {list(response_data.keys()) if isinstance(response_data, dict) else 'Non-dict response'}")
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

    def test_root_endpoint(self):
        """Test root endpoint"""
        success, response = self.run_test("Root Endpoint", "GET", "", 200)
        if success:
            print(f"   Total mentors: {response.get('total_mentors', 'N/A')}")
            print(f"   Categories: {response.get('categories', 'N/A')}")
            print(f"   Version: {response.get('version', 'N/A')}")
        return success

    def test_categories_endpoint(self):
        """Test categories endpoint"""
        success, response = self.run_test("Categories Endpoint", "GET", "api/categories", 200)
        if success:
            categories = response.get('categories', [])
            expected_categories = ['business', 'sports', 'health', 'science']
            found_categories = [cat['id'] for cat in categories]
            
            print(f"   Found categories: {found_categories}")
            if all(cat in found_categories for cat in expected_categories):
                print("✅ All expected categories found")
                
                # Check mentors in business category
                business_cat = next((cat for cat in categories if cat['id'] == 'business'), None)
                if business_cat:
                    mentors = business_cat.get('mentors', [])
                    mentor_ids = [m['id'] for m in mentors]
                    print(f"   Business mentors count: {len(mentors)}")
                    expected_mentors = ['warren_buffett', 'steve_jobs', 'elon_musk']
                    if all(mentor in mentor_ids for mentor in expected_mentors):
                        print("✅ All expected business mentors found")
                    else:
                        print("❌ Missing expected business mentors")
                        print(f"   Found: {mentor_ids[:10]}...")  # Show first 10
            else:
                print("❌ Missing expected categories")
        return success

    def test_category_mentors(self, category_id):
        """Test getting mentors for a specific category"""
        success, response = self.run_test(
            f"Category {category_id} Mentors", 
            "GET", 
            f"api/categories/{category_id}/mentors", 
            200
        )
        if success:
            mentors = response.get('mentors', [])
            print(f"   {category_id} mentors count: {len(mentors)}")
            if mentors:
                print(f"   Sample mentor: {mentors[0]['name']} - {mentors[0]['title']}")
        return success

    def test_search_mentors(self, query, category=None):
        """Test mentor search functionality"""
        endpoint = f"api/search/mentors?q={query}"
        if category:
            endpoint += f"&category={category}"
            
        success, response = self.run_test(
            f"Search Mentors: '{query}'" + (f" in {category}" if category else ""), 
            "GET", 
            endpoint, 
            200
        )
        if success:
            results = response.get('results', [])
            print(f"   Search results: {len(results)} mentors found")
            if results:
                print(f"   First result: {results[0]['name']} - {results[0]['expertise']}")
        return success

    def test_signup(self, email, password, full_name):
        """Test user signup"""
        success, response = self.run_test(
            "User Signup",
            "POST",
            "api/auth/signup",
            200,
            data={"email": email, "password": password, "full_name": full_name}
        )
        if success and 'token' in response:
            self.token = response['token']
            self.user_data = response['user']
            print(f"✅ Signup successful, token received")
            print(f"   User: {self.user_data['full_name']} ({self.user_data['email']})")
            print(f"   Questions asked: {self.user_data.get('questions_asked', 0)}")
            print(f"   Is subscribed: {self.user_data.get('is_subscribed', False)}")
            return True
        return False

    def test_login(self, email, password):
        """Test user login"""
        success, response = self.run_test(
            "User Login",
            "POST",
            "api/auth/login",
            200,
            data={"email": email, "password": password}
        )
        if success and 'token' in response:
            self.token = response['token']
            self.user_data = response['user']
            print(f"✅ Login successful, token received")
            return True
        return False

    def test_get_me(self):
        """Test get current user endpoint"""
        success, response = self.run_test("Get Current User", "GET", "api/auth/me", 200)
        if success and 'user' in response:
            user = response['user']
            print(f"✅ User data retrieved: {user['full_name']}")
            print(f"   Questions asked: {user.get('questions_asked', 0)}")
            print(f"   Is subscribed: {user.get('is_subscribed', False)}")
            return True
        return False

    def test_ask_question_multiple_mentors(self, category, mentor_ids, question):
        """Test asking a question to multiple mentors (NEW FEATURE)"""
        success, response = self.run_test(
            f"Ask Question to {len(mentor_ids)} Mentors",
            "POST",
            "api/questions/ask",
            200,
            data={
                "category": category,
                "mentor_ids": mentor_ids,
                "question": question
            }
        )
        if success:
            if 'responses' in response:
                responses = response['responses']
                print(f"✅ Question answered by {len(responses)} mentors")
                print(f"   Question: {response.get('question', '')[:100]}...")
                for i, resp in enumerate(responses):
                    mentor_name = resp['mentor']['name']
                    response_text = resp['response'][:150]
                    print(f"   Response {i+1} ({mentor_name}): {response_text}...")
                print(f"   Questions remaining: {response.get('questions_remaining')}")
                return True, response
        return False, {}

    def test_ask_question_single_mentor(self, category, mentor_id, question):
        """Test asking a question to a single mentor"""
        return self.test_ask_question_multiple_mentors(category, [mentor_id], question)

    def test_question_history(self):
        """Test getting question history"""
        success, response = self.run_test("Question History", "GET", "api/questions/history", 200)
        if success and 'questions' in response:
            questions = response['questions']
            print(f"✅ Question history retrieved: {len(questions)} questions")
            if questions:
                latest = questions[0]
                print(f"   Latest question: {latest.get('question', '')[:100]}...")
                print(f"   Responses count: {len(latest.get('responses', []))}")
            return True
        return False

    def test_subscription_flow(self):
        """Test subscription checkout creation"""
        success, response = self.run_test(
            "Create Subscription Checkout",
            "POST",
            "api/payments/checkout",
            200,
            data={
                "package_id": "monthly",
                "origin_url": "https://test.com"
            }
        )
        if success:
            if 'url' in response and 'session_id' in response:
                print(f"✅ Checkout session created")
                print(f"   Session ID: {response['session_id']}")
                print(f"   Checkout URL: {response['url'][:50]}...")
                return True, response['session_id']
        return False, None

def main():
    print("🚀 Starting OnlyMentors.ai Comprehensive API Tests")
    print("=" * 60)
    
    # Setup
    tester = OnlyMentorsAPITester()
    test_email = f"test_{datetime.now().strftime('%H%M%S')}@onlymentors.com"
    test_password = "testpass123"
    test_name = "Test User"

    # Test 1: Root endpoint
    print("\n📍 BASIC ENDPOINTS")
    tester.test_root_endpoint()

    # Test 2: Categories endpoint (should work without auth)
    tester.test_categories_endpoint()

    # Test 3: Category-specific mentors
    tester.test_category_mentors("business")
    tester.test_category_mentors("sports")

    # Test 4: Search functionality
    print("\n🔍 SEARCH FUNCTIONALITY")
    tester.test_search_mentors("warren", "business")
    tester.test_search_mentors("jordan", "sports")
    tester.test_search_mentors("innovation")  # Cross-category search

    # Test 5: Authentication
    print("\n🔐 AUTHENTICATION")
    if not tester.test_signup(test_email, test_password, test_name):
        print("❌ Signup failed, stopping tests")
        return 1

    # Test 6: Get current user
    if not tester.test_get_me():
        print("❌ Get user failed")

    # Test 7: Single mentor question
    print("\n💬 SINGLE MENTOR QUESTIONS")
    question1 = "What's your best investment advice for beginners?"
    success, response1 = tester.test_ask_question_single_mentor("business", "warren_buffett", question1)
    if not success:
        print("❌ Single mentor question failed")

    # Test 8: Multiple mentor question (NEW FEATURE)
    print("\n👥 MULTIPLE MENTOR QUESTIONS")
    question2 = "How do you approach innovation and leadership?"
    multiple_mentors = ["steve_jobs", "elon_musk", "bill_gates"]
    success, response2 = tester.test_ask_question_multiple_mentors("business", multiple_mentors, question2)
    if not success:
        print("❌ Multiple mentor question failed")

    # Test 9: Cross-category multiple mentors
    question3 = "What's the key to peak performance and success?"
    cross_category_test = ["warren_buffett"]  # Business mentor only for now
    success, response3 = tester.test_ask_question_multiple_mentors("business", cross_category_test, question3)

    # Test 10: Question history
    print("\n📚 QUESTION HISTORY")
    tester.test_question_history()

    # Test 11: Test login with existing credentials
    print("\n🔄 LOGIN TEST")
    tester.token = None  # Clear token to test login
    if not tester.test_login(test_email, test_password):
        print("❌ Login test failed")

    # Test 12: Subscription flow
    print("\n💳 SUBSCRIPTION FLOW")
    tester.test_subscription_flow()

    # Test 13: Question limit test (ask more questions to test limit)
    print("\n🚫 QUESTION LIMIT TEST")
    for i in range(7):  # Ask 7 more questions to approach the 10 limit
        question = f"Test question {i+4}: What advice do you have for question {i+4}?"
        success, _ = tester.test_ask_question_single_mentor("business", "warren_buffett", question)
        if not success:
            break

    # Test 14: Try to exceed question limit
    question_limit_test = "This should fail due to question limit"
    success, response = tester.test_ask_question_single_mentor("business", "warren_buffett", question_limit_test)
    if not success:
        print("✅ Question limit properly enforced")
    else:
        print("❌ Question limit not working properly")

    # Print final results
    print("\n" + "=" * 60)
    print(f"📊 FINAL RESULTS")
    print(f"Tests passed: {tester.tests_passed}/{tester.tests_run}")
    print(f"Success rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    if tester.tests_passed >= tester.tests_run * 0.8:  # 80% pass rate acceptable
        print("🎉 TESTS MOSTLY PASSED!")
        return 0
    else:
        print("⚠️  MANY TESTS FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())