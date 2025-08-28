#!/usr/bin/env python3
"""
Detailed Email System Test
Test the actual forgot password email sending process to identify the 401 error
"""

import asyncio
import sys
import os
sys.path.append('/app/backend')

from dotenv import load_dotenv
load_dotenv('/app/backend/.env')

# Import the actual forgot password system
from forgot_password_system import send_password_reset_email, send_email_unified, reset_config

async def test_email_sending_methods():
    """Test different email sending methods"""
    print("🔍 Testing Email Sending Methods")
    print("=" * 50)
    
    test_email = "test@example.com"
    test_token = "test_token_12345"
    
    # Test 1: Direct SMTP2GO via unified email system
    print(f"\n📧 Test 1: Unified Email System (SMTP2GO Primary)")
    try:
        result = await send_email_unified(
            test_email,
            "Test Subject",
            "<h1>Test HTML Content</h1>",
            "Test plain text content"
        )
        print(f"✅ Unified email system result: {result}")
    except Exception as e:
        print(f"❌ Unified email system error: {e}")
    
    # Test 2: Original SendGrid method
    print(f"\n📧 Test 2: Original SendGrid Method")
    try:
        result = await send_password_reset_email(
            test_email,
            test_token,
            "mentor",
            "Test User"
        )
        print(f"✅ SendGrid method result: {result}")
    except Exception as e:
        print(f"❌ SendGrid method error: {e}")
    
    # Test 3: Check configuration
    print(f"\n🔧 Test 3: Configuration Analysis")
    print(f"   Use SMTP: {reset_config.use_smtp}")
    print(f"   Use SendGrid: {reset_config.use_sendgrid}")
    print(f"   Use Console: {reset_config.use_console_logging}")
    print(f"   SMTP Username: {reset_config.smtp_username}")
    print(f"   SMTP Server: {reset_config.smtp_server}")
    print(f"   SMTP Port: {reset_config.smtp_port}")

async def test_forgot_password_flow():
    """Test the complete forgot password flow"""
    print(f"\n🔍 Testing Complete Forgot Password Flow")
    print("=" * 50)
    
    # Import database and other components
    from motor.motor_asyncio import AsyncIOMotorClient
    from forgot_password_system import (
        create_password_reset_token, 
        get_recent_reset_attempts,
        log_password_reset_attempt
    )
    
    # Connect to database
    MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.onlymentors_db
    
    test_email = "pdorsey@dorseyandassociates.com"
    
    print(f"📧 Testing with mentor email: {test_email}")
    
    # Test 1: Check recent attempts
    print(f"\n🔍 Step 1: Check Recent Reset Attempts")
    try:
        recent_attempts = await get_recent_reset_attempts(db, test_email, hours=1)
        print(f"   Recent attempts in last hour: {recent_attempts}")
        
        if recent_attempts >= 3:
            print(f"   ⚠️  Rate limit reached - this explains the 429 errors")
        else:
            print(f"   ✅ Under rate limit")
    except Exception as e:
        print(f"   ❌ Error checking attempts: {e}")
    
    # Test 2: Check if mentor exists
    print(f"\n🔍 Step 2: Check if Mentor Exists in Database")
    try:
        mentor_doc = await db.creators.find_one({"email": test_email})
        if mentor_doc:
            print(f"   ✅ Mentor found in creators collection")
            print(f"   Name: {mentor_doc.get('full_name', 'N/A')}")
            print(f"   Status: {mentor_doc.get('status', 'N/A')}")
        else:
            print(f"   ❌ Mentor not found in creators collection")
    except Exception as e:
        print(f"   ❌ Error checking mentor: {e}")
    
    # Test 3: Create reset token
    print(f"\n🔍 Step 3: Create Reset Token")
    try:
        reset_token = await create_password_reset_token(db, test_email, "mentor")
        if reset_token:
            print(f"   ✅ Reset token created: {reset_token[:20]}...")
        else:
            print(f"   ❌ Failed to create reset token")
    except Exception as e:
        print(f"   ❌ Error creating token: {e}")
    
    # Test 4: Send email
    print(f"\n🔍 Step 4: Send Password Reset Email")
    try:
        email_sent = await send_password_reset_email(
            test_email, 
            reset_token if 'reset_token' in locals() else "test_token",
            "mentor",
            "Test Mentor"
        )
        print(f"   Email sent result: {email_sent}")
    except Exception as e:
        print(f"   ❌ Error sending email: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Main test function"""
    print("🚀 OnlyMentors.ai Detailed Email System Testing")
    print("🎯 Goal: Identify the exact source of the 401 Unauthorized error")
    print("=" * 80)
    
    # Test email sending methods
    await test_email_sending_methods()
    
    # Test complete forgot password flow
    await test_forgot_password_flow()
    
    print(f"\n{'='*80}")
    print("📊 ANALYSIS COMPLETE")
    print(f"{'='*80}")
    
    print(f"🔍 Key Findings:")
    print(f"   • SMTP2GO credentials are working (tested separately)")
    print(f"   • The 401 error occurs during the forgot password process")
    print(f"   • Rate limiting may be preventing proper testing")
    print(f"   • Need to check the exact email sending implementation")

if __name__ == "__main__":
    asyncio.run(main())