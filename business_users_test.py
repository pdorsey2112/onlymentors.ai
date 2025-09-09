#!/usr/bin/env python3
"""
Comprehensive Backend Test for Business Users Management System Fix Verification
Testing the fixed authentication and database query issues for business users endpoints.
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime
import sys

# Configuration
BACKEND_URL = os.getenv("REACT_APP_BACKEND_URL", "https://enterprise-coach.preview.emergentagent.com")
API_BASE = f"{BACKEND_URL}/api"

class BusinessUsersTestSuite:
    def __init__(self):
        self.session = None
        self.admin_token = None
        self.test_results = []
        
    async def setup_session(self):
        """Setup HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
            
    def log_test(self, test_name, success, details="", error=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        if error:
            print(f"   Error: {error}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "error": error
        })
        
    async def create_admin_token(self):
        """Create admin token for testing"""
        try:
            # Try to login as super admin
            login_data = {
                "email": "admin@onlymentors.ai",
                "password": "SuperAdmin2024!"
            }
            
            async with self.session.post(f"{API_BASE}/admin/login", json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.admin_token = data.get("token")
                    self.log_test("Admin Authentication Setup", True, f"Admin token obtained successfully")
                    return True
                else:
                    error_text = await response.text()
                    self.log_test("Admin Authentication Setup", False, error=f"Status {response.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("Admin Authentication Setup", False, error=str(e))
            return False
            
    async def test_business_users_authentication(self):
        """Test 1: Fixed Authentication Test - GET /api/admin/business-users with get_current_admin middleware"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"} if self.admin_token else {}
            
            # First, let's check what admin info we have
            async with self.session.get(f"{API_BASE}/admin/dashboard", headers=headers) as dashboard_response:
                if dashboard_response.status == 200:
                    dashboard_data = await dashboard_response.json()
                    print(f"   Debug: Admin dashboard accessible, checking admin role...")
                else:
                    print(f"   Debug: Admin dashboard failed with status {dashboard_response.status}")
            
            async with self.session.get(f"{API_BASE}/admin/business-users", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    users = data.get("users", [])
                    total_count = data.get("total_count", 0)
                    
                    self.log_test(
                        "Business Users Authentication Fix", 
                        True, 
                        f"Endpoint accessible with admin auth. Found {total_count} business users"
                    )
                    return users
                    
                elif response.status in [401, 403]:
                    error_text = await response.text()
                    self.log_test(
                        "Business Users Authentication Fix", 
                        False, 
                        error=f"Authentication failed: {response.status} - {error_text}"
                    )
                    return []
                else:
                    error_text = await response.text()
                    self.log_test(
                        "Business Users Authentication Fix", 
                        False, 
                        error=f"Unexpected status {response.status}: {error_text}"
                    )
                    return []
                    
        except Exception as e:
            self.log_test("Business Users Authentication Fix", False, error=str(e))
            return []
            
    async def test_database_query_fix(self, business_users):
        """Test 2: Updated Database Query Test - verify query finds users with company_id"""
        try:
            # Analyze the returned business users
            users_with_company_id = [user for user in business_users if user.get("company_id")]
            users_with_user_type = [user for user in business_users if user.get("user_type") in ["business_employee", "business_admin"]]
            users_with_company_info = [user for user in business_users if user.get("company_name")]
            
            # Check if query is working correctly
            if len(users_with_company_id) > 0:
                self.log_test(
                    "Database Query Fix (company_id filter)", 
                    True, 
                    f"Found {len(users_with_company_id)} users with company_id. Company info enriched for {len(users_with_company_info)} users"
                )
                
                # Log details about the users found
                for user in users_with_company_id[:3]:  # Show first 3 users
                    print(f"   User: {user.get('full_name', 'N/A')} | Email: {user.get('email', 'N/A')} | Company: {user.get('company_name', 'N/A')}")
                    
                return True
            else:
                self.log_test(
                    "Database Query Fix (company_id filter)", 
                    False, 
                    error="No users found with company_id. Query may not be working correctly"
                )
                return False
                
        except Exception as e:
            self.log_test("Database Query Fix (company_id filter)", False, error=str(e))
            return False
            
    async def test_business_user_management_actions(self, business_users):
        """Test 3: Business User Management Actions - POST /api/admin/business-users/manage"""
        if not business_users:
            self.log_test("Business User Management Actions", False, error="No business users available for testing")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"} if self.admin_token else {}
            test_user = business_users[0]  # Use first business user for testing
            user_id = test_user.get("user_id")
            
            if not user_id:
                self.log_test("Business User Management Actions", False, error="No user_id found in business user data")
                return False
            
            # Test suspend action
            suspend_data = {
                "user_ids": [user_id],
                "action": "suspend",
                "reason": "Test suspension by admin"
            }
            
            async with self.session.post(f"{API_BASE}/admin/business-users/manage", json=suspend_data, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    results = data.get("results", [])
                    
                    if results and results[0].get("status") == "suspended":
                        self.log_test(
                            "Business User Management - Suspend Action", 
                            True, 
                            f"Successfully suspended user {user_id}"
                        )
                        
                        # Test activate action to restore user
                        activate_data = {
                            "user_ids": [user_id],
                            "action": "activate",
                            "reason": "Test activation by admin"
                        }
                        
                        async with self.session.post(f"{API_BASE}/admin/business-users/manage", json=activate_data, headers=headers) as activate_response:
                            if activate_response.status == 200:
                                activate_result = await activate_response.json()
                                activate_results = activate_result.get("results", [])
                                
                                if activate_results and activate_results[0].get("status") == "activated":
                                    self.log_test(
                                        "Business User Management - Activate Action", 
                                        True, 
                                        f"Successfully activated user {user_id}"
                                    )
                                    return True
                                else:
                                    self.log_test(
                                        "Business User Management - Activate Action", 
                                        False, 
                                        error=f"Activation failed: {activate_results}"
                                    )
                                    return False
                            else:
                                error_text = await activate_response.text()
                                self.log_test(
                                    "Business User Management - Activate Action", 
                                    False, 
                                    error=f"Status {activate_response.status}: {error_text}"
                                )
                                return False
                    else:
                        self.log_test(
                            "Business User Management - Suspend Action", 
                            False, 
                            error=f"Suspension failed: {results}"
                        )
                        return False
                else:
                    error_text = await response.text()
                    self.log_test(
                        "Business User Management - Suspend Action", 
                        False, 
                        error=f"Status {response.status}: {error_text}"
                    )
                    return False
                    
        except Exception as e:
            self.log_test("Business User Management Actions", False, error=str(e))
            return False
            
    async def test_password_reset_functionality(self, business_users):
        """Test 4: Password Reset Functionality"""
        if not business_users:
            self.log_test("Password Reset Functionality", False, error="No business users available for testing")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"} if self.admin_token else {}
            test_user = business_users[0]  # Use first business user for testing
            user_id = test_user.get("user_id")
            
            if not user_id:
                self.log_test("Password Reset Functionality", False, error="No user_id found in business user data")
                return False
            
            reset_data = {"user_id": user_id}
            
            async with self.session.post(f"{API_BASE}/admin/business-users/reset-password", json=reset_data, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    temp_password = data.get("temporary_password")
                    
                    if temp_password and len(temp_password) == 12:
                        self.log_test(
                            "Password Reset Functionality", 
                            True, 
                            f"Successfully generated temporary password for user {user_id} (length: {len(temp_password)})"
                        )
                        return True
                    else:
                        self.log_test(
                            "Password Reset Functionality", 
                            False, 
                            error=f"Invalid temporary password generated: {temp_password}"
                        )
                        return False
                else:
                    error_text = await response.text()
                    self.log_test(
                        "Password Reset Functionality", 
                        False, 
                        error=f"Status {response.status}: {error_text}"
                    )
                    return False
                    
        except Exception as e:
            self.log_test("Password Reset Functionality", False, error=str(e))
            return False
            
    async def test_user_type_field_analysis(self, business_users):
        """Test 5: User Type Field Analysis - check if existing business users appear in results"""
        try:
            if not business_users:
                self.log_test(
                    "User Type Field Analysis", 
                    False, 
                    error="No business users found - this indicates the query fix may not be working"
                )
                return False
            
            # Analyze user types and company associations
            users_by_type = {}
            users_with_company = 0
            users_with_null_type = 0
            
            for user in business_users:
                user_type = user.get("user_type")
                company_id = user.get("company_id")
                
                if company_id:
                    users_with_company += 1
                    
                if user_type is None:
                    users_with_null_type += 1
                    
                if user_type not in users_by_type:
                    users_by_type[user_type] = 0
                users_by_type[user_type] += 1
            
            # Check if we found the expected business users
            total_users = len(business_users)
            if total_users >= 3:  # Looking for the 3 business users mentioned in review
                self.log_test(
                    "User Type Field Analysis", 
                    True, 
                    f"Found {total_users} business users. {users_with_company} have company_id. User types: {users_by_type}"
                )
                
                # Additional analysis
                if users_with_null_type > 0:
                    print(f"   Note: {users_with_null_type} users have null user_type (this is expected if query now uses company_id)")
                    
                return True
            else:
                self.log_test(
                    "User Type Field Analysis", 
                    False, 
                    error=f"Only found {total_users} business users, expected at least 3. User types: {users_by_type}"
                )
                return False
                
        except Exception as e:
            self.log_test("User Type Field Analysis", False, error=str(e))
            return False
            
    async def test_end_to_end_verification(self):
        """Test 6: End-to-End Verification - complete business user management workflow"""
        try:
            print("\n🔍 PERFORMING END-TO-END BUSINESS USERS MANAGEMENT VERIFICATION...")
            
            # Step 1: Get business users with admin authentication
            business_users = await self.test_business_users_authentication()
            
            if not business_users:
                self.log_test(
                    "End-to-End Verification", 
                    False, 
                    error="Failed to retrieve business users - authentication or query issue"
                )
                return False
            
            # Step 2: Verify database query fix
            query_success = await self.test_database_query_fix(business_users)
            
            # Step 3: Test management actions
            management_success = await self.test_business_user_management_actions(business_users)
            
            # Step 4: Test password reset
            password_success = await self.test_password_reset_functionality(business_users)
            
            # Step 5: Analyze user type fields
            analysis_success = await self.test_user_type_field_analysis(business_users)
            
            # Overall success
            overall_success = query_success and management_success and password_success and analysis_success
            
            self.log_test(
                "End-to-End Verification", 
                overall_success, 
                f"Complete workflow test. Query: {query_success}, Management: {management_success}, Password: {password_success}, Analysis: {analysis_success}"
            )
            
            return overall_success
            
        except Exception as e:
            self.log_test("End-to-End Verification", False, error=str(e))
            return False
            
    async def run_comprehensive_tests(self):
        """Run all business users management tests"""
        print("🚀 STARTING COMPREHENSIVE BUSINESS USERS MANAGEMENT FIX VERIFICATION")
        print("=" * 80)
        
        await self.setup_session()
        
        try:
            # Setup admin authentication
            auth_success = await self.create_admin_token()
            if not auth_success:
                print("\n❌ CRITICAL: Cannot proceed without admin authentication")
                return False
            
            # Run end-to-end verification
            success = await self.test_end_to_end_verification()
            
            # Print summary
            print("\n" + "=" * 80)
            print("📊 TEST RESULTS SUMMARY")
            print("=" * 80)
            
            passed = sum(1 for result in self.test_results if result["success"])
            total = len(self.test_results)
            
            for result in self.test_results:
                status = "✅" if result["success"] else "❌"
                print(f"{status} {result['test']}")
                if result["error"]:
                    print(f"   Error: {result['error']}")
            
            print(f"\n📈 OVERALL RESULTS: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
            
            if passed == total:
                print("🎉 ALL BUSINESS USERS MANAGEMENT FIXES VERIFIED SUCCESSFULLY!")
                return True
            else:
                print("🚨 SOME TESTS FAILED - FIXES MAY NOT BE COMPLETE")
                return False
                
        finally:
            await self.cleanup_session()

async def main():
    """Main test execution"""
    test_suite = BusinessUsersTestSuite()
    success = await test_suite.run_comprehensive_tests()
    
    if success:
        print("\n✅ Business Users Management System Fix Verification: PASSED")
        sys.exit(0)
    else:
        print("\n❌ Business Users Management System Fix Verification: FAILED")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())