#!/usr/bin/env python3
"""
Detailed Verification Structure Testing
Tests the specific data structure mismatch fix for verification fields
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "https://mentor-search.preview.emergentagent.com/api"
TEST_ADMIN_EMAIL = "admin@onlymentors.ai"
TEST_ADMIN_PASSWORD = "SuperAdmin2024!"

class DetailedVerificationTester:
    def __init__(self):
        self.admin_token = None
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
        print()

    def setup_admin_auth(self):
        """Authenticate as admin"""
        print("🔧 Setting up admin authentication...")
        
        try:
            response = requests.post(f"{BASE_URL}/admin/login", json={
                "email": TEST_ADMIN_EMAIL,
                "password": TEST_ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token")
                self.log_result("Admin Authentication", True, f"Admin authenticated successfully")
                return True
            else:
                self.log_result("Admin Authentication", False, f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Exception: {str(e)}")
            return False

    def test_verification_field_mapping(self):
        """Test detailed verification field mapping"""
        print("🧪 Testing detailed verification field mapping...")
        
        if not self.admin_token:
            self.log_result("Verification Field Mapping", False, "No admin token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{BASE_URL}/admin/mentors", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                mentors = data.get("mentors", [])
                
                if len(mentors) > 0:
                    print(f"   Analyzing {len(mentors)} mentors...")
                    
                    verification_analysis = {
                        "total_mentors": len(mentors),
                        "id_verified_true": 0,
                        "id_verified_false": 0,
                        "bank_verified_true": 0,
                        "bank_verified_false": 0,
                        "both_verified": 0,
                        "neither_verified": 0,
                        "sample_verification_structures": []
                    }
                    
                    # Analyze first 5 mentors in detail
                    for i, mentor in enumerate(mentors[:5]):
                        verification = mentor.get("verification", {})
                        id_verified = verification.get("id_verified")
                        bank_verified = verification.get("bank_verified")
                        
                        verification_analysis["sample_verification_structures"].append({
                            "mentor_id": mentor.get("creator_id", "unknown"),
                            "mentor_name": mentor.get("full_name", "unknown"),
                            "verification_structure": verification,
                            "id_verified": id_verified,
                            "bank_verified": bank_verified,
                            "id_verified_type": type(id_verified).__name__,
                            "bank_verified_type": type(bank_verified).__name__
                        })
                    
                    # Count all mentors
                    for mentor in mentors:
                        verification = mentor.get("verification", {})
                        id_verified = verification.get("id_verified")
                        bank_verified = verification.get("bank_verified")
                        
                        if id_verified is True:
                            verification_analysis["id_verified_true"] += 1
                        elif id_verified is False:
                            verification_analysis["id_verified_false"] += 1
                            
                        if bank_verified is True:
                            verification_analysis["bank_verified_true"] += 1
                        elif bank_verified is False:
                            verification_analysis["bank_verified_false"] += 1
                            
                        if id_verified is True and bank_verified is True:
                            verification_analysis["both_verified"] += 1
                        elif id_verified is False and bank_verified is False:
                            verification_analysis["neither_verified"] += 1
                    
                    # Print detailed analysis
                    print(f"   📊 VERIFICATION ANALYSIS:")
                    print(f"   Total Mentors: {verification_analysis['total_mentors']}")
                    print(f"   ID Verified (True): {verification_analysis['id_verified_true']}")
                    print(f"   ID Verified (False): {verification_analysis['id_verified_false']}")
                    print(f"   Bank Verified (True): {verification_analysis['bank_verified_true']}")
                    print(f"   Bank Verified (False): {verification_analysis['bank_verified_false']}")
                    print(f"   Both Verified: {verification_analysis['both_verified']}")
                    print(f"   Neither Verified: {verification_analysis['neither_verified']}")
                    
                    print(f"\n   📋 SAMPLE VERIFICATION STRUCTURES:")
                    for sample in verification_analysis["sample_verification_structures"]:
                        print(f"   Mentor: {sample['mentor_name']}")
                        print(f"   ID Verified: {sample['id_verified']} ({sample['id_verified_type']})")
                        print(f"   Bank Verified: {sample['bank_verified']} ({sample['bank_verified_type']})")
                        print(f"   Full Structure: {sample['verification_structure']}")
                        print()
                    
                    # Check if all verification fields are boolean
                    all_boolean = True
                    for mentor in mentors:
                        verification = mentor.get("verification", {})
                        id_verified = verification.get("id_verified")
                        bank_verified = verification.get("bank_verified")
                        
                        if not isinstance(id_verified, bool) or not isinstance(bank_verified, bool):
                            all_boolean = False
                            break
                    
                    if all_boolean:
                        self.log_result("Verification Field Mapping", True, 
                                      f"All {len(mentors)} mentors have correct boolean verification mapping")
                        return True
                    else:
                        self.log_result("Verification Field Mapping", False, 
                                      f"Some mentors have non-boolean verification fields")
                        return False
                else:
                    self.log_result("Verification Field Mapping", False, "No mentors to analyze")
                    return False
            else:
                self.log_result("Verification Field Mapping", False, 
                              f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Verification Field Mapping", False, f"Exception: {str(e)}")
            return False

    def test_fallback_logic_verification(self):
        """Test that the fallback logic works for both old and new verification structures"""
        print("🧪 Testing fallback logic for verification structures...")
        
        if not self.admin_token:
            self.log_result("Fallback Logic Verification", False, "No admin token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{BASE_URL}/admin/mentors", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                mentors = data.get("mentors", [])
                
                if len(mentors) > 0:
                    print(f"   Testing fallback logic on {len(mentors)} mentors...")
                    
                    # Look for mentors with different verification structures
                    old_structure_count = 0
                    new_structure_count = 0
                    fallback_working = 0
                    
                    for mentor in mentors:
                        verification = mentor.get("verification", {})
                        
                        # Check if this looks like old structure (has id_verified/bank_verified directly)
                        if "id_verified" in verification and "bank_verified" in verification:
                            # Check if these are the original fields or fallback-generated
                            id_verified = verification.get("id_verified")
                            bank_verified = verification.get("bank_verified")
                            
                            if isinstance(id_verified, bool) and isinstance(bank_verified, bool):
                                fallback_working += 1
                        
                        # Check if this has status field (new structure)
                        if "status" in verification:
                            new_structure_count += 1
                        else:
                            old_structure_count += 1
                    
                    print(f"   📊 STRUCTURE ANALYSIS:")
                    print(f"   Mentors with old structure: {old_structure_count}")
                    print(f"   Mentors with new structure: {new_structure_count}")
                    print(f"   Mentors with working fallback: {fallback_working}")
                    
                    if fallback_working == len(mentors):
                        self.log_result("Fallback Logic Verification", True, 
                                      f"Fallback logic working for all {len(mentors)} mentors")
                        return True
                    else:
                        self.log_result("Fallback Logic Verification", False, 
                                      f"Fallback logic only working for {fallback_working}/{len(mentors)} mentors")
                        return False
                else:
                    self.log_result("Fallback Logic Verification", False, "No mentors to test fallback logic")
                    return False
            else:
                self.log_result("Fallback Logic Verification", False, 
                              f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Fallback Logic Verification", False, f"Exception: {str(e)}")
            return False

    def test_no_keyerror_exceptions(self):
        """Test that no KeyError exceptions occur when accessing verification fields"""
        print("🧪 Testing for KeyError exceptions...")
        
        if not self.admin_token:
            self.log_result("No KeyError Exceptions", False, "No admin token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Make multiple requests to ensure stability
            for i in range(3):
                response = requests.get(f"{BASE_URL}/admin/mentors?limit=50", headers=headers)
                
                if response.status_code != 200:
                    self.log_result("No KeyError Exceptions", False, 
                                  f"Request {i+1} failed with status: {response.status_code}")
                    return False
                
                data = response.json()
                mentors = data.get("mentors", [])
                
                # Verify all mentors have the expected structure
                for mentor in mentors:
                    verification = mentor.get("verification", {})
                    if "id_verified" not in verification or "bank_verified" not in verification:
                        self.log_result("No KeyError Exceptions", False, 
                                      f"Missing verification fields in mentor: {mentor.get('creator_id')}")
                        return False
            
            self.log_result("No KeyError Exceptions", True, 
                          f"All 3 requests successful, no KeyError exceptions detected")
            return True
                
        except Exception as e:
            self.log_result("No KeyError Exceptions", False, f"Exception: {str(e)}")
            return False

    def run_detailed_tests(self):
        """Run detailed verification tests"""
        print("🚀 Starting Detailed Verification Structure Testing...")
        print("=" * 70)
        
        # Setup
        if not self.setup_admin_auth():
            print("❌ Cannot proceed without admin authentication")
            return False
        
        # Detailed tests
        tests = [
            self.test_verification_field_mapping,
            self.test_fallback_logic_verification,
            self.test_no_keyerror_exceptions
        ]
        
        # Run tests
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
        
        # Summary
        print("=" * 70)
        print(f"🏁 DETAILED VERIFICATION TEST SUMMARY")
        print(f"Tests Passed: {passed}/{total}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("🎉 ALL DETAILED TESTS PASSED - Verification structure fix is working perfectly!")
        else:
            print("⚠️  Some detailed tests failed - Verification structure may have issues")
        
        return passed == total

def main():
    """Main test execution"""
    tester = DetailedVerificationTester()
    success = tester.run_detailed_tests()
    
    if success:
        print("\n✅ DETAILED VERIFICATION STRUCTURE FIX VERIFICATION COMPLETE!")
    else:
        print("\n❌ DETAILED VERIFICATION STRUCTURE FIX VERIFICATION FAILED!")
    
    return success

if __name__ == "__main__":
    main()