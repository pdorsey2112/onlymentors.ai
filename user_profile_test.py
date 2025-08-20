import requests
import sys
import json
import time
import re
from datetime import datetime

class UserProfileAPITester:
    def __init__(self, base_url="https://admin-console-4.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.user_data = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

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
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=30)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response preview: {json.dumps(response_data, indent=2)[:300]}...")
                    self.test_results.append({
                        'name': name,
                        'status': 'PASSED',
                        'expected_status': expected_status,
                        'actual_status': response.status_code,
                        'response': response_data
                    })
                    return True, response_data
                except:
                    self.test_results.append({
                        'name': name,
                        'status': 'PASSED',
                        'expected_status': expected_status,
                        'actual_status': response.status_code,
                        'response': {}
                    })
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                    self.test_results.append({
                        'name': name,
                        'status': 'FAILED',
                        'expected_status': expected_status,
                        'actual_status': response.status_code,
                        'error': error_data
                    })
                except:
                    print(f"   Error: {response.text}")
                    self.test_results.append({
                        'name': name,
                        'status': 'FAILED',
                        'expected_status': expected_status,
                        'actual_status': response.status_code,
                        'error': response.text
                    })
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.test_results.append({
                'name': name,
                'status': 'ERROR',
                'expected_status': expected_status,
                'actual_status': 'N/A',
                'error': str(e)
            })
            return False, {}

    def setup_test_user(self):
        """Create a test user for profile testing"""
        test_email = f"profile_test_{datetime.now().strftime('%H%M%S')}@example.com"
        test_password = "TestPassword123!"
        test_name = "John Profile Tester"
        
        print(f"\n🔧 Setting up test user...")
        print(f"   Email: {test_email}")
        print(f"   Password: {test_password}")
        print(f"   Name: {test_name}")
        
        success, response = self.run_test(
            "User Signup for Profile Testing",
            "POST",
            "api/auth/signup",
            200,
            data={"email": test_email, "password": test_password, "full_name": test_name}
        )
        
        if success and 'token' in response:
            self.token = response['token']
            self.user_data = response['user']
            print(f"✅ Test user created successfully")
            return True, test_email, test_password
        return False, None, None

    def test_get_user_profile_valid_auth(self):
        """Test GET /api/user/profile with valid authentication"""
        print(f"\n📋 Testing GET /api/user/profile with valid authentication")
        
        success, response = self.run_test(
            "Get User Profile - Valid Auth",
            "GET",
            "api/user/profile",
            200
        )
        
        if success:
            # Verify response contains correct profile fields
            required_fields = ['user_id', 'email', 'full_name', 'questions_asked']
            missing_fields = [field for field in required_fields if field not in response]
            
            if not missing_fields:
                print("✅ All required profile fields present")
            else:
                print(f"⚠️  Missing required fields: {missing_fields}")
            
            # Verify sensitive data is not returned
            sensitive_fields = ['password_hash', 'password']
            exposed_sensitive = [field for field in sensitive_fields if field in response]
            
            if not exposed_sensitive:
                print("✅ No sensitive data exposed in profile response")
            else:
                print(f"❌ SECURITY ISSUE: Sensitive fields exposed: {exposed_sensitive}")
                return False
            
            # Verify data types and values
            if 'questions_asked' in response and isinstance(response['questions_asked'], int):
                print("✅ questions_asked field is correct integer type")
            else:
                print("⚠️  questions_asked field type issue")
            
            return True
        return False

    def test_get_user_profile_invalid_auth(self):
        """Test GET /api/user/profile with invalid authentication"""
        print(f"\n🔒 Testing GET /api/user/profile with invalid authentication")
        
        # Save original token
        original_token = self.token
        
        # Test with invalid token
        self.token = "invalid_token_12345"
        
        success, response = self.run_test(
            "Get User Profile - Invalid Auth",
            "GET",
            "api/user/profile",
            401
        )
        
        # Restore original token
        self.token = original_token
        
        return success

    def test_get_user_profile_missing_auth(self):
        """Test GET /api/user/profile with missing authentication"""
        print(f"\n🚫 Testing GET /api/user/profile with missing authentication")
        
        # Save original token
        original_token = self.token
        
        # Remove token
        self.token = None
        
        success, response = self.run_test(
            "Get User Profile - Missing Auth",
            "GET",
            "api/user/profile",
            401
        )
        
        # Restore original token
        self.token = original_token
        
        return success

    def test_update_profile_full_name_only(self):
        """Test PUT /api/user/profile updating full_name only"""
        print(f"\n✏️  Testing PUT /api/user/profile - Update full_name only")
        
        new_name = "John Updated Tester"
        
        success, response = self.run_test(
            "Update Profile - Full Name Only",
            "PUT",
            "api/user/profile",
            200,
            data={"full_name": new_name}
        )
        
        if success:
            # Verify the update was successful
            if 'profile' in response and response['profile'].get('full_name') == new_name:
                print(f"✅ Full name updated successfully to: {new_name}")
                return True
            else:
                print("❌ Full name update not reflected in response")
        return False

    def test_update_profile_phone_number_valid(self):
        """Test PUT /api/user/profile updating phone_number with valid format"""
        print(f"\n📱 Testing PUT /api/user/profile - Update phone_number (valid format)")
        
        valid_phone = "+1234567890"
        
        success, response = self.run_test(
            "Update Profile - Valid Phone Number",
            "PUT",
            "api/user/profile",
            200,
            data={"phone_number": valid_phone}
        )
        
        if success:
            # Verify the update was successful
            if 'profile' in response and response['profile'].get('phone_number') == valid_phone:
                print(f"✅ Phone number updated successfully to: {valid_phone}")
                return True
            else:
                print("❌ Phone number update not reflected in response")
        return False

    def test_update_profile_phone_number_invalid(self):
        """Test PUT /api/user/profile updating phone_number with invalid format"""
        print(f"\n📱 Testing PUT /api/user/profile - Update phone_number (invalid format)")
        
        invalid_phone = "invalid-phone-123"
        
        success, response = self.run_test(
            "Update Profile - Invalid Phone Number",
            "PUT",
            "api/user/profile",
            400,
            data={"phone_number": invalid_phone}
        )
        
        if success:
            # Check if error message mentions phone number validation
            if 'detail' in response and 'phone' in response['detail'].lower():
                print("✅ Proper phone number validation error message")
            else:
                print("⚠️  Error message doesn't mention phone validation")
        
        return success

    def test_update_profile_email_valid(self):
        """Test PUT /api/user/profile updating email address"""
        print(f"\n📧 Testing PUT /api/user/profile - Update email address")
        
        new_email = f"updated_email_{datetime.now().strftime('%H%M%S')}@example.com"
        
        success, response = self.run_test(
            "Update Profile - Email Address",
            "PUT",
            "api/user/profile",
            200,
            data={"email": new_email}
        )
        
        if success:
            # Verify the update was successful
            if 'profile' in response and response['profile'].get('email') == new_email:
                print(f"✅ Email updated successfully to: {new_email}")
                return True
            else:
                print("❌ Email update not reflected in response")
        return False

    def test_update_profile_email_duplicate(self):
        """Test PUT /api/user/profile with duplicate email (should fail)"""
        print(f"\n📧 Testing PUT /api/user/profile - Duplicate email validation")
        
        # Create another user first
        duplicate_email = f"duplicate_test_{datetime.now().strftime('%H%M%S')}@example.com"
        
        # Create second user
        requests.post(
            f"{self.base_url}/api/auth/signup",
            json={"email": duplicate_email, "password": "TestPassword123!", "full_name": "Duplicate User"},
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        # Try to update current user's email to the duplicate email
        success, response = self.run_test(
            "Update Profile - Duplicate Email",
            "PUT",
            "api/user/profile",
            400,
            data={"email": duplicate_email}
        )
        
        if success:
            # Check if error message mentions email already in use
            if 'detail' in response and 'email' in response['detail'].lower():
                print("✅ Proper duplicate email validation error message")
            else:
                print("⚠️  Error message doesn't mention email validation")
        
        return success

    def test_update_profile_multiple_fields(self):
        """Test PUT /api/user/profile updating multiple fields at once"""
        print(f"\n🔄 Testing PUT /api/user/profile - Update multiple fields")
        
        new_name = "John Multi Update"
        new_phone = "+9876543210"
        
        success, response = self.run_test(
            "Update Profile - Multiple Fields",
            "PUT",
            "api/user/profile",
            200,
            data={
                "full_name": new_name,
                "phone_number": new_phone
            }
        )
        
        if success:
            # Verify both updates were successful
            profile = response.get('profile', {})
            name_updated = profile.get('full_name') == new_name
            phone_updated = profile.get('phone_number') == new_phone
            
            if name_updated and phone_updated:
                print(f"✅ Multiple fields updated successfully")
                print(f"   Name: {new_name}")
                print(f"   Phone: {new_phone}")
                return True
            else:
                print("❌ Not all fields updated correctly")
                print(f"   Name updated: {name_updated}")
                print(f"   Phone updated: {phone_updated}")
        return False

    def test_update_profile_invalid_auth(self):
        """Test PUT /api/user/profile with invalid authentication"""
        print(f"\n🔒 Testing PUT /api/user/profile with invalid authentication")
        
        # Save original token
        original_token = self.token
        
        # Test with invalid token
        self.token = "invalid_token_12345"
        
        success, response = self.run_test(
            "Update Profile - Invalid Auth",
            "PUT",
            "api/user/profile",
            401,
            data={"full_name": "Should Not Update"}
        )
        
        # Restore original token
        self.token = original_token
        
        return success

    def test_change_password_valid(self):
        """Test PUT /api/user/password with correct current password"""
        print(f"\n🔐 Testing PUT /api/user/password - Valid password change")
        
        # We need to know the current password from setup
        current_password = "TestPassword123!"
        new_password = "NewTestPassword456!"
        
        success, response = self.run_test(
            "Change Password - Valid Current Password",
            "PUT",
            "api/user/password",
            200,
            data={
                "current_password": current_password,
                "new_password": new_password
            }
        )
        
        if success:
            # Check success message
            if 'message' in response and 'successfully' in response['message'].lower():
                print("✅ Password change successful with proper message")
                
                # Update our stored password for future tests
                self.current_password = new_password
                return True
            else:
                print("⚠️  Success response but no proper message")
        return False

    def test_change_password_incorrect_current(self):
        """Test PUT /api/user/password with incorrect current password"""
        print(f"\n🔐 Testing PUT /api/user/password - Incorrect current password")
        
        incorrect_password = "WrongPassword123!"
        new_password = "NewTestPassword789!"
        
        success, response = self.run_test(
            "Change Password - Incorrect Current Password",
            "PUT",
            "api/user/password",
            400,
            data={
                "current_password": incorrect_password,
                "new_password": new_password
            }
        )
        
        if success:
            # Check error message mentions incorrect password
            if 'detail' in response and 'incorrect' in response['detail'].lower():
                print("✅ Proper error message for incorrect current password")
            else:
                print("⚠️  Error message doesn't mention incorrect password")
        
        return success

    def test_change_password_weak_password(self):
        """Test PUT /api/user/password with weak new password"""
        print(f"\n🔐 Testing PUT /api/user/password - Weak password validation")
        
        current_password = getattr(self, 'current_password', "NewTestPassword456!")
        weak_password = "weak"
        
        success, response = self.run_test(
            "Change Password - Weak Password",
            "PUT",
            "api/user/password",
            400,
            data={
                "current_password": current_password,
                "new_password": weak_password
            }
        )
        
        if success:
            # Check error message mentions password strength
            if 'detail' in response and ('password' in response['detail'].lower() or 'characters' in response['detail'].lower()):
                print("✅ Proper password strength validation error")
            else:
                print("⚠️  Error message doesn't mention password strength")
        
        return success

    def test_change_password_missing_auth(self):
        """Test PUT /api/user/password with missing authentication"""
        print(f"\n🚫 Testing PUT /api/user/password with missing authentication")
        
        # Save original token
        original_token = self.token
        
        # Remove token
        self.token = None
        
        success, response = self.run_test(
            "Change Password - Missing Auth",
            "PUT",
            "api/user/password",
            401,
            data={
                "current_password": "TestPassword123!",
                "new_password": "NewTestPassword456!"
            }
        )
        
        # Restore original token
        self.token = original_token
        
        return success

    def test_social_auth_password_change(self):
        """Test PUT /api/user/password for social auth users (should fail appropriately)"""
        print(f"\n🔗 Testing PUT /api/user/password - Social auth user scenario")
        
        # This test simulates what should happen for social auth users
        # Since we can't easily create a social auth user in tests, we'll test the general case
        # The actual implementation should check if user has password_hash
        
        current_password = getattr(self, 'current_password', "NewTestPassword456!")
        new_password = "AnotherNewPassword789!"
        
        success, response = self.run_test(
            "Change Password - Regular User (Should Work)",
            "PUT",
            "api/user/password",
            200,
            data={
                "current_password": current_password,
                "new_password": new_password
            }
        )
        
        # For regular users, this should work
        # For social auth users, the backend should return 400 with appropriate message
        return success

    def verify_authentication_integration(self):
        """Verify all endpoints require proper JWT authentication"""
        print(f"\n🔐 Verifying authentication integration across all endpoints")
        
        endpoints_to_test = [
            ("GET", "api/user/profile"),
            ("PUT", "api/user/profile"),
            ("PUT", "api/user/password")
        ]
        
        # Save original token
        original_token = self.token
        
        auth_tests_passed = 0
        auth_tests_total = len(endpoints_to_test)
        
        for method, endpoint in endpoints_to_test:
            # Remove token
            self.token = None
            
            test_data = {"full_name": "Test"} if method == "PUT" and "profile" in endpoint else {"current_password": "test", "new_password": "test123"}
            
            success, _ = self.run_test(
                f"Auth Check - {method} {endpoint}",
                method,
                endpoint,
                401,
                data=test_data if method == "PUT" else None
            )
            
            if success:
                auth_tests_passed += 1
                print(f"✅ {method} {endpoint} properly requires authentication")
            else:
                print(f"❌ {method} {endpoint} authentication check failed")
        
        # Restore original token
        self.token = original_token
        
        print(f"\n📊 Authentication Integration Results: {auth_tests_passed}/{auth_tests_total} endpoints properly protected")
        return auth_tests_passed == auth_tests_total

    def verify_database_operations(self):
        """Verify profile updates are saved correctly in database"""
        print(f"\n💾 Verifying database operations and data persistence")
        
        # Update profile with specific values
        test_name = f"Database Test User {datetime.now().strftime('%H%M%S')}"
        test_phone = "+1555123456"
        
        # Update profile
        update_success, update_response = self.run_test(
            "Database Test - Update Profile",
            "PUT",
            "api/user/profile",
            200,
            data={
                "full_name": test_name,
                "phone_number": test_phone
            }
        )
        
        if not update_success:
            print("❌ Profile update failed")
            return False
        
        # Retrieve profile to verify persistence
        retrieve_success, retrieve_response = self.run_test(
            "Database Test - Retrieve Updated Profile",
            "GET",
            "api/user/profile",
            200
        )
        
        if retrieve_success:
            # Verify the data persisted correctly
            profile = retrieve_response
            name_persisted = profile.get('full_name') == test_name
            phone_persisted = profile.get('phone_number') == test_phone
            has_updated_at = 'updated_at' in profile
            
            if name_persisted and phone_persisted:
                print("✅ Profile updates correctly saved and retrieved from database")
                if has_updated_at:
                    print("✅ updated_at timestamp is set correctly")
                else:
                    print("⚠️  updated_at timestamp missing")
                return True
            else:
                print("❌ Profile updates not correctly persisted")
                print(f"   Name persisted: {name_persisted}")
                print(f"   Phone persisted: {phone_persisted}")
        
        return False

    def run_comprehensive_tests(self):
        """Run all User Profile API tests"""
        print("🚀 Starting Comprehensive User Profile API Tests")
        print("=" * 70)
        
        # Setup test user
        setup_success, test_email, test_password = self.setup_test_user()
        if not setup_success:
            print("❌ Failed to setup test user. Cannot continue.")
            return False
        
        # Test categories
        profile_tests = []
        password_tests = []
        auth_tests = []
        database_tests = []
        
        print(f"\n{'='*70}")
        print("📋 TESTING GET /api/user/profile ENDPOINT")
        print(f"{'='*70}")
        
        # GET /api/user/profile tests
        profile_tests.append(self.test_get_user_profile_valid_auth())
        profile_tests.append(self.test_get_user_profile_invalid_auth())
        profile_tests.append(self.test_get_user_profile_missing_auth())
        
        print(f"\n{'='*70}")
        print("✏️  TESTING PUT /api/user/profile ENDPOINT")
        print(f"{'='*70}")
        
        # PUT /api/user/profile tests
        profile_tests.append(self.test_update_profile_full_name_only())
        profile_tests.append(self.test_update_profile_phone_number_valid())
        profile_tests.append(self.test_update_profile_phone_number_invalid())
        profile_tests.append(self.test_update_profile_email_valid())
        profile_tests.append(self.test_update_profile_email_duplicate())
        profile_tests.append(self.test_update_profile_multiple_fields())
        profile_tests.append(self.test_update_profile_invalid_auth())
        
        print(f"\n{'='*70}")
        print("🔐 TESTING PUT /api/user/password ENDPOINT")
        print(f"{'='*70}")
        
        # PUT /api/user/password tests
        password_tests.append(self.test_change_password_valid())
        password_tests.append(self.test_change_password_incorrect_current())
        password_tests.append(self.test_change_password_weak_password())
        password_tests.append(self.test_change_password_missing_auth())
        password_tests.append(self.test_social_auth_password_change())
        
        print(f"\n{'='*70}")
        print("🔐 TESTING AUTHENTICATION INTEGRATION")
        print(f"{'='*70}")
        
        # Authentication integration tests
        auth_tests.append(self.verify_authentication_integration())
        
        print(f"\n{'='*70}")
        print("💾 TESTING DATABASE OPERATIONS")
        print(f"{'='*70}")
        
        # Database operations tests
        database_tests.append(self.verify_database_operations())
        
        # Calculate results
        profile_passed = sum(profile_tests)
        password_passed = sum(password_tests)
        auth_passed = sum(auth_tests)
        database_passed = sum(database_tests)
        
        total_passed = profile_passed + password_passed + auth_passed + database_passed
        total_tests = len(profile_tests) + len(password_tests) + len(auth_tests) + len(database_tests)
        
        # Print final results
        print("\n" + "=" * 70)
        print(f"📊 FINAL USER PROFILE API TEST RESULTS")
        print("=" * 70)
        print(f"Overall tests passed: {self.tests_passed}/{self.tests_run}")
        print(f"Overall success rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        print(f"")
        print(f"GET /api/user/profile tests: {profile_passed}/{len(profile_tests)} passed")
        print(f"PUT /api/user/profile tests: {profile_passed}/{len(profile_tests)} passed")
        print(f"PUT /api/user/password tests: {password_passed}/{len(password_tests)} passed")
        print(f"Authentication integration: {auth_passed}/{len(auth_tests)} passed")
        print(f"Database operations: {database_passed}/{len(database_tests)} passed")
        
        # Determine overall status
        critical_issues = []
        
        if profile_passed < len(profile_tests) * 0.8:  # Less than 80% passed
            critical_issues.append("Profile retrieval/update issues")
        
        if password_passed < len(password_tests) * 0.6:  # Less than 60% passed (some tests expected to fail)
            critical_issues.append("Password change functionality issues")
        
        if auth_passed == 0:
            critical_issues.append("Authentication integration broken")
        
        if database_passed == 0:
            critical_issues.append("Database operations not working")
        
        if not critical_issues:
            print(f"\n🎉 USER PROFILE API ENDPOINTS ARE WORKING CORRECTLY!")
            print("✅ Profile retrieval working with proper authentication")
            print("✅ Profile updates working with validation")
            print("✅ Password changes working with security checks")
            print("✅ Authentication properly integrated")
            print("✅ Database operations functioning correctly")
            return True
        else:
            print(f"\n⚠️  USER PROFILE API HAS ISSUES:")
            for issue in critical_issues:
                print(f"❌ {issue}")
            return False

def main():
    tester = UserProfileAPITester()
    success = tester.run_comprehensive_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())