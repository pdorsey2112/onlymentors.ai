#!/usr/bin/env python3
"""
OnlyMentors.ai Premium Content Upload with File Testing
Testing the premium content upload functionality with file upload capability
"""

import asyncio
import aiohttp
import json
import uuid
import os
import tempfile
from datetime import datetime
from typing import Dict, Any

# Configuration
BACKEND_URL = "https://multi-tenant-ai.preview.emergentagent.com"

class PremiumContentFileUploadTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.creator_token = None
        self.test_content_id = None
        
    async def setup_session(self):
        """Setup HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
    
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} | {test_name}")
        if details:
            print(f"     Details: {details}")
        if not success and response_data:
            print(f"     Response: {response_data}")
        print()
    
    async def create_test_creator(self) -> bool:
        """Create a test creator account for testing"""
        try:
            # Create creator signup data
            creator_data = {
                "email": f"testcreator_{uuid.uuid4().hex[:8]}@example.com",
                "password": "TestPassword123!",
                "full_name": "Premium Content Creator",
                "account_name": f"PremiumCreator_{uuid.uuid4().hex[:8]}",
                "description": "Test creator for premium content file upload testing",
                "monthly_price": 199.0,
                "category": "business",
                "expertise_areas": ["content creation", "digital marketing"]
            }
            
            async with self.session.post(f"{BACKEND_URL}/api/creators/signup", json=creator_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.creator_token = data.get("token")
                    self.log_test("Create Test Creator", True, f"Creator created successfully")
                    return True
                else:
                    error_text = await response.text()
                    self.log_test("Create Test Creator", False, f"Status: {response.status}", error_text)
                    return False
                    
        except Exception as e:
            self.log_test("Create Test Creator", False, f"Exception: {str(e)}")
            return False
    
    def create_test_file(self, file_type: str, size_mb: float = 1.0) -> tuple:
        """Create a test file for upload testing"""
        content_map = {
            "pdf": (b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000074 00000 n \n0000000120 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n179\n%%EOF", "application/pdf"),
            "txt": (b"This is a test document for premium content upload testing.\nIt contains sample text content for validation.", "text/plain"),
            "jpg": (b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.' \",#\x1c\x1c(7),01444\x1f'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9", "image/jpeg"),
            "mp4": (b"\x00\x00\x00\x20ftypmp41\x00\x00\x00\x00mp41isom\x00\x00\x00\x08free", "video/mp4"),
            "mp3": (b"ID3\x03\x00\x00\x00\x00\x00\x00\x00", "audio/mpeg")
        }
        
        if file_type not in content_map:
            file_type = "txt"
        
        base_content, mime_type = content_map[file_type]
        
        # Pad content to reach desired size
        target_size = int(size_mb * 1024 * 1024)
        if len(base_content) < target_size:
            padding = b"0" * (target_size - len(base_content))
            content = base_content + padding
        else:
            content = base_content
        
        filename = f"test_content_{uuid.uuid4().hex[:8]}.{file_type}"
        return content, filename, mime_type
    
    async def test_premium_content_upload_with_file(self):
        """Test POST /api/api/creator/content/upload with FormData and file"""
        if not self.creator_token:
            self.log_test("Premium Content Upload with File", False, "No creator token available")
            return
        
        headers = {"Authorization": f"Bearer {self.creator_token}"}
        
        # Test 1: Valid PDF document upload
        try:
            file_content, filename, mime_type = self.create_test_file("pdf", 0.5)  # 0.5MB PDF
            
            # Create FormData
            data = aiohttp.FormData()
            data.add_field('title', 'Premium Business Strategy Guide')
            data.add_field('description', 'Comprehensive guide to modern business strategy with actionable insights')
            data.add_field('content_type', 'document')
            data.add_field('category', 'business')
            data.add_field('price', '24.99')
            data.add_field('tags', '["business", "strategy", "guide", "premium"]')
            data.add_field('preview_available', 'true')
            data.add_field('content_file', file_content, filename=filename, content_type=mime_type)
            
            async with self.session.post(f"{BACKEND_URL}/api/api/creator/content/upload", 
                                       data=data, headers=headers) as response:
                if response.status == 200:
                    response_data = await response.json()
                    self.test_content_id = response_data.get("content_id")
                    pricing = response_data.get("pricing_breakdown", {})
                    
                    # Verify pricing calculation (20% commission, min $2.99)
                    expected_platform_fee = max(24.99 * 0.20, 2.99)  # Should be 4.998
                    expected_creator_earnings = 24.99 - expected_platform_fee
                    
                    pricing_correct = (
                        abs(pricing.get("platform_fee", 0) - expected_platform_fee) < 0.01 and
                        abs(pricing.get("creator_earnings", 0) - expected_creator_earnings) < 0.01
                    )
                    
                    if pricing_correct and response_data.get("success"):
                        self.log_test("Premium Content Upload with File - PDF Document", True, 
                                    f"PDF uploaded successfully with correct pricing: Platform fee ${pricing.get('platform_fee'):.2f}, Creator earnings ${pricing.get('creator_earnings'):.2f}")
                    else:
                        self.log_test("Premium Content Upload with File - PDF Document", False, 
                                    f"Upload succeeded but pricing incorrect: {pricing}")
                else:
                    error_text = await response.text()
                    self.log_test("Premium Content Upload with File - PDF Document", False, 
                                f"Status: {response.status}", error_text)
                    
        except Exception as e:
            self.log_test("Premium Content Upload with File - PDF Document", False, f"Exception: {str(e)}")
        
        # Test 2: Valid image upload
        try:
            file_content, filename, mime_type = self.create_test_file("jpg", 0.1)  # 0.1MB image
            
            data = aiohttp.FormData()
            data.add_field('title', 'Premium Design Template')
            data.add_field('description', 'High-quality design template for professional use')
            data.add_field('content_type', 'image')
            data.add_field('category', 'design')
            data.add_field('price', '9.99')
            data.add_field('tags', '["design", "template", "graphics"]')
            data.add_field('preview_available', 'false')
            data.add_field('content_file', file_content, filename=filename, content_type=mime_type)
            
            async with self.session.post(f"{BACKEND_URL}/api/creator/content/upload", 
                                       data=data, headers=headers) as response:
                if response.status == 200:
                    response_data = await response.json()
                    pricing = response_data.get("pricing_breakdown", {})
                    
                    # For $9.99, should use minimum $2.99 fee (not 20% = $1.998)
                    if pricing.get("platform_fee") == 2.99:
                        self.log_test("Premium Content Upload with File - Image", True, 
                                    f"Image uploaded successfully with minimum platform fee applied")
                    else:
                        self.log_test("Premium Content Upload with File - Image", False, 
                                    f"Expected minimum $2.99 fee, got ${pricing.get('platform_fee')}")
                else:
                    error_text = await response.text()
                    self.log_test("Premium Content Upload with File - Image", False, 
                                f"Status: {response.status}", error_text)
                    
        except Exception as e:
            self.log_test("Premium Content Upload with File - Image", False, f"Exception: {str(e)}")
        
        # Test 3: Upload without file (should still work)
        try:
            data = aiohttp.FormData()
            data.add_field('title', 'Premium Text Content')
            data.add_field('description', 'Text-based premium content without file attachment')
            data.add_field('content_type', 'document')
            data.add_field('category', 'education')
            data.add_field('price', '15.00')
            data.add_field('tags', '["education", "text", "content"]')
            data.add_field('preview_available', 'true')
            
            async with self.session.post(f"{BACKEND_URL}/api/creator/content/upload", 
                                       data=data, headers=headers) as response:
                if response.status == 200:
                    response_data = await response.json()
                    if response_data.get("success"):
                        self.log_test("Premium Content Upload without File", True, 
                                    "Content created successfully without file attachment")
                    else:
                        self.log_test("Premium Content Upload without File", False, 
                                    "Upload failed despite valid data")
                else:
                    error_text = await response.text()
                    self.log_test("Premium Content Upload without File", False, 
                                f"Status: {response.status}", error_text)
                    
        except Exception as e:
            self.log_test("Premium Content Upload without File", False, f"Exception: {str(e)}")
    
    async def test_file_storage_and_retrieval(self):
        """Test file handling and storage"""
        if not self.creator_token:
            self.log_test("File Storage Test", False, "No creator token available")
            return
        
        headers = {"Authorization": f"Bearer {self.creator_token}"}
        
        # Test file storage with unique filename generation
        try:
            file_content, filename, mime_type = self.create_test_file("pdf", 0.2)
            
            data = aiohttp.FormData()
            data.add_field('title', 'File Storage Test Content')
            data.add_field('description', 'Testing file storage and unique filename generation')
            data.add_field('content_type', 'document')
            data.add_field('category', 'test')
            data.add_field('price', '5.99')
            data.add_field('tags', '["test", "storage"]')
            data.add_field('preview_available', 'false')
            data.add_field('content_file', file_content, filename=filename, content_type=mime_type)
            
            async with self.session.post(f"{BACKEND_URL}/api/creator/content/upload", 
                                       data=data, headers=headers) as response:
                if response.status == 200:
                    response_data = await response.json()
                    content_id = response_data.get("content_id")
                    
                    if content_id:
                        # Check if file was stored (we can't directly access filesystem, but we can verify the response)
                        self.log_test("File Storage - Unique Filename Generation", True, 
                                    f"File uploaded and content created with ID: {content_id}")
                    else:
                        self.log_test("File Storage - Unique Filename Generation", False, 
                                    "No content ID returned")
                else:
                    error_text = await response.text()
                    self.log_test("File Storage - Unique Filename Generation", False, 
                                f"Status: {response.status}", error_text)
                    
        except Exception as e:
            self.log_test("File Storage - Unique Filename Generation", False, f"Exception: {str(e)}")
        
        # Test directory creation (implicit test - if upload succeeds, directory was created)
        try:
            # Upload multiple files to test directory handling
            for i in range(2):
                file_content, filename, mime_type = self.create_test_file("txt", 0.01)
                
                data = aiohttp.FormData()
                data.add_field('title', f'Directory Test Content {i+1}')
                data.add_field('description', f'Testing directory creation - file {i+1}')
                data.add_field('content_type', 'document')
                data.add_field('category', 'test')
                data.add_field('price', '1.99')
                data.add_field('tags', '["test", "directory"]')
                data.add_field('preview_available', 'false')
                data.add_field('content_file', file_content, filename=filename, content_type=mime_type)
                
                async with self.session.post(f"{BACKEND_URL}/api/creator/content/upload", 
                                           data=data, headers=headers) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        self.log_test("File Storage - Directory Creation", False, 
                                    f"Upload {i+1} failed: Status {response.status}")
                        return
            
            self.log_test("File Storage - Directory Creation", True, 
                        "Multiple files uploaded successfully, directory handling working")
                        
        except Exception as e:
            self.log_test("File Storage - Directory Creation", False, f"Exception: {str(e)}")
    
    async def test_form_data_validation(self):
        """Test form parameter validation"""
        if not self.creator_token:
            self.log_test("Form Data Validation", False, "No creator token available")
            return
        
        headers = {"Authorization": f"Bearer {self.creator_token}"}
        
        # Test 1: Missing required fields
        try:
            data = aiohttp.FormData()
            data.add_field('title', 'Test Content')
            # Missing description, content_type, price
            
            async with self.session.post(f"{BACKEND_URL}/api/creator/content/upload", 
                                       data=data, headers=headers) as response:
                if response.status == 422:  # Validation error
                    self.log_test("Form Data Validation - Missing Required Fields", True, 
                                "Correctly rejected request with missing required fields")
                else:
                    self.log_test("Form Data Validation - Missing Required Fields", False, 
                                f"Should return 422 for missing fields, got: {response.status}")
                    
        except Exception as e:
            self.log_test("Form Data Validation - Missing Required Fields", False, f"Exception: {str(e)}")
        
        # Test 2: Invalid price range (too low)
        try:
            data = aiohttp.FormData()
            data.add_field('title', 'Invalid Price Test')
            data.add_field('description', 'Testing price validation')
            data.add_field('content_type', 'document')
            data.add_field('category', 'test')
            data.add_field('price', '0.005')  # Below minimum $0.01
            data.add_field('tags', '[]')
            data.add_field('preview_available', 'false')
            
            async with self.session.post(f"{BACKEND_URL}/api/creator/content/upload", 
                                       data=data, headers=headers) as response:
                if response.status == 400:
                    self.log_test("Form Data Validation - Price Too Low", True, 
                                "Correctly rejected price below $0.01")
                else:
                    self.log_test("Form Data Validation - Price Too Low", False, 
                                f"Should reject low price, got status: {response.status}")
                    
        except Exception as e:
            self.log_test("Form Data Validation - Price Too Low", False, f"Exception: {str(e)}")
        
        # Test 3: Invalid price range (too high)
        try:
            data = aiohttp.FormData()
            data.add_field('title', 'Invalid High Price Test')
            data.add_field('description', 'Testing high price validation')
            data.add_field('content_type', 'document')
            data.add_field('category', 'test')
            data.add_field('price', '75.00')  # Above maximum $50.00
            data.add_field('tags', '[]')
            data.add_field('preview_available', 'false')
            
            async with self.session.post(f"{BACKEND_URL}/api/creator/content/upload", 
                                       data=data, headers=headers) as response:
                if response.status == 400:
                    self.log_test("Form Data Validation - Price Too High", True, 
                                "Correctly rejected price above $50.00")
                else:
                    self.log_test("Form Data Validation - Price Too High", False, 
                                f"Should reject high price, got status: {response.status}")
                    
        except Exception as e:
            self.log_test("Form Data Validation - Price Too High", False, f"Exception: {str(e)}")
        
        # Test 4: Valid price range
        try:
            data = aiohttp.FormData()
            data.add_field('title', 'Valid Price Test')
            data.add_field('description', 'Testing valid price range')
            data.add_field('content_type', 'document')
            data.add_field('category', 'test')
            data.add_field('price', '25.50')  # Valid price
            data.add_field('tags', '["test", "validation"]')
            data.add_field('preview_available', 'true')
            
            async with self.session.post(f"{BACKEND_URL}/api/creator/content/upload", 
                                       data=data, headers=headers) as response:
                if response.status == 200:
                    response_data = await response.json()
                    if response_data.get("success"):
                        self.log_test("Form Data Validation - Valid Price Range", True, 
                                    "Valid price accepted successfully")
                    else:
                        self.log_test("Form Data Validation - Valid Price Range", False, 
                                    "Valid price rejected")
                else:
                    error_text = await response.text()
                    self.log_test("Form Data Validation - Valid Price Range", False, 
                                f"Status: {response.status}", error_text)
                    
        except Exception as e:
            self.log_test("Form Data Validation - Valid Price Range", False, f"Exception: {str(e)}")
        
        # Test 5: Optional fields handling
        try:
            data = aiohttp.FormData()
            data.add_field('title', 'Optional Fields Test')
            data.add_field('description', 'Testing optional field handling')
            data.add_field('content_type', 'document')
            data.add_field('price', '12.99')
            # category, tags, preview_available are optional
            
            async with self.session.post(f"{BACKEND_URL}/api/creator/content/upload", 
                                       data=data, headers=headers) as response:
                if response.status == 200:
                    response_data = await response.json()
                    if response_data.get("success"):
                        self.log_test("Form Data Validation - Optional Fields", True, 
                                    "Content created successfully with minimal required fields")
                    else:
                        self.log_test("Form Data Validation - Optional Fields", False, 
                                    "Failed to create content with minimal fields")
                else:
                    error_text = await response.text()
                    self.log_test("Form Data Validation - Optional Fields", False, 
                                f"Status: {response.status}", error_text)
                    
        except Exception as e:
            self.log_test("Form Data Validation - Optional Fields", False, f"Exception: {str(e)}")
    
    async def test_authentication_and_security(self):
        """Test authentication and security requirements"""
        
        # Test 1: Upload without authentication
        try:
            data = aiohttp.FormData()
            data.add_field('title', 'Unauthorized Test')
            data.add_field('description', 'Testing authentication requirement')
            data.add_field('content_type', 'document')
            data.add_field('category', 'test')
            data.add_field('price', '10.00')
            
            async with self.session.post(f"{BACKEND_URL}/api/creator/content/upload", 
                                       data=data) as response:
                if response.status in [401, 403]:
                    self.log_test("Authentication - No Token", True, 
                                "Correctly rejected request without authentication")
                else:
                    self.log_test("Authentication - No Token", False, 
                                f"Should require authentication, got status: {response.status}")
                    
        except Exception as e:
            self.log_test("Authentication - No Token", False, f"Exception: {str(e)}")
        
        # Test 2: Upload with invalid token
        try:
            invalid_headers = {"Authorization": "Bearer invalid_token_12345"}
            
            data = aiohttp.FormData()
            data.add_field('title', 'Invalid Token Test')
            data.add_field('description', 'Testing invalid token handling')
            data.add_field('content_type', 'document')
            data.add_field('category', 'test')
            data.add_field('price', '10.00')
            
            async with self.session.post(f"{BACKEND_URL}/api/creator/content/upload", 
                                       data=data, headers=invalid_headers) as response:
                if response.status in [401, 403]:
                    self.log_test("Authentication - Invalid Token", True, 
                                "Correctly rejected request with invalid token")
                else:
                    self.log_test("Authentication - Invalid Token", False, 
                                f"Should reject invalid token, got status: {response.status}")
                    
        except Exception as e:
            self.log_test("Authentication - Invalid Token", False, f"Exception: {str(e)}")
        
        # Test 3: Valid authentication (already tested in other methods, but verify here)
        if self.creator_token:
            try:
                headers = {"Authorization": f"Bearer {self.creator_token}"}
                
                data = aiohttp.FormData()
                data.add_field('title', 'Valid Auth Test')
                data.add_field('description', 'Testing valid authentication')
                data.add_field('content_type', 'document')
                data.add_field('category', 'test')
                data.add_field('price', '8.99')
                
                async with self.session.post(f"{BACKEND_URL}/api/creator/content/upload", 
                                           data=data, headers=headers) as response:
                    if response.status == 200:
                        response_data = await response.json()
                        if response_data.get("success"):
                            self.log_test("Authentication - Valid Token", True, 
                                        "Valid authentication accepted successfully")
                        else:
                            self.log_test("Authentication - Valid Token", False, 
                                        "Valid token rejected")
                    else:
                        error_text = await response.text()
                        self.log_test("Authentication - Valid Token", False, 
                                    f"Status: {response.status}", error_text)
                        
            except Exception as e:
                self.log_test("Authentication - Valid Token", False, f"Exception: {str(e)}")
        else:
            self.log_test("Authentication - Valid Token", False, "No creator token available for testing")
    
    async def run_all_tests(self):
        """Run all premium content file upload tests"""
        print("🧠 OnlyMentors.ai Premium Content Upload with File Testing")
        print("=" * 70)
        print()
        
        await self.setup_session()
        
        try:
            # Setup test creator
            print("📋 Setting up test creator...")
            creator_created = await self.create_test_creator()
            
            if not creator_created:
                print("⚠️  Failed to create test creator. Authentication tests will be limited.")
            
            print("\n📁 Testing Premium Content Upload with File...")
            await self.test_premium_content_upload_with_file()
            
            print("\n💾 Testing File Storage and Retrieval...")
            await self.test_file_storage_and_retrieval()
            
            print("\n✅ Testing Form Data Validation...")
            await self.test_form_data_validation()
            
            print("\n🔐 Testing Authentication and Security...")
            await self.test_authentication_and_security()
            
        finally:
            await self.cleanup_session()
        
        # Print summary
        print("\n" + "=" * 70)
        print("📊 TEST SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['details']}")
        
        print(f"\n🎯 PREMIUM CONTENT FILE UPLOAD STATUS:")
        
        # Analyze results by category
        categories = {
            "File Upload": [r for r in self.test_results if "Premium Content Upload with File" in r["test"] or "Premium Content Upload without File" in r["test"]],
            "File Storage": [r for r in self.test_results if "File Storage" in r["test"]],
            "Form Validation": [r for r in self.test_results if "Form Data Validation" in r["test"]],
            "Authentication": [r for r in self.test_results if "Authentication" in r["test"]]
        }
        
        for category, tests in categories.items():
            if tests:
                category_passed = sum(1 for t in tests if t["success"])
                category_total = len(tests)
                status = "✅" if category_passed == category_total else "⚠️" if category_passed > 0 else "❌"
                print(f"   {status} {category}: {category_passed}/{category_total} tests passed")
        
        return passed_tests, total_tests

async def main():
    """Main test execution"""
    tester = PremiumContentFileUploadTester()
    passed, total = await tester.run_all_tests()
    
    # Return exit code based on results
    if passed == total:
        print(f"\n🎉 ALL TESTS PASSED! Premium Content File Upload is fully functional.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} tests failed. Premium Content File Upload needs attention.")
        return 1

if __name__ == "__main__":
    import sys
    exit_code = asyncio.run(main())
    sys.exit(exit_code)