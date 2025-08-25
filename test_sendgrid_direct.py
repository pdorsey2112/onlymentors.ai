#!/usr/bin/env python3
"""
Direct SendGrid API Test
Test the SendGrid API key directly
"""

import os
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

def test_sendgrid_direct():
    """Test SendGrid API directly"""
    print("🧪 Testing SendGrid API directly...")
    
    # Get configuration
    api_key = os.getenv("SENDGRID_API_KEY")
    from_email = os.getenv("FROM_EMAIL", "noreply@onlymentors.ai")
    
    print(f"🔑 API Key: {api_key[:20]}..." if api_key else "❌ No API key")
    print(f"📧 From Email: {from_email}")
    
    if not api_key:
        print("❌ No SendGrid API key found")
        return False
        
    try:
        # Create SendGrid client
        sg = sendgrid.SendGridAPIClient(api_key=api_key)
        
        # Create test email
        from_email_obj = Email(from_email)
        to_email = To("pdorsey@dorseyandassociates.com")
        subject = "SendGrid Test - OnlyMentors.ai"
        
        plain_content = Content("text/plain", "This is a test email from OnlyMentors.ai SendGrid integration.")
        html_content = Content("text/html", """
        <html>
        <body>
            <h2>SendGrid Test Email</h2>
            <p>This is a test email from OnlyMentors.ai SendGrid integration.</p>
            <p>If you receive this, SendGrid is working correctly!</p>
        </body>
        </html>
        """)
        
        mail = Mail(from_email_obj, to_email, subject, plain_content)
        mail.add_content(html_content)
        
        # Send email
        print("📤 Sending test email...")
        response = sg.client.mail.send.post(request_body=mail.get())
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📋 Response Headers: {dict(response.headers)}")
        print(f"📄 Response Body: {response.body}")
        
        if response.status_code in [200, 202]:
            print("✅ SendGrid test email sent successfully!")
            return True
        else:
            print(f"❌ SendGrid test failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ SendGrid test error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_sendgrid_direct()
    if success:
        print("\n🎉 SendGrid API is working correctly!")
    else:
        print("\n💥 SendGrid API test failed!")