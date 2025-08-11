import requests
import sys
import json
import time
from datetime import datetime

class OnlyMentorsAPITester:
    def __init__(self, base_url="https://f2b0aa4c-4c6c-44c0-8e63-7550a30e04a0.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.user_data = None
        self.tests_run = 0
        self.tests_passed = 0
        self.llm_responses = []  # Store LLM responses for analysis

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
                    print(f"   Response preview: {json.dumps(response_data, indent=2)[:300]}...")
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
                
                # Check mentors in business category
                business_cat = next((cat for cat in categories if cat['id'] == 'business'), None)
                if business_cat:
                    mentors = [m['id'] for m in business_cat['mentors']]
                    print(f"   Business mentors: {mentors[:5]}...")  # Show first 5
                    expected_mentors = ['warren_buffett', 'steve_jobs', 'bill_gates']
                    found_mentors = [m for m in expected_mentors if m in mentors]
                    if found_mentors:
                        print(f"✅ Found expected business mentors: {found_mentors}")
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

    def test_llm_integration_single_mentor(self, category, mentor_id, question):
        """Test LLM integration with a single mentor"""
        print(f"\n🤖 Testing LLM Integration - Single Mentor ({mentor_id})")
        
        success, response = self.run_test(
            f"LLM Question to {mentor_id}",
            "POST",
            "api/questions/ask",
            200,
            data={
                "category": category,
                "mentor_ids": [mentor_id],  # Array with single mentor
                "question": question
            }
        )
        
        if success:
            if 'responses' in response and len(response['responses']) > 0:
                mentor_response = response['responses'][0]
                response_text = mentor_response.get('response', '')
                mentor_info = mentor_response.get('mentor', {})
                
                print(f"✅ LLM Response received from {mentor_info.get('name', mentor_id)}")
                print(f"   Question: {response.get('question', '')}")
                print(f"   Response length: {len(response_text)} characters")
                print(f"   Response preview: {response_text[:200]}...")
                print(f"   Questions remaining: {response.get('questions_remaining')}")
                
                # Store response for analysis
                self.llm_responses.append({
                    'mentor_id': mentor_id,
                    'mentor_name': mentor_info.get('name', ''),
                    'question': question,
                    'response': response_text,
                    'response_length': len(response_text)
                })
                
                # Check if response looks like LLM-generated (not mock)
                is_llm_response = self.analyze_llm_response(response_text, mentor_info.get('name', ''))
                if is_llm_response:
                    print("✅ Response appears to be LLM-generated (not mock)")
                else:
                    print("⚠️  Response might be mock or fallback")
                
                return True, response
            else:
                print("❌ No responses in response data")
        return False, {}

    def test_llm_integration_multiple_mentors(self, category, mentor_ids, question):
        """Test LLM integration with multiple mentors"""
        print(f"\n🤖 Testing LLM Integration - Multiple Mentors ({', '.join(mentor_ids)})")
        
        success, response = self.run_test(
            f"LLM Question to Multiple Mentors",
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
            if 'responses' in response and len(response['responses']) > 0:
                responses = response['responses']
                print(f"✅ Received {len(responses)} responses from {len(mentor_ids)} mentors")
                
                for i, mentor_response in enumerate(responses):
                    response_text = mentor_response.get('response', '')
                    mentor_info = mentor_response.get('mentor', {})
                    mentor_name = mentor_info.get('name', f'Mentor {i+1}')
                    
                    print(f"   📝 {mentor_name}: {len(response_text)} chars - {response_text[:100]}...")
                    
                    # Store response for analysis
                    self.llm_responses.append({
                        'mentor_id': mentor_info.get('id', ''),
                        'mentor_name': mentor_name,
                        'question': question,
                        'response': response_text,
                        'response_length': len(response_text)
                    })
                
                # Check if responses are unique (different mentors should give different responses)
                unique_responses = len(set(r.get('response', '') for r in responses))
                if unique_responses == len(responses):
                    print("✅ All mentor responses are unique")
                else:
                    print(f"⚠️  Only {unique_responses}/{len(responses)} responses are unique")
                
                return True, response
            else:
                print("❌ No responses in response data")
        return False, {}

    def analyze_llm_response(self, response_text, mentor_name):
        """Analyze if response appears to be LLM-generated vs mock"""
        # Check for mock response patterns
        mock_indicators = [
            "Thank you for your question about",
            "Based on my experience in",
            "While I'd love to provide a detailed response right now",
            "I encourage you to explore this further"
        ]
        
        # Check for LLM indicators
        llm_indicators = [
            len(response_text) > 200,  # LLM responses tend to be longer
            "I" in response_text,  # Personal pronouns
            mentor_name.split()[0] in response_text if mentor_name else False,  # Mentions own name
            any(word in response_text.lower() for word in ['experience', 'believe', 'think', 'approach'])
        ]
        
        # If contains mock indicators, likely fallback
        if any(indicator in response_text for indicator in mock_indicators):
            return False
        
        # If has multiple LLM indicators, likely real LLM
        if sum(llm_indicators) >= 2:
            return True
        
        return len(response_text) > 150  # Default to length check

    def test_question_history(self):
        """Test getting question history"""
        success, response = self.run_test("Question History", "GET", "api/questions/history", 200)
        if success and 'questions' in response:
            questions = response['questions']
            print(f"✅ Question history retrieved: {len(questions)} questions")
            return True
        return False

    def test_stripe_checkout_monthly(self):
        """Test Stripe checkout for monthly subscription"""
        print(f"\n💳 Testing Stripe Checkout - Monthly Package")
        
        success, response = self.run_test(
            "Stripe Checkout - Monthly",
            "POST",
            "api/payments/checkout",
            200,
            data={
                "package_id": "monthly",
                "origin_url": "https://f2b0aa4c-4c6c-44c0-8e63-7550a30e04a0.preview.emergentagent.com"
            }
        )
        
        if success:
            if 'url' in response and 'session_id' in response:
                print(f"✅ Checkout session created successfully")
                print(f"   Session ID: {response['session_id']}")
                print(f"   Checkout URL: {response['url'][:100]}...")
                
                # Validate URL format
                if response['url'].startswith('https://checkout.stripe.com/'):
                    print("✅ Valid Stripe checkout URL format")
                else:
                    print("⚠️  Unexpected checkout URL format")
                
                # Validate session ID format
                if response['session_id'].startswith('cs_'):
                    print("✅ Valid Stripe session ID format")
                else:
                    print("⚠️  Unexpected session ID format")
                
                return True, response
            else:
                print("❌ Missing url or session_id in response")
        return False, {}

    def test_stripe_checkout_yearly(self):
        """Test Stripe checkout for yearly subscription"""
        print(f"\n💳 Testing Stripe Checkout - Yearly Package")
        
        success, response = self.run_test(
            "Stripe Checkout - Yearly",
            "POST",
            "api/payments/checkout",
            200,
            data={
                "package_id": "yearly",
                "origin_url": "https://f2b0aa4c-4c6c-44c0-8e63-7550a30e04a0.preview.emergentagent.com"
            }
        )
        
        if success:
            if 'url' in response and 'session_id' in response:
                print(f"✅ Checkout session created successfully")
                print(f"   Session ID: {response['session_id']}")
                print(f"   Checkout URL: {response['url'][:100]}...")
                
                # Validate URL format
                if response['url'].startswith('https://checkout.stripe.com/'):
                    print("✅ Valid Stripe checkout URL format")
                else:
                    print("⚠️  Unexpected checkout URL format")
                
                # Validate session ID format
                if response['session_id'].startswith('cs_'):
                    print("✅ Valid Stripe session ID format")
                else:
                    print("⚠️  Unexpected session ID format")
                
                return True, response
            else:
                print("❌ Missing url or session_id in response")
        return False, {}

    def test_stripe_invalid_package(self):
        """Test Stripe checkout with invalid package"""
        print(f"\n💳 Testing Stripe Checkout - Invalid Package")
        
        success, response = self.run_test(
            "Stripe Checkout - Invalid Package",
            "POST",
            "api/payments/checkout",
            400,
            data={
                "package_id": "invalid_package",
                "origin_url": "https://f2b0aa4c-4c6c-44c0-8e63-7550a30e04a0.preview.emergentagent.com"
            }
        )
        
        return success

    def test_stripe_checkout_without_auth(self):
        """Test Stripe checkout without authentication"""
        print(f"\n💳 Testing Stripe Checkout - No Authentication")
        
        # Temporarily remove token
        original_token = self.token
        self.token = None
        
        success, response = self.run_test(
            "Stripe Checkout - No Auth",
            "POST",
            "api/payments/checkout",
            401,
            data={
                "package_id": "monthly",
                "origin_url": "https://f2b0aa4c-4c6c-44c0-8e63-7550a30e04a0.preview.emergentagent.com"
            }
        )
        
        # Restore token
        self.token = original_token
        
        return success

    def verify_payment_transaction_stored(self, session_id):
        """Verify that payment transaction is stored in database"""
        print(f"\n💾 Verifying Payment Transaction Storage")
        
        # We can't directly access the database, but we can test the payment status endpoint
        success, response = self.run_test(
            "Payment Status Check",
            "GET",
            f"api/payments/status/{session_id}",
            200
        )
        
        if success:
            if 'status' in response:
                print(f"✅ Payment transaction found in database")
                print(f"   Status: {response.get('status')}")
                print(f"   Payment Status: {response.get('payment_status')}")
                return True
            else:
                print("❌ Payment transaction not found or invalid response")
        return False

    def test_error_handling(self):
        """Test error handling scenarios"""
        print(f"\n🚨 Testing Error Handling")
        
        # Test invalid mentor
        success, response = self.run_test(
            "Invalid Mentor ID",
            "POST",
            "api/questions/ask",
            404,
            data={
                "category": "business",
                "mentor_ids": ["invalid_mentor"],
                "question": "Test question"
            }
        )
        
        # Test invalid category
        success2, response2 = self.run_test(
            "Invalid Category",
            "POST",
            "api/questions/ask",
            404,
            data={
                "category": "invalid_category",
                "mentor_ids": ["warren_buffett"],
                "question": "Test question"
            }
        )
        
        return success and success2

    def analyze_llm_integration_results(self):
        """Analyze all LLM responses to determine if integration is working"""
        print(f"\n📊 LLM Integration Analysis")
        print(f"Total responses analyzed: {len(self.llm_responses)}")
        
        if not self.llm_responses:
            print("❌ No LLM responses to analyze")
            return False
        
        # Analyze response lengths
        avg_length = sum(r['response_length'] for r in self.llm_responses) / len(self.llm_responses)
        print(f"Average response length: {avg_length:.0f} characters")
        
        # Check for variety in responses
        unique_responses = len(set(r['response'] for r in self.llm_responses))
        print(f"Unique responses: {unique_responses}/{len(self.llm_responses)}")
        
        # Check for mentor-specific content
        mentor_specific = 0
        for response in self.llm_responses:
            if response['mentor_name'] and response['mentor_name'].split()[0].lower() in response['response'].lower():
                mentor_specific += 1
        
        print(f"Responses with mentor-specific content: {mentor_specific}/{len(self.llm_responses)}")
        
        # Overall assessment
        llm_working = (
            avg_length > 100 and  # Reasonable response length
            unique_responses > len(self.llm_responses) * 0.7 and  # Most responses are unique
            mentor_specific > 0  # At least some mentor-specific content
        )
        
        if llm_working:
            print("✅ LLM Integration appears to be working correctly")
        else:
            print("❌ LLM Integration may not be working properly")
        
        return llm_working

def main():
    print("🚀 Starting OnlyMentors.ai LLM Integration Tests")
    print("=" * 60)
    
    # Setup
    tester = OnlyMentorsAPITester()
    test_email = f"test_{datetime.now().strftime('%H%M%S')}@test.com"
    test_password = "password123"
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

    # Test 5: LLM Integration - Single Mentor Tests
    print(f"\n{'='*60}")
    print("🤖 TESTING LLM INTEGRATION - CORE FUNCTIONALITY")
    print(f"{'='*60}")
    
    # Test Warren Buffett (Business)
    question1 = "How do I become successful in business?"
    success1, _ = tester.test_llm_integration_single_mentor("business", "warren_buffett", question1)
    
    # Test Steve Jobs (Business) 
    question2 = "What's your approach to innovation and product development?"
    success2, _ = tester.test_llm_integration_single_mentor("business", "steve_jobs", question2)
    
    # Test different category - Michael Jordan (Sports)
    question3 = "What's the key to mental toughness in competition?"
    success3, _ = tester.test_llm_integration_single_mentor("sports", "michael_jordan", question3)
    
    # Test 6: LLM Integration - Multiple Mentors
    question4 = "What advice do you have for young entrepreneurs?"
    success4, _ = tester.test_llm_integration_multiple_mentors(
        "business", 
        ["warren_buffett", "steve_jobs"], 
        question4
    )
    
    # Test 7: Question history
    tester.test_question_history()
    
    # Test 8: Error handling
    tester.test_error_handling()
    
    # Test 9: Analyze LLM integration results
    llm_working = tester.analyze_llm_integration_results()
    
    # Print final results
    print("\n" + "=" * 60)
    print(f"📊 FINAL TEST RESULTS")
    print("=" * 60)
    print(f"Tests passed: {tester.tests_passed}/{tester.tests_run}")
    print(f"Success rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    print(f"LLM Integration Status: {'✅ WORKING' if llm_working else '❌ NOT WORKING'}")
    
    if tester.tests_passed == tester.tests_run and llm_working:
        print("🎉 ALL TESTS PASSED - LLM INTEGRATION IS WORKING!")
        return 0
    else:
        print("⚠️  SOME TESTS FAILED OR LLM INTEGRATION ISSUES DETECTED")
        return 1

if __name__ == "__main__":
    sys.exit(main())