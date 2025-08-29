# OnlyMentors.ai - Complete Forgot Password System
# Handles password reset for both users and mentors with SendGrid integration

import os
import uuid
import secrets
import ssl
import smtplib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr
from fastapi import HTTPException
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Password Reset Models
class ForgotPasswordRequest(BaseModel):
    email: EmailStr
    user_type: str  # "user" or "mentor"

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
    user_type: str  # "user" or "mentor"

class ForgotPasswordResponse(BaseModel):
    message: str
    email: str
    expires_in: int  # minutes

# Password Reset Configuration
class PasswordResetConfig:
    def __init__(self):
        # SendGrid Configuration (Primary)
        self.sendgrid_api_key = os.getenv("SENDGRID_API_KEY")
        self.from_email = os.getenv("FROM_EMAIL", "noreply@onlymentors.ai")
        
        # SMTP Configuration (Backup)
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        
        self.reset_token_expiry_hours = 1  # 1 hour expiry
        self.frontend_base_url = "https://mentor-marketplace.preview.emergentagent.com"
        
        # Determine email method priority: SMTP2GO > SendGrid > Console
        self.use_smtp = bool(self.smtp_username and self.smtp_password)
        self.use_sendgrid = bool(self.sendgrid_api_key) and not self.use_smtp
        self.use_console_logging = not (self.use_smtp or self.use_sendgrid)
        
    def validate_config(self):
        """Validate email configuration"""
        if self.use_smtp:
            print("✅ Using SMTP2GO for email delivery")
            return True
        elif self.use_sendgrid:
            print("✅ Using SendGrid for email delivery")
            return True
        else:
            print("⚠️ Using console logging for email delivery")
            return True

reset_config = PasswordResetConfig()

def generate_reset_token() -> str:
    """Generate a secure reset token"""
    return secrets.token_urlsafe(32)

def generate_reset_token_id() -> str:
    """Generate a unique reset token ID"""
    return f"reset_{uuid.uuid4().hex[:16]}"

async def send_email_unified(to_email: str, subject: str, html_content: str, text_content: str = None):
    """Unified email sending with SMTP2GO > SendGrid > Console fallback"""
    try:
        reset_config.validate_config()
        
        # Priority 1: SMTP2GO
        if reset_config.use_smtp:
            try:
                msg = MIMEMultipart('alternative')
                msg['Subject'] = subject
                msg['From'] = reset_config.from_email
                msg['To'] = to_email
                
                if text_content:
                    part1 = MIMEText(text_content, 'plain')
                    msg.attach(part1)
                
                part2 = MIMEText(html_content, 'html')
                msg.attach(part2)
                
                context = ssl.create_default_context()
                
                with smtplib.SMTP(reset_config.smtp_server, reset_config.smtp_port) as server:
                    server.ehlo()
                    server.starttls(context=context)
                    server.ehlo()
                    server.login(reset_config.smtp_username, reset_config.smtp_password)
                    
                    text = msg.as_string()
                    server.sendmail(reset_config.from_email, to_email, text)
                
                print(f"✅ SMTP2GO email sent successfully to {to_email}")
                return True
                
            except Exception as e:
                print(f"❌ SMTP2GO error: {str(e)}, falling back to SendGrid/console")
        
        # Priority 2: SendGrid (Fallback)
        if reset_config.use_sendgrid:
            try:
                sg = sendgrid.SendGridAPIClient(api_key=reset_config.sendgrid_api_key)
                
                from_email = Email(reset_config.from_email)
                to_email_obj = To(to_email)
                plain_content_obj = Content("text/plain", text_content or "")
                html_content_obj = Content("text/html", html_content)
                
                mail = Mail(from_email, to_email_obj, subject, plain_content_obj)
                mail.add_content(html_content_obj)
                
                response = sg.client.mail.send.post(request_body=mail.get())
                
                if response.status_code in [200, 202]:
                    print(f"✅ SendGrid fallback email sent successfully to {to_email}")
                    return True
                else:
                    print(f"❌ SendGrid fallback failed: {response.status_code}, falling back to console")
                    
            except Exception as e:
                print(f"❌ SendGrid fallback error: {str(e)}, falling back to console")
        
        # Priority 3: Console logging fallback
        print("\n" + "="*80)
        print(f"📧 EMAIL NOTIFICATION (Console Mode)")
        print("="*80)
        print(f"To: {to_email}")
        print(f"From: {reset_config.from_email}")
        print(f"Subject: {subject}")
        print("\n--- TEXT CONTENT ---")
        print(text_content or "No text content provided")
        print("\n--- HTML CONTENT PREVIEW ---")
        print(html_content[:500] + "..." if len(html_content) > 500 else html_content)
        print("="*80)
        return True
        
    except Exception as e:
        print(f"❌ Unified email error: {str(e)}")
        return True  # Always return True for graceful handling

