#!/usr/bin/env python3
"""
Debug Mentor Document Structure
Check the actual structure of mentor documents to see what fields are missing
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "https://mentor-search.preview.emergentagent.com/api"

def debug_mentor_structure():
    """Debug the actual mentor document structure"""
    print("🔍 Debugging Mentor Document Structure")
    print("=" * 60)
    
    try:
        # Get human mentors
        response = requests.get(f"{BASE_URL}/search/mentors?mentor_type=human")
        
        if response.status_code == 200:
            data = response.json()
            mentors = data.get("results", [])
            
            print(f"📊 Found {len(mentors)} human mentors")
            print(f"📊 API Response metadata: {data.get('human_count', 0)} human mentors")
            print()
            
            if mentors:
                # Analyze first mentor structure
                mentor = mentors[0]
                print("📋 First Mentor Document Structure:")
                print(json.dumps(mentor, indent=2, default=str))
                print()
                
                # Check for admin console required fields
                admin_required = ["full_name", "category", "status", "verification"]
                print("🏛️ Admin Console Required Fields Check:")
                for field in admin_required:
                    if field in mentor:
                        value = mentor[field]
                        print(f"   ✅ {field}: {value} ({type(value).__name__})")
                    else:
                        print(f"   ❌ {field}: MISSING")
                print()
                
                # Check for search API required fields
                search_required = ["id", "name", "bio", "expertise", "mentor_type", "is_ai_mentor", 
                                 "tier", "tier_level", "tier_badge_color", "subscriber_count", "monthly_price"]
                print("🔍 Search API Required Fields Check:")
                for field in search_required:
                    if field in mentor:
                        value = mentor[field]
                        print(f"   ✅ {field}: {value} ({type(value).__name__})")
                    else:
                        print(f"   ❌ {field}: MISSING")
                print()
                
                # Check all available fields
                print("📝 All Available Fields:")
                for key, value in mentor.items():
                    print(f"   {key}: {value} ({type(value).__name__})")
                print()
                
                # Analyze multiple mentors if available
                if len(mentors) > 1:
                    print(f"📊 Analyzing all {len(mentors)} mentors for field consistency:")
                    
                    # Check field consistency across all mentors
                    all_fields = set()
                    for m in mentors:
                        all_fields.update(m.keys())
                    
                    field_presence = {}
                    for field in all_fields:
                        count = sum(1 for m in mentors if field in m)
                        field_presence[field] = count
                    
                    print("   Field presence across all mentors:")
                    for field, count in sorted(field_presence.items()):
                        percentage = (count / len(mentors)) * 100
                        print(f"     {field}: {count}/{len(mentors)} ({percentage:.1f}%)")
                    print()
            else:
                print("❌ No human mentors found to analyze")
        else:
            print(f"❌ Failed to get mentors. Status: {response.status_code}")
            print(f"   Response: {response.text}")
    
    except Exception as e:
        print(f"❌ Exception during debug: {str(e)}")

def test_admin_endpoint_error():
    """Test admin endpoint to see the exact error"""
    print("🏛️ Testing Admin Endpoint Error Details")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/admin/mentors")
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Text: {response.text}")
        
        if response.status_code == 500:
            print("\n🚨 500 Error Detected - This indicates the data structure issue is NOT fixed")
            
            # Try to parse error details
            try:
                if "full_name" in response.text:
                    print("   Error mentions 'full_name' - this field is missing from mentor documents")
                if "category" in response.text:
                    print("   Error mentions 'category' - this field is missing from mentor documents")
                if "status" in response.text:
                    print("   Error mentions 'status' - this field is missing from mentor documents")
                if "verification" in response.text:
                    print("   Error mentions 'verification' - verification object structure issue")
            except:
                pass
        elif response.status_code in [401, 403]:
            print("\n✅ Authentication Error - This means the endpoint is working (no 500 error)")
        
    except Exception as e:
        print(f"❌ Exception during admin endpoint test: {str(e)}")

def create_test_mentor_and_check():
    """Create a test mentor and immediately check its structure"""
    print("👤 Creating Test Mentor and Checking Structure")
    print("=" * 60)
    
    import time
    timestamp = int(time.time())
    test_email = f"structure.test.{timestamp}@test.com"
    test_name = f"Structure Test {timestamp}"
    
    signup_data = {
        "email": test_email,
        "password": "TestPass123!",
        "full_name": test_name,
        "phone_number": "+1234567894",
        "communication_preferences": json.dumps({"email": True, "text": False}),
        "subscription_plan": "free",
        "become_mentor": True
    }
    
    try:
        # Create mentor
        response = requests.post(f"{BASE_URL}/auth/register", data=signup_data)
        
        if response.status_code in [200, 201]:
            data = response.json()
            user_data = data.get("user", {})
            
            print(f"✅ Mentor created: {user_data.get('user_id')}")
            print(f"   Is mentor: {user_data.get('is_mentor', False)}")
            
            # Wait for database consistency
            print("⏳ Waiting 5 seconds for database consistency...")
            time.sleep(5)
            
            # Search for the mentor
            search_response = requests.get(f"{BASE_URL}/search/mentors?mentor_type=human&q={test_name}")
            
            if search_response.status_code == 200:
                search_data = search_response.json()
                mentors = search_data.get("results", [])
                
                # Find our mentor
                our_mentor = None
                for mentor in mentors:
                    if test_name in mentor.get("name", ""):
                        our_mentor = mentor
                        break
                
                if our_mentor:
                    print(f"✅ Found newly created mentor in search results")
                    print("\n📋 Newly Created Mentor Structure:")
                    print(json.dumps(our_mentor, indent=2, default=str))
                    
                    # Check specific fields
                    print("\n🔍 Field Analysis:")
                    print(f"   name: {our_mentor.get('name', 'MISSING')}")
                    print(f"   full_name: {our_mentor.get('full_name', 'MISSING')}")
                    print(f"   category: {our_mentor.get('category', 'MISSING')}")
                    print(f"   status: {our_mentor.get('status', 'MISSING')}")
                    print(f"   verification: {our_mentor.get('verification', 'MISSING')}")
                    print(f"   verification_status: {our_mentor.get('verification_status', 'MISSING')}")
                    print(f"   mentor_type: {our_mentor.get('mentor_type', 'MISSING')}")
                    print(f"   is_ai_mentor: {our_mentor.get('is_ai_mentor', 'MISSING')}")
                else:
                    print(f"❌ Newly created mentor not found in search results")
                    print(f"   Searched for: {test_name}")
                    print(f"   Total human mentors found: {len(mentors)}")
            else:
                print(f"❌ Search failed. Status: {search_response.status_code}")
        else:
            print(f"❌ Mentor creation failed. Status: {response.status_code}")
            print(f"   Response: {response.text}")
    
    except Exception as e:
        print(f"❌ Exception during mentor creation test: {str(e)}")

if __name__ == "__main__":
    debug_mentor_structure()
    print("\n" + "=" * 60 + "\n")
    test_admin_endpoint_error()
    print("\n" + "=" * 60 + "\n")
    create_test_mentor_and_check()