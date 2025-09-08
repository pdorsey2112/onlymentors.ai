#!/usr/bin/env python3
"""
Admin Console Mentors Endpoint Fix Testing
Tests the data structure mismatch fix for admin mentors endpoint
"""

import requests
import json
import time
import uuid
from datetime import datetime

# Configuration
BASE_URL = "https://enterprise-coach.preview.emergentagent.com/api"
TEST_ADMIN_EMAIL = "admin@onlymentors.ai"
TEST_ADMIN_PASSWORD = "SuperAdmin2024!"
TEST_USER_EMAIL = f"testmentor_{int(time.time())}@test.com"
TEST_USER_PASSWORD = "TestPass123!"
TEST_USER_NAME = "Test Mentor User"

class AdminMentorsEndpointTester:
    def __init__(self):
        self.admin_token = None
        self.user_token = None
        self.creator_id = None
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

    def setup_admin_auth(self):
        """Authenticate as admin"""
        print("🔧 Setting up admin authentication...")
        
        try:
            response = requests.post(f"{BASE_URL}/admin/login", json={
                "email": TEST_ADMIN_EMAIL,
                "password": TEST_ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token")
                self.log_result("Admin Authentication", True, f"Admin authenticated successfully")
                return True
            else:
                self.log_result("Admin Authentication", False, f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Exception: {str(e)}")
            return False

    def create_test_mentor(self):
        """Create a test mentor with new verification structure"""
        print("🔧 Creating test mentor...")
        
        try:
            # Register user with mentor option
            response = requests.post(f"{BASE_URL}/auth/register", data={
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD,
                "full_name": TEST_USER_NAME,
                "phone_number": "+1234567890",
                "communication_preferences": json.dumps({"email": True}),
                "subscription_plan": "free",
                "become_mentor": True
            })
            
            if response.status_code == 200:
                data = response.json()
                self.user_token = data.get("token")
                self.log_result("Test Mentor Creation", True, f"Mentor created successfully")
                return True
            else:
                self.log_result("Test Mentor Creation", False, f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Test Mentor Creation", False, f"Exception: {str(e)}")
            return False

    def test_admin_mentors_endpoint_no_error(self):
        """Test that admin mentors endpoint no longer returns 500 error"""
        print("🧪 Testing admin mentors endpoint for 500 error fix...")
        
        if not self.admin_token:
            self.log_result("Admin Mentors Endpoint - No 500 Error", False, "No admin token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{BASE_URL}/admin/mentors", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                mentors = data.get("mentors", [])
                self.log_result("Admin Mentors Endpoint - No 500 Error", True, 
                              f"Endpoint returned 200 OK with {len(mentors)} mentors")
                return True
            elif response.status_code == 500:
                self.log_result("Admin Mentors Endpoint - No 500 Error", False, 
                              f"Still returning 500 error", response.text)
                return False
            else:
                self.log_result("Admin Mentors Endpoint - No 500 Error", False, 
                              f"Unexpected status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Admin Mentors Endpoint - No 500 Error", False, f"Exception: {str(e)}")
            return False

    def test_mentors_visible_in_response(self):
        """Test that mentors are now visible in admin console response"""
        print("🧪 Testing mentor visibility in admin response...")
        
        if not self.admin_token:
            self.log_result("Mentors Visible in Response", False, "No admin token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{BASE_URL}/admin/mentors", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                mentors = data.get("mentors", [])
                total = data.get("total", 0)
                
                if len(mentors) > 0:
                    self.log_result("Mentors Visible in Response", True, 
                                  f"Found {len(mentors)} mentors in response (total: {total})")
                    return True
                else:
                    self.log_result("Mentors Visible in Response", False, 
                                  f"No mentors found in response (total: {total})")
                    return False
            else:
                self.log_result("Mentors Visible in Response", False, 
                              f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Mentors Visible in Response", False, f"Exception: {str(e)}")
            return False

    def test_expected_data_structure(self):
        """Test that admin console gets the expected fields"""
        print("🧪 Testing expected data structure in admin response...")
        
        if not self.admin_token:
            self.log_result("Expected Data Structure", False, "No admin token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{BASE_URL}/admin/mentors", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                mentors = data.get("mentors", [])
                
                if len(mentors) > 0:
                    mentor = mentors[0]  # Check first mentor
                    
                    # Expected fields
                    expected_fields = [
                        "creator_id", "email", "full_name", "account_name", 
                        "category", "monthly_price", "status", "subscriber_count", 
                        "total_earnings", "verification", "created_at"
                    ]
                    
                    missing_fields = []
                    for field in expected_fields:
                        if field not in mentor:
                            missing_fields.append(field)
                    
                    if not missing_fields:
                        # Check verification structure
                        verification = mentor.get("verification", {})
                        if "id_verified" in verification and "bank_verified" in verification:
                            self.log_result("Expected Data Structure", True, 
                                          f"All expected fields present including verification structure")
                            return True
                        else:
                            self.log_result("Expected Data Structure", False, 
                                          f"Verification structure missing id_verified/bank_verified: {verification}")
                            return False
                    else:
                        self.log_result("Expected Data Structure", False, 
                                      f"Missing fields: {missing_fields}")
                        return False
                else:
                    self.log_result("Expected Data Structure", False, "No mentors to check structure")
                    return False
            else:
                self.log_result("Expected Data Structure", False, 
                              f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Expected Data Structure", False, f"Exception: {str(e)}")
            return False

    def test_verification_status_mapping(self):
        """Test that verification status is properly mapped to id_verified/bank_verified booleans"""
        print("🧪 Testing verification status mapping...")
        
        if not self.admin_token:
            self.log_result("Verification Status Mapping", False, "No admin token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{BASE_URL}/admin/mentors", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                mentors = data.get("mentors", [])
                
                if len(mentors) > 0:
                    approved_mentors = 0
                    correct_mappings = 0
                    
                    for mentor in mentors:
                        verification = mentor.get("verification", {})
                        id_verified = verification.get("id_verified")
                        bank_verified = verification.get("bank_verified")
                        
                        # Check if these are boolean values
                        if isinstance(id_verified, bool) and isinstance(bank_verified, bool):
                            correct_mappings += 1
                            if id_verified and bank_verified:
                                approved_mentors += 1
                    
                    if correct_mappings == len(mentors):
                        self.log_result("Verification Status Mapping", True, 
                                      f"All {len(mentors)} mentors have correct boolean verification mapping. "
                                      f"{approved_mentors} are fully verified.")
                        return True
                    else:
                        self.log_result("Verification Status Mapping", False, 
                                      f"Only {correct_mappings}/{len(mentors)} mentors have correct mapping")
                        return False
                else:
                    self.log_result("Verification Status Mapping", False, "No mentors to check mapping")
                    return False
            else:
                self.log_result("Verification Status Mapping", False, 
                              f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Verification Status Mapping", False, f"Exception: {str(e)}")
            return False

    def test_search_functionality(self):
        """Test that search functionality works with the fixed endpoint"""
        print("🧪 Testing search functionality...")
        
        if not self.admin_token:
            self.log_result("Search Functionality", False, "No admin token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Test search by name
            response = requests.get(f"{BASE_URL}/admin/mentors?search=test", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                mentors = data.get("mentors", [])
                
                self.log_result("Search Functionality", True, 
                              f"Search returned {len(mentors)} mentors")
                return True
            else:
                self.log_result("Search Functionality", False, 
                              f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Search Functionality", False, f"Exception: {str(e)}")
            return False

    def test_pagination_functionality(self):
        """Test that pagination works with the fixed endpoint"""
        print("🧪 Testing pagination functionality...")
        
        if not self.admin_token:
            self.log_result("Pagination Functionality", False, "No admin token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Test pagination
            response = requests.get(f"{BASE_URL}/admin/mentors?limit=5&offset=0", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                mentors = data.get("mentors", [])
                total = data.get("total", 0)
                limit = data.get("limit", 0)
                offset = data.get("offset", 0)
                
                self.log_result("Pagination Functionality", True, 
                              f"Pagination working: {len(mentors)} mentors, total: {total}, limit: {limit}, offset: {offset}")
                return True
            else:
                self.log_result("Pagination Functionality", False, 
                              f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Pagination Functionality", False, f"Exception: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all admin mentors endpoint tests"""
        print("🚀 Starting Admin Mentors Endpoint Fix Testing...")
        print("=" * 60)
        
        # Setup
        if not self.setup_admin_auth():
            print("❌ Cannot proceed without admin authentication")
            return False
        
        # Create test mentor (optional - tests should work with existing mentors too)
        self.create_test_mentor()
        
        # Core tests for the fix
        tests = [
            self.test_admin_mentors_endpoint_no_error,
            self.test_mentors_visible_in_response,
            self.test_expected_data_structure,
            self.test_verification_status_mapping,
            self.test_search_functionality,
            self.test_pagination_functionality
        ]
        
        # Run tests
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
        
        # Summary
        print("=" * 60)
        print(f"🏁 ADMIN MENTORS ENDPOINT FIX TEST SUMMARY")
        print(f"Tests Passed: {passed}/{total}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED - Admin mentors endpoint fix is working correctly!")
        else:
            print("⚠️  Some tests failed - Admin mentors endpoint may still have issues")
        
        return passed == total

def main():
    """Main test execution"""
    tester = AdminMentorsEndpointTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ ADMIN MENTORS ENDPOINT FIX VERIFICATION COMPLETE - ALL TESTS PASSED!")
    else:
        print("\n❌ ADMIN MENTORS ENDPOINT FIX VERIFICATION FAILED - SOME TESTS FAILED!")
    
    return success

if __name__ == "__main__":
    main()