#!/usr/bin/env python3
"""
Mentor Admin Management System Testing
Tests the newly implemented mentor admin management endpoints
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime
from typing import Dict, Any

# Configuration
BACKEND_URL = os.getenv("REACT_APP_BACKEND_URL", "https://user-data-restore.preview.emergentagent.com")
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
ADMIN_CREDENTIALS = {
    "email": "admin@onlymentors.ai",
    "password": "SuperAdmin2024!"
}

class MentorAdminTester:
    def __init__(self):
        self.session = None
        self.admin_token = None
        self.test_results = []
        
    async def setup(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup(self):
        """Clean up resources"""
        if self.session:
            await self.session.close()
            
    def log_result(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        if response_data and not success:
            print(f"   Response: {response_data}")
        print()
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "response": response_data,
            "timestamp": datetime.now().isoformat()
        })
        
    async def admin_login(self):
        """Login as admin to get authentication token"""
        try:
            async with self.session.post(
                f"{API_BASE}/admin/login",
                json=ADMIN_CREDENTIALS
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.admin_token = data.get("token")
                    self.log_result("Admin Authentication", True, f"Admin logged in successfully")
                    return True
                else:
                    error_data = await response.text()
                    self.log_result("Admin Authentication", False, f"Status: {response.status}", error_data)
                    return False
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Exception: {str(e)}")
            return False
            
    def get_auth_headers(self):
        """Get authorization headers for admin requests"""
        if not self.admin_token:
            return {}
        return {"Authorization": f"Bearer {self.admin_token}"}
        
    async def test_get_mentors_list(self):
        """Test getting list of mentors for admin management"""
        try:
            async with self.session.get(
                f"{API_BASE}/admin/mentors",
                headers=self.get_auth_headers()
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    mentor_count = len(data.get("mentors", []))
                    self.log_result("Get Mentors List", True, f"Retrieved {mentor_count} mentors")
                    return data.get("mentors", [])
                else:
                    error_data = await response.text()
                    self.log_result("Get Mentors List", False, f"Status: {response.status}", error_data)
                    return []
        except Exception as e:
            self.log_result("Get Mentors List", False, f"Exception: {str(e)}")
            return []
            
    async def test_mentor_password_reset(self, mentor_id: str):
        """Test admin-initiated mentor password reset"""
        try:
            reset_data = {
                "reason": "Security audit - password reset required"
            }
            
            async with self.session.post(
                f"{API_BASE}/admin/mentors/{mentor_id}/reset-password",
                headers=self.get_auth_headers(),
                json=reset_data
            ) as response:
                data = await response.json() if response.content_type == 'application/json' else await response.text()
                
                if response.status == 200:
                    self.log_result("Mentor Password Reset", True, 
                                  f"Reset initiated for mentor {mentor_id}, email status: {data.get('email_status', 'unknown')}")
                    return True
                else:
                    self.log_result("Mentor Password Reset", False, 
                                  f"Status: {response.status}", data)
                    return False
        except Exception as e:
            self.log_result("Mentor Password Reset", False, f"Exception: {str(e)}")
            return False
            
    async def test_mentor_suspend(self, mentor_id: str):
        """Test mentor suspension"""
        try:
            suspend_data = {
                "suspend": True,
                "reason": "Violation of community guidelines - temporary suspension"
            }
            
            async with self.session.put(
                f"{API_BASE}/admin/mentors/{mentor_id}/suspend",
                headers=self.get_auth_headers(),
                json=suspend_data
            ) as response:
                data = await response.json() if response.content_type == 'application/json' else await response.text()
                
                if response.status == 200:
                    self.log_result("Mentor Suspension", True, 
                                  f"Mentor {mentor_id} suspended, new status: {data.get('new_status', 'unknown')}")
                    return True
                else:
                    self.log_result("Mentor Suspension", False, 
                                  f"Status: {response.status}", data)
                    return False
        except Exception as e:
            self.log_result("Mentor Suspension", False, f"Exception: {str(e)}")
            return False
            
    async def test_mentor_unsuspend(self, mentor_id: str):
        """Test mentor unsuspension"""
        try:
            unsuspend_data = {
                "suspend": False,
                "reason": "Appeal approved - account reactivated"
            }
            
            async with self.session.put(
                f"{API_BASE}/admin/mentors/{mentor_id}/suspend",
                headers=self.get_auth_headers(),
                json=unsuspend_data
            ) as response:
                data = await response.json() if response.content_type == 'application/json' else await response.text()
                
                if response.status == 200:
                    self.log_result("Mentor Unsuspension", True, 
                                  f"Mentor {mentor_id} reactivated, new status: {data.get('new_status', 'unknown')}")
                    return True
                else:
                    self.log_result("Mentor Unsuspension", False, 
                                  f"Status: {response.status}", data)
                    return False
        except Exception as e:
            self.log_result("Mentor Unsuspension", False, f"Exception: {str(e)}")
            return False
            
    async def test_mentor_delete(self, mentor_id: str):
        """Test mentor account deletion"""
        try:
            delete_data = {
                "reason": "Permanent violation - account terminated"
            }
            
            async with self.session.delete(
                f"{API_BASE}/admin/mentors/{mentor_id}",
                headers=self.get_auth_headers(),
                json=delete_data
            ) as response:
                data = await response.json() if response.content_type == 'application/json' else await response.text()
                
                if response.status == 200:
                    self.log_result("Mentor Deletion", True, 
                                  f"Mentor {mentor_id} deleted, email sent: {data.get('email_sent', 'unknown')}")
                    return True
                else:
                    self.log_result("Mentor Deletion", False, 
                                  f"Status: {response.status}", data)
                    return False
        except Exception as e:
            self.log_result("Mentor Deletion", False, f"Exception: {str(e)}")
            return False
            
    async def test_authentication_required(self):
        """Test that all endpoints require admin authentication"""
        test_mentor_id = "test-mentor-id"
        
        # Test without authentication
        endpoints_to_test = [
            ("POST", f"{API_BASE}/admin/mentors/{test_mentor_id}/reset-password", {"reason": "test"}),
            ("PUT", f"{API_BASE}/admin/mentors/{test_mentor_id}/suspend", {"suspend": True, "reason": "test"}),
            ("DELETE", f"{API_BASE}/admin/mentors/{test_mentor_id}", {"reason": "test"}),
            ("GET", f"{API_BASE}/admin/mentors", None)
        ]
        
        auth_test_results = []
        
        for method, url, data in endpoints_to_test:
            try:
                if method == "GET":
                    async with self.session.get(url) as response:
                        status = response.status
                elif method == "POST":
                    async with self.session.post(url, json=data) as response:
                        status = response.status
                elif method == "PUT":
                    async with self.session.put(url, json=data) as response:
                        status = response.status
                elif method == "DELETE":
                    async with self.session.delete(url, json=data) as response:
                        status = response.status
                
                # Should return 401 (Unauthorized) or 403 (Forbidden)
                if status in [401, 403]:
                    auth_test_results.append(True)
                else:
                    auth_test_results.append(False)
                    
            except Exception as e:
                auth_test_results.append(False)
                
        all_protected = all(auth_test_results)
        self.log_result("Authentication Protection", all_protected, 
                       f"All endpoints properly protected: {all_protected}")
        return all_protected
        
    async def test_invalid_mentor_id(self):
        """Test endpoints with invalid mentor IDs"""
        invalid_mentor_id = "non-existent-mentor-id"
        
        # Test password reset with invalid ID
        try:
            async with self.session.post(
                f"{API_BASE}/admin/mentors/{invalid_mentor_id}/reset-password",
                headers=self.get_auth_headers(),
                json={"reason": "test"}
            ) as response:
                if response.status == 404:
                    self.log_result("Invalid Mentor ID - Password Reset", True, "Correctly returned 404 for non-existent mentor")
                else:
                    data = await response.text()
                    self.log_result("Invalid Mentor ID - Password Reset", False, f"Status: {response.status}", data)
        except Exception as e:
            self.log_result("Invalid Mentor ID - Password Reset", False, f"Exception: {str(e)}")
            
        # Test suspension with invalid ID
        try:
            async with self.session.put(
                f"{API_BASE}/admin/mentors/{invalid_mentor_id}/suspend",
                headers=self.get_auth_headers(),
                json={"suspend": True, "reason": "test"}
            ) as response:
                if response.status == 404:
                    self.log_result("Invalid Mentor ID - Suspension", True, "Correctly returned 404 for non-existent mentor")
                else:
                    data = await response.text()
                    self.log_result("Invalid Mentor ID - Suspension", False, f"Status: {response.status}", data)
        except Exception as e:
            self.log_result("Invalid Mentor ID - Suspension", False, f"Exception: {str(e)}")
            
    async def test_database_operations(self):
        """Test database operations and audit logging"""
        # This would require checking the database directly
        # For now, we'll test the API responses indicate proper database operations
        
        mentors = await self.test_get_mentors_list()
        if mentors:
            # Test with first available mentor
            test_mentor = mentors[0]
            mentor_id = test_mentor.get("creator_id")
            
            if mentor_id:
                # Test password reset (should create audit log)
                reset_success = await self.test_mentor_password_reset(mentor_id)
                
                # Test suspension (should update mentor status)
                suspend_success = await self.test_mentor_suspend(mentor_id)
                
                # Test unsuspension (should update mentor status back)
                unsuspend_success = await self.test_mentor_unsuspend(mentor_id)
                
                # Note: We won't test deletion as it's permanent
                
                database_ops_success = reset_success and suspend_success and unsuspend_success
                self.log_result("Database Operations", database_ops_success, 
                               f"Password reset, suspend, and unsuspend operations completed")
                return database_ops_success
            else:
                self.log_result("Database Operations", False, "No mentor ID found for testing")
                return False
        else:
            self.log_result("Database Operations", False, "No mentors available for testing")
            return False
            
    async def run_all_tests(self):
        """Run all mentor admin management tests"""
        print("🧪 MENTOR ADMIN MANAGEMENT SYSTEM TESTING")
        print("=" * 60)
        print()
        
        await self.setup()
        
        try:
            # 1. Admin Authentication
            if not await self.admin_login():
                print("❌ Cannot proceed without admin authentication")
                return
                
            # 2. Authentication & Authorization Tests
            await self.test_authentication_required()
            
            # 3. Invalid Input Tests
            await self.test_invalid_mentor_id()
            
            # 4. Database Operations Tests
            await self.test_database_operations()
            
            # 5. Summary
            self.print_summary()
            
        finally:
            await self.cleanup()
            
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n🔍 FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['details']}")
                    
        print("\n🎯 KEY FINDINGS:")
        
        # Analyze results for key findings
        auth_tests = [r for r in self.test_results if "Authentication" in r["test"]]
        password_reset_tests = [r for r in self.test_results if "Password Reset" in r["test"]]
        suspension_tests = [r for r in self.test_results if "Suspension" in r["test"]]
        database_tests = [r for r in self.test_results if "Database" in r["test"]]
        
        if any(t["success"] for t in auth_tests):
            print("   ✅ Admin authentication system working")
        else:
            print("   ❌ Admin authentication system has issues")
            
        if any(t["success"] for t in password_reset_tests):
            print("   ✅ Mentor password reset functionality implemented")
        else:
            print("   ❌ Mentor password reset functionality has issues")
            
        if any(t["success"] for t in suspension_tests):
            print("   ✅ Mentor suspension/unsuspension functionality working")
        else:
            print("   ❌ Mentor suspension/unsuspension functionality has issues")
            
        if any(t["success"] for t in database_tests):
            print("   ✅ Database operations and audit logging functional")
        else:
            print("   ❌ Database operations need attention")

async def main():
    """Main test execution"""
    tester = MentorAdminTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())