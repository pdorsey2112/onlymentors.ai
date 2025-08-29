import requests
import sys
import json
import time
from datetime import datetime

class AuthenticationFlowTester:
    def __init__(self, base_url="https://mentor-marketplace.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.user_data = None
        self.tests_run = 0
        self.tests_passed = 0
        self.auth_issues = []
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
                    print(f"   Response preview: {json.dumps(response_data, indent=2)[:300]}...")
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
                    return False, {"error": response.text}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {"error": str(e)}

    def create_test_user(self):
        """Create a test user for authentication testing"""
        timestamp = datetime.now().strftime('%H%M%S')
        test_email = f"profile.tester@example.com"
        test_password = "TestPass123!"
        test_name = "Profile Tester"
        
        print(f"\n👤 Creating Test User")
        print(f"   Email: {test_email}")
        print(f"   Password: {test_password}")
        print(f"   Name: {test_name}")
        
        success, response = self.run_test(
            "Create Test User",
            "POST",
            "api/auth/signup",
            200,
            data={"email": test_email, "password": test_password, "full_name": test_name}
        )
        
        if success and 'token' in response:
            print(f"✅ Test user created successfully")
            return test_email, test_password, response
        else:
            # User might already exist, try login instead
            print(f"⚠️  User might already exist, trying login...")
            return test_email, test_password, None

    def test_login_api(self, email, password):
        """Test POST /api/auth/login with the created user"""
        print(f"\n🔑 STEP 1: Testing Login API")
        print(f"   Testing login with: {email}")
        
        success, response = self.run_test(
            "Login API Test",
            "POST",
            "api/auth/login",
            200,
            data={"email": email, "password": password}
        )
        
        if success:
            # Verify login response structure
            required_fields = ['token', 'user']
            missing_fields = [field for field in required_fields if field not in response]
            
            if not missing_fields:
                self.token = response['token']
                self.user_data = response['user']
                
                print(f"✅ Login successful with complete response")
                print(f"   Token received: {self.token[:20]}...")
                print(f"   Token length: {len(self.token)} characters")
                print(f"   User data: {json.dumps(self.user_data, indent=2)}")
                
                # Analyze token format
                self.analyze_token_format()
                
                self.test_results.append({
                    "test": "login_api",
                    "status": "passed",
                    "token_length": len(self.token),
                    "user_data": self.user_data
                })
                return True, response
            else:
                print(f"❌ Login response missing required fields: {missing_fields}")
                self.auth_issues.append(f"Login response missing: {missing_fields}")
                self.test_results.append({
                    "test": "login_api",
                    "status": "failed",
                    "error": f"Missing fields: {missing_fields}"
                })
        else:
            print(f"❌ Login API failed")
            self.auth_issues.append("Login API failed")
            self.test_results.append({
                "test": "login_api",
                "status": "failed",
                "error": "Login request failed"
            })
        
        return False, {}

    def analyze_token_format(self):
        """Analyze JWT token format and structure"""
        print(f"\n🔍 Analyzing JWT Token Format")
        
        if not self.token:
            print(f"❌ No token available for analysis")
            return False
        
        # Check JWT format (should have 3 parts separated by dots)
        token_parts = self.token.split('.')
        print(f"   Token parts: {len(token_parts)}")
        
        if len(token_parts) == 3:
            print(f"✅ Token has correct JWT format (3 parts)")
            
            # Try to decode header (first part) - just for format validation
            try:
                import base64
                # Add padding if needed
                header_part = token_parts[0]
                header_part += '=' * (4 - len(header_part) % 4)
                decoded_header = base64.b64decode(header_part)
                header_json = json.loads(decoded_header)
                print(f"   Token header: {header_json}")
                
                if 'typ' in header_json and header_json['typ'] == 'JWT':
                    print(f"✅ Valid JWT header format")
                else:
                    print(f"⚠️  Unexpected JWT header format")
                    
            except Exception as e:
                print(f"⚠️  Could not decode token header: {str(e)}")
        else:
            print(f"❌ Token has incorrect format ({len(token_parts)} parts, expected 3)")
            self.auth_issues.append(f"Invalid JWT format: {len(token_parts)} parts")
            return False
        
        return True

    def test_token_validation(self):
        """Test that the returned token works for authenticated endpoints"""
        print(f"\n🔐 STEP 2: Testing Token Validation")
        
        if not self.token:
            print(f"❌ No token available for validation")
            return False
        
        # Test multiple authenticated endpoints
        auth_endpoints = [
            ("GET", "api/auth/me", "Get Current User"),
            ("GET", "api/user/profile", "Get User Profile"),
            ("GET", "api/questions/history", "Get Question History")
        ]
        
        validation_results = []
        
        for method, endpoint, description in auth_endpoints:
            print(f"\n   Testing {description}")
            success, response = self.run_test(
                f"Token Validation - {description}",
                method,
                endpoint,
                200
            )
            
            validation_results.append({
                "endpoint": endpoint,
                "description": description,
                "success": success,
                "response": response if success else None
            })
            
            if success:
                print(f"   ✅ Token accepted by {endpoint}")
            else:
                print(f"   ❌ Token rejected by {endpoint}")
                self.auth_issues.append(f"Token validation failed for {endpoint}")
        
        # Calculate validation success rate
        successful_validations = sum(1 for r in validation_results if r['success'])
        validation_rate = successful_validations / len(validation_results)
        
        print(f"\n📊 Token Validation Results:")
        print(f"   Successful validations: {successful_validations}/{len(validation_results)}")
        print(f"   Validation success rate: {validation_rate*100:.1f}%")
        
        if validation_rate >= 0.8:  # At least 80% should pass
            print(f"✅ Token validation working correctly")
            self.test_results.append({
                "test": "token_validation",
                "status": "passed",
                "success_rate": validation_rate,
                "results": validation_results
            })
            return True
        else:
            print(f"❌ Token validation issues detected")
            self.test_results.append({
                "test": "token_validation",
                "status": "failed",
                "success_rate": validation_rate,
                "results": validation_results
            })
            return False

    def test_profile_access_after_login(self):
        """Test GET /api/user/profile with the login token"""
        print(f"\n👤 STEP 3: Testing Profile Access After Login")
        
        success, response = self.run_test(
            "Profile Access Test",
            "GET",
            "api/user/profile",
            200
        )
        
        if success:
            # Verify profile response structure
            required_profile_fields = [
                'user_id', 'email', 'full_name', 'questions_asked', 'is_subscribed'
            ]
            
            missing_fields = [field for field in required_profile_fields if field not in response]
            
            if not missing_fields:
                print(f"✅ Profile access successful with complete data")
                print(f"   Profile data structure valid")
                print(f"   User ID: {response.get('user_id')}")
                print(f"   Email: {response.get('email')}")
                print(f"   Full Name: {response.get('full_name')}")
                print(f"   Questions Asked: {response.get('questions_asked')}")
                print(f"   Is Subscribed: {response.get('is_subscribed')}")
                
                # Check if profile data matches login data
                if self.user_data:
                    data_consistency = self.check_profile_data_consistency(response)
                    if data_consistency:
                        print(f"✅ Profile data consistent with login data")
                    else:
                        print(f"⚠️  Profile data inconsistent with login data")
                        self.auth_issues.append("Profile data inconsistency")
                
                self.test_results.append({
                    "test": "profile_access",
                    "status": "passed",
                    "profile_data": response
                })
                return True, response
            else:
                print(f"❌ Profile response missing required fields: {missing_fields}")
                self.auth_issues.append(f"Profile missing fields: {missing_fields}")
                self.test_results.append({
                    "test": "profile_access",
                    "status": "failed",
                    "error": f"Missing fields: {missing_fields}"
                })
        else:
            print(f"❌ Profile access failed")
            self.auth_issues.append("Profile access failed")
            self.test_results.append({
                "test": "profile_access",
                "status": "failed",
                "error": "Profile request failed"
            })
        
        return False, {}

    def check_profile_data_consistency(self, profile_data):
        """Check if profile data is consistent with login data"""
        if not self.user_data:
            return True  # Can't check without login data
        
        consistency_checks = [
            ('user_id', 'user_id'),
            ('email', 'email'),
            ('full_name', 'full_name'),
            ('questions_asked', 'questions_asked'),
            ('is_subscribed', 'is_subscribed')
        ]
        
        inconsistencies = []
        for login_field, profile_field in consistency_checks:
            if login_field in self.user_data and profile_field in profile_data:
                if self.user_data[login_field] != profile_data[profile_field]:
                    inconsistencies.append(f"{login_field}: {self.user_data[login_field]} != {profile_data[profile_field]}")
        
        if inconsistencies:
            print(f"   ⚠️  Data inconsistencies found:")
            for inconsistency in inconsistencies:
                print(f"      {inconsistency}")
            return False
        
        return True

    def test_authentication_state_management(self):
        """Test the complete login → profile access flow"""
        print(f"\n🔄 STEP 4: Testing Authentication State Management")
        
        # Test sequence of authenticated operations
        auth_sequence = [
            ("GET", "api/auth/me", "Verify current user"),
            ("GET", "api/user/profile", "Get profile"),
            ("GET", "api/categories", "Get categories (should work)"),
            ("GET", "api/questions/history", "Get question history"),
            ("GET", "api/user/profile", "Get profile again")
        ]
        
        sequence_results = []
        
        for i, (method, endpoint, description) in enumerate(auth_sequence, 1):
            print(f"\n   Step {i}: {description}")
            success, response = self.run_test(
                f"Auth Sequence {i} - {description}",
                method,
                endpoint,
                200
            )
            
            sequence_results.append({
                "step": i,
                "description": description,
                "endpoint": endpoint,
                "success": success,
                "response_size": len(str(response)) if response else 0
            })
            
            if success:
                print(f"   ✅ Step {i} successful")
            else:
                print(f"   ❌ Step {i} failed")
                self.auth_issues.append(f"Auth sequence step {i} failed: {description}")
        
        # Calculate sequence success rate
        successful_steps = sum(1 for r in sequence_results if r['success'])
        sequence_rate = successful_steps / len(sequence_results)
        
        print(f"\n📊 Authentication Sequence Results:")
        print(f"   Successful steps: {successful_steps}/{len(sequence_results)}")
        print(f"   Sequence success rate: {sequence_rate*100:.1f}%")
        
        if sequence_rate >= 0.8:  # At least 80% should pass
            print(f"✅ Authentication state management working")
            self.test_results.append({
                "test": "auth_state_management",
                "status": "passed",
                "success_rate": sequence_rate,
                "sequence_results": sequence_results
            })
            return True
        else:
            print(f"❌ Authentication state management issues")
            self.test_results.append({
                "test": "auth_state_management",
                "status": "failed",
                "success_rate": sequence_rate,
                "sequence_results": sequence_results
            })
            return False

    def test_token_persistence_and_validity(self):
        """Test token persistence and validity over multiple requests"""
        print(f"\n⏱️ STEP 5: Testing Token Persistence and Validity")
        
        if not self.token:
            print(f"❌ No token available for persistence testing")
            return False
        
        # Test multiple rapid requests to simulate frontend behavior
        rapid_requests = []
        
        for i in range(5):
            print(f"   Making request {i+1}/5...")
            success, response = self.run_test(
                f"Token Persistence Test {i+1}",
                "GET",
                "api/user/profile",
                200
            )
            
            rapid_requests.append({
                "request_number": i+1,
                "success": success,
                "timestamp": datetime.now().isoformat()
            })
            
            # Small delay between requests
            time.sleep(0.5)
        
        # Calculate persistence success rate
        successful_requests = sum(1 for r in rapid_requests if r['success'])
        persistence_rate = successful_requests / len(rapid_requests)
        
        print(f"\n📊 Token Persistence Results:")
        print(f"   Successful requests: {successful_requests}/{len(rapid_requests)}")
        print(f"   Persistence success rate: {persistence_rate*100:.1f}%")
        
        if persistence_rate == 1.0:  # All should pass
            print(f"✅ Token persistence working perfectly")
            self.test_results.append({
                "test": "token_persistence",
                "status": "passed",
                "success_rate": persistence_rate,
                "requests": rapid_requests
            })
            return True
        else:
            print(f"❌ Token persistence issues detected")
            self.auth_issues.append("Token persistence problems")
            self.test_results.append({
                "test": "token_persistence",
                "status": "failed",
                "success_rate": persistence_rate,
                "requests": rapid_requests
            })
            return False

    def debug_authentication_issues(self):
        """Debug authentication issues by testing various scenarios"""
        print(f"\n🔍 STEP 6: Debugging Authentication Issues")
        
        debug_tests = []
        
        # Test 1: Invalid token format
        print(f"\n   Debug Test 1: Invalid Token Format")
        original_token = self.token
        self.token = "invalid.token.format"
        
        success, response = self.run_test(
            "Debug - Invalid Token",
            "GET",
            "api/user/profile",
            401
        )
        
        debug_tests.append({
            "test": "invalid_token_format",
            "expected_behavior": "Should reject with 401",
            "actual_result": "Rejected with 401" if success else "Unexpected behavior",
            "success": success
        })
        
        # Test 2: Missing Authorization header
        print(f"\n   Debug Test 2: Missing Authorization Header")
        self.token = None
        
        success, response = self.run_test(
            "Debug - No Auth Header",
            "GET",
            "api/user/profile",
            401
        )
        
        debug_tests.append({
            "test": "missing_auth_header",
            "expected_behavior": "Should reject with 401",
            "actual_result": "Rejected with 401" if success else "Unexpected behavior",
            "success": success
        })
        
        # Test 3: Malformed Authorization header
        print(f"\n   Debug Test 3: Malformed Authorization Header")
        success, response = self.run_test(
            "Debug - Malformed Auth",
            "GET",
            "api/user/profile",
            401,
            headers={"Authorization": "InvalidFormat token123"}
        )
        
        debug_tests.append({
            "test": "malformed_auth_header",
            "expected_behavior": "Should reject with 401",
            "actual_result": "Rejected with 401" if success else "Unexpected behavior",
            "success": success
        })
        
        # Restore original token
        self.token = original_token
        
        # Test 4: Valid token after restoration
        print(f"\n   Debug Test 4: Valid Token After Restoration")
        success, response = self.run_test(
            "Debug - Valid Token Restored",
            "GET",
            "api/user/profile",
            200
        )
        
        debug_tests.append({
            "test": "valid_token_restored",
            "expected_behavior": "Should accept with 200",
            "actual_result": "Accepted with 200" if success else "Token may be invalid",
            "success": success
        })
        
        # Analyze debug results
        debug_success_rate = sum(1 for t in debug_tests if t['success']) / len(debug_tests)
        
        print(f"\n📊 Debug Test Results:")
        for test in debug_tests:
            status = "✅" if test['success'] else "❌"
            print(f"   {status} {test['test']}: {test['actual_result']}")
        
        print(f"   Debug success rate: {debug_success_rate*100:.1f}%")
        
        self.test_results.append({
            "test": "debug_authentication",
            "status": "passed" if debug_success_rate >= 0.75 else "failed",
            "success_rate": debug_success_rate,
            "debug_tests": debug_tests
        })
        
        return debug_success_rate >= 0.75

    def test_jwt_token_expiration_and_encoding(self):
        """Test JWT token expiration and encoding"""
        print(f"\n🕐 STEP 7: Testing JWT Token Expiration and Encoding")
        
        if not self.token:
            print(f"❌ No token available for expiration testing")
            return False
        
        try:
            import base64
            import json
            
            # Decode JWT payload (second part)
            token_parts = self.token.split('.')
            if len(token_parts) != 3:
                print(f"❌ Invalid JWT format for expiration testing")
                return False
            
            # Decode payload
            payload_part = token_parts[1]
            payload_part += '=' * (4 - len(payload_part) % 4)  # Add padding
            decoded_payload = base64.b64decode(payload_part)
            payload_json = json.loads(decoded_payload)
            
            print(f"✅ JWT payload decoded successfully")
            print(f"   Payload keys: {list(payload_json.keys())}")
            
            # Check for required JWT fields
            jwt_fields = ['exp', 'user_id']  # Based on backend code
            missing_jwt_fields = [field for field in jwt_fields if field not in payload_json]
            
            if not missing_jwt_fields:
                print(f"✅ JWT contains required fields")
                
                # Check expiration
                if 'exp' in payload_json:
                    exp_timestamp = payload_json['exp']
                    exp_datetime = datetime.fromtimestamp(exp_timestamp)
                    current_datetime = datetime.now()
                    
                    print(f"   Token expires at: {exp_datetime}")
                    print(f"   Current time: {current_datetime}")
                    
                    if exp_datetime > current_datetime:
                        time_remaining = exp_datetime - current_datetime
                        print(f"✅ Token is valid (expires in {time_remaining})")
                    else:
                        print(f"❌ Token has expired")
                        self.auth_issues.append("JWT token expired")
                        return False
                
                # Check user_id
                if 'user_id' in payload_json:
                    token_user_id = payload_json['user_id']
                    if self.user_data and 'user_id' in self.user_data:
                        if token_user_id == self.user_data['user_id']:
                            print(f"✅ JWT user_id matches login user_id")
                        else:
                            print(f"❌ JWT user_id mismatch")
                            self.auth_issues.append("JWT user_id mismatch")
                            return False
                    else:
                        print(f"   JWT user_id: {token_user_id}")
                
                self.test_results.append({
                    "test": "jwt_expiration_encoding",
                    "status": "passed",
                    "payload": payload_json,
                    "expires_at": exp_datetime.isoformat() if 'exp' in payload_json else None
                })
                return True
            else:
                print(f"❌ JWT missing required fields: {missing_jwt_fields}")
                self.auth_issues.append(f"JWT missing fields: {missing_jwt_fields}")
                self.test_results.append({
                    "test": "jwt_expiration_encoding",
                    "status": "failed",
                    "error": f"Missing fields: {missing_jwt_fields}"
                })
                return False
                
        except Exception as e:
            print(f"❌ JWT decoding failed: {str(e)}")
            self.auth_issues.append(f"JWT decoding error: {str(e)}")
            self.test_results.append({
                "test": "jwt_expiration_encoding",
                "status": "failed",
                "error": str(e)
            })
            return False

    def test_middleware_authentication_problems(self):
        """Test for middleware authentication problems"""
        print(f"\n🔧 STEP 8: Testing Middleware Authentication Problems")
        
        # Test different authentication scenarios that might cause middleware issues
        middleware_tests = []
        
        # Test 1: Case sensitivity of Bearer token
        print(f"\n   Middleware Test 1: Bearer Token Case Sensitivity")
        original_token = self.token
        
        # Test with lowercase 'bearer'
        success, response = self.run_test(
            "Middleware - Lowercase Bearer",
            "GET",
            "api/user/profile",
            200,
            headers={"Authorization": f"bearer {self.token}"}
        )
        
        middleware_tests.append({
            "test": "lowercase_bearer",
            "success": success,
            "description": "Bearer token with lowercase 'bearer'"
        })
        
        # Test 2: Extra spaces in Authorization header
        print(f"\n   Middleware Test 2: Extra Spaces in Auth Header")
        success, response = self.run_test(
            "Middleware - Extra Spaces",
            "GET",
            "api/user/profile",
            200,
            headers={"Authorization": f"Bearer  {self.token}  "}
        )
        
        middleware_tests.append({
            "test": "extra_spaces",
            "success": success,
            "description": "Authorization header with extra spaces"
        })
        
        # Test 3: Different HTTP methods with same token
        print(f"\n   Middleware Test 3: Different HTTP Methods")
        methods_to_test = [
            ("GET", "api/user/profile", 200, None),
            ("PUT", "api/user/profile", 200, {"full_name": "Test Update"})
        ]
        
        method_results = []
        for method, endpoint, expected_status, data in methods_to_test:
            success, response = self.run_test(
                f"Middleware - {method} Method",
                method,
                endpoint,
                expected_status,
                data=data
            )
            method_results.append({
                "method": method,
                "success": success
            })
        
        middleware_tests.append({
            "test": "different_methods",
            "success": all(r['success'] for r in method_results),
            "description": "Different HTTP methods with same token",
            "method_results": method_results
        })
        
        # Test 4: Concurrent requests (simulate frontend behavior)
        print(f"\n   Middleware Test 4: Concurrent Request Handling")
        import threading
        import queue
        
        results_queue = queue.Queue()
        
        def make_request(request_id):
            try:
                success, response = self.run_test(
                    f"Concurrent Request {request_id}",
                    "GET",
                    "api/user/profile",
                    200
                )
                results_queue.put({"id": request_id, "success": success})
            except Exception as e:
                results_queue.put({"id": request_id, "success": False, "error": str(e)})
        
        # Start 3 concurrent requests
        threads = []
        for i in range(3):
            thread = threading.Thread(target=make_request, args=(i+1,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Collect results
        concurrent_results = []
        while not results_queue.empty():
            concurrent_results.append(results_queue.get())
        
        concurrent_success = all(r['success'] for r in concurrent_results)
        
        middleware_tests.append({
            "test": "concurrent_requests",
            "success": concurrent_success,
            "description": "Concurrent request handling",
            "results": concurrent_results
        })
        
        # Analyze middleware test results
        middleware_success_rate = sum(1 for t in middleware_tests if t['success']) / len(middleware_tests)
        
        print(f"\n📊 Middleware Test Results:")
        for test in middleware_tests:
            status = "✅" if test['success'] else "❌"
            print(f"   {status} {test['test']}: {test['description']}")
        
        print(f"   Middleware success rate: {middleware_success_rate*100:.1f}%")
        
        if middleware_success_rate >= 0.75:
            print(f"✅ Middleware authentication working correctly")
            self.test_results.append({
                "test": "middleware_authentication",
                "status": "passed",
                "success_rate": middleware_success_rate,
                "middleware_tests": middleware_tests
            })
            return True
        else:
            print(f"❌ Middleware authentication issues detected")
            self.auth_issues.append("Middleware authentication problems")
            self.test_results.append({
                "test": "middleware_authentication",
                "status": "failed",
                "success_rate": middleware_success_rate,
                "middleware_tests": middleware_tests
            })
            return False

    def run_complete_authentication_flow_test(self):
        """Run the complete authentication flow test"""
        print(f"\n{'='*90}")
        print("🔐 COMPLETE AUTHENTICATION FLOW TESTING")
        print("🎯 Focus: Identifying Profile Button Logout Issue")
        print(f"{'='*90}")
        
        # Step 0: Create test user
        email, password, signup_response = self.create_test_user()
        
        # Step 1: Test login API
        login_success, login_response = self.test_login_api(email, password)
        if not login_success:
            print(f"\n❌ CRITICAL: Login API failed - cannot proceed with authentication testing")
            return False
        
        # Step 2: Test token validation
        token_validation_success = self.test_token_validation()
        
        # Step 3: Test profile access after login
        profile_access_success, profile_response = self.test_profile_access_after_login()
        
        # Step 4: Test authentication state management
        auth_state_success = self.test_authentication_state_management()
        
        # Step 5: Test token persistence and validity
        token_persistence_success = self.test_token_persistence_and_validity()
        
        # Step 6: Debug authentication issues
        debug_success = self.debug_authentication_issues()
        
        # Step 7: Test JWT token expiration and encoding
        jwt_success = self.test_jwt_token_expiration_and_encoding()
        
        # Step 8: Test middleware authentication problems
        middleware_success = self.test_middleware_authentication_problems()
        
        return {
            "login_api": login_success,
            "token_validation": token_validation_success,
            "profile_access": profile_access_success,
            "auth_state_management": auth_state_success,
            "token_persistence": token_persistence_success,
            "debug_tests": debug_success,
            "jwt_validation": jwt_success,
            "middleware_tests": middleware_success
        }

    def generate_comprehensive_report(self, test_results):
        """Generate comprehensive authentication flow test report"""
        print(f"\n{'='*90}")
        print("📊 COMPREHENSIVE AUTHENTICATION FLOW TEST REPORT")
        print(f"{'='*90}")
        
        # Calculate overall statistics
        total_tests = len(test_results)
        passed_tests = sum(1 for result in test_results.values() if result)
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"\n📈 Overall Statistics:")
        print(f"   Total Authentication Tests: {total_tests}")
        print(f"   Passed Tests: {passed_tests}")
        print(f"   Failed Tests: {total_tests - passed_tests}")
        print(f"   Success Rate: {success_rate:.1f}%")
        print(f"   Total API Calls Made: {self.tests_run}")
        print(f"   API Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        # Detailed test results
        print(f"\n🔍 Detailed Test Results:")
        for test_name, result in test_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"   {test_name.replace('_', ' ').title()}: {status}")
        
        # Authentication issues summary
        if self.auth_issues:
            print(f"\n🚨 Authentication Issues Identified:")
            for i, issue in enumerate(self.auth_issues, 1):
                print(f"   {i}. {issue}")
        else:
            print(f"\n✅ No Critical Authentication Issues Detected")
        
        # Profile button issue analysis
        print(f"\n🎯 Profile Button Issue Analysis:")
        
        if test_results.get('login_api') and test_results.get('profile_access'):
            print(f"   ✅ Login → Profile Access Flow: WORKING")
            print(f"      - Login API returns valid token and user data")
            print(f"      - Profile endpoint accepts token and returns data")
            print(f"      - No authentication issues in basic flow")
        else:
            print(f"   ❌ Login → Profile Access Flow: BROKEN")
            if not test_results.get('login_api'):
                print(f"      - Login API is failing")
            if not test_results.get('profile_access'):
                print(f"      - Profile access is failing after login")
        
        if test_results.get('token_validation'):
            print(f"   ✅ Token Validation: WORKING")
            print(f"      - JWT tokens are properly formatted and accepted")
        else:
            print(f"   ❌ Token Validation: ISSUES DETECTED")
            print(f"      - JWT tokens may be malformed or rejected")
        
        if test_results.get('token_persistence'):
            print(f"   ✅ Token Persistence: WORKING")
            print(f"      - Tokens remain valid across multiple requests")
        else:
            print(f"   ❌ Token Persistence: ISSUES DETECTED")
            print(f"      - Tokens may be expiring or becoming invalid")
        
        if test_results.get('middleware_tests'):
            print(f"   ✅ Middleware Authentication: WORKING")
            print(f"      - Authentication middleware properly handles requests")
        else:
            print(f"   ❌ Middleware Authentication: ISSUES DETECTED")
            print(f"      - Authentication middleware may have problems")
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        
        if success_rate >= 80:
            print(f"   🎉 Authentication system is working well ({success_rate:.1f}% success rate)")
            print(f"   📝 Profile button logout issue is likely NOT due to backend authentication")
            print(f"   🔍 Investigate frontend routing, state management, or token storage")
            print(f"   ✅ Backend authentication APIs are functioning correctly")
        else:
            print(f"   ⚠️  Authentication system has issues ({success_rate:.1f}% success rate)")
            print(f"   🔧 Profile button logout issue may be due to backend authentication problems")
            
            if not test_results.get('login_api'):
                print(f"   🚨 CRITICAL: Fix login API issues first")
            if not test_results.get('token_validation'):
                print(f"   🚨 CRITICAL: Fix JWT token validation issues")
            if not test_results.get('profile_access'):
                print(f"   🚨 CRITICAL: Fix profile endpoint authentication")
            if not test_results.get('middleware_tests'):
                print(f"   🔧 Fix authentication middleware issues")
        
        # Token analysis
        if self.token:
            print(f"\n🔑 Token Analysis:")
            print(f"   Token Length: {len(self.token)} characters")
            print(f"   Token Format: {'Valid JWT' if len(self.token.split('.')) == 3 else 'Invalid JWT'}")
            print(f"   Token Sample: {self.token[:30]}...")
        
        return success_rate >= 80

def main():
    print("🚀 Starting OnlyMentors.ai Authentication Flow Testing")
    print("🎯 Focus: Complete authentication flow to identify profile button issue")
    print("=" * 90)
    
    # Setup
    tester = AuthenticationFlowTester()
    
    # Run complete authentication flow test
    test_results = tester.run_complete_authentication_flow_test()
    
    if test_results:
        # Generate comprehensive report
        overall_success = tester.generate_comprehensive_report(test_results)
        
        print(f"\n🎯 FINAL ASSESSMENT:")
        if overall_success:
            print("✅ AUTHENTICATION FLOW: WORKING CORRECTLY")
            print("\n🔍 Profile Button Issue Analysis:")
            print("   • Backend authentication APIs are functioning properly")
            print("   • Login → Profile access flow is working")
            print("   • JWT tokens are valid and persistent")
            print("   • Profile button logout issue is likely frontend-related")
            print("\n💡 Next Steps:")
            print("   • Check frontend routing configuration")
            print("   • Verify frontend token storage and retrieval")
            print("   • Investigate frontend authentication state management")
            print("   • Check for frontend JavaScript errors in browser console")
            return 0
        else:
            print("❌ AUTHENTICATION FLOW: CRITICAL ISSUES DETECTED")
            print("\n🚨 Profile Button Issue Analysis:")
            print("   • Backend authentication has problems")
            print("   • Profile button logout issue may be backend-related")
            print("\n💡 Next Steps:")
            print("   • Fix identified backend authentication issues")
            print("   • Re-test authentication flow after fixes")
            print("   • Then investigate frontend if backend issues are resolved")
            return 1
    else:
        print("❌ AUTHENTICATION FLOW TESTING FAILED")
        print("   • Could not complete authentication flow tests")
        print("   • Check API connectivity and basic functionality")
        return 1

if __name__ == "__main__":
    sys.exit(main())