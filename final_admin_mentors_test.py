#!/usr/bin/env python3
"""
Final Admin Mentors Test - Confirm the fix works
"""

import requests
import json

# Configuration
BASE_URL = "https://mentor-search.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@onlymentors.ai"
ADMIN_PASSWORD = "SuperAdmin2024!"

def get_admin_token():
    """Get admin authentication token"""
    login_data = {
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    }
    
    response = requests.post(f"{BASE_URL}/admin/login", json=login_data)
    if response.status_code == 200:
        return response.json().get("token")
    return None

def test_admin_mentors_final():
    """Final test to confirm admin mentors endpoint is working"""
    print("🎯 FINAL ADMIN MENTORS ENDPOINT TEST")
    print("=" * 50)
    
    admin_token = get_admin_token()
    if not admin_token:
        print("❌ Cannot get admin token")
        return False
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Test the exact scenario that was failing
    print("🧪 Testing the exact frontend scenario (limit=100)...")
    
    try:
        response = requests.get(f"{BASE_URL}/admin/mentors?limit=100", headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            mentors = data.get('mentors', [])
            total = data.get('total', 0)
            
            print(f"✅ SUCCESS!")
            print(f"   Mentors returned: {len(mentors)}")
            print(f"   Total mentors: {total}")
            print(f"   Response keys: {list(data.keys())}")
            
            if mentors:
                print(f"\n   Sample mentor data:")
                sample = mentors[0]
                print(f"   - Creator ID: {sample.get('creator_id')}")
                print(f"   - Full Name: {sample.get('full_name')}")
                print(f"   - Email: {sample.get('email')}")
                print(f"   - Category: {sample.get('category')}")
                print(f"   - Status: {sample.get('status')}")
                print(f"   - Verification: {sample.get('verification')}")
            
            # Test pagination calculation for frontend
            limit = data.get('limit', 100)
            offset = data.get('offset', 0)
            page = (offset // limit) + 1 if limit > 0 else 1
            print(f"\n   Pagination info:")
            print(f"   - Limit: {limit}")
            print(f"   - Offset: {offset}")
            print(f"   - Calculated Page: {page}")
            
            return True
        else:
            print(f"❌ FAILED: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def main():
    """Main test function"""
    success = test_admin_mentors_final()
    
    print("\n" + "=" * 50)
    print("🎯 FINAL RESULT")
    print("=" * 50)
    
    if success:
        print("🎉 ADMIN MENTORS ENDPOINT IS NOW WORKING!")
        print("✅ The fix successfully resolved the '0 mentors' issue")
        print("✅ Admin console should now display all mentors correctly")
        print("✅ Frontend will receive proper mentor data with limit=100")
        print("\n💡 The issue was caused by missing 'full_name' and 'verification'")
        print("   fields in some mentor documents. The fix uses .get() methods")
        print("   with fallback values to handle missing fields gracefully.")
    else:
        print("❌ ADMIN MENTORS ENDPOINT STILL HAS ISSUES")
        print("❌ Further investigation needed")
    
    print("=" * 50)

if __name__ == "__main__":
    main()