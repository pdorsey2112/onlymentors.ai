#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Podcast Upload Functionality
Tests the newly implemented podcast/audio file upload support for both standard and premium content uploads.
"""

import requests
import json
import os
import tempfile
import time
from io import BytesIO

# Configuration
BACKEND_URL = "https://multi-tenant-ai.preview.emergentagent.com/api"

class PodcastUploadTester:
    def __init__(self):
        self.results = []
        self.creator_token = None
        self.creator_id = None
        self.user_token = None
        self.user_id = None
        
    def log_result(self, test_name, success, details):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        self.results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
    
    def create_mock_audio_file(self, filename, size_mb=1, file_type="mp3"):
        """Create a mock audio file for testing"""
        # Create a temporary file with the specified size
        content = b"MOCK_AUDIO_DATA" * (size_mb * 1024 * 1024 // 15)  # Approximate size
        
        # Ensure we have at least some content
        if len(content) < 100:
            content = b"MOCK_AUDIO_DATA" * 100
            
        return BytesIO(content), len(content)
    
    def setup_test_creator(self):
        """Create a test creator account for testing"""
        try:
            # Use the proper creator signup endpoint
            creator_data = {
                "email": f"podcast_creator_{int(time.time())}@test.com",
                "password": "TestPassword123!",
                "full_name": "Podcast Creator Test",
                "account_name": f"podcast_creator_{int(time.time())}",
                "description": "A test creator for podcast upload testing",
                "monthly_price": 29.99,
                "category": "business",
                "expertise_areas": ["podcasting", "audio content", "testing"]
            }
            
            response = requests.post(f"{BACKEND_URL}/creators/signup", json=creator_data)
            
            if response.status_code == 200:
                data = response.json()
                self.creator_token = data["token"]
                self.creator_id = data["creator"]["creator_id"]
                
                self.log_result("Setup Test Creator", True, f"Created creator with ID: {self.creator_id}")
                return True
            else:
                self.log_result("Setup Test Creator", False, f"Failed to create creator: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Setup Test Creator", False, f"Exception: {str(e)}")
            return False
    
    def test_standard_content_podcast_upload(self):
        """Test standard content upload with podcast content type"""
        try:
            if not self.creator_token or not self.creator_id:
                self.log_result("Standard Podcast Upload", False, "No creator credentials available")
                return False
            
            # Create mock audio file
            audio_content, file_size = self.create_mock_audio_file("test_podcast.mp3", 5)  # 5MB file
            
            # Prepare form data
            files = {
                'content_file': ('test_podcast.mp3', audio_content, 'audio/mpeg')
            }
            
            data = {
                'title': 'Test Podcast Episode',
                'description': 'A test podcast episode for validation',
                'content_type': 'podcast',
                'category': 'business',
                'tags': '["podcast", "test", "audio"]',
                'is_public': 'true'
            }
            
            headers = {"Authorization": f"Bearer {self.creator_token}"}
            
            response = requests.post(
                f"{BACKEND_URL}/creators/{self.creator_id}/content",
                files=files,
                data=data,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                content_id = result.get("content_id")
                
                # Verify content type is podcast
                if result.get("content_type") == "podcast":
                    self.log_result("Standard Podcast Upload", True, f"Successfully uploaded podcast content: {content_id}")
                    return True
                else:
                    self.log_result("Standard Podcast Upload", False, f"Content type mismatch: {result.get('content_type')}")
                    return False
            else:
                self.log_result("Standard Podcast Upload", False, f"Upload failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Standard Podcast Upload", False, f"Exception: {str(e)}")
            return False
    
    def test_premium_content_podcast_upload(self):
        """Test premium content upload with podcast content type"""
        try:
            if not self.creator_token:
                self.log_result("Premium Podcast Upload", False, "No creator credentials available")
                return False
            
            # Create mock audio file
            audio_content, file_size = self.create_mock_audio_file("premium_podcast.mp3", 10)  # 10MB file
            
            # Prepare form data
            files = {
                'content_file': ('premium_podcast.mp3', audio_content, 'audio/mpeg')
            }
            
            data = {
                'title': 'Premium Podcast Episode',
                'description': 'A premium podcast episode for testing',
                'content_type': 'podcast',
                'category': 'business',
                'tags': '["premium", "podcast", "audio"]',
                'price': '9.99',
                'preview_enabled': 'true'
            }
            
            headers = {"Authorization": f"Bearer {self.creator_token}"}
            
            response = requests.post(
                f"{BACKEND_URL}/creator/content/upload",
                files=files,
                data=data,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                content_id = result.get("content_id")
                
                # Verify content type is podcast and pricing
                if result.get("content_type") == "podcast" and result.get("price") == 9.99:
                    self.log_result("Premium Podcast Upload", True, f"Successfully uploaded premium podcast: {content_id}")
                    return True
                else:
                    self.log_result("Premium Podcast Upload", False, f"Content validation failed: {result}")
                    return False
            else:
                self.log_result("Premium Podcast Upload", False, f"Upload failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Premium Podcast Upload", False, f"Exception: {str(e)}")
            return False
    
    def test_audio_file_format_validation(self):
        """Test different audio file formats (mp3, aac, wav)"""
        formats_to_test = [
            ("test.mp3", "audio/mpeg"),
            ("test.aac", "audio/aac"),
            ("test.wav", "audio/wav"),
            ("test.mp4a", "audio/mp4")
        ]
        
        success_count = 0
        
        for filename, mime_type in formats_to_test:
            try:
                if not self.creator_token or not self.creator_id:
                    continue
                
                # Create mock audio file
                audio_content, file_size = self.create_mock_audio_file(filename, 2)
                
                files = {
                    'content_file': (filename, audio_content, mime_type)
                }
                
                data = {
                    'title': f'Test Audio Format {filename}',
                    'description': f'Testing {filename} format',
                    'content_type': 'podcast',
                    'category': 'business',
                    'tags': '["test", "format"]',
                    'is_public': 'true'
                }
                
                headers = {"Authorization": f"Bearer {self.creator_token}"}
                
                response = requests.post(
                    f"{BACKEND_URL}/creators/{self.creator_id}/content",
                    files=files,
                    data=data,
                    headers=headers
                )
                
                if response.status_code == 200:
                    success_count += 1
                    print(f"  ✅ {filename} format accepted")
                else:
                    print(f"  ❌ {filename} format rejected: {response.text}")
                    
            except Exception as e:
                print(f"  ❌ {filename} format error: {str(e)}")
        
        success = success_count == len(formats_to_test)
        self.log_result("Audio Format Validation", success, f"{success_count}/{len(formats_to_test)} formats accepted")
        return success
    
    def test_invalid_file_format_rejection(self):
        """Test that invalid file formats are rejected"""
        invalid_formats = [
            ("test.txt", "text/plain"),
            ("test.jpg", "image/jpeg"),
            ("test.pdf", "application/pdf"),
            ("test.mp4", "video/mp4")
        ]
        
        rejection_count = 0
        
        for filename, mime_type in invalid_formats:
            try:
                if not self.creator_token or not self.creator_id:
                    continue
                
                # Create mock file
                content = BytesIO(b"INVALID_CONTENT" * 100)
                
                files = {
                    'content_file': (filename, content, mime_type)
                }
                
                data = {
                    'title': f'Invalid Format Test {filename}',
                    'description': f'Testing invalid format {filename}',
                    'content_type': 'podcast',
                    'category': 'business',
                    'tags': '["test"]',
                    'is_public': 'true'
                }
                
                headers = {"Authorization": f"Bearer {self.creator_token}"}
                
                response = requests.post(
                    f"{BACKEND_URL}/creators/{self.creator_id}/content",
                    files=files,
                    data=data,
                    headers=headers
                )
                
                if response.status_code == 400:
                    rejection_count += 1
                    print(f"  ✅ {filename} correctly rejected")
                else:
                    print(f"  ❌ {filename} incorrectly accepted: {response.status_code}")
                    
            except Exception as e:
                print(f"  ❌ {filename} test error: {str(e)}")
        
        success = rejection_count == len(invalid_formats)
        self.log_result("Invalid Format Rejection", success, f"{rejection_count}/{len(invalid_formats)} invalid formats rejected")
        return success
    
    def test_file_size_limits(self):
        """Test file size limits for podcast uploads (500MB max)"""
        test_cases = [
            ("small_file.mp3", 1, True),      # 1MB - should pass
            ("medium_file.mp3", 100, True),   # 100MB - should pass
            ("large_file.mp3", 400, True),    # 400MB - should pass
            # Note: We can't easily test 600MB file due to memory constraints in testing
        ]
        
        success_count = 0
        
        for filename, size_mb, should_pass in test_cases:
            try:
                if not self.creator_token or not self.creator_id:
                    continue
                
                # Create mock audio file of specified size
                audio_content, file_size = self.create_mock_audio_file(filename, size_mb)
                
                files = {
                    'content_file': (filename, audio_content, 'audio/mpeg')
                }
                
                data = {
                    'title': f'Size Test {filename}',
                    'description': f'Testing {size_mb}MB file size',
                    'content_type': 'podcast',
                    'category': 'business',
                    'tags': '["test", "size"]',
                    'is_public': 'true'
                }
                
                headers = {"Authorization": f"Bearer {self.creator_token}"}
                
                response = requests.post(
                    f"{BACKEND_URL}/creators/{self.creator_id}/content",
                    files=files,
                    data=data,
                    headers=headers
                )
                
                if (response.status_code == 200) == should_pass:
                    success_count += 1
                    status = "accepted" if should_pass else "rejected"
                    print(f"  ✅ {size_mb}MB file correctly {status}")
                else:
                    expected = "accepted" if should_pass else "rejected"
                    actual = "accepted" if response.status_code == 200 else "rejected"
                    print(f"  ❌ {size_mb}MB file expected {expected}, got {actual}: {response.text}")
                    
            except Exception as e:
                print(f"  ❌ {size_mb}MB file test error: {str(e)}")
        
        success = success_count == len(test_cases)
        self.log_result("File Size Limits", success, f"{success_count}/{len(test_cases)} size tests passed")
        return success
    
    def test_fallback_extension_validation(self):
        """Test fallback validation by file extension when MIME type fails"""
        try:
            if not self.creator_token or not self.creator_id:
                self.log_result("Fallback Extension Validation", False, "No creator credentials")
                return False
            
            # Test with incorrect MIME type but correct extension
            audio_content, file_size = self.create_mock_audio_file("test.mp3", 2)
            
            files = {
                'content_file': ('test.mp3', audio_content, 'application/octet-stream')  # Wrong MIME type
            }
            
            data = {
                'title': 'Fallback Extension Test',
                'description': 'Testing fallback validation by extension',
                'content_type': 'podcast',
                'category': 'business',
                'tags': '["test", "fallback"]',
                'is_public': 'true'
            }
            
            headers = {"Authorization": f"Bearer {self.creator_token}"}
            
            response = requests.post(
                f"{BACKEND_URL}/creators/{self.creator_id}/content",
                files=files,
                data=data,
                headers=headers
            )
            
            if response.status_code == 200:
                self.log_result("Fallback Extension Validation", True, "File accepted via extension fallback")
                return True
            else:
                self.log_result("Fallback Extension Validation", False, f"Fallback failed: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Fallback Extension Validation", False, f"Exception: {str(e)}")
            return False
    
    def test_database_storage_verification(self):
        """Verify that podcast content is stored correctly in database"""
        try:
            # This test would require direct database access or API endpoints to verify storage
            # For now, we'll test via content retrieval if available
            
            if not self.creator_id:
                self.log_result("Database Storage Verification", False, "No creator ID available")
                return False
            
            # Try to get creator's content to verify storage
            headers = {"Authorization": f"Bearer {self.creator_token}"}
            
            response = requests.get(
                f"{BACKEND_URL}/creator/content/analytics",
                headers=headers
            )
            
            if response.status_code == 200:
                analytics = response.json()
                
                # Check if podcast content appears in analytics
                content_breakdown = analytics.get("content_breakdown", {})
                podcast_count = content_breakdown.get("podcast", 0)
                
                if podcast_count > 0:
                    self.log_result("Database Storage Verification", True, f"Found {podcast_count} podcast content items in database")
                    return True
                else:
                    self.log_result("Database Storage Verification", False, "No podcast content found in database")
                    return False
            else:
                self.log_result("Database Storage Verification", False, f"Failed to retrieve analytics: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Database Storage Verification", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all podcast upload tests"""
        print("🎙️ STARTING COMPREHENSIVE PODCAST UPLOAD TESTING")
        print("=" * 60)
        
        # Setup
        if not self.setup_test_creator():
            print("❌ Failed to setup test creator. Aborting tests.")
            return
        
        # Run tests
        tests = [
            self.test_standard_content_podcast_upload,
            self.test_premium_content_podcast_upload,
            self.test_audio_file_format_validation,
            self.test_invalid_file_format_rejection,
            self.test_file_size_limits,
            self.test_fallback_extension_validation,
            self.test_database_storage_verification
        ]
        
        for test in tests:
            print(f"\n🧪 Running {test.__name__}...")
            test()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 PODCAST UPLOAD TESTING SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.results if result["success"])
        total = len(self.results)
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("🎉 PODCAST UPLOAD FUNCTIONALITY IS WORKING WELL!")
        elif success_rate >= 60:
            print("⚠️  PODCAST UPLOAD FUNCTIONALITY HAS SOME ISSUES")
        else:
            print("🚨 PODCAST UPLOAD FUNCTIONALITY HAS CRITICAL ISSUES")
        
        return success_rate >= 80

if __name__ == "__main__":
    tester = PodcastUploadTester()
    tester.run_all_tests()