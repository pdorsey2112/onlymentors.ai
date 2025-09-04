#!/usr/bin/env python3
"""
Focused Premium Content Management Fix Test
==========================================

Specifically testing the fix where uploaded premium content now appears 
in management interface by querying both db.premium_content and db.creator_content collections.
"""

import requests
import json
import time
import os
from datetime import datetime

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://multi-tenant-ai.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

def test_premium_content_management_fix():
    """Test the specific fix for premium content management"""
    print("🧪 TESTING PREMIUM CONTENT MANAGEMENT FIX")
    print("=" * 50)
    print("Issue: Uploaded premium content not appearing in management interface")
    print("Fix: Updated /api/creators/{creator_id}/content to query both collections")
    print("=" * 50)
    
    # Step 1: Create test creator
    print("\n1️⃣ Creating test creator...")
    timestamp = int(time.time())
    creator_data = {
        "email": f"testcreator_{timestamp}@example.com",
        "password": "TestPassword123!",
        "full_name": f"Test Creator {timestamp}",
        "account_name": f"testcreator{timestamp}",
        "bio": "Test creator for premium content fix testing",
        "category": "business",
        "hourly_rate": 150.0
    }
    
    try:
        response = requests.post(f"{API_BASE}/creators/signup", json=creator_data)
        if response.status_code != 200:
            print(f"❌ Creator signup failed: {response.status_code} - {response.text}")
            return False
        
        data = response.json()
        creator_token = data.get("token")
        creator_id = data.get("creator", {}).get("creator_id")
        
        if not creator_token or not creator_id:
            print("❌ Failed to get creator token or ID")
            return False
        
        print(f"✅ Creator created successfully: {creator_id}")
        
    except Exception as e:
        print(f"❌ Creator creation failed: {str(e)}")
        return False
    
    # Step 2: Upload premium content (stores in db.premium_content)
    print("\n2️⃣ Uploading premium content...")
    headers = {"Authorization": f"Bearer {creator_token}"}
    
    premium_content = {
        "title": "Premium Content Management Fix Test",
        "description": "Testing if uploaded premium content appears in management interface",
        "content_type": "document",
        "category": "business",
        "price": "29.99",
        "tags": json.dumps(["test", "premium", "management"]),
        "preview_available": "true"
    }
    
    try:
        response = requests.post(f"{API_BASE}/creator/content/upload", data=premium_content, headers=headers)
        if response.status_code != 200:
            print(f"❌ Premium content upload failed: {response.status_code} - {response.text}")
            return False
        
        upload_data = response.json()
        content_id = upload_data.get("content_id")
        print(f"✅ Premium content uploaded successfully: {content_id}")
        
    except Exception as e:
        print(f"❌ Premium content upload failed: {str(e)}")
        return False
    
    # Step 3: Wait for database consistency
    print("\n3️⃣ Waiting for database consistency...")
    time.sleep(3)
    
    # Step 4: Retrieve content via management interface (queries both collections)
    print("\n4️⃣ Testing management interface retrieval...")
    try:
        response = requests.get(f"{API_BASE}/creators/{creator_id}/content", headers=headers)
        if response.status_code != 200:
            print(f"❌ Content retrieval failed: {response.status_code} - {response.text}")
            return False
        
        retrieval_data = response.json()
        content_list = retrieval_data.get("content", [])
        total = retrieval_data.get("total", 0)
        
        print(f"✅ Content retrieval successful: {len(content_list)} items retrieved")
        
        # Step 5: Verify uploaded premium content appears in management interface
        print("\n5️⃣ Verifying premium content appears in management interface...")
        
        found_content = None
        for content in content_list:
            if content.get("title") == premium_content["title"]:
                found_content = content
                break
        
        if found_content:
            print("✅ SUCCESS: Uploaded premium content found in management interface!")
            print(f"   Title: {found_content.get('title')}")
            print(f"   Content Type: {found_content.get('content_type')}")
            print(f"   Price: ${found_content.get('price')}")
            print(f"   Category: {found_content.get('category')}")
            
            # Verify metadata preservation
            metadata_correct = True
            checks = [
                ("title", premium_content["title"]),
                ("description", premium_content["description"]),
                ("content_type", premium_content["content_type"]),
                ("category", premium_content["category"]),
                ("price", float(premium_content["price"]))
            ]
            
            for field, expected in checks:
                actual = found_content.get(field)
                if actual != expected:
                    print(f"⚠️  Metadata mismatch for {field}: expected {expected}, got {actual}")
                    metadata_correct = False
                else:
                    print(f"✅ Metadata correct for {field}: {actual}")
            
            return metadata_correct
            
        else:
            print("❌ FAILURE: Uploaded premium content NOT found in management interface!")
            print("   This indicates the fix is not working correctly.")
            print(f"   Available content titles: {[c.get('title') for c in content_list]}")
            return False
        
    except Exception as e:
        print(f"❌ Content retrieval failed: {str(e)}")
        return False

