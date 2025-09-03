#!/usr/bin/env python3
"""
Admin Console Mentors Endpoint Issue Testing
Testing the reported issue: "no mentors are being displayed" in admin console
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://mentor-search.preview.emergentagent.com/api"

class AdminMentorsIssueTester:
    def __init__(self):
        self.admin_token = None
        self.test_results = []
        
    def log_result(self, test_name, success, details, error=None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "error": str(error) if error else None,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅" if success else "❌"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        if error:
            print(f"   Error: {error}")
        print()
        
    def setup_admin_auth(self):
        """Setup admin authentication"""
        # Use the initial super admin credentials from the backend
        return self.login_admin()
            
    def login_admin(self):
        """Login with admin credentials"""
        try:
            login_data = {
                "email": "admin@onlymentors.ai", 
                "password": "SuperAdmin2024!"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/admin/login",
                json=login_data,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token")
                self.log_result(
                    "Admin Login", 
                    True, 
                    "Admin login successful"
                )
                return True
            else:
                self.log_result(
                    "Admin Login", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Admin Login", False, "Exception occurred", e)
            return False
            
    def test_admin_mentors_endpoint(self):
        """Test the main admin mentors endpoint that's failing"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            response = requests.get(
                f"{BACKEND_URL}/admin/mentors?limit=100",
                headers=headers,
                timeout=30
            )
            
            status = response.status_code
            
            if status == 200:
                data = response.json()
                mentors = data.get("mentors", [])
                total = data.get("total", 0)
                
                self.log_result(
                    "Admin Mentors Endpoint - Success", 
                    True, 
                    f"Retrieved {len(mentors)} mentors, total: {total}"
                )
                
                # Analyze mentor data structure
                if mentors:
                    sample_mentor = mentors[0]
                    required_fields = ["creator_id", "email", "full_name", "account_name", 
                                     "category", "status", "verification"]
                    missing_fields = []
                    
                    for field in required_fields:
                        if field not in sample_mentor:
                            missing_fields.append(field)
                            
                    if missing_fields:
                        self.log_result(
                            "Admin Mentors Data Structure", 
                            False, 
                            f"Missing fields: {missing_fields}",
                            f"Sample mentor keys: {list(sample_mentor.keys())}"
                        )
                    else:
                        self.log_result(
                            "Admin Mentors Data Structure", 
                            True, 
                            "All required fields present"
                        )
                        
                    # Check verification structure
                    verification = sample_mentor.get("verification", {})
                    if isinstance(verification, dict):
                        if "id_verified" in verification and "bank_verified" in verification:
                            self.log_result(
                                "Admin Mentors Verification Structure", 
                                True, 
                                "Verification object has required fields"
                            )
                        else:
                            self.log_result(
                                "Admin Mentors Verification Structure", 
                                False, 
                                f"Verification missing fields: {list(verification.keys())}"
                            )
                    else:
                        self.log_result(
                            "Admin Mentors Verification Structure", 
                            False, 
                            f"Verification is not object: {type(verification)}"
                        )
                        
                    # Print sample mentor for analysis
                    print(f"📋 Sample Mentor Data Structure:")
                    print(json.dumps(sample_mentor, indent=2, default=str))
                    print()
                        
                else:
                    self.log_result(
                        "Admin Mentors Data Analysis", 
                        False, 
                        "No mentors returned - this matches user report!"
                    )
                    
                return True
                
            elif status == 500:
                error_text = response.text
                self.log_result(
                    "Admin Mentors Endpoint - 500 Error", 
                    False, 
                    "Internal server error - this matches previous findings!",
                    error_text
                )
                
                # Try to parse error details
                try:
                    error_data = response.json()
                    if "detail" in error_data:
                        print(f"🔍 Error Details: {error_data['detail']}")
                except:
                    print(f"🔍 Raw Error Response: {error_text}")
                    
                return False
                
            else:
                error_text = response.text
                self.log_result(
                    "Admin Mentors Endpoint - Other Error", 
                    False, 
                    f"Status: {status}",
                    error_text
                )
                return False
                
        except Exception as e:
            self.log_result("Admin Mentors Endpoint", False, "Exception occurred", e)
            return False
            
    def test_search_mentors_endpoint(self):
        """Test the search mentors endpoint for comparison"""
        try:
            response = requests.get(
                f"{BACKEND_URL}/search/mentors?mentor_type=human&limit=100",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                human_count = data.get("human_count", 0)
                
                self.log_result(
                    "Search Mentors Endpoint", 
                    True, 
                    f"Retrieved {len(results)} human mentors, count: {human_count}"
                )
                
                # Analyze data structure difference
                if results:
                    sample_mentor = results[0]
                    search_fields = list(sample_mentor.keys())
                    self.log_result(
                        "Search Mentors Data Structure", 
                        True, 
                        f"Fields: {search_fields}"
                    )
                    
                    print(f"📋 Sample Search Mentor Data Structure:")
                    print(json.dumps(sample_mentor, indent=2, default=str))
                    print()
                
                return len(results)
            else:
                error_text = response.text
                self.log_result(
                    "Search Mentors Endpoint", 
                    False, 
                    f"Status: {response.status_code}",
                    error_text
                )
                return 0
                
        except Exception as e:
            self.log_result("Search Mentors Endpoint", False, "Exception occurred", e)
            return 0
            
    def test_all_mentors_search(self):
        """Test search for all mentors to see total available"""
        try:
            response = requests.get(
                f"{BACKEND_URL}/search/mentors?mentor_type=all&limit=100",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                ai_count = data.get("ai_count", 0)
                human_count = data.get("human_count", 0)
                
                self.log_result(
                    "All Mentors Search", 
                    True, 
                    f"Total: {len(results)}, AI: {ai_count}, Human: {human_count}"
                )
                
                return len(results), ai_count, human_count
            else:
                self.log_result(
                    "All Mentors Search", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return 0, 0, 0
                
        except Exception as e:
            self.log_result("All Mentors Search", False, "Exception occurred", e)
            return 0, 0, 0
            
    def test_authentication_requirements(self):
        """Test admin authentication requirements"""
        try:
            # Test without authentication
            response = requests.get(f"{BACKEND_URL}/admin/mentors", timeout=30)
            if response.status_code in [401, 403]:
                self.log_result(
                    "Admin Authentication - No Token", 
                    True, 
                    f"Correctly rejected with status {response.status_code}"
                )
            else:
                self.log_result(
                    "Admin Authentication - No Token", 
                    False, 
                    f"Should reject but got status {response.status_code}"
                )
                
            # Test with invalid token
            headers = {"Authorization": "Bearer invalid_token"}
            response = requests.get(
                f"{BACKEND_URL}/admin/mentors", 
                headers=headers,
                timeout=30
            )
            if response.status_code in [401, 403]:
                self.log_result(
                    "Admin Authentication - Invalid Token", 
                    True, 
                    f"Correctly rejected with status {response.status_code}"
                )
            else:
                self.log_result(
                    "Admin Authentication - Invalid Token", 
                    False, 
                    f"Should reject but got status {response.status_code}"
                )
                
        except Exception as e:
            self.log_result("Admin Authentication Tests", False, "Exception occurred", e)
            
    def run_comprehensive_test(self):
        """Run all tests"""
        print("🔍 ADMIN CONSOLE MENTORS ENDPOINT ISSUE TESTING")
        print("=" * 60)
        print("Testing the reported issue: 'no mentors are being displayed' in admin console")
        print()
        
        # Step 1: Setup admin authentication
        print("📋 STEP 1: Admin Authentication Setup")
        admin_ready = self.setup_admin_auth()
        
        if not admin_ready:
            print("❌ Cannot proceed without admin authentication")
            return
            
        print()
        
        # Step 2: Test authentication requirements
        print("📋 STEP 2: Authentication Requirements")
        self.test_authentication_requirements()
        print()
        
        # Step 3: Test the main admin mentors endpoint
        print("📋 STEP 3: Admin Mentors Endpoint Testing (THE MAIN ISSUE)")
        admin_success = self.test_admin_mentors_endpoint()
        print()
        
        # Step 4: Test search mentors for comparison
        print("📋 STEP 4: Search Mentors Comparison")
        search_count = self.test_search_mentors_endpoint()
        print()
        
        # Step 5: Test all mentors to see what's available
        print("📋 STEP 5: All Mentors Analysis")
        total_mentors, ai_count, human_count = self.test_all_mentors_search()
        print()
        
        # Summary
        print("📊 TEST SUMMARY")
        print("=" * 40)
        
        passed = len([r for r in self.test_results if r["success"]])
        total = len(self.test_results)
        
        print(f"Tests Passed: {passed}/{total}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        print()
        
        # Key findings
        print("🔍 KEY FINDINGS:")
        
        if not admin_success:
            print("❌ CRITICAL: Admin mentors endpoint is failing (matches user report)")
            print("   This confirms the issue where 'no mentors are being displayed'")
            
        if search_count > 0:
            print(f"✅ Search API works: Found {search_count} human mentors")
            print("   This suggests the data exists but admin endpoint can't access it")
        else:
            print("❌ No human mentors found in search API either")
            
        if total_mentors > 0:
            print(f"✅ Total mentors available: {total_mentors} (AI: {ai_count}, Human: {human_count})")
        else:
            print("❌ No mentors found in any endpoint")
            
        # Check for specific errors
        admin_errors = [r for r in self.test_results if "Admin Mentors Endpoint" in r["test"] and not r["success"]]
        if admin_errors:
            for error in admin_errors:
                if "500" in error["test"]:
                    print("❌ CONFIRMED: 500 Internal Server Error in admin endpoint")
                    print("   This matches the previous finding about data structure mismatch")
                    print("   The admin endpoint expects fields that don't exist in mentor documents")
                    
        print()
        print("🎯 CONCLUSION:")
        if not admin_success and search_count > 0:
            print("The issue is confirmed: Admin endpoint fails while search endpoint works.")
            print("This indicates a data structure mismatch between what the admin endpoint")
            print("expects and what the mentor signup process creates.")
        elif not admin_success and search_count == 0:
            print("Both admin and search endpoints show no mentors.")
            print("This could indicate no mentors exist or a broader data issue.")
        elif admin_success:
            print("Admin endpoint is working correctly.")
            print("The user's issue may have been resolved or is intermittent.")
            
        print()

def main():
    """Main test execution"""
    tester = AdminMentorsIssueTester()
    tester.run_comprehensive_test()

if __name__ == "__main__":
    main()