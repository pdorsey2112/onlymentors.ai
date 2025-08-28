"""
OnlyMentors.ai SMS System using Twilio
Provides SMS notifications and 2FA functionality
"""

import os
import re
from typing import Optional, Dict, Any
from twilio.rest import Client
from twilio.base.exceptions import TwilioException
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SMSService:
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.verify_service_sid = os.getenv("TWILIO_VERIFY_SERVICE_SID")
        
        if not self.account_sid or not self.auth_token:
            raise ValueError("Twilio credentials not found in environment variables")
        
        self.client = Client(self.account_sid, self.auth_token)
        
        # Initialize verify service if not exists
        if not self.verify_service_sid:
            self._create_verify_service()
    
    def _create_verify_service(self):
        """Create a Twilio Verify service for 2FA"""
        try:
            service = self.client.verify.services.create(
                friendly_name="OnlyMentors.ai 2FA",
                code_length=6,
                lookup_enabled=True,
                psd2_enabled=False,
                skip_sms_to_landlines=True,
                dtmf_input_required=False,
                tts_name="OnlyMentors.ai"
            )
            
            # Update the environment variable (you'll need to update .env file manually)
            self.verify_service_sid = service.sid
            logger.info(f"✅ Created Twilio Verify service: {service.sid}")
            print(f"🔧 IMPORTANT: Add this to your .env file:")
            print(f"TWILIO_VERIFY_SERVICE_SID={service.sid}")
            
        except TwilioException as e:
            logger.error(f"Failed to create Verify service: {str(e)}")
            raise
    
    def format_phone_number(self, phone: str) -> str:
        """Format phone number to E.164 format"""
        # Remove all non-digit characters
        digits = re.sub(r'\D', '', phone)
        
        # If starts with 1 and has 11 digits (US/Canada)
        if len(digits) == 11 and digits.startswith('1'):
            return f"+{digits}"
        
        # If has 10 digits, assume US/Canada
        elif len(digits) == 10:
            return f"+1{digits}"
        
        # If already has country code
        elif len(digits) > 10:
            return f"+{digits}"
        
        else:
            raise ValueError(f"Invalid phone number format: {phone}")
    
    def validate_phone_number(self, phone: str) -> bool:
        """Validate phone number using Twilio Lookup API"""
        try:
            formatted_phone = self.format_phone_number(phone)
            lookup = self.client.lookups.phone_numbers(formatted_phone).fetch()
            return lookup.phone_number is not None
        except Exception as e:
            logger.warning(f"Phone validation failed: {str(e)}")
            return False
    
    async def send_notification_sms(self, phone: str, message: str) -> Dict[str, Any]:
        """Send a notification SMS"""
        try:
            formatted_phone = self.format_phone_number(phone)
            
            # Validate phone number first
            if not self.validate_phone_number(phone):
                return {
                    "success": False,
                    "error": "Invalid phone number"
                }
            
            message_instance = self.client.messages.create(
                body=message,
                from_='+18445551234',  # You'll need a Twilio phone number for this
                to=formatted_phone
            )
            
            logger.info(f"✅ SMS sent to {formatted_phone}: {message_instance.sid}")
            
            return {
                "success": True,
                "message_sid": message_instance.sid,
                "status": message_instance.status,
                "phone": formatted_phone
            }
            
        except TwilioException as e:
            logger.error(f"Failed to send SMS: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"Unexpected error sending SMS: {str(e)}")
            return {
                "success": False,
                "error": "Failed to send SMS"
            }
    
    async def send_2fa_code(self, phone: str) -> Dict[str, Any]:
        """Send 2FA verification code using Twilio Verify"""
        try:
            if not self.verify_service_sid:
                return {
                    "success": False,
                    "error": "Verify service not configured"
                }
            
            formatted_phone = self.format_phone_number(phone)
            
            verification = self.client.verify \
                .services(self.verify_service_sid) \
                .verifications \
                .create(to=formatted_phone, channel='sms')
            
            logger.info(f"✅ 2FA code sent to {formatted_phone}: {verification.sid}")
            
            return {
                "success": True,
                "verification_sid": verification.sid,
                "status": verification.status,
                "phone": formatted_phone,
                "valid_until": (datetime.utcnow() + timedelta(minutes=10)).isoformat()
            }
            
        except TwilioException as e:
            logger.error(f"Failed to send 2FA code: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"Unexpected error sending 2FA: {str(e)}")
            return {
                "success": False,
                "error": "Failed to send verification code"
            }
    
    async def verify_2fa_code(self, phone: str, code: str) -> Dict[str, Any]:
        """Verify 2FA code using Twilio Verify"""
        try:
            if not self.verify_service_sid:
                return {
                    "success": False,
                    "error": "Verify service not configured"
                }
            
            formatted_phone = self.format_phone_number(phone)
            
            verification_check = self.client.verify \
                .services(self.verify_service_sid) \
                .verification_checks \
                .create(to=formatted_phone, code=code)
            
            is_valid = verification_check.status == 'approved'
            
            logger.info(f"✅ 2FA verification for {formatted_phone}: {verification_check.status}")
            
            return {
                "success": True,
                "valid": is_valid,
                "status": verification_check.status,
                "phone": formatted_phone
            }
            
        except TwilioException as e:
            logger.error(f"Failed to verify 2FA code: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"Unexpected error verifying 2FA: {str(e)}")
            return {
                "success": False,
                "error": "Failed to verify code"
            }
    
    # Pre-defined message templates
    def get_welcome_message(self, user_name: str) -> str:
        return f"Welcome to OnlyMentors.ai, {user_name}! Your account has been created successfully. Start asking questions to 400+ legendary mentors."
    
    def get_mentor_response_message(self, mentor_name: str) -> str:
        return f"💡 New response from {mentor_name} on OnlyMentors.ai! Check your account to read their wisdom."
    
    def get_password_reset_message(self, reset_code: str) -> str:
        return f"Your OnlyMentors.ai password reset code is: {reset_code}. This code expires in 15 minutes."
    
    def get_account_suspended_message(self) -> str:
        return "Your OnlyMentors.ai account has been temporarily suspended. Please contact support for assistance."
    
    def get_subscription_renewal_message(self, days_left: int) -> str:
        return f"Your OnlyMentors.ai subscription expires in {days_left} days. Renew now to continue unlimited access to mentors."
    
    def get_login_alert_message(self, location: str = "unknown location") -> str:
        return f"🔒 Security Alert: New login to your OnlyMentors.ai account from {location}. If this wasn't you, please secure your account immediately."

# Create singleton instance
sms_service = SMSService()

# Convenience functions for easy import
async def send_sms(phone: str, message: str) -> Dict[str, Any]:
    """Send SMS notification"""
    return await sms_service.send_notification_sms(phone, message)

async def send_2fa(phone: str) -> Dict[str, Any]:
    """Send 2FA verification code"""
    return await sms_service.send_2fa_code(phone)

async def verify_2fa(phone: str, code: str) -> Dict[str, Any]:
    """Verify 2FA code"""
    return await sms_service.verify_2fa_code(phone, code)

def format_phone(phone: str) -> str:
    """Format phone number to E.164"""
    return sms_service.format_phone_number(phone)

def validate_phone(phone: str) -> bool:
    """Validate phone number"""
    return sms_service.validate_phone_number(phone)