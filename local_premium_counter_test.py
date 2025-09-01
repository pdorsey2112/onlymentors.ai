#!/usr/bin/env python3
"""
Local Premium Content Counter Testing
Testing premium content counter endpoints using localhost backend
"""

import requests
import json
import time
from datetime import datetime

# Configuration - Use localhost since external URL has 502 issues
BASE_URL = "http://localhost:8001"
EXISTING_CREATOR_ID = "creator_fee1ffa3ece5"  # From logs

class LocalPremiumCounterTester:
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

    def check_stats_endpoint_exists(self):
        """Check if the stats endpoint exists by looking at available endpoints"""
        print("🔍 Checking Available Creator Endpoints...")
        
        # Test various possible stats endpoints
        possible_endpoints = [
            f"/creators/{EXISTING_CREATOR_ID}/stats",
            f"/creators/{EXISTING_CREATOR_ID}/analytics", 
            f"/creators/{EXISTING_CREATOR_ID}/dashboard",
            f"/creators/{EXISTING_CREATOR_ID}/summary"
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
            response = requests.get(f"{BASE_URL}/creators/{EXISTING_CREATOR_ID}/content")
            if response.status_code == 200:
                data = response.json()
                standard_count = len(data.get("content", []))
        except:
            pass
        
        # Get premium content count and earnings
        premium_count = 0
        premium_earnings = 0
        try:
            response = requests.get(f"{BASE_URL}/creators/{EXISTING_CREATOR_ID}/premium-content")
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

    def run_all_tests(self):
        """Run all local premium content counter tests"""
        print("🚀 Starting Local Premium Content Counter Testing")
        print("=" * 70)
        print(f"Testing Creator: {EXISTING_CREATOR_ID}")
        print("Backend: localhost:8001 (bypassing 502 external URL issue)")
        print("Focus: Verifying premium content counter endpoints and data")
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
        print("🎯 LOCAL PREMIUM CONTENT COUNTER TESTING SUMMARY")
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
        
        if results and results['premium_count'] > 0:
            print(f"   ✅ Premium content EXISTS: {results['premium_count']} items found")
            
            if results['stats_count'] == results['premium_count']:
                print(f"   ✅ Stats endpoint shows CORRECT count: {results['stats_count']}")
                print("   🎉 COUNTER FIX IS WORKING! Dashboard should show correct count.")
            elif results['stats_count'] == 0:
                print(f"   ❌ Stats endpoint shows 0 instead of {results['premium_count']}")
                print("   🚨 COUNTER ISSUE CONFIRMED: Stats endpoint not returning premium count")
            else:
                print(f"   ⚠️ Stats endpoint shows {results['stats_count']} but should be {results['premium_count']}")
                print("   🚨 COUNTER MISMATCH: Stats calculation may be incorrect")
        
        elif results and results['premium_count'] == 0:
            print("   ℹ️ No premium content found - counter showing 0 is correct")
            print("   💡 To test the fix, premium content needs to be uploaded first")
        
        else:
            print("   ❌ Could not determine premium content count")
        
        # Recommendations
        print("\n📋 RECOMMENDATIONS:")
        
        stats_endpoint_working = any(r["success"] for r in self.results if "Creator Stats Endpoint" in r["test"])
        
        if not stats_endpoint_working:
            print("   🔧 CRITICAL: Creator stats endpoint is not working - this is likely the root cause")
            print("   🔧 Need to implement or fix GET /api/creators/{creator_id}/stats endpoint")
        
        if results and results['premium_count'] > 0 and results['stats_count'] != results['premium_count']:
            print("   🔧 Stats calculation needs to be fixed to include premium content count")
            print("   🔧 Verify fetchCreatorStats() function includes premium content data")
        
        if results and results['premium_count'] == 0:
            print("   📝 Upload premium content to test counter functionality")
            print("   📝 Verify stats refresh after content upload operations")
        
        print("=" * 70)

if __name__ == "__main__":
    tester = LocalPremiumCounterTester()
    tester.run_all_tests()