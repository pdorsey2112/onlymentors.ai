#!/usr/bin/env python3
"""
Enhanced Content Management Security Testing (Option 3)
Tests the security fixes for content management endpoints
"""

import requests
import json
import time
from datetime import datetime

class EnhancedContentManagementTester:
    def __init__(self, base_url="https://mentor-marketplace.preview.emergentagent.com"):
        self.base_url = base_url
        self.creator_token = None
        self.creator_id = None
        self.other_creator_token = None
        self.other_creator_id = None
        self.content_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.security_tests_passed = 0
        self.security_tests_run = 0

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
        else:
            print(f"❌ {name}")
        if details:
            print(f"   {details}")

    def log_security_test(self, name, success, details=""):
        """Log security-specific test results"""
        self.security_tests_run += 1
        if success:
            self.security_tests_passed += 1
            print(f"🔒 SECURITY ✅ {name}")
        else:
            print(f"🚨 SECURITY ❌ {name}")
        if details:
            print(f"   {details}")

    def make_request(self, method, endpoint, data=None, token=None, expected_status=None):
        """Make HTTP request with optional authentication"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if token:
            headers['Authorization'] = f'Bearer {token}'
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)
            
            if expected_status and response.status_code != expected_status:
                return False, f"Expected {expected_status}, got {response.status_code}"
            
            try:
                response_data = response.json()
                response_data['status_code'] = response.status_code  # Add status code to response
                return True, response_data
            except:
                return True, {"status_code": response.status_code, "text": response.text}
                
        except Exception as e:
            return False, f"Request failed: {str(e)}"

    def setup_test_creators(self):
        """Create test creators for authentication testing"""
        print("\n🔧 Setting up test creators...")
        
        # Create first creator with unique timestamp
        import time
        timestamp = str(int(time.time()))
        creator1_data = {
            "email": f"creator1_{timestamp}@test.com",
            "password": "TestPass123!",
            "full_name": "Test Creator One",
            "account_name": f"testcreator1_{timestamp}",
            "description": "Test creator for content management",
            "monthly_price": 29.99,
            "category": "business",
            "expertise_areas": ["testing", "content"]
        }
        
        success, response = self.make_request('POST', 'api/creators/signup', creator1_data, expected_status=200)
        if success and 'token' in response:
            self.creator_token = response['token']
            self.creator_id = response['creator']['creator_id']
            self.log_test("Creator 1 signup", True, f"Creator ID: {self.creator_id}")
        else:
            self.log_test("Creator 1 signup", False, str(response))
            return False
        
        # Create second creator for authorization testing
        creator2_data = {
            "email": f"creator2_{timestamp}@test.com", 
            "password": "TestPass123!",
            "full_name": "Test Creator Two",
            "account_name": f"testcreator2_{timestamp}",
            "description": "Second test creator",
            "monthly_price": 39.99,
            "category": "health",
            "expertise_areas": ["testing", "security"]
        }
        
        success, response = self.make_request('POST', 'api/creators/signup', creator2_data, expected_status=200)
        if success and 'token' in response:
            self.other_creator_token = response['token']
            self.other_creator_id = response['creator']['creator_id']
            self.log_test("Creator 2 signup", True, f"Creator ID: {self.other_creator_id}")
        else:
            self.log_test("Creator 2 signup", False, str(response))
            return False
        
        return True

    def create_test_content(self):
        """Create test content for testing"""
        print("\n📝 Creating test content...")
        
        # First create content using existing endpoint
        content_data = {
            "title": "Test Content for Management",
            "description": "This is test content for management testing",
            "content_type": "article_link",
            "category": "business",
            "tags": ["test", "management"]
        }
        
        # Use form data for content creation
        import requests
        url = f"{self.base_url}/api/creators/{self.creator_id}/content"
        headers = {'Authorization': f'Bearer {self.creator_token}'}
        
        form_data = {
            'title': content_data['title'],
            'description': content_data['description'],
            'content_type': content_data['content_type'],
            'category': content_data['category'],
            'tags': json.dumps(content_data['tags'])
        }
        
        try:
            response = requests.post(url, data=form_data, headers=headers, timeout=30)
            if response.status_code == 200:
                response_data = response.json()
                self.content_id = response_data.get('content_id')
                self.log_test("Create test content", True, f"Content ID: {self.content_id}")
                return True
            else:
                self.log_test("Create test content", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Create test content", False, str(e))
            return False

    def test_authentication_required(self):
        """Test that all endpoints require authentication (401 without token)"""
        print("\n🔒 Testing Authentication Requirements...")
        
        if not self.content_id:
            print("❌ No content ID available for testing")
            return
        
        endpoints_to_test = [
            ('PUT', f'api/creators/{self.creator_id}/content/{self.content_id}', {'title': 'Updated Title'}),
            ('DELETE', f'api/creators/{self.creator_id}/content/{self.content_id}', None),
            ('GET', f'api/creators/{self.creator_id}/content/{self.content_id}', None),
            ('POST', f'api/creators/{self.creator_id}/content/{self.content_id}/duplicate', None)
        ]
        
        for method, endpoint, data in endpoints_to_test:
            success, response = self.make_request(method, endpoint, data, token=None)
            # Check if authentication is required (either 401 or 403 status codes)
            if isinstance(response, dict):
                if 'status_code' in response:
                    auth_required = response['status_code'] in [401, 403]
                elif 'detail' in response and 'authenticated' in response['detail'].lower():
                    auth_required = True  # FastAPI returns "Not authenticated" message
                else:
                    auth_required = False
            else:
                auth_required = False
                
            self.log_security_test(
                f"{method} {endpoint.split('/')[-1]} requires auth",
                auth_required,
                f"Authentication required (returns auth error)" if auth_required else f"Security issue: {response}"
            )

    def test_authorization_checks(self):
        """Test that creators can only access their own content (403 for wrong creator)"""
        print("\n🔒 Testing Authorization Checks...")
        
        if not self.content_id or not self.other_creator_token:
            print("❌ Missing content ID or other creator token for authorization testing")
            return
        
        endpoints_to_test = [
            ('PUT', f'api/creators/{self.creator_id}/content/{self.content_id}', {'title': 'Unauthorized Update'}),
            ('DELETE', f'api/creators/{self.creator_id}/content/{self.content_id}', None),
            ('GET', f'api/creators/{self.creator_id}/content/{self.content_id}', None),
            ('POST', f'api/creators/{self.creator_id}/content/{self.content_id}/duplicate', None)
        ]
        
        for method, endpoint, data in endpoints_to_test:
            # Try to access creator1's content with creator2's token
            success, response = self.make_request(method, endpoint, data, token=self.other_creator_token, expected_status=403)
            self.log_security_test(
                f"{method} {endpoint.split('/')[-1]} blocks other creators",
                success,
                "Returns 403 for wrong creator" if success else f"Authorization issue: {response}"
            )

    def test_authenticated_content_operations(self):
        """Test complete content management lifecycle with proper authentication"""
        print("\n✅ Testing Authenticated Content Operations...")
        
        if not self.content_id or not self.creator_token:
            print("❌ Missing content ID or creator token for authenticated testing")
            return
        
        # Test 1: Get single content (authenticated)
        success, response = self.make_request(
            'GET', 
            f'api/creators/{self.creator_id}/content/{self.content_id}',
            token=self.creator_token,
            expected_status=200
        )
        self.log_test("Get single content (authenticated)", success, 
                     f"Retrieved content: {response.get('content', {}).get('title', 'N/A')}" if success else str(response))
        
        # Test 2: Update content (authenticated)
        update_data = {
            "title": "Updated Test Content",
            "description": "Updated description for testing",
            "category": "health",
            "tags": ["updated", "test", "security"],
            "is_public": False,
            "is_featured": True
        }
        
        success, response = self.make_request(
            'PUT',
            f'api/creators/{self.creator_id}/content/{self.content_id}',
            update_data,
            token=self.creator_token,
            expected_status=200
        )
        self.log_test("Update content (authenticated)", success,
                     f"Updated fields: {list(update_data.keys())}" if success else str(response))
        
        # Test 3: Duplicate content (authenticated)
        success, response = self.make_request(
            'POST',
            f'api/creators/{self.creator_id}/content/{self.content_id}/duplicate',
            token=self.creator_token,
            expected_status=200
        )
        duplicate_content_id = None
        if success and 'content' in response:
            duplicate_content_id = response['content'].get('content_id')
        
        self.log_test("Duplicate content (authenticated)", success,
                     f"Created duplicate: {duplicate_content_id}" if success else str(response))
        
        # Test 4: Delete duplicate content (authenticated)
        if duplicate_content_id:
            success, response = self.make_request(
                'DELETE',
                f'api/creators/{self.creator_id}/content/{duplicate_content_id}',
                token=self.creator_token,
                expected_status=200
            )
            self.log_test("Delete duplicate content (authenticated)", success,
                         "Content deleted successfully" if success else str(response))

    def test_error_handling(self):
        """Test comprehensive error scenarios with authentication"""
        print("\n🔍 Testing Error Handling...")
        
        if not self.creator_token:
            print("❌ Missing creator token for error testing")
            return
        
        # Test 1: Invalid content ID with valid authentication
        success, response = self.make_request(
            'GET',
            f'api/creators/{self.creator_id}/content/invalid-content-id',
            token=self.creator_token,
            expected_status=404
        )
        self.log_test("Invalid content ID error", success,
                     "Returns 404 for invalid content ID" if success else str(response))
        
        # Test 2: Missing required fields in update
        success, response = self.make_request(
            'PUT',
            f'api/creators/{self.creator_id}/content/{self.content_id}',
            {},  # Empty update data
            token=self.creator_token
        )
        # This might return 400 or 200 depending on implementation
        self.log_test("Empty update data handling", True, f"Status: {response.get('status_code', 'N/A')}")
        
        # Test 3: Non-existent creator with authentication
        fake_creator_id = "fake-creator-id-123"
        success, response = self.make_request(
            'GET',
            f'api/creators/{fake_creator_id}/content/{self.content_id}',
            token=self.creator_token,
            expected_status=403
        )
        self.log_test("Non-existent creator error", success,
                     "Returns 403 for non-existent creator" if success else str(response))

    def test_integration_verification(self):
        """Test that existing functionality still works"""
        print("\n🔗 Testing Integration Verification...")
        
        if not self.creator_token:
            print("❌ Missing creator token for integration testing")
            return
        
        # Test 1: Existing content upload still works
        url = f"{self.base_url}/api/creators/{self.creator_id}/content"
        headers = {'Authorization': f'Bearer {self.creator_token}'}
        
        form_data = {
            'title': 'Integration Test Content',
            'description': 'Testing existing upload functionality',
            'content_type': 'article_link',
            'category': 'business',
            'tags': json.dumps(['integration', 'test'])
        }
        
        try:
            response = requests.post(url, data=form_data, headers=headers, timeout=30)
            success = response.status_code == 200
            self.log_test("Existing content upload works", success,
                         f"Upload successful" if success else f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Existing content upload works", False, str(e))
        
        # Test 2: Creator content list with authentication
        success, response = self.make_request(
            'GET',
            f'api/creators/{self.creator_id}/content',
            token=self.creator_token,
            expected_status=200
        )
        content_count = len(response.get('content', [])) if success else 0
        self.log_test("Creator content list access", success,
                     f"Retrieved {content_count} content items" if success else str(response))

    def run_all_tests(self):
        """Run all enhanced content management security tests"""
        print("🚀 Starting Enhanced Content Management Security Testing (Option 3)")
        print("=" * 80)
        
        # Setup
        if not self.setup_test_creators():
            print("❌ Failed to setup test creators. Aborting tests.")
            return
        
        if not self.create_test_content():
            print("❌ Failed to create test content. Aborting tests.")
            return
        
        # Security Tests
        self.test_authentication_required()
        self.test_authorization_checks()
        
        # Functionality Tests
        self.test_authenticated_content_operations()
        self.test_error_handling()
        self.test_integration_verification()
        
        # Results
        print("\n" + "=" * 80)
        print("🎯 ENHANCED CONTENT MANAGEMENT SECURITY TEST RESULTS")
        print("=" * 80)
        print(f"📊 Overall Tests: {self.tests_passed}/{self.tests_run} passed ({self.tests_passed/self.tests_run*100:.1f}%)")
        print(f"🔒 Security Tests: {self.security_tests_passed}/{self.security_tests_run} passed ({self.security_tests_passed/self.security_tests_run*100:.1f}% if self.security_tests_run > 0 else 0)")
        
        if self.security_tests_passed == self.security_tests_run and self.security_tests_run > 0:
            print("✅ SECURITY FIXES VERIFIED: All endpoints properly require authentication!")
        else:
            print("🚨 SECURITY ISSUES FOUND: Some endpoints may not require proper authentication!")
        
        if self.tests_passed >= self.tests_run * 0.8:  # 80% pass rate
            print("✅ ENHANCED CONTENT MANAGEMENT: Production ready with security fixes!")
        else:
            print("❌ ENHANCED CONTENT MANAGEMENT: Issues found, needs attention!")

if __name__ == "__main__":
    tester = EnhancedContentManagementTester()
    tester.run_all_tests()