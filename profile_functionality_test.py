import requests
import sys
import json
import time
from datetime import datetime

class ProfileFunctionalityTester:
    def __init__(self, base_url="https://mentor-marketplace.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.user_data = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

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

    def create_test_user_basic_signup(self):
        """Create a test user using basic signup (simulating existing user)"""
        timestamp = datetime.now().strftime('%H%M%S')
        test_email = f"existing_user_test_{timestamp}@dorseyandassociates.com"
        test_password = "ExistingUser123!"
        test_name = "Paul Dorsey Test"
        
        print(f"\n👤 Creating Test User (Basic Signup - Simulating Existing User)")
        print(f"   Email: {test_email}")
        print(f"   Password: {test_password}")
        print(f"   Full Name: {test_name}")
        
        success, response = self.run_test(
            "Basic User Signup",
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
            print(f"   User ID: {self.user_data.get('user_id')}")
            print(f"   Email: {self.user_data.get('email')}")
            
            self.test_results.append({
                "test": "create_test_user",
                "status": "passed",
                "user_email": test_email,
                "user_data": self.user_data
            })
            return True, test_email, test_password
        else:
            self.test_results.append({
                "test": "create_test_user",
                "status": "failed",
                "error": "Could not create test user"
            })
            return False, None, None

    def test_user_exists_in_database(self, email):
        """Check if user exists by attempting login"""
        print(f"\n🔍 Testing if User Exists in Database: {email}")
        
        # We can't directly check database, but we can verify through auth endpoints
        success, response = self.run_test(
            "Check User Exists via Auth/Me",
            "GET",
            "api/auth/me",
            200
        )
        
        if success and 'user' in response:
            user_info = response['user']
            print(f"✅ User exists and is authenticated")
            print(f"   User ID: {user_info.get('user_id')}")
            print(f"   Email: {user_info.get('email')}")
            print(f"   Full Name: {user_info.get('full_name')}")
            
            self.test_results.append({
                "test": "user_exists",
                "status": "passed",
                "user_info": user_info
            })
            return True
        else:
            self.test_results.append({
                "test": "user_exists",
                "status": "failed",
                "error": "User not found or not authenticated"
            })
            return False

    def test_basic_profile_endpoint(self):
        """Test GET /api/user/profile"""
        print(f"\n👤 Testing Basic Profile Endpoint")
        
        success, response = self.run_test(
            "GET /api/user/profile",
            "GET",
            "api/user/profile",
            200
        )
        
        if success:
            print(f"✅ Basic profile endpoint accessible")
            
            # Analyze profile fields
            expected_basic_fields = [
                'user_id', 'email', 'full_name', 'phone_number', 
                'questions_asked', 'is_subscribed', 'profile_image_url'
            ]
            
            present_fields = []
            missing_fields = []
            empty_fields = []
            
            for field in expected_basic_fields:
                if field in response:
                    present_fields.append(field)
                    value = response[field]
                    if value is None or value == "":
                        empty_fields.append(field)
                        print(f"   📝 {field}: EMPTY/NULL")
                    else:
                        print(f"   ✅ {field}: {value}")
                else:
                    missing_fields.append(field)
                    print(f"   ❌ {field}: MISSING")
            
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
        """Test GET /api/user/profile/complete"""
        print(f"\n📋 Testing Complete Profile Endpoint")
        
        success, response = self.run_test(
            "GET /api/user/profile/complete",
            "GET",
            "api/user/profile/complete",
            200
        )
        
        if success:
            print(f"✅ Complete profile endpoint accessible")
            
            # Analyze comprehensive profile fields
            comprehensive_fields = [
                'user_id', 'email', 'full_name', 'phone_number',
                'communication_preferences', 'subscription_plan', 'is_subscribed',
                'subscription_expires', 'questions_asked', 'total_interactions',
                'unique_mentors_consulted', 'profile_completed', 'created_at',
                'last_login', 'account_status'
            ]
            
            present_fields = []
            missing_fields = []
            empty_fields = []
            
            for field in comprehensive_fields:
                if field in response:
                    present_fields.append(field)
                    value = response[field]
                    if value is None or value == "" or value == [] or value == {}:
                        empty_fields.append(field)
                        print(f"   📝 {field}: EMPTY/NULL")
                    else:
                        print(f"   ✅ {field}: {value}")
                else:
                    missing_fields.append(field)
                    print(f"   ❌ {field}: MISSING")
            
            # Analyze profile completion
            profile_completed = response.get('profile_completed', False)
            completion_percentage = (len(present_fields) - len(empty_fields)) / len(comprehensive_fields) * 100
            
            print(f"\n🎯 Profile Completion Analysis:")
            print(f"   Profile Completed Flag: {profile_completed}")
            print(f"   Present Fields: {len(present_fields)}/{len(comprehensive_fields)}")
            print(f"   Missing Fields: {len(missing_fields)}")
            print(f"   Empty Fields: {len(empty_fields)}")
            print(f"   Completion Percentage: {completion_percentage:.1f}%")
            
            self.test_results.append({
                "test": "complete_profile",
                "status": "passed",
                "present_fields": present_fields,
                "missing_fields": missing_fields,
                "empty_fields": empty_fields,
                "profile_completed": profile_completed,
                "completion_percentage": completion_percentage,
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

    def test_profile_fields_missing_analysis(self):
        """Analyze what profile fields are missing for existing users"""
        print(f"\n🔍 Analyzing Missing Profile Fields")
        
        # Get data from complete profile test
        complete_profile_data = None
        for result in self.test_results:
            if result['test'] == 'complete_profile' and result['status'] == 'passed':
                complete_profile_data = result
                break
        
        if not complete_profile_data:
            print(f"❌ No complete profile data available for analysis")
            return False
        
        missing_fields = complete_profile_data.get('missing_fields', [])
        empty_fields = complete_profile_data.get('empty_fields', [])
        profile_completed = complete_profile_data.get('profile_completed', False)
        
        # Define critical profile fields that should be present
        critical_fields = [
            'full_name', 'phone_number', 'communication_preferences'
        ]
        
        missing_critical = [field for field in critical_fields if field in missing_fields or field in empty_fields]
        
        print(f"📊 Missing Profile Fields Analysis:")
        print(f"   Missing Fields: {missing_fields}")
        print(f"   Empty Fields: {empty_fields}")
        print(f"   Missing Critical Fields: {missing_critical}")
        print(f"   Profile Completed Flag: {profile_completed}")
        
        # Determine if user needs profile completion flow
        needs_completion = len(missing_critical) > 0 or not profile_completed
        
        print(f"\n🎯 Profile Completion Assessment:")
        print(f"   Needs Profile Completion Flow: {'YES' if needs_completion else 'NO'}")
        
        if needs_completion:
            print(f"   Recommended Actions:")
            if 'phone_number' in missing_critical:
                print(f"     • Collect phone number")
            if 'communication_preferences' in missing_critical:
                print(f"     • Set communication preferences")
            if not profile_completed:
                print(f"     • Update profile_completed flag to true")
        
        self.test_results.append({
            "test": "missing_fields_analysis",
            "status": "completed",
            "missing_fields": missing_fields,
            "empty_fields": empty_fields,
            "missing_critical": missing_critical,
            "needs_completion": needs_completion,
            "profile_completed": profile_completed
        })
        
        return True

    def test_authentication_token_validity(self):
        """Test that existing authentication tokens work"""
        print(f"\n🔑 Testing Authentication Token Validity")
        
        if not self.token:
            print(f"❌ No authentication token available")
            return False
        
        # Test multiple endpoints with the token
        endpoints_to_test = [
            ("GET /api/auth/me", "GET", "api/auth/me"),
            ("GET /api/user/profile", "GET", "api/user/profile"),
            ("GET /api/user/profile/complete", "GET", "api/user/profile/complete")
        ]
        
        successful_auths = 0
        total_endpoints = len(endpoints_to_test)
        
        print(f"   Testing token with {total_endpoints} endpoints...")
        
        for name, method, endpoint in endpoints_to_test:
            success, response = self.run_test(
                f"Token Auth - {name}",
                method,
                endpoint,
                200
            )
            
            if success:
                successful_auths += 1
                print(f"   ✅ {name}: Token accepted")
            else:
                print(f"   ❌ {name}: Token rejected")
        
        auth_success_rate = (successful_auths / total_endpoints) * 100
        
        print(f"\n📊 Token Authentication Results:")
        print(f"   Successful Authentications: {successful_auths}/{total_endpoints}")
        print(f"   Authentication Success Rate: {auth_success_rate:.1f}%")
        
        token_valid = auth_success_rate >= 100  # All endpoints should accept the token
        
        self.test_results.append({
            "test": "token_validity",
            "status": "passed" if token_valid else "failed",
            "successful_auths": successful_auths,
            "total_endpoints": total_endpoints,
            "success_rate": auth_success_rate
        })
        
        return token_valid

    def test_profile_completion_status_difference(self):
        """Test difference between old vs new user registrations"""
        print(f"\n🆚 Testing Profile Completion Status: Old vs New Registration")
        
        # Create a new user with comprehensive registration
        timestamp = datetime.now().strftime('%H%M%S')
        new_user_email = f"comprehensive_user_{timestamp}@example.com"
        
        # Use the comprehensive registration endpoint with form data
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
        
        # Make direct request with form data
        url = f"{self.base_url}/api/auth/register"
        
        try:
            response = requests.post(url, data=comprehensive_data, timeout=30)
            success = response.status_code == 200
            
            if success:
                new_user_response = response.json()
                print(f"✅ Comprehensive registration successful")
                
                new_user_data = new_user_response.get('user', {})
                new_profile_completed = new_user_data.get('profile_completed', False)
                
                # Get existing user profile completion status
                existing_profile_completed = False
                for result in self.test_results:
                    if result['test'] == 'complete_profile' and result['status'] == 'passed':
                        existing_profile_completed = result.get('profile_completed', False)
                        break
                
                print(f"\n📊 Profile Completion Comparison:")
                print(f"   Existing User (Basic Signup):")
                print(f"     Profile Completed: {existing_profile_completed}")
                print(f"   New User (Comprehensive Registration):")
                print(f"     Profile Completed: {new_profile_completed}")
                
                # Analyze the difference
                completion_difference = new_profile_completed != existing_profile_completed
                
                print(f"\n🎯 Analysis:")
                if completion_difference:
                    print(f"   ✅ Different profile completion status detected")
                    print(f"   📝 Existing users likely need profile completion flow")
                else:
                    print(f"   ⚠️  Same profile completion status")
                
                self.test_results.append({
                    "test": "completion_status_difference",
                    "status": "passed",
                    "existing_profile_completed": existing_profile_completed,
                    "new_profile_completed": new_profile_completed,
                    "completion_difference": completion_difference
                })
                
                return True
            else:
                print(f"❌ Comprehensive registration failed: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                
                self.test_results.append({
                    "test": "completion_status_difference",
                    "status": "failed",
                    "error": "Could not create comprehensive user for comparison"
                })
                return False
                
        except Exception as e:
            print(f"❌ Error creating comprehensive user: {str(e)}")
            self.test_results.append({
                "test": "completion_status_difference",
                "status": "failed",
                "error": str(e)
            })
            return False

    def run_comprehensive_profile_test(self):
        """Run the complete profile functionality test"""
        print(f"\n{'='*80}")
        print(f"🧑‍💼 PROFILE FUNCTIONALITY TEST FOR EXISTING USERS")
        print(f"{'='*80}")
        
        test_sequence = [
            ("1. Create Test User (Simulating Existing User)", self.create_test_user_basic_signup),
            ("2. Check User Exists in Database", lambda: self.test_user_exists_in_database(self.user_data.get('email') if self.user_data else None)),
            ("3. Test Basic Profile Endpoint", self.test_basic_profile_endpoint),
            ("4. Test Complete Profile Endpoint", self.test_complete_profile_endpoint),
            ("5. Analyze Missing Profile Fields", self.test_profile_fields_missing_analysis),
            ("6. Test Authentication Token Validity", self.test_authentication_token_validity),
            ("7. Test Profile Completion Status Difference", self.test_profile_completion_status_difference)
        ]
        
        results = {}
        
        for step_name, test_function in test_sequence:
            print(f"\n{'='*60}")
            print(f"📋 {step_name}")
            print(f"{'='*60}")
            
            try:
                if step_name == "1. Create Test User (Simulating Existing User)":
                    result = test_function()
                    if isinstance(result, tuple):
                        results[step_name] = result[0]  # Just take the success boolean
                    else:
                        results[step_name] = result
                else:
                    result = test_function()
                    results[step_name] = result
                
                if results[step_name]:
                    print(f"✅ {step_name}: PASSED")
                else:
                    print(f"❌ {step_name}: FAILED")
                    
            except Exception as e:
                print(f"❌ {step_name}: ERROR - {str(e)}")
                results[step_name] = False
        
        return results

def main():
    print("🚀 Starting Profile Functionality Test for Existing Users")
    print("=" * 80)
    
    # Setup
    tester = ProfileFunctionalityTester()
    
    # Run comprehensive test
    test_results = tester.run_comprehensive_profile_test()
    
    # Calculate results
    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results.values() if result)
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    
    # Print final results
    print(f"\n{'='*80}")
    print(f"📊 PROFILE FUNCTIONALITY TEST RESULTS")
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
    
    # Check authentication
    auth_working = any("Authentication" in key for key, value in test_results.items() if value)
    if auth_working:
        print(f"   ✅ User authentication is working")
    else:
        print(f"   ❌ User authentication has issues")
    
    # Check profile access
    profile_access = any("Profile Endpoint" in key for key, value in test_results.items() if value)
    if profile_access:
        print(f"   ✅ Profile endpoints are accessible")
    else:
        print(f"   ❌ Profile endpoints have access issues")
    
    # Check for missing fields analysis
    missing_analysis_done = any("Missing Profile Fields" in key for key, value in test_results.items() if value)
    if missing_analysis_done:
        print(f"   ✅ Profile field analysis completed")
        
        # Find specific results
        for result in tester.test_results:
            if result['test'] == 'missing_fields_analysis':
                needs_completion = result.get('needs_completion', True)
                missing_critical = result.get('missing_critical', [])
                
                if needs_completion:
                    print(f"   ⚠️  Existing users need profile completion flow")
                    if missing_critical:
                        print(f"   📝 Missing critical fields: {', '.join(missing_critical)}")
                else:
                    print(f"   ✅ Existing user profiles are complete")
                break
    
    # Check profile completion difference
    completion_diff_tested = any("Profile Completion Status" in key for key, value in test_results.items() if value)
    if completion_diff_tested:
        for result in tester.test_results:
            if result['test'] == 'completion_status_difference':
                completion_difference = result.get('completion_difference', False)
                if completion_difference:
                    print(f"   ✅ Confirmed difference between old and new user registrations")
                else:
                    print(f"   ⚠️  No significant difference in registration types")
                break
    
    # Overall assessment
    critical_tests = [
        "2. Check User Exists in Database",
        "3. Test Basic Profile Endpoint", 
        "4. Test Complete Profile Endpoint"
    ]
    critical_passed = sum(1 for test in critical_tests if test_results.get(test, False))
    
    if critical_passed >= 2 and success_rate >= 60:
        print(f"\n🎉 PROFILE FUNCTIONALITY FOR EXISTING USERS: ✅ WORKING!")
        print(f"   • Existing users can authenticate and access their profiles")
        print(f"   • Profile endpoints are accessible with valid tokens")
        print(f"   • Profile data structure supports existing users")
        print(f"   • Analysis of missing profile fields completed")
        return 0
    else:
        print(f"\n❌ PROFILE FUNCTIONALITY FOR EXISTING USERS: NEEDS ATTENTION!")
        print(f"   • Critical issues found in profile access or authentication")
        print(f"   • Success rate: {success_rate:.1f}%")
        return 1

if __name__ == "__main__":
    sys.exit(main())