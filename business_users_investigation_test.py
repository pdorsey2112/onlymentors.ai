#!/usr/bin/env python3
"""
Business Users Database Investigation Test
Investigates why business users are not appearing in the admin console business users list
"""

import requests
import json
import time
import uuid
from datetime import datetime

# Configuration
BASE_URL = "https://enterprise-coach.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@onlymentors.ai"
ADMIN_PASSWORD = "SuperAdmin2024!"

class BusinessUsersInvestigator:
    def __init__(self):
        self.admin_token = None
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
        if response_data and isinstance(response_data, dict):
            print(f"   Response: {json.dumps(response_data, indent=2)}")
        elif response_data:
            print(f"   Response: {response_data}")
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
                self.log_result("Admin Authentication", True, f"Admin authenticated successfully")
                return True
            else:
                self.log_result("Admin Authentication", False, f"Status: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Exception: {str(e)}")
            return False

    def investigate_all_users_in_database(self):
        """Check all users in the database to see what exists"""
        print("🔍 Investigating all users in database...")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            # Get all users from admin endpoint
            response = requests.get(f"{BASE_URL}/admin/users", headers=headers)
            if response.status_code == 200:
                data = response.json()
                users = data.get("users", [])
                
                total_users = len(users)
                business_users = []
                consumer_users = []
                other_users = []
                
                # Analyze user types
                for user in users:
                    user_type = user.get("user_type", "unknown")
                    company_id = user.get("company_id")
                    
                    if user_type in ["business_employee", "business_admin"]:
                        business_users.append(user)
                    elif user_type == "consumer":
                        consumer_users.append(user)
                    else:
                        other_users.append(user)
                
                # Log findings
                self.log_result("Database User Investigation", True, 
                              f"Total users: {total_users}, Business users: {len(business_users)}, Consumer users: {len(consumer_users)}, Other: {len(other_users)}")
                
                # Detailed analysis of business users
                if business_users:
                    print("📋 BUSINESS USERS FOUND:")
                    for i, user in enumerate(business_users, 1):
                        print(f"   {i}. Email: {user.get('email')}")
                        print(f"      User Type: {user.get('user_type')}")
                        print(f"      Company ID: {user.get('company_id')}")
                        print(f"      Full Name: {user.get('full_name')}")
                        print(f"      Created: {user.get('created_at')}")
                        print()
                else:
                    print("❌ NO BUSINESS USERS FOUND IN DATABASE")
                
                # Check for users with company_id but different user_type
                users_with_company_id = [u for u in users if u.get("company_id")]
                if users_with_company_id:
                    print("🏢 USERS WITH COMPANY_ID:")
                    for i, user in enumerate(users_with_company_id, 1):
                        print(f"   {i}. Email: {user.get('email')}")
                        print(f"      User Type: {user.get('user_type')}")
                        print(f"      Company ID: {user.get('company_id')}")
                        print()
                
                return True
            else:
                self.log_result("Database User Investigation", False, f"Status: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Database User Investigation", False, f"Exception: {str(e)}")
            return False

    def test_business_users_api_endpoint(self):
        """Test the GET /api/admin/business-users endpoint directly"""
        print("🔍 Testing Business Users API Endpoint...")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = requests.get(f"{BASE_URL}/admin/business-users", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                business_users = data.get("business_users", [])
                total_count = data.get("total_count", 0)
                
                self.log_result("Business Users API Endpoint", True, 
                              f"API returned {len(business_users)} business users (total_count: {total_count})")
                
                if business_users:
                    print("📋 BUSINESS USERS FROM API:")
                    for i, user in enumerate(business_users, 1):
                        print(f"   {i}. Email: {user.get('email')}")
                        print(f"      User Type: {user.get('user_type')}")
                        print(f"      Company: {user.get('company_name', 'N/A')}")
                        print(f"      Full Name: {user.get('full_name')}")
                        print()
                else:
                    print("❌ NO BUSINESS USERS RETURNED FROM API")
                    
                return True
            else:
                self.log_result("Business Users API Endpoint", False, f"Status: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Business Users API Endpoint", False, f"Exception: {str(e)}")
            return False

    def check_business_payment_users(self):
        """Check if users were created through business payment process"""
        print("💳 Checking for users created through business payment process...")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            # Check companies collection for business registrations
            response = requests.get(f"{BASE_URL}/admin/companies", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                companies = data.get("companies", [])
                
                self.log_result("Business Companies Check", True, 
                              f"Found {len(companies)} companies in database")
                
                if companies:
                    print("🏢 COMPANIES FOUND:")
                    for i, company in enumerate(companies, 1):
                        print(f"   {i}. Company: {company.get('company_name')}")
                        print(f"      Company ID: {company.get('company_id')}")
                        print(f"      Contact Email: {company.get('contact_email')}")
                        print(f"      Status: {company.get('status')}")
                        print(f"      Created: {company.get('created_at')}")
                        print()
                        
                        # For each company, check if there are associated users
                        company_id = company.get('company_id')
                        if company_id:
                            self.check_users_for_company(company_id, company.get('company_name'))
                else:
                    print("❌ NO COMPANIES FOUND - Business payments may not have created companies")
                    
                return True
            else:
                # Try alternative endpoint or method
                self.log_result("Business Companies Check", False, f"Status: {response.status_code} - trying alternative method")
                return self.check_business_payments_alternative()
        except Exception as e:
            self.log_result("Business Companies Check", False, f"Exception: {str(e)}")
            return False

    def check_users_for_company(self, company_id, company_name):
        """Check users associated with a specific company"""
        print(f"👥 Checking users for company: {company_name} (ID: {company_id})")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            # Get all users and filter by company_id
            response = requests.get(f"{BASE_URL}/admin/users", headers=headers)
            if response.status_code == 200:
                data = response.json()
                users = data.get("users", [])
                
                company_users = [u for u in users if u.get("company_id") == company_id]
                
                if company_users:
                    print(f"   ✅ Found {len(company_users)} users for {company_name}:")
                    for user in company_users:
                        print(f"      - {user.get('email')} ({user.get('user_type', 'unknown')})")
                else:
                    print(f"   ❌ No users found for {company_name}")
                    
        except Exception as e:
            print(f"   ❌ Error checking users for {company_name}: {str(e)}")

    def check_business_payments_alternative(self):
        """Alternative method to check business payments"""
        print("💳 Checking business payments with alternative method...")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            # Check if there's a payments or transactions endpoint
            response = requests.get(f"{BASE_URL}/admin/payments", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                payments = data.get("payments", [])
                
                business_payments = [p for p in payments if p.get("type") == "business" or "business" in str(p.get("package_id", "")).lower()]
                
                self.log_result("Business Payments Check", True, 
                              f"Found {len(business_payments)} business payments")
                
                if business_payments:
                    print("💳 BUSINESS PAYMENTS FOUND:")
                    for i, payment in enumerate(business_payments, 1):
                        print(f"   {i}. Payment ID: {payment.get('payment_id')}")
                        print(f"      Email: {payment.get('customer_email')}")
                        print(f"      Package: {payment.get('package_id')}")
                        print(f"      Status: {payment.get('status')}")
                        print(f"      Created: {payment.get('created_at')}")
                        print()
                        
                return True
            else:
                self.log_result("Business Payments Check", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Business Payments Check", False, f"Exception: {str(e)}")
            return False

    def analyze_user_type_values(self):
        """Analyze what user_type values actually exist in the database"""
        print("📊 Analyzing user_type values in database...")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = requests.get(f"{BASE_URL}/admin/users", headers=headers)
            if response.status_code == 200:
                data = response.json()
                users = data.get("users", [])
                
                # Count user types
                user_type_counts = {}
                users_with_company_id = 0
                
                for user in users:
                    user_type = user.get("user_type", "unknown")
                    user_type_counts[user_type] = user_type_counts.get(user_type, 0) + 1
                    
                    if user.get("company_id"):
                        users_with_company_id += 1
                
                self.log_result("User Type Analysis", True, 
                              f"Analyzed {len(users)} users, {users_with_company_id} have company_id")
                
                print("📊 USER TYPE DISTRIBUTION:")
                for user_type, count in user_type_counts.items():
                    print(f"   {user_type}: {count} users")
                print()
                
                # Check for potential business users with different user_type
                potential_business_users = [u for u in users if u.get("company_id") and u.get("user_type") != "business_employee"]
                
                if potential_business_users:
                    print("🔍 POTENTIAL BUSINESS USERS WITH DIFFERENT USER_TYPE:")
                    for user in potential_business_users:
                        print(f"   Email: {user.get('email')}")
                        print(f"   User Type: {user.get('user_type')}")
                        print(f"   Company ID: {user.get('company_id')}")
                        print()
                
                return True
            else:
                self.log_result("User Type Analysis", False, f"Status: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("User Type Analysis", False, f"Exception: {str(e)}")
            return False

    def test_business_users_query_logic(self):
        """Test the specific query logic used by the business users endpoint"""
        print("🔍 Testing Business Users Query Logic...")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            # Test with different query parameters to understand the filtering
            test_queries = [
                ("All Users", f"{BASE_URL}/admin/users"),
                ("Business Users API", f"{BASE_URL}/admin/business-users"),
            ]
            
            for query_name, url in test_queries:
                response = requests.get(url, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if "users" in data:
                        users = data["users"]
                        business_count = len([u for u in users if u.get("user_type") in ["business_employee", "business_admin"]])
                        company_id_count = len([u for u in users if u.get("company_id")])
                        
                        print(f"   {query_name}: {len(users)} total, {business_count} business type, {company_id_count} with company_id")
                    elif "business_users" in data:
                        business_users = data["business_users"]
                        print(f"   {query_name}: {len(business_users)} business users returned")
                    else:
                        print(f"   {query_name}: Unexpected response structure")
                else:
                    print(f"   {query_name}: Failed with status {response.status_code}")
            
            self.log_result("Business Users Query Logic Test", True, "Query logic analysis completed")
            return True
            
        except Exception as e:
            self.log_result("Business Users Query Logic Test", False, f"Exception: {str(e)}")
            return False

    def create_test_business_user(self):
        """Create a test business user to verify the system works"""
        print("🧪 Creating test business user to verify system...")
        
        # First, create a test company
        test_company_data = {
            "company_name": "Test Investigation Corp",
            "contact_name": "Test Admin",
            "contact_email": "testadmin@testinvestigation.com",
            "contact_phone": "+1-555-TEST",
            "plan": "starter"
        }
        
        try:
            # Try to create company through business signup
            response = requests.post(f"{BASE_URL}/business/register", json=test_company_data)
            
            if response.status_code in [200, 201]:
                company_data = response.json()
                company_id = company_data.get("company_id")
                
                # Now create a business user
                test_user_data = {
                    "email": "testuser@testinvestigation.com",
                    "password": "TestPass123!",
                    "full_name": "Test Business User",
                    "company_id": company_id,
                    "user_type": "business_employee"
                }
                
                user_response = requests.post(f"{BASE_URL}/auth/signup", json=test_user_data)
                
                if user_response.status_code in [200, 201]:
                    self.log_result("Test Business User Creation", True, 
                                  f"Created test business user with company_id: {company_id}")
                    
                    # Now check if it appears in business users list
                    time.sleep(2)  # Wait for database consistency
                    return self.verify_test_user_appears()
                else:
                    self.log_result("Test Business User Creation", False, 
                                  f"User creation failed: {user_response.status_code}")
                    return False
            else:
                self.log_result("Test Business User Creation", False, 
                              f"Company creation failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Test Business User Creation", False, f"Exception: {str(e)}")
            return False

    def verify_test_user_appears(self):
        """Verify that the test user appears in business users list"""
        print("✅ Verifying test user appears in business users list...")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = requests.get(f"{BASE_URL}/admin/business-users", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                business_users = data.get("business_users", [])
                
                test_user_found = any(u.get("email") == "testuser@testinvestigation.com" for u in business_users)
                
                if test_user_found:
                    self.log_result("Test User Verification", True, 
                                  "Test business user appears in business users list - system is working")
                    return True
                else:
                    self.log_result("Test User Verification", False, 
                                  "Test business user does NOT appear in business users list - issue confirmed")
                    return False
            else:
                self.log_result("Test User Verification", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Test User Verification", False, f"Exception: {str(e)}")
            return False

    def run_investigation(self):
        """Run complete business users database investigation"""
        print("🚀 Starting Business Users Database Investigation")
        print("=" * 70)
        
        # Setup
        if not self.setup_admin_auth():
            print("❌ Failed to authenticate as admin. Aborting investigation.")
            return
        
        # Run investigation steps
        print("\n🔍 STEP 1: Investigating all users in database...")
        self.investigate_all_users_in_database()
        
        print("\n🔍 STEP 2: Testing business users API endpoint...")
        self.test_business_users_api_endpoint()
        
        print("\n🔍 STEP 3: Analyzing user type values...")
        self.analyze_user_type_values()
        
        print("\n🔍 STEP 4: Checking business payment users...")
        self.check_business_payment_users()
        
        print("\n🔍 STEP 5: Testing query logic...")
        self.test_business_users_query_logic()
        
        print("\n🔍 STEP 6: Creating test business user...")
        self.create_test_business_user()
        
        # Summary
        self.print_investigation_summary()

    def print_investigation_summary(self):
        """Print investigation summary"""
        print("\n" + "=" * 70)
        print("🎯 BUSINESS USERS DATABASE INVESTIGATION SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"📊 Total Investigation Steps: {total_tests}")
        print(f"✅ Successful: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print()
        
        # Key findings
        print("🔍 KEY FINDINGS:")
        for result in self.results:
            if not result["success"] or "business users" in result["details"].lower():
                print(f"   {result['status']}: {result['test']}")
                print(f"      {result['details']}")
                print()
        
        # Recommendations
        print("💡 RECOMMENDATIONS:")
        print("   1. Check if business users have user_type='business_employee' or 'business_admin'")
        print("   2. Verify business payment success handler creates users correctly")
        print("   3. Check MongoDB query in GET /api/admin/business-users endpoint")
        print("   4. Ensure company_id is properly set during business signup")
        print("   5. Verify business signup flow creates users with correct user_type")
        
        print("=" * 70)

if __name__ == "__main__":
    investigator = BusinessUsersInvestigator()
    investigator.run_investigation()