#!/usr/bin/env python3
"""
Business Mentor Functionality Testing
Tests complete business mentor creation, authentication, and integration
"""

import requests
import json
import time
import uuid
from datetime import datetime

# Configuration
BASE_URL = "https://enterprise-coach.preview.emergentagent.com/api"

class BusinessMentorTester:
    def __init__(self):
        self.business_employee_token = None
        self.business_employee_id = None
        self.creator_id = None
        self.company_id = None
        self.results = []
        
    def log_result(self, test_name, success, details="", response_data=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if not success and response_data:
            print(f"   Response: {response_data}")
        print()

    def setup_test_data(self):
        """Setup test company and business employee"""
        print("🔧 Setting up test data...")
        
        try:
            # Setup business test data
            response = requests.post(f"{BASE_URL}/business/setup-test-data")
            
            if response.status_code == 200:
                data = response.json()
                self.company_id = data.get("company_id")
                self.log_result(
                    "Business Test Data Setup",
                    True,
                    f"Company ID: {self.company_id}, Categories: {data.get('categories_created')}, Mentors: {data.get('mentor_assignments')}"
                )
                return True
            else:
                self.log_result(
                    "Business Test Data Setup",
                    False,
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Business Test Data Setup", False, f"Exception: {str(e)}")
            return False

    def create_business_employee_account(self):
        """Create business employee account"""
        print("👤 Creating business employee account...")
        
        test_email = f"test-{uuid.uuid4().hex[:8]}@acme-corp.com"
        
        try:
            # Create business employee account
            signup_data = {
                "email": test_email,
                "password": "TestPass123!",
                "full_name": "John Business Employee",
                "business_slug": "acme-corp",
                "department_code": "engineering"
            }
            
            response = requests.post(f"{BASE_URL}/auth/business/signup-test", json=signup_data)
            
            if response.status_code == 200:
                data = response.json()
                self.business_employee_token = data["token"]
                self.business_employee_id = data["user"]["user_id"]
                self.company_id = data["user"]["company_id"]
                
                self.log_result(
                    "Business Employee Account Creation",
                    True,
                    f"Email: {test_email}, User ID: {self.business_employee_id}, Company ID: {self.company_id}"
                )
                return True
            else:
                self.log_result(
                    "Business Employee Account Creation",
                    False,
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Business Employee Account Creation", False, f"Exception: {str(e)}")
            return False

    def test_become_mentor_endpoint(self):
        """Test business employee becoming a mentor"""
        print("🧑‍🏫 Testing become mentor functionality...")
        
        try:
            headers = {"Authorization": f"Bearer {self.business_employee_token}"}
            response = requests.post(f"{BASE_URL}/users/become-mentor", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.creator_id = data.get("creator_id")
                
                # Verify business mentor specific fields
                success = True
                details = []
                
                if data.get("success"):
                    details.append("✅ Success flag: true")
                else:
                    success = False
                    details.append("❌ Success flag: false")
                
                if self.creator_id:
                    details.append(f"✅ Creator ID generated: {self.creator_id}")
                else:
                    success = False
                    details.append("❌ No creator ID returned")
                
                mentor_profile = data.get("mentor_profile", {})
                if mentor_profile.get("is_business_mentor"):
                    details.append("✅ Business mentor flag: true")
                else:
                    details.append("⚠️ Business mentor flag not explicitly set")
                
                self.log_result(
                    "Business Employee Become Mentor",
                    success,
                    "; ".join(details),
                    data
                )
                return success
            else:
                self.log_result(
                    "Business Employee Become Mentor",
                    False,
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Business Employee Become Mentor", False, f"Exception: {str(e)}")
            return False

    def verify_business_mentor_profile(self):
        """Verify business mentor profile has correct properties"""
        print("🔍 Verifying business mentor profile...")
        
        if not self.creator_id:
            self.log_result("Business Mentor Profile Verification", False, "No creator ID available")
            return False
        
        try:
            # We'll verify through the search API since we don't have direct creator profile endpoint
            headers = {"Authorization": f"Bearer {self.business_employee_token}"}
            response = requests.get(f"{BASE_URL}/search/mentors?mentor_type=human", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                human_mentors = data.get("results", [])
                
                # Find our business mentor
                business_mentor = None
                for mentor in human_mentors:
                    if mentor.get("id") == self.creator_id:
                        business_mentor = mentor
                        break
                
                if business_mentor:
                    success = True
                    details = []
                    
                    # Check mentor type
                    if business_mentor.get("mentor_type") == "human":
                        details.append("✅ Mentor type: human")
                    else:
                        success = False
                        details.append(f"❌ Mentor type: {business_mentor.get('mentor_type')}")
                    
                    # Check is_ai_mentor flag
                    if business_mentor.get("is_ai_mentor") == False:
                        details.append("✅ is_ai_mentor: false")
                    else:
                        success = False
                        details.append(f"❌ is_ai_mentor: {business_mentor.get('is_ai_mentor')}")
                    
                    # Check monthly price (should be 0.0 for business mentors)
                    monthly_price = business_mentor.get("monthly_price", 0)
                    if monthly_price == 0.0:
                        details.append("✅ Monthly price: 0.0 (no revenue sharing)")
                    else:
                        details.append(f"⚠️ Monthly price: {monthly_price} (expected 0.0)")
                    
                    # Check tier information
                    tier = business_mentor.get("tier", "")
                    if tier:
                        details.append(f"✅ Tier: {tier}")
                    
                    self.log_result(
                        "Business Mentor Profile Verification",
                        success,
                        "; ".join(details),
                        business_mentor
                    )
                    return success
                else:
                    self.log_result(
                        "Business Mentor Profile Verification",
                        False,
                        "Business mentor not found in human mentors search",
                        data
                    )
                    return False
            else:
                self.log_result(
                    "Business Mentor Profile Verification",
                    False,
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Business Mentor Profile Verification", False, f"Exception: {str(e)}")
            return False

    def test_business_mentor_authentication(self):
        """Test authentication returns proper business mentor flags"""
        print("🔐 Testing business mentor authentication...")
        
        try:
            # Login with business employee credentials
            login_data = {
                "email": f"test@acme-corp.com",  # Use existing test account
                "password": "TestPass123!"
            }
            
            response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                user = data.get("user", {})
                
                success = True
                details = []
                
                # Check user_type
                user_type = user.get("user_type")
                if user_type == "business_employee":
                    details.append("✅ User type: business_employee")
                else:
                    details.append(f"⚠️ User type: {user_type}")
                
                # Check is_mentor flag
                is_mentor = user.get("is_mentor")
                if is_mentor:
                    details.append("✅ is_mentor: true")
                else:
                    details.append(f"⚠️ is_mentor: {is_mentor}")
                
                # Check company_id
                company_id = user.get("company_id")
                if company_id:
                    details.append(f"✅ Company ID: {company_id}")
                else:
                    details.append("⚠️ No company ID")
                
                self.log_result(
                    "Business Mentor Authentication",
                    success,
                    "; ".join(details),
                    user
                )
                return success
            else:
                self.log_result(
                    "Business Mentor Authentication",
                    False,
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Business Mentor Authentication", False, f"Exception: {str(e)}")
            return False

    def test_business_mentor_integration(self):
        """Test business mentor integration with assignment system"""
        print("🔗 Testing business mentor integration...")
        
        try:
            headers = {"Authorization": f"Bearer {self.business_employee_token}"}
            response = requests.get(f"{BASE_URL}/business/employee/mentors", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                mentors = data.get("results", [])
                
                success = True
                details = []
                
                # Check if we have company-assigned mentors
                if len(mentors) > 0:
                    details.append(f"✅ Found {len(mentors)} company-assigned mentors")
                    
                    # Check mentor types
                    ai_mentors = [m for m in mentors if m.get("type") == "ai"]
                    human_mentors = [m for m in mentors if m.get("type") == "human"]
                    
                    details.append(f"✅ AI mentors: {len(ai_mentors)}")
                    details.append(f"✅ Human mentors: {len(human_mentors)}")
                    
                    # Check company_id in response
                    company_id = data.get("company_id")
                    if company_id == self.company_id:
                        details.append(f"✅ Company ID matches: {company_id}")
                    else:
                        success = False
                        details.append(f"❌ Company ID mismatch: {company_id} vs {self.company_id}")
                    
                else:
                    success = False
                    details.append("❌ No company-assigned mentors found")
                
                self.log_result(
                    "Business Mentor Integration",
                    success,
                    "; ".join(details),
                    data
                )
                return success
            else:
                self.log_result(
                    "Business Mentor Integration",
                    False,
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Business Mentor Integration", False, f"Exception: {str(e)}")
            return False

    def test_business_mentor_no_revenue_sharing(self):
        """Test that business mentors have no revenue sharing"""
        print("💰 Testing business mentor revenue sharing settings...")
        
        try:
            # Test through search API to verify monthly_price
            response = requests.get(f"{BASE_URL}/search/mentors?mentor_type=human")
            
            if response.status_code == 200:
                data = response.json()
                human_mentors = data.get("results", [])
                
                if len(human_mentors) > 0:
                    success = True
                    details = []
                    
                    business_mentors_count = 0
                    for mentor in human_mentors:
                        monthly_price = mentor.get("monthly_price", 0)
                        allow_tips = mentor.get("allow_tips", True)
                        
                        # Check if this could be a business mentor (price = 0)
                        if monthly_price == 0.0:
                            business_mentors_count += 1
                            details.append(f"✅ Business mentor found: {mentor.get('name')} - Price: ${monthly_price}")
                            
                            if not allow_tips:
                                details.append(f"✅ Tips disabled for {mentor.get('name')}")
                            else:
                                details.append(f"⚠️ Tips enabled for {mentor.get('name')} (may be regular mentor)")
                    
                    if business_mentors_count > 0:
                        details.append(f"✅ Found {business_mentors_count} mentors with no revenue sharing")
                    else:
                        success = False
                        details.append("❌ No business mentors with 0.0 pricing found")
                    
                    self.log_result(
                        "Business Mentor No Revenue Sharing",
                        success,
                        "; ".join(details),
                        {"business_mentors_count": business_mentors_count, "total_human_mentors": len(human_mentors)}
                    )
                    return success
                else:
                    self.log_result(
                        "Business Mentor No Revenue Sharing",
                        False,
                        "No human mentors found to test revenue sharing",
                        data
                    )
                    return False
            else:
                self.log_result(
                    "Business Mentor No Revenue Sharing",
                    False,
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Business Mentor No Revenue Sharing", False, f"Exception: {str(e)}")
            return False

    def run_comprehensive_test(self):
        """Run all business mentor tests"""
        print("🚀 Starting Business Mentor Comprehensive Testing")
        print("=" * 60)
        
        # Test sequence
        tests = [
            ("Setup Test Data", self.setup_test_data),
            ("Create Business Employee Account", self.create_business_employee_account),
            ("Test Become Mentor Endpoint", self.test_become_mentor_endpoint),
            ("Verify Business Mentor Profile", self.verify_business_mentor_profile),
            ("Test Business Mentor Authentication", self.test_business_mentor_authentication),
            ("Test Business Mentor Integration", self.test_business_mentor_integration),
            ("Test No Revenue Sharing", self.test_business_mentor_no_revenue_sharing)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n📋 Running: {test_name}")
            print("-" * 40)
            
            if test_func():
                passed += 1
            
            time.sleep(1)  # Brief pause between tests
        
        # Summary
        print("\n" + "=" * 60)
        print("🎯 BUSINESS MENTOR TESTING SUMMARY")
        print("=" * 60)
        
        success_rate = (passed / total) * 100
        print(f"Tests Passed: {passed}/{total} ({success_rate:.1f}%)")
        
        print(f"\n📊 Detailed Results:")
        for result in self.results:
            print(f"{result['status']}: {result['test']}")
            if result['details']:
                print(f"   {result['details']}")
        
        if success_rate >= 80:
            print(f"\n🎉 BUSINESS MENTOR SYSTEM FUNCTIONAL! ({success_rate:.1f}% success rate)")
        elif success_rate >= 60:
            print(f"\n⚠️ BUSINESS MENTOR SYSTEM PARTIALLY FUNCTIONAL ({success_rate:.1f}% success rate)")
        else:
            print(f"\n🚨 BUSINESS MENTOR SYSTEM NEEDS ATTENTION ({success_rate:.1f}% success rate)")
        
        return success_rate >= 80

if __name__ == "__main__":
    tester = BusinessMentorTester()
    tester.run_comprehensive_test()