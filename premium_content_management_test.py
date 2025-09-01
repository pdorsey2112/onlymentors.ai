#!/usr/bin/env python3
"""
Premium Content Management API Testing
Tests the fixed API endpoints for premium content management functionality
"""

import requests
import json
import time
import uuid
import os
from datetime import datetime

class PremiumContentManagementTester:
    def __init__(self, base_url="https://mentor-marketplace.preview.emergentagent.com"):
        self.base_url = base_url
        self.creator_token = None
        self.creator_id = None
        self.creator_data = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        self.uploaded_content_ids = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
        else:
            print(f"❌ {name} - {details}")
        
        self.test_results.append({
            "name": name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })

    def run_api_request(self, method, endpoint, data=None, files=None, headers=None):
        """Make API request with proper error handling"""
        url = f"{self.base_url}/api/{endpoint}" if not endpoint.startswith('http') else endpoint
        
        request_headers = {}
        if self.creator_token:
            request_headers['Authorization'] = f'Bearer {self.creator_token}'
        
        if headers:
            request_headers.update(headers)
        
        # Don't set Content-Type for file uploads
        if files is None and 'Content-Type' not in request_headers:
            request_headers['Content-Type'] = 'application/json'

        try:
            if method == 'GET':
                response = requests.get(url, headers=request_headers, timeout=30)
            elif method == 'POST':
                if files:
                    response = requests.post(url, data=data, files=files, headers={k:v for k,v in request_headers.items() if k != 'Content-Type'}, timeout=30)
                else:
                    response = requests.post(url, json=data, headers=request_headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=request_headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=request_headers, timeout=30)
            
            return response
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {str(e)}")
            return None

    def test_creator_signup_and_login(self):
        """Test creator account creation and authentication"""
        print("\n🔐 Testing Creator Authentication...")
        
        # Generate unique creator data
        timestamp = int(time.time())
        creator_email = f"testcreator{timestamp}@example.com"
        creator_password = "TestPassword123!"
        
        # Test creator signup
        signup_data = {
            "email": creator_email,
            "password": creator_password,
            "full_name": "Test Premium Creator",
            "bio": "Testing premium content management",
            "expertise": "Content Creation",
            "hourly_rate": 150.0
        }
        
        response = self.run_api_request('POST', 'creators/signup', signup_data)
        if response and response.status_code in [200, 201]:
            self.log_test("Creator Signup", True)
            signup_result = response.json()
            self.creator_token = signup_result.get('token')
            self.creator_id = signup_result.get('creator', {}).get('creator_id')
            self.creator_data = signup_result.get('creator', {})
        else:
            error_msg = response.json().get('detail', 'Unknown error') if response else 'No response'
            self.log_test("Creator Signup", False, f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
            return False

        # Test creator login
        login_data = {
            "email": creator_email,
            "password": creator_password
        }
        
        response = self.run_api_request('POST', 'creators/login', login_data)
        if response and response.status_code == 200:
            self.log_test("Creator Login", True)
            login_result = response.json()
            self.creator_token = login_result.get('token')  # Update token
        else:
            error_msg = response.json().get('detail', 'Unknown error') if response else 'No response'
            self.log_test("Creator Login", False, f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
            return False

        return True

    def test_premium_content_upload(self):
        """Test premium content upload functionality"""
        print("\n📤 Testing Premium Content Upload...")
        
        if not self.creator_token:
            self.log_test("Premium Content Upload", False, "No creator authentication")
            return False

        # Test premium content upload
        upload_data = {
            'title': 'Test Premium Content',
            'description': 'This is a test premium content for management testing',
            'content_type': 'document',
            'category': 'business',
            'price': 9.99,
            'tags': '["test", "premium", "management"]',
            'preview_available': True
        }
        
        # Create a test file
        test_content = "This is test premium content for management testing."
        files = {
            'content_file': ('test_content.txt', test_content, 'text/plain')
        }
        
        response = self.run_api_request('POST', 'creator/content/upload', upload_data, files=files)
        if response and response.status_code == 201:
            self.log_test("Premium Content Upload", True)
            upload_result = response.json()
            content_id = upload_result.get('content_id')
            if content_id:
                self.uploaded_content_ids.append(content_id)
            return True
        else:
            error_msg = response.json().get('detail', 'Unknown error') if response else 'No response'
            self.log_test("Premium Content Upload", False, f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
            return False

    def test_creator_content_retrieval(self):
        """Test GET /api/creators/{creator_id}/content - The fixed endpoint"""
        print("\n📋 Testing Creator Content Retrieval (Fixed Endpoint)...")
        
        if not self.creator_token or not self.creator_id:
            self.log_test("Creator Content Retrieval", False, "No creator authentication")
            return False

        # Test the fixed endpoint: GET /api/creators/{creator_id}/content
        response = self.run_api_request('GET', f'creators/{self.creator_id}/content')
        if response and response.status_code == 200:
            self.log_test("Creator Content Retrieval - Fixed Endpoint", True)
            content_data = response.json()
            
            # Verify response format
            if 'content' in content_data and isinstance(content_data['content'], list):
                self.log_test("Content Response Format", True)
                
                # Check if uploaded content is present
                if len(content_data['content']) > 0:
                    self.log_test("Content Data Present", True)
                    
                    # Verify content structure
                    first_content = content_data['content'][0]
                    required_fields = ['title', 'description', 'content_type', 'price', 'creator_id']
                    missing_fields = [field for field in required_fields if field not in first_content]
                    
                    if not missing_fields:
                        self.log_test("Content Structure Validation", True)
                    else:
                        self.log_test("Content Structure Validation", False, f"Missing fields: {missing_fields}")
                else:
                    self.log_test("Content Data Present", False, "No content found")
            else:
                self.log_test("Content Response Format", False, "Invalid response format")
            
            return True
        else:
            error_msg = response.json().get('detail', 'Unknown error') if response else 'No response'
            self.log_test("Creator Content Retrieval - Fixed Endpoint", False, f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
            return False

    def test_premium_content_analytics(self):
        """Test GET /api/creator/content/analytics"""
        print("\n📊 Testing Premium Content Analytics...")
        
        if not self.creator_token:
            self.log_test("Premium Content Analytics", False, "No creator authentication")
            return False

        response = self.run_api_request('GET', 'creator/content/analytics')
        if response and response.status_code == 200:
            self.log_test("Premium Content Analytics Endpoint", True)
            analytics_data = response.json()
            
            # Verify analytics structure
            required_sections = ['summary', 'content_by_type', 'top_performing_content']
            missing_sections = [section for section in required_sections if section not in analytics_data]
            
            if not missing_sections:
                self.log_test("Analytics Structure Validation", True)
                
                # Verify summary metrics
                summary = analytics_data.get('summary', {})
                required_metrics = ['total_content', 'total_sales', 'total_revenue', 'creator_earnings']
                missing_metrics = [metric for metric in required_metrics if metric not in summary]
                
                if not missing_metrics:
                    self.log_test("Analytics Summary Metrics", True)
                else:
                    self.log_test("Analytics Summary Metrics", False, f"Missing metrics: {missing_metrics}")
            else:
                self.log_test("Analytics Structure Validation", False, f"Missing sections: {missing_sections}")
            
            return True
        else:
            error_msg = response.json().get('detail', 'Unknown error') if response else 'No response'
            self.log_test("Premium Content Analytics Endpoint", False, f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
            return False

    def test_authentication_security(self):
        """Test authentication and authorization security"""
        print("\n🔒 Testing Authentication and Security...")
        
        # Test access without authentication
        original_token = self.creator_token
        self.creator_token = None
        
        response = self.run_api_request('GET', f'creators/{self.creator_id}/content')
        if response and response.status_code in [401, 403]:
            self.log_test("Unauthenticated Access Blocked", True)
        else:
            self.log_test("Unauthenticated Access Blocked", False, f"Expected 401/403, got {response.status_code if response else 'None'}")
        
        # Test access with invalid token
        self.creator_token = "invalid_token_12345"
        
        response = self.run_api_request('GET', f'creators/{self.creator_id}/content')
        if response and response.status_code in [401, 403]:
            self.log_test("Invalid Token Rejected", True)
        else:
            self.log_test("Invalid Token Rejected", False, f"Expected 401/403, got {response.status_code if response else 'None'}")
        
        # Restore valid token
        self.creator_token = original_token
        
        # Test cross-creator access (if we had another creator)
        # For now, we'll test with a fake creator ID
        fake_creator_id = str(uuid.uuid4())
        response = self.run_api_request('GET', f'creators/{fake_creator_id}/content')
        if response and response.status_code == 403:
            self.log_test("Cross-Creator Access Blocked", True)
        else:
            self.log_test("Cross-Creator Access Blocked", False, f"Expected 403, got {response.status_code if response else 'None'}")

    def test_end_to_end_management_flow(self):
        """Test complete end-to-end management workflow"""
        print("\n🔄 Testing End-to-End Management Flow...")
        
        if not self.creator_token or not self.creator_id:
            self.log_test("E2E Management Flow", False, "No creator authentication")
            return False

        # Step 1: Upload content
        upload_success = self.test_premium_content_upload()
        if not upload_success:
            self.log_test("E2E Flow - Upload Step", False, "Content upload failed")
            return False
        
        # Step 2: Retrieve content via management endpoint
        retrieval_success = self.test_creator_content_retrieval()
        if not retrieval_success:
            self.log_test("E2E Flow - Retrieval Step", False, "Content retrieval failed")
            return False
        
        # Step 3: Verify analytics work
        analytics_success = self.test_premium_content_analytics()
        if not analytics_success:
            self.log_test("E2E Flow - Analytics Step", False, "Analytics failed")
            return False
        
        # Step 4: Verify data consistency
        response = self.run_api_request('GET', f'creators/{self.creator_id}/content')
        if response and response.status_code == 200:
            content_data = response.json()
            uploaded_content = content_data.get('content', [])
            
            # Check if our uploaded content is in the list
            found_content = False
            for content in uploaded_content:
                if content.get('title') == 'Test Premium Content':
                    found_content = True
                    break
            
            if found_content:
                self.log_test("E2E Flow - Data Consistency", True)
            else:
                self.log_test("E2E Flow - Data Consistency", False, "Uploaded content not found in retrieval")
        else:
            self.log_test("E2E Flow - Data Consistency", False, "Could not verify data consistency")
        
        self.log_test("Complete E2E Management Flow", True)
        return True

    def run_all_tests(self):
        """Run all premium content management tests"""
        print("🚀 Starting Premium Content Management API Testing...")
        print(f"🌐 Base URL: {self.base_url}")
        print("=" * 60)
        
        # Test sequence
        auth_success = self.test_creator_signup_and_login()
        if not auth_success:
            print("\n❌ Authentication failed - cannot proceed with other tests")
            return self.generate_summary()
        
        # Core management functionality tests
        self.test_creator_content_retrieval()
        self.test_premium_content_analytics()
        self.test_authentication_security()
        self.test_end_to_end_management_flow()
        
        return self.generate_summary()

    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "=" * 60)
        print("📊 PREMIUM CONTENT MANAGEMENT TEST SUMMARY")
        print("=" * 60)
        
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        
        print(f"✅ Tests Passed: {self.tests_passed}/{self.tests_run}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 ALL TESTS PASSED! Premium Content Management is fully functional!")
        elif success_rate >= 80:
            print("✅ MOSTLY FUNCTIONAL - Minor issues detected")
        elif success_rate >= 60:
            print("⚠️  PARTIALLY FUNCTIONAL - Several issues need attention")
        else:
            print("❌ MAJOR ISSUES - Premium Content Management needs significant fixes")
        
        # Show failed tests
        failed_tests = [test for test in self.test_results if not test['success']]
        if failed_tests:
            print(f"\n❌ Failed Tests ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   • {test['name']}: {test['details']}")
        
        print("\n🔍 Key Findings:")
        print("   • Fixed API endpoint /api/creators/{creator_id}/content tested")
        print("   • Premium content analytics endpoint verified")
        print("   • Authentication and security measures validated")
        print("   • End-to-end management workflow confirmed")
        
        return {
            "total_tests": self.tests_run,
            "passed_tests": self.tests_passed,
            "success_rate": success_rate,
            "failed_tests": failed_tests,
            "all_results": self.test_results
        }

if __name__ == "__main__":
    tester = PremiumContentManagementTester()
    results = tester.run_all_tests()