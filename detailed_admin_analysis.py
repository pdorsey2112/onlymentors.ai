#!/usr/bin/env python3
"""
Detailed Admin Analysis
Deep dive into what the admin mentors endpoint is actually returning
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "https://mentor-search.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@onlymentors.ai"
ADMIN_PASSWORD = "SuperAdmin2024!"

class DetailedAdminAnalyzer:
    def __init__(self):
        self.admin_token = None
        
    def get_admin_token(self):
        """Get admin authentication token"""
        login_data = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        
        try:
            response = requests.post(f"{BASE_URL}/admin/login", json=login_data)
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token")
                print(f"✅ Admin authenticated successfully")
                return True
            else:
                print(f"❌ Admin login failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Admin login exception: {str(e)}")
            return False

    def analyze_admin_mentors_data(self):
        """Analyze what the admin mentors endpoint returns"""
        print("\n🔍 ANALYZING ADMIN MENTORS ENDPOINT DATA")
        print("=" * 50)
        
        if not self.admin_token:
            print("❌ No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            # Get all mentors from admin endpoint
            response = requests.get(f"{BASE_URL}/admin/mentors?limit=100", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                mentors = data.get("mentors", [])
                total = data.get("total", 0)
                
                print(f"📊 Admin endpoint returns: {len(mentors)} mentors (Total: {total})")
                
                if mentors:
                    # Analyze the first few mentors
                    print(f"\n📋 SAMPLE MENTOR DATA:")
                    print("-" * 30)
                    
                    for i, mentor in enumerate(mentors[:3]):
                        print(f"\nMentor {i+1}:")
                        print(f"  Creator ID: {mentor.get('creator_id')}")
                        print(f"  Email: {mentor.get('email')}")
                        print(f"  Full Name: {mentor.get('full_name')}")
                        print(f"  Account Name: {mentor.get('account_name')}")
                        print(f"  Category: {mentor.get('category')}")
                        print(f"  Status: {mentor.get('status')}")
                        print(f"  Monthly Price: ${mentor.get('monthly_price')}")
                        print(f"  Subscriber Count: {mentor.get('subscriber_count')}")
                        print(f"  Total Earnings: ${mentor.get('total_earnings')}")
                        print(f"  Created At: {mentor.get('created_at')}")
                        
                        # Check verification structure
                        verification = mentor.get('verification', {})
                        print(f"  Verification: ID={verification.get('id_verified')}, Bank={verification.get('bank_verified')}")
                    
                    # Analyze categories
                    categories = {}
                    statuses = {}
                    
                    for mentor in mentors:
                        category = mentor.get('category', 'Unknown')
                        status = mentor.get('status', 'Unknown')
                        
                        categories[category] = categories.get(category, 0) + 1
                        statuses[status] = statuses.get(status, 0) + 1
                    
                    print(f"\n📊 CATEGORY BREAKDOWN:")
                    print("-" * 25)
                    for category, count in sorted(categories.items()):
                        print(f"  {category}: {count}")
                    
                    print(f"\n📊 STATUS BREAKDOWN:")
                    print("-" * 20)
                    for status, count in sorted(statuses.items()):
                        print(f"  {status}: {count}")
                    
                    return mentors
                else:
                    print("❌ No mentors returned from admin endpoint")
                    return []
            else:
                print(f"❌ Admin mentors request failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return []
        except Exception as e:
            print(f"❌ Exception analyzing admin mentors: {str(e)}")
            return []

    def compare_with_search_api(self):
        """Compare admin mentors with search API results"""
        print("\n🔍 COMPARING WITH SEARCH API")
        print("=" * 35)
        
        try:
            # Get human mentors from search API
            response = requests.get(f"{BASE_URL}/search/mentors?mentor_type=human")
            
            if response.status_code == 200:
                data = response.json()
                human_mentors = data.get("results", [])
                
                print(f"📊 Search API human mentors: {len(human_mentors)}")
                
                if human_mentors:
                    print(f"\n📋 SAMPLE HUMAN MENTOR FROM SEARCH API:")
                    print("-" * 40)
                    
                    sample = human_mentors[0]
                    print(f"  ID: {sample.get('id')}")
                    print(f"  Name: {sample.get('name')}")
                    print(f"  Title: {sample.get('title')}")
                    print(f"  Bio: {sample.get('bio')[:100]}...")
                    print(f"  Expertise: {sample.get('expertise')}")
                    print(f"  Category: {sample.get('category')}")
                    print(f"  Mentor Type: {sample.get('mentor_type')}")
                    print(f"  Is AI Mentor: {sample.get('is_ai_mentor')}")
                    print(f"  Tier: {sample.get('tier')}")
                    print(f"  Monthly Price: ${sample.get('monthly_price')}")
                    print(f"  Subscriber Count: {sample.get('subscriber_count')}")
                
                return human_mentors
            else:
                print(f"❌ Search API request failed: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Exception comparing with search API: {str(e)}")
            return []

    def analyze_data_source_discrepancy(self, admin_mentors, search_human_mentors):
        """Analyze why there's a discrepancy between admin and search results"""
        print("\n🔍 ANALYZING DATA SOURCE DISCREPANCY")
        print("=" * 40)
        
        print(f"📊 Admin mentors count: {len(admin_mentors)}")
        print(f"📊 Search human mentors count: {len(search_human_mentors)}")
        
        if len(admin_mentors) > len(search_human_mentors):
            print(f"\n❓ WHY DOES ADMIN SHOW MORE MENTORS?")
            print("-" * 35)
            print("Possible reasons:")
            print("1. Admin endpoint queries a different collection or uses different criteria")
            print("2. Admin endpoint includes mentors that search API filters out")
            print("3. Admin endpoint includes both AI and human mentors")
            print("4. Different verification status requirements")
            
            # Check if admin mentors include AI mentors
            if admin_mentors:
                # Look for patterns that might indicate AI mentors
                potential_ai_mentors = []
                for mentor in admin_mentors:
                    # Check for typical AI mentor characteristics
                    name = mentor.get('account_name', '').lower()
                    if any(famous_name in name for famous_name in ['steve jobs', 'elon musk', 'warren buffett', 'oprah', 'einstein']):
                        potential_ai_mentors.append(mentor)
                
                if potential_ai_mentors:
                    print(f"\n🤖 POTENTIAL AI MENTORS IN ADMIN RESULTS: {len(potential_ai_mentors)}")
                    print("-" * 45)
                    for ai_mentor in potential_ai_mentors[:5]:
                        print(f"  - {ai_mentor.get('account_name')} ({ai_mentor.get('category')})")
                else:
                    print("\n✅ No obvious AI mentors detected in admin results")
        
        elif len(search_human_mentors) > len(admin_mentors):
            print(f"\n❓ WHY DOES SEARCH SHOW MORE HUMAN MENTORS?")
            print("-" * 40)
            print("Possible reasons:")
            print("1. Search API includes mentors that admin endpoint filters out")
            print("2. Different status or verification requirements")
            print("3. Admin endpoint has bugs or incorrect query logic")
        
        else:
            print("\n✅ Counts match - investigating data structure differences")

    def run_analysis(self):
        """Run complete detailed analysis"""
        print("🚀 STARTING DETAILED ADMIN ANALYSIS")
        print("=" * 45)
        
        if not self.get_admin_token():
            return
        
        admin_mentors = self.analyze_admin_mentors_data()
        search_human_mentors = self.compare_with_search_api()
        
        self.analyze_data_source_discrepancy(admin_mentors, search_human_mentors)
        
        print(f"\n🎯 CONCLUSION")
        print("=" * 15)
        
        if len(admin_mentors) > 0:
            print("✅ Admin mentors endpoint IS returning data")
            print("❓ If admin console shows 'no mentors', the issue is likely:")
            print("   1. Frontend not calling the correct endpoint")
            print("   2. Frontend not handling the response correctly")
            print("   3. Frontend filtering out the results")
            print("   4. Authentication issues in frontend")
        else:
            print("❌ Admin mentors endpoint returns no data")
            print("🔧 Backend investigation needed")

if __name__ == "__main__":
    analyzer = DetailedAdminAnalyzer()
    analyzer.run_analysis()