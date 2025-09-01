#!/usr/bin/env python3
"""
Final Premium Content Counter Testing
Testing premium content counter endpoints with correct URLs
"""

import requests
import json
import time
from datetime import datetime

# Configuration - Use localhost with correct API paths
BASE_URL = "http://localhost:8001"
EXISTING_CREATOR_ID = "creator_fee1ffa3ece5"  # From logs

class FinalPremiumCounterTester:
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

    def test_api_root(self):
        """Test API root endpoint"""
        print("🔧 Testing API Root...")
        
        try:
            response = requests.get(f"{BASE_URL}/")
            if response.status_code == 200:
                data = response.json()
                self.log_result("API Root", True, 
                              f"API accessible - Total mentors: {data.get('total_mentors', 0)}")
                return True
            else:
                self.log_result("API Root", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("API Root", False, f"Exception: {str(e)}")
            return False

    def test_standard_content_endpoint(self):
        """Test GET /api/creators/{creator_id}/content for standard content count"""
        print("📊 Testing Standard Content Endpoint...")
        
        try:
            response = requests.get(f"{BASE_URL}/api/creators/{EXISTING_CREATOR_ID}/content")
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
            response = requests.get(f"{BASE_URL}/api/creators/{EXISTING_CREATOR_ID}/premium-content")
            if response.status_code == 200:
                data = response.json()
                content_list = data.get("content", [])
                total_count = data.get("total", len(content_list))
                
                # Calculate total revenue and earnings
                total_revenue = sum(c.get("total_revenue", 0) for c in content_list)
                creator_earnings = sum(c.get("creator_earnings", 0) for c in content_list)
                
                self.log_result("Premium Content Endpoint", True, 
                              f"Premium content count: {len(content_list)}, Total: {total_count}, Revenue: ${total_revenue}, Earnings: ${creator_earnings}")
                
                # Show details of each premium content
                if content_list:
                    print("   Premium Content Details:")
                    for i, content in enumerate(content_list[:5]):  # Show first 5
                        print(f"     {i+1}. {content.get('title', 'No Title')} - ${content.get('price', 0)} - Purchases: {content.get('total_purchases', 0)}")
                
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
            response = requests.get(f"{BASE_URL}/api/creators/{EXISTING_CREATOR_ID}/stats")
            if response.status_code == 200:
                data = response.json()
                stats = data.get("stats", {})
                
                premium_count = stats.get("premium_content_count", 0)
                premium_earnings = stats.get("premium_earnings", 0)
                total_sales = stats.get("total_sales", 0)
                
                self.log_result("Creator Stats Endpoint", True, 
                              f"Stats - Premium count: {premium_count}, Earnings: ${premium_earnings}, Sales: {total_sales}")
                return premium_count, premium_earnings, total_sales
            elif response.status_code == 404:
                self.log_result("Creator Stats Endpoint", False, 
                              "Stats endpoint not found - this might be the issue!")
                return 0, 0, 0
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
            response = requests.get(f"{BASE_URL}/api/mentor/{EXISTING_CREATOR_ID}/premium-content")
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

    def check_stats_endpoint_exists(self):
        """Check if the stats endpoint exists by looking at available endpoints"""
        print("🔍 Checking Available Creator Endpoints...")
        
        # Test various possible stats endpoints
        possible_endpoints = [
            f"/api/creators/{EXISTING_CREATOR_ID}/stats",
            f"/api/creators/{EXISTING_CREATOR_ID}/analytics", 
            f"/api/creators/{EXISTING_CREATOR_ID}/dashboard",
            f"/api/creators/{EXISTING_CREATOR_ID}/summary"
        ]
        
        for endpoint in possible_endpoints:
            try:
                response = requests.get(f"{BASE_URL}{endpoint}")
                if response.status_code == 200:
                    self.log_result(f"Endpoint Check - {endpoint}", True, "Endpoint exists and accessible")
                elif response.status_code == 404:
                    self.log_result(f"Endpoint Check - {endpoint}", False, "Endpoint not found (404)")
                else:
                    self.log_result(f"Endpoint Check - {endpoint}", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_result(f"Endpoint Check - {endpoint}", False, f"Exception: {str(e)}")

    def test_fetchCreatorStats_function(self):
        """Test if there's a fetchCreatorStats function by checking what endpoints combine the data"""
        print("🔄 Testing Combined Stats Functionality...")
        
        # Get standard content count
        standard_count = 0
        try:
            response = requests.get(f"{BASE_URL}/api/creators/{EXISTING_CREATOR_ID}/content")
            if response.status_code == 200:
                data = response.json()
                standard_count = len(data.get("content", []))
        except:
            pass
        
        # Get premium content count and earnings
        premium_count = 0
        premium_earnings = 0
        try:
            response = requests.get(f"{BASE_URL}/api/creators/{EXISTING_CREATOR_ID}/premium-content")
            if response.status_code == 200:
                data = response.json()
                content_list = data.get("content", [])
                premium_count = len(content_list)
                premium_earnings = sum(c.get("creator_earnings", 0) for c in content_list)
        except:
            pass
        
        # Manual calculation of what stats should be
        total_content = standard_count + premium_count
        
        self.log_result("Manual Stats Calculation", True, 
                      f"Standard: {standard_count}, Premium: {premium_count}, Total: {total_content}, Premium Earnings: ${premium_earnings}")
        
        # This is what the dashboard should show
        if premium_count > 0:
            self.log_result("Expected Dashboard Behavior", True, 
                          f"✅ Dashboard should show Premium Content Count: {premium_count} (not 0)")
        else:
            self.log_result("Expected Dashboard Behavior", False, 
                          f"❌ No premium content found - dashboard would correctly show 0")
        
        return {
            "standard_count": standard_count,
            "premium_count": premium_count,
            "total_content": total_content,
            "premium_earnings": premium_earnings
        }

    def test_premium_content_counter_issue(self):
        """Test the specific issue: premium content counter showing 0 when it should show 1"""
        print("🎯 Testing Premium Content Counter Issue...")
        
        # Get actual premium content count
        try:
            response = requests.get(f"{BASE_URL}/api/creators/{EXISTING_CREATOR_ID}/premium-content")
            if response.status_code == 200:
                data = response.json()
                actual_premium_count = len(data.get("content", []))
                
                # Get stats endpoint count
                stats_response = requests.get(f"{BASE_URL}/api/creators/{EXISTING_CREATOR_ID}/stats")
                if stats_response.status_code == 200:
                    stats_data = stats_response.json()
                    stats_premium_count = stats_data.get("stats", {}).get("premium_content_count", 0)
                    
                    # Compare actual vs stats
                    if actual_premium_count > 0 and stats_premium_count == actual_premium_count:
                        self.log_result("Premium Counter Issue Check", True, 
                                      f"✅ FIXED! Actual: {actual_premium_count}, Stats: {stats_premium_count} - Counter shows correct count")
                    elif actual_premium_count > 0 and stats_premium_count == 0:
                        self.log_result("Premium Counter Issue Check", False, 
                                      f"❌ ISSUE PERSISTS! Actual: {actual_premium_count}, Stats: {stats_premium_count} - Counter shows 0 instead of {actual_premium_count}")
                    elif actual_premium_count == 0:
                        self.log_result("Premium Counter Issue Check", True, 
                                      f"ℹ️ No premium content exists - counter correctly shows 0")
                    else:
                        self.log_result("Premium Counter Issue Check", False, 
                                      f"⚠️ Mismatch: Actual: {actual_premium_count}, Stats: {stats_premium_count}")
                else:
                    self.log_result("Premium Counter Issue Check", False, 
                                  f"Stats endpoint failed: {stats_response.status_code}")
            else:
                self.log_result("Premium Counter Issue Check", False, 
                              f"Premium content endpoint failed: {response.status_code}")
        except Exception as e:
            self.log_result("Premium Counter Issue Check", False, f"Exception: {str(e)}")

    def run_all_tests(self):
        """Run all final premium content counter tests"""
        print("🚀 Starting Final Premium Content Counter Testing")
        print("=" * 70)
        print(f"Testing Creator: {EXISTING_CREATOR_ID}")
        print("Backend: localhost:8001")
        print("Focus: Verifying premium content counter fix")
        print("Issue: Dashboard showing '0' when it should show '1'")
        print("=" * 70)
        
        # Test API accessibility first
        if not self.test_api_root():
            print("❌ Cannot access API. Aborting tests.")
            return
        
        # Run endpoint tests
        standard_count = self.test_standard_content_endpoint()
        premium_count, premium_revenue, premium_earnings = self.test_premium_content_endpoint()
        stats_count, stats_earnings, stats_sales = self.test_creator_stats_endpoint()
        discovery_count = self.test_premium_content_discovery()
        
        # Check endpoint availability
        self.check_stats_endpoint_exists()
        
        # Manual calculation test
        manual_stats = self.test_fetchCreatorStats_function()
        
        # Test the specific issue
        self.test_premium_content_counter_issue()
        
        # Summary
        self.print_summary({
            "standard_count": standard_count,
            "premium_count": premium_count,
            "stats_count": stats_count,
            "discovery_count": discovery_count,
            "premium_earnings": premium_earnings,
            "stats_earnings": stats_earnings,
            "manual_stats": manual_stats
        })

    def print_summary(self, results=None):
        """Print test summary"""
        print("\n" + "=" * 70)
        print("🎯 FINAL PREMIUM CONTENT COUNTER TESTING SUMMARY")
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
        
        # Analysis of the main issue
        print("🎯 PREMIUM CONTENT COUNTER ANALYSIS:")
        
        counter_issue_result = next((r for r in self.results if "Premium Counter Issue Check" in r["test"]), None)
        
        if counter_issue_result:
            if counter_issue_result["success"] and "FIXED" in counter_issue_result["details"]:
                print("   🎉 SUCCESS: Premium content counter fix is working!")
                print("   ✅ Dashboard now shows correct premium content count")
            elif not counter_issue_result["success"] and "ISSUE PERSISTS" in counter_issue_result["details"]:
                print("   🚨 ISSUE CONFIRMED: Premium content counter still showing 0")
                print("   ❌ Dashboard not displaying correct premium content count")
            elif counter_issue_result["success"] and "No premium content" in counter_issue_result["details"]:
                print("   ℹ️ No premium content exists to test counter")
                print("   💡 Need to upload premium content to verify fix")
            else:
                print("   ⚠️ Counter behavior unclear - see test details above")
        
        # Critical recommendations
        print("\n📋 CRITICAL FINDINGS:")
        
        stats_endpoint_working = any(r["success"] for r in self.results if "Creator Stats Endpoint" in r["test"])
        
        if not stats_endpoint_working:
            print("   🚨 CRITICAL: Creator stats endpoint (/api/creators/{id}/stats) not working")
            print("   🔧 This is likely the root cause of the counter issue")
            print("   🔧 Need to implement fetchCreatorStats() function and endpoint")
        
        if results and results['premium_count'] > 0:
            if results['stats_count'] == results['premium_count']:
                print("   ✅ Premium content counter is working correctly")
            else:
                print("   🚨 Premium content exists but stats endpoint not reflecting it")
                print("   🔧 Stats calculation needs to include premium content count")
        
        if results and results['premium_count'] == 0:
            print("   💡 No premium content found - upload content to test counter")
        
        print("=" * 70)

if __name__ == "__main__":
    tester = FinalPremiumCounterTester()
    tester.run_all_tests()