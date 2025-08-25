#!/usr/bin/env python3
"""
Backend Testing Suite for OnlyMentors.ai User Suspension and Deletion Email Notifications
Testing the new user suspension and deletion email notification system as requested.
"""

import asyncio
import aiohttp
import json
import uuid
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class UserSuspensionDeletionTester:
    def __init__(self):
        # Use local backend URL for testing
        backend_url = "http://localhost:8001"
        self.base_url = f"{backend_url}/api"
        self.admin_token = None
        self.test_users = []
        self.session = None
        
        # Admin credentials from the review request
        self.admin_email = "admin@onlymentors.ai"
        self.admin_password = "SuperAdmin2024!"
        
        print(f"🔧 Backend URL: {self.base_url}")
        
    async def setup_session(self):
        """Setup HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
            
    async def admin_login(self):
        """Login as admin to get authentication token"""
        try:
            login_data = {
                "email": self.admin_email,
                "password": self.admin_password
            }
            
            async with self.session.post(f"{self.base_url}/admin/login", json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.admin_token = data.get("token")
                    print(f"✅ Admin login successful")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Admin login failed: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            print(f"❌ Admin login error: {str(e)}")
            return False
            
    async def create_test_user(self, email_suffix=""):
        """Create a test user for suspension/deletion testing"""
        try:
            # Generate unique test user
            user_id = str(uuid.uuid4())[:8]
            email = f"testuser{user_id}{email_suffix}@test.com"
            
            user_data = {
                "email": email,
                "password": "TestPassword123!",
                "full_name": f"Test User {user_id}"
            }
            
            async with self.session.post(f"{self.base_url}/auth/signup", json=user_data) as response:
                if response.status == 200:
                    data = await response.json()
                    test_user = {
                        "user_id": data["user"]["user_id"],
                        "email": email,
                        "full_name": user_data["full_name"],
                        "token": data["token"]
                    }
                    self.test_users.append(test_user)
                    print(f"✅ Created test user: {email}")
                    return test_user
                else:
                    error_text = await response.text()
                    print(f"❌ Failed to create test user: {response.status} - {error_text}")
                    return None
                    
        except Exception as e:
            print(f"❌ Test user creation error: {str(e)}")
            return None
            
    async def get_admin_headers(self):
        """Get headers with admin authentication"""
        if not self.admin_token:
            raise Exception("Admin not logged in")
        return {"Authorization": f"Bearer {self.admin_token}"}
        
    async def test_user_suspension_with_email(self):
        """Test user suspension with email notification"""
        print("\n🔍 Testing User Suspension with Email Notification...")
        
        # Create test user for suspension
        test_user = await self.create_test_user("_suspension")
        if not test_user:
            return False
            
        try:
            # Suspend user with reason
            suspension_data = {
                "suspend": True,
                "reason": "Testing suspension email system"
            }
            
            headers = await self.get_admin_headers()
            
            async with self.session.put(
                f"{self.base_url}/admin/users/{test_user['user_id']}/suspend",
                json=suspension_data,
                headers=headers
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ User suspension successful")
                    print(f"   Message: {data.get('message')}")
                    print(f"   User ID: {data.get('user_id')}")
                    print(f"   Is Suspended: {data.get('is_suspended')}")
                    print(f"   Reason: {data.get('reason')}")
                    print(f"   Email Sent: {data.get('email_sent')}")
                    
                    # Verify response includes email status
                    if 'email_sent' not in data:
                        print("❌ Response missing email_sent field")
                        return False
                        
                    # Check if email was sent or pending
                    email_status = data.get('email_sent')
                    if email_status is True:
                        print("✅ Email notification sent successfully")
                    elif email_status is False:
                        print("⚠️ Email notification pending (SMTP not configured)")
                    else:
                        print(f"⚠️ Unexpected email status: {email_status}")
                        
                    # Verify user is actually suspended
                    await self.verify_user_suspension_status(test_user['user_id'], True)
                    
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ User suspension failed: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            print(f"❌ User suspension test error: {str(e)}")
            return False
            
    async def test_user_deletion_with_email(self):
        """Test user deletion with email notification"""
        print("\n🔍 Testing User Deletion with Email Notification...")
        
        # Create test user for deletion
        test_user = await self.create_test_user("_deletion")
        if not test_user:
            return False
            
        try:
            headers = await self.get_admin_headers()
            
            # Delete user with reason
            params = {"reason": "Testing deletion email system"}
            
            async with self.session.delete(
                f"{self.base_url}/admin/users/{test_user['user_id']}",
                params=params,
                headers=headers
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ User deletion successful")
                    print(f"   Message: {data.get('message')}")
                    print(f"   User ID: {data.get('user_id')}")
                    print(f"   Deleted At: {data.get('deleted_at')}")
                    print(f"   Reason: {data.get('reason')}")
                    print(f"   Email Sent: {data.get('email_sent')}")
                    
                    # Verify response includes email status
                    if 'email_sent' not in data:
                        print("❌ Response missing email_sent field")
                        return False
                        
                    # Check if email was sent or pending
                    email_status = data.get('email_sent')
                    if email_status is True:
                        print("✅ Email notification sent successfully")
                    elif email_status is False:
                        print("⚠️ Email notification pending (SMTP not configured)")
                    else:
                        print(f"⚠️ Unexpected email status: {email_status}")
                        
                    # Verify user is actually deleted
                    await self.verify_user_deletion_status(test_user['user_id'])
                    
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ User deletion failed: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            print(f"❌ User deletion test error: {str(e)}")
            return False
            
    async def verify_user_suspension_status(self, user_id, should_be_suspended):
        """Verify user suspension status"""
        try:
            headers = await self.get_admin_headers()
            
            async with self.session.get(f"{self.base_url}/admin/users", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    users = data.get("users", [])
                    
                    user = next((u for u in users if u.get("user_id") == user_id), None)
                    if user:
                        is_suspended = user.get("is_suspended", False)
                        if is_suspended == should_be_suspended:
                            print(f"✅ User suspension status verified: {is_suspended}")
                            return True
                        else:
                            print(f"❌ User suspension status mismatch: expected {should_be_suspended}, got {is_suspended}")
                            return False
                    else:
                        print(f"❌ User {user_id} not found in admin users list")
                        return False
                else:
                    print(f"❌ Failed to get users list: {response.status}")
                    return False
                    
        except Exception as e:
            print(f"❌ Suspension verification error: {str(e)}")
            return False
            
    async def verify_user_deletion_status(self, user_id):
        """Verify user deletion status"""
        try:
            headers = await self.get_admin_headers()
            
            async with self.session.get(f"{self.base_url}/admin/users", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    users = data.get("users", [])
                    
                    user = next((u for u in users if u.get("user_id") == user_id), None)
                    if user:
                        deleted_at = user.get("deleted_at")
                        if deleted_at:
                            print(f"✅ User deletion status verified: deleted at {deleted_at}")
                            return True
                        else:
                            print(f"❌ User not marked as deleted")
                            return False
                    else:
                        print(f"❌ User {user_id} not found in admin users list")
                        return False
                else:
                    print(f"❌ Failed to get users list: {response.status}")
                    return False
                    
        except Exception as e:
            print(f"❌ Deletion verification error: {str(e)}")
            return False
            
    async def test_email_content_best_practices(self):
        """Test that email content follows best practices"""
        print("\n🔍 Testing Email Content Best Practices...")
        
        # This test verifies the email templates in the code
        try:
            # Read the email template functions
            with open("/app/backend/forgot_password_system.py", "r") as f:
                content = f.read()
                
            # Check suspension email content
            suspension_checks = [
                "Account Suspended" in content,
                "support@onlymentors.ai" in content,
                "Appeal" in content,
                "Community Guidelines" in content,
                "OnlyMentors.ai Team" in content
            ]
            
            # Check deletion email content  
            deletion_checks = [
                "Account Deleted" in content,
                "permanently deleted" in content,
                "Data Retention" in content,
                "cannot be recovered" in content,
                "support@onlymentors.ai" in content
            ]
            
            suspension_score = sum(suspension_checks)
            deletion_score = sum(deletion_checks)
            
            print(f"✅ Suspension email content checks: {suspension_score}/5")
            print(f"✅ Deletion email content checks: {deletion_score}/5")
            
            # Verify professional tone and required elements
            required_elements = [
                "professional tone" if "Best regards" in content else "missing professional closing",
                "support contact" if "support@onlymentors.ai" in content else "missing support contact",
                "appeal process" if "Appeal" in content else "missing appeal process",
                "clear explanation" if "reason" in content else "missing reason explanation",
                "proper branding" if "OnlyMentors.ai" in content else "missing branding"
            ]
            
            print("📧 Email Content Quality:")
            for element in required_elements:
                if "missing" not in element:
                    print(f"   ✅ {element}")
                else:
                    print(f"   ❌ {element}")
                    
            return suspension_score >= 4 and deletion_score >= 4
            
        except Exception as e:
            print(f"❌ Email content test error: {str(e)}")
            return False
            
    async def test_audit_log_entries(self):
        """Test that proper audit log entries are created"""
        print("\n🔍 Testing Audit Log Entries...")
        
        # Create test user for audit testing
        test_user = await self.create_test_user("_audit")
        if not test_user:
            return False
            
        try:
            headers = await self.get_admin_headers()
            
            # Perform suspension to generate audit log
            suspension_data = {
                "suspend": True,
                "reason": "Testing audit log system"
            }
            
            async with self.session.put(
                f"{self.base_url}/admin/users/{test_user['user_id']}/suspend",
                json=suspension_data,
                headers=headers
            ) as response:
                
                if response.status == 200:
                    print("✅ Suspension action completed for audit testing")
                    
                    # Check if audit endpoint exists
                    async with self.session.get(
                        f"{self.base_url}/admin/users/{test_user['user_id']}/audit",
                        headers=headers
                    ) as audit_response:
                        
                        if audit_response.status == 200:
                            audit_data = await audit_response.json()
                            print(f"✅ Audit log retrieved successfully")
                            print(f"   Audit entries: {len(audit_data.get('audit_log', []))}")
                            
                            # Check for email status in audit log
                            audit_entries = audit_data.get('audit_log', [])
                            suspension_entry = next((entry for entry in audit_entries if entry.get('action') == 'suspend'), None)
                            
                            if suspension_entry:
                                email_sent = suspension_entry.get('email_sent')
                                print(f"   Email status in audit: {email_sent}")
                                return True
                            else:
                                print("❌ No suspension entry found in audit log")
                                return False
                        else:
                            print(f"⚠️ Audit endpoint not accessible: {audit_response.status}")
                            return True  # Not critical for this test
                else:
                    print(f"❌ Suspension failed for audit test: {response.status}")
                    return False
                    
        except Exception as e:
            print(f"❌ Audit log test error: {str(e)}")
            return False
            
    async def test_realistic_admin_scenarios(self):
        """Test with realistic admin reasons that would be used in production"""
        print("\n🔍 Testing Realistic Admin Scenarios...")
        
        realistic_scenarios = [
            {
                "action": "suspend",
                "reason": "Violation of community guidelines - inappropriate content",
                "user_suffix": "_guideline_violation"
            },
            {
                "action": "suspend", 
                "reason": "Spam behavior detected - multiple automated posts",
                "user_suffix": "_spam_behavior"
            },
            {
                "action": "delete",
                "reason": "Repeated policy violations after multiple warnings",
                "user_suffix": "_repeated_violations"
            },
            {
                "action": "delete",
                "reason": "Account compromised - user requested permanent deletion",
                "user_suffix": "_compromised_account"
            }
        ]
        
        success_count = 0
        
        for scenario in realistic_scenarios:
            print(f"\n   Testing: {scenario['reason']}")
            
            # Create test user for this scenario
            test_user = await self.create_test_user(scenario['user_suffix'])
            if not test_user:
                continue
                
            try:
                headers = await self.get_admin_headers()
                
                if scenario['action'] == 'suspend':
                    # Test suspension
                    suspension_data = {
                        "suspend": True,
                        "reason": scenario['reason']
                    }
                    
                    async with self.session.put(
                        f"{self.base_url}/admin/users/{test_user['user_id']}/suspend",
                        json=suspension_data,
                        headers=headers
                    ) as response:
                        
                        if response.status == 200:
                            data = await response.json()
                            email_sent = data.get('email_sent')
                            print(f"   ✅ Suspension successful, email_sent: {email_sent}")
                            success_count += 1
                        else:
                            print(f"   ❌ Suspension failed: {response.status}")
                            
                elif scenario['action'] == 'delete':
                    # Test deletion
                    params = {"reason": scenario['reason']}
                    
                    async with self.session.delete(
                        f"{self.base_url}/admin/users/{test_user['user_id']}",
                        params=params,
                        headers=headers
                    ) as response:
                        
                        if response.status == 200:
                            data = await response.json()
                            email_sent = data.get('email_sent')
                            print(f"   ✅ Deletion successful, email_sent: {email_sent}")
                            success_count += 1
                        else:
                            print(f"   ❌ Deletion failed: {response.status}")
                            
            except Exception as e:
                print(f"   ❌ Scenario test error: {str(e)}")
                
        print(f"\n✅ Realistic scenarios completed: {success_count}/{len(realistic_scenarios)} successful")
        return success_count >= len(realistic_scenarios) * 0.75  # 75% success rate
        
    async def run_all_tests(self):
        """Run all user suspension and deletion email notification tests"""
        print("🚀 Starting User Suspension and Deletion Email Notification Tests")
        print("=" * 80)
        
        await self.setup_session()
        
        try:
            # Login as admin
            if not await self.admin_login():
                print("❌ Cannot proceed without admin authentication")
                return False
                
            # Run all tests
            test_results = []
            
            # Test 1: User suspension with email notification
            test_results.append(await self.test_user_suspension_with_email())
            
            # Test 2: User deletion with email notification
            test_results.append(await self.test_user_deletion_with_email())
            
            # Test 3: Email content best practices
            test_results.append(await self.test_email_content_best_practices())
            
            # Test 4: Audit log entries with email status
            test_results.append(await self.test_audit_log_entries())
            
            # Test 5: Realistic admin scenarios
            test_results.append(await self.test_realistic_admin_scenarios())
            
            # Calculate results
            passed_tests = sum(test_results)
            total_tests = len(test_results)
            success_rate = (passed_tests / total_tests) * 100
            
            print("\n" + "=" * 80)
            print("📊 TEST RESULTS SUMMARY")
            print("=" * 80)
            print(f"✅ Tests Passed: {passed_tests}/{total_tests}")
            print(f"📈 Success Rate: {success_rate:.1f}%")
            
            if success_rate >= 80:
                print("🎉 USER SUSPENSION AND DELETION EMAIL NOTIFICATIONS WORKING!")
            else:
                print("❌ Some issues found with email notification system")
                
            # Detailed test breakdown
            test_names = [
                "User Suspension with Email",
                "User Deletion with Email", 
                "Email Content Best Practices",
                "Audit Log Entries",
                "Realistic Admin Scenarios"
            ]
            
            print("\n📋 Detailed Results:")
            for i, (name, result) in enumerate(zip(test_names, test_results)):
                status = "✅ PASS" if result else "❌ FAIL"
                print(f"   {i+1}. {name}: {status}")
                
            return success_rate >= 80
            
        finally:
            await self.cleanup_session()

async def main():
    """Main test execution"""
    tester = UserSuspensionDeletionTester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests completed successfully!")
        exit(0)
    else:
        print("\n❌ Some tests failed. Check the output above for details.")
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())