def test_collection_integration():
    """Test that both standard and premium content appear together"""
    print("\n\n🔄 TESTING COLLECTION INTEGRATION")
    print("=" * 50)
    
    # Create test creator
    timestamp = int(time.time())
    creator_data = {
        "email": f"testcreator2_{timestamp}@example.com",
        "password": "TestPassword123!",
        "full_name": f"Test Creator 2 {timestamp}",
        "account_name": f"testcreator2{timestamp}",
        "bio": "Test creator for collection integration testing",
        "category": "business",
        "hourly_rate": 150.0
    }
    
    try:
        response = requests.post(f"{API_BASE}/creators/signup", json=creator_data)
        data = response.json()
        creator_token = data.get("token")
        creator_id = data.get("creator", {}).get("creator_id")
        headers = {"Authorization": f"Bearer {creator_token}"}
        
        print(f"✅ Test creator 2 created: {creator_id}")
        
        # Upload standard content (stores in db.creator_content)
        standard_content = {
            "title": "Standard Content Test",
            "description": "Testing standard content in combined results",
            "content_type": "document",
            "category": "business",
            "tags": ["standard", "test"]
        }
        
        response = requests.post(f"{API_BASE}/creators/{creator_id}/content", json=standard_content, headers=headers)
        if response.status_code == 200:
            print("✅ Standard content uploaded")
        else:
            print(f"⚠️  Standard content upload failed: {response.status_code}")
        
        # Upload premium content (stores in db.premium_content)
        premium_content = {
            "title": "Premium Content Test",
            "description": "Testing premium content in combined results",
            "content_type": "video",
            "category": "business",
            "price": "19.99",
            "tags": json.dumps(["premium", "test"]),
            "preview_available": "false"
        }
        
        response = requests.post(f"{API_BASE}/creator/content/upload", data=premium_content, headers=headers)
        if response.status_code == 200:
            print("✅ Premium content uploaded")
        else:
            print(f"⚠️  Premium content upload failed: {response.status_code}")
        
        time.sleep(3)
        
        # Retrieve combined content
        response = requests.get(f"{API_BASE}/creators/{creator_id}/content", headers=headers)
        if response.status_code == 200:
            data = response.json()
            content_list = data.get("content", [])
            
            # Check for both types
            standard_found = any(c.get("title") == "Standard Content Test" for c in content_list)
            premium_found = any(c.get("title") == "Premium Content Test" for c in content_list)
            
            print(f"✅ Retrieved {len(content_list)} total content items")
            print(f"✅ Standard content found: {standard_found}")
            print(f"✅ Premium content found: {premium_found}")
            
            if standard_found and premium_found:
                print("✅ SUCCESS: Both standard and premium content appear in combined results!")
                return True
            else:
                print("❌ FAILURE: Not all content types found in combined results")
                return False
        else:
            print(f"❌ Failed to retrieve combined content: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Collection integration test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 PREMIUM CONTENT MANAGEMENT FIX VERIFICATION")
    print("=" * 60)
    
    # Test 1: Core fix verification
    test1_result = test_premium_content_management_fix()
    
    # Test 2: Collection integration
    test2_result = test_collection_integration()
    
    # Final assessment
    print("\n" + "=" * 60)
    print("🎯 FINAL ASSESSMENT")
    print("=" * 60)
    
    if test1_result and test2_result:
        print("✅ PREMIUM CONTENT MANAGEMENT FIX IS WORKING CORRECTLY!")
        print("   ✓ Uploaded premium content appears in management interface")
        print("   ✓ Both standard and premium content are properly combined")
        print("   ✓ Metadata is preserved correctly")
        print("   ✓ Database collection integration is functional")
    elif test1_result:
        print("⚠️  PREMIUM CONTENT MANAGEMENT PARTIALLY WORKING")
        print("   ✓ Core fix is working (premium content appears)")
        print("   ❌ Some issues with collection integration")
    else:
        print("❌ PREMIUM CONTENT MANAGEMENT FIX NEEDS ATTENTION")
        print("   ❌ Core issue not resolved - premium content not appearing")
        print("   ❌ Database collection mismatch may still exist")
    
    print(f"\nTest Results: Core Fix = {test1_result}, Integration = {test2_result}")