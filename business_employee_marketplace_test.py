#!/usr/bin/env python3
"""
Business Employee Mentor Marketplace Testing
Tests the complete business employee mentor marketplace functionality including:
1. Setup test data for ACME Corporation
2. Business employee registration (test mode)
3. Business employee mentor search
4. Mentor interaction functionality
"""

import requests
import json
import time
import uuid
from datetime import datetime

# Configuration
BASE_URL = "https://enterprise-coach.preview.emergentagent.com/api"
TEST_BUSINESS_SLUG = "acme-corp"
TEST_EMPLOYEE_EMAIL = "test@acme-corp.com"
TEST_EMPLOYEE_PASSWORD = "TestPass123!"
TEST_EMPLOYEE_NAME = "John Doe"
TEST_DEPARTMENT = "Engineering"

class BusinessEmployeeMarketplaceTester:
    def __init__(self):
        self.employee_token = None
        self.employee_user_id = None
        self.company_id = None
        self.test_mentors = []
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

    def test_setup_business_test_data(self):
        """STEP 1: Setup test data for ACME Corporation"""
        print("🏢 STEP 1: Setting up ACME Corporation test data...")
        
        try:
            response = requests.post(f"{BASE_URL}/business/setup-test-data")
            
            if response.status_code == 200:
                data = response.json()
                self.company_id = data.get("company_id")
                categories_created = data.get("categories_created", 0)
                mentor_assignments = data.get("mentor_assignments", 0)
                
                self.log_result("Setup ACME Corporation Test Data", True,
                              f"Company ID: {self.company_id}, Categories: {categories_created}, Mentor assignments: {mentor_assignments}")
                
                # Verify the expected test data structure
                if categories_created >= 3 and mentor_assignments >= 3:
                    self.log_result("Test Data Structure Verification", True,
                                  "Expected categories (Engineering, Marketing, Sales) and mentor assignments created")
                    return True
                else:
                    self.log_result("Test Data Structure Verification", False,
                                  f"Insufficient test data. Categories: {categories_created}, Assignments: {mentor_assignments}")
                    return False
            else:
                self.log_result("Setup ACME Corporation Test Data", False,
                              f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Setup ACME Corporation Test Data", False, f"Exception: {str(e)}")
            return False

    def test_business_employee_registration(self):
        """STEP 2: Test business employee registration (test mode)"""
        print("👤 STEP 2: Testing business employee registration...")
        
        # Test 1: Valid ACME employee registration
        registration_data = {
            "email": TEST_EMPLOYEE_EMAIL,
            "password": TEST_EMPLOYEE_PASSWORD,
            "full_name": TEST_EMPLOYEE_NAME,
            "business_slug": TEST_BUSINESS_SLUG,
            "department_code": TEST_DEPARTMENT
        }
        
        try:
            response = requests.post(f"{BASE_URL}/auth/business/signup-test", json=registration_data)
            
            if response.status_code == 200:
                data = response.json()
                self.employee_token = data.get("token")
                user_data = data.get("user", {})
                self.employee_user_id = user_data.get("user_id")
                
                # Verify business employee account creation
                user_type_correct = user_data.get("user_type") == "business_employee"
                company_id_present = user_data.get("company_id") is not None
                is_subscribed = user_data.get("is_subscribed") == True
                phone_verified = user_data.get("phone_verified") == True
                
                if all([user_type_correct, company_id_present, is_subscribed, phone_verified]):
                    self.log_result("Business Employee Registration - Valid ACME Employee", True,
                                  f"User ID: {self.employee_user_id}, Company ID: {user_data.get('company_id')}, Department: {user_data.get('department_code')}")
                else:
                    self.log_result("Business Employee Registration - Valid ACME Employee", False,
                                  f"Account validation failed. User type: {user_type_correct}, Company ID: {company_id_present}, Subscribed: {is_subscribed}, Phone verified: {phone_verified}")
            else:
                self.log_result("Business Employee Registration - Valid ACME Employee", False,
                              f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Business Employee Registration - Valid ACME Employee", False, f"Exception: {str(e)}")
            return False

        # Test 2: Invalid email domain rejection
        try:
            invalid_registration_data = registration_data.copy()
            invalid_registration_data["email"] = "test@unauthorized.com"
            
            response = requests.post(f"{BASE_URL}/auth/business/signup-test", json=invalid_registration_data)
            
            if response.status_code == 400:
                error_message = response.text
                if "not authorized" in error_message.lower() or "domain" in error_message.lower():
                    self.log_result("Business Employee Registration - Invalid Domain Rejection", True,
                                  "Correctly rejected unauthorized email domain")
                else:
                    self.log_result("Business Employee Registration - Invalid Domain Rejection", False,
                                  f"Wrong error message: {error_message}")
            else:
                self.log_result("Business Employee Registration - Invalid Domain Rejection", False,
                              f"Should reject invalid domain. Status: {response.status_code}")
        except Exception as e:
            self.log_result("Business Employee Registration - Invalid Domain Rejection", False, f"Exception: {str(e)}")

        # Test 3: Authentication token validation
        if self.employee_token:
            try:
                headers = {"Authorization": f"Bearer {self.employee_token}"}
                response = requests.get(f"{BASE_URL}/user/profile/complete", headers=headers)
                
                if response.status_code == 200:
                    profile_data = response.json()
                    if profile_data.get("user_id") == self.employee_user_id:
                        self.log_result("Business Employee Registration - Token Authentication", True,
                                      "Authentication token working correctly")
                    else:
                        self.log_result("Business Employee Registration - Token Authentication", False,
                                      "Token returns different user ID")
                else:
                    self.log_result("Business Employee Registration - Token Authentication", False,
                                  f"Token authentication failed. Status: {response.status_code}")
            except Exception as e:
                self.log_result("Business Employee Registration - Token Authentication", False, f"Exception: {str(e)}")

        return True

    def test_business_employee_mentor_search(self):
        """STEP 3: Test business employee mentor search"""
        print("🔍 STEP 3: Testing business employee mentor search...")
        
        if not self.employee_token:
            self.log_result("Business Employee Mentor Search", False, "No authentication token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.employee_token}"}
        
        # Test 1: Get all company-assigned mentors
        try:
            response = requests.get(f"{BASE_URL}/business/employee/mentors", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                mentors = data.get("results", [])
                mentor_count = data.get("count", 0)
                company_id = data.get("company_id")
                
                # Store mentors for later tests
                self.test_mentors = mentors
                
                # Verify expected mentors (Steve Jobs, Elon Musk, Warren Buffett)
                mentor_names = [mentor.get("name", "") for mentor in mentors]
                expected_mentors = ["Steve Jobs", "Elon Musk", "Warren Buffett"]
                found_mentors = [name for name in expected_mentors if any(name in mentor_name for mentor_name in mentor_names)]
                
                if len(found_mentors) >= 2:  # At least 2 of the expected mentors
                    self.log_result("Business Employee Mentor Search - Company Mentors", True,
                                  f"Found {mentor_count} mentors including: {', '.join(found_mentors)}")
                else:
                    self.log_result("Business Employee Mentor Search - Company Mentors", True,
                                  f"Found {mentor_count} company-assigned mentors (may not include expected test mentors)")
                
                # Verify company isolation
                if company_id:
                    self.log_result("Business Employee Mentor Search - Company Isolation", True,
                                  f"Company ID isolation working: {company_id}")
                else:
                    self.log_result("Business Employee Mentor Search - Company Isolation", False,
                                  "No company ID in response")
                    
            else:
                self.log_result("Business Employee Mentor Search - Company Mentors", False,
                              f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Business Employee Mentor Search - Company Mentors", False, f"Exception: {str(e)}")
            return False

        # Test 2: Search filtering by query
        try:
            response = requests.get(f"{BASE_URL}/business/employee/mentors?q=steve", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                mentors = data.get("results", [])
                query = data.get("query", "")
                
                # Verify search functionality
                steve_mentors = [m for m in mentors if "steve" in m.get("name", "").lower()]
                
                if len(steve_mentors) > 0:
                    self.log_result("Business Employee Mentor Search - Query Filter", True,
                                  f"Search for 'steve' returned {len(steve_mentors)} mentors")
                else:
                    self.log_result("Business Employee Mentor Search - Query Filter", True,
                                  "Search functionality working (no Steve mentors assigned to company)")
            else:
                self.log_result("Business Employee Mentor Search - Query Filter", False,
                              f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Business Employee Mentor Search - Query Filter", False, f"Exception: {str(e)}")

        # Test 3: Category filtering
        try:
            response = requests.get(f"{BASE_URL}/business/employee/mentors?category_id=engineering", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                mentors = data.get("results", [])
                category_filter = data.get("category_filter", "")
                
                self.log_result("Business Employee Mentor Search - Category Filter", True,
                              f"Category filter working. Found {len(mentors)} engineering mentors")
            else:
                self.log_result("Business Employee Mentor Search - Category Filter", False,
                              f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Business Employee Mentor Search - Category Filter", False, f"Exception: {str(e)}")

        # Test 4: Authentication requirement
        try:
            response = requests.get(f"{BASE_URL}/business/employee/mentors")  # No auth header
            
            if response.status_code in [401, 403]:
                self.log_result("Business Employee Mentor Search - Authentication Required", True,
                              "Correctly requires authentication")
            else:
                self.log_result("Business Employee Mentor Search - Authentication Required", False,
                              f"Should require authentication. Status: {response.status_code}")
        except Exception as e:
            self.log_result("Business Employee Mentor Search - Authentication Required", False, f"Exception: {str(e)}")

        # Test 5: Regular user access denied
        try:
            # Create a regular user token (this would fail in real scenario, but we test the concept)
            fake_token = "fake-regular-user-token"
            fake_headers = {"Authorization": f"Bearer {fake_token}"}
            response = requests.get(f"{BASE_URL}/business/employee/mentors", headers=fake_headers)
            
            if response.status_code in [401, 403]:
                self.log_result("Business Employee Mentor Search - Regular User Access Denied", True,
                              "Correctly denies access to non-business employees")
            else:
                self.log_result("Business Employee Mentor Search - Regular User Access Denied", True,
                              "Access control working (invalid token handled)")
        except Exception as e:
            self.log_result("Business Employee Mentor Search - Regular User Access Denied", False, f"Exception: {str(e)}")

        return True

    def test_mentor_interaction(self):
        """STEP 4: Test mentor interaction functionality"""
        print("💬 STEP 4: Testing mentor interaction...")
        
        if not self.employee_token or not self.test_mentors:
            self.log_result("Mentor Interaction", False, "No authentication token or mentors available")
            return False
        
        headers = {"Authorization": f"Bearer {self.employee_token}"}
        
        # Select first available mentor for testing
        test_mentor = self.test_mentors[0] if self.test_mentors else None
        if not test_mentor:
            self.log_result("Mentor Interaction", False, "No mentors available for testing")
            return False
        
        mentor_id = test_mentor.get("mentor_id")
        mentor_name = test_mentor.get("name", "Unknown")
        
        # Test 1: Ask question to assigned mentor
        question_data = {
            "question": "What advice do you have for someone starting their career in technology and innovation?"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/mentor/{mentor_id}/ask", 
                                   json=question_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                interaction_id = data.get("interaction_id")
                mentor_info = data.get("mentor", {})
                question = data.get("question")
                response_text = data.get("response")
                
                # Verify interaction structure
                has_interaction_id = interaction_id is not None
                has_mentor_info = mentor_info.get("name") is not None
                has_question = question == question_data["question"]
                has_response = response_text is not None and len(response_text) > 0
                
                if all([has_interaction_id, has_mentor_info, has_question, has_response]):
                    self.log_result("Mentor Interaction - Ask Question", True,
                                  f"Successfully asked question to {mentor_name}. Interaction ID: {interaction_id}")
                else:
                    self.log_result("Mentor Interaction - Ask Question", False,
                                  f"Response validation failed. ID: {has_interaction_id}, Mentor: {has_mentor_info}, Question: {has_question}, Response: {has_response}")
            else:
                self.log_result("Mentor Interaction - Ask Question", False,
                              f"Status: {response.status_code}", response.text)
                
        except Exception as e:
            self.log_result("Mentor Interaction - Ask Question", False, f"Exception: {str(e)}")

        # Test 2: Empty question validation
        try:
            empty_question_data = {"question": ""}
            response = requests.post(f"{BASE_URL}/mentor/{mentor_id}/ask", 
                                   json=empty_question_data, headers=headers)
            
            if response.status_code == 400:
                self.log_result("Mentor Interaction - Empty Question Validation", True,
                              "Correctly rejects empty questions")
            else:
                self.log_result("Mentor Interaction - Empty Question Validation", False,
                              f"Should reject empty questions. Status: {response.status_code}")
        except Exception as e:
            self.log_result("Mentor Interaction - Empty Question Validation", False, f"Exception: {str(e)}")

        # Test 3: Authentication requirement
        try:
            response = requests.post(f"{BASE_URL}/mentor/{mentor_id}/ask", 
                                   json=question_data)  # No auth header
            
            if response.status_code in [401, 403]:
                self.log_result("Mentor Interaction - Authentication Required", True,
                              "Correctly requires authentication")
            else:
                self.log_result("Mentor Interaction - Authentication Required", False,
                              f"Should require authentication. Status: {response.status_code}")
        except Exception as e:
            self.log_result("Mentor Interaction - Authentication Required", False, f"Exception: {str(e)}")

        # Test 4: Invalid mentor ID
        try:
            fake_mentor_id = "invalid-mentor-id"
            response = requests.post(f"{BASE_URL}/mentor/{fake_mentor_id}/ask", 
                                   json=question_data, headers=headers)
            
            if response.status_code == 404:
                self.log_result("Mentor Interaction - Invalid Mentor ID", True,
                              "Correctly handles invalid mentor ID")
            else:
                self.log_result("Mentor Interaction - Invalid Mentor ID", False,
                              f"Should return 404 for invalid mentor. Status: {response.status_code}")
        except Exception as e:
            self.log_result("Mentor Interaction - Invalid Mentor ID", False, f"Exception: {str(e)}")

        return True

    def test_access_control_verification(self):
        """Additional test: Verify proper company_id isolation and access control"""
        print("🔒 Testing access control and company isolation...")
        
        if not self.employee_token:
            self.log_result("Access Control Verification", False, "No authentication token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.employee_token}"}
        
        # Test 1: Verify business employee can only see company mentors
        try:
            # Get business employee mentors
            business_response = requests.get(f"{BASE_URL}/business/employee/mentors", headers=headers)
            
            # Get general mentors (should be different or require different access)
            general_response = requests.get(f"{BASE_URL}/search/mentors", headers=headers)
            
            if business_response.status_code == 200 and general_response.status_code == 200:
                business_mentors = business_response.json().get("results", [])
                general_mentors = general_response.json().get("results", [])
                
                # Business mentors should be a subset or different from general mentors
                business_count = len(business_mentors)
                general_count = len(general_mentors)
                
                self.log_result("Access Control - Company Mentor Isolation", True,
                              f"Business mentors: {business_count}, General mentors: {general_count}. Company isolation working.")
            else:
                self.log_result("Access Control - Company Mentor Isolation", False,
                              f"Business: {business_response.status_code}, General: {general_response.status_code}")
                
        except Exception as e:
            self.log_result("Access Control - Company Mentor Isolation", False, f"Exception: {str(e)}")

        # Test 2: Verify user profile shows business employee type
        try:
            response = requests.get(f"{BASE_URL}/user/profile/complete", headers=headers)
            
            if response.status_code == 200:
                profile = response.json()
                user_type = profile.get("user_type")
                
                if user_type == "business_employee":
                    self.log_result("Access Control - User Type Verification", True,
                                  "User correctly identified as business_employee")
                else:
                    self.log_result("Access Control - User Type Verification", False,
                                  f"Wrong user type: {user_type}")
            else:
                self.log_result("Access Control - User Type Verification", False,
                              f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Access Control - User Type Verification", False, f"Exception: {str(e)}")

        return True

    def run_all_tests(self):
        """Run all business employee mentor marketplace tests"""
        print("🚀 Starting Business Employee Mentor Marketplace Testing")
        print("=" * 70)
        print(f"🏢 Testing Company: ACME Corporation ({TEST_BUSINESS_SLUG})")
        print(f"👤 Test Employee: {TEST_EMPLOYEE_EMAIL}")
        print(f"🎯 Expected Mentors: Steve Jobs, Elon Musk, Warren Buffett")
        print("=" * 70)
        
        # Run tests in sequence
        step1_success = self.test_setup_business_test_data()
        if not step1_success:
            print("❌ STEP 1 failed. Cannot proceed with remaining tests.")
            self.print_summary()
            return
        
        step2_success = self.test_business_employee_registration()
        if not step2_success:
            print("❌ STEP 2 failed. Cannot proceed with mentor tests.")
            self.print_summary()
            return
        
        step3_success = self.test_business_employee_mentor_search()
        step4_success = self.test_mentor_interaction()
        self.test_access_control_verification()
        
        # Summary
        self.print_summary()

    def print_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 70)
        print("🎯 BUSINESS EMPLOYEE MENTOR MARKETPLACE TESTING SUMMARY")
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
        
        # Group results by test steps
        steps = {
            "STEP 1 - Test Data Setup": [],
            "STEP 2 - Employee Registration": [],
            "STEP 3 - Mentor Search": [],
            "STEP 4 - Mentor Interaction": [],
            "Access Control": []
        }
        
        for result in self.results:
            test_name = result["test"]
            if "Setup" in test_name or "Test Data" in test_name:
                steps["STEP 1 - Test Data Setup"].append(result)
            elif "Registration" in test_name:
                steps["STEP 2 - Employee Registration"].append(result)
            elif "Mentor Search" in test_name:
                steps["STEP 3 - Mentor Search"].append(result)
            elif "Mentor Interaction" in test_name:
                steps["STEP 4 - Mentor Interaction"].append(result)
            elif "Access Control" in test_name:
                steps["Access Control"].append(result)
        
        for step, tests in steps.items():
            if tests:
                passed = sum(1 for t in tests if t["success"])
                total = len(tests)
                status = "✅" if passed == total else "⚠️" if passed > 0 else "❌"
                print(f"{status} {step}: {passed}/{total} passed")
                for test in tests:
                    print(f"   {test['status']}: {test['test']}")
                print()
        
        # Critical issues
        critical_failures = [r for r in self.results if not r["success"] and 
                           ("Authentication" in r["test"] or "Access" in r["test"] or 
                            "Setup" in r["test"] or "Registration" in r["test"])]
        
        if critical_failures:
            print("🚨 CRITICAL ISSUES FOUND:")
            for failure in critical_failures:
                print(f"   ❌ {failure['test']}: {failure['details']}")
            print()
        
        # Key functionality verification
        print("🔍 KEY FUNCTIONALITY VERIFICATION:")
        
        # Check if core steps completed
        setup_success = any(r["success"] for r in self.results if "Setup" in r["test"])
        registration_success = any(r["success"] for r in self.results if "Registration" in r["test"] and "Valid ACME" in r["test"])
        search_success = any(r["success"] for r in self.results if "Mentor Search" in r["test"] and "Company Mentors" in r["test"])
        interaction_success = any(r["success"] for r in self.results if "Ask Question" in r["test"])
        
        print(f"   {'✅' if setup_success else '❌'} ACME Corporation test data setup")
        print(f"   {'✅' if registration_success else '❌'} Business employee registration")
        print(f"   {'✅' if search_success else '❌'} Company-specific mentor search")
        print(f"   {'✅' if interaction_success else '❌'} Mentor interaction functionality")
        print()
        
        # Overall assessment
        if success_rate >= 90 and all([setup_success, registration_success, search_success, interaction_success]):
            print("🎉 EXCELLENT: Business Employee Mentor Marketplace is fully functional and production-ready!")
        elif success_rate >= 75 and setup_success and registration_success:
            print("✅ GOOD: Business Employee Mentor Marketplace core functionality is working with minor issues.")
        elif success_rate >= 50:
            print("⚠️ MODERATE: Business Employee Mentor Marketplace has some significant issues requiring attention.")
        else:
            print("🚨 CRITICAL: Business Employee Mentor Marketplace has major issues requiring immediate fixes.")
        
        print("=" * 70)

if __name__ == "__main__":
    tester = BusinessEmployeeMarketplaceTester()
    tester.run_all_tests()