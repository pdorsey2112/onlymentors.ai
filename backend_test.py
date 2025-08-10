import requests
import sys
import json
from datetime import datetime

class AIMentorshipAPITester:
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
                    print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
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
        return self.run_test("Root Endpoint", "GET", "", 200)

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
                
                # Check great minds in business category
                business_cat = next((cat for cat in categories if cat['id'] == 'business'), None)
                if business_cat:
                    great_minds = [gm['id'] for gm in business_cat['great_minds']]
                    print(f"   Business great minds: {great_minds}")
                    expected_minds = ['warren_buffett', 'steve_jobs', 'elon_musk']
                    if all(mind in great_minds for mind in expected_minds):
                        print("✅ All expected business mentors found")
                    else:
                        print("❌ Missing expected business mentors")
            else:
                print("❌ Missing expected categories")
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
            print(f"   User: {self.user_data}")
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
            print(f"✅ User data retrieved: {response['user']}")
            return True
        return False

    def test_ask_question(self, category, great_mind_id, question):
        """Test asking a question to a mentor"""
        success, response = self.run_test(
            f"Ask Question to {great_mind_id}",
            "POST",
            "api/questions/ask",
            200,
            data={
                "category": category,
                "great_mind_id": great_mind_id,
                "question": question
            }
        )
        if success:
            if 'response' in response and 'great_mind' in response:
                print(f"✅ Question answered successfully")
                print(f"   Question: {response.get('question', '')[:100]}...")
                print(f"   Response: {response.get('response', '')[:200]}...")
                print(f"   Questions remaining: {response.get('questions_remaining')}")
                return True, response
        return False, {}

    def test_question_history(self):
        """Test getting question history"""
        success, response = self.run_test("Question History", "GET", "api/questions/history", 200)
        if success and 'questions' in response:
            questions = response['questions']
            print(f"✅ Question history retrieved: {len(questions)} questions")
            return True
        return False

def main():
    print("🚀 Starting AI Mentorship API Tests")
    print("=" * 50)
    
    # Setup
    tester = AIMentorshipAPITester()
    test_email = f"test_{datetime.now().strftime('%H%M%S')}@example.com"
    test_password = "testpass123"
    test_name = "Test User"

    # Test 1: Root endpoint
    tester.test_root_endpoint()

    # Test 2: Categories endpoint (should work without auth)
    tester.test_categories_endpoint()

    # Test 3: User signup
    if not tester.test_signup(test_email, test_password, test_name):
        print("❌ Signup failed, stopping tests")
        return 1

    # Test 4: Get current user
    if not tester.test_get_me():
        print("❌ Get user failed")

    # Test 5: Ask a question to Warren Buffett
    question1 = "What's your best investment advice for beginners?"
    success, response1 = tester.test_ask_question("business", "warren_buffett", question1)
    if not success:
        print("❌ First question failed")

    # Test 6: Ask a question to Steve Jobs
    question2 = "How do you approach innovation and product design?"
    success, response2 = tester.test_ask_question("business", "steve_jobs", question2)
    if not success:
        print("❌ Second question failed")

    # Test 7: Ask a question to Michael Jordan (Sports category)
    question3 = "What's the key to mental toughness in competition?"
    success, response3 = tester.test_ask_question("sports", "michael_jordan", question3)
    if not success:
        print("❌ Third question failed")

    # Test 8: Question history
    tester.test_question_history()

    # Test 9: Test login with existing credentials
    tester.token = None  # Clear token to test login
    if not tester.test_login(test_email, test_password):
        print("❌ Login test failed")

    # Print final results
    print("\n" + "=" * 50)
    print(f"📊 FINAL RESULTS")
    print(f"Tests passed: {tester.tests_passed}/{tester.tests_run}")
    print(f"Success rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 ALL TESTS PASSED!")
        return 0
    else:
        print("⚠️  SOME TESTS FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())