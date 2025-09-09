#!/usr/bin/env python3
"""
Detailed User Analysis Test
Analyzes the actual user data to understand why business users are not appearing
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "https://enterprise-coach.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@onlymentors.ai"
ADMIN_PASSWORD = "SuperAdmin2024!"

class DetailedUserAnalyzer:
    def __init__(self):
        self.admin_token = None
        
    def setup_admin_auth(self):
        """Authenticate as admin"""
        print("🔧 Setting up admin authentication...")
        
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
                print(f"❌ Admin auth failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Admin auth exception: {str(e)}")
            return False

    def analyze_user_data_in_detail(self):
        """Get detailed analysis of user data"""
        print("\n🔍 DETAILED USER DATA ANALYSIS")
        print("=" * 50)
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = requests.get(f"{BASE_URL}/admin/users", headers=headers)
            if response.status_code == 200:
                data = response.json()
                users = data.get("users", [])
                
                print(f"📊 Total users found: {len(users)}")
                print()
                
                # Analyze first 10 users in detail
                print("👥 SAMPLE USER DATA (First 10 users):")
                for i, user in enumerate(users[:10], 1):
                    print(f"\n   User {i}:")
                    print(f"      Email: {user.get('email', 'N/A')}")
                    print(f"      Full Name: {user.get('full_name', 'N/A')}")
                    print(f"      User Type: {user.get('user_type', 'N/A')}")
                    print(f"      Company ID: {user.get('company_id', 'N/A')}")
                    print(f"      Is Subscribed: {user.get('is_subscribed', 'N/A')}")
                    print(f"      Subscription Plan: {user.get('subscription_plan', 'N/A')}")
                    print(f"      Created At: {user.get('created_at', 'N/A')}")
                    
                    # Check for any business-related fields
                    business_fields = {}
                    for key, value in user.items():
                        if 'business' in key.lower() or 'company' in key.lower():
                            business_fields[key] = value
                    
                    if business_fields:
                        print(f"      Business Fields: {business_fields}")
                
                # Look for users with business-related emails
                print("\n🏢 USERS WITH BUSINESS-RELATED EMAILS:")
                business_email_users = []
                for user in users:
                    email = user.get('email', '')
                    if any(domain in email.lower() for domain in ['corp', 'company', 'business', 'acme', 'enterprise']):
                        business_email_users.append(user)
                
                if business_email_users:
                    for user in business_email_users:
                        print(f"   📧 {user.get('email')}")
                        print(f"      User Type: {user.get('user_type', 'N/A')}")
                        print(f"      Company ID: {user.get('company_id', 'N/A')}")
                        print()
                else:
                    print("   ❌ No users with business-related email domains found")
                
                # Check for users created recently (might be the 3 business users)
                print("\n📅 RECENTLY CREATED USERS (Last 10):")
                sorted_users = sorted(users, key=lambda x: x.get('created_at', ''), reverse=True)
                for i, user in enumerate(sorted_users[:10], 1):
                    print(f"   {i}. {user.get('email')} - {user.get('created_at')} - Type: {user.get('user_type', 'unknown')}")
                
                return True
            else:
                print(f"❌ Failed to get users: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            return False

    def test_business_users_endpoint_with_proper_auth(self):
        """Test business users endpoint with proper admin token"""
        print("\n🔍 TESTING BUSINESS USERS ENDPOINT WITH PROPER AUTH")
        print("=" * 55)
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = requests.get(f"{BASE_URL}/admin/business-users", headers=headers)
            print(f"📡 GET /api/admin/business-users")
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                business_users = data.get("business_users", [])
                print(f"   ✅ Success! Found {len(business_users)} business users")
                
                if business_users:
                    print("\n   📋 BUSINESS USERS RETURNED:")
                    for i, user in enumerate(business_users, 1):
                        print(f"      {i}. {user.get('email')}")
                        print(f"         User Type: {user.get('user_type')}")
                        print(f"         Company: {user.get('company_name', 'N/A')}")
                        print()
                else:
                    print("   ❌ No business users returned from API")
                    
            elif response.status_code == 401:
                print(f"   ❌ Authentication failed: {response.text}")
            else:
                print(f"   ❌ Error: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")

    def check_database_collections(self):
        """Check what collections exist in the database"""
        print("\n🗄️ CHECKING DATABASE COLLECTIONS")
        print("=" * 40)
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Try to access different collections that might contain business data
        collections_to_check = [
            ("companies", "/admin/companies"),
            ("business_payments", "/admin/payments"),
            ("business_signups", "/admin/business-signups"),
        ]
        
        for collection_name, endpoint in collections_to_check:
            try:
                response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
                print(f"📂 {collection_name} ({endpoint})")
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, dict):
                        for key, value in data.items():
                            if isinstance(value, list):
                                print(f"   {key}: {len(value)} items")
                            else:
                                print(f"   {key}: {value}")
                    else:
                        print(f"   Data: {data}")
                elif response.status_code == 404:
                    print(f"   ❌ Endpoint not found")
                else:
                    print(f"   ❌ Error: {response.text}")
                print()
            except Exception as e:
                print(f"   ❌ Exception: {str(e)}")
                print()

    def search_for_business_indicators(self):
        """Search for any indicators of business users in the system"""
        print("\n🔍 SEARCHING FOR BUSINESS INDICATORS")
        print("=" * 45)
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = requests.get(f"{BASE_URL}/admin/users", headers=headers)
            if response.status_code == 200:
                data = response.json()
                users = data.get("users", [])
                
                # Search for various business indicators
                indicators = {
                    "has_company_id": [],
                    "business_subscription": [],
                    "business_email_domains": [],
                    "business_user_type": [],
                    "recent_signups": []
                }
                
                for user in users:
                    # Check for company_id
                    if user.get("company_id"):
                        indicators["has_company_id"].append(user)
                    
                    # Check for business subscription
                    if user.get("subscription_plan") == "business":
                        indicators["business_subscription"].append(user)
                    
                    # Check for business email domains
                    email = user.get("email", "")
                    if any(domain in email.lower() for domain in ["corp", "company", "business", "enterprise", "acme"]):
                        indicators["business_email_domains"].append(user)
                    
                    # Check for business user types
                    user_type = user.get("user_type", "")
                    if "business" in user_type.lower():
                        indicators["business_user_type"].append(user)
                    
                    # Check for recent signups (last 7 days)
                    created_at = user.get("created_at", "")
                    if created_at:
                        try:
                            created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                            days_ago = (datetime.now(created_date.tzinfo) - created_date).days
                            if days_ago <= 7:
                                indicators["recent_signups"].append(user)
                        except:
                            pass
                
                # Report findings
                print("🔍 BUSINESS INDICATORS FOUND:")
                for indicator, users_list in indicators.items():
                    print(f"\n   📊 {indicator.replace('_', ' ').title()}: {len(users_list)} users")
                    if users_list:
                        for user in users_list[:5]:  # Show first 5
                            print(f"      - {user.get('email')} (type: {user.get('user_type', 'unknown')})")
                        if len(users_list) > 5:
                            print(f"      ... and {len(users_list) - 5} more")
                
                return True
            else:
                print(f"❌ Failed to get users: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            return False

    def run_analysis(self):
        """Run complete detailed analysis"""
        print("🚀 Starting Detailed User Analysis")
        print("=" * 50)
        
        if not self.setup_admin_auth():
            print("❌ Failed to authenticate. Aborting analysis.")
            return
        
        self.analyze_user_data_in_detail()
        self.test_business_users_endpoint_with_proper_auth()
        self.check_database_collections()
        self.search_for_business_indicators()
        
        print("\n" + "=" * 50)
        print("🎯 ANALYSIS COMPLETE")
        print("=" * 50)
        print("💡 KEY FINDINGS:")
        print("   1. Check if users have user_type field properly set")
        print("   2. Look for users with business-related email domains")
        print("   3. Check if business signup process is setting user_type correctly")
        print("   4. Verify if company_id is being set during business registration")
        print("=" * 50)

if __name__ == "__main__":
    analyzer = DetailedUserAnalyzer()
    analyzer.run_analysis()