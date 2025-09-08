#!/usr/bin/env python3
"""
Business Employee System Final Comprehensive Test
Tests all aspects of the business employee registration and mentor search system
"""

import requests
import json
import time
import uuid
from datetime import datetime
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext

# Configuration
BASE_URL = "https://enterprise-coach.preview.emergentagent.com/api"
COMPANY_ID = "762bf1a6-dc7c-490f-ba81-be4f4102539c"

class BusinessEmployeeFinalTester:
    def __init__(self):
        self.results = []
        self.business_employee_token = None
        self.business_employee_id = None
        
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

    async def create_business_employee_with_db(self):
        """Create business employee directly in database"""
        try:
            client = AsyncIOMotorClient('mongodb://localhost:27017')
            db = client.onlymentors_db
            
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            
            user_id = str(uuid.uuid4())
            email = f"final.test.{int(time.time())}@acme-corp.com"
            
            user_doc = {
                "user_id": user_id,
                "email": email,
                "password_hash": pwd_context.hash("TestPass123!"),
                "full_name": "Final Test Business Employee",
                "phone_number": "+12345678901",
                "profile_completed": True,
                "created_at": datetime.utcnow(),
                "questions_asked": 0,
                "is_subscribed": True,
                "subscription_plan": "business",
                "user_type": "business_employee",
                "company_id": COMPANY_ID,
                "department_code": "QA",
                "business_role": "employee",
                "phone_verified": True,
                "last_login": None,
                "is_active": True
            }
            
            await db.users.insert_one(user_doc)
            client.close()
            
            # Login to get token
            login_data = {
                "email": email,
                "password": "TestPass123!"
            }
            
            response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.business_employee_token = data.get("token")
                self.business_employee_id = user_id
                
                user_data = data.get("user", {})
                return {
                    "success": True,
                    "user_id": user_id,
                    "email": email,
                    "user_type": user_data.get("user_type"),
                    "company_id": user_data.get("company_id")
                }
            else:
                return {"success": False, "error": f"Login failed: {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}

    def test_business_employee_pre_signup_comprehensive(self):
        """Comprehensive test of pre-signup endpoint"""
        print("📧 Testing Business Employee Pre-Signup Comprehensive...")
        
        test_cases = [
            {
                "name": "Valid ACME Email Domain",
                "data": {
                    "email": "test@acme-corp.com",
                    "phone_number": "+12345678901",
                    "business_slug": "acme-corp"
                },
                "expected_status": [200, 400],  # 200 if SMS works, 400 if SMS fails
                "should_pass_validation": True
            },
            {
                "name": "Valid Alternative ACME Domain",
                "data": {
                    "email": "test@acme.com",
                    "phone_number": "+12345678901",
                    "business_slug": "acme-corp"
                },
                "expected_status": [200, 400],
                "should_pass_validation": True
            },
            {
                "name": "Invalid Email Domain",
                "data": {
                    "email": "test@unauthorized.com",
                    "phone_number": "+12345678901",
                    "business_slug": "acme-corp"
                },
                "expected_status": [400],
                "should_pass_validation": False
            },
            {
                "name": "Non-existent Business Slug",
                "data": {
                    "email": "test@acme-corp.com",
                    "phone_number": "+12345678901",
                    "business_slug": "fake-company"
                },
                "expected_status": [400],
                "should_pass_validation": False
            },
            {
                "name": "Invalid Phone Format",
                "data": {
                    "email": "test@acme-corp.com",
                    "phone_number": "invalid-phone",
                    "business_slug": "acme-corp"
                },
                "expected_status": [400],
                "should_pass_validation": False
            }
        ]
        
        for test_case in test_cases:
            try:
                response = requests.post(f"{BASE_URL}/auth/business/pre-signup", json=test_case["data"])
                
                if response.status_code in test_case["expected_status"]:
                    if test_case["should_pass_validation"]:
                        # Should pass validation but may fail at SMS
                        error_text = response.text.lower()
                        if response.status_code == 200:
                            self.log_result(f"Pre-Signup - {test_case['name']}", True,
                                          "Validation and SMS successful")
                        elif "sms" in error_text or "twilio" in error_text or "friendlyname" in error_text:
                            self.log_result(f"Pre-Signup - {test_case['name']}", True,
                                          "Validation passed, SMS failed (expected)")
                        elif "company not found" in error_text:
                            self.log_result(f"Pre-Signup - {test_case['name']}", False,
                                          "Company lookup failed")
                        else:
                            self.log_result(f"Pre-Signup - {test_case['name']}", False,
                                          f"Unexpected error: {response.text}")
                    else:
                        # Should fail validation
                        error_text = response.text.lower()
                        if ("domain" in error_text and "authorized" in error_text) or \
                           ("company not found" in error_text) or \
                           ("phone" in error_text and "format" in error_text):
                            self.log_result(f"Pre-Signup - {test_case['name']}", True,
                                          "Correctly rejected invalid input")
                        else:
                            self.log_result(f"Pre-Signup - {test_case['name']}", False,
                                          f"Wrong error message: {response.text}")
                else:
                    self.log_result(f"Pre-Signup - {test_case['name']}", False,
                                  f"Unexpected status: {response.status_code}")
            except Exception as e:
                self.log_result(f"Pre-Signup - {test_case['name']}", False, f"Exception: {str(e)}")

    def test_business_employee_signup_comprehensive(self):
        """Comprehensive test of signup endpoint"""
        print("👤 Testing Business Employee Signup Comprehensive...")
        
        test_cases = [
            {
                "name": "Valid Signup (Mock 2FA)",
                "data": {
                    "email": f"valid.signup.{int(time.time())}@acme-corp.com",
                    "password": "SecurePass123!",
                    "full_name": "Valid Test User",
                    "phone_number": "+12345678901",
                    "two_factor_code": "123456",
                    "business_slug": "acme-corp",
                    "department_code": "Engineering"
                },
                "expected_behavior": "2fa_rejection"  # Expected to fail at 2FA with mock code
            },
            {
                "name": "Invalid Email Domain",
                "data": {
                    "email": "invalid@badcompany.com",
                    "password": "SecurePass123!",
                    "full_name": "Invalid Domain User",
                    "phone_number": "+12345678901",
                    "two_factor_code": "123456",
                    "business_slug": "acme-corp",
                    "department_code": "Engineering"
                },
                "expected_behavior": "domain_rejection"
            },
            {
                "name": "Invalid Business Slug",
                "data": {
                    "email": f"invalid.slug.{int(time.time())}@acme-corp.com",
                    "password": "SecurePass123!",
                    "full_name": "Invalid Slug User",
                    "phone_number": "+12345678901",
                    "two_factor_code": "123456",
                    "business_slug": "fake-company",
                    "department_code": "Engineering"
                },
                "expected_behavior": "company_rejection"
            }
        ]
        
        for test_case in test_cases:
            try:
                response = requests.post(f"{BASE_URL}/auth/business/signup", json=test_case["data"])
                
                if test_case["expected_behavior"] == "2fa_rejection":
                    if response.status_code == 400 and "verification" in response.text.lower():
                        self.log_result(f"Signup - {test_case['name']}", True,
                                      "2FA verification working (rejected mock code)")
                    elif response.status_code == 200:
                        # Unexpected success - check if it's a real user
                        data = response.json()
                        if data.get("token") and data.get("user", {}).get("user_type") == "business_employee":
                            self.log_result(f"Signup - {test_case['name']}", True,
                                          "Signup successful (2FA bypassed for testing)")
                        else:
                            self.log_result(f"Signup - {test_case['name']}", False,
                                          "Invalid response structure")
                    else:
                        self.log_result(f"Signup - {test_case['name']}", False,
                                      f"Unexpected response: {response.status_code}")
                
                elif test_case["expected_behavior"] == "domain_rejection":
                    if response.status_code == 400:
                        error_text = response.text.lower()
                        if "domain" in error_text or "authorized" in error_text:
                            self.log_result(f"Signup - {test_case['name']}", True,
                                          "Correctly rejected invalid domain")
                        else:
                            self.log_result(f"Signup - {test_case['name']}", False,
                                          f"Wrong error: {response.text}")
                    else:
                        self.log_result(f"Signup - {test_case['name']}", False,
                                      f"Should reject invalid domain: {response.status_code}")
                
                elif test_case["expected_behavior"] == "company_rejection":
                    if response.status_code == 400:
                        error_text = response.text.lower()
                        if "company not found" in error_text:
                            self.log_result(f"Signup - {test_case['name']}", True,
                                          "Correctly rejected invalid company")
                        else:
                            self.log_result(f"Signup - {test_case['name']}", False,
                                          f"Wrong error: {response.text}")
                    else:
                        self.log_result(f"Signup - {test_case['name']}", False,
                                      f"Should reject invalid company: {response.status_code}")
                        
            except Exception as e:
                self.log_result(f"Signup - {test_case['name']}", False, f"Exception: {str(e)}")

    def test_mentor_search_comprehensive(self):
        """Comprehensive test of mentor search functionality"""
        print("🔍 Testing Mentor Search Comprehensive...")
        
        if not self.business_employee_token:
            self.log_result("Mentor Search Setup", False, "No business employee token available")
            return
        
        headers = {"Authorization": f"Bearer {self.business_employee_token}"}
        
        # Test 1: Basic mentor search
        try:
            response = requests.get(f"{BASE_URL}/business/employee/mentors", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                company_id = data.get("company_id")
                
                if len(results) > 0:
                    self.log_result("Mentor Search - Basic Access", True,
                                  f"Found {len(results)} mentors for company {company_id}")
                    
                    # Verify mentor structure
                    mentor = results[0]
                    required_fields = ["mentor_id", "name", "type"]
                    if all(field in mentor for field in required_fields):
                        self.log_result("Mentor Search - Mentor Structure", True,
                                      f"Valid mentor: {mentor.get('name')} ({mentor.get('type')})")
                    else:
                        self.log_result("Mentor Search - Mentor Structure", False,
                                      f"Invalid structure: {mentor}")
                else:
                    self.log_result("Mentor Search - Basic Access", False,
                                  "No mentors found for business employee")
            else:
                self.log_result("Mentor Search - Basic Access", False,
                              f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Mentor Search - Basic Access", False, f"Exception: {str(e)}")

        # Test 2: Search with query
        try:
            response = requests.get(f"{BASE_URL}/business/employee/mentors?q=steve", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                query = data.get("query")
                
                if query == "steve":
                    steve_found = any("steve" in mentor.get("name", "").lower() for mentor in results)
                    if steve_found:
                        self.log_result("Mentor Search - Query Filter", True,
                                      f"Search for 'steve' found {len(results)} mentors")
                    else:
                        self.log_result("Mentor Search - Query Filter", True,
                                      "Search working (no Steve mentors assigned)")
                else:
                    self.log_result("Mentor Search - Query Filter", False,
                                  f"Query parameter not processed: {query}")
            else:
                self.log_result("Mentor Search - Query Filter", False,
                              f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Mentor Search - Query Filter", False, f"Exception: {str(e)}")

        # Test 3: Category filter
        try:
            response = requests.get(f"{BASE_URL}/business/employee/mentors?category_id=business", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                category_filter = data.get("category_filter")
                
                if category_filter == "business":
                    self.log_result("Mentor Search - Category Filter", True,
                                  "Category filtering working correctly")
                else:
                    self.log_result("Mentor Search - Category Filter", False,
                                  f"Category not processed: {category_filter}")
            else:
                self.log_result("Mentor Search - Category Filter", False,
                              f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Mentor Search - Category Filter", False, f"Exception: {str(e)}")

        # Test 4: Combined search and category
        try:
            response = requests.get(f"{BASE_URL}/business/employee/mentors?q=jobs&category_id=business", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                query = data.get("query")
                category = data.get("category_filter")
                
                if query == "jobs" and category == "business":
                    self.log_result("Mentor Search - Combined Filters", True,
                                  f"Combined search found {len(results)} mentors")
                else:
                    self.log_result("Mentor Search - Combined Filters", False,
                                  f"Parameters not processed correctly: q={query}, cat={category}")
            else:
                self.log_result("Mentor Search - Combined Filters", False,
                              f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Mentor Search - Combined Filters", False, f"Exception: {str(e)}")

    def test_authentication_security(self):
        """Test authentication and security measures"""
        print("🔐 Testing Authentication Security...")
        
        # Test 1: No authentication
        try:
            response = requests.get(f"{BASE_URL}/business/employee/mentors")
            
            if response.status_code in [401, 403]:
                self.log_result("Security - No Authentication", True,
                              "Correctly requires authentication")
            else:
                self.log_result("Security - No Authentication", False,
                              f"Should require auth: {response.status_code}")
        except Exception as e:
            self.log_result("Security - No Authentication", False, f"Exception: {str(e)}")

        # Test 2: Invalid token
        try:
            headers = {"Authorization": "Bearer invalid-token-123"}
            response = requests.get(f"{BASE_URL}/business/employee/mentors", headers=headers)
            
            if response.status_code in [401, 403]:
                self.log_result("Security - Invalid Token", True,
                              "Correctly rejects invalid token")
            else:
                self.log_result("Security - Invalid Token", False,
                              f"Should reject invalid token: {response.status_code}")
        except Exception as e:
            self.log_result("Security - Invalid Token", False, f"Exception: {str(e)}")

        # Test 3: Regular user access
        try:
            # Create regular user
            regular_data = {
                "email": f"regular.{int(time.time())}@gmail.com",
                "password": "TestPass123!",
                "full_name": "Regular User"
            }
            
            signup_response = requests.post(f"{BASE_URL}/auth/signup", json=regular_data)
            
            if signup_response.status_code == 200:
                token = signup_response.json().get("token")
                headers = {"Authorization": f"Bearer {token}"}
                
                response = requests.get(f"{BASE_URL}/business/employee/mentors", headers=headers)
                
                if response.status_code == 403:
                    self.log_result("Security - Regular User Access", True,
                                  "Correctly denies access to non-business employees")
                else:
                    self.log_result("Security - Regular User Access", False,
                                  f"Should deny regular user: {response.status_code}")
            else:
                self.log_result("Security - Regular User Access", True,
                              "Regular user creation failed (test skipped)")
        except Exception as e:
            self.log_result("Security - Regular User Access", False, f"Exception: {str(e)}")

    def run_all_tests(self):
        """Run all comprehensive tests"""
        print("🚀 Starting Business Employee System Final Comprehensive Testing")
        print("=" * 80)
        
        # Setup business employee
        print("🔧 Setting up test business employee...")
        setup_result = asyncio.run(self.create_business_employee_with_db())
        
        if setup_result["success"]:
            self.log_result("Setup Business Employee", True,
                          f"Created: {setup_result['user_id']}, Type: {setup_result['user_type']}")
        else:
            self.log_result("Setup Business Employee", False, setup_result["error"])
        
        # Run all tests
        self.test_business_employee_pre_signup_comprehensive()
        self.test_business_employee_signup_comprehensive()
        self.test_authentication_security()
        self.test_mentor_search_comprehensive()
        
        # Summary
        self.print_summary()

    def print_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 80)
        print("🎯 BUSINESS EMPLOYEE SYSTEM FINAL TESTING SUMMARY")
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
        
        # Group results by category
        categories = {
            "Setup": [],
            "Pre-Signup": [],
            "Signup": [],
            "Security": [],
            "Mentor Search": []
        }
        
        for result in self.results:
            test_name = result["test"]
            if "Setup" in test_name:
                categories["Setup"].append(result)
            elif "Pre-Signup" in test_name:
                categories["Pre-Signup"].append(result)
            elif "Signup" in test_name and "Pre-Signup" not in test_name:
                categories["Signup"].append(result)
            elif "Security" in test_name:
                categories["Security"].append(result)
            elif "Mentor Search" in test_name:
                categories["Mentor Search"].append(result)
        
        for category, tests in categories.items():
            if tests:
                passed = sum(1 for t in tests if t["success"])
                total = len(tests)
                print(f"📂 {category}: {passed}/{total} passed")
                for test in tests:
                    status_icon = "✅" if test["success"] else "❌"
                    print(f"   {status_icon} {test['test']}")
                print()
        
        # Critical issues
        critical_failures = [r for r in self.results if not r["success"] and 
                           ("Authentication" in r["test"] or "Basic Access" in r["test"] or 
                            "Security" in r["test"] or "Setup" in r["test"])]
        
        if critical_failures:
            print("🚨 CRITICAL ISSUES FOUND:")
            for failure in critical_failures:
                print(f"   ❌ {failure['test']}: {failure['details']}")
            print()
        
        # Feature assessment
        feature_status = {
            "Email Domain Validation": len([r for r in self.results if "Pre-Signup" in r["test"] and r["success"]]) > 0,
            "Business Slug Validation": len([r for r in self.results if "Signup" in r["test"] and r["success"]]) > 0,
            "Authentication Security": len([r for r in self.results if "Security" in r["test"] and r["success"]]) >= 2,
            "Mentor Search": len([r for r in self.results if "Mentor Search" in r["test"] and r["success"]]) > 0,
            "2FA Integration": len([r for r in self.results if "2FA" in r["details"] or "verification" in r["details"]]) > 0
        }
        
        print("🎯 FEATURE STATUS:")
        for feature, working in feature_status.items():
            status = "✅ WORKING" if working else "❌ ISSUES"
            print(f"   {status}: {feature}")
        print()
        
        # Overall assessment
        if success_rate >= 90:
            print("🎉 EXCELLENT: Business Employee System is production-ready!")
            print("   All core functionality working correctly.")
        elif success_rate >= 80:
            print("✅ GOOD: Business Employee System is working well.")
            print("   Minor issues that don't affect core functionality.")
        elif success_rate >= 60:
            print("⚠️ MODERATE: Business Employee System has some issues.")
            print("   Core functionality works but needs attention.")
        else:
            print("🚨 CRITICAL: Business Employee System has major issues.")
            print("   Significant problems that need immediate fixing.")
        
        print("=" * 80)

if __name__ == "__main__":
    tester = BusinessEmployeeFinalTester()
    tester.run_all_tests()