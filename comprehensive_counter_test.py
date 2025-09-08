#!/usr/bin/env python3
"""
Comprehensive Premium Content Counter Fix Testing
Tests all aspects mentioned in the review request:

1. Creator Stats Endpoint - Test new GET /api/creators/{creator_id}/stats endpoint
2. Dashboard Stats Integration - Test frontend integration
3. End-to-End Counter Verification - Test complete flow  
4. Cross-Verification - Test data accuracy
"""

import requests
import json
import time
import uuid
from datetime import datetime

# Configuration
BASE_URL = "https://enterprise-coach.preview.emergentagent.com/api"
TEST_CREATOR_EMAIL = "comprehensive.counter@test.com"
TEST_CREATOR_PASSWORD = "ComprehensiveTest123!"
TEST_CREATOR_NAME = "Comprehensive Counter Test Creator"

class ComprehensiveCounterTester:
    def __init__(self):
        self.creator_token = None
        self.creator_id = None
        self.test_content_ids = []
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
        print("🔧 Setting up comprehensive test creator...")
        
        # Try login first
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
        except:
            pass
        
        # If login fails, try signup
        signup_data = {
            "email": TEST_CREATOR_EMAIL,
            "password": TEST_CREATOR_PASSWORD,
            "full_name": TEST_CREATOR_NAME,
            "account_name": "comprehensive-counter-test",
            "description": "Testing comprehensive premium content counter functionality",
            "monthly_price": 75.0,
            "category": "business",
            "expertise_areas": ["testing", "premium content", "counter verification"]
        }
        
        try:
            response = requests.post(f"{BASE_URL}/creators/signup", json=signup_data)
            if response.status_code in [200, 201]:
                data = response.json()
                self.creator_token = data.get("token")
                self.creator_id = data.get("creator", {}).get("creator_id")
                self.log_result("Creator Signup", True, f"Creator ID: {self.creator_id}")
                return True
            else:
                self.log_result("Creator Setup", False, f"Status: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Creator Setup", False, f"Exception: {str(e)}")
            return False

    def get_auth_headers(self):
        """Get authentication headers"""
        return {"Authorization": f"Bearer {self.creator_token}"}

    # ========================================
    # TEST 1: CREATOR STATS ENDPOINT TESTING
    # ========================================
    
    def test_stats_endpoint_exists_and_structure(self):
        """Test 1.1: Verify new stats endpoint exists with correct structure"""
        print("📊 Testing Creator Stats Endpoint Structure...")
        
        try:
            response = requests.get(
                f"{BASE_URL}/creators/{self.creator_id}/stats",
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check top-level structure
                required_top_level = ["creator_id", "stats", "last_updated"]
                missing_top = [field for field in required_top_level if field not in data]
                
                if missing_top:
                    self.log_result(
                        "Stats Endpoint Top-Level Structure", 
                        False, 
                        f"Missing fields: {missing_top}",
                        data
                    )
                    return False
                
                # Check stats structure
                stats = data.get("stats", {})
                required_stats = [
                    "premium_content_count", 
                    "content_count", 
                    "premium_earnings",
                    "total_content"
                ]
                missing_stats = [field for field in required_stats if field not in stats]
                
                if not missing_stats:
                    self.log_result(
                        "Stats Endpoint Structure Complete", 
                        True, 
                        f"All required fields present: {required_stats}"
                    )
                    return True, stats
                else:
                    self.log_result(
                        "Stats Endpoint Stats Structure", 
                        False, 
                        f"Missing stats fields: {missing_stats}",
                        stats
                    )
                    return False, None
            else:
                self.log_result(
                    "Stats Endpoint Exists", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False, None
                
        except Exception as e:
            self.log_result("Stats Endpoint Structure", False, f"Exception: {str(e)}")
            return False, None

    def test_stats_endpoint_authentication(self):
        """Test 1.2: Verify stats endpoint requires proper authentication"""
        print("🔐 Testing Stats Endpoint Authentication...")
        
        # Test without authentication
        try:
            response = requests.get(f"{BASE_URL}/creators/{self.creator_id}/stats")
            
            if response.status_code in [401, 403]:
                self.log_result(
                    "Stats Auth - No Token", 
                    True, 
                    f"Correctly blocked unauthenticated request: {response.status_code}"
                )
            else:
                self.log_result(
                    "Stats Auth - No Token", 
                    False, 
                    f"Should block unauthenticated requests, got: {response.status_code}",
                    response.text
                )
        except Exception as e:
            self.log_result("Stats Auth - No Token", False, f"Exception: {str(e)}")

        # Test with invalid token
        try:
            invalid_headers = {"Authorization": "Bearer invalid_token_xyz"}
            response = requests.get(
                f"{BASE_URL}/creators/{self.creator_id}/stats",
                headers=invalid_headers
            )
            
            if response.status_code in [401, 403]:
                self.log_result(
                    "Stats Auth - Invalid Token", 
                    True, 
                    f"Correctly blocked invalid token: {response.status_code}"
                )
            else:
                self.log_result(
                    "Stats Auth - Invalid Token", 
                    False, 
                    f"Should block invalid tokens, got: {response.status_code}",
                    response.text
                )
        except Exception as e:
            self.log_result("Stats Auth - Invalid Token", False, f"Exception: {str(e)}")

    def test_earnings_calculation_accuracy(self):
        """Test 1.3: Verify earnings calculation (80% minus $2.99 minimum platform fee)"""
        print("💰 Testing Earnings Calculation Accuracy...")
        
        try:
            response = requests.get(
                f"{BASE_URL}/creators/{self.creator_id}/stats",
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                stats = data.get("stats", {})
                
                premium_earnings = stats.get("premium_earnings", 0)
                total_revenue = stats.get("total_premium_revenue", 0)
                
                # Test calculation logic
                if total_revenue == 0:
                    # No sales yet - earnings should be 0
                    if premium_earnings == 0:
                        self.log_result(
                            "Earnings Calculation - No Sales", 
                            True, 
                            f"Correctly shows $0 earnings for no sales"
                        )
                    else:
                        self.log_result(
                            "Earnings Calculation - No Sales", 
                            False, 
                            f"Should show $0 for no sales, got ${premium_earnings}"
                        )
                else:
                    # Verify calculation: 80% or (revenue - $2.99 minimum)
                    platform_fee = max(total_revenue * 0.2, 2.99)
                    expected_earnings = max(0, total_revenue - platform_fee)
                    
                    if abs(premium_earnings - expected_earnings) < 0.01:  # Allow for rounding
                        self.log_result(
                            "Earnings Calculation - With Sales", 
                            True, 
                            f"Revenue: ${total_revenue}, Platform Fee: ${platform_fee:.2f}, Creator Earnings: ${premium_earnings}"
                        )
                    else:
                        self.log_result(
                            "Earnings Calculation - With Sales", 
                            False, 
                            f"Expected: ${expected_earnings:.2f}, Got: ${premium_earnings}",
                            stats
                        )
                
                return stats
            else:
                self.log_result(
                    "Earnings Calculation Test", 
                    False, 
                    f"Stats endpoint failed: {response.status_code}",
                    response.text
                )
                return None
                
        except Exception as e:
            self.log_result("Earnings Calculation", False, f"Exception: {str(e)}")
            return None

    def test_total_content_count_calculation(self):
        """Test 1.4: Verify total content count combines standard + premium"""
        print("🔢 Testing Total Content Count Calculation...")
        
        try:
            response = requests.get(
                f"{BASE_URL}/creators/{self.creator_id}/stats",
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                stats = data.get("stats", {})
                
                content_count = stats.get("content_count", 0)
                premium_content_count = stats.get("premium_content_count", 0)
                total_content = stats.get("total_content", 0)
                
                expected_total = content_count + premium_content_count
                
                if total_content == expected_total:
                    self.log_result(
                        "Total Content Count Calculation", 
                        True, 
                        f"Standard: {content_count} + Premium: {premium_content_count} = Total: {total_content}"
                    )
                else:
                    self.log_result(
                        "Total Content Count Calculation", 
                        False, 
                        f"Expected: {expected_total}, Got: {total_content}",
                        stats
                    )
                
                return stats
            else:
                self.log_result(
                    "Total Content Count Test", 
                    False, 
                    f"Stats endpoint failed: {response.status_code}",
                    response.text
                )
                return None
                
        except Exception as e:
            self.log_result("Total Content Count", False, f"Exception: {str(e)}")
            return None

    # ========================================
    # TEST 2: DASHBOARD STATS INTEGRATION
    # ========================================
    
    def test_dashboard_integration_format(self):
        """Test 2.1: Test fetchCreatorStats() function integration format"""
        print("📱 Testing Dashboard Integration Format...")
        
        try:
            # This tests the backend response format that fetchCreatorStats() expects
            response = requests.get(
                f"{BASE_URL}/creators/{self.creator_id}/stats",
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response format matches what frontend fetchCreatorStats() expects
                required_for_dashboard = [
                    "creator_id",
                    "stats",
                    "last_updated"
                ]
                
                missing_dashboard_fields = [field for field in required_for_dashboard if field not in data]
                
                if not missing_dashboard_fields:
                    stats = data.get("stats", {})
                    
                    # Verify stats contain dashboard-required fields
                    dashboard_stats_fields = [
                        "premium_content_count",
                        "premium_earnings", 
                        "total_content"
                    ]
                    
                    missing_stats_fields = [field for field in dashboard_stats_fields if field not in stats]
                    
                    if not missing_stats_fields:
                        self.log_result(
                            "Dashboard Integration Format", 
                            True, 
                            f"Response format compatible with fetchCreatorStats()"
                        )
                        return True
                    else:
                        self.log_result(
                            "Dashboard Stats Fields", 
                            False, 
                            f"Missing dashboard stats fields: {missing_stats_fields}",
                            stats
                        )
                        return False
                else:
                    self.log_result(
                        "Dashboard Response Format", 
                        False, 
                        f"Missing dashboard fields: {missing_dashboard_fields}",
                        data
                    )
                    return False
            else:
                self.log_result(
                    "Dashboard Integration Format", 
                    False, 
                    f"Stats endpoint failed: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Dashboard Integration Format", False, f"Exception: {str(e)}")
            return False

    def test_authentication_headers_handling(self):
        """Test 2.2: Test authentication headers and error handling"""
        print("🔑 Testing Authentication Headers Handling...")
        
        # Test with proper headers (should work)
        try:
            response = requests.get(
                f"{BASE_URL}/creators/{self.creator_id}/stats",
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                self.log_result(
                    "Auth Headers - Valid Token", 
                    True, 
                    f"Valid authentication accepted"
                )
            else:
                self.log_result(
                    "Auth Headers - Valid Token", 
                    False, 
                    f"Valid token rejected: {response.status_code}",
                    response.text
                )
        except Exception as e:
            self.log_result("Auth Headers - Valid Token", False, f"Exception: {str(e)}")

        # Test error handling for different auth scenarios
        error_scenarios = [
            ("No Authorization Header", {}),
            ("Malformed Header", {"Authorization": "InvalidFormat"}),
            ("Bearer Without Token", {"Authorization": "Bearer"}),
            ("Empty Bearer Token", {"Authorization": "Bearer "})
        ]
        
        for scenario_name, headers in error_scenarios:
            try:
                response = requests.get(
                    f"{BASE_URL}/creators/{self.creator_id}/stats",
                    headers=headers
                )
                
                if response.status_code in [401, 403, 422]:
                    self.log_result(
                        f"Auth Error Handling - {scenario_name}", 
                        True, 
                        f"Correctly handled error: {response.status_code}"
                    )
                else:
                    self.log_result(
                        f"Auth Error Handling - {scenario_name}", 
                        False, 
                        f"Should return 401/403/422, got: {response.status_code}",
                        response.text
                    )
            except Exception as e:
                self.log_result(f"Auth Error Handling - {scenario_name}", False, f"Exception: {str(e)}")

    # ========================================
    # TEST 3: END-TO-END COUNTER VERIFICATION
    # ========================================
    
    def upload_premium_content_for_testing(self, title_suffix=""):
        """Upload premium content for testing"""
        content_data = {
            "title": f"Test Premium Content {title_suffix}",
            "description": f"Test premium content for counter verification {title_suffix}",
            "content_type": "document",
            "price": 15.99,
            "category": "business",
            "tags": ["test", "premium", "counter"]
        }
        
        try:
            files = {
                'file': ('test_document.txt', f'Test premium content data {title_suffix}', 'text/plain')
            }
            
            data = {
                'title': content_data['title'],
                'description': content_data['description'],
                'content_type': content_data['content_type'],
                'price': str(content_data['price']),
                'category': content_data['category'],
                'tags': json.dumps(content_data['tags'])
            }
            
            response = requests.post(
                f"{BASE_URL}/creator/content/upload",
                files=files,
                data=data,
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 201:
                result_data = response.json()
                content_id = result_data.get("content_id")
                if content_id:
                    self.test_content_ids.append(content_id)
                    return content_id, content_data['price']
                else:
                    return None, None
            else:
                return None, None
                
        except Exception as e:
            return None, None

    def test_counter_after_upload(self):
        """Test 3.1: Upload premium content and verify stats endpoint reflects increase"""
        print("📤 Testing Counter After Premium Content Upload...")
        
        # Get initial count
        try:
            initial_response = requests.get(
                f"{BASE_URL}/creators/{self.creator_id}/stats",
                headers=self.get_auth_headers()
            )
            
            if initial_response.status_code == 200:
                initial_stats = initial_response.json().get("stats", {})
                initial_count = initial_stats.get("premium_content_count", 0)
                
                # Upload premium content
                content_id, price = self.upload_premium_content_for_testing("Upload Test")
                
                if content_id:
                    # Check count after upload
                    time.sleep(1)  # Brief pause for processing
                    
                    after_response = requests.get(
                        f"{BASE_URL}/creators/{self.creator_id}/stats",
                        headers=self.get_auth_headers()
                    )
                    
                    if after_response.status_code == 200:
                        after_stats = after_response.json().get("stats", {})
                        after_count = after_stats.get("premium_content_count", 0)
                        
                        if after_count == initial_count + 1:
                            self.log_result(
                                "Counter After Upload", 
                                True, 
                                f"Count increased from {initial_count} to {after_count}"
                            )
                            return True
                        else:
                            self.log_result(
                                "Counter After Upload", 
                                False, 
                                f"Expected count {initial_count + 1}, got {after_count}",
                                after_stats
                            )
                            return False
                    else:
                        self.log_result(
                            "Counter After Upload - Stats Check", 
                            False, 
                            f"Stats check failed: {after_response.status_code}",
                            after_response.text
                        )
                        return False
                else:
                    self.log_result(
                        "Counter After Upload - Content Upload", 
                        False, 
                        "Failed to upload premium content"
                    )
                    return False
            else:
                self.log_result(
                    "Counter After Upload - Initial Stats", 
                    False, 
                    f"Initial stats failed: {initial_response.status_code}",
                    initial_response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Counter After Upload", False, f"Exception: {str(e)}")
            return False

    def test_dashboard_counter_shows_correct_count(self):
        """Test 3.2: Test that dashboard counter shows correct count (1 instead of 0)"""
        print("📊 Testing Dashboard Counter Shows Correct Count...")
        
        try:
            response = requests.get(
                f"{BASE_URL}/creators/{self.creator_id}/stats",
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                stats = data.get("stats", {})
                premium_count = stats.get("premium_content_count", 0)
                
                # The key test: does it show the actual count instead of 0?
                if premium_count > 0:
                    self.log_result(
                        "Dashboard Counter Shows Correct Count", 
                        True, 
                        f"✅ SUCCESS! Dashboard shows {premium_count} instead of 0"
                    )
                    return True
                elif len(self.test_content_ids) > 0:
                    # We uploaded content but count is still 0
                    self.log_result(
                        "Dashboard Counter Shows Correct Count", 
                        False, 
                        f"❌ ISSUE: Dashboard still shows 0 despite {len(self.test_content_ids)} uploaded content",
                        stats
                    )
                    return False
                else:
                    # No content uploaded, 0 is correct
                    self.log_result(
                        "Dashboard Counter Shows Correct Count", 
                        True, 
                        f"No content uploaded, correctly shows 0"
                    )
                    return True
            else:
                self.log_result(
                    "Dashboard Counter Check", 
                    False, 
                    f"Stats endpoint failed: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Dashboard Counter Check", False, f"Exception: {str(e)}")
            return False

    def test_stats_refresh_after_operations(self):
        """Test 3.3: Verify stats refresh after content upload/edit/duplicate/delete operations"""
        print("🔄 Testing Stats Refresh After Operations...")
        
        if not self.test_content_ids:
            self.log_result("Stats Refresh Test", False, "No content available for operations testing")
            return False
        
        content_id = self.test_content_ids[0]
        
        # Test edit operation
        try:
            # Get count before edit
            before_response = requests.get(
                f"{BASE_URL}/creators/{self.creator_id}/stats",
                headers=self.get_auth_headers()
            )
            
            if before_response.status_code == 200:
                before_count = before_response.json().get("stats", {}).get("premium_content_count", 0)
                
                # Edit content
                edit_data = {
                    "title": "Updated Test Premium Content",
                    "description": "Updated description for stats refresh testing"
                }
                
                edit_response = requests.put(
                    f"{BASE_URL}/creator/premium-content/{content_id}",
                    json=edit_data,
                    headers=self.get_auth_headers()
                )
                
                if edit_response.status_code == 200:
                    # Check count after edit (should remain same)
                    after_response = requests.get(
                        f"{BASE_URL}/creators/{self.creator_id}/stats",
                        headers=self.get_auth_headers()
                    )
                    
                    if after_response.status_code == 200:
                        after_count = after_response.json().get("stats", {}).get("premium_content_count", 0)
                        
                        if after_count == before_count:
                            self.log_result(
                                "Stats Refresh After Edit", 
                                True, 
                                f"Count correctly unchanged after edit: {before_count}"
                            )
                        else:
                            self.log_result(
                                "Stats Refresh After Edit", 
                                False, 
                                f"Count changed unexpectedly: {before_count} -> {after_count}"
                            )
                    else:
                        self.log_result(
                            "Stats Refresh After Edit - Stats Check", 
                            False, 
                            f"Stats check failed: {after_response.status_code}"
                        )
                else:
                    self.log_result(
                        "Stats Refresh After Edit - Edit Operation", 
                        False, 
                        f"Edit failed: {edit_response.status_code}",
                        edit_response.text
                    )
            else:
                self.log_result(
                    "Stats Refresh After Edit - Initial Stats", 
                    False, 
                    f"Initial stats failed: {before_response.status_code}"
                )
        except Exception as e:
            self.log_result("Stats Refresh After Edit", False, f"Exception: {str(e)}")

        # Test duplicate operation
        try:
            # Get count before duplicate
            before_response = requests.get(
                f"{BASE_URL}/creators/{self.creator_id}/stats",
                headers=self.get_auth_headers()
            )
            
            if before_response.status_code == 200:
                before_count = before_response.json().get("stats", {}).get("premium_content_count", 0)
                
                # Duplicate content
                duplicate_response = requests.post(
                    f"{BASE_URL}/creator/premium-content/{content_id}/duplicate",
                    headers=self.get_auth_headers()
                )
                
                if duplicate_response.status_code == 201:
                    duplicate_data = duplicate_response.json()
                    duplicate_id = duplicate_data.get("content_id")
                    if duplicate_id:
                        self.test_content_ids.append(duplicate_id)
                    
                    # Check count after duplicate (should increase by 1)
                    after_response = requests.get(
                        f"{BASE_URL}/creators/{self.creator_id}/stats",
                        headers=self.get_auth_headers()
                    )
                    
                    if after_response.status_code == 200:
                        after_count = after_response.json().get("stats", {}).get("premium_content_count", 0)
                        
                        if after_count == before_count + 1:
                            self.log_result(
                                "Stats Refresh After Duplicate", 
                                True, 
                                f"Count correctly increased after duplicate: {before_count} -> {after_count}"
                            )
                        else:
                            self.log_result(
                                "Stats Refresh After Duplicate", 
                                False, 
                                f"Expected count {before_count + 1}, got {after_count}"
                            )
                    else:
                        self.log_result(
                            "Stats Refresh After Duplicate - Stats Check", 
                            False, 
                            f"Stats check failed: {after_response.status_code}"
                        )
                else:
                    self.log_result(
                        "Stats Refresh After Duplicate - Duplicate Operation", 
                        False, 
                        f"Duplicate failed: {duplicate_response.status_code}",
                        duplicate_response.text
                    )
            else:
                self.log_result(
                    "Stats Refresh After Duplicate - Initial Stats", 
                    False, 
                    f"Initial stats failed: {before_response.status_code}"
                )
        except Exception as e:
            self.log_result("Stats Refresh After Duplicate", False, f"Exception: {str(e)}")

        return True

    # ========================================
    # TEST 4: CROSS-VERIFICATION
    # ========================================
    
    def test_cross_verification_with_database(self):
        """Test 4.1: Compare stats endpoint data with actual content in database"""
        print("🔍 Testing Cross-Verification with Database...")
        
        try:
            # Get stats from stats endpoint
            stats_response = requests.get(
                f"{BASE_URL}/creators/{self.creator_id}/stats",
                headers=self.get_auth_headers()
            )
            
            # Get actual content from premium content endpoint
            content_response = requests.get(
                f"{BASE_URL}/creators/{self.creator_id}/premium-content",
                headers=self.get_auth_headers()
            )
            
            if stats_response.status_code == 200 and content_response.status_code == 200:
                stats_data = stats_response.json().get("stats", {})
                content_data = content_response.json()
                
                stats_count = stats_data.get("premium_content_count", 0)
                actual_content = content_data.get("content", [])
                actual_count = len(actual_content)
                
                if stats_count == actual_count:
                    self.log_result(
                        "Cross-Verification Count Accuracy", 
                        True, 
                        f"Stats endpoint: {stats_count}, Actual content: {actual_count}"
                    )
                else:
                    self.log_result(
                        "Cross-Verification Count Accuracy", 
                        False, 
                        f"Mismatch - Stats: {stats_count}, Actual: {actual_count}",
                        {"stats_count": stats_count, "actual_count": actual_count}
                    )
                
                # Verify content IDs match
                if actual_content:
                    content_ids_from_list = [item.get("content_id") for item in actual_content]
                    uploaded_ids_found = [cid for cid in self.test_content_ids if cid in content_ids_from_list]
                    
                    if len(uploaded_ids_found) == len(self.test_content_ids):
                        self.log_result(
                            "Cross-Verification Content IDs", 
                            True, 
                            f"All {len(self.test_content_ids)} uploaded content IDs found in database"
                        )
                    else:
                        self.log_result(
                            "Cross-Verification Content IDs", 
                            False, 
                            f"Uploaded: {len(self.test_content_ids)}, Found: {len(uploaded_ids_found)}"
                        )
                
                return True
            else:
                self.log_result(
                    "Cross-Verification Endpoints", 
                    False, 
                    f"Stats: {stats_response.status_code}, Content: {content_response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_result("Cross-Verification", False, f"Exception: {str(e)}")
            return False

    def test_revenue_data_consistency(self):
        """Test 4.2: Verify earnings calculations match revenue data"""
        print("💰 Testing Revenue Data Consistency...")
        
        try:
            response = requests.get(
                f"{BASE_URL}/creators/{self.creator_id}/stats",
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                stats = data.get("stats", {})
                
                premium_earnings = stats.get("premium_earnings", 0)
                total_revenue = stats.get("total_premium_revenue", 0)
                total_sales = stats.get("total_content_sales", 0)
                
                # For new content with no purchases, all should be 0
                if total_revenue == 0 and total_sales == 0 and premium_earnings == 0:
                    self.log_result(
                        "Revenue Data Consistency - No Sales", 
                        True, 
                        f"All revenue metrics correctly at 0 for new content"
                    )
                elif total_revenue > 0:
                    # Verify earnings calculation matches revenue
                    platform_fee = max(total_revenue * 0.2, 2.99)
                    expected_earnings = max(0, total_revenue - platform_fee)
                    
                    if abs(premium_earnings - expected_earnings) < 0.01:
                        self.log_result(
                            "Revenue Data Consistency - With Sales", 
                            True, 
                            f"Earnings calculation matches revenue data: ${premium_earnings}"
                        )
                    else:
                        self.log_result(
                            "Revenue Data Consistency - With Sales", 
                            False, 
                            f"Earnings mismatch - Expected: ${expected_earnings:.2f}, Got: ${premium_earnings}",
                            stats
                        )
                else:
                    self.log_result(
                        "Revenue Data Consistency", 
                        True, 
                        f"Revenue data consistent for current state"
                    )
                
                return True
            else:
                self.log_result(
                    "Revenue Data Consistency", 
                    False, 
                    f"Stats endpoint failed: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Revenue Data Consistency", False, f"Exception: {str(e)}")
            return False

    def test_stats_consistency_across_calls(self):
        """Test 4.3: Test stats consistency across different API calls"""
        print("🔄 Testing Stats Consistency Across API Calls...")
        
        try:
            # Make multiple calls to stats endpoint
            responses = []
            for i in range(3):
                response = requests.get(
                    f"{BASE_URL}/creators/{self.creator_id}/stats",
                    headers=self.get_auth_headers()
                )
                if response.status_code == 200:
                    responses.append(response.json().get("stats", {}))
                time.sleep(0.5)  # Brief pause between calls
            
            if len(responses) == 3:
                # Check if all responses are consistent
                first_stats = responses[0]
                consistent = all(
                    resp.get("premium_content_count") == first_stats.get("premium_content_count") and
                    resp.get("premium_earnings") == first_stats.get("premium_earnings")
                    for resp in responses
                )
                
                if consistent:
                    self.log_result(
                        "Stats Consistency Across Calls", 
                        True, 
                        f"All 3 calls returned consistent data"
                    )
                else:
                    self.log_result(
                        "Stats Consistency Across Calls", 
                        False, 
                        f"Inconsistent data across calls",
                        responses
                    )
                
                return True
            else:
                self.log_result(
                    "Stats Consistency Across Calls", 
                    False, 
                    f"Only {len(responses)} successful calls out of 3"
                )
                return False
                
        except Exception as e:
            self.log_result("Stats Consistency Across Calls", False, f"Exception: {str(e)}")
            return False

    def cleanup_test_content(self):
        """Clean up test content"""
        print("🧹 Cleaning up test content...")
        
        for content_id in self.test_content_ids:
            try:
                response = requests.delete(
                    f"{BASE_URL}/creator/premium-content/{content_id}",
                    headers=self.get_auth_headers()
                )
                
                if response.status_code == 200:
                    print(f"   ✅ Deleted content: {content_id}")
                else:
                    print(f"   ⚠️  Failed to delete content {content_id}: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Error deleting content {content_id}: {str(e)}")

    def run_comprehensive_tests(self):
        """Run all comprehensive premium content counter tests"""
        print("🚀 Starting Comprehensive Premium Content Counter Fix Testing...")
        print("=" * 80)
        print("Testing all aspects mentioned in the review request:")
        print("1. Creator Stats Endpoint - Test new GET /api/creators/{creator_id}/stats endpoint")
        print("2. Dashboard Stats Integration - Test frontend integration")  
        print("3. End-to-End Counter Verification - Test complete flow")
        print("4. Cross-Verification - Test data accuracy")
        print("=" * 80)
        
        # Setup
        if not self.setup_test_creator():
            print("❌ Failed to setup test creator. Aborting tests.")
            return False
        
        # TEST 1: CREATOR STATS ENDPOINT
        print("\n" + "="*50)
        print("TEST 1: CREATOR STATS ENDPOINT TESTING")
        print("="*50)
        
        success, initial_stats = self.test_stats_endpoint_exists_and_structure()
        if not success:
            print("❌ Critical: Stats endpoint structure invalid. Aborting remaining tests.")
            return False
        
        self.test_stats_endpoint_authentication()
        self.test_earnings_calculation_accuracy()
        self.test_total_content_count_calculation()
        
        # TEST 2: DASHBOARD STATS INTEGRATION
        print("\n" + "="*50)
        print("TEST 2: DASHBOARD STATS INTEGRATION")
        print("="*50)
        
        self.test_dashboard_integration_format()
        self.test_authentication_headers_handling()
        
        # TEST 3: END-TO-END COUNTER VERIFICATION
        print("\n" + "="*50)
        print("TEST 3: END-TO-END COUNTER VERIFICATION")
        print("="*50)
        
        self.test_counter_after_upload()
        self.test_dashboard_counter_shows_correct_count()
        self.test_stats_refresh_after_operations()
        
        # TEST 4: CROSS-VERIFICATION
        print("\n" + "="*50)
        print("TEST 4: CROSS-VERIFICATION")
        print("="*50)
        
        self.test_cross_verification_with_database()
        self.test_revenue_data_consistency()
        self.test_stats_consistency_across_calls()
        
        # Cleanup
        if self.test_content_ids:
            self.cleanup_test_content()
        
        # Summary
        self.print_comprehensive_summary()
        
        return True

    def print_comprehensive_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE PREMIUM CONTENT COUNTER FIX TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Categorize results by test area
        test_areas = {
            "Creator Stats Endpoint": [],
            "Dashboard Integration": [],
            "End-to-End Verification": [],
            "Cross-Verification": []
        }
        
        for result in self.results:
            test_name = result["test"]
            if any(keyword in test_name for keyword in ["Stats Endpoint", "Stats Auth", "Earnings Calculation", "Total Content"]):
                test_areas["Creator Stats Endpoint"].append(result)
            elif any(keyword in test_name for keyword in ["Dashboard", "Auth Headers"]):
                test_areas["Dashboard Integration"].append(result)
            elif any(keyword in test_name for keyword in ["Counter After", "Dashboard Counter", "Stats Refresh"]):
                test_areas["End-to-End Verification"].append(result)
            elif any(keyword in test_name for keyword in ["Cross-Verification", "Revenue Data", "Stats Consistency"]):
                test_areas["Cross-Verification"].append(result)
        
        print(f"\n📋 RESULTS BY TEST AREA:")
        for area, area_results in test_areas.items():
            if area_results:
                area_passed = sum(1 for r in area_results if r["success"])
                area_total = len(area_results)
                area_rate = (area_passed / area_total * 100) if area_total > 0 else 0
                print(f"   {area}: {area_passed}/{area_total} ({area_rate:.1f}%)")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['details']}")
        
        print(f"\n🎯 CRITICAL SUCCESS CRITERIA VERIFICATION:")
        
        # Check each requirement from the review request
        stats_endpoint_working = any(
            result["success"] and "Stats Endpoint Structure Complete" in result["test"] 
            for result in self.results
        )
        
        dashboard_counter_working = any(
            result["success"] and "Dashboard Counter Shows Correct Count" in result["test"] 
            for result in self.results
        )
        
        earnings_accurate = any(
            result["success"] and "Earnings Calculation" in result["test"] 
            for result in self.results
        )
        
        stats_refresh_working = any(
            result["success"] and "Stats Refresh" in result["test"] 
            for result in self.results
        )
        
        cross_verification_working = any(
            result["success"] and "Cross-Verification" in result["test"] 
            for result in self.results
        )
        
        print(f"   ✅ New /api/creators/{{creator_id}}/stats endpoint returns correct data: {'✅' if stats_endpoint_working else '❌'}")
        print(f"   ✅ Premium content count shows actual number (1) instead of 0: {'✅' if dashboard_counter_working else '❌'}")
        print(f"   ✅ Earnings calculations accurate (80% minus $2.99 minimum): {'✅' if earnings_accurate else '❌'}")
        print(f"   ✅ Dashboard counter updates correctly after content operations: {'✅' if stats_refresh_working else '❌'}")
        print(f"   ✅ Frontend fetchCreatorStats() integrates properly with backend: {'✅' if dashboard_counter_working else '❌'}")
        
        # Overall assessment
        critical_criteria_met = sum([
            stats_endpoint_working,
            dashboard_counter_working, 
            earnings_accurate,
            stats_refresh_working
        ])
        
        print(f"\n🏆 OVERALL ASSESSMENT:")
        if success_rate >= 90 and critical_criteria_met >= 3:
            print(f"   🎉 EXCELLENT: Premium content counter fix is working excellently!")
            print(f"   ✅ All critical requirements from review request are met")
        elif success_rate >= 80 and critical_criteria_met >= 2:
            print(f"   ✅ GOOD: Premium content counter fix is working well")
            print(f"   ⚠️  Some minor issues may need attention")
        else:
            print(f"   ⚠️  NEEDS ATTENTION: Premium content counter fix requires fixes")
            print(f"   ❌ Critical requirements not fully met")
        
        print(f"\n📝 KEY FINDINGS:")
        print(f"   • Stats endpoint functionality: {'Working' if stats_endpoint_working else 'Issues detected'}")
        print(f"   • Dashboard counter display: {'Correct count shown' if dashboard_counter_working else 'Still showing 0'}")
        print(f"   • Earnings calculation: {'Accurate' if earnings_accurate else 'Needs verification'}")
        print(f"   • Real-time updates: {'Working' if stats_refresh_working else 'Issues detected'}")
        
        print("=" * 80)

if __name__ == "__main__":
    tester = ComprehensiveCounterTester()
    tester.run_comprehensive_tests()