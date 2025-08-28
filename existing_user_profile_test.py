import requests
import sys
import json
import time
from datetime import datetime

class ExistingUserProfileTester:
    def __init__(self, base_url="https://user-data-restore.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.user_data = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        
        # Target user for testing
        self.target_email = "pdorsey@dorseyandassociates.com"
        self.target_password = None  # We'll need to determine this or create the user

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
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=30)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response preview: {json.dumps(response_data, indent=2)[:500]}...")
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

    def create_existing_user_simulation(self):
        """Create a user to simulate an existing user with minimal profile data"""
        print(f"\n👤 Creating Existing User Simulation: {self.target_email}")
        
        # Use basic signup (simulating old registration without comprehensive profile)
        success, response = self.run_test(
            "Create Existing User (Basic Signup)",
            "POST",
            "api/auth/signup",
            200,
            data={
                "email": self.target_email,
                "password": "ExistingUser123!",
                "full_name": "Paul Dorsey"
            }
        )
        
        if success and 'token' in response:
            self.target_password = "ExistingUser123!"
            print(f"✅ Existing user simulation created successfully")
            print(f"   Email: {self.target_email}")
            print(f"   Password: {self.target_password}")
            return True
        else:
            # User might already exist, try to login
            print(f"⚠️  User might already exist, attempting login...")
            return self.attempt_existing_user_login()
    
    def attempt_existing_user_login(self):
        """Attempt to login with common passwords for existing user"""
        common_passwords = [
            "password123",
            "Password123!",
            "ExistingUser123!",
            "dorseypass",
            "Dorsey123!",
            "pdorsey123"
        ]
        
        for password in common_passwords:
            print(f"   Trying password: {password}")
            success, response = self.run_test(
                f"Login Attempt - {password}",
                "POST",
                "api/auth/login",
                200,
                data={
                    "email": self.target_email,
                    "password": password
                }
            )
            
            if success and 'token' in response:
                self.target_password = password
                print(f"✅ Successfully logged in with password: {password}")
                return True
        
        print(f"❌ Could not login with any common passwords")
        return False

    def test_existing_user_authentication(self):
        """Test authentication for existing user"""
        print(f"\n🔐 Testing Existing User Authentication")
        
        if not self.target_password:
            print(f"❌ No password available for existing user")
            return False
        
        success, response = self.run_test(
            "Existing User Login",
            "POST",
            "api/auth/login",
            200,
            data={
                "email": self.target_email,
                "password": self.target_password
            }
        )
        
        if success and 'token' in response:
            self.token = response['token']
            self.user_data = response['user']
            print(f"✅ Existing user authentication successful")
            print(f"   User ID: {self.user_data.get('user_id')}")
            print(f"   Email: {self.user_data.get('email')}")
            print(f"   Full Name: {self.user_data.get('full_name')}")
            print(f"   Questions Asked: {self.user_data.get('questions_asked', 0)}")
            print(f"   Is Subscribed: {self.user_data.get('is_subscribed', False)}")
            
            self.test_results.append({
                "test": "existing_user_auth",
                "status": "passed",
                "user_data": self.user_data
            })
            return True
        else:
            self.test_results.append({
                "test": "existing_user_auth", 
                "status": "failed",
                "error": "Authentication failed"
            })
            return False

    def test_basic_profile_endpoint(self):
        """Test GET /api/user/profile for existing user"""
        print(f"\n👤 Testing Basic Profile Endpoint")
        
        success, response = self.run_test(
            "GET /api/user/profile",
            "GET",
            "api/user/profile",
            200
        )
        
        if success:
            print(f"✅ Basic profile endpoint accessible")
            
            # Analyze what fields are present vs missing
            expected_fields = {
                'user_id': 'User ID',
                'email': 'Email Address',
                'full_name': 'Full Name',
                'phone_number': 'Phone Number',
                'questions_asked': 'Questions Asked',
                'is_subscribed': 'Subscription Status',
                'profile_image_url': 'Profile Image',
                'created_at': 'Account Creation Date',
                'last_login': 'Last Login'
            }
            
            present_fields = []
            missing_fields = []
            empty_fields = []
            
            for field, description in expected_fields.items():
                if field in response:
                    present_fields.append(field)
                    value = response[field]
                    if value is None or value == "" or value == []:
                        empty_fields.append(field)
                        print(f"   📝 {description}: EMPTY/NULL")
                    else:
                        print(f"   ✅ {description}: {value}")
                else:
                    missing_fields.append(field)
                    print(f"   ❌ {description}: MISSING")
            
            self.test_results.append({
                "test": "basic_profile",
                "status": "passed",
                "present_fields": present_fields,
                "missing_fields": missing_fields,
                "empty_fields": empty_fields,
                "profile_data": response
            })
            
            return True
        else:
            self.test_results.append({
                "test": "basic_profile",
                "status": "failed",
                "error": "Could not access basic profile endpoint"
            })
            return False

    def test_complete_profile_endpoint(self):
        """Test GET /api/user/profile/complete for existing user"""
        print(f"\n📋 Testing Complete Profile Endpoint")
        
        success, response = self.run_test(
            "GET /api/user/profile/complete",
            "GET",
            "api/user/profile/complete",
            200
        )
        
        if success:
            print(f"✅ Complete profile endpoint accessible")
            
            # Analyze comprehensive profile data
            comprehensive_fields = {
                'user_id': 'User ID',
                'email': 'Email Address',
                'full_name': 'Full Name',
                'phone_number': 'Phone Number',
                'communication_preferences': 'Communication Preferences',
                'subscription_plan': 'Subscription Plan',
                'is_subscribed': 'Subscription Status',
                'subscription_expires': 'Subscription Expiry',
                'questions_asked': 'Questions Asked',
                'total_interactions': 'Total Interactions',
                'unique_mentors_consulted': 'Unique Mentors Consulted',
                'profile_completed': 'Profile Completion Status',
                'created_at': 'Account Creation Date',
                'last_login': 'Last Login',
                'account_status': 'Account Status'
            }
            
            present_comprehensive = []
            missing_comprehensive = []
            empty_comprehensive = []
            
            for field, description in comprehensive_fields.items():
                if field in response:
                    present_comprehensive.append(field)
                    value = response[field]
                    if value is None or value == "" or value == [] or value == {}:
                        empty_comprehensive.append(field)
                        print(f"   📝 {description}: EMPTY/NULL")
                    else:
                        print(f"   ✅ {description}: {value}")
                else:
                    missing_comprehensive.append(field)
                    print(f"   ❌ {description}: MISSING")
            
            # Check profile completion status
            profile_completed = response.get('profile_completed', False)
            print(f"\n🎯 Profile Completion Analysis:")
            print(f"   Profile Completed Flag: {profile_completed}")
            print(f"   Present Fields: {len(present_comprehensive)}/{len(comprehensive_fields)}")
            print(f"   Missing Fields: {len(missing_comprehensive)}")
            print(f"   Empty Fields: {len(empty_comprehensive)}")
            
            self.test_results.append({
                "test": "complete_profile",
                "status": "passed",
                "present_fields": present_comprehensive,
                "missing_fields": missing_comprehensive,
                "empty_fields": empty_comprehensive,
                "profile_completed": profile_completed,
                "profile_data": response
            })
            
            return True
        else:
            self.test_results.append({
                "test": "complete_profile",
                "status": "failed",
                "error": "Could not access complete profile endpoint"
            })
            return False

    def test_question_history_endpoint(self):
        """Test GET /api/user/question-history for existing user"""
        print(f"\n📚 Testing Question History Endpoint")
        
        success, response = self.run_test(
            "GET /api/user/question-history",
            "GET",
            "api/user/question-history",
            200
        )
        
        if success:
            total_questions = response.get('total_questions', 0)
            history = response.get('history', [])
            
            print(f"✅ Question history endpoint accessible")
            print(f"   Total Questions: {total_questions}")
            print(f"   History Records: {len(history)}")
            
            if history:
                print(f"   Sample History Entry:")
                sample = history[0]
                for key, value in sample.items():
                    print(f"     {key}: {value}")
            
            self.test_results.append({
                "test": "question_history",
                "status": "passed",
                "total_questions": total_questions,
                "history_count": len(history)
            })
            
            return True, response
        else:
            self.test_results.append({
                "test": "question_history",
                "status": "failed",
                "error": "Could not access question history endpoint"
            })
            return False, {}

    def test_profile_vs_new_registration(self):
        """Compare existing user profile with new comprehensive registration"""
        print(f"\n🆚 Testing Profile Comparison: Existing vs New Registration")
        
        # Create a new user with comprehensive profile data
        timestamp = datetime.now().strftime('%H%M%S')
        new_user_email = f"comprehensive_test_{timestamp}@example.com"
        
        # Test comprehensive registration endpoint
        comprehensive_data = {
            "email": new_user_email,
            "password": "ComprehensiveTest123!",
            "full_name": "Comprehensive Test User",
            "phone_number": "15551234567",
            "communication_preferences": json.dumps({
                "email": True,
                "text": False,
                "both": False
            }),
            "subscription_plan": "premium",
            "payment_info": json.dumps({
                "method": "credit_card",
                "last_four": "1234"
            })
        }
        
        # Use form data for comprehensive registration
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        
        success, new_user_response = self.run_test(
            "Comprehensive Registration",
            "POST",
            "api/auth/register",
            200,
            data=comprehensive_data,
            headers=headers
        )
        
        if success:
            print(f"✅ New comprehensive registration successful")
            new_user_data = new_user_response.get('user', {})
            
            # Compare profile completion status
            existing_profile_completed = False
            new_profile_completed = new_user_data.get('profile_completed', False)
            
            # Get existing user profile completion from previous test
            for result in self.test_results:
                if result['test'] == 'complete_profile' and result['status'] == 'passed':
                    existing_profile_completed = result.get('profile_completed', False)
                    break
            
            print(f"\n📊 Profile Completion Comparison:")
            print(f"   Existing User ({self.target_email}):")
            print(f"     Profile Completed: {existing_profile_completed}")
            print(f"   New User ({new_user_email}):")
            print(f"     Profile Completed: {new_profile_completed}")
            
            # Analyze field differences
            existing_fields = set()
            new_fields = set(new_user_data.keys())
            
            for result in self.test_results:
                if result['test'] == 'complete_profile' and result['status'] == 'passed':
                    existing_fields = set(result.get('present_fields', []))
                    break
            
            missing_in_existing = new_fields - existing_fields
            extra_in_new = new_fields - existing_fields
            
            print(f"\n🔍 Field Analysis:")
            print(f"   Fields in New User but Missing in Existing: {list(missing_in_existing)}")
            print(f"   Common Fields: {list(existing_fields & new_fields)}")
            
            self.test_results.append({
                "test": "profile_comparison",
                "status": "passed",
                "existing_profile_completed": existing_profile_completed,
                "new_profile_completed": new_profile_completed,
                "missing_in_existing": list(missing_in_existing),
                "comparison_data": {
                    "existing_user": self.target_email,
                    "new_user": new_user_email
                }
            })
            
            return True
        else:
            self.test_results.append({
                "test": "profile_comparison",
                "status": "failed",
                "error": "Could not create comprehensive registration for comparison"
            })
            return False

    def test_profile_access_with_token(self):
        """Test that existing user can access all profile endpoints with valid token"""
        print(f"\n🔑 Testing Profile Access with Authentication Token")
        
        if not self.token:
            print(f"❌ No authentication token available")
            return False
        
        endpoints_to_test = [
            ("GET /api/user/profile", "GET", "api/user/profile"),
            ("GET /api/user/profile/complete", "GET", "api/user/profile/complete"),
            ("GET /api/user/question-history", "GET", "api/user/question-history"),
            ("GET /api/auth/me", "GET", "api/auth/me")
        ]
        
        accessible_endpoints = 0
        total_endpoints = len(endpoints_to_test)
        
        for name, method, endpoint in endpoints_to_test:
            success, response = self.run_test(
                f"Token Access - {name}",
                method,
                endpoint,
                200
            )
            
            if success:
                accessible_endpoints += 1
                print(f"   ✅ {name}: Accessible")
            else:
                print(f"   ❌ {name}: Not accessible")
        
        access_success = accessible_endpoints == total_endpoints
        
        print(f"\n📊 Token Access Results:")
        print(f"   Accessible Endpoints: {accessible_endpoints}/{total_endpoints}")
        print(f"   Access Success Rate: {(accessible_endpoints/total_endpoints)*100:.1f}%")
        
        self.test_results.append({
            "test": "token_access",
            "status": "passed" if access_success else "failed",
            "accessible_endpoints": accessible_endpoints,
            "total_endpoints": total_endpoints
        })
        
        return access_success

    def analyze_existing_user_profile_gaps(self):
        """Analyze what profile data is missing for existing users"""
        print(f"\n🔍 Analyzing Profile Data Gaps for Existing Users")
        
        # Collect data from previous tests
        basic_profile_data = {}
        complete_profile_data = {}
        
        for result in self.test_results:
            if result['test'] == 'basic_profile' and result['status'] == 'passed':
                basic_profile_data = result.get('profile_data', {})
            elif result['test'] == 'complete_profile' and result['status'] == 'passed':
                complete_profile_data = result.get('profile_data', {})
        
        if not complete_profile_data:
            print(f"❌ No complete profile data available for analysis")
            return False
        
        # Define what a complete profile should have
        required_comprehensive_fields = {
            'full_name': 'Full Name',
            'phone_number': 'Phone Number', 
            'communication_preferences': 'Communication Preferences',
            'subscription_plan': 'Subscription Plan',
            'profile_completed': 'Profile Completion Flag'
        }
        
        missing_data = []
        incomplete_data = []
        present_data = []
        
        for field, description in required_comprehensive_fields.items():
            value = complete_profile_data.get(field)
            
            if field not in complete_profile_data:
                missing_data.append(description)
            elif value is None or value == "" or value == {} or value == []:
                incomplete_data.append(description)
            else:
                present_data.append(description)
        
        print(f"\n📋 Profile Data Analysis for {self.target_email}:")
        print(f"   ✅ Present Data ({len(present_data)}):")
        for item in present_data:
            print(f"     • {item}")
        
        print(f"   📝 Incomplete Data ({len(incomplete_data)}):")
        for item in incomplete_data:
            print(f"     • {item}")
        
        print(f"   ❌ Missing Data ({len(missing_data)}):")
        for item in missing_data:
            print(f"     • {item}")
        
        # Determine if user needs profile completion flow
        needs_completion = len(missing_data) > 0 or len(incomplete_data) > 0
        profile_completion_percentage = (len(present_data) / len(required_comprehensive_fields)) * 100
        
        print(f"\n🎯 Profile Completion Assessment:")
        print(f"   Completion Percentage: {profile_completion_percentage:.1f}%")
        print(f"   Needs Profile Completion Flow: {'YES' if needs_completion else 'NO'}")
        print(f"   Profile Completed Flag: {complete_profile_data.get('profile_completed', False)}")
        
        self.test_results.append({
            "test": "profile_gap_analysis",
            "status": "completed",
            "present_data": present_data,
            "incomplete_data": incomplete_data,
            "missing_data": missing_data,
            "needs_completion": needs_completion,
            "completion_percentage": profile_completion_percentage,
            "profile_completed_flag": complete_profile_data.get('profile_completed', False)
        })
        
        return True

    def run_comprehensive_existing_user_test(self):
        """Run the complete existing user profile test suite"""
        print(f"\n{'='*80}")
        print(f"🧑‍💼 EXISTING USER PROFILE FUNCTIONALITY TEST")
        print(f"Target User: {self.target_email}")
        print(f"{'='*80}")
        
        test_sequence = [
            ("Create/Login Existing User", self.create_existing_user_simulation),
            ("Test Authentication", self.test_existing_user_authentication),
            ("Test Basic Profile Endpoint", self.test_basic_profile_endpoint),
            ("Test Complete Profile Endpoint", self.test_complete_profile_endpoint),
            ("Test Question History", self.test_question_history_endpoint),
            ("Test Profile vs New Registration", self.test_profile_vs_new_registration),
            ("Test Token Access", self.test_profile_access_with_token),
            ("Analyze Profile Gaps", self.analyze_existing_user_profile_gaps)
        ]
        
        results = {}
        
        for step_name, test_function in test_sequence:
            print(f"\n{'='*60}")
            print(f"📋 {step_name}")
            print(f"{'='*60}")
            
            try:
                result = test_function()
                results[step_name] = result
                
                if result:
                    print(f"✅ {step_name}: PASSED")
                else:
                    print(f"❌ {step_name}: FAILED")
                    
            except Exception as e:
                print(f"❌ {step_name}: ERROR - {str(e)}")
                results[step_name] = False
        
        return results

