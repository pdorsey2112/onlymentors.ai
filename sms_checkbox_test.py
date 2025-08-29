#!/usr/bin/env python3
"""
SMS Checkbox Backend Testing - OnlyMentors.ai
Focus: Test SMS notifications checkbox saving issue specifically
"""

import requests
import sys
import json
import time
from datetime import datetime

class SMSCheckboxTester:
    def __init__(self, base_url="https://mentor-marketplace.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.user_data = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test_result(self, test_name, success, details=None):
        """Log test result for analysis"""
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        if endpoint == "":
            url = self.base_url
        elif endpoint.startswith('api/'):
            url = f"{self.base_url}/{endpoint}"
        else:
            url = f"{self.base_url}/api/{endpoint}"
            
        test_headers = {'Content-Type': 'application/json'}
        
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'
        
        if headers:
            test_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        if data:
            print(f"   Data: {json.dumps(data, indent=2)}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=30)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)}")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {json.dumps(error_data, indent=2)}")
                    return False, error_data
                except:
                    print(f"   Error: {response.text}")
                    return False, {"error": response.text}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {"exception": str(e)}

    def setup_test_user(self):
        """Create and login test user for SMS testing"""
        print(f"\n{'='*60}")
        print("🔧 SETTING UP TEST USER FOR SMS TESTING")
        print(f"{'='*60}")
        
        # Generate unique test data
        timestamp = datetime.now().strftime('%H%M%S')
        test_email = f"sms_test_{timestamp}@example.com"
        test_password = "TestPass123!"
        test_name = "SMS Test User"
        
        print(f"Creating test user: {test_email}")
        
        # Create test user
        success, response = self.run_test(
            "Create Test User",
            "POST",
            "api/auth/signup",
            200,
            data={
                "email": test_email,
                "password": test_password,
                "full_name": test_name
            }
        )
        
        if success and 'token' in response:
            self.token = response['token']
            self.user_data = response['user']
            print(f"✅ Test user created successfully")
            self.log_test_result("setup_user", True, {"email": test_email})
            return True
        else:
            print(f"❌ Failed to create test user")
            self.log_test_result("setup_user", False, response)
            return False

    def test_profile_update_with_sms_and_phone(self):
        """Test 1: Profile update with SMS=true AND phone number"""
        print(f"\n📱 TEST 1: Profile Update with SMS=true AND Phone Number")
        
        profile_data = {
            "full_name": "SMS Test User Updated",
            "phone_number": "+1234567890",
            "communication_preferences": {
                "email": True,
                "sms": True,
                "notifications": True
            }
        }
        
        success, response = self.run_test(
            "Profile Update - SMS=true WITH Phone",
            "PUT",
            "api/user/profile",
            200,
            data=profile_data
        )
        
        if success:
            # Verify the update was applied correctly
            profile = response.get('profile', {})
            comm_prefs = profile.get('communication_preferences', {})
            
            print(f"   📋 Verification:")
            print(f"   Phone Number: {profile.get('phone_number')}")
            print(f"   SMS Preference: {comm_prefs.get('sms')}")
            print(f"   Email Preference: {comm_prefs.get('email')}")
            print(f"   Notifications: {comm_prefs.get('notifications')}")
            
            # Check if SMS preference was saved correctly
            sms_saved_correctly = comm_prefs.get('sms') == True
            phone_saved_correctly = profile.get('phone_number') == "+1234567890"
            
            if sms_saved_correctly and phone_saved_correctly:
                print(f"   ✅ SMS preference and phone number saved correctly")
                self.log_test_result("sms_with_phone", True, {
                    "sms_saved": sms_saved_correctly,
                    "phone_saved": phone_saved_correctly,
                    "profile": profile
                })
                return True
            else:
                print(f"   ❌ SMS preference or phone number not saved correctly")
                print(f"      SMS saved: {sms_saved_correctly} (expected: True)")
                print(f"      Phone saved: {phone_saved_correctly} (expected: True)")
                self.log_test_result("sms_with_phone", False, {
                    "sms_saved": sms_saved_correctly,
                    "phone_saved": phone_saved_correctly,
                    "profile": profile
                })
                return False
        else:
            self.log_test_result("sms_with_phone", False, response)
            return False

    def test_profile_update_with_sms_no_phone(self):
        """Test 2: Profile update with SMS=true WITHOUT phone number"""
        print(f"\n📱 TEST 2: Profile Update with SMS=true WITHOUT Phone Number")
        
        profile_data = {
            "full_name": "SMS Test User No Phone",
            "phone_number": "",  # Empty phone number
            "communication_preferences": {
                "email": True,
                "sms": True,
                "notifications": True
            }
        }
        
        success, response = self.run_test(
            "Profile Update - SMS=true WITHOUT Phone",
            "PUT",
            "api/user/profile",
            200,  # We'll check if this should be 400 based on validation
            data=profile_data
        )
        
        if success:
            # Check if backend allowed SMS=true without phone (might be validation issue)
            profile = response.get('profile', {})
            comm_prefs = profile.get('communication_preferences', {})
            
            print(f"   📋 Verification:")
            print(f"   Phone Number: '{profile.get('phone_number')}'")
            print(f"   SMS Preference: {comm_prefs.get('sms')}")
            
            sms_preference = comm_prefs.get('sms')
            phone_number = profile.get('phone_number', '')
            
            if sms_preference == True and not phone_number:
                print(f"   ⚠️  VALIDATION ISSUE: SMS=true allowed without phone number")
                self.log_test_result("sms_without_phone", False, {
                    "issue": "SMS enabled without phone number - validation missing",
                    "sms_preference": sms_preference,
                    "phone_number": phone_number
                })
                return False
            elif sms_preference == False and not phone_number:
                print(f"   ✅ Backend correctly disabled SMS when no phone number")
                self.log_test_result("sms_without_phone", True, {
                    "validation_working": True,
                    "sms_preference": sms_preference,
                    "phone_number": phone_number
                })
                return True
            else:
                print(f"   ❓ Unexpected behavior")
                self.log_test_result("sms_without_phone", False, {
                    "unexpected_behavior": True,
                    "sms_preference": sms_preference,
                    "phone_number": phone_number
                })
                return False
        else:
            # Check if it's a validation error (which would be correct)
            if response.get('detail') and 'phone' in str(response.get('detail')).lower():
                print(f"   ✅ Backend correctly rejected SMS=true without phone number")
                print(f"   Validation message: {response.get('detail')}")
                self.log_test_result("sms_without_phone", True, {
                    "validation_working": True,
                    "error_message": response.get('detail')
                })
                return True
            else:
                print(f"   ❌ Unexpected error response")
                self.log_test_result("sms_without_phone", False, response)
                return False

    def test_data_persistence_verification(self):
        """Test 3: Data Persistence - Save → Retrieve Cycle"""
        print(f"\n💾 TEST 3: Data Persistence Verification (Save → Retrieve)")
        
        # First, update profile with SMS preferences
        profile_data = {
            "full_name": "SMS Persistence Test",
            "phone_number": "+1987654321",
            "communication_preferences": {
                "email": True,
                "sms": True,
                "notifications": False
            }
        }
        
        print(f"   Step 1: Saving profile with SMS preferences...")
        success_save, save_response = self.run_test(
            "Save Profile with SMS",
            "PUT",
            "api/user/profile",
            200,
            data=profile_data
        )
        
        if not success_save:
            print(f"   ❌ Failed to save profile")
            self.log_test_result("data_persistence", False, {"step": "save", "response": save_response})
            return False
        
        # Wait a moment to ensure data is persisted
        time.sleep(1)
        
        print(f"   Step 2: Retrieving profile to verify persistence...")
        success_get, get_response = self.run_test(
            "Retrieve Profile",
            "GET",
            "api/user/profile",
            200
        )
        
        if not success_get:
            print(f"   ❌ Failed to retrieve profile")
            self.log_test_result("data_persistence", False, {"step": "retrieve", "response": get_response})
            return False
        
        # Compare saved vs retrieved data
        saved_profile = save_response.get('profile', {})
        retrieved_profile = get_response
        
        print(f"   📋 Persistence Verification:")
        print(f"   Saved Phone: {saved_profile.get('phone_number')}")
        print(f"   Retrieved Phone: {retrieved_profile.get('phone_number')}")
        
        saved_comm_prefs = saved_profile.get('communication_preferences', {})
        # Check if retrieved profile has communication_preferences
        retrieved_comm_prefs = retrieved_profile.get('communication_preferences', {})
        
        print(f"   Saved SMS: {saved_comm_prefs.get('sms')}")
        print(f"   Retrieved SMS: {retrieved_comm_prefs.get('sms')}")
        print(f"   Saved Email: {saved_comm_prefs.get('email')}")
        print(f"   Retrieved Email: {retrieved_comm_prefs.get('email')}")
        
        # Verify persistence
        phone_persisted = saved_profile.get('phone_number') == retrieved_profile.get('phone_number')
        sms_persisted = saved_comm_prefs.get('sms') == retrieved_comm_prefs.get('sms')
        email_persisted = saved_comm_prefs.get('email') == retrieved_comm_prefs.get('email')
        
        if phone_persisted and sms_persisted and email_persisted:
            print(f"   ✅ All data persisted correctly")
            self.log_test_result("data_persistence", True, {
                "phone_persisted": phone_persisted,
                "sms_persisted": sms_persisted,
                "email_persisted": email_persisted
            })
            return True
        else:
            print(f"   ❌ Data persistence issues detected")
            print(f"      Phone persisted: {phone_persisted}")
            print(f"      SMS persisted: {sms_persisted}")
            print(f"      Email persisted: {email_persisted}")
            self.log_test_result("data_persistence", False, {
                "phone_persisted": phone_persisted,
                "sms_persisted": sms_persisted,
                "email_persisted": email_persisted,
                "saved_data": saved_profile,
                "retrieved_data": retrieved_profile
            })
            return False

    def test_different_phone_formats(self):
        """Test 4: Different Phone Number Formats"""
        print(f"\n📞 TEST 4: Different Phone Number Formats with SMS")
        
        phone_formats = [
            "+1234567890",      # International format
            "1234567890",       # US format without +
            "(123) 456-7890",   # US format with parentheses
            "123-456-7890",     # US format with dashes
            "+44 20 7946 0958", # UK format
        ]
        
        format_results = []
        
        for i, phone_format in enumerate(phone_formats):
            print(f"\n   Testing format {i+1}: '{phone_format}'")
            
            profile_data = {
                "full_name": f"Phone Format Test {i+1}",
                "phone_number": phone_format,
                "communication_preferences": {
                    "email": True,
                    "sms": True,
                    "notifications": True
                }
            }
            
            success, response = self.run_test(
                f"Phone Format {i+1}: {phone_format}",
                "PUT",
                "api/user/profile",
                200,
                data=profile_data
            )
            
            if success:
                profile = response.get('profile', {})
                saved_phone = profile.get('phone_number')
                sms_enabled = profile.get('communication_preferences', {}).get('sms')
                
                format_result = {
                    "format": phone_format,
                    "saved_as": saved_phone,
                    "sms_enabled": sms_enabled,
                    "success": True
                }
                
                print(f"      ✅ Accepted - Saved as: '{saved_phone}', SMS: {sms_enabled}")
            else:
                format_result = {
                    "format": phone_format,
                    "success": False,
                    "error": response.get('detail', 'Unknown error')
                }
                print(f"      ❌ Rejected - Error: {response.get('detail', 'Unknown error')}")
            
            format_results.append(format_result)
        
        # Analyze results
        accepted_formats = [r for r in format_results if r['success']]
        rejected_formats = [r for r in format_results if not r['success']]
        
        print(f"\n   📊 Phone Format Analysis:")
        print(f"   Accepted formats: {len(accepted_formats)}/{len(phone_formats)}")
        print(f"   Rejected formats: {len(rejected_formats)}/{len(phone_formats)}")
        
        # At least basic formats should work
        basic_formats_working = any(r['success'] and r['format'] in ["+1234567890", "1234567890"] for r in format_results)
        
        if basic_formats_working:
            print(f"   ✅ Basic phone formats working with SMS")
            self.log_test_result("phone_formats", True, format_results)
            return True
        else:
            print(f"   ❌ Basic phone formats not working")
            self.log_test_result("phone_formats", False, format_results)
            return False

    def test_backend_validation_logic(self):
        """Test 5: Backend Validation Logic"""
        print(f"\n🔍 TEST 5: Backend Validation Logic")
        
        validation_tests = []
        
        # Test 1: SMS=true with valid phone
        test1_data = {
            "phone_number": "+1555123456",
            "communication_preferences": {"email": True, "sms": True, "notifications": True}
        }
        
        success1, response1 = self.run_test(
            "Validation: SMS=true + Valid Phone",
            "PUT",
            "api/user/profile",
            200,
            data=test1_data
        )
        
        validation_tests.append({
            "test": "sms_true_valid_phone",
            "expected": "accept",
            "actual": "accept" if success1 else "reject",
            "success": success1,
            "response": response1
        })
        
        # Test 2: SMS=true with empty phone
        test2_data = {
            "phone_number": "",
            "communication_preferences": {"email": True, "sms": True, "notifications": True}
        }
        
        success2, response2 = self.run_test(
            "Validation: SMS=true + Empty Phone",
            "PUT",
            "api/user/profile",
            400,  # Should be rejected
            data=test2_data
        )
        
        # If it returns 200, check if SMS was automatically disabled
        if not success2:
            # Try with 200 to see if it auto-corrects
            success2_alt, response2_alt = self.run_test(
                "Validation: SMS=true + Empty Phone (Auto-correct)",
                "PUT",
                "api/user/profile",
                200,
                data=test2_data
            )
            
            if success2_alt:
                # Check if SMS was disabled
                profile = response2_alt.get('profile', {})
                sms_disabled = not profile.get('communication_preferences', {}).get('sms', True)
                if sms_disabled:
                    success2 = True  # Auto-correction is acceptable
                    response2 = response2_alt
        
        validation_tests.append({
            "test": "sms_true_empty_phone",
            "expected": "reject_or_auto_correct",
            "actual": "reject" if not success2 else "auto_correct",
            "success": success2,
            "response": response2
        })
        
        # Test 3: SMS=false with empty phone (should be fine)
        test3_data = {
            "phone_number": "",
            "communication_preferences": {"email": True, "sms": False, "notifications": True}
        }
        
        success3, response3 = self.run_test(
            "Validation: SMS=false + Empty Phone",
            "PUT",
            "api/user/profile",
            200,
            data=test3_data
        )
        
        validation_tests.append({
            "test": "sms_false_empty_phone",
            "expected": "accept",
            "actual": "accept" if success3 else "reject",
            "success": success3,
            "response": response3
        })
        
        # Analyze validation logic
        print(f"\n   📋 Validation Logic Analysis:")
        for test in validation_tests:
            status = "✅ PASS" if test['success'] else "❌ FAIL"
            print(f"   {test['test']}: {status} ({test['actual']})")
        
        validation_working = sum(t['success'] for t in validation_tests) >= 2
        
        if validation_working:
            print(f"   ✅ Backend validation logic working correctly")
            self.log_test_result("validation_logic", True, validation_tests)
            return True
        else:
            print(f"   ❌ Backend validation logic has issues")
            self.log_test_result("validation_logic", False, validation_tests)
            return False

    def test_pydantic_model_validation(self):
        """Test 6: UserProfileUpdate Pydantic Model Testing"""
        print(f"\n🏗️ TEST 6: UserProfileUpdate Pydantic Model Validation")
        
        model_tests = []
        
        # Test valid communication_preferences structure
        valid_data = {
            "full_name": "Model Test User",
            "phone_number": "+1234567890",
            "communication_preferences": {
                "email": True,
                "sms": True,
                "notifications": False
            }
        }
        
        success1, response1 = self.run_test(
            "Model: Valid Structure",
            "PUT",
            "api/user/profile",
            200,
            data=valid_data
        )
        
        model_tests.append({"test": "valid_structure", "success": success1})
        
        # Test invalid communication_preferences (not a dict)
        invalid_data1 = {
            "full_name": "Model Test User",
            "communication_preferences": "invalid_string"
        }
        
        success2, response2 = self.run_test(
            "Model: Invalid Comm Prefs Type",
            "PUT",
            "api/user/profile",
            422,  # Pydantic validation error
            data=invalid_data1
        )
        
        model_tests.append({"test": "invalid_comm_prefs_type", "success": success2})
        
        # Test missing required fields (should still work as all fields are optional)
        minimal_data = {
            "communication_preferences": {
                "sms": True
            }
        }
        
        success3, response3 = self.run_test(
            "Model: Minimal Valid Data",
            "PUT",
            "api/user/profile",
            200,
            data=minimal_data
        )
        
        model_tests.append({"test": "minimal_data", "success": success3})
        
        # Test extra fields (should be ignored)
        extra_fields_data = {
            "full_name": "Model Test User",
            "communication_preferences": {
                "email": True,
                "sms": True,
                "extra_field": "should_be_ignored"
            },
            "unknown_field": "should_be_ignored"
        }
        
        success4, response4 = self.run_test(
            "Model: Extra Fields",
            "PUT",
            "api/user/profile",
            200,
            data=extra_fields_data
        )
        
        model_tests.append({"test": "extra_fields", "success": success4})
        
        # Analyze model validation
        print(f"\n   📋 Pydantic Model Analysis:")
        for test in model_tests:
            status = "✅ PASS" if test['success'] else "❌ FAIL"
            print(f"   {test['test']}: {status}")
        
        model_working = sum(t['success'] for t in model_tests) >= 3
        
        if model_working:
            print(f"   ✅ UserProfileUpdate model validation working")
            self.log_test_result("pydantic_model", True, model_tests)
            return True
        else:
            print(f"   ❌ UserProfileUpdate model validation issues")
            self.log_test_result("pydantic_model", False, model_tests)
            return False

    def run_comprehensive_sms_test(self):
        """Run all SMS checkbox tests"""
        print(f"\n{'='*80}")
        print("📱 COMPREHENSIVE SMS CHECKBOX BACKEND TESTING")
        print(f"{'='*80}")
        
        # Setup test user
        if not self.setup_test_user():
            print("❌ Cannot proceed without test user")
            return False
        
        # Run all SMS-specific tests
        test_results = {
            "sms_with_phone": self.test_profile_update_with_sms_and_phone(),
            "sms_without_phone": self.test_profile_update_with_sms_no_phone(),
            "data_persistence": self.test_data_persistence_verification(),
            "phone_formats": self.test_different_phone_formats(),
            "validation_logic": self.test_backend_validation_logic(),
            "pydantic_model": self.test_pydantic_model_validation()
        }
        
        return test_results

    def generate_final_report(self, test_results):
        """Generate comprehensive final report"""
        print(f"\n{'='*80}")
        print("📊 SMS CHECKBOX TESTING - FINAL REPORT")
        print(f"{'='*80}")
        
        passed_tests = sum(test_results.values())
        total_tests = len(test_results)
        
        print(f"\n🔍 Individual Test Results:")
        for test_name, passed in test_results.items():
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"   {test_name.replace('_', ' ').title()}: {status}")
        
        print(f"\n📈 Overall Statistics:")
        print(f"   Total API Calls: {self.tests_run}")
        print(f"   Successful API Calls: {self.tests_passed}")
        print(f"   API Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        print(f"   SMS Tests Passed: {passed_tests}/{total_tests}")
        print(f"   SMS Test Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Identify the root cause
        print(f"\n🔍 ROOT CAUSE ANALYSIS:")
        
        if not test_results.get("sms_with_phone"):
            print("❌ CRITICAL: SMS checkbox not saving even WITH phone number")
            print("   → This indicates a backend data handling issue")
            
        if not test_results.get("data_persistence"):
            print("❌ CRITICAL: Data persistence issues detected")
            print("   → SMS preferences not being stored in database correctly")
            
        if not test_results.get("validation_logic"):
            print("❌ ISSUE: Backend validation logic problems")
            print("   → SMS=true allowed without phone number validation")
            
        if not test_results.get("pydantic_model"):
            print("❌ ISSUE: Pydantic model validation problems")
            print("   → UserProfileUpdate model not handling communication_preferences correctly")
        
        # Determine overall assessment
        critical_tests = ["sms_with_phone", "data_persistence"]
        critical_passed = sum(test_results.get(test, False) for test in critical_tests)
        
        if critical_passed == len(critical_tests) and passed_tests >= 4:
            print(f"\n🎉 SMS CHECKBOX FUNCTIONALITY: ✅ WORKING CORRECTLY!")
            print("   The SMS checkbox saving issue appears to be resolved.")
            return True
        else:
            print(f"\n❌ SMS CHECKBOX FUNCTIONALITY: ISSUES DETECTED!")
            
            if not test_results.get("sms_with_phone"):
                print("   🚨 PRIMARY ISSUE: SMS checkbox not saving with phone number")
                print("      → Check UserProfileUpdate model and database update logic")
                
            if not test_results.get("data_persistence"):
                print("   🚨 PRIMARY ISSUE: Communication preferences not persisting")
                print("      → Check database schema and update operations")
                
            if not test_results.get("validation_logic"):
                print("   ⚠️  SECONDARY ISSUE: Missing validation for SMS without phone")
                print("      → Add validation to prevent SMS=true when phone_number is empty")
            
            return False

def main():
    print("🚀 Starting SMS Checkbox Backend Testing - OnlyMentors.ai")
    print("Focus: Identify why SMS checkbox doesn't save properly")
    print("=" * 80)
    
    # Initialize tester
    tester = SMSCheckboxTester()
    
    # Run comprehensive SMS tests
    test_results = tester.run_comprehensive_sms_test()
    
    if test_results:
        # Generate final report
        success = tester.generate_final_report(test_results)
        
        # Save detailed results for analysis
        with open('/app/sms_test_results.json', 'w') as f:
            json.dump({
                "test_results": test_results,
                "detailed_results": tester.test_results,
                "api_stats": {
                    "total_calls": tester.tests_run,
                    "successful_calls": tester.tests_passed,
                    "success_rate": (tester.tests_passed/tester.tests_run)*100 if tester.tests_run > 0 else 0
                },
                "timestamp": datetime.now().isoformat()
            }, f, indent=2)
        
        print(f"\n💾 Detailed test results saved to: /app/sms_test_results.json")
        
        return 0 if success else 1
    else:
        print("❌ Failed to run SMS tests")
        return 1

if __name__ == "__main__":
    sys.exit(main())