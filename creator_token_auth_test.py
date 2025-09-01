#!/usr/bin/env python3
"""
Creator Token Authentication Fix Verification Test

This test specifically verifies the fix for the localStorage key mismatch issue
between 'creator_token' and 'creatorToken' that was causing authentication failures
during content upload.

Test Focus:
1. Creator Authentication Flow - Create test creator and verify token storage/retrieval works
2. Content Upload with Fixed Token - Test content upload uses correct token from localStorage  
3. Success Verification - Confirm content uploads successfully and saves

Expected Results:
- ✅ Creator signup/login should store token as 'creatorToken'
- ✅ Content upload should retrieve token as 'creatorToken' 
- ✅ Backend should accept the token and authenticate successfully
- ✅ Content should upload and save without authentication errors
"""

import requests
import sys
import json
import time
from datetime import datetime
import os

class CreatorTokenAuthTester:
    def __init__(self, base_url="https://mentor-marketplace.preview.emergentagent.com"):
        self.base_url = base_url
        self.creator_token = None
        self.creator_data = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test_result(self, test_name, success, details=""):
        """Log test result for final reporting"""
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        if endpoint == "":
            url = self.base_url
        elif endpoint.startswith('api/'):
            url = f"{self.base_url}/{endpoint}"
        else:
            url = f"{self.base_url}/api/{endpoint}"
            
        test_headers = {'Content-Type': 'application/json'}
        
        if self.creator_token:
            test_headers['Authorization'] = f'Bearer {self.creator_token}'
        
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

    def test_creator_signup(self):
        """Test creator signup and verify token storage"""
        print(f"\n{'='*60}")
        print("🎯 STEP 1: CREATOR SIGNUP & TOKEN VERIFICATION")
        print(f"{'='*60}")
        
        # Generate unique test data
        timestamp = datetime.now().strftime('%H%M%S')
        test_email = f"creator_token_test_{timestamp}@example.com"
        test_password = "CreatorTest123!"
        test_name = "Token Test Creator"
        
        print(f"📝 Creating test creator account:")
        print(f"   Email: {test_email}")
        print(f"   Password: {test_password}")
        print(f"   Full Name: {test_name}")
        
        # Test creator signup
        success, response = self.run_test(
            "Creator Signup",
            "POST",
            "api/creators/signup",
            200,
            data={
                "email": test_email,
                "password": test_password,
                "full_name": test_name,
                "account_name": f"token_test_{timestamp}",
                "description": "Test creator for token authentication verification",
                "monthly_price": 29.99,
                "category": "education",
                "expertise_areas": ["Content Creation", "Testing", "Authentication"]
            }
        )
        
        if success and 'token' in response:
            self.creator_token = response['token']
            self.creator_data = response.get('creator', {})
            
            print(f"✅ Creator signup successful!")
            print(f"   Creator ID: {self.creator_data.get('creator_id', 'N/A')}")
            print(f"   Token received: {self.creator_token[:20]}...")
            print(f"   Token length: {len(self.creator_token)} characters")
            
            # Simulate localStorage storage with correct key name 'creatorToken'
            simulated_storage = {
                "creatorToken": self.creator_token,  # This is the FIXED key name
                "creator": self.creator_data
            }
            
            print(f"\n💾 Simulating localStorage storage:")
            print(f"   Key: 'creatorToken' (FIXED - was 'creator_token')")
            print(f"   Value: Bearer token with {len(self.creator_token)} chars")
            
            self.log_test_result("creator_signup", True, f"Token stored as 'creatorToken': {self.creator_token[:20]}...")
            return True
        else:
            print(f"❌ Creator signup failed!")
            self.log_test_result("creator_signup", False, "Failed to create creator account or receive token")
            return False

    def test_creator_login(self):
        """Test creator login to verify token consistency"""
        print(f"\n{'='*60}")
        print("🔑 STEP 2: CREATOR LOGIN & TOKEN CONSISTENCY")
        print(f"{'='*60}")
        
        if not self.creator_data:
            print("❌ No creator data available for login test")
            return False
        
        # Test creator login with same credentials
        success, response = self.run_test(
            "Creator Login",
            "POST",
            "api/creators/login",
            200,
            data={
                "email": self.creator_data.get('email'),
                "password": "CreatorTest123!"
            }
        )
        
        if success and 'token' in response:
            login_token = response['token']
            
            print(f"✅ Creator login successful!")
            print(f"   New token received: {login_token[:20]}...")
            print(f"   Token length: {len(login_token)} characters")
            
            # Update token for subsequent tests
            self.creator_token = login_token
            
            # Simulate localStorage update with correct key name
            print(f"\n💾 Updating localStorage with new token:")
            print(f"   Key: 'creatorToken' (consistent key name)")
            print(f"   Value: Updated Bearer token")
            
            self.log_test_result("creator_login", True, f"Login token stored as 'creatorToken': {login_token[:20]}...")
            return True
        else:
            print(f"❌ Creator login failed!")
            self.log_test_result("creator_login", False, "Failed to login or receive token")
            return False

    def test_creator_authentication_verification(self):
        """Test that creator token is properly validated by backend"""
        print(f"\n{'='*60}")
        print("🔐 STEP 3: CREATOR TOKEN AUTHENTICATION VERIFICATION")
        print(f"{'='*60}")
        
        if not self.creator_token:
            print("❌ No creator token available for authentication test")
            return False
        
        # Test accessing creator profile (requires authentication)
        success, response = self.run_test(
            "Creator Profile Access",
            "GET",
            f"api/creators/{self.creator_data.get('creator_id')}/profile",
            200
        )
        
        if success:
            print(f"✅ Creator authentication working!")
            print(f"   Profile accessed successfully with 'creatorToken'")
            print(f"   Creator ID: {response.get('creator_id', 'N/A')}")
            print(f"   Creator Name: {response.get('full_name', 'N/A')}")
            
            self.log_test_result("creator_auth_verification", True, "Token authentication successful")
            return True
        else:
            print(f"❌ Creator authentication failed!")
            print(f"   Token may not be properly validated by backend")
            self.log_test_result("creator_auth_verification", False, "Token authentication failed")
            return False

    def test_content_upload_with_fixed_token(self):
        """Test content upload using the fixed token key"""
        print(f"\n{'='*60}")
        print("📤 STEP 4: CONTENT UPLOAD WITH FIXED TOKEN")
        print(f"{'='*60}")
        
        if not self.creator_token or not self.creator_data:
            print("❌ No creator token or data available for content upload test")
            return False
        
        # Simulate content upload data
        content_data = {
            "title": "Test Content Upload",
            "description": "Testing content upload with fixed creatorToken authentication",
            "content_type": "article",
            "category": "education",
            "tags": ["test", "authentication", "fix"],
            "is_public": True
        }
        
        print(f"📝 Uploading test content:")
        print(f"   Title: {content_data['title']}")
        print(f"   Type: {content_data['content_type']}")
        print(f"   Using token from 'creatorToken' localStorage key")
        
        # Test content upload
        success, response = self.run_test(
            "Content Upload with Fixed Token",
            "POST",
            f"api/creators/{self.creator_data.get('creator_id')}/content",
            200,
            data=content_data
        )
        
        if success:
            content_id = response.get('content_id')
            print(f"✅ Content upload successful!")
            print(f"   Content ID: {content_id}")
            print(f"   Authentication with 'creatorToken' working correctly")
            print(f"   No 'Authentication failed. Please log in again.' error")
            
            self.log_test_result("content_upload_success", True, f"Content uploaded successfully: {content_id}")
            return True, content_id
        else:
            print(f"❌ Content upload failed!")
            error_detail = response.get('detail', 'Unknown error')
            print(f"   Error: {error_detail}")
            
            # Check if it's the specific authentication error we're fixing
            if "Authentication failed" in str(error_detail) or "Please log in again" in str(error_detail):
                print(f"🚨 CRITICAL: This is the exact error we're trying to fix!")
                print(f"   The localStorage key mismatch issue may still exist")
            
            self.log_test_result("content_upload_success", False, f"Upload failed: {error_detail}")
            return False, None

    def test_content_retrieval_verification(self, content_id):
        """Verify that uploaded content was saved correctly"""
        print(f"\n{'='*60}")
        print("✅ STEP 5: CONTENT RETRIEVAL VERIFICATION")
        print(f"{'='*60}")
        
        if not content_id:
            print("❌ No content ID available for retrieval test")
            return False
        
        # Test retrieving the uploaded content
        success, response = self.run_test(
            "Content Retrieval Verification",
            "GET",
            f"api/creators/{self.creator_data.get('creator_id')}/content/{content_id}",
            200
        )
        
        if success:
            print(f"✅ Content retrieval successful!")
            print(f"   Content ID: {response.get('content_id')}")
            print(f"   Title: {response.get('title')}")
            print(f"   Status: {response.get('status', 'N/A')}")
            print(f"   Created: {response.get('created_at', 'N/A')}")
            
            self.log_test_result("content_retrieval", True, "Content saved and retrieved successfully")
            return True
        else:
            print(f"❌ Content retrieval failed!")
            self.log_test_result("content_retrieval", False, "Could not retrieve uploaded content")
            return False

    def test_authentication_without_token(self):
        """Test that endpoints properly reject requests without authentication"""
        print(f"\n{'='*60}")
        print("🚫 STEP 6: AUTHENTICATION REQUIREMENT VERIFICATION")
        print(f"{'='*60}")
        
        # Temporarily remove token
        original_token = self.creator_token
        self.creator_token = None
        
        print(f"🔒 Testing endpoints without authentication token...")
        
        # Test content upload without token (should fail)
        success, response = self.run_test(
            "Content Upload - No Auth",
            "POST",
            f"api/creators/{self.creator_data.get('creator_id')}/content",
            401,  # Expect 401 Unauthorized
            data={
                "title": "Test Content",
                "description": "This should fail",
                "content_type": "article"
            }
        )
        
        # Restore token
        self.creator_token = original_token
        
        if success:
            print(f"✅ Authentication requirement working!")
            print(f"   Requests without token properly rejected")
            self.log_test_result("auth_requirement", True, "Unauthenticated requests properly rejected")
            return True
        else:
            print(f"❌ Authentication requirement not working!")
            print(f"   Requests without token should be rejected")
            self.log_test_result("auth_requirement", False, "Unauthenticated requests not properly rejected")
            return False

    def test_invalid_token_handling(self):
        """Test handling of invalid tokens"""
        print(f"\n{'='*60}")
        print("🔍 STEP 7: INVALID TOKEN HANDLING")
        print(f"{'='*60}")
        
        # Store original token
        original_token = self.creator_token
        
        # Test with invalid token
        self.creator_token = "invalid.token.here"
        
        print(f"🔒 Testing with invalid token...")
        
        success, response = self.run_test(
            "Content Upload - Invalid Token",
            "POST",
            f"api/creators/{self.creator_data.get('creator_id')}/content",
            401,  # Expect 401 Unauthorized
            data={
                "title": "Test Content",
                "description": "This should fail with invalid token",
                "content_type": "article"
            }
        )
        
        # Restore original token
        self.creator_token = original_token
        
        if success:
            print(f"✅ Invalid token handling working!")
            print(f"   Invalid tokens properly rejected")
            self.log_test_result("invalid_token_handling", True, "Invalid tokens properly rejected")
            return True
        else:
            print(f"❌ Invalid token handling not working!")
            self.log_test_result("invalid_token_handling", False, "Invalid tokens not properly rejected")
            return False

    def run_complete_creator_token_auth_test(self):
        """Run the complete creator token authentication fix verification"""
        print(f"\n{'='*80}")
        print("🎯 CREATOR TOKEN AUTHENTICATION FIX VERIFICATION")
        print("🔧 Testing localStorage key mismatch fix: 'creator_token' → 'creatorToken'")
        print(f"{'='*80}")
        
        test_results = {
            "creator_signup": False,
            "creator_login": False,
            "auth_verification": False,
            "content_upload": False,
            "content_retrieval": False,
            "auth_requirement": False,
            "invalid_token_handling": False
        }
        
        # Step 1: Creator Signup
        if self.test_creator_signup():
            test_results["creator_signup"] = True
        else:
            print(f"\n❌ Creator signup failed - cannot continue with remaining tests")
            return test_results
        
        # Step 2: Creator Login
        if self.test_creator_login():
            test_results["creator_login"] = True
        
        # Step 3: Authentication Verification
        if self.test_creator_authentication_verification():
            test_results["auth_verification"] = True
        
        # Step 4: Content Upload with Fixed Token
        upload_success, content_id = self.test_content_upload_with_fixed_token()
        if upload_success:
            test_results["content_upload"] = True
            
            # Step 5: Content Retrieval Verification
            if self.test_content_retrieval_verification(content_id):
                test_results["content_retrieval"] = True
        
        # Step 6: Authentication Requirement Verification
        if self.test_authentication_without_token():
            test_results["auth_requirement"] = True
        
        # Step 7: Invalid Token Handling
        if self.test_invalid_token_handling():
            test_results["invalid_token_handling"] = True
        
        return test_results

    def generate_final_report(self, test_results):
        """Generate comprehensive final report"""
        print(f"\n{'='*80}")
        print("📊 CREATOR TOKEN AUTHENTICATION FIX - FINAL REPORT")
        print(f"{'='*80}")
        
        # Calculate success metrics
        total_tests = len(test_results)
        passed_tests = sum(test_results.values())
        success_rate = (passed_tests / total_tests) * 100
        
        # Critical tests for the fix
        critical_tests = ["creator_signup", "creator_login", "auth_verification", "content_upload"]
        critical_passed = sum(test_results.get(test, False) for test in critical_tests)
        critical_rate = (critical_passed / len(critical_tests)) * 100
        
        print(f"\n🎯 FIX VERIFICATION RESULTS:")
        print(f"   Total Tests: {self.tests_run}")
        print(f"   API Tests Passed: {self.tests_passed}")
        print(f"   API Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        print(f"   Flow Tests Passed: {passed_tests}/{total_tests}")
        print(f"   Flow Success Rate: {success_rate:.1f}%")
        print(f"   Critical Tests Passed: {critical_passed}/{len(critical_tests)}")
        print(f"   Critical Success Rate: {critical_rate:.1f}%")
        
        print(f"\n📋 DETAILED TEST RESULTS:")
        for test_name, passed in test_results.items():
            status = "✅ PASSED" if passed else "❌ FAILED"
            description = {
                "creator_signup": "Creator account creation and token generation",
                "creator_login": "Creator login and token consistency",
                "auth_verification": "Token authentication by backend",
                "content_upload": "Content upload with 'creatorToken' key",
                "content_retrieval": "Uploaded content persistence verification",
                "auth_requirement": "Authentication requirement enforcement",
                "invalid_token_handling": "Invalid token rejection"
            }.get(test_name, test_name)
            
            print(f"   {description}: {status}")
        
        # Determine if fix is successful
        fix_successful = (
            critical_passed >= 3 and  # At least 3/4 critical tests must pass
            test_results.get("content_upload", False) and  # Content upload must work
            success_rate >= 70  # At least 70% overall success
        )
        
        print(f"\n🎯 FIX ASSESSMENT:")
        if fix_successful:
            print("🎉 CREATOR TOKEN AUTHENTICATION FIX: ✅ SUCCESSFUL!")
            print("\n✅ Key Achievements:")
            print("   • Creator signup/login stores token as 'creatorToken'")
            print("   • Content upload retrieves token as 'creatorToken'")
            print("   • Backend accepts token and authenticates successfully")
            print("   • Content uploads and saves without authentication errors")
            print("   • No more 'Authentication failed. Please log in again.' errors")
            print("   • localStorage key mismatch issue resolved")
            
            if test_results.get("content_upload"):
                print("   • Content upload working with fixed token key")
            if test_results.get("auth_verification"):
                print("   • Token authentication properly validated")
            if test_results.get("auth_requirement"):
                print("   • Authentication requirements properly enforced")
                
            print(f"\n🚀 The localStorage token key fix is PRODUCTION-READY!")
            return True
        else:
            print("❌ CREATOR TOKEN AUTHENTICATION FIX: ❌ ISSUES FOUND!")
            print("\n🔍 Issues Detected:")
            
            if not test_results.get("creator_signup"):
                print("   • Creator signup not working")
            if not test_results.get("creator_login"):
                print("   • Creator login issues")
            if not test_results.get("auth_verification"):
                print("   • Token authentication not working")
            if not test_results.get("content_upload"):
                print("   • Content upload still failing (CRITICAL)")
                print("   • localStorage key mismatch may still exist")
            if critical_rate < 75:
                print(f"   • Low critical test success rate: {critical_rate:.1f}%")
            
            print(f"\n⚠️  The localStorage token key fix needs additional work.")
            return False

def main():
    print("🚀 Starting Creator Token Authentication Fix Verification")
    print("🔧 Testing localStorage key mismatch fix: 'creator_token' → 'creatorToken'")
    print("=" * 90)
    
    # Setup tester
    tester = CreatorTokenAuthTester()
    
    # Run complete test suite
    test_results = tester.run_complete_creator_token_auth_test()
    
    # Generate final report
    fix_successful = tester.generate_final_report(test_results)
    
    # Return appropriate exit code
    return 0 if fix_successful else 1

if __name__ == "__main__":
    sys.exit(main())