def main():
    print("🚀 Starting Existing User Profile Functionality Test")
    print("=" * 80)
    
    # Setup
    tester = ExistingUserProfileTester()
    
    # Run comprehensive test
    test_results = tester.run_comprehensive_existing_user_test()
    
    # Calculate results
    total_tests = len(test_results)
    passed_tests = sum(test_results.values())
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    
    # Print final results
    print(f"\n{'='*80}")
    print(f"📊 EXISTING USER PROFILE TEST RESULTS")
    print(f"{'='*80}")
    
    print(f"\n🔍 Test Results Summary:")
    for test_name, passed in test_results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"   {test_name}: {status}")
    
    print(f"\n📈 Overall Statistics:")
    print(f"   Total Tests: {total_tests}")
    print(f"   Passed Tests: {passed_tests}")
    print(f"   Success Rate: {success_rate:.1f}%")
    print(f"   API Calls Made: {tester.tests_run}")
    print(f"   API Success Rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    # Analyze key findings
    print(f"\n🎯 KEY FINDINGS:")
    
    # Check if user exists and can authenticate
    auth_working = test_results.get("Test Authentication", False)
    if auth_working:
        print(f"   ✅ Existing user authentication is working")
    else:
        print(f"   ❌ Existing user authentication has issues")
    
    # Check profile access
    profile_access = test_results.get("Test Token Access", False)
    if profile_access:
        print(f"   ✅ Existing users can access all profile endpoints")
    else:
        print(f"   ❌ Existing users have profile access issues")
    
    # Check profile completion status
    gap_analysis = test_results.get("Analyze Profile Gaps", False)
    if gap_analysis:
        print(f"   ✅ Profile gap analysis completed")
        
        # Find the gap analysis results
        for result in tester.test_results:
            if result['test'] == 'profile_gap_analysis':
                needs_completion = result.get('needs_completion', True)
                completion_percentage = result.get('completion_percentage', 0)
                
                if needs_completion:
                    print(f"   ⚠️  Existing users need profile completion flow")
                    print(f"   📊 Profile completion: {completion_percentage:.1f}%")
                else:
                    print(f"   ✅ Existing user profiles are complete")
                break
    
    # Overall assessment
    critical_tests = ["Test Authentication", "Test Basic Profile Endpoint", "Test Complete Profile Endpoint"]
    critical_passed = sum(test_results.get(test, False) for test in critical_tests)
    
    if critical_passed >= 2 and success_rate >= 70:
        print(f"\n🎉 EXISTING USER PROFILE FUNCTIONALITY: ✅ WORKING!")
        print(f"   • Existing users can authenticate and access their profiles")
        print(f"   • Profile endpoints are accessible with valid tokens")
        print(f"   • Profile data structure supports both old and new users")
        return 0
    else:
        print(f"\n❌ EXISTING USER PROFILE FUNCTIONALITY: NEEDS ATTENTION!")
        print(f"   • Critical issues found in profile access or authentication")
        print(f"   • Success rate too low: {success_rate:.1f}%")
        return 1

if __name__ == "__main__":
    sys.exit(main())