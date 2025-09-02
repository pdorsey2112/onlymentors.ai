#!/usr/bin/env python3
"""
Comprehensive Test Suite for Mentor Tier Rating System using curl
Tests the 4-tier mentor rating system based on subscriber counts
"""

import subprocess
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://mentor-marketplace.preview.emergentagent.com/api"

class MentorTierTester:
    def __init__(self):
        self.test_results = []
        self.creator_token = None
        self.test_creator_id = None
        
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
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if error:
            print(f"   Error: {error}")
        print()

    def curl_request(self, method, endpoint, headers=None, data=None):
        """Make HTTP request using curl"""
        try:
            cmd = ["curl", "-s", "-X", method]
            
            if headers:
                for key, value in headers.items():
                    cmd.extend(["-H", f"{key}: {value}"])
            
            if data:
                cmd.extend(["-H", "Content-Type: application/json"])
                cmd.extend(["-d", json.dumps(data)])
            
            cmd.append(f"{BACKEND_URL}{endpoint}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            # Try to parse JSON response
            try:
                response_data = json.loads(result.stdout) if result.stdout else {}
            except json.JSONDecodeError:
                response_data = {"raw_response": result.stdout}
            
            return {
                "status_code": result.returncode,
                "data": response_data,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
        except subprocess.TimeoutExpired:
            return {"status_code": 408, "data": {}, "error": "Request timeout"}
        except Exception as e:
            return {"status_code": 500, "data": {}, "error": str(e)}

    def get_http_status(self, endpoint):
        """Get HTTP status code using curl"""
        try:
            cmd = ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", f"{BACKEND_URL}{endpoint}"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            return int(result.stdout) if result.stdout.isdigit() else 0
        except:
            return 0

    def test_tier_calculation_logic(self):
        """Test tier calculation logic by validating tier info endpoint"""
        print("🧪 Testing Tier Calculation Logic...")
        
        # Get tier information
        response = self.curl_request("GET", "/mentor-tiers/info")
        
        if response["status_code"] == 0 and response["data"].get("tiers"):
            tiers = response["data"]["tiers"]
            
            # Test cases for different subscriber counts
            test_cases = [
                {"subscribers": 0, "expected_tier": "New Mentor", "expected_level": "new"},
                {"subscribers": 50, "expected_tier": "New Mentor", "expected_level": "new"},
                {"subscribers": 150, "expected_tier": "Silver Mentor", "expected_level": "silver"},
                {"subscribers": 1500, "expected_tier": "Gold Mentor", "expected_level": "gold"},
                {"subscribers": 15000, "expected_tier": "Platinum Mentor", "expected_level": "platinum"},
                {"subscribers": 150000, "expected_tier": "Ultimate Mentor", "expected_level": "ultimate"},
                # Edge cases at tier boundaries
                {"subscribers": 99, "expected_tier": "New Mentor", "expected_level": "new"},
                {"subscribers": 100, "expected_tier": "Silver Mentor", "expected_level": "silver"},
                {"subscribers": 999, "expected_tier": "Silver Mentor", "expected_level": "silver"},
                {"subscribers": 1000, "expected_tier": "Gold Mentor", "expected_level": "gold"},
                {"subscribers": 9999, "expected_tier": "Gold Mentor", "expected_level": "gold"},
                {"subscribers": 10000, "expected_tier": "Platinum Mentor", "expected_level": "platinum"},
                {"subscribers": 99999, "expected_tier": "Platinum Mentor", "expected_level": "platinum"},
                {"subscribers": 100000, "expected_tier": "Ultimate Mentor", "expected_level": "ultimate"}
            ]
            
            for case in test_cases:
                # Find the appropriate tier for this subscriber count
                matching_tier = None
                for tier in tiers:
                    if case["subscribers"] >= tier["min_subscribers"]:
                        if not matching_tier or tier["min_subscribers"] > matching_tier["min_subscribers"]:
                            matching_tier = tier
                
                if (matching_tier and 
                    matching_tier["tier"] == case["expected_tier"] and 
                    matching_tier["level"] == case["expected_level"]):
                    self.log_test(
                        f"Tier Calculation - {case['subscribers']} subscribers",
                        True,
                        f"Correctly maps to {case['expected_tier']} ({case['expected_level']})"
                    )
                else:
                    self.log_test(
                        f"Tier Calculation - {case['subscribers']} subscribers",
                        False,
                        f"Expected {case['expected_tier']}, got {matching_tier['tier'] if matching_tier else 'None'}"
                    )
        else:
            self.log_test(
                "Tier Calculation Logic",
                False,
                error="Failed to get tier information from API"
            )

    def test_mentor_tier_info_endpoint(self):
        """Test GET /api/mentor-tiers/info endpoint"""
        print("🧪 Testing Mentor Tier Info Endpoint...")
        
        # Test HTTP status
        status_code = self.get_http_status("/mentor-tiers/info")
        if status_code == 200:
            self.log_test(
                "Tier Info Endpoint - HTTP Status",
                True,
                f"Returns HTTP 200"
            )
        else:
            self.log_test(
                "Tier Info Endpoint - HTTP Status",
                False,
                f"Expected HTTP 200, got {status_code}"
            )
            return
        
        # Test response structure
        response = self.curl_request("GET", "/mentor-tiers/info")
        
        if response["status_code"] == 0 and response["data"].get("tiers"):
            tiers = response["data"]["tiers"]
            
            # Verify all 5 tiers are present
            expected_tiers = ["Ultimate Mentor", "Platinum Mentor", "Gold Mentor", "Silver Mentor", "New Mentor"]
            found_tiers = [tier["tier"] for tier in tiers]
            
            if len(tiers) == 5:
                self.log_test(
                    "Tier Info Endpoint - Tier Count",
                    True,
                    f"Found all 5 tiers: {found_tiers}"
                )
            else:
                self.log_test(
                    "Tier Info Endpoint - Tier Count",
                    False,
                    f"Expected 5 tiers, found {len(tiers)}: {found_tiers}"
                )
            
            # Verify tier structure and required fields
            required_fields = ["level", "tier", "min_subscribers", "badge_color", "description", "benefits"]
            for tier in tiers:
                tier_name = tier.get("tier", "Unknown")
                missing_fields = [field for field in required_fields if field not in tier]
                
                if not missing_fields:
                    self.log_test(
                        f"Tier Info Structure - {tier_name}",
                        True,
                        f"All required fields present"
                    )
                else:
                    self.log_test(
                        f"Tier Info Structure - {tier_name}",
                        False,
                        f"Missing fields: {missing_fields}"
                    )
            
            # Verify subscriber thresholds are correct
            expected_thresholds = {
                "Ultimate Mentor": 100000,
                "Platinum Mentor": 10000,
                "Gold Mentor": 1000,
                "Silver Mentor": 100,
                "New Mentor": 0
            }
            
            for tier in tiers:
                tier_name = tier.get("tier")
                min_subs = tier.get("min_subscribers")
                expected_min = expected_thresholds.get(tier_name)
                
                if min_subs == expected_min:
                    self.log_test(
                        f"Tier Threshold - {tier_name}",
                        True,
                        f"Correct threshold: {min_subs} subscribers"
                    )
                else:
                    self.log_test(
                        f"Tier Threshold - {tier_name}",
                        False,
                        f"Expected {expected_min}, got {min_subs}"
                    )
            
            # Verify badge colors are present and valid
            for tier in tiers:
                tier_name = tier.get("tier")
                badge_color = tier.get("badge_color", "")
                
                if badge_color and badge_color.startswith("#") and len(badge_color) == 7:
                    self.log_test(
                        f"Badge Color - {tier_name}",
                        True,
                        f"Valid hex color: {badge_color}"
                    )
                else:
                    self.log_test(
                        f"Badge Color - {tier_name}",
                        False,
                        f"Invalid badge color: {badge_color}"
                    )
                    
        else:
            self.log_test(
                "Tier Info Endpoint - Response",
                False,
                error="Failed to get valid response from API"
            )

    def setup_test_creator(self):
        """Create a test creator for tier update testing"""
        print("🧪 Setting up Test Creator...")
        
        # Create test creator
        creator_data = {
            "email": f"tiertest_{int(datetime.now().timestamp())}@test.com",
            "password": "TestPassword123!",
            "full_name": "Tier Test Creator",
            "expertise": "Testing",
            "bio": "Test creator for tier system testing",
            "monthly_price": 50.0
        }
        
        response = self.curl_request("POST", "/creators/signup", data=creator_data)
        
        if response["status_code"] == 0 and response["data"].get("token"):
            self.creator_token = response["data"]["token"]
            creator_info = response["data"].get("creator", {})
            self.test_creator_id = creator_info.get("creator_id")
            
            self.log_test(
                "Test Creator Setup",
                True,
                f"Created test creator: {self.test_creator_id}"
            )
            return True
        else:
            self.log_test(
                "Test Creator Setup",
                False,
                error=f"Failed to create test creator: {response.get('error', 'Unknown error')}"
            )
            return False

    def test_tier_update_endpoint(self):
        """Test POST /api/creators/{creator_id}/update-tier endpoint"""
        print("🧪 Testing Tier Update Endpoint...")
        
        if not self.creator_token or not self.test_creator_id:
            self.log_test(
                "Tier Update Endpoint",
                False,
                error="No test creator available"
            )
            return
        
        # Test tier update with authentication
        headers = {"Authorization": f"Bearer {self.creator_token}"}
        response = self.curl_request("POST", f"/creators/{self.test_creator_id}/update-tier", headers=headers)
        
        if response["status_code"] == 0 and response["data"].get("tier_info"):
            tier_info = response["data"]["tier_info"]
            
            # Verify response structure
            required_fields = ["tier", "level", "badge_color", "description", "min_subscribers"]
            missing_fields = [field for field in required_fields if field not in tier_info]
            
            if not missing_fields:
                self.log_test(
                    "Tier Update Endpoint - Response Structure",
                    True,
                    f"Tier updated to: {tier_info.get('tier')} ({tier_info.get('level')})"
                )
            else:
                self.log_test(
                    "Tier Update Endpoint - Response Structure",
                    False,
                    f"Missing fields in response: {missing_fields}"
                )
        else:
            self.log_test(
                "Tier Update Endpoint",
                False,
                error=f"Failed to update tier: {response.get('error', 'Unknown error')}"
            )

    def test_tier_update_authentication(self):
        """Test tier update endpoint authentication and authorization"""
        print("🧪 Testing Tier Update Authentication...")
        
        if not self.test_creator_id:
            self.log_test(
                "Tier Update Authentication",
                False,
                error="No test creator available"
            )
            return
        
        # Test without authentication
        status_code = self.get_http_status(f"/creators/{self.test_creator_id}/update-tier")
        
        if status_code in [401, 403]:
            self.log_test(
                "Tier Update - No Auth",
                True,
                f"Correctly rejected unauthenticated request: {status_code}"
            )
        else:
            self.log_test(
                "Tier Update - No Auth",
                False,
                f"Should reject unauthenticated request, got: {status_code}"
            )
        
        # Test with invalid token
        headers = {"Authorization": "Bearer invalid_token_12345"}
        response = self.curl_request("POST", f"/creators/{self.test_creator_id}/update-tier", headers=headers)
        
        # Check if it's properly rejected (should not have tier_info in response)
        if not response["data"].get("tier_info"):
            self.log_test(
                "Tier Update - Invalid Token",
                True,
                "Correctly rejected invalid token"
            )
        else:
            self.log_test(
                "Tier Update - Invalid Token",
                False,
                "Should reject invalid token"
            )

    def test_tier_scenarios(self):
        """Test various tier assignment scenarios"""
        print("🧪 Testing Tier Assignment Scenarios...")
        
        # Test scenarios with different subscriber counts
        scenarios = [
            {"name": "New Mentor (0 subscribers)", "subscribers": 0, "expected": "New Mentor"},
            {"name": "New Mentor (50 subscribers)", "subscribers": 50, "expected": "New Mentor"},
            {"name": "Silver Mentor (150 subscribers)", "subscribers": 150, "expected": "Silver Mentor"},
            {"name": "Gold Mentor (1500 subscribers)", "subscribers": 1500, "expected": "Gold Mentor"},
            {"name": "Platinum Mentor (15000 subscribers)", "subscribers": 15000, "expected": "Platinum Mentor"},
            {"name": "Ultimate Mentor (150000 subscribers)", "subscribers": 150000, "expected": "Ultimate Mentor"}
        ]
        
        # Get tier information
        response = self.curl_request("GET", "/mentor-tiers/info")
        
        if response["status_code"] == 0 and response["data"].get("tiers"):
            tiers = response["data"]["tiers"]
            
            for scenario in scenarios:
                # Find the appropriate tier for this subscriber count
                matching_tier = None
                for tier in tiers:
                    if scenario["subscribers"] >= tier["min_subscribers"]:
                        if not matching_tier or tier["min_subscribers"] > matching_tier["min_subscribers"]:
                            matching_tier = tier
                
                if matching_tier and matching_tier["tier"] == scenario["expected"]:
                    self.log_test(
                        f"Tier Scenario - {scenario['name']}",
                        True,
                        f"Correctly maps to {matching_tier['tier']} (min: {matching_tier['min_subscribers']})"
                    )
                else:
                    self.log_test(
                        f"Tier Scenario - {scenario['name']}",
                        False,
                        f"Expected {scenario['expected']}, got {matching_tier['tier'] if matching_tier else 'None'}"
                    )
        else:
            self.log_test(
                "Tier Scenarios",
                False,
                error="Failed to get tier info"
            )

    def run_all_tests(self):
        """Run all mentor tier system tests"""
        print("🚀 Starting Mentor Tier Rating System Tests")
        print("=" * 60)
        
        # Test 1: Tier Calculation Logic
        self.test_tier_calculation_logic()
        
        # Test 2: Mentor Tier API Endpoints
        self.test_mentor_tier_info_endpoint()
        
        # Test 3: Setup test creator for tier update tests
        if self.setup_test_creator():
            # Test 4: Tier Update Functionality
            self.test_tier_update_endpoint()
            
            # Test 5: Authentication and Authorization
            self.test_tier_update_authentication()
        
        # Test 6: Tier Assignment Scenarios
        self.test_tier_scenarios()
        
        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print("=" * 60)
        print("🎯 MENTOR TIER SYSTEM TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['error']}")
            print()
        
        # Key findings
        print("🔍 KEY FINDINGS:")
        
        # Check if tier calculation logic is working
        tier_calc_tests = [r for r in self.test_results if "Tier Calculation" in r["test"]]
        tier_calc_passed = sum(1 for r in tier_calc_tests if r["success"])
        if tier_calc_passed == len(tier_calc_tests) and len(tier_calc_tests) > 0:
            print("   ✅ Tier calculation logic working correctly for all subscriber thresholds")
        else:
            print(f"   ❌ Tier calculation issues found ({tier_calc_passed}/{len(tier_calc_tests)} passed)")
        
        # Check if API endpoints are working
        api_tests = [r for r in self.test_results if "Endpoint" in r["test"]]
        api_passed = sum(1 for r in api_tests if r["success"])
        if api_passed == len(api_tests) and len(api_tests) > 0:
            print("   ✅ All tier-related API endpoints functional")
        else:
            print(f"   ❌ API endpoint issues found ({api_passed}/{len(api_tests)} passed)")
        
        # Check authentication
        auth_tests = [r for r in self.test_results if "Auth" in r["test"] or "Token" in r["test"]]
        auth_passed = sum(1 for r in auth_tests if r["success"])
        if auth_passed == len(auth_tests) and len(auth_tests) > 0:
            print("   ✅ Authentication and authorization working properly")
        else:
            print(f"   ❌ Authentication issues found ({auth_passed}/{len(auth_tests)} passed)")
        
        # Overall assessment
        print()
        if success_rate >= 90:
            print("🎉 MENTOR TIER SYSTEM IS PRODUCTION-READY!")
        elif success_rate >= 75:
            print("⚠️  Mentor tier system mostly functional with minor issues")
        else:
            print("🚨 Mentor tier system has significant issues requiring fixes")
        
        print("=" * 60)

if __name__ == "__main__":
    tester = MentorTierTester()
    tester.run_all_tests()