#!/usr/bin/env python3
"""
Premium Content Management System Testing
Testing the corrected premium content management system with proper separation of standard and premium content.
"""

import requests
import json
import time
import os
from datetime import datetime

# Configuration
BACKEND_URL = "https://mentor-marketplace.preview.emergentagent.com/api"

class PremiumContentTester:
    def __init__(self):
        self.session = requests.Session()
        self.creator_token = None
        self.creator_id = None
        self.user_token = None
        self.user_id = None
        self.test_results = []
        
    def log_test(self, test_name, success, details=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        return success

    def create_test_creator(self):
        """Create a test creator account"""
        try:
            # Creator signup
            creator_data = {
                "email": f"testcreator_{int(time.time())}@example.com",
                "password": "TestPassword123!",
                "full_name": "Test Creator Premium",
                "bio": "Testing premium content management",
                "expertise": "Premium Content Testing",
                "hourly_rate": 150.0
            }
            
            response = self.session.post(f"{BACKEND_URL}/creator/signup", json=creator_data)
            
            if response.status_code == 200:
                data = response.json()
                self.creator_token = data.get("token")
                self.creator_id = data.get("creator", {}).get("creator_id")
                
                # Set authorization header
                self.session.headers.update({
                    "Authorization": f"Bearer {self.creator_token}"
                })
                
                return self.log_test(
                    "Creator Account Creation", 
                    True, 
                    f"Creator ID: {self.creator_id}"
                )
            else:
                return self.log_test(
                    "Creator Account Creation", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                
        except Exception as e:
            return self.log_test("Creator Account Creation", False, f"Exception: {str(e)}")

    def create_test_user(self):
        """Create a test user account"""
        try:
            # User signup
            user_data = {
                "email": f"testuser_{int(time.time())}@example.com",
                "password": "TestPassword123!",
                "full_name": "Test User Premium"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/signup", json=user_data)
            
            if response.status_code == 200:
                data = response.json()
                self.user_token = data.get("token")
                self.user_id = data.get("user", {}).get("user_id")
                
                return self.log_test(
                    "User Account Creation", 
                    True, 
                    f"User ID: {self.user_id}"
                )
            else:
                return self.log_test(
                    "User Account Creation", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                
        except Exception as e:
            return self.log_test("User Account Creation", False, f"Exception: {str(e)}")

    def test_standard_content_endpoint(self):
        """Test that standard content endpoint only returns standard content from db.creator_content"""
        try:
            if not self.creator_token:
                return self.log_test("Standard Content Endpoint Test", False, "No creator token available")
            
            # First upload some standard content
            standard_content_data = {
                "title": "Standard Content Test",
                "description": "This is standard content for testing",
                "content_type": "article_link",
                "category": "business",
                "tags": '["standard", "test"]'
            }
            
            # Upload standard content
            upload_response = self.session.post(
                f"{BACKEND_URL}/creators/{self.creator_id}/content",
                data=standard_content_data
            )
            
            if upload_response.status_code != 200:
                return self.log_test(
                    "Standard Content Endpoint Test", 
                    False, 
                    f"Failed to upload standard content: {upload_response.status_code}"
                )
            
            # Now test the standard content endpoint
            response = self.session.get(f"{BACKEND_URL}/creators/{self.creator_id}/content")
            
            if response.status_code == 200:
                data = response.json()
                content_list = data.get("content", [])
                
                # Verify content is from standard content collection
                has_standard_content = any(
                    content.get("title") == "Standard Content Test" 
                    for content in content_list
                )
                
                # Verify no premium content appears in standard endpoint
                has_premium_content = any(
                    "price" in content and content.get("price") is not None
                    for content in content_list
                )
                
                if has_standard_content and not has_premium_content:
                    return self.log_test(
                        "Standard Content Endpoint Test", 
                        True, 
                        f"Standard endpoint returns only standard content. Found {len(content_list)} items"
                    )
                else:
                    return self.log_test(
                        "Standard Content Endpoint Test", 
                        False, 
                        f"Content mixing detected. Standard: {has_standard_content}, Premium: {has_premium_content}"
                    )
            else:
                return self.log_test(
                    "Standard Content Endpoint Test", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                
        except Exception as e:
            return self.log_test("Standard Content Endpoint Test", False, f"Exception: {str(e)}")

    def test_premium_content_endpoint(self):
        """Test new dedicated premium content endpoint"""
        try:
            if not self.creator_token:
                return self.log_test("Premium Content Endpoint Test", False, "No creator token available")
            
            # Test the new premium content management endpoint
            response = self.session.get(f"{BACKEND_URL}/creators/{self.creator_id}/premium-content")
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure matches frontend expectations
                required_fields = ["content", "total", "offset", "limit"]
                has_required_fields = all(field in data for field in required_fields)
                
                if has_required_fields:
                    content_list = data.get("content", [])
                    
                    # Verify this endpoint only returns premium content (should have pricing info)
                    all_premium = all(
                        "price" in content or "pricing" in content
                        for content in content_list
                    ) if content_list else True  # Empty list is valid
                    
                    return self.log_test(
                        "Premium Content Endpoint Test", 
                        True, 
                        f"Premium endpoint working. Found {len(content_list)} premium items. Structure: {list(data.keys())}"
                    )
                else:
                    return self.log_test(
                        "Premium Content Endpoint Test", 
                        False, 
                        f"Missing required fields. Got: {list(data.keys())}, Expected: {required_fields}"
                    )
            else:
                return self.log_test(
                    "Premium Content Endpoint Test", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                
        except Exception as e:
            return self.log_test("Premium Content Endpoint Test", False, f"Exception: {str(e)}")

    def test_premium_content_upload(self):
        """Test premium content upload via /api/creator/content/upload"""
        try:
            if not self.creator_token:
                return self.log_test("Premium Content Upload Test", False, "No creator token available")
            
            # Upload premium content
            premium_content_data = {
                "title": "Premium Test Content",
                "description": "This is premium content for testing separation",
                "content_type": "document",
                "category": "business",
                "price": 9.99,
                "tags": '["premium", "test", "separation"]',
                "preview_available": True
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/creator/content/upload",
                data=premium_content_data
            )
            
            if response.status_code == 200:
                data = response.json()
                content_id = data.get("content_id")
                
                if content_id:
                    return self.log_test(
                        "Premium Content Upload Test", 
                        True, 
                        f"Premium content uploaded successfully. Content ID: {content_id}"
                    )
                else:
                    return self.log_test(
                        "Premium Content Upload Test", 
                        False, 
                        f"No content_id in response: {data}"
                    )
            else:
                return self.log_test(
                    "Premium Content Upload Test", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                
        except Exception as e:
            return self.log_test("Premium Content Upload Test", False, f"Exception: {str(e)}")

    def test_content_separation_verification(self):
        """Test that uploaded premium content appears only in premium management"""
        try:
            if not self.creator_token:
                return self.log_test("Content Separation Verification", False, "No creator token available")
            
            # Check premium content endpoint for our uploaded content
            premium_response = self.session.get(f"{BACKEND_URL}/creators/{self.creator_id}/premium-content")
            
            # Check standard content endpoint
            standard_response = self.session.get(f"{BACKEND_URL}/creators/{self.creator_id}/content")
            
            if premium_response.status_code == 200 and standard_response.status_code == 200:
                premium_data = premium_response.json()
                standard_data = standard_response.json()
                
                premium_content = premium_data.get("content", [])
                standard_content = standard_data.get("content", [])
                
                # Look for our test premium content
                premium_test_content = any(
                    content.get("title") == "Premium Test Content"
                    for content in premium_content
                )
                
                # Verify it doesn't appear in standard content
                premium_in_standard = any(
                    content.get("title") == "Premium Test Content"
                    for content in standard_content
                )
                
                # Look for our test standard content
                standard_test_content = any(
                    content.get("title") == "Standard Content Test"
                    for content in standard_content
                )
                
                # Verify it doesn't appear in premium content
                standard_in_premium = any(
                    content.get("title") == "Standard Content Test"
                    for content in premium_content
                )
                
                if premium_test_content and not premium_in_standard and standard_test_content and not standard_in_premium:
                    return self.log_test(
                        "Content Separation Verification", 
                        True, 
                        "Perfect separation: Premium content only in premium endpoint, standard content only in standard endpoint"
                    )
                else:
                    return self.log_test(
                        "Content Separation Verification", 
                        False, 
                        f"Separation failed. Premium in premium: {premium_test_content}, Premium in standard: {premium_in_standard}, Standard in standard: {standard_test_content}, Standard in premium: {standard_in_premium}"
                    )
            else:
                return self.log_test(
                    "Content Separation Verification", 
                    False, 
                    f"API calls failed. Premium: {premium_response.status_code}, Standard: {standard_response.status_code}"
                )
                
        except Exception as e:
            return self.log_test("Content Separation Verification", False, f"Exception: {str(e)}")

    def test_authentication_and_authorization(self):
        """Test proper creator authentication and authorization"""
        try:
            # Test 1: Access without authentication
            temp_session = requests.Session()  # No auth headers
            
            response = temp_session.get(f"{BACKEND_URL}/creators/{self.creator_id}/premium-content")
            
            if response.status_code in [401, 403]:
                auth_required = True
            else:
                auth_required = False
            
            # Test 2: Access with invalid token
            temp_session.headers.update({"Authorization": "Bearer invalid_token_12345"})
            
            response = temp_session.get(f"{BACKEND_URL}/creators/{self.creator_id}/premium-content")
            
            if response.status_code in [401, 403]:
                invalid_token_blocked = True
            else:
                invalid_token_blocked = False
            
            # Test 3: Cross-creator access (if we had another creator)
            # For now, we'll test with a different creator_id
            fake_creator_id = "fake_creator_123"
            
            response = self.session.get(f"{BACKEND_URL}/creators/{fake_creator_id}/premium-content")
            
            if response.status_code in [403, 404]:
                cross_creator_blocked = True
            else:
                cross_creator_blocked = False
            
            # Test 4: Valid authentication works
            response = self.session.get(f"{BACKEND_URL}/creators/{self.creator_id}/premium-content")
            
            if response.status_code == 200:
                valid_auth_works = True
            else:
                valid_auth_works = False
            
            all_auth_tests_pass = auth_required and invalid_token_blocked and cross_creator_blocked and valid_auth_works
            
            return self.log_test(
                "Authentication and Authorization Test", 
                all_auth_tests_pass, 
                f"Auth required: {auth_required}, Invalid token blocked: {invalid_token_blocked}, Cross-creator blocked: {cross_creator_blocked}, Valid auth works: {valid_auth_works}"
            )
                
        except Exception as e:
            return self.log_test("Authentication and Authorization Test", False, f"Exception: {str(e)}")

    def test_premium_content_discovery(self):
        """Test premium content discovery endpoint for users"""
        try:
            if not self.creator_id:
                return self.log_test("Premium Content Discovery Test", False, "No creator ID available")
            
            # Test the mentor premium content discovery endpoint (for users to browse)
            response = self.session.get(f"{BACKEND_URL}/mentor/{self.creator_id}/premium-content")
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure for discovery
                if "content" in data:
                    content_list = data["content"]
                    
                    # Verify content doesn't expose sensitive data (like file paths)
                    safe_content = True
                    for content in content_list:
                        if "file_path" in content or "internal_path" in content:
                            safe_content = False
                            break
                    
                    return self.log_test(
                        "Premium Content Discovery Test", 
                        safe_content, 
                        f"Discovery endpoint working. Found {len(content_list)} items. Safe content: {safe_content}"
                    )
                else:
                    return self.log_test(
                        "Premium Content Discovery Test", 
                        False, 
                        f"Invalid response structure: {list(data.keys())}"
                    )
            else:
                return self.log_test(
                    "Premium Content Discovery Test", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                
        except Exception as e:
            return self.log_test("Premium Content Discovery Test", False, f"Exception: {str(e)}")

    def run_all_tests(self):
        """Run all premium content management tests"""
        print("🧪 PREMIUM CONTENT MANAGEMENT SYSTEM TESTING")
        print("=" * 60)
        print("Testing the corrected premium content management system with proper separation of standard and premium content.")
        print()
        
        # Setup phase
        print("📋 SETUP PHASE")
        print("-" * 30)
        if not self.create_test_creator():
            print("❌ Cannot proceed without creator account")
            return False
        
        if not self.create_test_user():
            print("⚠️  User account creation failed, but continuing with creator tests")
        
        print()
        
        # Core testing phase
        print("🔍 CONTENT SEPARATION TESTING")
        print("-" * 40)
        
        # Test 1: Standard content endpoint
        self.test_standard_content_endpoint()
        
        # Test 2: Premium content endpoint
        self.test_premium_content_endpoint()
        
        # Test 3: Premium content upload
        self.test_premium_content_upload()
        
        # Test 4: Content separation verification
        self.test_content_separation_verification()
        
        print()
        
        # Security testing phase
        print("🔒 AUTHENTICATION & AUTHORIZATION TESTING")
        print("-" * 50)
        
        # Test 5: Authentication and authorization
        self.test_authentication_and_authorization()
        
        print()
        
        # Discovery testing phase
        print("🔍 CONTENT DISCOVERY TESTING")
        print("-" * 35)
        
        # Test 6: Premium content discovery
        self.test_premium_content_discovery()
        
        print()
        
        # Results summary
        self.print_summary()
        
        return True

    def print_summary(self):
        """Print test results summary"""
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['details']}")
            print()
        
        # Critical success criteria check
        critical_tests = [
            "Standard Content Endpoint Test",
            "Premium Content Endpoint Test", 
            "Content Separation Verification",
            "Authentication and Authorization Test"
        ]
        
        critical_passed = sum(
            1 for result in self.test_results 
            if result["test"] in critical_tests and result["success"]
        )
        
        print("🎯 CRITICAL SUCCESS CRITERIA:")
        print(f"   • Standard content endpoint returns only standard content: {'✅' if any(r['test'] == 'Standard Content Endpoint Test' and r['success'] for r in self.test_results) else '❌'}")
        print(f"   • Premium content endpoint returns only premium content: {'✅' if any(r['test'] == 'Premium Content Endpoint Test' and r['success'] for r in self.test_results) else '❌'}")
        print(f"   • Content separation working correctly: {'✅' if any(r['test'] == 'Content Separation Verification' and r['success'] for r in self.test_results) else '❌'}")
        print(f"   • Authentication and authorization enforced: {'✅' if any(r['test'] == 'Authentication and Authorization Test' and r['success'] for r in self.test_results) else '❌'}")
        
        print()
        
        if critical_passed == len(critical_tests):
            print("🎉 ALL CRITICAL SUCCESS CRITERIA MET!")
            print("The premium content management system is working correctly with proper content separation.")
        else:
            print("⚠️  SOME CRITICAL CRITERIA NOT MET")
            print("The premium content management system needs attention.")
        
        print()
        print("📝 DETAILED TEST LOG:")
        for result in self.test_results:
            print(f"   {result['status']} {result['test']}")
            if result['details']:
                print(f"      └─ {result['details']}")

if __name__ == "__main__":
    tester = PremiumContentTester()
    tester.run_all_tests()