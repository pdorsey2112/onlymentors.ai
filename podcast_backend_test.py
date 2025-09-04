#!/usr/bin/env python3
"""
Backend Testing for Podcast Upload Functionality
Tests the newly implemented podcast/audio file upload support for both standard and premium content uploads.
"""

import requests
import json
import time
from io import BytesIO

# Configuration
BACKEND_URL = "https://mentor-search.preview.emergentagent.com/api"

class PodcastUploadTester:
    def __init__(self):
        self.results = []
        self.creator_token = None
        self.creator_id = None
        
    def log_result(self, test_name, success, details):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        self.results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
    
    def create_mock_audio_file(self, filename, size_kb=100):
        """Create a small mock audio file for testing"""
        # Create small content to avoid memory issues
        content = b"MOCK_AUDIO_DATA" * (size_kb * 10)  # Approximate size in KB
        return BytesIO(content), len(content)
    
    def setup_test_creator(self):
        """Create a test creator account for testing"""
        try:
            timestamp = int(time.time())
            creator_data = {
                "email": f"podcast_creator_{timestamp}@test.com",
                "password": "TestPassword123!",
                "full_name": "Podcast Creator Test",
                "account_name": f"podcast_creator_{timestamp}",
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
            
            # Create small mock audio file
            audio_content, file_size = self.create_mock_audio_file("test_podcast.mp3", 50)  # 50KB file
            
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
            
            # Create small mock audio file
            audio_content, file_size = self.create_mock_audio_file("premium_podcast.mp3", 50)  # 50KB file
            
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
                'preview_available': 'true'
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
    
    def test_audio_file_formats(self):
        """Test different audio file formats (mp3, aac, wav)"""
        formats_to_test = [
            ("test.mp3", "audio/mpeg"),
            ("test.aac", "audio/aac"),
            ("test.wav", "audio/wav"),
        ]
        
        success_count = 0
        
        for filename, mime_type in formats_to_test:
            try:
                if not self.creator_token or not self.creator_id:
                    continue
                
                # Create small mock audio file
                audio_content, file_size = self.create_mock_audio_file(filename, 30)
                
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
        
        success = success_count >= 2  # At least 2 formats should work
        self.log_result("Audio Format Validation", success, f"{success_count}/{len(formats_to_test)} formats accepted")
        return success
    
    def test_invalid_file_format_rejection(self):
        """Test that invalid file formats are rejected"""
        invalid_formats = [
            ("test.txt", "text/plain"),
            ("test.jpg", "image/jpeg"),
            ("test.pdf", "application/pdf")
        ]
        
        rejection_count = 0
        
        for filename, mime_type in invalid_formats:
            try:
                if not self.creator_token or not self.creator_id:
                    continue
                
                # Create mock file
                content = BytesIO(b"INVALID_CONTENT" * 10)
                
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
    
    def run_all_tests(self):
        """Run all podcast upload tests"""
        print("🎙️ STARTING PODCAST UPLOAD TESTING")
        print("=" * 50)
        
        # Setup
        if not self.setup_test_creator():
            print("❌ Failed to setup test creator. Aborting tests.")
            return
        
        # Run tests
        tests = [
            self.test_standard_content_podcast_upload,
            self.test_premium_content_podcast_upload,
            self.test_audio_file_formats,
            self.test_invalid_file_format_rejection,
        ]
        
        for test in tests:
            print(f"\n🧪 Running {test.__name__}...")
            test()
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 PODCAST UPLOAD TESTING SUMMARY")
        print("=" * 50)
        
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