#!/usr/bin/env python3
"""
Focused Admin Mentors Test - Debug the exact issue
"""

import requests
import json

# Configuration
BASE_URL = "https://enterprise-coach.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@onlymentors.ai"
ADMIN_PASSWORD = "SuperAdmin2024!"

def get_admin_token():
    """Get admin authentication token"""
    login_data = {
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    }
    
    try:
        response = requests.post(f"{BASE_URL}/admin/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            return data.get("token")
        else:
            print(f"❌ Admin login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Admin login exception: {str(e)}")
        return None

def test_admin_mentors_detailed():
    """Test admin mentors endpoint in detail"""
    print("🔍 DETAILED ADMIN MENTORS ENDPOINT TESTING")
    print("=" * 50)
    
    # Get admin token
    admin_token = get_admin_token()
    if not admin_token:
        print("❌ Cannot proceed without admin token")
        return
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Test 1: Basic call without parameters
    print("\n1️⃣ Testing basic admin mentors call...")
    try:
        response = requests.get(f"{BASE_URL}/admin/mentors", headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS: Returned {len(data.get('mentors', []))} mentors")
            print(f"   Total: {data.get('total', 0)}")
            print(f"   Limit: {data.get('limit', 0)}")
            print(f"   Offset: {data.get('offset', 0)}")
            print(f"   Response keys: {list(data.keys())}")
            
            # Check if any mentors have missing full_name
            mentors = data.get('mentors', [])
            if mentors:
                print(f"\n   Sample mentor fields: {list(mentors[0].keys())}")
                
                # Check for missing full_name fields
                missing_full_name = [m for m in mentors if 'full_name' not in m or not m.get('full_name')]
                if missing_full_name:
                    print(f"   ⚠️ Found {len(missing_full_name)} mentors without full_name field")
                    for i, mentor in enumerate(missing_full_name[:3]):
                        print(f"      Mentor {i+1}: {mentor.get('email', 'No email')} - full_name: {mentor.get('full_name', 'MISSING')}")
        else:
            print(f"❌ FAILED: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
    
    # Test 2: Call with pagination parameters that match frontend expectations
    print("\n2️⃣ Testing with page-style pagination...")
    try:
        response = requests.get(f"{BASE_URL}/admin/mentors?limit=10&offset=0", headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS: Pagination works")
            print(f"   Returned: {len(data.get('mentors', []))} mentors")
            print(f"   Total: {data.get('total', 0)}")
            
            # Calculate page number from offset
            limit = data.get('limit', 10)
            offset = data.get('offset', 0)
            page = (offset // limit) + 1 if limit > 0 else 1
            print(f"   Calculated page: {page}")
        else:
            print(f"❌ FAILED: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
    
    # Test 3: Test search functionality with a simple search term
    print("\n3️⃣ Testing search functionality...")
    try:
        response = requests.get(f"{BASE_URL}/admin/mentors?search=test", headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS: Search works")
            print(f"   Found: {len(data.get('mentors', []))} mentors matching 'test'")
        else:
            print(f"❌ SEARCH FAILED: {response.text}")
            
            # This is likely the issue causing "0 mentors" in frontend
            print("   🚨 This search failure might be why frontend shows 0 mentors!")
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
    
    # Test 4: Test empty search (should return all)
    print("\n4️⃣ Testing empty search...")
    try:
        response = requests.get(f"{BASE_URL}/admin/mentors?search=", headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS: Empty search works")
            print(f"   Returned: {len(data.get('mentors', []))} mentors")
        else:
            print(f"❌ FAILED: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
    
    # Test 5: Check what the frontend might be sending
    print("\n5️⃣ Testing potential frontend request patterns...")
    
    # Common frontend patterns
    test_params = [
        "?page=1&limit=10",
        "?page=1&limit=10&search=",
        "?page=1&limit=10&search=mentor",
        "?limit=10&offset=0&search=",
    ]
    
    for params in test_params:
        try:
            response = requests.get(f"{BASE_URL}/admin/mentors{params}", headers=headers)
            print(f"   {params}: Status {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"      ✅ Returned {len(data.get('mentors', []))} mentors")
            else:
                print(f"      ❌ Error: {response.text[:100]}...")
        except Exception as e:
            print(f"      ❌ Exception: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎯 ANALYSIS COMPLETE")
    print("=" * 50)

if __name__ == "__main__":
    test_admin_mentors_detailed()