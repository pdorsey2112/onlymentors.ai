#!/usr/bin/env python3
"""
Test the email system directly to diagnose the issue
"""

import asyncio
import sys
import os
sys.path.append('/app/backend')

from forgot_password_system import send_admin_password_reset_email, reset_config

async def test_email_system():
    """Test the email system directly"""
    print("🧪 Testing Email System Configuration")
    print("=" * 50)
    
    try:
        # Test configuration validation
        print("📋 Validating SendGrid configuration...")
        reset_config.validate_config()
        print("✅ SendGrid configuration is valid")
        
        # Test email sending
        print("\n📧 Testing email sending...")
        test_email = "test@example.com"
        test_token = "test_token_12345"
        test_name = "Test User"
        test_reason = "Testing email system"
        
        result = await send_admin_password_reset_email(
            test_email, test_token, test_name, test_reason
        )
        
        if result:
            print("✅ Email sending function executed successfully")
        else:
            print("❌ Email sending function failed")
            
        return result
        
    except Exception as e:
        print(f"❌ Email system test failed: {str(e)}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_email_system())
    if result:
        print("\n🎉 Email system is working correctly")
    else:
        print("\n⚠️  Email system has issues")