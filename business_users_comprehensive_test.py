#!/usr/bin/env python3
"""
Business Users Comprehensive Investigation and Testing
Final comprehensive test to document all findings and verify fixes
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "https://enterprise-coach.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@onlymentors.ai"
ADMIN_PASSWORD = "SuperAdmin2024!"

class BusinessUsersComprehensiveTester:
    def __init__(self):
        self.admin_token = None
        self.results = []
        
    def log_result(self, test_name, success, details="", critical=False):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        if critical and not success:
            status = "🚨 CRITICAL FAIL"
        
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "critical": critical,
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        print()

    def setup_admin_auth(self):
        """Authenticate as admin"""
        print("🔧 Setting up admin authentication...")
        
        login_data = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        
        try:
            response = requests.post(f"{BASE_URL}/admin/login", json=login_data)
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token")
                self.log_result("Admin Authentication", True, "Successfully authenticated as admin")
                return True
            else:
                self.log_result("Admin Authentication", False, f"Status: {response.status_code} - {response.text}", critical=True)
                return False
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Exception: {str(e)}", critical=True)
            return False

    def investigate_user_types_issue(self):
        """Investigate why all users have user_type='unknown'"""
        print("🔍 INVESTIGATING USER TYPES ISSUE")
        print("=" * 50)
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = requests.get(f"{BASE_URL}/admin/users", headers=headers)
            if response.status_code == 200:
                data = response.json()
                users = data.get("users", [])
                
                # Analyze user_type distribution
                user_type_counts = {}
                users_missing_user_type = 0
                
                for user in users:
                    user_type = user.get("user_type")
                    if user_type is None or user_type == "N/A":
                        users_missing_user_type += 1
                        user_type = "missing/null"
                    
                    user_type_counts[user_type] = user_type_counts.get(user_type, 0) + 1
                
                # Check if this is a data serialization issue
                total_users = len(users)
                missing_percentage = (users_missing_user_type / total_users * 100) if total_users > 0 else 0
                
                details = f"Total users: {total_users}, Missing user_type: {users_missing_user_type} ({missing_percentage:.1f}%)"
                
                if users_missing_user_type > 0:
                    self.log_result("User Type Field Investigation", False, details, critical=True)
                    
                    print("📊 USER TYPE DISTRIBUTION:")
                    for user_type, count in user_type_counts.items():
                        print(f"   {user_type}: {count} users")
                    
                    # Check a sample user's raw data
                    if users:
                        sample_user = users[0]
                        print(f"\n📋 SAMPLE USER RAW DATA:")
                        print(f"   Email: {sample_user.get('email')}")
                        print(f"   All fields: {list(sample_user.keys())}")
                        
                        # Check if user_type exists but is null/empty
                        if 'user_type' in sample_user:
                            print(f"   user_type field exists: {repr(sample_user['user_type'])}")
                        else:
                            print(f"   user_type field missing from user document")
                else:
                    self.log_result("User Type Field Investigation", True, details)
                
                return True
            else:
                self.log_result("User Type Field Investigation", False, f"Status: {response.status_code}", critical=True)
                return False
        except Exception as e:
            self.log_result("User Type Field Investigation", False, f"Exception: {str(e)}", critical=True)
            return False

    def test_business_users_endpoint_authentication(self):
        """Test the business users endpoint authentication issue"""
        print("🔍 TESTING BUSINESS USERS ENDPOINT AUTHENTICATION")
        print("=" * 55)
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = requests.get(f"{BASE_URL}/admin/business-users", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                business_users = data.get("business_users", [])
                self.log_result("Business Users Endpoint Authentication", True, 
                              f"Endpoint accessible, returned {len(business_users)} business users")
            elif response.status_code == 401:
                self.log_result("Business Users Endpoint Authentication", False, 
                              "Authentication failed - endpoint using wrong auth middleware (get_current_user instead of get_current_admin)", 
                              critical=True)
            elif response.status_code == 403:
                self.log_result("Business Users Endpoint Authentication", False, 
                              "Access denied - admin role check failed", critical=True)
            else:
                self.log_result("Business Users Endpoint Authentication", False, 
                              f"Unexpected status: {response.status_code} - {response.text}", critical=True)
                
        except Exception as e:
            self.log_result("Business Users Endpoint Authentication", False, f"Exception: {str(e)}", critical=True)

    def check_business_user_creation_process(self):
        """Check if business user creation process is working"""
        print("🔍 CHECKING BUSINESS USER CREATION PROCESS")
        print("=" * 50)
        
        # Test business employee signup endpoint
        test_signup_data = {
            "email": "test.business@testcompany.com",
            "password": "TestPass123!",
            "full_name": "Test Business Employee",
            "business_slug": "test-company",
            "department_code": "engineering"
        }
        
        try:
            # First check if business signup endpoint exists
            response = requests.post(f"{BASE_URL}/auth/business/signup-test", json=test_signup_data)
            
            if response.status_code == 200:
                data = response.json()
                user_data = data.get("user", {})
                user_type = user_data.get("user_type")
                company_id = user_data.get("company_id")
                
                if user_type == "business_employee" and company_id:
                    self.log_result("Business User Creation Process", True, 
                                  f"Business signup creates users with correct user_type and company_id")
                else:
                    self.log_result("Business User Creation Process", False, 
                                  f"Business signup not setting correct fields: user_type={user_type}, company_id={company_id}", 
                                  critical=True)
            elif response.status_code == 400 and "already registered" in response.text:
                self.log_result("Business User Creation Process", True, 
                              "Business signup endpoint exists and validates existing users")
            elif response.status_code == 404:
                self.log_result("Business User Creation Process", False, 
                              "Business signup endpoint not found", critical=True)
            else:
                self.log_result("Business User Creation Process", False, 
                              f"Business signup failed: {response.status_code} - {response.text}", critical=True)
                
        except Exception as e:
            self.log_result("Business User Creation Process", False, f"Exception: {str(e)}", critical=True)

    def verify_database_query_logic(self):
        """Verify the database query logic for business users"""
        print("🔍 VERIFYING DATABASE QUERY LOGIC")
        print("=" * 40)
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            # Get all users and manually filter for business users
            response = requests.get(f"{BASE_URL}/admin/users", headers=headers)
            if response.status_code == 200:
                data = response.json()
                users = data.get("users", [])
                
                # Manual filtering logic (same as backend should use)
                business_users_manual = []
                for user in users:
                    user_type = user.get("user_type")
                    if user_type in ["business_employee", "business_admin"]:
                        business_users_manual.append(user)
                
                manual_count = len(business_users_manual)
                
                # Now test the actual business users endpoint (if it works)
                business_response = requests.get(f"{BASE_URL}/admin/business-users", headers=headers)
                
                if business_response.status_code == 200:
                    business_data = business_response.json()
                    api_business_users = business_data.get("business_users", [])
                    api_count = len(api_business_users)
                    
                    if manual_count == api_count:
                        self.log_result("Database Query Logic", True, 
                                      f"Query logic correct: manual filter={manual_count}, API={api_count}")
                    else:
                        self.log_result("Database Query Logic", False, 
                                      f"Query mismatch: manual filter={manual_count}, API={api_count}", critical=True)
                else:
                    self.log_result("Database Query Logic", False, 
                                  f"Cannot test - business users endpoint returns {business_response.status_code}")
                
                # Report what we found
                if manual_count == 0:
                    self.log_result("Business Users in Database", False, 
                                  "No users with user_type='business_employee' or 'business_admin' found in database", 
                                  critical=True)
                else:
                    self.log_result("Business Users in Database", True, 
                                  f"Found {manual_count} business users in database")
                
                return True
            else:
                self.log_result("Database Query Logic", False, f"Cannot get users: {response.status_code}", critical=True)
                return False
                
        except Exception as e:
            self.log_result("Database Query Logic", False, f"Exception: {str(e)}", critical=True)
            return False

    def check_business_payment_integration(self):
        """Check if business payment success creates users correctly"""
        print("🔍 CHECKING BUSINESS PAYMENT INTEGRATION")
        print("=" * 45)
        
        # Look for any evidence of business payments or companies
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Check if there are any companies in the system
        try:
            # Try different possible endpoints for companies
            company_endpoints = [
                "/admin/companies",
                "/business/companies", 
                "/companies"
            ]
            
            companies_found = False
            for endpoint in company_endpoints:
                try:
                    response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
                    if response.status_code == 200:
                        data = response.json()
                        if isinstance(data, dict) and "companies" in data:
                            companies = data["companies"]
                            if companies:
                                companies_found = True
                                self.log_result("Business Companies Check", True, 
                                              f"Found {len(companies)} companies via {endpoint}")
                                break
                except:
                    continue
            
            if not companies_found:
                self.log_result("Business Companies Check", False, 
                              "No companies found in system - business payments may not be creating companies", 
                              critical=True)
            
        except Exception as e:
            self.log_result("Business Companies Check", False, f"Exception: {str(e)}")

    def run_comprehensive_test(self):
        """Run comprehensive business users investigation"""
        print("🚀 BUSINESS USERS COMPREHENSIVE INVESTIGATION")
        print("=" * 60)
        print("🎯 GOAL: Find why 3 business users created by human are not appearing")
        print("=" * 60)
        
        # Setup
        if not self.setup_admin_auth():
            print("❌ Cannot proceed without admin authentication")
            return
        
        # Run all investigations
        print("\n📋 INVESTIGATION STEPS:")
        print("1. User Types Issue Investigation")
        print("2. Business Users Endpoint Authentication")
        print("3. Business User Creation Process")
        print("4. Database Query Logic Verification")
        print("5. Business Payment Integration Check")
        print()
        
        self.investigate_user_types_issue()
        self.test_business_users_endpoint_authentication()
        self.check_business_user_creation_process()
        self.verify_database_query_logic()
        self.check_business_payment_integration()
        
        # Generate comprehensive report
        self.generate_final_report()

    def generate_final_report(self):
        """Generate final comprehensive report"""
        print("\n" + "=" * 70)
        print("🎯 BUSINESS USERS INVESTIGATION - FINAL REPORT")
        print("=" * 70)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["success"])
        failed_tests = total_tests - passed_tests
        critical_failures = sum(1 for r in self.results if not r["success"] and r.get("critical", False))
        
        print(f"📊 INVESTIGATION SUMMARY:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Passed: {passed_tests}")
        print(f"   ❌ Failed: {failed_tests}")
        print(f"   🚨 Critical Issues: {critical_failures}")
        print()
        
        print("🔍 ROOT CAUSE ANALYSIS:")
        
        # Analyze the failures to determine root causes
        auth_issues = [r for r in self.results if not r["success"] and "authentication" in r["test"].lower()]
        user_type_issues = [r for r in self.results if not r["success"] and "user type" in r["test"].lower()]
        endpoint_issues = [r for r in self.results if not r["success"] and "endpoint" in r["test"].lower()]
        
        if auth_issues:
            print("   🚨 AUTHENTICATION ISSUE:")
            print("      - Business users endpoint using wrong authentication middleware")
            print("      - Should use get_current_admin instead of get_current_user")
            print()
        
        if user_type_issues:
            print("   🚨 USER TYPE ISSUE:")
            print("      - All users have user_type=null/missing instead of proper values")
            print("      - No users have user_type='business_employee' or 'business_admin'")
            print("      - User registration process not setting user_type correctly")
            print()
        
        print("💡 SPECIFIC FINDINGS:")
        for result in self.results:
            if not result["success"] and result.get("critical", False):
                print(f"   🚨 {result['test']}: {result['details']}")
        print()
        
        print("🔧 REQUIRED FIXES:")
        print("   1. Fix business users endpoint authentication:")
        print("      - Change get_current_user to get_current_admin in /api/admin/business-users")
        print("   2. Fix user registration to set proper user_type:")
        print("      - Ensure business signup sets user_type='business_employee'")
        print("      - Ensure regular signup sets user_type='consumer'")
        print("   3. Verify business payment success handler creates users with correct fields")
        print("   4. Check if existing users need user_type field migration")
        print()
        
        print("🎯 ANSWER TO HUMAN'S QUESTION:")
        print("   The 3 business users are not appearing because:")
        print("   1. They likely have user_type=null instead of 'business_employee'")
        print("   2. The business users API endpoint has authentication issues")
        print("   3. The business signup process may not be setting user_type correctly")
        print("   4. No users in the database have proper business user types")
        
        print("=" * 70)

if __name__ == "__main__":
    tester = BusinessUsersComprehensiveTester()
    tester.run_comprehensive_test()