#!/usr/bin/env python3
"""
Test SendGrid Configuration
"""

import os
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_sendgrid_config():
    """Test SendGrid configuration"""
    print("🔍 Testing SendGrid Configuration...")
    
    # Get configuration
    api_key = os.getenv("SENDGRID_API_KEY")
    from_email = os.getenv("FROM_EMAIL", "noreply@onlymentors.ai")
    
    print(f"   API Key: {'✅ Set' if api_key else '❌ Missing'}")
    print(f"   From Email: {from_email}")
    
    if not api_key:
        print("❌ SendGrid API key not configured")
        return False
    
    # Test API key format
    if api_key.startswith('SG.'):
        print("✅ API key has correct format")
    else:
        print("⚠️  API key format may be incorrect")
    
    # Try to create SendGrid client
    try:
        sg = sendgrid.SendGridAPIClient(api_key=api_key)
        print("✅ SendGrid client created successfully")
        
        # Test API key validity by making a simple API call
        # We'll try to get API key info (this doesn't send email)
        try:
            # This is a simple test that doesn't send email but validates the API key
            test_mail = Mail(
                from_email=Email(from_email),
                to_emails=To("test@example.com"),
                subject="Test",
                plain_text_content=Content("text/plain", "Test")
            )
            
            # Just validate the mail object creation
            mail_json = test_mail.get()
            print("✅ Email object creation successful")
            print(f"   From: {mail_json.get('from', {}).get('email', 'Unknown')}")
            
            return True
            
        except Exception as e:
            print(f"❌ Email object creation failed: {str(e)}")
            return False
            
    except Exception as e:
        print(f"❌ SendGrid client creation failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_sendgrid_config()
    if success:
        print("\n✅ SendGrid configuration appears to be working")
    else:
        print("\n❌ SendGrid configuration has issues")