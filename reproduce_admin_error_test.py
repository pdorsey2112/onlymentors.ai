#!/usr/bin/env python3
"""
Reproduce Admin Mentors 500 Error
"""

import requests
import json

# Configuration
BASE_URL = "https://multi-tenant-ai.preview.emergentagent.com/api"
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

def test_reproduce_500_error():
    """Try to reproduce the 500 error seen in logs"""
    print("🔍 REPRODUCING ADMIN MENTORS 500 ERROR")
    print("=" * 50)
    
    admin_token = get_admin_token()
    if not admin_token:
        print("❌ Cannot get admin token")
        return
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Test cases that caused 500 errors in logs
    test_cases = [
        ("limit=100", "High limit that caused 500 in logs"),
        ("limit=100&search=mentor", "High limit + search that caused 500"),
        ("limit=200", "Very high limit"),
        ("limit=50&search=test", "Medium limit + search"),
        ("limit=10&search=nonexistent", "Search for non-existent term"),
        ("limit=1000", "Extremely high limit"),
    ]
    
    for params, description in test_cases:
        print(f"\n🧪 Testing: {description}")
        print(f"   URL: /api/admin/mentors?{params}")
        
        try:
            response = requests.get(f"{BASE_URL}/admin/mentors?{params}", headers=headers)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                mentors_count = len(data.get('mentors', []))
                total = data.get('total', 0)
                print(f"   ✅ SUCCESS: {mentors_count} mentors returned, Total: {total}")
            elif response.status_code == 500:
                print(f"   🚨 500 ERROR REPRODUCED!")
                print(f"   Error: {response.text}")
                
                # This is likely what's causing the frontend to show "0 mentors"
                print("   💡 This 500 error explains why frontend shows 0 mentors!")
            else:
                print(f"   ❌ Other error: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎯 ANALYSIS")
    print("=" * 50)
    print("If any 500 errors were reproduced above, that explains")
    print("why the admin console shows '0 mentors' in the user's screenshot.")
    print("The frontend likely uses limit=100 or a search term that triggers the error.")

if __name__ == "__main__":
    test_reproduce_500_error()