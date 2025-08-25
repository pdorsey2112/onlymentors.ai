#!/usr/bin/env python3
"""
Direct SMTP2GO Connection Test
Tests the SMTP2GO credentials and connection directly.
"""

import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

def test_smtp2go_direct():
    """Test SMTP2GO connection directly with provided credentials"""
    
    # SMTP2GO Configuration from review request
    smtp_server = "mail.smtp2go.com"
    smtp_port = 587
    smtp_username = "pdorsey@dorseyandassociates.com"
    smtp_password = "Mfpatd2117!"
    from_email = "customerservice@onlymentors.ai"
    to_email = "pdorsey@dorseyandassociates.com"
    
    print("🧪 Direct SMTP2GO Connection Test")
    print("="*50)
    print(f"Server: {smtp_server}:{smtp_port}")
    print(f"Username: {smtp_username}")
    print(f"From: {from_email}")
    print(f"To: {to_email}")
    print("="*50)
    
    try:
        # Create test email
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "SMTP2GO Test - OnlyMentors.ai"
        msg['From'] = from_email
        msg['To'] = to_email
        
        text_content = f"""
SMTP2GO Test Email - OnlyMentors.ai

This is a test email to verify SMTP2GO configuration.

Test Details:
- Server: {smtp_server}:{smtp_port}
- Username: {smtp_username}
- From Email: {from_email}
- Test Time: {datetime.utcnow().isoformat()}

If you receive this email, SMTP2GO is working correctly!

Best regards,
OnlyMentors.ai Testing System
        """
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>SMTP2GO Test - OnlyMentors.ai</title>
        </head>
        <body>
            <h2>🧪 SMTP2GO Test Email - OnlyMentors.ai</h2>
            <p>This is a test email to verify SMTP2GO configuration.</p>
            
            <h3>Test Details:</h3>
            <ul>
                <li><strong>Server:</strong> {smtp_server}:{smtp_port}</li>
                <li><strong>Username:</strong> {smtp_username}</li>
                <li><strong>From Email:</strong> {from_email}</li>
                <li><strong>Test Time:</strong> {datetime.utcnow().isoformat()}</li>
            </ul>
            
            <p><strong>✅ If you receive this email, SMTP2GO is working correctly!</strong></p>
            
            <p>Best regards,<br>
            OnlyMentors.ai Testing System</p>
        </body>
        </html>
        """
        
        part1 = MIMEText(text_content, 'plain')
        part2 = MIMEText(html_content, 'html')
        msg.attach(part1)
        msg.attach(part2)
        
        # Create SSL context
        context = ssl.create_default_context()
        
        print("🔌 Connecting to SMTP2GO server...")
        
        # Connect and send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            print("✅ Connected to SMTP server")
            
            print("🤝 Starting EHLO...")
            server.ehlo()
            print("✅ EHLO successful")
            
            print("🔒 Starting TLS...")
            server.starttls(context=context)
            print("✅ TLS started")
            
            print("🤝 EHLO after TLS...")
            server.ehlo()
            print("✅ EHLO after TLS successful")
            
            print("🔐 Authenticating...")
            server.login(smtp_username, smtp_password)
            print("✅ Authentication successful!")
            
            print("📧 Sending email...")
            text = msg.as_string()
            server.sendmail(from_email, to_email, text)
            print("✅ Email sent successfully!")
        
        print("\n🎉 SMTP2GO Direct Test SUCCESSFUL!")
        print(f"✅ Email sent from {from_email} to {to_email}")
        print("✅ SMTP2GO credentials are working correctly")
        print("✅ Server connection and authentication successful")
        
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"\n❌ SMTP Authentication Error: {e}")
        print("❌ SMTP2GO credentials may be incorrect")
        return False
        
    except smtplib.SMTPConnectError as e:
        print(f"\n❌ SMTP Connection Error: {e}")
        print("❌ Cannot connect to SMTP2GO server")
        return False
        
    except smtplib.SMTPException as e:
        print(f"\n❌ SMTP Error: {e}")
        print("❌ General SMTP error occurred")
        return False
        
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        print("❌ An unexpected error occurred")
        return False

if __name__ == "__main__":
    success = test_smtp2go_direct()
    exit(0 if success else 1)