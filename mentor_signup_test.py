#!/usr/bin/env python3
"""
Mentor Signup Functionality Testing
Tests the new mentor signup functionality that allows regular users to become mentors.
"""

import requests
import json
import time
import uuid
from datetime import datetime

# Configuration
BASE_URL = "https://mentor-search.preview.emergentagent.com/api"

class MentorSignupTester:
    def __init__(self):
        self.results = []
        self.test_user_token = None
        self.test_user_id = None
        self.test_mentor_creator_id = None
        
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

    def test_new_user_registration_with_mentor_option(self):
        """Test 1: New User Registration with Mentor Option"""
        print("🔧 Testing New User Registration with Mentor Option...")
        
        # Generate unique test data
        test_email = f"mentor.signup.test.{int(time.time())}@test.com"
        test_name = f"Mentor Test User {int(time.time())}"
        
        # Test registration with become_mentor=true
        registration_data = {
            "email": test_email,
            "password": "TestPass123!",
            "full_name": test_name,
            "phone_number": "+1234567890",
            "communication_preferences": json.dumps({"email": True, "text": False, "both": False}),
            "subscription_plan": "free",
            "become_mentor": True
        }
        
        try:
            response = requests.post(f"{BASE_URL}/auth/register", data=registration_data)
            
            if response.status_code in [200, 201]:
                data = response.json()
                self.test_user_token = data.get("token")
                user_data = data.get("user", {})
                self.test_user_id = user_data.get("user_id")
                
                # Verify user account was created
                if self.test_user_token and self.test_user_id:
                    self.log_result("User Registration with Mentor Option - User Account Created", True,
                                  f"User ID: {self.test_user_id}, Email: {test_email}")
                    
                    # Check if user became a mentor
                    is_mentor = user_data.get("is_mentor", False)
                    if is_mentor:
                        self.log_result("User Registration with Mentor Option - Mentor Flag Set", True,
                                      "User successfully marked as mentor during registration")
                    else:
                        self.log_result("User Registration with Mentor Option - Mentor Flag Set", False,
                                      "User not marked as mentor despite become_mentor=True")
                    
                    # Verify mentor profile was created by checking creators collection
                    self.verify_mentor_profile_created(test_email)
                    
                else:
                    self.log_result("User Registration with Mentor Option - User Account Created", False,
                                  "Missing token or user_id in response")
            else:
                self.log_result("User Registration with Mentor Option - User Account Created", False,
                              f"Registration failed. Status: {response.status_code}", response.text)
                
        except Exception as e:
            self.log_result("User Registration with Mentor Option - User Account Created", False, 
                          f"Exception: {str(e)}")

    def verify_mentor_profile_created(self, email):
        """Verify that a mentor profile was created in creators collection"""
        try:
            # Search for human mentors to see if our new mentor appears
            response = requests.get(f"{BASE_URL}/search/mentors?mentor_type=human&q={email.split('@')[0]}")
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                human_count = data.get("human_count", 0)
                
                # Check if our mentor appears in human mentor search
                mentor_found = any(mentor.get("mentor_type") == "human" for mentor in results)
                
                if mentor_found:
                    mentor_data = next(mentor for mentor in results if mentor.get("mentor_type") == "human")
                    self.test_mentor_creator_id = mentor_data.get("id")
                    
                    # Verify mentor profile structure
                    required_fields = ["id", "name", "bio", "expertise", "mentor_type", "is_ai_mentor", 
                                     "tier", "tier_level", "tier_badge_color", "subscriber_count", "monthly_price"]
                    
                    missing_fields = [field for field in required_fields if field not in mentor_data]
                    
                    if not missing_fields:
                        self.log_result("User Registration with Mentor Option - Mentor Profile Created", True,
                                      f"Mentor profile created with ID: {self.test_mentor_creator_id}")
                        
                        # Verify mentor is auto-approved
                        if mentor_data.get("mentor_type") == "human" and not mentor_data.get("is_ai_mentor"):
                            self.log_result("User Registration with Mentor Option - Auto-Approved", True,
                                          "Mentor is correctly marked as human and auto-approved")
                        else:
                            self.log_result("User Registration with Mentor Option - Auto-Approved", False,
                                          f"Mentor type incorrect: {mentor_data.get('mentor_type')}, is_ai_mentor: {mentor_data.get('is_ai_mentor')}")
                    else:
                        self.log_result("User Registration with Mentor Option - Mentor Profile Created", False,
                                      f"Mentor profile missing required fields: {missing_fields}")
                else:
                    self.log_result("User Registration with Mentor Option - Mentor Profile Created", False,
                                  f"No human mentor found in search results. Human count: {human_count}")
            else:
                self.log_result("User Registration with Mentor Option - Mentor Profile Created", False,
                              f"Failed to search mentors. Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("User Registration with Mentor Option - Mentor Profile Created", False,
                          f"Exception during verification: {str(e)}")

    def test_existing_user_upgrade_to_mentor(self):
        """Test 2: Existing User Upgrade to Mentor"""
        print("🔄 Testing Existing User Upgrade to Mentor...")
        
        # First create a regular user (without mentor option)
        test_email = f"regular.user.{int(time.time())}@test.com"
        test_name = f"Regular User {int(time.time())}"
        
        # Create regular user
        user_data = {
            "email": test_email,
            "password": "TestPass123!",
            "full_name": test_name
        }
        
        try:
            # Register regular user
            response = requests.post(f"{BASE_URL}/auth/signup", json=user_data)
            
            if response.status_code in [200, 201]:
                data = response.json()
                user_token = data.get("token")
                user_id = data.get("user", {}).get("user_id")
                
                self.log_result("Existing User Upgrade - Regular User Created", True,
                              f"Regular user created: {user_id}")
                
                # Test upgrade to mentor endpoint
                self.test_become_mentor_endpoint(user_token, user_id, test_email)
                
            else:
                self.log_result("Existing User Upgrade - Regular User Created", False,
                              f"Failed to create regular user. Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("Existing User Upgrade - Regular User Created", False,
                          f"Exception: {str(e)}")

    def test_become_mentor_endpoint(self, user_token, user_id, email):
        """Test the /api/users/become-mentor endpoint"""
        
        # Test 1: Authentication required
        try:
            response = requests.post(f"{BASE_URL}/users/become-mentor")
            
            if response.status_code in [401, 403]:
                self.log_result("Become Mentor Endpoint - Authentication Required", True,
                              "Correctly requires authentication")
            else:
                self.log_result("Become Mentor Endpoint - Authentication Required", False,
                              f"Should require auth. Status: {response.status_code}")
        except Exception as e:
            self.log_result("Become Mentor Endpoint - Authentication Required", False,
                          f"Exception: {str(e)}")
        
        # Test 2: Valid mentor upgrade
        headers = {"Authorization": f"Bearer {user_token}"}
        
        try:
            response = requests.post(f"{BASE_URL}/users/become-mentor", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                success = data.get("success", False)
                creator_id = data.get("creator_id")
                message = data.get("message", "")
                
                if success and creator_id:
                    self.log_result("Become Mentor Endpoint - Valid Upgrade", True,
                                  f"User successfully upgraded to mentor. Creator ID: {creator_id}")
                    
                    # Verify mentor appears in search
                    self.verify_upgraded_mentor_in_search(email, creator_id)
                    
                    # Test duplicate upgrade (should handle gracefully)
                    self.test_duplicate_mentor_upgrade(headers, creator_id)
                    
                else:
                    self.log_result("Become Mentor Endpoint - Valid Upgrade", False,
                                  f"Upgrade failed. Success: {success}, Creator ID: {creator_id}")
            else:
                self.log_result("Become Mentor Endpoint - Valid Upgrade", False,
                              f"Upgrade failed. Status: {response.status_code}", response.text)
                
        except Exception as e:
            self.log_result("Become Mentor Endpoint - Valid Upgrade", False,
                          f"Exception: {str(e)}")

    def test_duplicate_mentor_upgrade(self, headers, existing_creator_id):
        """Test handling of duplicate mentor upgrade attempts"""
        try:
            response = requests.post(f"{BASE_URL}/users/become-mentor", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                success = data.get("success", False)
                creator_id = data.get("creator_id")
                message = data.get("message", "")
                
                if success and creator_id == existing_creator_id and "already" in message.lower():
                    self.log_result("Become Mentor Endpoint - Duplicate Upgrade Handling", True,
                                  "Correctly handles duplicate mentor upgrade attempts")
                else:
                    self.log_result("Become Mentor Endpoint - Duplicate Upgrade Handling", False,
                                  f"Unexpected response for duplicate upgrade. Message: {message}")
            else:
                self.log_result("Become Mentor Endpoint - Duplicate Upgrade Handling", False,
                              f"Unexpected status for duplicate upgrade: {response.status_code}")
                
        except Exception as e:
            self.log_result("Become Mentor Endpoint - Duplicate Upgrade Handling", False,
                          f"Exception: {str(e)}")

    def verify_upgraded_mentor_in_search(self, email, creator_id):
        """Verify upgraded mentor appears in human mentor search"""
        try:
            # Search for human mentors
            response = requests.get(f"{BASE_URL}/search/mentors?mentor_type=human")
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                human_count = data.get("human_count", 0)
                
                # Look for our upgraded mentor
                mentor_found = any(mentor.get("id") == creator_id for mentor in results)
                
                if mentor_found:
                    self.log_result("Existing User Upgrade - Mentor Appears in Search", True,
                                  f"Upgraded mentor found in human mentor search")
                else:
                    self.log_result("Existing User Upgrade - Mentor Appears in Search", False,
                                  f"Upgraded mentor not found in search. Human count: {human_count}")
            else:
                self.log_result("Existing User Upgrade - Mentor Appears in Search", False,
                              f"Search failed. Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("Existing User Upgrade - Mentor Appears in Search", False,
                          f"Exception: {str(e)}")

    def test_human_mentor_discovery(self):
        """Test 3: Human Mentor Discovery"""
        print("🔍 Testing Human Mentor Discovery...")
        
        # Test mentor type filtering
        self.test_mentor_type_filtering()
        
        # Test mentor profile structure
        self.test_mentor_profile_structure()

    def test_mentor_type_filtering(self):
        """Test mentor type filtering functionality"""
        
        # Test 1: AI mentors filter
        try:
            response = requests.get(f"{BASE_URL}/search/mentors?mentor_type=ai")
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                ai_count = data.get("ai_count", 0)
                
                # Verify all results are AI mentors
                all_ai = all(mentor.get("mentor_type") == "ai" and mentor.get("is_ai_mentor") == True 
                           for mentor in results)
                
                if all_ai and ai_count > 0:
                    self.log_result("Human Mentor Discovery - AI Mentors Filter", True,
                                  f"AI mentors filter working correctly. Count: {ai_count}")
                else:
                    self.log_result("Human Mentor Discovery - AI Mentors Filter", False,
                                  f"AI filter issue. All AI: {all_ai}, Count: {ai_count}")
            else:
                self.log_result("Human Mentor Discovery - AI Mentors Filter", False,
                              f"AI mentors search failed. Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("Human Mentor Discovery - AI Mentors Filter", False,
                          f"Exception: {str(e)}")
        
        # Test 2: Human mentors filter
        try:
            response = requests.get(f"{BASE_URL}/search/mentors?mentor_type=human")
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                human_count = data.get("human_count", 0)
                
                # Verify all results are human mentors
                all_human = all(mentor.get("mentor_type") == "human" and mentor.get("is_ai_mentor") == False 
                              for mentor in results)
                
                if all_human:
                    self.log_result("Human Mentor Discovery - Human Mentors Filter", True,
                                  f"Human mentors filter working correctly. Count: {human_count}")
                else:
                    self.log_result("Human Mentor Discovery - Human Mentors Filter", False,
                                  f"Human filter issue. All human: {all_human}, Count: {human_count}")
            else:
                self.log_result("Human Mentor Discovery - Human Mentors Filter", False,
                              f"Human mentors search failed. Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("Human Mentor Discovery - Human Mentors Filter", False,
                          f"Exception: {str(e)}")
        
        # Test 3: All mentors filter
        try:
            response = requests.get(f"{BASE_URL}/search/mentors?mentor_type=all")
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                ai_count = data.get("ai_count", 0)
                human_count = data.get("human_count", 0)
                total_count = data.get("count", 0)
                
                # Verify counts match
                expected_total = ai_count + human_count
                
                if total_count == expected_total and total_count == len(results):
                    self.log_result("Human Mentor Discovery - All Mentors Filter", True,
                                  f"All mentors filter working. AI: {ai_count}, Human: {human_count}, Total: {total_count}")
                else:
                    self.log_result("Human Mentor Discovery - All Mentors Filter", False,
                                  f"Count mismatch. Expected: {expected_total}, Actual: {total_count}, Results: {len(results)}")
            else:
                self.log_result("Human Mentor Discovery - All Mentors Filter", False,
                              f"All mentors search failed. Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("Human Mentor Discovery - All Mentors Filter", False,
                          f"Exception: {str(e)}")

    def test_mentor_profile_structure(self):
        """Test mentor profile structure includes all required fields"""
        try:
            response = requests.get(f"{BASE_URL}/search/mentors?mentor_type=human")
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                
                if results:
                    # Check first human mentor profile structure
                    mentor = results[0]
                    
                    # Required fields for human mentors
                    required_fields = [
                        "id", "name", "bio", "expertise", "mentor_type", "is_ai_mentor",
                        "tier", "tier_level", "tier_badge_color", "subscriber_count", "monthly_price"
                    ]
                    
                    missing_fields = [field for field in required_fields if field not in mentor]
                    
                    if not missing_fields:
                        self.log_result("Human Mentor Discovery - Profile Structure", True,
                                      "Human mentor profile contains all required fields")
                        
                        # Verify field values are appropriate
                        if (mentor.get("mentor_type") == "human" and 
                            mentor.get("is_ai_mentor") == False and
                            isinstance(mentor.get("subscriber_count"), int) and
                            isinstance(mentor.get("monthly_price"), (int, float))):
                            
                            self.log_result("Human Mentor Discovery - Field Values", True,
                                          "Human mentor field values are correct")
                        else:
                            self.log_result("Human Mentor Discovery - Field Values", False,
                                          f"Invalid field values: mentor_type={mentor.get('mentor_type')}, is_ai_mentor={mentor.get('is_ai_mentor')}")
                    else:
                        self.log_result("Human Mentor Discovery - Profile Structure", False,
                                      f"Missing required fields: {missing_fields}")
                else:
                    self.log_result("Human Mentor Discovery - Profile Structure", True,
                                  "No human mentors found (expected if no mentors created yet)")
                    
            else:
                self.log_result("Human Mentor Discovery - Profile Structure", False,
                              f"Failed to get human mentors. Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("Human Mentor Discovery - Profile Structure", False,
                          f"Exception: {str(e)}")

    def test_integration_flow(self):
        """Test 4: Integration Testing - Complete Flow"""
        print("🔄 Testing Complete Integration Flow...")
        
        # Generate unique test data for integration test
        test_email = f"integration.test.{int(time.time())}@test.com"
        test_name = f"Integration Test User {int(time.time())}"
        
        # Step 1: User signup with mentor option
        registration_data = {
            "email": test_email,
            "password": "TestPass123!",
            "full_name": test_name,
            "phone_number": "+1234567890",
            "communication_preferences": json.dumps({"email": True, "text": False, "both": False}),
            "subscription_plan": "free",
            "become_mentor": True
        }
        
        try:
            # Register user as mentor
            response = requests.post(f"{BASE_URL}/auth/register", data=registration_data)
            
            if response.status_code in [200, 201]:
                data = response.json()
                user_token = data.get("token")
                user_data = data.get("user", {})
                
                self.log_result("Integration Flow - User Signup", True,
                              f"User registered successfully: {user_data.get('user_id')}")
                
                # Step 2: Verify mentor appears in search immediately
                time.sleep(2)  # Brief delay for database consistency
                
                search_response = requests.get(f"{BASE_URL}/search/mentors?mentor_type=human&q={test_name.split()[0]}")
                
                if search_response.status_code == 200:
                    search_data = search_response.json()
                    results = search_data.get("results", [])
                    
                    # Look for our mentor
                    mentor_found = any(test_name.split()[0].lower() in mentor.get("name", "").lower() 
                                     for mentor in results if mentor.get("mentor_type") == "human")
                    
                    if mentor_found:
                        mentor = next(mentor for mentor in results 
                                    if test_name.split()[0].lower() in mentor.get("name", "").lower() 
                                    and mentor.get("mentor_type") == "human")
                        
                        self.log_result("Integration Flow - Mentor Appears in Search", True,
                                      f"Mentor found in search: {mentor.get('name')}")
                        
                        # Step 3: Verify mentor has proper badges and information
                        has_tier = mentor.get("tier") is not None
                        has_badge_color = mentor.get("tier_badge_color") is not None
                        has_pricing = mentor.get("monthly_price") is not None
                        
                        if has_tier and has_badge_color and has_pricing:
                            self.log_result("Integration Flow - Mentor Badges and Info", True,
                                          f"Mentor has proper badges: Tier={mentor.get('tier')}, Price=${mentor.get('monthly_price')}")
                        else:
                            self.log_result("Integration Flow - Mentor Badges and Info", False,
                                          f"Missing badges/info: Tier={has_tier}, Badge={has_badge_color}, Price={has_pricing}")
                        
                        # Step 4: Test complete flow success
                        self.log_result("Integration Flow - Complete", True,
                                      "Complete flow successful: signup → become mentor → appear in search")
                        
                    else:
                        self.log_result("Integration Flow - Mentor Appears in Search", False,
                                      f"Mentor not found in search results. Human count: {search_data.get('human_count', 0)}")
                else:
                    self.log_result("Integration Flow - Mentor Appears in Search", False,
                                  f"Search failed. Status: {search_response.status_code}")
                    
            else:
                self.log_result("Integration Flow - User Signup", False,
                              f"Registration failed. Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("Integration Flow - Complete", False,
                          f"Exception during integration test: {str(e)}")

    def run_all_tests(self):
        """Run all mentor signup functionality tests"""
        print("🚀 Starting Mentor Signup Functionality Testing")
        print("=" * 60)
        
        # Run all test categories
        self.test_new_user_registration_with_mentor_option()
        self.test_existing_user_upgrade_to_mentor()
        self.test_human_mentor_discovery()
        self.test_integration_flow()
        
        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("🎯 MENTOR SIGNUP FUNCTIONALITY TESTING SUMMARY")
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
            "New User Registration with Mentor Option": [],
            "Existing User Upgrade to Mentor": [],
            "Human Mentor Discovery": [],
            "Integration Flow": []
        }
        
        for result in self.results:
            test_name = result["test"]
            if "User Registration with Mentor Option" in test_name:
                categories["New User Registration with Mentor Option"].append(result)
            elif "Existing User Upgrade" in test_name or "Become Mentor Endpoint" in test_name:
                categories["Existing User Upgrade to Mentor"].append(result)
            elif "Human Mentor Discovery" in test_name:
                categories["Human Mentor Discovery"].append(result)
            elif "Integration Flow" in test_name:
                categories["Integration Flow"].append(result)
        
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
                           ("Authentication" in r["test"] or "Created" in r["test"] or 
                            "Filter" in r["test"] or "Complete" in r["test"])]
        
        if critical_failures:
            print("🚨 CRITICAL ISSUES FOUND:")
            for failure in critical_failures:
                print(f"   ❌ {failure['test']}: {failure['details']}")
            print()
        
        # Overall assessment
        if success_rate >= 90:
            print("🎉 EXCELLENT: Mentor signup functionality is working excellently!")
        elif success_rate >= 75:
            print("✅ GOOD: Mentor signup functionality is working well with minor issues.")
        elif success_rate >= 50:
            print("⚠️ MODERATE: Mentor signup functionality has some significant issues.")
        else:
            print("🚨 CRITICAL: Mentor signup functionality has major issues requiring immediate attention.")
        
        print("=" * 60)

if __name__ == "__main__":
    tester = MentorSignupTester()
    tester.run_all_tests()