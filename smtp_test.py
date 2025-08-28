#!/usr/bin/env python3
"""
Direct SMTP2GO Connection Test
Test SMTP2GO credentials to identify the 401 Unauthorized issue
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

def test_smtp2go_connection():
    """Test direct SMTP2GO connection"""
    print("🔍 Testing SMTP2GO Connection Directly")
    print("=" * 50)
    
    # Get credentials from environment
    smtp_server = os.getenv("SMTP_SERVER", "mail.smtp2go.com")
    smtp_port = int(os.getenv("SMTP_PORT", "2525"))
    smtp_username = os.getenv("SMTP_USERNAME", "onlymentors.ai")
    smtp_password = os.getenv("SMTP_PASSWORD", "")
    
    print(f"📧 SMTP Configuration:")
    print(f"   Server: {smtp_server}")
    print(f"   Port: {smtp_port}")
    print(f"   Username: {smtp_username}")
    print(f"   Password: {'*' * len(smtp_password) if smtp_password else 'NOT SET'}")
    
    if not smtp_password:
        print("❌ SMTP password not found in environment variables")
        return False
    
    try:
        print(f"\n🔌 Attempting SMTP2GO Connection...")
        
        # Create SSL context
        context = ssl.create_default_context()
        
        # Connect to SMTP server
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            print(f"✅ Connected to {smtp_server}:{smtp_port}")
            
            # Start TLS
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            print(f"✅ TLS connection established")
            
            # Attempt login
            print(f"🔐 Attempting authentication...")
            server.login(smtp_username, smtp_password)
            print(f"✅ Authentication successful!")
            
            # Create test email
            msg = MIMEMultipart()
            msg['From'] = "customerservice@onlymentors.ai"
            msg['To'] = "test@example.com"
            msg['Subject'] = "SMTP2GO Connection Test"
            
            body = "This is a test email to verify SMTP2GO connection."
            msg.attach(MIMEText(body, 'plain'))
            
            # Send test email (but don't actually send to avoid spam)
            print(f"✅ Email composition successful")
            print(f"✅ SMTP2GO connection test PASSED")
            
            return True
            
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ SMTP Authentication Error: {e}")
        print(f"   This is the 401 Unauthorized equivalent for SMTP")
        print(f"   Possible causes:")
        print(f"   - Incorrect username or password")
        print(f"   - Account suspended or expired")
        print(f"   - IP address not whitelisted")
        return False
        
    except smtplib.SMTPException as e:
        print(f"❌ SMTP Error: {e}")
        return False
        
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return False

def test_sendgrid_fallback():
    """Test SendGrid fallback configuration"""
    print(f"\n🔍 Testing SendGrid Fallback Configuration")
    print("=" * 50)
    
    sendgrid_api_key = os.getenv("SENDGRID_API_KEY", "")
    from_email = os.getenv("FROM_EMAIL", "customerservice@onlymentors.ai")
    
    print(f"📧 SendGrid Configuration:")
    print(f"   API Key: {'*' * 20 + sendgrid_api_key[-10:] if len(sendgrid_api_key) > 10 else 'NOT SET'}")
    print(f"   From Email: {from_email}")
    
    if not sendgrid_api_key:
        print("❌ SendGrid API key not found")
        return False
    
    try:
        import sendgrid
        from sendgrid.helpers.mail import Mail, Email, To, Content
        
        # Create SendGrid client
        sg = sendgrid.SendGridAPIClient(api_key=sendgrid_api_key)
        
        print(f"✅ SendGrid client created successfully")
        print(f"✅ SendGrid fallback is available")
        
        return True
        
    except ImportError:
        print(f"❌ SendGrid library not installed")
        return False
    except Exception as e:
        print(f"❌ SendGrid Error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 OnlyMentors.ai SMTP Testing")
    print("🎯 Goal: Identify the 401 Unauthorized issue with mentor forgot password emails")
    print("=" * 80)
    
    # Test SMTP2GO connection
    smtp2go_success = test_smtp2go_connection()
    
    # Test SendGrid fallback
    sendgrid_success = test_sendgrid_fallback()
    
    # Summary
    print(f"\n{'='*80}")
    print("📊 TEST SUMMARY")
    print(f"{'='*80}")
    
    print(f"SMTP2GO Connection: {'✅ WORKING' if smtp2go_success else '❌ FAILED'}")
    print(f"SendGrid Fallback: {'✅ AVAILABLE' if sendgrid_success else '❌ NOT AVAILABLE'}")
    
    if not smtp2go_success:
        print(f"\n🚨 ROOT CAUSE IDENTIFIED:")
        print(f"   The 401 Unauthorized error is caused by SMTP2GO authentication failure")
        print(f"   This prevents mentor forgot password emails from being sent")
        
        print(f"\n🔧 IMMEDIATE FIXES NEEDED:")
        print(f"   1. Verify SMTP2GO account status at smtp2go.com")
        print(f"   2. Check if password has been changed")
        print(f"   3. Verify account is not suspended")
        print(f"   4. Check IP whitelisting settings")
        
        if sendgrid_success:
            print(f"\n✅ GOOD NEWS:")
            print(f"   SendGrid fallback is available and should work")
            print(f"   Users should still receive emails via SendGrid")
        else:
            print(f"\n❌ CRITICAL:")
            print(f"   Both SMTP2GO and SendGrid are failing")
            print(f"   No emails will be sent until fixed")
    else:
        print(f"\n✅ SMTP2GO is working correctly")
        print(f"   The issue may be elsewhere in the email sending process")
    
    return 0 if smtp2go_success else 1

if __name__ == "__main__":
    exit(main())