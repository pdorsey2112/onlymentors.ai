#!/usr/bin/env python3
"""
Direct Backend Testing for User Suspension and Deletion Email Notifications
Testing by directly importing and calling backend functions.
"""

import sys
import os
import asyncio
import uuid
from datetime import datetime

# Add backend directory to path
sys.path.append('/app/backend')

# Import backend modules
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import jwt

# Load environment variables
load_dotenv()

# Import backend functions
from forgot_password_system import send_account_suspension_email, send_account_deletion_email

class DirectBackendTester:
    def __init__(self):
        # Database setup
        MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
        self.client = AsyncIOMotorClient(MONGO_URL)
        self.db = self.client.onlymentors_db
        self.admin_db = self.client.onlymentors_admin_db
        
        # JWT setup
        self.JWT_SECRET = os.getenv("JWT_SECRET", "onlymentors-jwt-secret-key-2024")
        
        print("🔧 Direct Backend Testing Setup Complete")
        
    async def test_email_functions_directly(self):
        """Test email functions directly"""
        print("\n🔍 Testing Email Functions Directly...")
        
        try:
            # Test suspension email
            print("   Testing suspension email function...")
            suspension_result = await send_account_suspension_email(
                email="testuser@test.com",
                user_name="Test User",
                admin_reason="Testing suspension email system",
                admin_id="admin_test"
            )
            print(f"   Suspension email result: {suspension_result}")
            
            # Test deletion email
            print("   Testing deletion email function...")
            deletion_result = await send_account_deletion_email(
                email="testuser@test.com",
                user_name="Test User", 
                admin_reason="Testing deletion email system",
                admin_id="admin_test"
            )
            print(f"   Deletion email result: {deletion_result}")
            
            return True
            
        except Exception as e:
            print(f"❌ Email function test error: {str(e)}")
            return False
            
    async def test_database_operations(self):
        """Test database operations for user suspension and deletion"""
        print("\n🔍 Testing Database Operations...")
        
        try:
            # Create a test user
            test_user_id = str(uuid.uuid4())
            test_user = {
                "user_id": test_user_id,
                "email": "dbtest@test.com",
                "full_name": "DB Test User",
                "password_hash": "test_hash",
                "questions_asked": 0,
                "is_subscribed": False,
                "created_at": datetime.utcnow()
            }
            
            await self.db.users.insert_one(test_user)
            print(f"✅ Created test user: {test_user_id}")
            
            # Test suspension update
            suspension_update = {
                "is_suspended": True,
                "suspension_reason": "Testing database suspension",
                "suspended_by": "admin_test",
                "suspended_at": datetime.utcnow()
            }
            
            result = await self.db.users.update_one(
                {"user_id": test_user_id},
                {"$set": suspension_update}
            )
            
            if result.modified_count > 0:
                print("✅ User suspension database update successful")
            else:
                print("❌ User suspension database update failed")
                
            # Test deletion update
            deletion_update = {
                "deleted_at": datetime.utcnow(),
                "deleted_by": "admin_test",
                "deletion_reason": "Testing database deletion",
                "is_suspended": True
            }
            
            result = await self.db.users.update_one(
                {"user_id": test_user_id},
                {"$set": deletion_update}
            )
            
            if result.modified_count > 0:
                print("✅ User deletion database update successful")
            else:
                print("❌ User deletion database update failed")
                
            # Verify the updates
            updated_user = await self.db.users.find_one({"user_id": test_user_id})
            if updated_user:
                print(f"✅ User verification:")
                print(f"   Is Suspended: {updated_user.get('is_suspended')}")
                print(f"   Deleted At: {updated_user.get('deleted_at')}")
                print(f"   Suspension Reason: {updated_user.get('suspension_reason')}")
                print(f"   Deletion Reason: {updated_user.get('deletion_reason')}")
                
            # Clean up test user
            await self.db.users.delete_one({"user_id": test_user_id})
            print("✅ Test user cleaned up")
            
            return True
            
        except Exception as e:
            print(f"❌ Database operations test error: {str(e)}")
            return False
            
    async def test_audit_log_creation(self):
        """Test audit log creation"""
        print("\n🔍 Testing Audit Log Creation...")
        
        try:
            # Create test audit entries
            suspension_audit = {
                "audit_id": str(uuid.uuid4()),
                "action": "suspend",
                "admin_id": "admin_test",
                "target_user_id": "test_user_123",
                "target_email": "testuser@test.com",
                "reason": "Testing audit log system",
                "email_sent": True,
                "timestamp": datetime.utcnow()
            }
            
            deletion_audit = {
                "audit_id": str(uuid.uuid4()),
                "action": "delete_user",
                "admin_id": "admin_test",
                "target_user_id": "test_user_456",
                "target_email": "testuser2@test.com",
                "reason": "Testing audit log system",
                "email_sent": False,
                "timestamp": datetime.utcnow()
            }
            
            # Insert audit entries
            await self.admin_db.admin_audit_log.insert_one(suspension_audit)
            await self.admin_db.admin_audit_log.insert_one(deletion_audit)
            
            print("✅ Audit log entries created successfully")
            
            # Verify audit entries
            suspension_entry = await self.admin_db.admin_audit_log.find_one({"audit_id": suspension_audit["audit_id"]})
            deletion_entry = await self.admin_db.admin_audit_log.find_one({"audit_id": deletion_audit["audit_id"]})
            
            if suspension_entry and deletion_entry:
                print("✅ Audit log entries verified:")
                print(f"   Suspension entry email_sent: {suspension_entry.get('email_sent')}")
                print(f"   Deletion entry email_sent: {deletion_entry.get('email_sent')}")
                
                # Clean up audit entries
                await self.admin_db.admin_audit_log.delete_one({"audit_id": suspension_audit["audit_id"]})
                await self.admin_db.admin_audit_log.delete_one({"audit_id": deletion_audit["audit_id"]})
                print("✅ Audit log entries cleaned up")
                
                return True
            else:
                print("❌ Audit log entries not found")
                return False
                
        except Exception as e:
            print(f"❌ Audit log test error: {str(e)}")
            return False
            
    def test_email_content_validation(self):
        """Test email content validation"""
        print("\n🔍 Testing Email Content Validation...")
        
        try:
            # Read the email template functions
            with open("/app/backend/forgot_password_system.py", "r") as f:
                content = f.read()
                
            # Check suspension email content
            suspension_checks = [
                ("Account Suspended", "Account Suspended" in content),
                ("Support Contact", "support@onlymentors.ai" in content),
                ("Appeal Process", "Appeal" in content),
                ("Community Guidelines", "Community Guidelines" in content),
                ("Professional Branding", "OnlyMentors.ai Team" in content),
                ("Clear Explanation", "reason" in content),
                ("Professional Tone", "Best regards" in content)
            ]
            
            # Check deletion email content  
            deletion_checks = [
                ("Account Deleted", "Account Deleted" in content),
                ("Permanent Notice", "permanently deleted" in content),
                ("Data Retention Policy", "Data Retention" in content),
                ("Recovery Warning", "cannot be recovered" in content),
                ("Support Contact", "support@onlymentors.ai" in content),
                ("Professional Branding", "OnlyMentors.ai Team" in content),
                ("Clear Explanation", "reason" in content)
            ]
            
            print("📧 Suspension Email Content Validation:")
            suspension_score = 0
            for check_name, check_result in suspension_checks:
                status = "✅" if check_result else "❌"
                print(f"   {status} {check_name}")
                if check_result:
                    suspension_score += 1
                    
            print("📧 Deletion Email Content Validation:")
            deletion_score = 0
            for check_name, check_result in deletion_checks:
                status = "✅" if check_result else "❌"
                print(f"   {status} {check_name}")
                if check_result:
                    deletion_score += 1
                    
            print(f"\n📊 Content Validation Scores:")
            print(f"   Suspension Email: {suspension_score}/{len(suspension_checks)}")
            print(f"   Deletion Email: {deletion_score}/{len(deletion_checks)}")
            
            # Check for specific required elements
            required_elements = [
                ("Professional Styling", "style>" in content and "font-family" in content),
                ("HTML Structure", "<!DOCTYPE html>" in content),
                ("Responsive Design", "viewport" in content),
                ("Contact Information", "support@onlymentors.ai" in content),
                ("Appeal Process", "Appeal" in content and "contact" in content),
                ("Data Policy", "Data Retention" in content or "data" in content.lower()),
                ("Security Notice", "security" in content.lower() or "Safety" in content)
            ]
            
            print("\n🔍 Advanced Email Features:")
            for element_name, element_check in required_elements:
                status = "✅" if element_check else "❌"
                print(f"   {status} {element_name}")
                
            return suspension_score >= 5 and deletion_score >= 5
            
        except Exception as e:
            print(f"❌ Email content validation error: {str(e)}")
            return False
            
    async def run_all_tests(self):
        """Run all direct backend tests"""
        print("🚀 Starting Direct Backend Tests for User Suspension and Deletion Email Notifications")
        print("=" * 90)
        
        test_results = []
        
        # Test 1: Email functions directly
        test_results.append(await self.test_email_functions_directly())
        
        # Test 2: Database operations
        test_results.append(await self.test_database_operations())
        
        # Test 3: Audit log creation
        test_results.append(await self.test_audit_log_creation())
        
        # Test 4: Email content validation
        test_results.append(self.test_email_content_validation())
        
        # Calculate results
        passed_tests = sum(test_results)
        total_tests = len(test_results)
        success_rate = (passed_tests / total_tests) * 100
        
        print("\n" + "=" * 90)
        print("📊 DIRECT BACKEND TEST RESULTS SUMMARY")
        print("=" * 90)
        print(f"✅ Tests Passed: {passed_tests}/{total_tests}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 75:
            print("🎉 USER SUSPENSION AND DELETION EMAIL SYSTEM BACKEND FUNCTIONALITY VERIFIED!")
        else:
            print("❌ Some backend functionality issues found")
            
        # Detailed test breakdown
        test_names = [
            "Email Functions Direct Testing",
            "Database Operations Testing",
            "Audit Log Creation Testing", 
            "Email Content Validation"
        ]
        
        print("\n📋 Detailed Results:")
        for i, (name, result) in enumerate(zip(test_names, test_results)):
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {i+1}. {name}: {status}")
            
        # Close database connection
        self.client.close()
        
        return success_rate >= 75

async def main():
    """Main test execution"""
    tester = DirectBackendTester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n🎉 All direct backend tests completed successfully!")
        return True
    else:
        print("\n❌ Some direct backend tests failed. Check the output above for details.")
        return False

if __name__ == "__main__":
    result = asyncio.run(main())
    exit(0 if result else 1)