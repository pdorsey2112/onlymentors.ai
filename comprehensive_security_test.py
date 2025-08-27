#!/usr/bin/env python3
"""
Comprehensive Enhanced Content Management Security Test Report
Testing all requirements from the review request
"""

import requests
import json
import time
from datetime import datetime

class ComprehensiveSecurityTest:
    def __init__(self, base_url="https://user-data-restore.preview.emergentagent.com"):
        self.base_url = base_url
        self.creator_token = None
        self.creator_id = None
        self.other_creator_token = None
        self.other_creator_id = None
        self.content_id = None
        self.results = {
            "authentication_tests": [],
            "authorization_tests": [],
            "lifecycle_tests": [],
            "error_handling_tests": [],
            "integration_tests": []
        }

    def make_request(self, method, endpoint, data=None, token=None):
        """Make HTTP request and return response with status code"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if token:
            headers['Authorization'] = f'Bearer {token}'
        
        try:
            response = requests.request(method, url, json=data, headers=headers, timeout=30)
            try:
                response_data = response.json()
                response_data['status_code'] = response.status_code
                return response_data
            except:
                return {"status_code": response.status_code, "text": response.text}
        except Exception as e:
            return {"error": str(e), "status_code": 0}

    def setup_test_environment(self):
        """Setup test creators and content"""
        print("🔧 Setting up test environment...")
        
        timestamp = str(int(time.time()))
        
        # Create first creator
        creator1_data = {
            "email": f"security_test1_{timestamp}@test.com",
            "password": "SecurePass123!",
            "full_name": "Security Test Creator One",
            "account_name": f"sectest1_{timestamp}",
            "description": "Security testing creator",
            "monthly_price": 49.99,
            "category": "business",
            "expertise_areas": ["security", "testing"]
        }
        
        response = self.make_request('POST', 'api/creators/signup', creator1_data)
        if response.get('status_code') == 200 and 'token' in response:
            self.creator_token = response['token']
            self.creator_id = response['creator']['creator_id']
            print(f"✅ Creator 1 setup: {self.creator_id}")
        else:
            print(f"❌ Creator 1 setup failed: {response}")
            return False
        
        # Create second creator
        creator2_data = {
            "email": f"security_test2_{timestamp}@test.com",
            "password": "SecurePass123!",
            "full_name": "Security Test Creator Two",
            "account_name": f"sectest2_{timestamp}",
            "description": "Second security testing creator",
            "monthly_price": 59.99,
            "category": "health",
            "expertise_areas": ["security", "authorization"]
        }
        
        response = self.make_request('POST', 'api/creators/signup', creator2_data)
        if response.get('status_code') == 200 and 'token' in response:
            self.other_creator_token = response['token']
            self.other_creator_id = response['creator']['creator_id']
            print(f"✅ Creator 2 setup: {self.other_creator_id}")
        else:
            print(f"❌ Creator 2 setup failed: {response}")
            return False
        
        # Create test content
        url = f"{self.base_url}/api/creators/{self.creator_id}/content"
        headers = {'Authorization': f'Bearer {self.creator_token}'}
        form_data = {
            'title': 'Security Test Content',
            'description': 'Content for comprehensive security testing',
            'content_type': 'article_link',
            'category': 'business',
            'tags': json.dumps(['security', 'testing', 'management'])
        }
        
        response = requests.post(url, data=form_data, headers=headers, timeout=30)
        if response.status_code == 200:
            self.content_id = response.json().get('content_id')
            print(f"✅ Test content created: {self.content_id}")
            return True
        else:
            print(f"❌ Content creation failed: {response.status_code}")
            return False

    def test_requirement_1_authentication_required(self):
        """Test Requirement 1: All endpoints return 401 without auth"""
        print("\n🔒 REQUIREMENT 1: Testing Authentication Requirements")
        
        endpoints = [
            ('PUT', f'api/creators/{self.creator_id}/content/{self.content_id}', {'title': 'Unauthorized Update'}),
            ('DELETE', f'api/creators/{self.creator_id}/content/{self.content_id}', None),
            ('GET', f'api/creators/{self.creator_id}/content/{self.content_id}', None),
            ('POST', f'api/creators/{self.creator_id}/content/{self.content_id}/duplicate', None)
        ]
        
        for method, endpoint, data in endpoints:
            response = self.make_request(method, endpoint, data, token=None)
            
            # Check if authentication is required (401 or 403 with auth error)
            auth_required = (
                response.get('status_code') in [401, 403] or
                ('detail' in response and 'authenticated' in str(response['detail']).lower())
            )
            
            test_result = {
                "endpoint": f"{method} {endpoint.split('/')[-1]}",
                "expected": "401/403 Unauthorized",
                "actual": f"{response.get('status_code', 'N/A')} - {response.get('detail', 'N/A')}",
                "passed": auth_required
            }
            
            self.results["authentication_tests"].append(test_result)
            
            if auth_required:
                print(f"✅ {method} {endpoint.split('/')[-1]} - Authentication required")
            else:
                print(f"❌ {method} {endpoint.split('/')[-1]} - Security vulnerability!")

    def test_requirement_2_authorization_checks(self):
        """Test Requirement 2: Creators can only access their own content (403 for wrong creator)"""
        print("\n🔒 REQUIREMENT 2: Testing Authorization Checks")
        
        endpoints = [
            ('PUT', f'api/creators/{self.creator_id}/content/{self.content_id}', {'title': 'Unauthorized Update'}),
            ('DELETE', f'api/creators/{self.creator_id}/content/{self.content_id}', None),
            ('GET', f'api/creators/{self.creator_id}/content/{self.content_id}', None),
            ('POST', f'api/creators/{self.creator_id}/content/{self.content_id}/duplicate', None)
        ]
        
        for method, endpoint, data in endpoints:
            # Try to access creator1's content with creator2's token
            response = self.make_request(method, endpoint, data, token=self.other_creator_token)
            
            # Should return 403 Forbidden for wrong creator
            authorized_correctly = response.get('status_code') == 403
            
            test_result = {
                "endpoint": f"{method} {endpoint.split('/')[-1]}",
                "expected": "403 Forbidden (wrong creator)",
                "actual": f"{response.get('status_code', 'N/A')} - {response.get('detail', 'N/A')}",
                "passed": authorized_correctly
            }
            
            self.results["authorization_tests"].append(test_result)
            
            if authorized_correctly:
                print(f"✅ {method} {endpoint.split('/')[-1]} - Authorization working")
            else:
                print(f"❌ {method} {endpoint.split('/')[-1]} - Authorization bypass!")

    def test_requirement_3_complete_lifecycle(self):
        """Test Requirement 3: Complete content management lifecycle with authentication"""
        print("\n✅ REQUIREMENT 3: Testing Complete Content Management Lifecycle")
        
        # Test 1: Get single content
        response = self.make_request('GET', f'api/creators/{self.creator_id}/content/{self.content_id}', token=self.creator_token)
        get_test = {
            "operation": "Get single content",
            "expected": "200 OK with content data",
            "actual": f"{response.get('status_code', 'N/A')} - Content: {response.get('content', {}).get('title', 'N/A')}",
            "passed": response.get('status_code') == 200 and 'content' in response
        }
        self.results["lifecycle_tests"].append(get_test)
        print(f"{'✅' if get_test['passed'] else '❌'} Get content: {get_test['actual']}")
        
        # Test 2: Update content with all fields
        update_data = {
            "title": "Updated Security Test Content",
            "description": "Updated description with comprehensive field testing",
            "category": "health",
            "tags": ["updated", "security", "comprehensive"],
            "is_public": False,
            "is_featured": True
        }
        
        response = self.make_request('PUT', f'api/creators/{self.creator_id}/content/{self.content_id}', update_data, token=self.creator_token)
        update_test = {
            "operation": "Update content (all fields)",
            "expected": "200 OK with updated content",
            "actual": f"{response.get('status_code', 'N/A')} - Updated: {response.get('message', 'N/A')}",
            "passed": response.get('status_code') == 200 and 'content' in response
        }
        self.results["lifecycle_tests"].append(update_test)
        print(f"{'✅' if update_test['passed'] else '❌'} Update content: {update_test['actual']}")
        
        # Test 3: Duplicate content
        response = self.make_request('POST', f'api/creators/{self.creator_id}/content/{self.content_id}/duplicate', token=self.creator_token)
        duplicate_content_id = response.get('content', {}).get('content_id') if response.get('status_code') == 200 else None
        duplicate_test = {
            "operation": "Duplicate content",
            "expected": "200 OK with new content ID",
            "actual": f"{response.get('status_code', 'N/A')} - New ID: {duplicate_content_id or 'N/A'}",
            "passed": response.get('status_code') == 200 and duplicate_content_id is not None
        }
        self.results["lifecycle_tests"].append(duplicate_test)
        print(f"{'✅' if duplicate_test['passed'] else '❌'} Duplicate content: {duplicate_test['actual']}")
        
        # Test 4: Delete duplicate content
        if duplicate_content_id:
            response = self.make_request('DELETE', f'api/creators/{self.creator_id}/content/{duplicate_content_id}', token=self.creator_token)
            delete_test = {
                "operation": "Delete content",
                "expected": "200 OK with deletion confirmation",
                "actual": f"{response.get('status_code', 'N/A')} - {response.get('message', 'N/A')}",
                "passed": response.get('status_code') == 200
            }
            self.results["lifecycle_tests"].append(delete_test)
            print(f"{'✅' if delete_test['passed'] else '❌'} Delete content: {delete_test['actual']}")

    def test_requirement_4_error_handling(self):
        """Test Requirement 4: Comprehensive error scenarios"""
        print("\n🔍 REQUIREMENT 4: Testing Error Handling")
        
        # Test 1: Invalid content ID
        response = self.make_request('GET', f'api/creators/{self.creator_id}/content/invalid-content-id', token=self.creator_token)
        invalid_id_test = {
            "scenario": "Invalid content ID",
            "expected": "404 Not Found",
            "actual": f"{response.get('status_code', 'N/A')} - {response.get('detail', 'N/A')}",
            "passed": response.get('status_code') == 404
        }
        self.results["error_handling_tests"].append(invalid_id_test)
        print(f"{'✅' if invalid_id_test['passed'] else '❌'} Invalid content ID: {invalid_id_test['actual']}")
        
        # Test 2: Non-existent creator
        response = self.make_request('GET', f'api/creators/fake-creator-id/content/{self.content_id}', token=self.creator_token)
        fake_creator_test = {
            "scenario": "Non-existent creator",
            "expected": "403 Forbidden",
            "actual": f"{response.get('status_code', 'N/A')} - {response.get('detail', 'N/A')}",
            "passed": response.get('status_code') == 403
        }
        self.results["error_handling_tests"].append(fake_creator_test)
        print(f"{'✅' if fake_creator_test['passed'] else '❌'} Non-existent creator: {fake_creator_test['actual']}")
        
        # Test 3: Empty update data (should handle gracefully)
        response = self.make_request('PUT', f'api/creators/{self.creator_id}/content/{self.content_id}', {}, token=self.creator_token)
        empty_update_test = {
            "scenario": "Empty update data",
            "expected": "200 OK or 400 Bad Request (handled gracefully)",
            "actual": f"{response.get('status_code', 'N/A')} - {response.get('detail', response.get('message', 'N/A'))}",
            "passed": response.get('status_code') in [200, 400]  # Either should be acceptable
        }
        self.results["error_handling_tests"].append(empty_update_test)
        print(f"{'✅' if empty_update_test['passed'] else '❌'} Empty update: {empty_update_test['actual']}")

    def test_requirement_5_integration_verification(self):
        """Test Requirement 5: No breaking changes to existing functionality"""
        print("\n🔗 REQUIREMENT 5: Testing Integration Verification")
        
        # Test 1: Existing content upload still works
        url = f"{self.base_url}/api/creators/{self.creator_id}/content"
        headers = {'Authorization': f'Bearer {self.creator_token}'}
        form_data = {
            'title': 'Integration Test Content',
            'description': 'Testing backward compatibility',
            'content_type': 'article_link',
            'category': 'business',
            'tags': json.dumps(['integration', 'compatibility'])
        }
        
        response = requests.post(url, data=form_data, headers=headers, timeout=30)
        upload_test = {
            "feature": "Content upload (existing)",
            "expected": "200 OK with content ID",
            "actual": f"{response.status_code} - {response.json().get('message', 'N/A') if response.status_code == 200 else 'Failed'}",
            "passed": response.status_code == 200
        }
        self.results["integration_tests"].append(upload_test)
        print(f"{'✅' if upload_test['passed'] else '❌'} Content upload: {upload_test['actual']}")
        
        # Test 2: Creator content list access
        response = self.make_request('GET', f'api/creators/{self.creator_id}/content', token=self.creator_token)
        content_count = len(response.get('content', [])) if response.get('status_code') == 200 else 0
        list_test = {
            "feature": "Content list access",
            "expected": "200 OK with content list",
            "actual": f"{response.get('status_code', 'N/A')} - {content_count} items",
            "passed": response.get('status_code') == 200 and content_count > 0
        }
        self.results["integration_tests"].append(list_test)
        print(f"{'✅' if list_test['passed'] else '❌'} Content list: {list_test['actual']}")

    def generate_comprehensive_report(self):
        """Generate comprehensive test report"""
        print("\n" + "="*80)
        print("🎯 COMPREHENSIVE ENHANCED CONTENT MANAGEMENT SECURITY REPORT")
        print("="*80)
        
        # Calculate overall statistics
        total_tests = 0
        passed_tests = 0
        
        for category, tests in self.results.items():
            category_passed = sum(1 for test in tests if test.get('passed', False))
            category_total = len(tests)
            total_tests += category_total
            passed_tests += category_passed
            
            print(f"\n📊 {category.replace('_', ' ').title()}: {category_passed}/{category_total} passed")
            for test in tests:
                status = "✅" if test.get('passed', False) else "❌"
                test_name = test.get('endpoint', test.get('operation', test.get('scenario', test.get('feature', 'Unknown'))))
                print(f"   {status} {test_name}")
        
        # Overall results
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        print(f"\n🎯 OVERALL RESULTS: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)")
        
        # Security assessment
        auth_tests = self.results["authentication_tests"]
        authz_tests = self.results["authorization_tests"]
        
        auth_passed = sum(1 for test in auth_tests if test.get('passed', False))
        authz_passed = sum(1 for test in authz_tests if test.get('passed', False))
        
        if auth_passed == len(auth_tests) and authz_passed == len(authz_tests):
            print("🔒 SECURITY STATUS: ✅ ALL SECURITY FIXES VERIFIED!")
            print("   • All endpoints properly require creator authentication")
            print("   • All endpoints properly verify creator ownership")
            print("   • Authorization checks prevent cross-creator access")
        else:
            print("🚨 SECURITY STATUS: ❌ SECURITY ISSUES FOUND!")
            if auth_passed < len(auth_tests):
                print("   • Some endpoints may not require proper authentication")
            if authz_passed < len(authz_tests):
                print("   • Some endpoints may not verify creator ownership")
        
        # Production readiness
        if success_rate >= 90:
            print("✅ PRODUCTION READINESS: Ready for deployment!")
        elif success_rate >= 80:
            print("⚠️  PRODUCTION READINESS: Minor issues found, review recommended")
        else:
            print("❌ PRODUCTION READINESS: Major issues found, fixes required")
        
        return success_rate >= 90 and auth_passed == len(auth_tests) and authz_passed == len(authz_tests)

    def run_comprehensive_test(self):
        """Run all comprehensive security tests"""
        print("🚀 Starting Comprehensive Enhanced Content Management Security Testing")
        print("Testing all requirements from the review request")
        print("="*80)
        
        if not self.setup_test_environment():
            print("❌ Test environment setup failed. Aborting tests.")
            return False
        
        # Run all requirement tests
        self.test_requirement_1_authentication_required()
        self.test_requirement_2_authorization_checks()
        self.test_requirement_3_complete_lifecycle()
        self.test_requirement_4_error_handling()
        self.test_requirement_5_integration_verification()
        
        # Generate comprehensive report
        return self.generate_comprehensive_report()

if __name__ == "__main__":
    tester = ComprehensiveSecurityTest()
    success = tester.run_comprehensive_test()
    exit(0 if success else 1)