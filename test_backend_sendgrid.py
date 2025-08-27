#!/usr/bin/env python3
"""
Test Backend SendGrid Implementation
Test the exact same SendGrid code that the backend uses
"""

import os
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

async def test_backend_sendgrid():
    """Test the exact SendGrid implementation from backend"""
    print("🧪 Testing backend SendGrid implementation...")
    
    # Get configuration (same as backend)
    api_key = os.getenv("SENDGRID_API_KEY")
    from_email = os.getenv("FROM_EMAIL", "noreply@onlymentors.ai")
    
    print(f"🔑 API Key: {api_key[:20]}..." if api_key else "❌ No API key")
    print(f"📧 From Email: {from_email}")
    
    if not api_key:
        print("❌ No SendGrid API key found")
        return False
        
    try:
        # Create SendGrid client (exactly like backend)
        sg = sendgrid.SendGridAPIClient(api_key=api_key)
        
        # Test email data
        to_email = "pdorsey@dorseyandassociates.com"
        user_name = "Paul Dorsey"
        admin_reason = "Testing SendGrid email delivery"
        reset_token = "test_token_123"
        
        # Create reset link (exactly like backend)
        frontend_base_url = "https://user-data-restore.preview.emergentagent.com"
        reset_link = f"{frontend_base_url}/reset-password?token={reset_token}&type=user"
        
        # Email subject (exactly like backend)
        subject = "Password Reset Required - OnlyMentors.ai"
        
        # Text content (exactly like backend)
        text_content = f"""
OnlyMentors.ai - Password Reset Required

Hello {user_name},

Your password has been reset by an administrator for the following reason: {admin_reason}

For security reasons, you need to set a new password for your OnlyMentors.ai account.

Click this link to create your new password: {reset_link}

Important:
- This link expires in 1 hour for security
- You will not be able to log in until you set a new password
- Choose a strong password with at least 8 characters

Best regards,
The OnlyMentors.ai Team
        """
        
        # HTML content (exactly like backend)
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Password Reset Required - OnlyMentors.ai</title>
            <style>
                body {{ font-family: 'Arial', sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .header h1 {{ color: white; margin: 0; font-size: 24px; }}
                .content {{ background: white; padding: 30px; border-radius: 0 0 10px 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                .button {{ display: inline-block; background: #f59e0b; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; margin: 20px 0; }}
                .admin-notice {{ background: #fef3c7; border: 1px solid #f59e0b; color: #92400e; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .warning {{ background: #fef2f2; border: 1px solid #fecaca; color: #b91c1c; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🧠 OnlyMentors.ai</h1>
                </div>
                <div class="content">
                    <h2>🔒 Password Reset Required</h2>
                    <p>Hello {user_name},</p>
                    
                    <div class="admin-notice">
                        <strong>📋 Administrative Notice:</strong><br>
                        Your password has been reset by an administrator for the following reason: <strong>{admin_reason}</strong>
                    </div>
                    
                    <p>For security reasons, you need to set a new password for your OnlyMentors.ai account. Click the button below to create your new password:</p>
                    
                    <div style="text-align: center;">
                        <a href="{reset_link}" class="button">Set New Password</a>
                    </div>
                    
                    <p>Or copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; background: #f7fafc; padding: 10px; border-radius: 5px; font-family: monospace;">
                        {reset_link}
                    </p>
                    
                    <div class="warning">
                        <strong>⚠️ Important Security Information:</strong>
                        <ul>
                            <li>This link expires in <strong>1 hour</strong> for security</li>
                            <li>You will not be able to log in until you set a new password</li>
                            <li>Choose a strong password with at least 8 characters</li>
                            <li>Never share this link with anyone</li>
                            <li>If you have questions, contact our support team</li>
                        </ul>
                    </div>
                    
                    <p>Once you set your new password, you'll be able to log in normally to your OnlyMentors.ai account.</p>
                    
                    <p>Best regards,<br>
                    The OnlyMentors.ai Team</p>
                </div>
                <div class="footer">
                    <p>© 2024 OnlyMentors.ai - Connect with the Greatest Minds</p>
                    <p>This email was sent to {to_email}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Create email objects (exactly like backend)
        from_email_obj = Email(from_email)
        to_email_obj = To(to_email)
        plain_content_obj = Content("text/plain", text_content)
        html_content_obj = Content("text/html", html_content)
        
        mail = Mail(from_email_obj, to_email_obj, subject, plain_content_obj)
        mail.add_content(html_content_obj)
        
        # Send email (exactly like backend)
        print("📤 Sending email via SendGrid...")
        response = sg.client.mail.send.post(request_body=mail.get())
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📋 Response Headers: {dict(response.headers)}")
        print(f"📄 Response Body: {response.body}")
        
        if response.status_code in [200, 202]:
            print("✅ SendGrid email sent successfully!")
            return True
        else:
            print(f"❌ SendGrid failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ SendGrid error: {str(e)}")
        return False

if __name__ == "__main__":
    import asyncio
    success = asyncio.run(test_backend_sendgrid())
    if success:
        print("\n🎉 Backend SendGrid implementation is working!")
    else:
        print("\n💥 Backend SendGrid implementation failed!")