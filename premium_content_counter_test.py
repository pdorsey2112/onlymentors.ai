#!/usr/bin/env python3
"""
Premium Content Counter Fix Testing
Tests the premium content counter fix to ensure dashboard shows correct premium content count.

Focus Areas:
1. Premium Content Stats Fetching - Test the new stats endpoint integration
2. Stats Refresh After Upload - Test stats update after content operations  
3. Real-time Stats Updates - Test dashboard updates
4. Cross-Verification - Test data consistency
"""

import requests
import json
import time
import uuid
from datetime import datetime

# Configuration
BASE_URL = "https://enterprise-coach.preview.emergentagent.com/api"
TEST_CREATOR_EMAIL = "counter.test@creator.com"
TEST_CREATOR_PASSWORD = "CounterTest123!"
TEST_CREATOR_NAME = "Counter Test Creator"

class PremiumContentCounterTester:
    def __init__(self):
        self.creator_token = None
        self.creator_id = None
        self.uploaded_content_ids = []
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
        print("🔧 Setting up test creator for counter testing...")
        
        # Creator signup
        signup_data = {
            "email": TEST_CREATOR_EMAIL,
            "password": TEST_CREATOR_PASSWORD,
            "full_name": TEST_CREATOR_NAME,
            "account_name": "CounterTestCreator",
            "description": "Test creator for premium content counter testing",
            "monthly_price": 50.0,
            "category": "business",
            "expertise_areas": ["Content Creation", "Counter Testing"]
        }
        
        try:
            response = requests.post(f"{BASE_URL}/creators/signup", json=signup_data)
            if response.status_code in [200, 201]:
                data = response.json()
                self.creator_token = data.get("token")
                self.creator_id = data.get("creator", {}).get("creator_id")
                self.log_result("Creator Setup", True, f"Creator ID: {self.creator_id}")
                return True
            elif response.status_code == 400 and ("already exists" in response.text or "already registered" in response.text):
                # Try login instead
                return self.login_test_creator()
            else:
                self.log_result("Creator Setup", False, f"Status: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Creator Setup", False, f"Exception: {str(e)}")
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

    def test_initial_stats_endpoints(self):
        """Test 1: Premium Content Stats Fetching - Test the new stats endpoint integration"""
        print("📊 Testing Premium Content Stats Endpoints...")
        
        headers = {"Authorization": f"Bearer {self.creator_token}"}
        
        # Test standard content endpoint
        try:
            response = requests.get(f"{BASE_URL}/creators/{self.creator_id}/content", headers=headers)
            if response.status_code == 200:
                data = response.json()
                standard_count = len(data.get("content", []))
                self.log_result("Standard Content Endpoint", True, 
                              f"Standard content count: {standard_count}")
            else:
                self.log_result("Standard Content Endpoint", False, 
                              f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Standard Content Endpoint", False, f"Exception: {str(e)}")

        # Test premium content endpoint
        try:
            response = requests.get(f"{BASE_URL}/creators/{self.creator_id}/premium-content", headers=headers)
            if response.status_code == 200:
                data = response.json()
                premium_count = len(data.get("content", []))
                self.log_result("Premium Content Endpoint", True, 
                              f"Premium content count: {premium_count}")
                return premium_count
            else:
                self.log_result("Premium Content Endpoint", False, 
                              f"Status: {response.status_code}", response.text)
                return 0
        except Exception as e:
            self.log_result("Premium Content Endpoint", False, f"Exception: {str(e)}")
            return 0

    def test_creator_stats_endpoint(self):
        """Test creator stats endpoint that should include premium content count"""
        print("📈 Testing Creator Stats Endpoint...")
        
        headers = {"Authorization": f"Bearer {self.creator_token}"}
        
        try:
            response = requests.get(f"{BASE_URL}/creators/{self.creator_id}/stats", headers=headers)
            if response.status_code == 200:
                data = response.json()
                stats = data.get("stats", {})
                
                # Check if premium content count is included
                premium_count = stats.get("premium_content_count", 0)
                premium_earnings = stats.get("premium_earnings", 0)
                total_sales = stats.get("total_sales", 0)
                
                self.log_result("Creator Stats Endpoint", True, 
                              f"Premium count: {premium_count}, Earnings: ${premium_earnings}, Sales: {total_sales}")
                return premium_count, premium_earnings
            else:
                self.log_result("Creator Stats Endpoint", False, 
                              f"Status: {response.status_code}", response.text)
                return 0, 0
        except Exception as e:
            self.log_result("Creator Stats Endpoint", False, f"Exception: {str(e)}")
            return 0, 0

    def upload_premium_content(self, title_suffix=""):
        """Upload premium content for testing"""
        print(f"📝 Uploading premium content{title_suffix}...")
        
        headers = {"Authorization": f"Bearer {self.creator_token}"}
        
        content_data = {
            "title": f"Premium Counter Test Content{title_suffix}",
            "description": f"Test premium content for counter testing{title_suffix}",
            "content_type": "document",
            "category": "business",
            "price": 19.99,
            "tags": '["counter", "test", "premium"]',
            "preview_available": True
        }
        
        try:
            response = requests.post(f"{BASE_URL}/creator/content/upload", data=content_data, headers=headers)
            if response.status_code == 200:
                data = response.json()
                content_id = data.get("content_id")
                self.uploaded_content_ids.append(content_id)
                self.log_result(f"Upload Premium Content{title_suffix}", True, 
                              f"Content ID: {content_id}, Price: ${content_data['price']}")
                return content_id
            else:
                self.log_result(f"Upload Premium Content{title_suffix}", False, 
                              f"Status: {response.status_code}", response.text)
                return None
        except Exception as e:
            self.log_result(f"Upload Premium Content{title_suffix}", False, f"Exception: {str(e)}")
            return None

    def test_stats_refresh_after_upload(self):
        """Test 2: Stats Refresh After Upload - Test stats update after content operations"""
        print("🔄 Testing Stats Refresh After Upload...")
        
        # Get initial counts
        initial_premium_count = self.test_initial_stats_endpoints()
        initial_stats_count, initial_earnings = self.test_creator_stats_endpoint()
        
        # Upload premium content
        content_id = self.upload_premium_content(" #1")
        if not content_id:
            self.log_result("Stats Refresh Test", False, "Failed to upload content for testing")
            return
        
        # Wait a moment for potential async processing
        time.sleep(2)
        
        # Check updated counts
        updated_premium_count = self.test_initial_stats_endpoints()
        updated_stats_count, updated_earnings = self.test_creator_stats_endpoint()
        
        # Verify count increased
        premium_count_increased = updated_premium_count > initial_premium_count
        stats_count_increased = updated_stats_count > initial_stats_count
        
        if premium_count_increased and stats_count_increased:
            self.log_result("Stats Refresh After Upload", True, 
                          f"Premium count increased from {initial_premium_count} to {updated_premium_count}, Stats count from {initial_stats_count} to {updated_stats_count}")
        else:
            self.log_result("Stats Refresh After Upload", False, 
                          f"Count not updated properly. Premium: {initial_premium_count}→{updated_premium_count}, Stats: {initial_stats_count}→{updated_stats_count}")

    def test_real_time_stats_updates(self):
        """Test 3: Real-time Stats Updates - Test dashboard updates after various operations"""
        print("⚡ Testing Real-time Stats Updates...")
        
        headers = {"Authorization": f"Bearer {self.creator_token}"}
        
        # Get baseline
        baseline_count = self.test_initial_stats_endpoints()
        baseline_stats, baseline_earnings = self.test_creator_stats_endpoint()
        
        # Test 1: Upload → verify counter increases
        content_id_1 = self.upload_premium_content(" #2")
        time.sleep(1)
        after_upload_count = self.test_initial_stats_endpoints()
        after_upload_stats, after_upload_earnings = self.test_creator_stats_endpoint()
        
        upload_success = (after_upload_count > baseline_count and after_upload_stats > baseline_stats)
        self.log_result("Real-time Update - Upload", upload_success, 
                      f"Count after upload: {after_upload_count}, Stats: {after_upload_stats}")
        
        if not content_id_1:
            return
        
        # Test 2: Edit → verify stats remain accurate
        edit_data = {
            "title": "Edited Premium Counter Test Content #2",
            "description": "Updated description for counter testing",
            "price": 24.99
        }
        
        try:
            edit_response = requests.put(
                f"{BASE_URL}/creators/{self.creator_id}/premium-content/{content_id_1}",
                data=edit_data, headers=headers
            )
            
            if edit_response.status_code == 200:
                time.sleep(1)
                after_edit_count = self.test_initial_stats_endpoints()
                after_edit_stats, after_edit_earnings = self.test_creator_stats_endpoint()
                
                # Count should remain same, but earnings might change due to price update
                edit_success = (after_edit_count == after_upload_count and after_edit_stats == after_upload_stats)
                self.log_result("Real-time Update - Edit", edit_success, 
                              f"Count after edit: {after_edit_count}, Stats: {after_edit_stats}")
            else:
                self.log_result("Real-time Update - Edit", False, f"Edit failed: {edit_response.status_code}")
        except Exception as e:
            self.log_result("Real-time Update - Edit", False, f"Edit exception: {str(e)}")
        
        # Test 3: Duplicate → verify counter increases
        try:
            duplicate_response = requests.post(
                f"{BASE_URL}/creators/{self.creator_id}/premium-content/{content_id_1}/duplicate",
                headers=headers
            )
            
            if duplicate_response.status_code == 200:
                duplicate_id = duplicate_response.json().get("content", {}).get("content_id")
                self.uploaded_content_ids.append(duplicate_id)
                
                time.sleep(1)
                after_duplicate_count = self.test_initial_stats_endpoints()
                after_duplicate_stats, after_duplicate_earnings = self.test_creator_stats_endpoint()
                
                duplicate_success = (after_duplicate_count > after_edit_count and after_duplicate_stats > after_edit_stats)
                self.log_result("Real-time Update - Duplicate", duplicate_success, 
                              f"Count after duplicate: {after_duplicate_count}, Stats: {after_duplicate_stats}")
                
                # Test 4: Delete → verify counter decreases
                delete_response = requests.delete(
                    f"{BASE_URL}/creators/{self.creator_id}/premium-content/{duplicate_id}",
                    headers=headers
                )
                
                if delete_response.status_code == 200:
                    time.sleep(1)
                    after_delete_count = self.test_initial_stats_endpoints()
                    after_delete_stats, after_delete_earnings = self.test_creator_stats_endpoint()
                    
                    delete_success = (after_delete_count < after_duplicate_count and after_delete_stats < after_duplicate_stats)
                    self.log_result("Real-time Update - Delete", delete_success, 
                                  f"Count after delete: {after_delete_count}, Stats: {after_delete_stats}")
                else:
                    self.log_result("Real-time Update - Delete", False, f"Delete failed: {delete_response.status_code}")
            else:
                self.log_result("Real-time Update - Duplicate", False, f"Duplicate failed: {duplicate_response.status_code}")
        except Exception as e:
            self.log_result("Real-time Update - Duplicate/Delete", False, f"Exception: {str(e)}")

    def test_cross_verification(self):
        """Test 4: Cross-Verification - Test data consistency between endpoints"""
        print("🔍 Testing Cross-Verification - Data Consistency...")
        
        headers = {"Authorization": f"Bearer {self.creator_token}"}
        
        # Get counts from different endpoints
        try:
            # Premium content management endpoint
            mgmt_response = requests.get(f"{BASE_URL}/creators/{self.creator_id}/premium-content", headers=headers)
            mgmt_count = 0
            if mgmt_response.status_code == 200:
                mgmt_data = mgmt_response.json()
                mgmt_count = len(mgmt_data.get("content", []))
                mgmt_total_revenue = sum(c.get("total_revenue", 0) for c in mgmt_data.get("content", []))
            
            # Creator stats endpoint
            stats_response = requests.get(f"{BASE_URL}/creators/{self.creator_id}/stats", headers=headers)
            stats_count = 0
            stats_earnings = 0
            if stats_response.status_code == 200:
                stats_data = stats_response.json()
                stats = stats_data.get("stats", {})
                stats_count = stats.get("premium_content_count", 0)
                stats_earnings = stats.get("premium_earnings", 0)
            
            # Premium content discovery endpoint (public view)
            discovery_response = requests.get(f"{BASE_URL}/mentor/{self.creator_id}/premium-content")
            discovery_count = 0
            if discovery_response.status_code == 200:
                discovery_data = discovery_response.json()
                discovery_count = len(discovery_data.get("content", []))
            
            # Verify consistency
            mgmt_stats_match = (mgmt_count == stats_count)
            mgmt_discovery_match = (mgmt_count == discovery_count)
            
            if mgmt_stats_match and mgmt_discovery_match:
                self.log_result("Cross-Verification - Count Consistency", True, 
                              f"All endpoints show consistent count: {mgmt_count}")
            else:
                self.log_result("Cross-Verification - Count Consistency", False, 
                              f"Inconsistent counts - Mgmt: {mgmt_count}, Stats: {stats_count}, Discovery: {discovery_count}")
            
            # Verify earnings calculation (80% minus $2.99 minimum)
            expected_earnings = max(mgmt_total_revenue * 0.8, mgmt_total_revenue - 2.99) if mgmt_total_revenue > 0 else 0
            earnings_correct = abs(stats_earnings - expected_earnings) < 0.01  # Allow for small floating point differences
            
            self.log_result("Cross-Verification - Earnings Calculation", earnings_correct, 
                          f"Expected: ${expected_earnings:.2f}, Actual: ${stats_earnings:.2f}")
            
        except Exception as e:
            self.log_result("Cross-Verification", False, f"Exception: {str(e)}")

    def test_dashboard_stats_persistence(self):
        """Test stats persistence across dashboard reloads"""
        print("💾 Testing Dashboard Stats Persistence...")
        
        headers = {"Authorization": f"Bearer {self.creator_token}"}
        
        # Get current stats
        try:
            response1 = requests.get(f"{BASE_URL}/creators/{self.creator_id}/stats", headers=headers)
            if response1.status_code != 200:
                self.log_result("Stats Persistence - Initial Load", False, f"Status: {response1.status_code}")
                return
            
            stats1 = response1.json().get("stats", {})
            count1 = stats1.get("premium_content_count", 0)
            earnings1 = stats1.get("premium_earnings", 0)
            
            # Wait and reload
            time.sleep(2)
            
            response2 = requests.get(f"{BASE_URL}/creators/{self.creator_id}/stats", headers=headers)
            if response2.status_code != 200:
                self.log_result("Stats Persistence - Reload", False, f"Status: {response2.status_code}")
                return
            
            stats2 = response2.json().get("stats", {})
            count2 = stats2.get("premium_content_count", 0)
            earnings2 = stats2.get("premium_earnings", 0)
            
            # Verify persistence
            persistent = (count1 == count2 and earnings1 == earnings2)
            self.log_result("Stats Persistence Across Reloads", persistent, 
                          f"Load 1: Count={count1}, Earnings=${earnings1} | Load 2: Count={count2}, Earnings=${earnings2}")
            
        except Exception as e:
            self.log_result("Stats Persistence", False, f"Exception: {str(e)}")

    def test_zero_to_one_scenario(self):
        """Test the specific scenario: counter should show '1' instead of '0' after upload"""
        print("🎯 Testing Zero-to-One Scenario (Main Issue)...")
        
        headers = {"Authorization": f"Bearer {self.creator_token}"}
        
        # Clean slate - delete all existing premium content first
        try:
            response = requests.get(f"{BASE_URL}/creators/{self.creator_id}/premium-content", headers=headers)
            if response.status_code == 200:
                existing_content = response.json().get("content", [])
                for content in existing_content:
                    content_id = content.get("content_id")
                    if content_id:
                        delete_response = requests.delete(
                            f"{BASE_URL}/creators/{self.creator_id}/premium-content/{content_id}",
                            headers=headers
                        )
                        print(f"   Cleaned up existing content: {content_id}")
        except Exception as e:
            print(f"   Cleanup warning: {str(e)}")
        
        # Verify we start with 0
        time.sleep(1)
        initial_count = self.test_initial_stats_endpoints()
        initial_stats, initial_earnings = self.test_creator_stats_endpoint()
        
        if initial_count == 0 and initial_stats == 0:
            self.log_result("Zero-to-One - Initial State", True, "Starting with 0 premium content as expected")
        else:
            self.log_result("Zero-to-One - Initial State", False, f"Expected 0, got Count: {initial_count}, Stats: {initial_stats}")
        
        # Upload one premium content
        content_id = self.upload_premium_content(" - Zero to One Test")
        if not content_id:
            self.log_result("Zero-to-One - Upload", False, "Failed to upload test content")
            return
        
        # Verify it shows 1
        time.sleep(2)
        final_count = self.test_initial_stats_endpoints()
        final_stats, final_earnings = self.test_creator_stats_endpoint()
        
        success = (final_count == 1 and final_stats == 1)
        if success:
            self.log_result("Zero-to-One - Final Verification", True, 
                          f"✅ SUCCESS! Counter now shows 1 (Count: {final_count}, Stats: {final_stats}) instead of 0")
        else:
            self.log_result("Zero-to-One - Final Verification", False, 
                          f"❌ ISSUE PERSISTS! Expected 1, got Count: {final_count}, Stats: {final_stats}")

    def cleanup_test_content(self):
        """Clean up test content"""
        print("🧹 Cleaning up test content...")
        
        headers = {"Authorization": f"Bearer {self.creator_token}"}
        
        for content_id in self.uploaded_content_ids:
            try:
                response = requests.delete(
                    f"{BASE_URL}/creators/{self.creator_id}/premium-content/{content_id}",
                    headers=headers
                )
                if response.status_code == 200:
                    print(f"   ✅ Cleaned up content: {content_id}")
                else:
                    print(f"   ⚠️ Failed to clean up content: {content_id}")
            except Exception as e:
                print(f"   ⚠️ Cleanup error for {content_id}: {str(e)}")

    def run_all_tests(self):
        """Run all premium content counter tests"""
        print("🚀 Starting Premium Content Counter Fix Testing")
        print("=" * 70)
        print("Focus: Testing dashboard premium content counter fix")
        print("Issue: Counter showing '0' when it should show '1'")
        print("=" * 70)
        
        # Setup
        if not self.setup_test_creator():
            print("❌ Failed to setup test creator. Aborting tests.")
            return
        
        # Run tests in order
        self.test_initial_stats_endpoints()
        self.test_creator_stats_endpoint()
        self.test_stats_refresh_after_upload()
        self.test_real_time_stats_updates()
        self.test_cross_verification()
        self.test_dashboard_stats_persistence()
        
        # Main test - the specific issue
        self.test_zero_to_one_scenario()
        
        # Cleanup
        self.cleanup_test_content()
        
        # Summary
        self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 70)
        print("🎯 PREMIUM CONTENT COUNTER FIX TESTING SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        print()
        
        # Critical test results
        critical_tests = [
            "Zero-to-One - Final Verification",
            "Stats Refresh After Upload", 
            "Cross-Verification - Count Consistency",
            "Real-time Update - Upload"
        ]
        
        print("🔍 CRITICAL TEST RESULTS:")
        for test_name in critical_tests:
            result = next((r for r in self.results if test_name in r["test"]), None)
            if result:
                print(f"   {result['status']}: {result['test']}")
                if result['details']:
                    print(f"      {result['details']}")
        print()
        
        # Overall assessment
        zero_to_one_result = next((r for r in self.results if "Zero-to-One - Final Verification" in r["test"]), None)
        
        if zero_to_one_result and zero_to_one_result["success"]:
            print("🎉 SUCCESS: Premium content counter fix is working! Dashboard now shows correct count.")
        elif zero_to_one_result and not zero_to_one_result["success"]:
            print("🚨 ISSUE PERSISTS: Premium content counter still showing '0' when it should show '1'.")
        else:
            print("⚠️ INCONCLUSIVE: Could not complete the main zero-to-one test.")
        
        if success_rate >= 90:
            print("✅ EXCELLENT: Premium content counter system is working excellently!")
        elif success_rate >= 75:
            print("✅ GOOD: Premium content counter system is working well with minor issues.")
        elif success_rate >= 50:
            print("⚠️ MODERATE: Premium content counter system has some significant issues.")
        else:
            print("🚨 CRITICAL: Premium content counter system has major issues requiring immediate attention.")
        
        print("=" * 70)

if __name__ == "__main__":
    tester = PremiumContentCounterTester()
    tester.run_all_tests()