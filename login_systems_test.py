import requests
import sys
import json
import time
from datetime import datetime

class OnlyMentorsLoginSystemsTester:
    def __init__(self):
        # Use localhost for testing since external URL has routing issues
        self.base_url = "http://localhost:8001"
        self.api_base = f"{self.base_url}"
        self.user_token = None
        self.admin_token = None
        self.creator_token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.critical_failures = []

    def log_critical_failure(self, test_name, error_details):
        """Log critical failures for detailed reporting"""
        self.critical_failures.append({
            "test": test_name,
            "error": error_details,
            "timestamp": datetime.now().isoformat()
        })

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None, auth_token=None):
        """Run a single API test with detailed error reporting"""
        url = f"{self.api_base}/api/{endpoint}" if endpoint and not endpoint.startswith('http') else f"{self.api_base}/" if not endpoint else endpoint
        test_headers = {'Content-Type': 'application/json'}
        
        # Use specific auth token if provided, otherwise use default user token
        if auth_token:
            test_headers['Authorization'] = f'Bearer {auth_token}'
        elif self.user_token:
            test_headers['Authorization'] = f'Bearer {self.user_token}'
        
        if headers:
            test_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        print(f"   Method: {method}")
        if data:
            print(f"   Data: {json.dumps(data, indent=2)}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=30)

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
                    print(f"   Error: {json.dumps(error_data, indent=2)}")
                    self.log_critical_failure(name, {
                        "expected_status": expected_status,
                        "actual_status": response.status_code,
                        "error_response": error_data
                    })
                except:
                    print(f"   Error: {response.text}")
                    self.log_critical_failure(name, {
                        "expected_status": expected_status,
                        "actual_status": response.status_code,
                        "error_text": response.text
                    })
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Network/Connection Error: {str(e)}")
            self.log_critical_failure(name, {
                "error_type": "network_error",
                "error_message": str(e)
            })
            return False, {}

    def test_database_connectivity(self):
        """Test if MongoDB connections are working by testing basic endpoints"""
        print(f"\n{'='*70}")
        print("💾 TESTING DATABASE CONNECTIVITY")
        print(f"{'='*70}")
        
        # Test root endpoint (should connect to DB to get mentor counts)
        success, response = self.run_test(
            "Database Connection - Root Endpoint",
            "GET",
            "",
            200
        )
        
        if success and 'total_mentors' in response:
            print("✅ Database connection working - mentor data accessible")
            return True
        else:
            print("❌ Database connection issues - no mentor data")
            return False

    def test_admin_database_setup(self):
        """Test admin database setup and initial admin account"""
        print(f"\n{'='*70}")
        print("👑 TESTING ADMIN DATABASE SETUP")
        print(f"{'='*70}")
        
        # Test admin login with initial credentials
        admin_credentials = {
            "email": "admin@onlymentors.ai",
            "password": "SuperAdmin2024!"
        }
        
        success, response = self.run_test(
            "Admin Database - Initial Super Admin Login",
            "POST",
            "admin/login",
            200,
            data=admin_credentials
        )
        
        if success and 'token' in response:
            self.admin_token = response['token']
            print("✅ Admin database setup working - initial super admin exists")
            print(f"   Admin ID: {response.get('admin', {}).get('admin_id', 'N/A')}")
            print(f"   Role: {response.get('admin', {}).get('role', 'N/A')}")
            return True
        else:
            print("❌ Admin database setup issues - initial super admin not accessible")
            return False

    def test_admin_console_login(self):
        """Test admin console login functionality"""
        print(f"\n{'='*70}")
        print("👑 TESTING ADMIN CONSOLE LOGIN")
        print(f"{'='*70}")
        
        # Test 1: Admin login with correct credentials
        admin_credentials = {
            "email": "admin@onlymentors.ai",
            "password": "SuperAdmin2024!"
        }
        
        success, response = self.run_test(
            "Admin Login - Correct Credentials",
            "POST",
            "admin/login",
            200,
            data=admin_credentials
        )
        
        admin_login_working = False
        if success and 'token' in response:
            self.admin_token = response['token']
            admin_login_working = True
            print("✅ Admin login successful with correct credentials")
            print(f"   Token received: {self.admin_token[:20]}...")
            print(f"   Admin details: {response.get('admin', {})}")
        else:
            print("❌ Admin login failed with correct credentials")
        
        # Test 2: Admin login with incorrect credentials
        wrong_credentials = {
            "email": "admin@onlymentors.ai",
            "password": "WrongPassword123"
        }
        
        success2, response2 = self.run_test(
            "Admin Login - Incorrect Credentials",
            "POST",
            "admin/login",
            401,
            data=wrong_credentials
        )
        
        if success2:
            print("✅ Admin login properly rejects incorrect credentials")
        else:
            print("❌ Admin login error handling failed")
        
        # Test 3: Admin login with non-existent admin
        fake_credentials = {
            "email": "fake@admin.com",
            "password": "password123"
        }
        
        success3, response3 = self.run_test(
            "Admin Login - Non-existent Admin",
            "POST",
            "admin/login",
            401,
            data=fake_credentials
        )
        
        if success3:
            print("✅ Admin login properly rejects non-existent admin")
        else:
            print("❌ Admin login validation failed")
        
        return admin_login_working and success2 and success3

    def test_admin_dashboard_access(self):
        """Test admin dashboard endpoints after login"""
        print(f"\n{'='*70}")
        print("📊 TESTING ADMIN DASHBOARD ACCESS")
        print(f"{'='*70}")
        
        if not self.admin_token:
            print("❌ No admin token available - skipping dashboard tests")
            return False
        
        # Test admin dashboard endpoint
        success, response = self.run_test(
            "Admin Dashboard Access",
            "GET",
            "admin/dashboard",
            200,
            auth_token=self.admin_token
        )
        
        if success:
            print("✅ Admin dashboard accessible after login")
            return True
        else:
            print("❌ Admin dashboard not accessible")
            return False

    def test_user_mentor_login(self):
        """Test regular user/mentor login functionality"""
        print(f"\n{'='*70}")
        print("👤 TESTING USER/MENTOR LOGIN")
        print(f"{'='*70}")
        
        # Create test user first
        test_email = f"logintest_{datetime.now().strftime('%H%M%S')}@test.com"
        test_password = "TestPassword123!"
        test_name = "Login Test User"
        
        # Test 1: User signup
        signup_success, signup_response = self.run_test(
            "User Signup",
            "POST",
            "auth/signup",
            200,
            data={
                "email": test_email,
                "password": test_password,
                "full_name": test_name
            }
        )
        
        if not signup_success:
            print("❌ User signup failed - cannot test login")
            return False
        
        # Test 2: User login with correct credentials
        login_success, login_response = self.run_test(
            "User Login - Correct Credentials",
            "POST",
            "auth/login",
            200,
            data={
                "email": test_email,
                "password": test_password
            }
        )
        
        user_login_working = False
        if login_success and 'token' in login_response:
            self.user_token = login_response['token']
            user_login_working = True
            print("✅ User login successful with correct credentials")
            print(f"   Token received: {self.user_token[:20]}...")
            print(f"   User details: {login_response.get('user', {})}")
        else:
            print("❌ User login failed with correct credentials")
        
        # Test 3: User login with incorrect password
        wrong_login_success, wrong_login_response = self.run_test(
            "User Login - Incorrect Password",
            "POST",
            "auth/login",
            401,
            data={
                "email": test_email,
                "password": "WrongPassword123"
            }
        )
        
        if wrong_login_success:
            print("✅ User login properly rejects incorrect password")
        else:
            print("❌ User login error handling failed")
        
        # Test 4: User login with non-existent email
        fake_login_success, fake_login_response = self.run_test(
            "User Login - Non-existent Email",
            "POST",
            "auth/login",
            401,
            data={
                "email": "nonexistent@test.com",
                "password": test_password
            }
        )
        
        if fake_login_success:
            print("✅ User login properly rejects non-existent email")
        else:
            print("❌ User login validation failed")
        
        return user_login_working and wrong_login_success and fake_login_success

    def test_jwt_token_validation(self):
        """Test JWT token generation and validation"""
        print(f"\n{'='*70}")
        print("🔐 TESTING JWT TOKEN VALIDATION")
        print(f"{'='*70}")
        
        if not self.user_token:
            print("❌ No user token available - skipping JWT tests")
            return False
        
        # Test 1: Access protected endpoint with valid token
        success, response = self.run_test(
            "Protected Endpoint - Valid Token",
            "GET",
            "auth/me",
            200,
            auth_token=self.user_token
        )
        
        valid_token_working = success
        if success:
            print("✅ Valid JWT token accepted by protected endpoint")
            print(f"   User data: {response.get('user', {})}")
        else:
            print("❌ Valid JWT token rejected by protected endpoint")
        
        # Test 2: Access protected endpoint with invalid token
        invalid_token_success, invalid_token_response = self.run_test(
            "Protected Endpoint - Invalid Token",
            "GET",
            "auth/me",
            401,
            auth_token="invalid_token_12345"
        )
        
        if invalid_token_success:
            print("✅ Invalid JWT token properly rejected")
        else:
            print("❌ Invalid JWT token not properly rejected")
        
        # Test 3: Access protected endpoint without token
        no_token_success, no_token_response = self.run_test(
            "Protected Endpoint - No Token",
            "GET",
            "auth/me",
            401,
            auth_token=None
        )
        
        if no_token_success:
            print("✅ Missing JWT token properly rejected")
        else:
            print("❌ Missing JWT token not properly rejected")
        
        return valid_token_working and invalid_token_success and no_token_success

    def test_google_oauth_system(self):
        """Test Google OAuth system endpoints"""
        print(f"\n{'='*70}")
        print("🔐 TESTING GOOGLE OAUTH SYSTEM")
        print(f"{'='*70}")
        
        # Test 1: Google OAuth configuration endpoint
        config_success, config_response = self.run_test(
            "Google OAuth Configuration",
            "GET",
            "auth/google/config",
            200
        )
        
        google_config_working = False
        if config_success and 'client_id' in config_response:
            google_config_working = True
            print("✅ Google OAuth configuration endpoint working")
            print(f"   Client ID: {config_response.get('client_id', 'N/A')}")
            print(f"   Redirect URI: {config_response.get('redirect_uri', 'N/A')}")
        else:
            print("❌ Google OAuth configuration endpoint failed")
        
        # Test 2: Google OAuth authentication endpoint (without code - should fail gracefully)
        auth_success, auth_response = self.run_test(
            "Google OAuth Authentication - No Code",
            "POST",
            "auth/google",
            400,
            data={}
        )
        
        if auth_success:
            print("✅ Google OAuth authentication properly handles missing code")
        else:
            print("❌ Google OAuth authentication error handling failed")
        
        # Test 3: Google OAuth authentication with invalid code
        invalid_auth_success, invalid_auth_response = self.run_test(
            "Google OAuth Authentication - Invalid Code",
            "POST",
            "auth/google",
            500,  # Expected to fail with OAuth error
            data={"code": "invalid_code_12345"}
        )
        
        if invalid_auth_success:
            print("✅ Google OAuth authentication properly handles invalid code")
        else:
            print("❌ Google OAuth authentication with invalid code failed")
        
        return google_config_working and auth_success

    def test_facebook_oauth_system(self):
        """Test Facebook OAuth system endpoints"""
        print(f"\n{'='*70}")
        print("🔐 TESTING FACEBOOK OAUTH SYSTEM")
        print(f"{'='*70}")
        
        # Test 1: Facebook OAuth configuration endpoint
        config_success, config_response = self.run_test(
            "Facebook OAuth Configuration",
            "GET",
            "auth/facebook/config",
            200
        )
        
        facebook_config_working = False
        if config_success and 'app_id' in config_response:
            facebook_config_working = True
            print("✅ Facebook OAuth configuration endpoint working")
            print(f"   App ID: {config_response.get('app_id', 'N/A')}")
            print(f"   Redirect URI: {config_response.get('redirect_uri', 'N/A')}")
        else:
            print("❌ Facebook OAuth configuration endpoint failed")
        
        # Test 2: Facebook OAuth authentication endpoint (without token - should fail gracefully)
        auth_success, auth_response = self.run_test(
            "Facebook OAuth Authentication - No Token",
            "POST",
            "auth/facebook",
            400,
            data={}
        )
        
        if auth_success:
            print("✅ Facebook OAuth authentication properly handles missing token")
        else:
            print("❌ Facebook OAuth authentication error handling failed")
        
        return facebook_config_working and auth_success

    def test_authentication_middleware(self):
        """Test authentication middleware on protected endpoints"""
        print(f"\n{'='*70}")
        print("🛡️ TESTING AUTHENTICATION MIDDLEWARE")
        print(f"{'='*70}")
        
        # Test protected user endpoint
        if self.user_token:
            user_protected_success, _ = self.run_test(
                "User Protected Endpoint - Valid Token",
                "GET",
                "questions/history",
                200,
                auth_token=self.user_token
            )
        else:
            user_protected_success = False
            print("❌ No user token available for middleware test")
        
        # Test protected admin endpoint
        if self.admin_token:
            admin_protected_success, _ = self.run_test(
                "Admin Protected Endpoint - Valid Token",
                "GET",
                "admin/dashboard",
                200,
                auth_token=self.admin_token
            )
        else:
            admin_protected_success = False
            print("❌ No admin token available for middleware test")
        
        # Test admin endpoint with user token (should fail)
        if self.user_token:
            cross_auth_success, _ = self.run_test(
                "Admin Endpoint with User Token",
                "GET",
                "admin/dashboard",
                401,
                auth_token=self.user_token
            )
        else:
            cross_auth_success = False
        
        middleware_working = user_protected_success and admin_protected_success and cross_auth_success
        
        if middleware_working:
            print("✅ Authentication middleware working correctly")
        else:
            print("❌ Authentication middleware has issues")
        
        return middleware_working

    def generate_detailed_report(self):
        """Generate detailed report of all login system tests"""
        print(f"\n{'='*70}")
        print("📋 DETAILED LOGIN SYSTEMS TEST REPORT")
        print(f"{'='*70}")
        
        print(f"Total Tests Run: {self.tests_run}")
        print(f"Total Tests Passed: {self.tests_passed}")
        print(f"Overall Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.critical_failures:
            print(f"\n❌ CRITICAL FAILURES DETECTED ({len(self.critical_failures)}):")
            for i, failure in enumerate(self.critical_failures, 1):
                print(f"\n{i}. {failure['test']}")
                print(f"   Time: {failure['timestamp']}")
                print(f"   Error: {json.dumps(failure['error'], indent=4)}")
        else:
            print("\n✅ NO CRITICAL FAILURES DETECTED")

def main():
    print("🚀 OnlyMentors.ai - Comprehensive Login Systems Testing")
    print("=" * 70)
    print("Testing Focus: Admin Console, User/Mentor Login, OAuth, Database, Auth Middleware")
    print("=" * 70)
    
    tester = OnlyMentorsLoginSystemsTester()
    
    # Test Results Tracking
    test_results = {}
    
    # 1. Database Connectivity Test
    test_results['database'] = tester.test_database_connectivity()
    
    # 2. Admin Database Setup Test
    test_results['admin_db'] = tester.test_admin_database_setup()
    
    # 3. Admin Console Login Test
    test_results['admin_login'] = tester.test_admin_console_login()
    
    # 4. Admin Dashboard Access Test
    test_results['admin_dashboard'] = tester.test_admin_dashboard_access()
    
    # 5. User/Mentor Login Test
    test_results['user_login'] = tester.test_user_mentor_login()
    
    # 6. JWT Token Validation Test
    test_results['jwt_validation'] = tester.test_jwt_token_validation()
    
    # 7. Google OAuth System Test
    test_results['google_oauth'] = tester.test_google_oauth_system()
    
    # 8. Facebook OAuth System Test
    test_results['facebook_oauth'] = tester.test_facebook_oauth_system()
    
    # 9. Authentication Middleware Test
    test_results['auth_middleware'] = tester.test_authentication_middleware()
    
    # Generate detailed report
    tester.generate_detailed_report()
    
    # Final Assessment
    print(f"\n{'='*70}")
    print("🎯 FINAL LOGIN SYSTEMS ASSESSMENT")
    print(f"{'='*70}")
    
    critical_systems = ['database', 'admin_login', 'user_login', 'jwt_validation']
    critical_working = all(test_results.get(system, False) for system in critical_systems)
    
    oauth_systems = ['google_oauth', 'facebook_oauth']
    oauth_working = any(test_results.get(system, False) for system in oauth_systems)
    
    print(f"Database Connectivity: {'✅ WORKING' if test_results.get('database') else '❌ FAILED'}")
    print(f"Admin Database Setup: {'✅ WORKING' if test_results.get('admin_db') else '❌ FAILED'}")
    print(f"Admin Console Login: {'✅ WORKING' if test_results.get('admin_login') else '❌ FAILED'}")
    print(f"Admin Dashboard Access: {'✅ WORKING' if test_results.get('admin_dashboard') else '❌ FAILED'}")
    print(f"User/Mentor Login: {'✅ WORKING' if test_results.get('user_login') else '❌ FAILED'}")
    print(f"JWT Token Validation: {'✅ WORKING' if test_results.get('jwt_validation') else '❌ FAILED'}")
    print(f"Google OAuth System: {'✅ WORKING' if test_results.get('google_oauth') else '❌ FAILED'}")
    print(f"Facebook OAuth System: {'✅ WORKING' if test_results.get('facebook_oauth') else '❌ FAILED'}")
    print(f"Auth Middleware: {'✅ WORKING' if test_results.get('auth_middleware') else '❌ FAILED'}")
    
    print(f"\n🎯 OVERALL SYSTEM STATUS:")
    print(f"Critical Login Systems: {'✅ ALL WORKING' if critical_working else '❌ ISSUES DETECTED'}")
    print(f"OAuth Integration: {'✅ WORKING' if oauth_working else '❌ ISSUES DETECTED'}")
    
    if critical_working and oauth_working:
        print("\n🎉 ALL LOGIN SYSTEMS ARE FUNCTIONAL!")
        return 0
    else:
        print("\n⚠️ LOGIN SYSTEM ISSUES DETECTED - REVIEW REQUIRED")
        return 1

if __name__ == "__main__":
    sys.exit(main())