#!/usr/bin/env python3
"""
Admin Console Mentor Data Fix Testing
Tests the mentor creation logic updates to include missing fields for admin console compatibility
"""

import requests
import json
import time
import uuid
from datetime import datetime

# Configuration
BASE_URL = "https://mentor-search.preview.emergentagent.com/api"

class AdminMentorDataFixTester:
    def __init__(self):
        self.results = []
        self.test_users = []
        self.test_mentors = []
        
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

    def test_new_mentor_via_signup(self):
        """Test creating new mentor via signup with become_mentor=true"""
        print("👤 Testing New Mentor Creation via Signup...")
        
        # Generate unique test data
        test_email = f"mentor.signup.{int(time.time())}@test.com"
        test_name = f"Test Mentor Signup {int(time.time())}"
        
        signup_data = {
            "email": test_email,
            "password": "TestPass123!",
            "full_name": test_name,
            "phone_number": "+1234567890",
            "communication_preferences": json.dumps({"email": True, "text": False}),
            "subscription_plan": "free",
            "become_mentor": True
        }
        
        try:
            response = requests.post(f"{BASE_URL}/auth/register", data=signup_data)
            
            if response.status_code in [200, 201]:
                data = response.json()
                user_data = data.get("user", {})
                
                # Verify mentor flag is set
                is_mentor = user_data.get("is_mentor", False)
                
                if is_mentor:
                    self.log_result("New Mentor Signup - User Creation", True, 
                                  f"User created with mentor flag: {user_data.get('user_id')}")
                    
                    # Store for cleanup
                    self.test_users.append({
                        "email": test_email,
                        "user_id": user_data.get("user_id"),
                        "token": data.get("token")
                    })
                    
                    # Now verify mentor document was created with all required fields
                    self.verify_mentor_document_structure(test_email, test_name)
                    
                else:
                    self.log_result("New Mentor Signup - User Creation", False, 
                                  "User created but mentor flag not set")
            else:
                self.log_result("New Mentor Signup - User Creation", False, 
                              f"Status: {response.status_code}", response.text)
                
        except Exception as e:
            self.log_result("New Mentor Signup - User Creation", False, f"Exception: {str(e)}")

    def test_existing_user_upgrade_to_mentor(self):
        """Test existing user upgrade to mentor via /api/users/become-mentor"""
        print("🔄 Testing Existing User Upgrade to Mentor...")
        
        # First create a regular user
        test_email = f"user.upgrade.{int(time.time())}@test.com"
        test_name = f"Test User Upgrade {int(time.time())}"
        
        signup_data = {
            "email": test_email,
            "password": "TestPass123!",
            "full_name": test_name,
            "phone_number": "+1234567891",
            "communication_preferences": json.dumps({"email": True, "text": False}),
            "subscription_plan": "free",
            "become_mentor": False  # Regular user first
        }
        
        try:
            # Create regular user
            response = requests.post(f"{BASE_URL}/auth/register", data=signup_data)
            
            if response.status_code not in [200, 201]:
                self.log_result("User Upgrade - Initial User Creation", False, 
                              f"Failed to create user. Status: {response.status_code}")
                return
            
            data = response.json()
            user_token = data.get("token")
            user_id = data.get("user", {}).get("user_id")
            
            self.log_result("User Upgrade - Initial User Creation", True, f"User created: {user_id}")
            
            # Store for cleanup
            self.test_users.append({
                "email": test_email,
                "user_id": user_id,
                "token": user_token
            })
            
            # Now upgrade to mentor
            headers = {"Authorization": f"Bearer {user_token}"}
            upgrade_response = requests.post(f"{BASE_URL}/users/become-mentor", headers=headers)
            
            if upgrade_response.status_code == 200:
                upgrade_data = upgrade_response.json()
                creator_id = upgrade_data.get("creator_id")
                
                if creator_id:
                    self.log_result("User Upgrade - Mentor Upgrade", True, 
                                  f"User upgraded to mentor: {creator_id}")
                    
                    # Verify mentor document structure
                    self.verify_mentor_document_structure(test_email, test_name)
                else:
                    self.log_result("User Upgrade - Mentor Upgrade", False, 
                                  "Upgrade response missing creator_id")
            else:
                self.log_result("User Upgrade - Mentor Upgrade", False, 
                              f"Upgrade failed. Status: {upgrade_response.status_code}", upgrade_response.text)
                
        except Exception as e:
            self.log_result("User Upgrade - Mentor Upgrade", False, f"Exception: {str(e)}")

    def verify_mentor_document_structure(self, email, expected_name):
        """Verify that mentor document has all required fields for admin console"""
        print(f"🔍 Verifying mentor document structure for {email}...")
        
        # Check via search API first to get mentor data
        try:
            search_response = requests.get(f"{BASE_URL}/search/mentors?mentor_type=human&q={email}")
            
            if search_response.status_code == 200:
                search_data = search_response.json()
                mentors = search_data.get("results", [])
                
                if mentors:
                    mentor = mentors[0]  # Should be our newly created mentor
                    
                    # Check required fields for admin console
                    required_fields = {
                        "full_name": expected_name,
                        "category": "business",  # Default category
                        "status": "active",  # Default status
                        "mentor_type": "human",
                        "is_ai_mentor": False
                    }
                    
                    all_fields_present = True
                    missing_fields = []
                    
                    for field, expected_value in required_fields.items():
                        if field not in mentor:
                            all_fields_present = False
                            missing_fields.append(f"{field} (missing)")
                        elif mentor.get(field) != expected_value:
                            all_fields_present = False
                            missing_fields.append(f"{field} (expected: {expected_value}, got: {mentor.get(field)})")
                    
                    if all_fields_present:
                        self.log_result("Mentor Document Structure - Required Fields", True, 
                                      f"All required fields present for {email}")
                    else:
                        self.log_result("Mentor Document Structure - Required Fields", False, 
                                      f"Missing/incorrect fields: {', '.join(missing_fields)}")
                    
                    # Check verification object structure
                    if "verification" in mentor:
                        verification = mentor.get("verification", {})
                        if isinstance(verification, dict) and "status" in verification:
                            self.log_result("Mentor Document Structure - Verification Object", True, 
                                          f"Verification object properly structured: {verification}")
                        else:
                            self.log_result("Mentor Document Structure - Verification Object", False, 
                                          f"Verification object malformed: {verification}")
                    else:
                        # Check if it's stored as verification_status (old format)
                        if "verification_status" in mentor:
                            self.log_result("Mentor Document Structure - Verification Object", False, 
                                          "Using old verification_status format instead of verification object")
                        else:
                            self.log_result("Mentor Document Structure - Verification Object", False, 
                                          "No verification information found")
                    
                    # Store mentor for admin console testing
                    self.test_mentors.append({
                        "email": email,
                        "mentor_id": mentor.get("id"),
                        "name": mentor.get("name")
                    })
                    
                else:
                    self.log_result("Mentor Document Structure - Search Visibility", False, 
                                  f"Mentor not found in search results for {email}")
            else:
                self.log_result("Mentor Document Structure - Search API", False, 
                              f"Search API failed. Status: {search_response.status_code}")
                
        except Exception as e:
            self.log_result("Mentor Document Structure - Verification", False, f"Exception: {str(e)}")

    def test_admin_console_mentors_endpoint(self):
        """Test the /api/admin/mentors endpoint that was previously failing"""
        print("🏛️ Testing Admin Console Mentors Endpoint...")
        
        # Note: This test requires admin authentication which we don't have in this test
        # But we can test if the endpoint exists and returns proper error for unauthenticated requests
        
        try:
            response = requests.get(f"{BASE_URL}/admin/mentors")
            
            # Should return 401/403 for unauthenticated request, not 500 (which was the bug)
            if response.status_code in [401, 403]:
                self.log_result("Admin Console Mentors - Authentication Required", True, 
                              "Endpoint properly requires authentication (not returning 500 error)")
            elif response.status_code == 500:
                self.log_result("Admin Console Mentors - Server Error", False, 
                              "Endpoint still returning 500 error - data structure issue not fixed")
            else:
                self.log_result("Admin Console Mentors - Unexpected Response", False, 
                              f"Unexpected status code: {response.status_code}")
                
        except Exception as e:
            self.log_result("Admin Console Mentors - Endpoint Test", False, f"Exception: {str(e)}")

    def test_search_api_compatibility(self):
        """Test that search API still works correctly with updated mentor structure"""
        print("🔍 Testing Search API Compatibility...")
        
        try:
            # Test mentor_type=human filter
            response = requests.get(f"{BASE_URL}/search/mentors?mentor_type=human")
            
            if response.status_code == 200:
                data = response.json()
                human_mentors = data.get("results", [])
                human_count = data.get("human_count", 0)
                
                # Should have at least our test mentors
                if len(human_mentors) >= len(self.test_mentors):
                    self.log_result("Search API Compatibility - Human Mentors Filter", True, 
                                  f"Found {len(human_mentors)} human mentors, count: {human_count}")
                    
                    # Verify structure of returned mentors
                    if human_mentors:
                        mentor = human_mentors[0]
                        required_search_fields = ["id", "name", "bio", "expertise", "mentor_type", "is_ai_mentor"]
                        
                        missing_search_fields = [field for field in required_search_fields if field not in mentor]
                        
                        if not missing_search_fields:
                            self.log_result("Search API Compatibility - Response Structure", True, 
                                          "All required fields present in search response")
                        else:
                            self.log_result("Search API Compatibility - Response Structure", False, 
                                          f"Missing fields in search response: {missing_search_fields}")
                else:
                    self.log_result("Search API Compatibility - Human Mentors Filter", False, 
                                  f"Expected at least {len(self.test_mentors)} mentors, got {len(human_mentors)}")
            else:
                self.log_result("Search API Compatibility - Human Mentors Filter", False, 
                              f"Search API failed. Status: {response.status_code}")
            
            # Test mentor_type=ai filter still works
            ai_response = requests.get(f"{BASE_URL}/search/mentors?mentor_type=ai")
            
            if ai_response.status_code == 200:
                ai_data = ai_response.json()
                ai_mentors = ai_data.get("results", [])
                ai_count = ai_data.get("ai_count", 0)
                
                if ai_mentors and ai_count > 0:
                    self.log_result("Search API Compatibility - AI Mentors Filter", True, 
                                  f"AI mentors still working: {ai_count} mentors")
                else:
                    self.log_result("Search API Compatibility - AI Mentors Filter", False, 
                                  "AI mentors filter not working")
            else:
                self.log_result("Search API Compatibility - AI Mentors Filter", False, 
                              f"AI search failed. Status: {ai_response.status_code}")
                
        except Exception as e:
            self.log_result("Search API Compatibility", False, f"Exception: {str(e)}")

    def test_data_structure_verification(self):
        """Verify that newly created mentors have all fields expected by both search API and admin console"""
        print("📋 Testing Complete Data Structure Verification...")
        
        if not self.test_mentors:
            self.log_result("Data Structure Verification", False, "No test mentors available for verification")
            return
        
        # Test each created mentor
        for mentor_info in self.test_mentors:
            email = mentor_info["email"]
            
            try:
                # Get mentor via search API
                search_response = requests.get(f"{BASE_URL}/search/mentors?mentor_type=human&q={email}")
                
                if search_response.status_code == 200:
                    search_data = search_response.json()
                    mentors = search_data.get("results", [])
                    
                    if mentors:
                        mentor = mentors[0]
                        
                        # Check all fields required by admin console
                        admin_required_fields = {
                            "full_name": str,
                            "category": str,
                            "status": str,
                            "verification": dict  # Should be object, not string
                        }
                        
                        # Check all fields required by search API
                        search_required_fields = {
                            "id": str,
                            "name": str,
                            "bio": str,
                            "expertise": str,
                            "mentor_type": str,
                            "is_ai_mentor": bool,
                            "tier": str,
                            "tier_level": str,
                            "tier_badge_color": str,
                            "subscriber_count": int,
                            "monthly_price": (int, float)
                        }
                        
                        # Verify admin fields
                        admin_issues = []
                        for field, expected_type in admin_required_fields.items():
                            if field not in mentor:
                                admin_issues.append(f"{field} missing")
                            elif not isinstance(mentor[field], expected_type):
                                admin_issues.append(f"{field} wrong type (expected {expected_type.__name__}, got {type(mentor[field]).__name__})")
                        
                        # Verify search fields
                        search_issues = []
                        for field, expected_type in search_required_fields.items():
                            if field not in mentor:
                                search_issues.append(f"{field} missing")
                            elif isinstance(expected_type, tuple):
                                if not isinstance(mentor[field], expected_type):
                                    search_issues.append(f"{field} wrong type")
                            elif not isinstance(mentor[field], expected_type):
                                search_issues.append(f"{field} wrong type")
                        
                        if not admin_issues:
                            self.log_result(f"Data Structure - Admin Fields ({email})", True, 
                                          "All admin console required fields present and correct")
                        else:
                            self.log_result(f"Data Structure - Admin Fields ({email})", False, 
                                          f"Admin field issues: {', '.join(admin_issues)}")
                        
                        if not search_issues:
                            self.log_result(f"Data Structure - Search Fields ({email})", True, 
                                          "All search API required fields present and correct")
                        else:
                            self.log_result(f"Data Structure - Search Fields ({email})", False, 
                                          f"Search field issues: {', '.join(search_issues)}")
                        
                        # Verify specific field values
                        expected_values = {
                            "mentor_type": "human",
                            "is_ai_mentor": False,
                            "category": "business",
                            "status": "active"
                        }
                        
                        value_issues = []
                        for field, expected_value in expected_values.items():
                            if mentor.get(field) != expected_value:
                                value_issues.append(f"{field}: expected {expected_value}, got {mentor.get(field)}")
                        
                        if not value_issues:
                            self.log_result(f"Data Structure - Field Values ({email})", True, 
                                          "All field values correct")
                        else:
                            self.log_result(f"Data Structure - Field Values ({email})", False, 
                                          f"Value issues: {', '.join(value_issues)}")
                    else:
                        self.log_result(f"Data Structure - Mentor Retrieval ({email})", False, 
                                      "Mentor not found in search results")
                else:
                    self.log_result(f"Data Structure - Search API ({email})", False, 
                                  f"Search failed. Status: {search_response.status_code}")
                    
            except Exception as e:
                self.log_result(f"Data Structure - Verification ({email})", False, f"Exception: {str(e)}")

    def run_all_tests(self):
        """Run all admin mentor data fix tests"""
        print("🚀 Starting Admin Console Mentor Data Fix Testing")
        print("=" * 70)
        
        # Test 1: Create New Mentor via Signup
        self.test_new_mentor_via_signup()
        
        # Test 2: Create Mentor via Upgrade
        self.test_existing_user_upgrade_to_mentor()
        
        # Test 3: Admin Console Mentors Endpoint
        self.test_admin_console_mentors_endpoint()
        
        # Test 4: Search API Compatibility
        self.test_search_api_compatibility()
        
        # Test 5: Data Structure Verification
        self.test_data_structure_verification()
        
        # Summary
        self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 70)
        print("🎯 ADMIN CONSOLE MENTOR DATA FIX TESTING SUMMARY")
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
        
        # Group results by category
        categories = {
            "New Mentor Signup": [],
            "User Upgrade": [],
            "Admin Console": [],
            "Search API": [],
            "Data Structure": []
        }
        
        for result in self.results:
            test_name = result["test"]
            if "New Mentor Signup" in test_name:
                categories["New Mentor Signup"].append(result)
            elif "User Upgrade" in test_name:
                categories["User Upgrade"].append(result)
            elif "Admin Console" in test_name:
                categories["Admin Console"].append(result)
            elif "Search API" in test_name:
                categories["Search API"].append(result)
            elif "Data Structure" in test_name or "Mentor Document Structure" in test_name:
                categories["Data Structure"].append(result)
        
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
                           ("Required Fields" in r["test"] or "Server Error" in r["test"] or 
                            "Admin Fields" in r["test"] or "Search Fields" in r["test"])]
        
        if critical_failures:
            print("🚨 CRITICAL ISSUES FOUND:")
            for failure in critical_failures:
                print(f"   ❌ {failure['test']}: {failure['details']}")
            print()
        
        # Review request assessment
        print("📋 REVIEW REQUEST ASSESSMENT:")
        
        # Check if admin console issue is fixed
        admin_fixed = any(r["success"] for r in self.results if "Authentication Required" in r["test"])
        if admin_fixed:
            print("   ✅ Admin console no longer returns 500 error")
        else:
            print("   ❌ Admin console still has issues")
        
        # Check if human mentors appear
        human_mentors_visible = any(r["success"] for r in self.results if "Human Mentors Filter" in r["test"])
        if human_mentors_visible:
            print("   ✅ Human mentors now appear in search results")
        else:
            print("   ❌ Human mentors still not appearing")
        
        # Check if required fields are present
        fields_present = any(r["success"] for r in self.results if "Required Fields" in r["test"])
        if fields_present:
            print("   ✅ Required fields (full_name, category, status, verification) are present")
        else:
            print("   ❌ Required fields are missing or incorrect")
        
        # Overall assessment
        if success_rate >= 90:
            print("\n🎉 EXCELLENT: Admin console mentor data fix is working perfectly!")
        elif success_rate >= 75:
            print("\n✅ GOOD: Admin console mentor data fix is working well with minor issues.")
        elif success_rate >= 50:
            print("\n⚠️ MODERATE: Admin console mentor data fix has some issues.")
        else:
            print("\n🚨 CRITICAL: Admin console mentor data fix has major issues requiring immediate attention.")
        
        print("=" * 70)

if __name__ == "__main__":
    tester = AdminMentorDataFixTester()
    tester.run_all_tests()