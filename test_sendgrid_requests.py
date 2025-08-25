#!/usr/bin/env python3
"""
Test SendGrid with requests library instead of sendgrid library
"""

import os
import json
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

def test_sendgrid_with_requests():
    """Test SendGrid using requests library directly"""
    print("🧪 Testing SendGrid with requests library...")
    
    api_key = os.getenv("SENDGRID_API_KEY")
    from_email = os.getenv("FROM_EMAIL", "noreply@onlymentors.ai")
    
    if not api_key:
        print("❌ No SendGrid API key found")
        return False
        
    # SendGrid API endpoint
    url = "https://api.sendgrid.com/v3/mail/send"
    
    # Headers
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Email data
    email_data = {
        "personalizations": [
            {
                "to": [
                    {
                        "email": "pdorsey@dorseyandassociates.com",
                        "name": "Paul Dorsey"
                    }
                ],
                "subject": "SendGrid Test via Requests - OnlyMentors.ai"
            }
        ],
        "from": {
            "email": from_email,
            "name": "OnlyMentors.ai"
        },
        "content": [
            {
                "type": "text/plain",
                "value": "This is a test email sent via SendGrid using the requests library directly."
            },
            {
                "type": "text/html",
                "value": "<html><body><h2>SendGrid Test</h2><p>This is a test email sent via SendGrid using the requests library directly.</p><p>If you receive this, the requests approach is working!</p></body></html>"
            }
        ]
    }
    
    try:
        print("📤 Sending email via SendGrid API...")
        response = requests.post(url, headers=headers, json=email_data)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Response Headers: {dict(response.headers)}")
        print(f"📄 Response Text: {response.text}")
        
        if response.status_code == 202:
            print("✅ SendGrid email sent successfully via requests!")
            return True
        else:
            print(f"❌ SendGrid failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending email: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_sendgrid_with_requests()
    if success:
        print("\n🎉 SendGrid works with requests library!")
    else:
        print("\n💥 SendGrid failed with requests library!")