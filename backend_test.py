#!/usr/bin/env python3
"""
Premium Content Management System Testing
Tests edit, duplicate, and delete functionality for premium content
"""

import requests
import json
import time
import uuid
from datetime import datetime

# Configuration
BASE_URL = "https://mentor-search.preview.emergentagent.com/api"
TEST_CREATOR_EMAIL = "premium.creator@test.com"
TEST_CREATOR_PASSWORD = "TestPass123!"
TEST_CREATOR_NAME = "Premium Content Creator"

class PremiumContentManagementTester:
    def __init__(self):
        self.creator_token = None
        self.creator_id = None
        self.test_content_id = None
        self.duplicate_content_id = None
        self.results = []
        
    def log_result(self, test_name, success, details="", response_data=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if not success and response_data:
            print(f"   Response: {response_data}")
        print()

    def setup_test_creator(self):
        """Create and authenticate test creator"""
        print("🔧 Setting up test creator...")
        
        # Creator signup
        signup_data = {
            "email": TEST_CREATOR_EMAIL,
            "password": TEST_CREATOR_PASSWORD,
            "full_name": TEST_CREATOR_NAME,
            "account_name": "PremiumCreatorTest",
            "description": "Test creator for premium content management",
            "monthly_price": 100.0,
            "category": "business",
            "expertise_areas": ["Premium Content Creation", "Content Management"]
        }
        
        try:
            response = requests.post(f"{BASE_URL}/creators/signup", json=signup_data)
            if response.status_code in [200, 201]:
                data = response.json()
                self.creator_token = data.get("token")
                self.creator_id = data.get("creator", {}).get("creator_id")
                self.log_result("Creator Signup", True, f"Creator ID: {self.creator_id}")
                return True
            elif response.status_code == 400 and ("already exists" in response.text or "already registered" in response.text):
                # Try login instead
                return self.login_test_creator()
            else:
                self.log_result("Creator Signup", False, f"Status: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Creator Signup", False, f"Exception: {str(e)}")
            return False

    def login_test_creator(self):
        """Login existing test creator"""
        login_data = {
            "email": TEST_CREATOR_EMAIL,
            "password": TEST_CREATOR_PASSWORD
        }
        
        try:
            response = requests.post(f"{BASE_URL}/creators/login", json=login_data)
            if response.status_code == 200:
                data = response.json()
                self.creator_token = data.get("token")
                self.creator_id = data.get("creator", {}).get("creator_id")
                self.log_result("Creator Login", True, f"Creator ID: {self.creator_id}")
                return True
            else:
                self.log_result("Creator Login", False, f"Status: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Creator Login", False, f"Exception: {str(e)}")
            return False

    def create_test_premium_content(self):
        """Create premium content for testing"""
        print("📝 Creating test premium content...")
        
        headers = {"Authorization": f"Bearer {self.creator_token}"}
        
        # Create premium content using form data
        content_data = {
            "title": "Test Premium Content for Management",
            "description": "This is a test premium content for testing edit, duplicate, and delete operations",
            "content_type": "document",
            "category": "business",
            "price": 9.99,
            "tags": '["test", "premium", "management"]',
            "preview_available": True
        }
        
        try:
            response = requests.post(f"{BASE_URL}/creator/content/upload", data=content_data, headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.test_content_id = data.get("content_id")
                self.log_result("Create Test Premium Content", True, 
                              f"Content ID: {self.test_content_id}, Price: ${content_data['price']}")
                return True
            else:
                self.log_result("Create Test Premium Content", False, 
                              f"Status: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Create Test Premium Content", False, f"Exception: {str(e)}")
            return False

    def test_premium_content_edit(self):
        """Test premium content edit functionality"""
        print("✏️ Testing Premium Content Edit...")
        
        headers = {"Authorization": f"Bearer {self.creator_token}"}
        
        # Test 1: Valid content update
        updated_data = {
            "title": "Updated Premium Content Title",
            "description": "Updated description with new information",
            "category": "health",
            "price": 15.99,
            "tags": '["updated", "premium", "health"]',
            "preview_available": False
        }
        
        try:
            response = requests.put(
                f"{BASE_URL}/creators/{self.creator_id}/premium-content/{self.test_content_id}",
                data=updated_data,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("content", {})
                
                # Verify updates
                title_correct = content.get("title") == updated_data["title"]
                price_correct = content.get("price") == updated_data["price"]
                category_correct = content.get("category") == updated_data["category"]
                preview_correct = content.get("preview_available") == updated_data["preview_available"]
                
                if all([title_correct, price_correct, category_correct, preview_correct]):
                    self.log_result("Premium Content Edit - Valid Update", True,
                                  f"All fields updated correctly. New price: ${content.get('price')}")
                else:
                    self.log_result("Premium Content Edit - Valid Update", False,
                                  f"Field validation failed. Title: {title_correct}, Price: {price_correct}, Category: {category_correct}, Preview: {preview_correct}")
            else:
                self.log_result("Premium Content Edit - Valid Update", False,
                              f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Premium Content Edit - Valid Update", False, f"Exception: {str(e)}")

        # Test 2: Price validation (too low)
        try:
            invalid_price_data = updated_data.copy()
            invalid_price_data["price"] = 0.005  # Below minimum
            
            response = requests.put(
                f"{BASE_URL}/creators/{self.creator_id}/premium-content/{self.test_content_id}",
                data=invalid_price_data,
                headers=headers
            )
            
            if response.status_code == 400:
                self.log_result("Premium Content Edit - Price Validation (Low)", True,
                              "Correctly rejected price below $0.01")
            else:
                self.log_result("Premium Content Edit - Price Validation (Low)", False,
                              f"Should reject low price. Status: {response.status_code}")
        except Exception as e:
            self.log_result("Premium Content Edit - Price Validation (Low)", False, f"Exception: {str(e)}")

        # Test 3: Price validation (too high)
        try:
            invalid_price_data = updated_data.copy()
            invalid_price_data["price"] = 55.00  # Above maximum
            
            response = requests.put(
                f"{BASE_URL}/creators/{self.creator_id}/premium-content/{self.test_content_id}",
                data=invalid_price_data,
                headers=headers
            )
            
            if response.status_code == 400:
                self.log_result("Premium Content Edit - Price Validation (High)", True,
                              "Correctly rejected price above $50.00")
            else:
                self.log_result("Premium Content Edit - Price Validation (High)", False,
                              f"Should reject high price. Status: {response.status_code}")
        except Exception as e:
            self.log_result("Premium Content Edit - Price Validation (High)", False, f"Exception: {str(e)}")

        # Test 4: Authentication required
        try:
            response = requests.put(
                f"{BASE_URL}/creators/{self.creator_id}/premium-content/{self.test_content_id}",
                data=updated_data
                # No headers (no auth)
            )
            
            if response.status_code in [401, 403]:
                self.log_result("Premium Content Edit - Authentication Required", True,
                              "Correctly requires authentication")
            else:
                self.log_result("Premium Content Edit - Authentication Required", False,
                              f"Should require auth. Status: {response.status_code}")
        except Exception as e:
            self.log_result("Premium Content Edit - Authentication Required", False, f"Exception: {str(e)}")

        # Test 5: Cross-creator access denied
        try:
            fake_creator_id = str(uuid.uuid4())
            response = requests.put(
                f"{BASE_URL}/creators/{fake_creator_id}/premium-content/{self.test_content_id}",
                data=updated_data,
                headers=headers
            )
            
            if response.status_code == 403:
                self.log_result("Premium Content Edit - Cross-Creator Access Denied", True,
                              "Correctly denies access to other creator's content")
            else:
                self.log_result("Premium Content Edit - Cross-Creator Access Denied", False,
                              f"Should deny cross-creator access. Status: {response.status_code}")
        except Exception as e:
            self.log_result("Premium Content Edit - Cross-Creator Access Denied", False, f"Exception: {str(e)}")

    def test_premium_content_duplicate(self):
        """Test premium content duplicate functionality"""
        print("📋 Testing Premium Content Duplicate...")
        
        headers = {"Authorization": f"Bearer {self.creator_token}"}
        
        # Test 1: Valid content duplication
        try:
            response = requests.post(
                f"{BASE_URL}/creators/{self.creator_id}/premium-content/{self.test_content_id}/duplicate",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                duplicate_content = data.get("content", {})
                self.duplicate_content_id = duplicate_content.get("content_id")
                
                # Verify duplicate properties
                title_has_copy = "(Copy)" in duplicate_content.get("title", "")
                new_content_id = duplicate_content.get("content_id") != self.test_content_id
                stats_reset = (duplicate_content.get("total_purchases", -1) == 0 and 
                             duplicate_content.get("total_revenue", -1) == 0 and
                             duplicate_content.get("creator_earnings", -1) == 0)
                
                if all([title_has_copy, new_content_id, stats_reset]):
                    self.log_result("Premium Content Duplicate - Valid Duplication", True,
                                  f"Duplicate created with ID: {self.duplicate_content_id}, Title: {duplicate_content.get('title')}")
                else:
                    self.log_result("Premium Content Duplicate - Valid Duplication", False,
                                  f"Validation failed. Copy suffix: {title_has_copy}, New ID: {new_content_id}, Stats reset: {stats_reset}")
            else:
                self.log_result("Premium Content Duplicate - Valid Duplication", False,
                              f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Premium Content Duplicate - Valid Duplication", False, f"Exception: {str(e)}")

        # Test 2: Authentication required
        try:
            response = requests.post(
                f"{BASE_URL}/creators/{self.creator_id}/premium-content/{self.test_content_id}/duplicate"
                # No headers (no auth)
            )
            
            if response.status_code in [401, 403]:
                self.log_result("Premium Content Duplicate - Authentication Required", True,
                              "Correctly requires authentication")
            else:
                self.log_result("Premium Content Duplicate - Authentication Required", False,
                              f"Should require auth. Status: {response.status_code}")
        except Exception as e:
            self.log_result("Premium Content Duplicate - Authentication Required", False, f"Exception: {str(e)}")

        # Test 3: Cross-creator access denied
        try:
            fake_creator_id = str(uuid.uuid4())
            response = requests.post(
                f"{BASE_URL}/creators/{fake_creator_id}/premium-content/{self.test_content_id}/duplicate",
                headers=headers
            )
            
            if response.status_code == 403:
                self.log_result("Premium Content Duplicate - Cross-Creator Access Denied", True,
                              "Correctly denies access to other creator's content")
            else:
                self.log_result("Premium Content Duplicate - Cross-Creator Access Denied", False,
                              f"Should deny cross-creator access. Status: {response.status_code}")
        except Exception as e:
            self.log_result("Premium Content Duplicate - Cross-Creator Access Denied", False, f"Exception: {str(e)}")

        # Test 4: Non-existent content
        try:
            fake_content_id = str(uuid.uuid4())
            response = requests.post(
                f"{BASE_URL}/creators/{self.creator_id}/premium-content/{fake_content_id}/duplicate",
                headers=headers
            )
            
            if response.status_code == 404:
                self.log_result("Premium Content Duplicate - Non-Existent Content", True,
                              "Correctly handles non-existent content")
            else:
                self.log_result("Premium Content Duplicate - Non-Existent Content", False,
                              f"Should return 404 for non-existent content. Status: {response.status_code}")
        except Exception as e:
            self.log_result("Premium Content Duplicate - Non-Existent Content", False, f"Exception: {str(e)}")

    def test_premium_content_delete(self):
        """Test premium content delete functionality"""
        print("🗑️ Testing Premium Content Delete...")
        
        headers = {"Authorization": f"Bearer {self.creator_token}"}
        
        # Test 1: Authentication required
        try:
            response = requests.delete(
                f"{BASE_URL}/creators/{self.creator_id}/premium-content/{self.duplicate_content_id}"
                # No headers (no auth)
            )
            
            if response.status_code in [401, 403]:
                self.log_result("Premium Content Delete - Authentication Required", True,
                              "Correctly requires authentication")
            else:
                self.log_result("Premium Content Delete - Authentication Required", False,
                              f"Should require auth. Status: {response.status_code}")
        except Exception as e:
            self.log_result("Premium Content Delete - Authentication Required", False, f"Exception: {str(e)}")

        # Test 2: Cross-creator access denied
        try:
            fake_creator_id = str(uuid.uuid4())
            response = requests.delete(
                f"{BASE_URL}/creators/{fake_creator_id}/premium-content/{self.duplicate_content_id}",
                headers=headers
            )
            
            if response.status_code == 403:
                self.log_result("Premium Content Delete - Cross-Creator Access Denied", True,
                              "Correctly denies access to other creator's content")
            else:
                self.log_result("Premium Content Delete - Cross-Creator Access Denied", False,
                              f"Should deny cross-creator access. Status: {response.status_code}")
        except Exception as e:
            self.log_result("Premium Content Delete - Cross-Creator Access Denied", False, f"Exception: {str(e)}")

        # Test 3: Valid content deletion (delete duplicate first)
        if self.duplicate_content_id:
            try:
                response = requests.delete(
                    f"{BASE_URL}/creators/{self.creator_id}/premium-content/{self.duplicate_content_id}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    self.log_result("Premium Content Delete - Valid Deletion (Duplicate)", True,
                                  f"Successfully deleted duplicate content: {self.duplicate_content_id}")
                else:
                    self.log_result("Premium Content Delete - Valid Deletion (Duplicate)", False,
                                  f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Premium Content Delete - Valid Deletion (Duplicate)", False, f"Exception: {str(e)}")

        # Test 4: Delete non-existent content
        try:
            fake_content_id = str(uuid.uuid4())
            response = requests.delete(
                f"{BASE_URL}/creators/{self.creator_id}/premium-content/{fake_content_id}",
                headers=headers
            )
            
            if response.status_code == 404:
                self.log_result("Premium Content Delete - Non-Existent Content", True,
                              "Correctly handles non-existent content")
            else:
                self.log_result("Premium Content Delete - Non-Existent Content", False,
                              f"Should return 404 for non-existent content. Status: {response.status_code}")
        except Exception as e:
            self.log_result("Premium Content Delete - Non-Existent Content", False, f"Exception: {str(e)}")

        # Test 5: Valid content deletion (delete original)
        if self.test_content_id:
            try:
                response = requests.delete(
                    f"{BASE_URL}/creators/{self.creator_id}/premium-content/{self.test_content_id}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    self.log_result("Premium Content Delete - Valid Deletion (Original)", True,
                                  f"Successfully deleted original content: {self.test_content_id}")
                    
                    # Verify content is actually deleted by trying to access it
                    verify_response = requests.get(
                        f"{BASE_URL}/creators/{self.creator_id}/premium-content",
                        headers=headers
                    )
                    
                    if verify_response.status_code == 200:
                        content_list = verify_response.json().get("content", [])
                        content_exists = any(c.get("content_id") == self.test_content_id for c in content_list)
                        
                        if not content_exists:
                            self.log_result("Premium Content Delete - Verification", True,
                                          "Content successfully removed from database")
                        else:
                            self.log_result("Premium Content Delete - Verification", False,
                                          "Content still exists in database after deletion")
                else:
                    self.log_result("Premium Content Delete - Valid Deletion (Original)", False,
                                  f"Status: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Premium Content Delete - Valid Deletion (Original)", False, f"Exception: {str(e)}")

    def test_end_to_end_workflow(self):
        """Test complete end-to-end premium content management workflow"""
        print("🔄 Testing End-to-End Premium Content Management Workflow...")
        
        headers = {"Authorization": f"Bearer {self.creator_token}"}
        
        # Step 1: Upload new content
        workflow_content_data = {
            "title": "E2E Workflow Test Content",
            "description": "Content for testing complete workflow",
            "content_type": "video",
            "category": "science",
            "price": 25.00,
            "tags": '["workflow", "test", "e2e"]',
            "preview_available": True
        }
        
        try:
            # Upload
            upload_response = requests.post(f"{BASE_URL}/creator/content/upload", 
                                          data=workflow_content_data, headers=headers)
            
            if upload_response.status_code != 200:
                self.log_result("E2E Workflow - Upload", False, 
                              f"Upload failed. Status: {upload_response.status_code}")
                return
            
            workflow_content_id = upload_response.json().get("content_id")
            self.log_result("E2E Workflow - Upload", True, f"Content uploaded: {workflow_content_id}")
            
            # Step 2: Edit the content
            edit_data = {
                "title": "E2E Workflow Test Content (Edited)",
                "description": "Updated description for workflow test",
                "category": "health",
                "price": 30.00,
                "tags": '["workflow", "test", "e2e", "edited"]',
                "preview_available": False
            }
            
            edit_response = requests.put(
                f"{BASE_URL}/creators/{self.creator_id}/premium-content/{workflow_content_id}",
                data=edit_data, headers=headers
            )
            
            if edit_response.status_code == 200:
                self.log_result("E2E Workflow - Edit", True, "Content successfully edited")
            else:
                self.log_result("E2E Workflow - Edit", False, 
                              f"Edit failed. Status: {edit_response.status_code}")
                return
            
            # Step 3: Duplicate the content
            duplicate_response = requests.post(
                f"{BASE_URL}/creators/{self.creator_id}/premium-content/{workflow_content_id}/duplicate",
                headers=headers
            )
            
            if duplicate_response.status_code == 200:
                duplicate_id = duplicate_response.json().get("content", {}).get("content_id")
                self.log_result("E2E Workflow - Duplicate", True, f"Content duplicated: {duplicate_id}")
            else:
                self.log_result("E2E Workflow - Duplicate", False, 
                              f"Duplicate failed. Status: {duplicate_response.status_code}")
                return
            
            # Step 4: Delete the duplicate
            delete_duplicate_response = requests.delete(
                f"{BASE_URL}/creators/{self.creator_id}/premium-content/{duplicate_id}",
                headers=headers
            )
            
            if delete_duplicate_response.status_code == 200:
                self.log_result("E2E Workflow - Delete Duplicate", True, "Duplicate successfully deleted")
            else:
                self.log_result("E2E Workflow - Delete Duplicate", False, 
                              f"Delete duplicate failed. Status: {delete_duplicate_response.status_code}")
            
            # Step 5: Delete the original
            delete_original_response = requests.delete(
                f"{BASE_URL}/creators/{self.creator_id}/premium-content/{workflow_content_id}",
                headers=headers
            )
            
            if delete_original_response.status_code == 200:
                self.log_result("E2E Workflow - Delete Original", True, "Original content successfully deleted")
                self.log_result("E2E Workflow - Complete", True, 
                              "Full workflow completed: Upload → Edit → Duplicate → Delete")
            else:
                self.log_result("E2E Workflow - Delete Original", False, 
                              f"Delete original failed. Status: {delete_original_response.status_code}")
                
        except Exception as e:
            self.log_result("E2E Workflow", False, f"Exception during workflow: {str(e)}")

    def run_all_tests(self):
        """Run all premium content management tests"""
        print("🚀 Starting Premium Content Management System Testing")
        print("=" * 60)
        
        # Setup
        if not self.setup_test_creator():
            print("❌ Failed to setup test creator. Aborting tests.")
            return
        
        if not self.create_test_premium_content():
            print("❌ Failed to create test content. Aborting tests.")
            return
        
        # Run tests
        self.test_premium_content_edit()
        self.test_premium_content_duplicate()
        self.test_premium_content_delete()
        self.test_end_to_end_workflow()
        
        # Summary
        self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("🎯 PREMIUM CONTENT MANAGEMENT TESTING SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        print()
        
        # Group results by category
        categories = {
            "Setup": [],
            "Edit": [],
            "Duplicate": [],
            "Delete": [],
            "E2E Workflow": []
        }
        
        for result in self.results:
            test_name = result["test"]
            if "Setup" in test_name or "Signup" in test_name or "Login" in test_name or "Create Test" in test_name:
                categories["Setup"].append(result)
            elif "Edit" in test_name:
                categories["Edit"].append(result)
            elif "Duplicate" in test_name:
                categories["Duplicate"].append(result)
            elif "Delete" in test_name:
                categories["Delete"].append(result)
            elif "E2E" in test_name or "Workflow" in test_name:
                categories["E2E Workflow"].append(result)
        
        for category, tests in categories.items():
            if tests:
                passed = sum(1 for t in tests if t["success"])
                total = len(tests)
                print(f"📂 {category}: {passed}/{total} passed")
                for test in tests:
                    print(f"   {test['status']}: {test['test']}")
                print()
        
        # Critical issues
        critical_failures = [r for r in self.results if not r["success"] and 
                           ("Authentication" in r["test"] or "Cross-Creator" in r["test"] or 
                            "Valid" in r["test"] and ("Edit" in r["test"] or "Delete" in r["test"] or "Duplicate" in r["test"]))]
        
        if critical_failures:
            print("🚨 CRITICAL ISSUES FOUND:")
            for failure in critical_failures:
                print(f"   ❌ {failure['test']}: {failure['details']}")
            print()
        
        # Overall assessment
        if success_rate >= 90:
            print("🎉 EXCELLENT: Premium Content Management System is working excellently!")
        elif success_rate >= 75:
            print("✅ GOOD: Premium Content Management System is working well with minor issues.")
        elif success_rate >= 50:
            print("⚠️ MODERATE: Premium Content Management System has some significant issues.")
        else:
            print("🚨 CRITICAL: Premium Content Management System has major issues requiring immediate attention.")
        
        print("=" * 60)

if __name__ == "__main__":
    tester = PremiumContentManagementTester()
    tester.run_all_tests()