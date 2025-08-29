import requests
import sys
import json
from datetime import datetime

class ComprehensiveAIMentorshipTester:
    def __init__(self, base_url="https://mentor-marketplace.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.user_data = None
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return True, response.json()
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

    def test_all_mentors(self):
        """Test asking questions to all mentors in all categories"""
        print("\n🎯 Testing All Mentors Across All Categories")
        print("=" * 60)
        
        # Get categories first
        success, categories_data = self.run_test("Get Categories", "GET", "api/categories", 200)
        if not success:
            return False
            
        categories = categories_data.get('categories', [])
        
        # Test questions for each mentor
        test_questions = {
            "warren_buffett": "What's your investment philosophy?",
            "steve_jobs": "How do you create innovative products?",
            "elon_musk": "What's your approach to solving complex problems?",
            "michael_jordan": "How do you maintain peak performance?",
            "serena_williams": "What drives your competitive spirit?",
            "andrew_huberman": "What are the key principles of brain health?",
            "peter_attia": "How can we optimize longevity?",
            "albert_einstein": "What's the role of imagination in science?",
            "marie_curie": "How do you persevere through challenges?"
        }
        
        questions_asked = 0
        successful_responses = 0
        
        for category in categories:
            print(f"\n📂 Testing {category['name']} Category")
            print("-" * 40)
            
            for mentor in category['great_minds']:
                mentor_id = mentor['id']
                question = test_questions.get(mentor_id, f"What's your best advice for success?")
                
                success, response = self.run_test(
                    f"Ask {mentor['name']}",
                    "POST",
                    "api/questions/ask",
                    200,
                    data={
                        "category": category['id'],
                        "great_mind_id": mentor_id,
                        "question": question
                    }
                )
                
                if success:
                    questions_asked += 1
                    successful_responses += 1
                    print(f"   ✅ {mentor['name']}: {response.get('response', '')[:100]}...")
                    print(f"   📊 Questions remaining: {response.get('questions_remaining')}")
                else:
                    questions_asked += 1
                    print(f"   ❌ Failed to get response from {mentor['name']}")
        
        print(f"\n📈 Mentor Testing Summary:")
        print(f"   Questions asked: {questions_asked}")
        print(f"   Successful responses: {successful_responses}")
        print(f"   Success rate: {(successful_responses/questions_asked)*100:.1f}%")
        
        return successful_responses == questions_asked

    def test_question_limit(self):
        """Test the 10 question limit for free users"""
        print("\n🚫 Testing Question Limit (10 Free Questions)")
        print("=" * 50)
        
        # Get current user to check questions asked
        success, user_data = self.run_test("Get Current User", "GET", "api/auth/me", 200)
        if not success:
            return False
            
        current_questions = user_data['user']['questions_asked']
        print(f"Current questions asked: {current_questions}")
        
        # If we haven't reached the limit, ask more questions
        remaining_questions = 10 - current_questions
        
        if remaining_questions > 0:
            print(f"Asking {remaining_questions} more questions to reach the limit...")
            
            for i in range(remaining_questions):
                success, response = self.run_test(
                    f"Question {current_questions + i + 1}",
                    "POST",
                    "api/questions/ask",
                    200,
                    data={
                        "category": "business",
                        "great_mind_id": "warren_buffett",
                        "question": f"Test question number {current_questions + i + 1}"
                    }
                )
                
                if success:
                    print(f"   ✅ Question {current_questions + i + 1} successful")
                    print(f"   📊 Questions remaining: {response.get('questions_remaining')}")
                else:
                    print(f"   ❌ Question {current_questions + i + 1} failed")
                    return False
        
        # Now try to ask the 11th question - should fail with 402
        print("\n🚫 Testing 11th question (should fail with 402)...")
        success, response = self.run_test(
            "11th Question (Should Fail)",
            "POST",
            "api/questions/ask",
            402,  # Expecting 402 Payment Required
            data={
                "category": "business",
                "great_mind_id": "warren_buffett",
                "question": "This should fail - 11th question"
            }
        )
        
        if success:
            print("✅ Question limit properly enforced!")
            return True
        else:
            print("❌ Question limit not properly enforced")
            return False

    def test_subscription_flow(self):
        """Test subscription checkout initialization"""
        print("\n💳 Testing Subscription Flow")
        print("=" * 40)
        
        success, response = self.run_test(
            "Create Checkout Session",
            "POST",
            "api/payments/checkout",
            200,
            data={
                "package_id": "monthly",
                "origin_url": "https://example.com"
            }
        )
        
        if success and 'url' in response and 'session_id' in response:
            print(f"✅ Checkout session created successfully")
            print(f"   Checkout URL: {response['url'][:50]}...")
            print(f"   Session ID: {response['session_id']}")
            return True
        else:
            print("❌ Failed to create checkout session")
            return False

def main():
    print("🚀 Starting Comprehensive AI Mentorship API Tests")
    print("=" * 60)
    
    # Setup
    tester = ComprehensiveAIMentorshipTester()
    test_email = f"comprehensive_test_{datetime.now().strftime('%H%M%S')}@example.com"
    test_password = "testpass123"
    test_name = "Comprehensive Test User"

    # Test 1: User signup
    success, response = tester.run_test(
        "User Signup",
        "POST",
        "api/auth/signup",
        200,
        data={"email": test_email, "password": test_password, "full_name": test_name}
    )
    
    if success and 'token' in response:
        tester.token = response['token']
        tester.user_data = response['user']
        print(f"✅ Signup successful")
    else:
        print("❌ Signup failed, stopping tests")
        return 1

    # Test 2: Test all mentors
    if not tester.test_all_mentors():
        print("❌ Not all mentors working properly")

    # Test 3: Test question limit
    if not tester.test_question_limit():
        print("❌ Question limit not working properly")

    # Test 4: Test subscription flow
    if not tester.test_subscription_flow():
        print("❌ Subscription flow not working properly")

    # Print final results
    print("\n" + "=" * 60)
    print(f"📊 COMPREHENSIVE TEST RESULTS")
    print(f"Tests passed: {tester.tests_passed}/{tester.tests_run}")
    print(f"Success rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    if tester.tests_passed >= tester.tests_run * 0.9:  # 90% success rate
        print("🎉 COMPREHENSIVE TESTS MOSTLY SUCCESSFUL!")
        return 0
    else:
        print("⚠️  COMPREHENSIVE TESTS NEED ATTENTION")
        return 1

if __name__ == "__main__":
    sys.exit(main())