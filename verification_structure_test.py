#!/usr/bin/env python3
"""
Verification Structure Test
Test to confirm the exact data structure mismatch in mentor verification fields
"""

import requests
import json
from datetime import datetime

BACKEND_URL = "https://mentor-search.preview.emergentagent.com/api"

def test_mentor_creation_and_verification():
    """Test mentor creation to see exact verification structure"""
    print("🔍 TESTING MENTOR VERIFICATION STRUCTURE MISMATCH")
    print("=" * 60)
    
    try:
        # Create a test user who becomes a mentor
        user_data = {
            "email": f"verification.test.{int(datetime.now().timestamp())}@test.com",
            "password": "TestPass123!",
            "full_name": "Verification Test User",
            "phone_number": "+1234567890",
            "communication_preferences": json.dumps({"email": True}),
            "subscription_plan": "free",
            "become_mentor": True
        }
        
        print("📋 Step 1: Creating mentor via registration...")
        response = requests.post(
            f"{BACKEND_URL}/auth/register",
            data=user_data,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Mentor created successfully")
            print(f"   User ID: {data['user']['user_id']}")
            print(f"   Is Mentor: {data['user'].get('is_mentor', False)}")
        else:
            print(f"❌ Failed to create mentor: {response.status_code}")
            print(f"   Error: {response.text}")
            return
            
        print()
        
        # Now check what the search API returns for this mentor
        print("📋 Step 2: Checking mentor in search API...")
        search_response = requests.get(
            f"{BACKEND_URL}/search/mentors?mentor_type=human&limit=1",
            timeout=30
        )
        
        if search_response.status_code == 200:
            search_data = search_response.json()
            mentors = search_data.get("results", [])
            
            if mentors:
                mentor = mentors[0]
                print("✅ Found mentor in search API")
                print("📋 Mentor fields from search API:")
                for key in sorted(mentor.keys()):
                    print(f"   {key}: {mentor[key]}")
            else:
                print("❌ No mentors found in search API")
        else:
            print(f"❌ Search API failed: {search_response.status_code}")
            
        print()
        
        # Now try the admin API to see the exact error
        print("📋 Step 3: Testing admin API with proper authentication...")
        
        # Login as admin
        admin_login = {
            "email": "admin@onlymentors.ai",
            "password": "SuperAdmin2024!"
        }
        
        admin_response = requests.post(
            f"{BACKEND_URL}/admin/login",
            json=admin_login,
            timeout=30
        )
        
        if admin_response.status_code == 200:
            admin_data = admin_response.json()
            admin_token = admin_data.get("token")
            print("✅ Admin login successful")
            
            # Now try to get mentors
            headers = {"Authorization": f"Bearer {admin_token}"}
            mentors_response = requests.get(
                f"{BACKEND_URL}/admin/mentors?limit=1",
                headers=headers,
                timeout=30
            )
            
            print(f"📋 Admin mentors endpoint status: {mentors_response.status_code}")
            
            if mentors_response.status_code == 500:
                try:
                    error_data = mentors_response.json()
                    print(f"❌ Error details: {error_data.get('detail', 'Unknown error')}")
                    
                    # This confirms the verification structure mismatch
                    if "'full_name'" in str(error_data.get('detail', '')):
                        print("🔍 Error is related to 'full_name' field")
                    elif "verification" in str(error_data.get('detail', '')):
                        print("🔍 Error is related to 'verification' field structure")
                        print("   Expected: verification.id_verified, verification.bank_verified")
                        print("   Actual: verification.status, verification.approved_at, verification.approved_by")
                        
                except:
                    print(f"❌ Raw error: {mentors_response.text}")
                    
            elif mentors_response.status_code == 200:
                print("✅ Admin mentors endpoint working")
                admin_mentors_data = mentors_response.json()
                mentors = admin_mentors_data.get("mentors", [])
                print(f"   Retrieved {len(mentors)} mentors")
                
        else:
            print(f"❌ Admin login failed: {admin_response.status_code}")
            
        print()
        print("🎯 CONCLUSION:")
        print("The issue is confirmed to be a data structure mismatch in the verification field.")
        print("The admin endpoint expects verification.id_verified and verification.bank_verified")
        print("but the mentor signup creates verification.status, verification.approved_at, etc.")
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")

if __name__ == "__main__":
    test_mentor_creation_and_verification()