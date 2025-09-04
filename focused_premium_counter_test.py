#!/usr/bin/env python3
"""
Focused Premium Content Counter Testing
Direct testing of premium content counter endpoints without creator setup
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "https://multi-tenant-ai.preview.emergentagent.com/api"
EXISTING_CREATOR_ID = "creator_fee1ffa3ece5"  # From logs

class FocusedPremiumCounterTester:
    def __init__(self):
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

    def test_standard_content_endpoint(self):
        """Test GET /api/creators/{creator_id}/content for standard content count"""
        print("📊 Testing Standard Content Endpoint...")
        
        try:
            response = requests.get(f"{BASE_URL}/creators/{EXISTING_CREATOR_ID}/content")
            if response.status_code == 200:
                data = response.json()
                content_list = data.get("content", [])
                total_count = data.get("total", len(content_list))
                
                self.log_result("Standard Content Endpoint", True, 
                              f"Standard content count: {len(content_list)}, Total: {total_count}")
                return len(content_list)
            else:
                self.log_result("Standard Content Endpoint", False, 
                              f"Status: {response.status_code}", response.text[:200])
                return 0
        except Exception as e:
            self.log_result("Standard Content Endpoint", False, f"Exception: {str(e)}")
            return 0

    def test_premium_content_endpoint(self):
        """Test GET /api/creators/{creator_id}/premium-content for premium content count"""
        print("💎 Testing Premium Content Endpoint...")
        
        try:
            response = requests.get(f"{BASE_URL}/creators/{EXISTING_CREATOR_ID}/premium-content")
            if response.status_code == 200:
                data = response.json()
                content_list = data.get("content", [])
                total_count = data.get("total", len(content_list))
                
                # Calculate total revenue and earnings
                total_revenue = sum(c.get("total_revenue", 0) for c in content_list)
                creator_earnings = sum(c.get("creator_earnings", 0) for c in content_list)
                
                self.log_result("Premium Content Endpoint", True, 
                              f"Premium content count: {len(content_list)}, Total: {total_count}, Revenue: ${total_revenue}, Earnings: ${creator_earnings}")
                return len(content_list), total_revenue, creator_earnings
            else:
                self.log_result("Premium Content Endpoint", False, 
                              f"Status: {response.status_code}", response.text[:200])
                return 0, 0, 0
        except Exception as e:
            self.log_result("Premium Content Endpoint", False, f"Exception: {str(e)}")
            return 0, 0, 0

    def test_creator_stats_endpoint(self):
        """Test creator stats endpoint that should include premium content count"""
        print("📈 Testing Creator Stats Endpoint...")
        
        try:
            response = requests.get(f"{BASE_URL}/creators/{EXISTING_CREATOR_ID}/stats")
            if response.status_code == 200:
                data = response.json()
                stats = data.get("stats", {})
                
                premium_count = stats.get("premium_content_count", 0)
                premium_earnings = stats.get("premium_earnings", 0)
                total_sales = stats.get("total_sales", 0)
                
                self.log_result("Creator Stats Endpoint", True, 
                              f"Stats - Premium count: {premium_count}, Earnings: ${premium_earnings}, Sales: {total_sales}")
                return premium_count, premium_earnings, total_sales
            else:
                self.log_result("Creator Stats Endpoint", False, 
                              f"Status: {response.status_code}", response.text[:200])
                return 0, 0, 0
        except Exception as e:
            self.log_result("Creator Stats Endpoint", False, f"Exception: {str(e)}")
            return 0, 0, 0

    def test_premium_content_discovery(self):
        """Test premium content discovery endpoint (public view)"""
        print("🔍 Testing Premium Content Discovery Endpoint...")
        
        try:
            response = requests.get(f"{BASE_URL}/mentor/{EXISTING_CREATOR_ID}/premium-content")
            if response.status_code == 200:
                data = response.json()
                content_list = data.get("content", [])
                
                self.log_result("Premium Content Discovery", True, 
                              f"Discovery endpoint shows {len(content_list)} premium content items")
                return len(content_list)
            else:
                self.log_result("Premium Content Discovery", False, 
                              f"Status: {response.status_code}", response.text[:200])
                return 0
        except Exception as e:
            self.log_result("Premium Content Discovery", False, f"Exception: {str(e)}")
            return 0

    def test_cross_verification(self):
        """Test data consistency between all endpoints"""
        print("🔍 Testing Cross-Verification - Data Consistency...")
        
        # Get counts from all endpoints
        standard_count = self.test_standard_content_endpoint()
        premium_count, premium_revenue, premium_earnings = self.test_premium_content_endpoint()
        stats_count, stats_earnings, stats_sales = self.test_creator_stats_endpoint()
        discovery_count = self.test_premium_content_discovery()
        
        # Verify premium content count consistency
        premium_counts_match = (premium_count == stats_count == discovery_count)
        
        if premium_counts_match:
            self.log_result("Cross-Verification - Premium Count Consistency", True, 
                          f"All endpoints show consistent premium count: {premium_count}")
        else:
            self.log_result("Cross-Verification - Premium Count Consistency", False, 
                          f"Inconsistent counts - Premium: {premium_count}, Stats: {stats_count}, Discovery: {discovery_count}")
        
        # Verify earnings consistency
        earnings_match = abs(premium_earnings - stats_earnings) < 0.01  # Allow small floating point differences
        
        if earnings_match:
            self.log_result("Cross-Verification - Earnings Consistency", True, 
                          f"Earnings consistent: Premium=${premium_earnings}, Stats=${stats_earnings}")
        else:
            self.log_result("Cross-Verification - Earnings Consistency", False, 
                          f"Earnings mismatch - Premium: ${premium_earnings}, Stats: ${stats_earnings}")
        
        # Test the main issue: Is premium count > 0 when content exists?
        if premium_count > 0:
            self.log_result("Main Issue Check - Premium Count > 0", True, 
                          f"✅ Premium content counter shows {premium_count} (not 0)")
        else:
            self.log_result("Main Issue Check - Premium Count > 0", False, 
                          f"❌ Premium content counter shows 0 (this is the reported issue)")
        
        return {
            "standard_count": standard_count,
            "premium_count": premium_count,
            "stats_count": stats_count,
            "discovery_count": discovery_count,
            "premium_earnings": premium_earnings,
            "stats_earnings": stats_earnings
        }

    def test_earnings_calculation(self):
        """Test premium earnings calculation (80% of revenue minus $2.99 platform fee)"""
        print("💰 Testing Premium Earnings Calculation...")
        
        try:
            response = requests.get(f"{BASE_URL}/creators/{EXISTING_CREATOR_ID}/premium-content")
            if response.status_code != 200:
                self.log_result("Earnings Calculation", False, "Could not fetch premium content")
                return
            
            data = response.json()
            content_list = data.get("content", [])
            
            if not content_list:
                self.log_result("Earnings Calculation", True, "No premium content to test earnings calculation")
                return
            
            total_calculated_earnings = 0
            for content in content_list:
                price = content.get("price", 0)
                total_purchases = content.get("total_purchases", 0)
                total_revenue = content.get("total_revenue", 0)
                creator_earnings = content.get("creator_earnings", 0)
                
                # Calculate expected earnings: 80% of revenue OR revenue minus $2.99 (whichever is higher)
                expected_earnings_80_percent = total_revenue * 0.8
                expected_earnings_minus_fee = max(0, total_revenue - 2.99)
                expected_earnings = max(expected_earnings_80_percent, expected_earnings_minus_fee)
                
                total_calculated_earnings += expected_earnings
                
                # Check if individual content earnings are correct
                earnings_correct = abs(creator_earnings - expected_earnings) < 0.01
                
                if earnings_correct:
                    self.log_result(f"Earnings Calculation - Content {content.get('content_id', 'Unknown')[:8]}", True, 
                                  f"Price: ${price}, Revenue: ${total_revenue}, Expected: ${expected_earnings:.2f}, Actual: ${creator_earnings:.2f}")
                else:
                    self.log_result(f"Earnings Calculation - Content {content.get('content_id', 'Unknown')[:8]}", False, 
                                  f"Price: ${price}, Revenue: ${total_revenue}, Expected: ${expected_earnings:.2f}, Actual: ${creator_earnings:.2f}")
            
            # Verify total earnings
            stats_response = requests.get(f"{BASE_URL}/creators/{EXISTING_CREATOR_ID}/stats")
            if stats_response.status_code == 200:
                stats_data = stats_response.json()
                stats_earnings = stats_data.get("stats", {}).get("premium_earnings", 0)
                
                total_earnings_correct = abs(stats_earnings - total_calculated_earnings) < 0.01
                
                if total_earnings_correct:
                    self.log_result("Earnings Calculation - Total", True, 
                                  f"Total earnings correct: Expected=${total_calculated_earnings:.2f}, Stats=${stats_earnings:.2f}")
                else:
                    self.log_result("Earnings Calculation - Total", False, 
                                  f"Total earnings mismatch: Expected=${total_calculated_earnings:.2f}, Stats=${stats_earnings:.2f}")
            
        except Exception as e:
            self.log_result("Earnings Calculation", False, f"Exception: {str(e)}")

    def test_endpoint_response_structure(self):
        """Test that all endpoints return proper response structure"""
        print("🏗️ Testing Endpoint Response Structure...")
        
        endpoints = [
            (f"/creators/{EXISTING_CREATOR_ID}/content", "Standard Content"),
            (f"/creators/{EXISTING_CREATOR_ID}/premium-content", "Premium Content"),
            (f"/creators/{EXISTING_CREATOR_ID}/stats", "Creator Stats"),
            (f"/mentor/{EXISTING_CREATOR_ID}/premium-content", "Premium Discovery")
        ]
        
        for endpoint, name in endpoints:
            try:
                response = requests.get(f"{BASE_URL}{endpoint}")
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check basic structure
                    if "content" in endpoint and "stats" not in endpoint:
                        has_content = "content" in data
                        content_is_list = isinstance(data.get("content", []), list)
                        
                        if has_content and content_is_list:
                            self.log_result(f"Response Structure - {name}", True, 
                                          f"Proper structure with content array ({len(data.get('content', []))} items)")
                        else:
                            self.log_result(f"Response Structure - {name}", False, 
                                          f"Missing or invalid content structure")
                    
                    elif "stats" in endpoint:
                        has_stats = "stats" in data
                        stats_is_dict = isinstance(data.get("stats", {}), dict)
                        
                        if has_stats and stats_is_dict:
                            stats = data.get("stats", {})
                            has_premium_count = "premium_content_count" in stats
                            has_premium_earnings = "premium_earnings" in stats
                            
                            if has_premium_count and has_premium_earnings:
                                self.log_result(f"Response Structure - {name}", True, 
                                              f"Proper stats structure with premium fields")
                            else:
                                self.log_result(f"Response Structure - {name}", False, 
                                              f"Missing premium fields in stats")
                        else:
                            self.log_result(f"Response Structure - {name}", False, 
                                          f"Missing or invalid stats structure")
                else:
                    self.log_result(f"Response Structure - {name}", False, 
                                  f"HTTP {response.status_code}")
            except Exception as e:
                self.log_result(f"Response Structure - {name}", False, f"Exception: {str(e)}")

    def run_all_tests(self):
        """Run all focused premium content counter tests"""
        print("🚀 Starting Focused Premium Content Counter Testing")
        print("=" * 70)
        print(f"Testing Creator: {EXISTING_CREATOR_ID}")
        print("Focus: Verifying premium content counter shows correct count")
        print("=" * 70)
        
        # Run tests
        self.test_endpoint_response_structure()
        results = self.test_cross_verification()
        self.test_earnings_calculation()
        
        # Summary
        self.print_summary(results)

    def print_summary(self, results=None):
        """Print test summary"""
        print("\n" + "=" * 70)
        print("🎯 FOCUSED PREMIUM CONTENT COUNTER TESTING SUMMARY")
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
        
        # Key findings
        if results:
            print("🔍 KEY FINDINGS:")
            print(f"   📄 Standard Content Count: {results['standard_count']}")
            print(f"   💎 Premium Content Count: {results['premium_count']}")
            print(f"   📊 Stats Premium Count: {results['stats_count']}")
            print(f"   🔍 Discovery Premium Count: {results['discovery_count']}")
            print(f"   💰 Premium Earnings: ${results['premium_earnings']:.2f}")
            print(f"   📈 Stats Earnings: ${results['stats_earnings']:.2f}")
            print()
        
        # Critical test results
        main_issue_result = next((r for r in self.results if "Main Issue Check" in r["test"]), None)
        consistency_result = next((r for r in self.results if "Premium Count Consistency" in r["test"]), None)
        
        print("🔍 CRITICAL RESULTS:")
        if main_issue_result:
            print(f"   {main_issue_result['status']}: {main_issue_result['test']}")
            print(f"      {main_issue_result['details']}")
        
        if consistency_result:
            print(f"   {consistency_result['status']}: {consistency_result['test']}")
            print(f"      {consistency_result['details']}")
        print()
        
        # Overall assessment
        if main_issue_result and main_issue_result["success"]:
            print("🎉 SUCCESS: Premium content counter is showing correct count (not 0)!")
        elif main_issue_result and not main_issue_result["success"]:
            print("🚨 ISSUE CONFIRMED: Premium content counter is showing 0 when it should show actual count.")
        else:
            print("⚠️ INCONCLUSIVE: Could not determine if the main issue is resolved.")
        
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
    tester = FocusedPremiumCounterTester()
    tester.run_all_tests()