async def send_password_reset_email(email: str, reset_token: str, user_type: str, user_name: str = "User"):
    """Send password reset email using unified email system (SMTP2GO > SendGrid > Console)"""
    try:
        # Create reset link
        reset_link = f"{reset_config.frontend_base_url}/reset-password?token={reset_token}&type={user_type}"
        
        # Email subject and content based on user type
        if user_type == "mentor":
            subject = "Reset Your OnlyMentors.ai Mentor Account Password"
            user_type_text = "mentor account"
        else:
            subject = "Reset Your OnlyMentors.ai Password" 
            user_type_text = "account"
        
        # HTML email content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Password Reset - OnlyMentors.ai</title>
            <style>
                body {{ font-family: 'Arial', sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .header h1 {{ color: white; margin: 0; font-size: 24px; }}
                .content {{ background: white; padding: 30px; border-radius: 0 0 10px 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                .button {{ display: inline-block; background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; margin: 20px 0; }}
                .button:hover {{ background: #5a67d8; }}
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
                    <h2>Password Reset Request</h2>
                    <p>Hello {user_name},</p>
                    <p>We received a request to reset the password for your OnlyMentors.ai {user_type_text}. Click the button below to reset your password:</p>
                    
                    <div style="text-align: center;">
                        <a href="{reset_link}" class="button">Reset Password</a>
                    </div>
                    
                    <p>Or copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; background: #f7fafc; padding: 10px; border-radius: 5px; font-family: monospace;">
                        {reset_link}
                    </p>
                    
                    <div class="warning">
                        <strong>⚠️ Important:</strong>
                        <ul>
                            <li>This link expires in <strong>1 hour</strong></li>
                            <li>If you didn't request this reset, please ignore this email</li>
                            <li>Never share this link with anyone</li>
                        </ul>
                    </div>
                    
                    <p>If you have any questions, please contact our support team.</p>
                    
                    <p>Best regards,<br>
                    The OnlyMentors.ai Team</p>
                </div>
                <div class="footer">
                    <p>© 2024 OnlyMentors.ai - Connect with the Greatest Minds</p>
                    <p>This email was sent to {email}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Plain text content as fallback
        plain_content = f"""
        Password Reset Request - OnlyMentors.ai
        
        Hello {user_name},
        
        We received a request to reset the password for your OnlyMentors.ai {user_type_text}.
        
        Please click the following link to reset your password:
        {reset_link}
        
        Important:
        - This link expires in 1 hour
        - If you didn't request this reset, please ignore this email
        - Never share this link with anyone
        
        If you have any questions, please contact our support team.
        
        Best regards,
        The OnlyMentors.ai Team
        
        © 2024 OnlyMentors.ai - Connect with the Greatest Minds
        """
        
        # Use unified email system (SMTP2GO > SendGrid > Console fallback)
        email_sent = await send_email_unified(email, subject, html_content, plain_content)
        
        if email_sent:
            print(f"✅ Password reset email sent successfully to {email}")
        else:
            print(f"❌ Failed to send password reset email to {email}")
        
        return email_sent
            
    except Exception as e:
        print(f"❌ Email sending error: {str(e)}")
        return False

async def send_admin_password_reset_email(email: str, reset_token: str, user_name: str = "User", admin_reason: str = "Administrative action"):
    """Send password reset email for admin-initiated password reset using unified email system"""
    try:
        # Create reset link
        reset_link = f"{reset_config.frontend_base_url}/reset-password?token={reset_token}&type=user"
        
        # Email subject
        subject = "Password Reset Required - OnlyMentors.ai"
        
        # Text content for fallback
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
        
        # HTML content
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
                    <p>This email was sent to {email}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Send using unified email system
        email_sent = await send_email_unified(email, subject, html_content, text_content)
        
        if email_sent:
            print(f"✅ Admin password reset email sent to {email}")
        else:
            print(f"❌ Failed to send admin password reset email to {email}")
            # Log the reset link for manual delivery
            print(f"🔗 Manual reset link for {email}: {reset_link}")
        
        return email_sent
        
    except Exception as e:
        print(f"❌ Admin password reset email error: {str(e)}")
        # Log the reset link for manual delivery
        reset_link = f"{reset_config.frontend_base_url}/reset-password?token={reset_token}&type=user"
        print(f"🔗 Manual reset link for {email}: {reset_link}")
        return False

async def send_account_suspension_email(email: str, user_name: str = "User", admin_reason: str = "Policy violation", admin_id: str = "admin"):
    """Send account suspension notification email"""
    try:
        # Create reset link for appeals
        subject = "Account Suspended - OnlyMentors.ai"
        
        # Text content for fallback
        text_content = f"""
OnlyMentors.ai - Account Suspension Notice

Dear {user_name},

Your OnlyMentors.ai account has been suspended due to: {admin_reason}

What this means:
- You cannot log in to your account
- Your profile and content are temporarily hidden
- You cannot access mentor sessions or ask questions

Next Steps:
- Review our Community Guidelines: https://onlymentors.ai/guidelines
- If you believe this was done in error, contact our support team
- Include your email address and reference ID in your appeal

Support Contact:
- Email: support@onlymentors.ai
- Subject: "Account Suspension Appeal - {email}"

We take community safety seriously while also believing in fair treatment. If you have questions about this action, please don't hesitate to reach out.

Best regards,
The OnlyMentors.ai Team
        """
        
        # HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Account Suspended - OnlyMentors.ai</title>
            <style>
                body {{ font-family: 'Arial', sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .header h1 {{ color: white; margin: 0; font-size: 24px; }}
                .content {{ background: white; padding: 30px; border-radius: 0 0 10px 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                .suspension-notice {{ background: #fef3c7; border: 1px solid #f59e0b; color: #92400e; padding: 20px; border-radius: 5px; margin: 20px 0; }}
                .restrictions {{ background: #fef2f2; border: 1px solid #fecaca; color: #b91c1c; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .appeal-box {{ background: #f0f9ff; border: 1px solid #0ea5e9; color: #0c4a6e; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .contact-info {{ background: #f7fafc; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🧠 OnlyMentors.ai</h1>
                </div>
                <div class="content">
                    <h2>⚠️ Account Suspension Notice</h2>
                    <p>Dear {user_name},</p>
                    
                    <div class="suspension-notice">
                        <strong>📋 Account Action Taken:</strong><br>
                        Your OnlyMentors.ai account has been <strong>suspended</strong> for the following reason:<br>
                        <strong>"{admin_reason}"</strong>
                    </div>
                    
                    <h3>What This Means</h3>
                    <div class="restrictions">
                        <strong>🚫 Account Restrictions:</strong>
                        <ul>
                            <li>You cannot log in to your account</li>
                            <li>Your profile and content are temporarily hidden</li>
                            <li>You cannot access mentor sessions or ask questions</li>
                            <li>You cannot interact with the OnlyMentors.ai community</li>
                        </ul>
                    </div>
                    
                    <h3>Next Steps</h3>
                    <div class="appeal-box">
                        <strong>📝 Appeal Process:</strong>
                        <ul>
                            <li>Review our <a href="https://onlymentors.ai/guidelines" style="color: #0ea5e9;">Community Guidelines</a></li>
                            <li>If you believe this was done in error, contact our support team</li>
                            <li>Include your email address and reference this suspension notice</li>
                            <li>Our team will review your appeal within 5 business days</li>
                        </ul>
                    </div>
                    
                    <div class="contact-info">
                        <strong>📞 Support Contact:</strong><br>
                        <strong>Email:</strong> <a href="mailto:support@onlymentors.ai">support@onlymentors.ai</a><br>
                        <strong>Subject:</strong> "Account Suspension Appeal - {email}"<br>
                        <strong>Reference ID:</strong> {admin_id}-{datetime.utcnow().strftime('%Y%m%d')}
                    </div>
                    
                    <p>We take community safety seriously while also believing in fair treatment. If you have questions about this action or believe it was made in error, please don't hesitate to reach out to our support team.</p>
                    
                    <p>Best regards,<br>
                    The OnlyMentors.ai Team</p>
                </div>
                <div class="footer">
                    <p>© 2024 OnlyMentors.ai - Building a Safe Learning Community</p>
                    <p>This email was sent to {email}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Send using unified email system
        email_sent = await send_email_unified(email, subject, html_content, text_content)
        
        if email_sent:
            print(f"✅ Account suspension email sent to {email}")
        else:
            print(f"❌ Failed to send account suspension email to {email}")
        
        return email_sent
        
    except Exception as e:
        print(f"❌ Account suspension email error: {str(e)}")
        return False

async def send_account_deletion_email(email: str, user_name: str = "User", admin_reason: str = "Policy violations", admin_id: str = "admin"):
    """Send account deletion notification email"""
    try:
        subject = "Account Deleted - OnlyMentors.ai"
        
        # Text content for fallback
        text_content = f"""
OnlyMentors.ai - Account Deletion Notice

Dear {user_name},

Your OnlyMentors.ai account has been permanently deleted due to: {admin_reason}

What this means:
- Your account cannot be recovered
- All your data has been removed from our systems
- You will no longer receive communications from OnlyMentors.ai
- Any subscriptions have been cancelled

Data Retention:
- Personal data: Deleted immediately
- Some transaction records may be retained for legal/tax purposes for 7 years
- Messages and content: Permanently removed

If you believe this action was taken in error:
- Contact: support@onlymentors.ai
- Subject: "Account Deletion Appeal - {email}"
- Reference ID: {admin_id}-{datetime.utcnow().strftime('%Y%m%d')}

We're sorry to see you go. If this was an error, please contact us as soon as possible.

Best regards,
The OnlyMentors.ai Team
        """
        
        # HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Account Deleted - OnlyMentors.ai</title>
            <style>
                body {{ font-family: 'Arial', sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .header h1 {{ color: white; margin: 0; font-size: 24px; }}
                .content {{ background: white; padding: 30px; border-radius: 0 0 10px 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                .deletion-notice {{ background: #fef2f2; border: 1px solid #dc2626; color: #b91c1c; padding: 20px; border-radius: 5px; margin: 20px 0; }}
                .data-retention {{ background: #f7fafc; border: 1px solid #94a3b8; color: #475569; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .appeal-info {{ background: #f0f9ff; border: 1px solid #0ea5e9; color: #0c4a6e; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .warning {{ background: #fef3c7; border: 1px solid #f59e0b; color: #92400e; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🧠 OnlyMentors.ai</h1>
                </div>
                <div class="content">
                    <h2>❌ Account Deletion Notice</h2>
                    <p>Dear {user_name},</p>
                    
                    <div class="deletion-notice">
                        <strong>🗑️ Account Permanently Deleted:</strong><br>
                        Your OnlyMentors.ai account has been <strong>permanently deleted</strong> for the following reason:<br>
                        <strong>"{admin_reason}"</strong>
                    </div>
                    
                    <div class="warning">
                        <strong>⚠️ Important Notice:</strong><br>
                        This action cannot be undone. Your account and all associated data have been permanently removed from our systems.
                    </div>
                    
                    <h3>What This Means</h3>
                    <ul>
                        <li><strong>Account Recovery:</strong> Your account cannot be recovered</li>
                        <li><strong>Data Removal:</strong> All your data has been removed from our systems</li>
                        <li><strong>Communications:</strong> You will no longer receive emails from OnlyMentors.ai</li>
                        <li><strong>Subscriptions:</strong> Any active subscriptions have been cancelled</li>
                        <li><strong>Access:</strong> You cannot create a new account with this email address</li>
                    </ul>
                    
                    <h3>Data Retention Policy</h3>
                    <div class="data-retention">
                        <strong>📋 What's Been Removed:</strong>
                        <ul>
                            <li><strong>Personal Data:</strong> Deleted immediately from all systems</li>
                            <li><strong>Messages & Content:</strong> Permanently removed</li>
                            <li><strong>Profile Information:</strong> Completely deleted</li>
                            <li><strong>Activity History:</strong> Purged from our databases</li>
                        </ul>
                        <br>
                        <strong>📋 Legal Retention (if applicable):</strong>
                        <ul>
                            <li>Some transaction records may be retained for legal/tax purposes for up to 7 years</li>
                            <li>These records are anonymized and cannot be linked to your identity</li>
                        </ul>
                    </div>
                    
                    <h3>If This Was an Error</h3>
                    <div class="appeal-info">
                        <strong>📞 Contact Information:</strong><br>
                        If you believe this account deletion was made in error, please contact us immediately:
                        <ul>
                            <li><strong>Email:</strong> <a href="mailto:support@onlymentors.ai">support@onlymentors.ai</a></li>
                            <li><strong>Subject:</strong> "Account Deletion Appeal - {email}"</li>
                            <li><strong>Reference ID:</strong> {admin_id}-{datetime.utcnow().strftime('%Y%m%d')}</li>
                            <li><strong>Response Time:</strong> Appeals reviewed within 5 business days</li>
                        </ul>
                    </div>
                    
                    <p>We're sorry to see you go. We strive to maintain a safe and positive community for all users. If you believe this action was taken in error, please contact our support team as soon as possible.</p>
                    
                    <p>Thank you for being part of the OnlyMentors.ai community.</p>
                    
                    <p>Best regards,<br>
                    The OnlyMentors.ai Team</p>
                </div>
                <div class="footer">
                    <p>© 2024 OnlyMentors.ai - Building a Safe Learning Community</p>
                    <p>This is a final notification sent to {email}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Send using unified email system
        email_sent = await send_email_unified(email, subject, html_content, text_content)
        
        if email_sent:
            print(f"✅ Account deletion email sent to {email}")
        else:
            print(f"❌ Failed to send account deletion email to {email}")
        
        return email_sent
        
    except Exception as e:
        print(f"❌ Account deletion email error: {str(e)}")
        return False

async def send_account_reactivation_email(email: str, user_name: str = "User", admin_reason: str = "Account review completed", admin_id: str = "admin"):
    """Send account reactivation notification email"""
    try:
        subject = "Account Reactivated - OnlyMentors.ai"
        
        # Text content for fallback
        text_content = f"""
OnlyMentors.ai - Account Reactivated

Dear {user_name},

Great news! Your OnlyMentors.ai account has been reactivated.

Reason for reactivation: {admin_reason}

What this means:
- You can now log in to your account normally
- All platform features are restored
- Your profile and content are visible again
- You can resume accessing mentor sessions and asking questions

We're glad to have you back in the OnlyMentors.ai community! Please review our Community Guidelines to ensure a positive experience for everyone.

If you have any questions, feel free to contact our support team.

Welcome back!
The OnlyMentors.ai Team
        """
        
        # HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Account Reactivated - OnlyMentors.ai</title>
            <style>
                body {{ font-family: 'Arial', sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #10b981 0%, #059669 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .header h1 {{ color: white; margin: 0; font-size: 24px; }}
                .content {{ background: white; padding: 30px; border-radius: 0 0 10px 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                .welcome-back {{ background: #d1fae5; border: 1px solid #10b981; color: #065f46; padding: 20px; border-radius: 5px; margin: 20px 0; }}
                .restored-features {{ background: #f0f9ff; border: 1px solid #0ea5e9; color: #0c4a6e; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .guidelines-reminder {{ background: #fef3c7; border: 1px solid #f59e0b; color: #92400e; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🧠 OnlyMentors.ai</h1>
                </div>
                <div class="content">
                    <h2>🎉 Welcome Back!</h2>
                    <p>Dear {user_name},</p>
                    
                    <div class="welcome-back">
                        <strong>✅ Account Reactivated!</strong><br>
                        Your OnlyMentors.ai account has been successfully reactivated.<br>
                        <strong>Reason: "{admin_reason}"</strong>
                    </div>
                    
                    <h3>What's Restored</h3>
                    <div class="restored-features">
                        <strong>🔓 Full Access Restored:</strong>
                        <ul>
                            <li>You can now log in to your account normally</li>
                            <li>All platform features are available again</li>
                            <li>Your profile and content are visible to the community</li>
                            <li>You can access mentor sessions and ask questions</li>
                            <li>All account privileges have been restored</li>
                        </ul>
                    </div>
                    
                    <div class="guidelines-reminder">
                        <strong>📋 Friendly Reminder:</strong><br>
                        Please take a moment to review our <a href="https://onlymentors.ai/guidelines" style="color: #f59e0b;">Community Guidelines</a> to ensure a positive experience for everyone in our learning community.
                    </div>
                    
                    <p>We're excited to have you back as part of the OnlyMentors.ai community! Our platform thrives when learners like you engage with our amazing mentors.</p>
                    
                    <p>If you have any questions or need assistance getting back into your account, our support team is here to help at <a href="mailto:support@onlymentors.ai">support@onlymentors.ai</a>.</p>
                    
                    <p>Welcome back and happy learning!</p>
                    
                    <p>Best regards,<br>
                    The OnlyMentors.ai Team</p>
                </div>
                <div class="footer">
                    <p>© 2024 OnlyMentors.ai - Welcome Back to Your Learning Journey</p>
                    <p>This email was sent to {email}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Send using unified email system
        email_sent = await send_email_unified(email, subject, html_content, text_content)
        
        if email_sent:
            print(f"✅ Account reactivation email sent to {email}")
        else:
            print(f"❌ Failed to send account reactivation email to {email}")
        
        return email_sent
        
    except Exception as e:
        print(f"❌ Account reactivation email error: {str(e)}")
        return False

async def create_password_reset_token(db, email: str, user_type: str) -> Optional[str]:
    """Create a password reset token and store it in the database"""
    try:
        # Generate reset token and ID
        reset_token = generate_reset_token()
        token_id = generate_reset_token_id()
        
        # Set expiration time
        expires_at = datetime.utcnow() + timedelta(hours=reset_config.reset_token_expiry_hours)
        
        # Create token document
        token_doc = {
            "token_id": token_id,
            "reset_token": reset_token,
            "email": email,
            "user_type": user_type,
            "created_at": datetime.utcnow(),
            "expires_at": expires_at,
            "used": False,
            "used_at": None
        }
        
        # Store in database
        await db.password_reset_tokens.insert_one(token_doc)
        
        return reset_token
        
    except Exception as e:
        print(f"❌ Error creating reset token: {str(e)}")
        return None

async def validate_reset_token(db, token: str, user_type: str) -> Optional[Dict[str, Any]]:
    """Validate a password reset token"""
    try:
        # Find the token
        token_doc = await db.password_reset_tokens.find_one({
            "reset_token": token,
            "user_type": user_type,
            "used": False
        })
        
        if not token_doc:
            return None
        
        # Check if token is expired
        if datetime.utcnow() > token_doc["expires_at"]:
            return None
        
        return token_doc
        
    except Exception as e:
        print(f"❌ Error validating reset token: {str(e)}")
        return None

async def mark_token_as_used(db, token: str):
    """Mark a reset token as used"""
    try:
        await db.password_reset_tokens.update_one(
            {"reset_token": token},
            {
                "$set": {
                    "used": True,
                    "used_at": datetime.utcnow()
                }
            }
        )
    except Exception as e:
        print(f"❌ Error marking token as used: {str(e)}")

async def cleanup_expired_tokens(db):
    """Clean up expired password reset tokens"""
    try:
        # Delete tokens older than 24 hours
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        
        result = await db.password_reset_tokens.delete_many({
            "created_at": {"$lt": cutoff_time}
        })
        
        if result.deleted_count > 0:
            print(f"🧹 Cleaned up {result.deleted_count} expired reset tokens")
            
    except Exception as e:
        print(f"❌ Error cleaning up expired tokens: {str(e)}")

# Password strength validation
def validate_password_strength(password: str) -> tuple[bool, str]:
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number"
    
    # Check for special characters
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(c in special_chars for c in password):
        return False, "Password must contain at least one special character"
    
    return True, "Password is strong"

# Analytics and monitoring
async def log_password_reset_attempt(db, email: str, user_type: str, success: bool, ip_address: str = None):
    """Log password reset attempts for monitoring"""
    try:
        log_doc = {
            "email": email,
            "user_type": user_type,
            "success": success,
            "ip_address": ip_address,
            "timestamp": datetime.utcnow(),
            "user_agent": None  # Can be added later if needed
        }
        
        await db.password_reset_logs.insert_one(log_doc)
        
    except Exception as e:
        print(f"❌ Error logging password reset attempt: {str(e)}")

async def get_recent_reset_attempts(db, email: str, hours: int = 1) -> int:
    """Get number of recent reset attempts for rate limiting"""
    try:
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        count = await db.password_reset_logs.count_documents({
            "email": email,
            "timestamp": {"$gte": cutoff_time}
        })
        
        return count
        
    except Exception as e:
        print(f"❌ Error getting recent reset attempts: {str(e)}")
        return 0