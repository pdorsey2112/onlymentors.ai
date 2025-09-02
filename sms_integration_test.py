#!/usr/bin/env python3
"""
Direct SMS System Integration Test
Testing Twilio integration with real credentials
"""

import asyncio
import aiohttp
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Test configuration
BACKEND_URL = "https://mentor-search.preview.emergentagent.com/api"

async def test_sms_integration():
    """Test SMS system integration directly"""
    print("🧪 Testing SMS System Integration with Twilio")
    print("=" * 50)
    
    # Check environment variables
    print("📋 Environment Variables:")
    print(f"   TWILIO_ACCOUNT_SID: {os.getenv('TWILIO_ACCOUNT_SID')}")
    print(f"   TWILIO_AUTH_TOKEN: {'*' * 10 if os.getenv('TWILIO_AUTH_TOKEN') else 'Not set'}")
    print(f"   TWILIO_VERIFY_SERVICE_SID: {os.getenv('TWILIO_VERIFY_SERVICE_SID')}")
    
    # Test phone validation with a real phone number format
    async with aiohttp.ClientSession() as session:
        
        # Test 1: Phone validation with various formats
        print("\n🧪 Test 1: Phone Number Validation")
        test_phones = [
            "+15551234567",  # Valid US format
            "5551234567",    # US without country code
            "+447700900123", # UK format
            "123",           # Invalid
            ""               # Empty
        ]
        
        for phone in test_phones:
            try:
                data = {"phone_number": phone}
                async with session.post(f"{BACKEND_URL}/sms/validate-phone", json=data) as response:
                    result = await response.json()
                    status = "✅" if response.status == 200 else "❌"
                    print(f"   {status} {phone}: {result}")
            except Exception as e:
                print(f"   ❌ {phone}: Error - {str(e)}")
        
        # Test 2: 2FA Code Sending
        print("\n🧪 Test 2: 2FA Code Sending")
        try:
            data = {"phone_number": "+15551234567"}  # Test number
            async with session.post(f"{BACKEND_URL}/sms/send-2fa", json=data) as response:
                result = await response.json()
                status = "✅" if response.status == 200 else "❌"
                print(f"   {status} 2FA Send: {result}")
                
                # If successful, test verification
                if response.status == 200:
                    print("\n🧪 Test 3: 2FA Code Verification")
                    verify_data = {"phone_number": "+15551234567", "code": "123456"}
                    async with session.post(f"{BACKEND_URL}/sms/verify-2fa", json=verify_data) as verify_response:
                        verify_result = await verify_response.json()
                        verify_status = "✅" if verify_response.status == 200 else "❌"
                        print(f"   {verify_status} 2FA Verify: {verify_result}")
                        
        except Exception as e:
            print(f"   ❌ 2FA Test Error: {str(e)}")
        
        # Test 3: Error handling
        print("\n🧪 Test 4: Error Handling")
        error_tests = [
            {"endpoint": "/sms/validate-phone", "data": {}, "name": "Missing phone"},
            {"endpoint": "/sms/send-2fa", "data": {"phone_number": ""}, "name": "Empty phone"},
            {"endpoint": "/sms/verify-2fa", "data": {"phone_number": "+15551234567"}, "name": "Missing code"}
        ]
        
        for test in error_tests:
            try:
                async with session.post(f"{BACKEND_URL}{test['endpoint']}", json=test["data"]) as response:
                    result = await response.json()
                    status = "✅" if response.status in [400, 422] else "❌"
                    print(f"   {status} {test['name']}: {response.status} - {result.get('detail', 'No detail')}")
            except Exception as e:
                print(f"   ❌ {test['name']}: Error - {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_sms_integration())