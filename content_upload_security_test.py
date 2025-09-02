#!/usr/bin/env python3
"""
Standard Content Upload Security Testing for OnlyMentors.ai
Testing the security fixes implemented for standard content upload functionality.

Security Fixes Tested:
1. Frontend: Added Authorization header to ContentUpload.js fetch request
2. Backend: Added `current_creator = Depends(get_current_creator)` authentication to upload endpoint  
3. Backend: Added creator authorization check to prevent cross-creator uploads

Test Focus:
1. Authenticated Upload - Test content upload with proper creator token works
2. Unauthenticated Upload - Verify upload fails without authentication (401/403 error)
3. Cross-Creator Protection - Verify creator cannot upload content for another creator
4. Content Saving - Verify uploaded content is properly saved and retrievable
5. Error Handling - Verify proper error messages for authentication failures
"""

import requests
import json
import os
import time
import uuid
from datetime import datetime
import tempfile

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://mentor-search.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class ContentUploadSecurityTester:
    def __init__(self):
        self.test_results = []
        self.creator_tokens = {}
        self.creator_ids = {}
        self.test_content_ids = []
        
    def log_test(self, test_name, success, details="", error=""):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   📝 {details}")
        if error:
            print(f"   🚨 {error}")
        print()

    def create_test_creator(self, email_suffix=""):
        """Create a test creator account for testing"""
        try:
            # Create unique test creator
            creator_email = f"testcreator{email_suffix}_{int(time.time())}@example.com"
            creator_data = {
                "email": creator_email,
                "password": "TestPassword123!",
                "full_name": f"Test Creator {email_suffix}",
                "account_name": f"testcreator{email_suffix}",
                "category": "business",
                "hourly_rate": 100.0,
                "bio": "Test creator for security testing"
            }
            
            # Sign up creator
            response = requests.post(f"{API_BASE}/creators/signup", json=creator_data)
            if response.status_code == 201:
                signup_result = response.json()
                creator_id = signup_result["creator"]["creator_id"]
                
                # Login to get token
                login_response = requests.post(f"{API_BASE}/creators/login", json={
                    "email": creator_email,
                    "password": "TestPassword123!"
                })
                
                if login_response.status_code == 200:
                    login_result = login_response.json()
                    token = login_result["token"]
                    
                    return {
                        "creator_id": creator_id,
                        "token": token,
                        "email": creator_email
                    }
            
            return None
            
        except Exception as e:
            print(f"❌ Failed to create test creator: {str(e)}")
            return None

    def create_test_file(self, content="Test content for upload", filename="test.txt"):
        """Create a temporary test file"""
        try:
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix=f"_{filename}", delete=False)
            temp_file.write(content)
            temp_file.close()
            return temp_file.name
        except Exception as e:
            print(f"❌ Failed to create test file: {str(e)}")
            return None

    def test_authenticated_content_upload(self):
        """Test 1: Authenticated Upload - Test content upload with proper creator token works"""
        try:
            # Create test creator
            creator = self.create_test_creator("auth")
            if not creator:
                self.log_test("Authenticated Content Upload", False, error="Failed to create test creator")
                return
            
            creator_id = creator["creator_id"]
            token = creator["token"]
            
            # Store for later tests
            self.creator_tokens["creator1"] = token
            self.creator_ids["creator1"] = creator_id
            
            # Create test file
            test_file_path = self.create_test_file("Test document content for authenticated upload", "auth_test.txt")
            if not test_file_path:
                self.log_test("Authenticated Content Upload", False, error="Failed to create test file")
                return
            
            # Prepare upload data
            upload_data = {
                "title": "Authenticated Test Content",
                "description": "Test content uploaded with proper authentication",
                "content_type": "document",
                "category": "business",
                "tags": '["test", "authentication", "security"]'
            }
            
            # Upload content with authentication
            with open(test_file_path, 'rb') as f:
                files = {'content_file': ('auth_test.txt', f, 'text/plain')}
                headers = {'Authorization': f'Bearer {token}'}
                
                response = requests.post(
                    f"{API_BASE}/creators/{creator_id}/content",
                    data=upload_data,
                    files=files,
                    headers=headers
                )
            
            # Clean up test file
            os.unlink(test_file_path)
            
            if response.status_code == 201:
                result = response.json()
                content_id = result.get("content_id")
                if content_id:
                    self.test_content_ids.append(content_id)
                
                self.log_test(
                    "Authenticated Content Upload", 
                    True, 
                    f"Content uploaded successfully with ID: {content_id}. Title: {result.get('title', 'N/A')}"
                )
            else:
                self.log_test(
                    "Authenticated Content Upload", 
                    False, 
                    error=f"Upload failed with status {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test("Authenticated Content Upload", False, error=f"Exception: {str(e)}")

    def test_unauthenticated_content_upload(self):
        """Test 2: Unauthenticated Upload - Verify upload fails without authentication (401/403 error)"""
        try:
            # Use existing creator ID but no token
            creator_id = self.creator_ids.get("creator1")
            if not creator_id:
                self.log_test("Unauthenticated Content Upload", False, error="No creator ID available for test")
                return
            
            # Create test file
            test_file_path = self.create_test_file("Test content without auth", "unauth_test.txt")
            if not test_file_path:
                self.log_test("Unauthenticated Content Upload", False, error="Failed to create test file")
                return
            
            # Prepare upload data
            upload_data = {
                "title": "Unauthenticated Test Content",
                "description": "This should fail without authentication",
                "content_type": "document",
                "category": "business",
                "tags": '["test", "no-auth"]'
            }
            
            # Attempt upload WITHOUT authentication header
            with open(test_file_path, 'rb') as f:
                files = {'content_file': ('unauth_test.txt', f, 'text/plain')}
                # No Authorization header
                
                response = requests.post(
                    f"{API_BASE}/creators/{creator_id}/content",
                    data=upload_data,
                    files=files
                )
            
            # Clean up test file
            os.unlink(test_file_path)
            
            # Should fail with 401 or 403
            if response.status_code in [401, 403]:
                self.log_test(
                    "Unauthenticated Content Upload", 
                    True, 
                    f"Correctly rejected unauthenticated upload with status {response.status_code}"
                )
            else:
                self.log_test(
                    "Unauthenticated Content Upload", 
                    False, 
                    error=f"Expected 401/403 but got {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test("Unauthenticated Content Upload", False, error=f"Exception: {str(e)}")

    def test_invalid_token_upload(self):
        """Test 3: Invalid Token Upload - Verify upload fails with invalid token"""
        try:
            creator_id = self.creator_ids.get("creator1")
            if not creator_id:
                self.log_test("Invalid Token Content Upload", False, error="No creator ID available for test")
                return
            
            # Create test file
            test_file_path = self.create_test_file("Test content with invalid token", "invalid_test.txt")
            if not test_file_path:
                self.log_test("Invalid Token Content Upload", False, error="Failed to create test file")
                return
            
            # Prepare upload data
            upload_data = {
                "title": "Invalid Token Test Content",
                "description": "This should fail with invalid token",
                "content_type": "document",
                "category": "business",
                "tags": '["test", "invalid-token"]'
            }
            
            # Attempt upload with INVALID token
            with open(test_file_path, 'rb') as f:
                files = {'content_file': ('invalid_test.txt', f, 'text/plain')}
                headers = {'Authorization': 'Bearer invalid_token_12345'}
                
                response = requests.post(
                    f"{API_BASE}/creators/{creator_id}/content",
                    data=upload_data,
                    files=files,
                    headers=headers
                )
            
            # Clean up test file
            os.unlink(test_file_path)
            
            # Should fail with 401
            if response.status_code == 401:
                self.log_test(
                    "Invalid Token Content Upload", 
                    True, 
                    f"Correctly rejected invalid token upload with status {response.status_code}"
                )
            else:
                self.log_test(
                    "Invalid Token Content Upload", 
                    False, 
                    error=f"Expected 401 but got {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test("Invalid Token Content Upload", False, error=f"Exception: {str(e)}")

    def test_cross_creator_upload_protection(self):
        """Test 4: Cross-Creator Protection - Verify creator cannot upload content for another creator"""
        try:
            # Create second test creator
            creator2 = self.create_test_creator("cross")
            if not creator2:
                self.log_test("Cross-Creator Upload Protection", False, error="Failed to create second test creator")
                return
            
            creator2_id = creator2["creator_id"]
            creator1_token = self.creator_tokens.get("creator1")
            
            if not creator1_token:
                self.log_test("Cross-Creator Upload Protection", False, error="No creator1 token available")
                return
            
            # Store second creator info
            self.creator_tokens["creator2"] = creator2["token"]
            self.creator_ids["creator2"] = creator2_id
            
            # Create test file
            test_file_path = self.create_test_file("Cross-creator test content", "cross_test.txt")
            if not test_file_path:
                self.log_test("Cross-Creator Upload Protection", False, error="Failed to create test file")
                return
            
            # Prepare upload data
            upload_data = {
                "title": "Cross-Creator Test Content",
                "description": "Attempting to upload for another creator",
                "content_type": "document",
                "category": "business",
                "tags": '["test", "cross-creator"]'
            }
            
            # Attempt to upload to creator2's account using creator1's token
            with open(test_file_path, 'rb') as f:
                files = {'content_file': ('cross_test.txt', f, 'text/plain')}
                headers = {'Authorization': f'Bearer {creator1_token}'}
                
                response = requests.post(
                    f"{API_BASE}/creators/{creator2_id}/content",  # creator2's ID
                    data=upload_data,
                    files=files,
                    headers=headers  # creator1's token
                )
            
            # Clean up test file
            os.unlink(test_file_path)
            
            # Should fail with 403
            if response.status_code == 403:
                self.log_test(
                    "Cross-Creator Upload Protection", 
                    True, 
                    f"Correctly prevented cross-creator upload with status {response.status_code}"
                )
            else:
                self.log_test(
                    "Cross-Creator Upload Protection", 
                    False, 
                    error=f"Expected 403 but got {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test("Cross-Creator Upload Protection", False, error=f"Exception: {str(e)}")

    def test_content_retrieval(self):
        """Test 5: Content Saving - Verify uploaded content is properly saved and retrievable"""
        try:
            creator_id = self.creator_ids.get("creator1")
            token = self.creator_tokens.get("creator1")
            
            if not creator_id or not token:
                self.log_test("Content Retrieval", False, error="No creator credentials available")
                return
            
            # Get creator's content list
            headers = {'Authorization': f'Bearer {token}'}
            response = requests.get(f"{API_BASE}/creators/{creator_id}/content", headers=headers)
            
            if response.status_code == 200:
                content_list = response.json()
                content_items = content_list.get("content", [])
                
                if len(content_items) > 0:
                    # Check if our test content is in the list
                    test_content = None
                    for item in content_items:
                        if item.get("title") == "Authenticated Test Content":
                            test_content = item
                            break
                    
                    if test_content:
                        content_id = test_content.get("content_id")
                        
                        # Try to retrieve individual content item
                        detail_response = requests.get(
                            f"{API_BASE}/creators/{creator_id}/content/{content_id}", 
                            headers=headers
                        )
                        
                        if detail_response.status_code == 200:
                            content_detail = detail_response.json()
                            self.log_test(
                                "Content Retrieval", 
                                True, 
                                f"Successfully retrieved content: {content_detail.get('title')} (ID: {content_id})"
                            )
                        else:
                            self.log_test(
                                "Content Retrieval", 
                                False, 
                                error=f"Failed to retrieve content detail: {detail_response.status_code}"
                            )
                    else:
                        self.log_test(
                            "Content Retrieval", 
                            False, 
                            error="Test content not found in creator's content list"
                        )
                else:
                    self.log_test(
                        "Content Retrieval", 
                        False, 
                        error="No content found for creator"
                    )
            else:
                self.log_test(
                    "Content Retrieval", 
                    False, 
                    error=f"Failed to get content list: {response.status_code}"
                )
                
        except Exception as e:
            self.log_test("Content Retrieval", False, error=f"Exception: {str(e)}")

    def test_file_validation(self):
        """Test 6: File Validation - Test file type and size validation"""
        try:
            creator_id = self.creator_ids.get("creator1")
            token = self.creator_tokens.get("creator1")
            
            if not creator_id or not token:
                self.log_test("File Validation", False, error="No creator credentials available")
                return
            
            # Test with invalid file type (should fail)
            test_file_path = self.create_test_file("Invalid file content", "test.exe")
            if not test_file_path:
                self.log_test("File Validation", False, error="Failed to create test file")
                return
            
            upload_data = {
                "title": "Invalid File Test",
                "description": "Testing file validation",
                "content_type": "document",
                "category": "business",
                "tags": '["test", "validation"]'
            }
            
            with open(test_file_path, 'rb') as f:
                files = {'content_file': ('test.exe', f, 'application/octet-stream')}
                headers = {'Authorization': f'Bearer {token}'}
                
                response = requests.post(
                    f"{API_BASE}/creators/{creator_id}/content",
                    data=upload_data,
                    files=files,
                    headers=headers
                )
            
            # Clean up test file
            os.unlink(test_file_path)
            
            # Should fail with 400 (validation error)
            if response.status_code == 400:
                self.log_test(
                    "File Validation", 
                    True, 
                    f"Correctly rejected invalid file type with status {response.status_code}"
                )
            else:
                self.log_test(
                    "File Validation", 
                    False, 
                    error=f"Expected 400 for invalid file but got {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test("File Validation", False, error=f"Exception: {str(e)}")

    def run_all_tests(self):
        """Run all content upload security tests"""
        print("🔒 STANDARD CONTENT UPLOAD SECURITY TESTING")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Testing Time: {datetime.now().isoformat()}")
        print()
        
        # Run tests in order
        self.test_authenticated_content_upload()
        self.test_unauthenticated_content_upload()
        self.test_invalid_token_upload()
        self.test_cross_creator_upload_protection()
        self.test_content_retrieval()
        self.test_file_validation()
        
        # Summary
        print("=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        print()
        
        # Detailed results
        print("📋 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}")
            if result["details"]:
                print(f"   📝 {result['details']}")
            if result["error"]:
                print(f"   🚨 {result['error']}")
        
        print()
        print("🔒 SECURITY ASSESSMENT:")
        
        # Check critical security tests
        auth_test = next((r for r in self.test_results if "Authenticated Content Upload" in r["test"]), None)
        unauth_test = next((r for r in self.test_results if "Unauthenticated Content Upload" in r["test"]), None)
        cross_creator_test = next((r for r in self.test_results if "Cross-Creator Upload Protection" in r["test"]), None)
        
        if auth_test and auth_test["success"]:
            print("✅ Authenticated uploads working correctly")
        else:
            print("❌ CRITICAL: Authenticated uploads not working")
            
        if unauth_test and unauth_test["success"]:
            print("✅ Unauthenticated uploads properly blocked")
        else:
            print("❌ CRITICAL SECURITY ISSUE: Unauthenticated uploads not blocked!")
            
        if cross_creator_test and cross_creator_test["success"]:
            print("✅ Cross-creator upload protection working")
        else:
            print("❌ CRITICAL SECURITY ISSUE: Cross-creator uploads not blocked!")
        
        print()
        
        if success_rate >= 80:
            print("🎉 CONTENT UPLOAD SECURITY: EXCELLENT")
        elif success_rate >= 60:
            print("⚠️  CONTENT UPLOAD SECURITY: GOOD (some issues)")
        else:
            print("🚨 CONTENT UPLOAD SECURITY: NEEDS ATTENTION")
        
        return self.test_results

if __name__ == "__main__":
    tester = ContentUploadSecurityTester()
    results = tester.run_all_tests()