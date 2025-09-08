#!/usr/bin/env python3
"""
Detailed Admin Console Mentor Data Fix Testing
More thorough testing with database verification and timing considerations
"""

import requests
import json
import time
import uuid
from datetime import datetime

# Configuration
BASE_URL = "https://enterprise-coach.preview.emergentagent.com/api"

class DetailedMentorFixTester:
    def __init__(self):
        self.results = []
        self.test_mentor_email = None
        self.test_mentor_token = None
        
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

    def test_mentor_signup_with_detailed_verification(self):
        """Test mentor signup with detailed field verification"""
        print("🔍 Testing Mentor Signup with Detailed Verification...")
        
        # Generate unique test data
        timestamp = int(time.time())
        self.test_mentor_email = f"detailed.mentor.{timestamp}@test.com"
        test_name = f"Detailed Test Mentor {timestamp}"
        
        signup_data = {
            "email": self.test_mentor_email,
            "password": "TestPass123!",
            "full_name": test_name,
            "phone_number": "+1234567892",
            "communication_preferences": json.dumps({"email": True, "text": False}),
            "subscription_plan": "free",
            "become_mentor": True
        }
        
        try:
            response = requests.post(f"{BASE_URL}/auth/register", data=signup_data)
            
            if response.status_code in [200, 201]:
                data = response.json()
                user_data = data.get("user", {})
                self.test_mentor_token = data.get("token")
                
                # Verify mentor flag is set
                is_mentor = user_data.get("is_mentor", False)
                
                if is_mentor:
                    self.log_result("Detailed Mentor Signup - User Creation", True, 
                                  f"User created with mentor flag: {user_data.get('user_id')}")
                    
                    # Wait a moment for database consistency
                    print("⏳ Waiting for database consistency...")
                    time.sleep(3)
                    
                    # Now test search with multiple approaches
                    self.test_mentor_search_visibility(test_name)
                    
                else:
                    self.log_result("Detailed Mentor Signup - User Creation", False, 
                                  "User created but mentor flag not set")
            else:
                self.log_result("Detailed Mentor Signup - User Creation", False, 
                              f"Status: {response.status_code}", response.text)
                
        except Exception as e:
            self.log_result("Detailed Mentor Signup - User Creation", False, f"Exception: {str(e)}")

    def test_mentor_search_visibility(self, expected_name):
        """Test mentor visibility in search with multiple search methods"""
        print("🔍 Testing Mentor Search Visibility...")
        
        # Test 1: Search by email
        try:
            email_search = requests.get(f"{BASE_URL}/search/mentors?mentor_type=human&q={self.test_mentor_email}")
            
            if email_search.status_code == 200:
                data = email_search.json()
                mentors = data.get("results", [])
                
                if mentors:
                    mentor = mentors[0]
                    self.log_result("Mentor Search - Email Search", True, 
                                  f"Found mentor by email: {mentor.get('name')}")
                    self.verify_mentor_fields(mentor, expected_name)
                else:
                    self.log_result("Mentor Search - Email Search", False, 
                                  f"Mentor not found by email search")
            else:
                self.log_result("Mentor Search - Email Search", False, 
                              f"Email search failed. Status: {email_search.status_code}")
        except Exception as e:
            self.log_result("Mentor Search - Email Search", False, f"Exception: {str(e)}")
        
        # Test 2: Search by name
        try:
            name_parts = expected_name.split()
            if name_parts:
                name_search = requests.get(f"{BASE_URL}/search/mentors?mentor_type=human&q={name_parts[0]}")
                
                if name_search.status_code == 200:
                    data = name_search.json()
                    mentors = data.get("results", [])
                    
                    # Look for our mentor in results
                    our_mentor = None
                    for mentor in mentors:
                        if expected_name in mentor.get("name", ""):
                            our_mentor = mentor
                            break
                    
                    if our_mentor:
                        self.log_result("Mentor Search - Name Search", True, 
                                      f"Found mentor by name: {our_mentor.get('name')}")
                        self.verify_mentor_fields(our_mentor, expected_name)
                    else:
                        self.log_result("Mentor Search - Name Search", False, 
                                      f"Mentor not found by name search. Found {len(mentors)} mentors")
                else:
                    self.log_result("Mentor Search - Name Search", False, 
                                  f"Name search failed. Status: {name_search.status_code}")
        except Exception as e:
            self.log_result("Mentor Search - Name Search", False, f"Exception: {str(e)}")
        
        # Test 3: General human mentors search
        try:
            general_search = requests.get(f"{BASE_URL}/search/mentors?mentor_type=human")
            
            if general_search.status_code == 200:
                data = general_search.json()
                mentors = data.get("results", [])
                human_count = data.get("human_count", 0)
                
                # Look for our mentor in results
                our_mentor = None
                for mentor in mentors:
                    if expected_name in mentor.get("name", "") or self.test_mentor_email in mentor.get("name", ""):
                        our_mentor = mentor
                        break
                
                if our_mentor:
                    self.log_result("Mentor Search - General Human Search", True, 
                                  f"Found mentor in general search. Total human mentors: {human_count}")
                    self.verify_mentor_fields(our_mentor, expected_name)
                else:
                    self.log_result("Mentor Search - General Human Search", False, 
                                  f"Mentor not found in general search. Total human mentors: {human_count}")
                    
                    # Debug: Show first few mentors
                    if mentors:
                        print(f"   Debug: First few mentors found:")
                        for i, mentor in enumerate(mentors[:3]):
                            print(f"     {i+1}. {mentor.get('name', 'No name')} - {mentor.get('id', 'No ID')}")
            else:
                self.log_result("Mentor Search - General Human Search", False, 
                              f"General search failed. Status: {general_search.status_code}")
        except Exception as e:
            self.log_result("Mentor Search - General Human Search", False, f"Exception: {str(e)}")

    def verify_mentor_fields(self, mentor, expected_name):
        """Verify mentor has all required fields for admin console"""
        print("📋 Verifying Mentor Fields...")
        
        # Required fields for admin console
        admin_required_fields = {
            "full_name": expected_name,
            "category": "business",  # Default category
            "status": "active"  # Default status
        }
        
        # Check each required field
        field_issues = []
        for field, expected_value in admin_required_fields.items():
            if field not in mentor:
                field_issues.append(f"{field} missing")
            elif mentor.get(field) != expected_value:
                field_issues.append(f"{field}: expected '{expected_value}', got '{mentor.get(field)}'")
        
        if not field_issues:
            self.log_result("Mentor Fields - Admin Required Fields", True, 
                          "All admin console required fields present and correct")
        else:
            self.log_result("Mentor Fields - Admin Required Fields", False, 
                          f"Field issues: {', '.join(field_issues)}")
        
        # Check verification object structure
        verification = mentor.get("verification")
        if verification:
            if isinstance(verification, dict):
                if "status" in verification:
                    self.log_result("Mentor Fields - Verification Object", True, 
                                  f"Verification object properly structured: {verification}")
                else:
                    self.log_result("Mentor Fields - Verification Object", False, 
                                  f"Verification object missing status field: {verification}")
            else:
                self.log_result("Mentor Fields - Verification Object", False, 
                              f"Verification is not an object: {type(verification)} - {verification}")
        else:
            # Check if using old format
            verification_status = mentor.get("verification_status")
            if verification_status:
                self.log_result("Mentor Fields - Verification Object", False, 
                              f"Using old verification_status format: {verification_status}")
            else:
                self.log_result("Mentor Fields - Verification Object", False, 
                              "No verification information found")
        
        # Check mentor type fields
        mentor_type = mentor.get("mentor_type")
        is_ai_mentor = mentor.get("is_ai_mentor")
        
        if mentor_type == "human" and is_ai_mentor == False:
            self.log_result("Mentor Fields - Mentor Type", True, 
                          f"Mentor type correctly set: {mentor_type}, is_ai_mentor: {is_ai_mentor}")
        else:
            self.log_result("Mentor Fields - Mentor Type", False, 
                          f"Mentor type incorrect: {mentor_type}, is_ai_mentor: {is_ai_mentor}")
        
        # Check tier information
        tier_fields = ["tier", "tier_level", "tier_badge_color", "subscriber_count", "monthly_price"]
        missing_tier_fields = [field for field in tier_fields if field not in mentor]
        
        if not missing_tier_fields:
            self.log_result("Mentor Fields - Tier Information", True, 
                          f"All tier fields present. Tier: {mentor.get('tier')}")
        else:
            self.log_result("Mentor Fields - Tier Information", False, 
                          f"Missing tier fields: {missing_tier_fields}")

    def test_admin_console_endpoint_detailed(self):
        """Test admin console endpoint with more detailed analysis"""
        print("🏛️ Testing Admin Console Endpoint (Detailed)...")
        
        try:
            response = requests.get(f"{BASE_URL}/admin/mentors")
            
            if response.status_code == 401:
                self.log_result("Admin Console - Authentication Check", True, 
                              "Endpoint correctly requires authentication (401)")
            elif response.status_code == 403:
                self.log_result("Admin Console - Authentication Check", True, 
                              "Endpoint correctly requires authentication (403)")
            elif response.status_code == 500:
                # This was the original bug - server error due to missing fields
                self.log_result("Admin Console - Server Error Bug", False, 
                              "Endpoint still returning 500 error - data structure issue not fixed")
                
                # Try to get more details about the error
                try:
                    error_text = response.text
                    if "full_name" in error_text:
                        self.log_result("Admin Console - Error Analysis", False, 
                                      "Error mentions 'full_name' - field missing in mentor documents")
                    elif "category" in error_text:
                        self.log_result("Admin Console - Error Analysis", False, 
                                      "Error mentions 'category' - field missing in mentor documents")
                    elif "verification" in error_text:
                        self.log_result("Admin Console - Error Analysis", False, 
                                      "Error mentions 'verification' - verification object structure issue")
                    else:
                        self.log_result("Admin Console - Error Analysis", False, 
                                      f"500 error with message: {error_text[:200]}")
                except:
                    self.log_result("Admin Console - Error Analysis", False, 
                                  "500 error but couldn't parse error message")
            else:
                self.log_result("Admin Console - Unexpected Response", False, 
                              f"Unexpected status code: {response.status_code}")
                
        except Exception as e:
            self.log_result("Admin Console - Endpoint Test", False, f"Exception: {str(e)}")

    def test_existing_mentor_upgrade(self):
        """Test the existing user upgrade to mentor functionality"""
        print("🔄 Testing Existing User Upgrade to Mentor...")
        
        # Create a regular user first
        timestamp = int(time.time())
        upgrade_email = f"upgrade.test.{timestamp}@test.com"
        upgrade_name = f"Upgrade Test User {timestamp}"
        
        signup_data = {
            "email": upgrade_email,
            "password": "TestPass123!",
            "full_name": upgrade_name,
            "phone_number": "+1234567893",
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
            
            # Now upgrade to mentor
            headers = {"Authorization": f"Bearer {user_token}"}
            upgrade_response = requests.post(f"{BASE_URL}/users/become-mentor", headers=headers)
            
            if upgrade_response.status_code == 200:
                upgrade_data = upgrade_response.json()
                creator_id = upgrade_data.get("creator_id")
                
                if creator_id:
                    self.log_result("User Upgrade - Mentor Upgrade", True, 
                                  f"User upgraded to mentor: {creator_id}")
                    
                    # Wait for database consistency
                    print("⏳ Waiting for database consistency...")
                    time.sleep(3)
                    
                    # Verify the upgraded mentor appears in search
                    self.verify_upgraded_mentor_search(upgrade_email, upgrade_name)
                    
                else:
                    self.log_result("User Upgrade - Mentor Upgrade", False, 
                                  "Upgrade response missing creator_id")
            else:
                self.log_result("User Upgrade - Mentor Upgrade", False, 
                              f"Upgrade failed. Status: {upgrade_response.status_code}", upgrade_response.text)
                
        except Exception as e:
            self.log_result("User Upgrade - Process", False, f"Exception: {str(e)}")

    def verify_upgraded_mentor_search(self, email, name):
        """Verify upgraded mentor appears in search with correct fields"""
        print("🔍 Verifying Upgraded Mentor in Search...")
        
        try:
            search_response = requests.get(f"{BASE_URL}/search/mentors?mentor_type=human&q={email}")
            
            if search_response.status_code == 200:
                data = search_response.json()
                mentors = data.get("results", [])
                
                if mentors:
                    mentor = mentors[0]
                    self.log_result("Upgraded Mentor - Search Visibility", True, 
                                  f"Upgraded mentor found: {mentor.get('name')}")
                    
                    # Verify fields for upgraded mentor
                    self.verify_mentor_fields(mentor, name)
                else:
                    self.log_result("Upgraded Mentor - Search Visibility", False, 
                                  f"Upgraded mentor not found in search")
            else:
                self.log_result("Upgraded Mentor - Search API", False, 
                              f"Search failed. Status: {search_response.status_code}")
                
        except Exception as e:
            self.log_result("Upgraded Mentor - Verification", False, f"Exception: {str(e)}")

    def test_search_api_comprehensive(self):
        """Comprehensive test of search API functionality"""
        print("🔍 Testing Search API Comprehensively...")
        
        # Test all mentor types
        mentor_types = ["ai", "human", "all"]
        
        for mentor_type in mentor_types:
            try:
                response = requests.get(f"{BASE_URL}/search/mentors?mentor_type={mentor_type}")
                
                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results", [])
                    count = data.get("count", 0)
                    ai_count = data.get("ai_count", 0)
                    human_count = data.get("human_count", 0)
                    
                    self.log_result(f"Search API - {mentor_type.upper()} Filter", True, 
                                  f"Results: {len(results)}, Count: {count}, AI: {ai_count}, Human: {human_count}")
                    
                    # Verify response structure
                    required_response_fields = ["results", "count", "query", "mentor_type_filter", "ai_count", "human_count"]
                    missing_fields = [field for field in required_response_fields if field not in data]
                    
                    if not missing_fields:
                        self.log_result(f"Search API - {mentor_type.upper()} Response Structure", True, 
                                      "All required response fields present")
                    else:
                        self.log_result(f"Search API - {mentor_type.upper()} Response Structure", False, 
                                      f"Missing response fields: {missing_fields}")
                    
                    # Verify mentor data structure if results exist
                    if results:
                        mentor = results[0]
                        required_mentor_fields = ["id", "name", "bio", "expertise", "mentor_type", "is_ai_mentor"]
                        missing_mentor_fields = [field for field in required_mentor_fields if field not in mentor]
                        
                        if not missing_mentor_fields:
                            self.log_result(f"Search API - {mentor_type.upper()} Mentor Structure", True, 
                                          "All required mentor fields present")
                        else:
                            self.log_result(f"Search API - {mentor_type.upper()} Mentor Structure", False, 
                                          f"Missing mentor fields: {missing_mentor_fields}")
                else:
                    self.log_result(f"Search API - {mentor_type.upper()} Filter", False, 
                                  f"API failed. Status: {response.status_code}")
                    
            except Exception as e:
                self.log_result(f"Search API - {mentor_type.upper()} Filter", False, f"Exception: {str(e)}")

    def run_all_tests(self):
        """Run all detailed tests"""
        print("🚀 Starting Detailed Admin Console Mentor Data Fix Testing")
        print("=" * 80)
        
        # Test 1: Mentor signup with detailed verification
        self.test_mentor_signup_with_detailed_verification()
        
        # Test 2: Admin console endpoint detailed analysis
        self.test_admin_console_endpoint_detailed()
        
        # Test 3: Existing user upgrade to mentor
        self.test_existing_mentor_upgrade()
        
        # Test 4: Comprehensive search API testing
        self.test_search_api_comprehensive()
        
        # Summary
        self.print_summary()

    def print_summary(self):
        """Print detailed test summary"""
        print("\n" + "=" * 80)
        print("🎯 DETAILED ADMIN CONSOLE MENTOR DATA FIX TESTING SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        print()
        
        # Critical findings
        critical_issues = []
        
        # Check for admin console 500 error
        admin_500_error = any(r for r in self.results if not r["success"] and "Server Error Bug" in r["test"])
        if admin_500_error:
            critical_issues.append("Admin console still returns 500 error - data structure not fixed")
        
        # Check for missing required fields
        missing_fields = any(r for r in self.results if not r["success"] and "Admin Required Fields" in r["test"])
        if missing_fields:
            critical_issues.append("Required admin console fields (full_name, category, status) are missing")
        
        # Check for verification object issues
        verification_issues = any(r for r in self.results if not r["success"] and "Verification Object" in r["test"])
        if verification_issues:
            critical_issues.append("Verification object structure is incorrect")
        
        # Check for search visibility issues
        search_issues = any(r for r in self.results if not r["success"] and "Search Visibility" in r["test"])
        if search_issues:
            critical_issues.append("Newly created mentors not appearing in search results")
        
        if critical_issues:
            print("🚨 CRITICAL ISSUES IDENTIFIED:")
            for issue in critical_issues:
                print(f"   ❌ {issue}")
            print()
        
        # Success indicators
        success_indicators = []
        
        # Check if admin console authentication works (not 500)
        admin_auth_works = any(r["success"] for r in self.results if "Authentication Check" in r["test"])
        if admin_auth_works:
            success_indicators.append("Admin console endpoint no longer returns 500 error")
        
        # Check if human mentors are visible
        human_mentors_visible = any(r["success"] for r in self.results if "Human" in r["test"] and "Filter" in r["test"])
        if human_mentors_visible:
            success_indicators.append("Human mentors are visible in search results")
        
        # Check if mentor creation works
        mentor_creation_works = any(r["success"] for r in self.results if "User Creation" in r["test"] or "Mentor Upgrade" in r["test"])
        if mentor_creation_works:
            success_indicators.append("Mentor creation process is working")
        
        if success_indicators:
            print("✅ SUCCESS INDICATORS:")
            for indicator in success_indicators:
                print(f"   ✅ {indicator}")
            print()
        
        # Review request assessment
        print("📋 REVIEW REQUEST ASSESSMENT:")
        print("   Required Changes:")
        print("   1. Added full_name field (admin console requirement)")
        print("   2. Added category field with default 'business'")
        print("   3. Added status field with default 'active'")
        print("   4. Added verification object structure")
        print("   5. Applied to both signup and upgrade paths")
        print()
        
        # Check each requirement
        requirements_met = 0
        total_requirements = 5
        
        if not admin_500_error:
            print("   ✅ Admin console no longer returns 500 error")
            requirements_met += 1
        else:
            print("   ❌ Admin console still returns 500 error")
        
        if human_mentors_visible:
            print("   ✅ Human mentors appear in search results")
            requirements_met += 1
        else:
            print("   ❌ Human mentors not appearing in search results")
        
        if mentor_creation_works:
            print("   ✅ Mentor creation processes are working")
            requirements_met += 1
        else:
            print("   ❌ Mentor creation processes have issues")
        
        if not missing_fields:
            print("   ✅ Required fields (full_name, category, status) are present")
            requirements_met += 1
        else:
            print("   ❌ Required fields are missing or incorrect")
        
        if not verification_issues:
            print("   ✅ Verification object structure is correct")
            requirements_met += 1
        else:
            print("   ❌ Verification object structure needs fixing")
        
        print(f"\n📊 Requirements Met: {requirements_met}/{total_requirements} ({requirements_met/total_requirements*100:.1f}%)")
        
        # Overall assessment
        if success_rate >= 90 and requirements_met >= 4:
            print("\n🎉 EXCELLENT: Admin console mentor data fix is working perfectly!")
        elif success_rate >= 75 and requirements_met >= 3:
            print("\n✅ GOOD: Admin console mentor data fix is mostly working with minor issues.")
        elif success_rate >= 50 and requirements_met >= 2:
            print("\n⚠️ MODERATE: Admin console mentor data fix has some significant issues.")
        else:
            print("\n🚨 CRITICAL: Admin console mentor data fix has major issues requiring immediate attention.")
        
        print("=" * 80)

if __name__ == "__main__":
    tester = DetailedMentorFixTester()
    tester.run_all_tests()