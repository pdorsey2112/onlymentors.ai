#!/usr/bin/env python3
"""
Simple Premium Content Upload Test
Testing the premium content upload functionality with file upload capability
"""

import requests
import json
import uuid
import tempfile
import os

# Configuration
BACKEND_URL = "http://127.0.0.1:8001"

def test_premium_content_upload():
    """Test premium content upload with file functionality"""
    print("🧠 OnlyMentors.ai Premium Content Upload Test")
    print("=" * 50)
    
    # Step 1: Create test creator
    print("\n📋 Creating test creator...")
    creator_data = {
        "email": f"testcreator_{uuid.uuid4().hex[:8]}@example.com",
        "password": "TestPassword123!",
        "full_name": "Premium Content Creator",
        "account_name": f"PremiumCreator_{uuid.uuid4().hex[:8]}",
        "description": "Test creator for premium content file upload testing",
        "monthly_price": 199.0,
        "category": "business",
        "expertise_areas": ["content creation", "digital marketing"]
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/api/creators/signup", json=creator_data)
        if response.status_code == 200:
            data = response.json()
            creator_token = data.get("token")
            print(f"✅ Creator created successfully")
        else:
            print(f"❌ Failed to create creator: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception creating creator: {str(e)}")
        return False
    
    # Step 2: Test premium content upload with FormData
    print("\n📁 Testing premium content upload with FormData...")
    
    headers = {"Authorization": f"Bearer {creator_token}"}
    
    # Test 1: Upload without file
    print("\n1. Testing upload without file...")
    try:
        form_data = {
            'title': 'Premium Business Strategy Guide',
            'description': 'Comprehensive guide to modern business strategy with actionable insights',
            'content_type': 'document',
            'category': 'business',
            'price': '24.99',
            'tags': '["business", "strategy", "guide", "premium"]',
            'preview_available': 'true'
        }
        
        response = requests.post(f"{BACKEND_URL}/api/creator/content/upload", 
                               data=form_data, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            pricing = data.get("pricing_breakdown", {})
            print(f"✅ Upload without file successful")
            print(f"   Content ID: {data.get('content_id')}")
            print(f"   Platform fee: ${pricing.get('platform_fee'):.2f}")
            print(f"   Creator earnings: ${pricing.get('creator_earnings'):.2f}")
        else:
            print(f"❌ Upload without file failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Exception in upload without file: {str(e)}")
    
    # Test 2: Upload with file
    print("\n2. Testing upload with file...")
    try:
        # Create a test PDF file
        pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000074 00000 n \n0000000120 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n179\n%%EOF"
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_file.write(pdf_content)
            temp_file_path = temp_file.name
        
        form_data = {
            'title': 'Premium PDF Guide with File',
            'description': 'Testing file upload with premium content',
            'content_type': 'document',
            'category': 'business',
            'price': '15.99',
            'tags': '["test", "pdf", "file"]',
            'preview_available': 'false'
        }
        
        with open(temp_file_path, 'rb') as f:
            files = {'content_file': ('test_guide.pdf', f, 'application/pdf')}
            
            response = requests.post(f"{BACKEND_URL}/api/creator/content/upload", 
                                   data=form_data, files=files, headers=headers)
        
        # Clean up temp file
        os.unlink(temp_file_path)
        
        if response.status_code == 200:
            data = response.json()
            pricing = data.get("pricing_breakdown", {})
            print(f"✅ Upload with file successful")
            print(f"   Content ID: {data.get('content_id')}")
            print(f"   Platform fee: ${pricing.get('platform_fee'):.2f}")
            print(f"   Creator earnings: ${pricing.get('creator_earnings'):.2f}")
            
            # Verify minimum platform fee calculation
            if pricing.get('platform_fee') == 2.99:
                print(f"✅ Minimum platform fee correctly applied ($2.99)")
            else:
                print(f"⚠️  Platform fee: ${pricing.get('platform_fee'):.2f} (expected $2.99 minimum)")
                
        else:
            print(f"❌ Upload with file failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Exception in upload with file: {str(e)}")
    
    # Test 3: Test form validation
    print("\n3. Testing form validation...")
    
    # Test invalid price (too low)
    try:
        form_data = {
            'title': 'Invalid Price Test',
            'description': 'Testing price validation',
            'content_type': 'document',
            'category': 'test',
            'price': '0.005',  # Below minimum $0.01
            'tags': '[]',
            'preview_available': 'false'
        }
        
        response = requests.post(f"{BACKEND_URL}/api/creator/content/upload", 
                               data=form_data, headers=headers)
        
        if response.status_code == 400:
            print(f"✅ Price validation working - correctly rejected price below $0.01")
        else:
            print(f"❌ Price validation failed - should reject low price, got: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Exception in price validation: {str(e)}")
    
    # Test invalid price (too high)
    try:
        form_data = {
            'title': 'Invalid High Price Test',
            'description': 'Testing high price validation',
            'content_type': 'document',
            'category': 'test',
            'price': '75.00',  # Above maximum $50.00
            'tags': '[]',
            'preview_available': 'false'
        }
        
        response = requests.post(f"{BACKEND_URL}/api/creator/content/upload", 
                               data=form_data, headers=headers)
        
        if response.status_code == 400:
            print(f"✅ Price validation working - correctly rejected price above $50.00")
        else:
            print(f"❌ Price validation failed - should reject high price, got: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Exception in high price validation: {str(e)}")
    
    # Test 4: Test authentication
    print("\n4. Testing authentication...")
    
    # Test without token
    try:
        form_data = {
            'title': 'Unauthorized Test',
            'description': 'Testing authentication requirement',
            'content_type': 'document',
            'category': 'test',
            'price': '10.00'
        }
        
        response = requests.post(f"{BACKEND_URL}/api/creator/content/upload", data=form_data)
        
        if response.status_code in [401, 403]:
            print(f"✅ Authentication working - correctly rejected request without token")
        else:
            print(f"❌ Authentication failed - should require token, got: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Exception in authentication test: {str(e)}")
    
    # Test with invalid token
    try:
        invalid_headers = {"Authorization": "Bearer invalid_token_12345"}
        
        response = requests.post(f"{BACKEND_URL}/api/creator/content/upload", 
                               data=form_data, headers=invalid_headers)
        
        if response.status_code in [401, 403]:
            print(f"✅ Authentication working - correctly rejected invalid token")
        else:
            print(f"❌ Authentication failed - should reject invalid token, got: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Exception in invalid token test: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎯 PREMIUM CONTENT FILE UPLOAD TESTING COMPLETE")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    test_premium_content_upload()