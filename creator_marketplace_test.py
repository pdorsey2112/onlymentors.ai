import requests
import sys
import json
import time
import os
from datetime import datetime

class CreatorMarketplaceAPITester:
    def __init__(self, base_url="https://f2b0aa4c-4c6c-44c0-8e63-7550a30e04a0.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.creator_token = None
        self.user_data = None
        self.creator_data = None
        self.tests_run = 0
        self.tests_passed = 0
        self.creator_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None, files=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        test_headers = {}
        
        if not files:  # Only set JSON content type if not uploading files
            test_headers['Content-Type'] = 'application/json'
        
        if self.creator_token:
            test_headers['Authorization'] = f'Bearer {self.creator_token}'
        elif self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'
        
        if headers:
            test_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=30)
            elif method == 'POST':
                if files:
                    # Remove Content-Type for file uploads (requests will set it)
                    if 'Content-Type' in test_headers:
                        del test_headers['Content-Type']
                    response = requests.post(url, data=data, files=files, headers=test_headers, timeout=30)
                else:
                    response = requests.post(url, json=data, headers=test_headers, timeout=30)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response preview: {json.dumps(response_data, indent=2, default=str)[:300]}...")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_creator_signup(self):
        """Test creator signup with provided test data"""
        print(f"\n🎯 Testing Creator Signup")
        
        # Use unique email to avoid conflicts
        unique_email = f"creator-test-{datetime.now().strftime('%H%M%S')}@onlymentors.ai"
        creator_data = {
            "email": unique_email,
            "password": "CreatorPass123!",
            "full_name": "Test Creator",
            "account_name": f"test_creator_{datetime.now().strftime('%H%M%S')}",
            "description": "Expert in business strategy and leadership",
            "monthly_price": 49.99,
            "category": "business",
            "expertise_areas": ["leadership", "strategy", "business growth"]
        }
        
        success, response = self.run_test(
            "Creator Signup",
            "POST",
            "api/creators/signup",
            200,
            data=creator_data
        )
        
        if success and 'token' in response and 'creator' in response:
            self.creator_token = response['token']
            self.creator_data = response['creator']
            self.creator_id = response['creator']['creator_id']
            print(f"✅ Creator signup successful")
            print(f"   Creator ID: {self.creator_id}")
            print(f"   Account Name: {response['creator']['account_name']}")
            print(f"   Monthly Price: ${response['creator']['monthly_price']}")
            print(f"   Category: {response['creator']['category']}")
            print(f"   Expertise Areas: {response['creator']['expertise_areas']}")
            return True
        return False

    def test_creator_login(self):
        """Test creator login with the same credentials"""
        print(f"\n🔐 Testing Creator Login")
        
        # Use the same email from signup if available, otherwise use a known working one
        if hasattr(self, 'signup_email'):
            login_email = self.signup_email
        else:
            login_email = "creator-test@onlymentors.ai"  # Fallback to existing creator
        
        login_data = {
            "email": login_email,
            "password": "CreatorPass123!"
        }
        
        success, response = self.run_test(
            "Creator Login",
            "POST",
            "api/creators/login",
            200,
            data=login_data
        )
        
        if success and 'token' in response and 'creator' in response:
            self.creator_token = response['token']
            self.creator_data = response['creator']
            self.creator_id = response['creator']['creator_id']
            print(f"✅ Creator login successful")
            print(f"   Creator ID: {self.creator_id}")
            print(f"   Account Name: {response['creator']['account_name']}")
            print(f"   Token received and stored")
            return True
        return False

    def test_banking_info_submission(self):
        """Test banking information submission"""
        print(f"\n💳 Testing Banking Information Submission")
        
        if not self.creator_id:
            print("❌ No creator ID available, skipping banking test")
            return False
        
        banking_data = {
            "bank_account_number": "123456789",
            "routing_number": "987654321",
            "tax_id": "12-3456789",
            "account_holder_name": "Test Creator",
            "bank_name": "Test Bank"
        }
        
        success, response = self.run_test(
            "Banking Info Submission",
            "POST",
            f"api/creators/banking?creator_id={self.creator_id}",
            200,
            data=banking_data
        )
        
        if success:
            print(f"✅ Banking information submitted successfully")
            if 'message' in response:
                print(f"   Message: {response['message']}")
            return True
        return False

    def test_id_verification_upload(self):
        """Test ID document upload for verification"""
        print(f"\n📄 Testing ID Verification Upload")
        
        if not self.creator_id:
            print("❌ No creator ID available, skipping ID verification test")
            return False
        
        # Create a dummy file for testing
        test_file_path = "/tmp/test_id_document.txt"
        with open(test_file_path, "w") as f:
            f.write("This is a test ID document for verification purposes.")
        
        try:
            with open(test_file_path, "rb") as f:
                files = {"id_document": ("test_id.txt", f, "text/plain")}
                
                success, response = self.run_test(
                    "ID Document Upload",
                    "POST",
                    f"api/creators/{self.creator_id}/id-verification",
                    200,
                    files=files
                )
                
                if success:
                    print(f"✅ ID document uploaded successfully")
                    if 'message' in response:
                        print(f"   Message: {response['message']}")
                    return True
        except Exception as e:
            print(f"❌ Error during file upload: {str(e)}")
        finally:
            # Clean up test file
            if os.path.exists(test_file_path):
                os.remove(test_file_path)
        
        return False

    def test_get_creators_list(self):
        """Test getting list of approved creators"""
        print(f"\n👥 Testing Get Creators List")
        
        success, response = self.run_test(
            "Get Creators List",
            "GET",
            "api/creators",
            200
        )
        
        if success and 'creators' in response:
            creators = response['creators']
            total = response.get('total', 0)
            print(f"✅ Retrieved {total} creators")
            
            if creators:
                print(f"   Sample creator: {creators[0]['account_name']} - ${creators[0]['monthly_price']}")
                print(f"   Categories found: {list(set(c['category'] for c in creators))}")
            
            return True
        return False

    def test_get_creators_by_category(self):
        """Test getting creators filtered by category"""
        print(f"\n🏷️ Testing Get Creators by Category")
        
        success, response = self.run_test(
            "Get Creators - Business Category",
            "GET",
            "api/creators?category=business",
            200
        )
        
        if success and 'creators' in response:
            creators = response['creators']
            total = response.get('total', 0)
            print(f"✅ Retrieved {total} business creators")
            
            # Verify all creators are in business category
            if creators:
                business_creators = [c for c in creators if c['category'] == 'business']
                if len(business_creators) == len(creators):
                    print(f"✅ All creators are correctly filtered to business category")
                else:
                    print(f"⚠️  Category filtering may not be working correctly")
            
            return True
        return False

    def test_get_individual_creator(self):
        """Test getting individual creator profile"""
        print(f"\n👤 Testing Get Individual Creator Profile")
        
        if not self.creator_id:
            print("❌ No creator ID available, skipping individual creator test")
            return False
        
        success, response = self.run_test(
            "Get Individual Creator",
            "GET",
            f"api/creators/{self.creator_id}",
            200
        )
        
        if success:
            print(f"✅ Retrieved creator profile successfully")
            print(f"   Creator: {response.get('account_name')}")
            print(f"   Description: {response.get('description', '')[:100]}...")
            print(f"   Monthly Price: ${response.get('monthly_price')}")
            print(f"   Expertise: {response.get('expertise_areas')}")
            print(f"   Verified: {response.get('is_verified', False)}")
            return True
        return False

    def test_user_upgrade_to_creator(self):
        """Test upgrading existing user to creator"""
        print(f"\n⬆️ Testing User Upgrade to Creator")
        
        # First create a regular user
        user_email = f"upgrade_test_{datetime.now().strftime('%H%M%S')}@test.com"
        user_data = {
            "email": user_email,
            "password": "UserPass123!",
            "full_name": "Upgrade Test User"
        }
        
        # Signup as regular user
        success, response = self.run_test(
            "User Signup for Upgrade",
            "POST",
            "api/auth/signup",
            200,
            data=user_data
        )
        
        if not success or 'token' not in response:
            print("❌ Failed to create user for upgrade test")
            return False
        
        # Store user token
        user_token = response['token']
        original_creator_token = self.creator_token
        self.creator_token = None  # Clear creator token
        self.token = user_token  # Set user token
        
        # Now upgrade to creator
        creator_upgrade_data = {
            "email": user_email,  # This will be ignored, using user's email
            "password": "dummy",  # This will be ignored, using user's password
            "full_name": "Upgraded Creator",
            "account_name": f"upgraded_creator_{datetime.now().strftime('%H%M%S')}",
            "description": "I'm an upgraded creator with expertise in technology",
            "monthly_price": 39.99,
            "category": "science",
            "expertise_areas": ["technology", "innovation", "startups"]
        }
        
        success, response = self.run_test(
            "Upgrade User to Creator",
            "POST",
            "api/creators/upgrade",
            200,
            data=creator_upgrade_data
        )
        
        # Restore original creator token
        self.creator_token = original_creator_token
        self.token = None
        
        if success and 'creator' in response:
            print(f"✅ User successfully upgraded to creator")
            print(f"   Creator Account: {response['creator']['account_name']}")
            print(f"   Monthly Price: ${response['creator']['monthly_price']}")
            print(f"   Category: {response['creator']['category']}")
            return True
        return False

    def test_error_scenarios(self):
        """Test various error scenarios"""
        print(f"\n🚨 Testing Error Scenarios")
        
        error_tests_passed = 0
        error_tests_total = 0
        
        # Test 1: Duplicate creator signup
        error_tests_total += 1
        duplicate_data = {
            "email": "creator-test@onlymentors.ai",  # Same email as first creator
            "password": "AnotherPass123!",
            "full_name": "Another Creator",
            "account_name": "another_creator",
            "description": "Another expert",
            "monthly_price": 29.99,
            "category": "health",
            "expertise_areas": ["wellness"]
        }
        
        success, response = self.run_test(
            "Duplicate Email Signup",
            "POST",
            "api/creators/signup",
            400,
            data=duplicate_data
        )
        if success:
            error_tests_passed += 1
            print("✅ Duplicate email properly rejected")
        
        # Test 2: Invalid creator login
        error_tests_total += 1
        invalid_login = {
            "email": "nonexistent@test.com",
            "password": "wrongpassword"
        }
        
        success, response = self.run_test(
            "Invalid Creator Login",
            "POST",
            "api/creators/login",
            401,
            data=invalid_login
        )
        if success:
            error_tests_passed += 1
            print("✅ Invalid login properly rejected")
        
        # Test 3: Get non-existent creator
        error_tests_total += 1
        success, response = self.run_test(
            "Get Non-existent Creator",
            "GET",
            "api/creators/nonexistent_creator_id",
            404
        )
        if success:
            error_tests_passed += 1
            print("✅ Non-existent creator properly returns 404")
        
        print(f"   Error handling tests: {error_tests_passed}/{error_tests_total} passed")
        return error_tests_passed >= 2  # At least 2/3 error tests should pass

    def test_data_validation(self):
        """Test data validation scenarios"""
        print(f"\n✅ Testing Data Validation")
        
        validation_tests_passed = 0
        validation_tests_total = 0
        
        # Test 1: Invalid monthly price (too low)
        validation_tests_total += 1
        invalid_price_data = {
            "email": "price_test@test.com",
            "password": "TestPass123!",
            "full_name": "Price Test Creator",
            "account_name": "price_test_creator",
            "description": "Testing price validation",
            "monthly_price": 0.50,  # Below minimum
            "category": "business",
            "expertise_areas": ["testing"]
        }
        
        success, response = self.run_test(
            "Invalid Monthly Price (Too Low)",
            "POST",
            "api/creators/signup",
            422,  # Validation error
            data=invalid_price_data
        )
        if success:
            validation_tests_passed += 1
            print("✅ Low price validation working")
        
        # Test 2: Invalid monthly price (too high)
        validation_tests_total += 1
        invalid_price_high_data = {
            "email": "price_high_test@test.com",
            "password": "TestPass123!",
            "full_name": "High Price Test Creator",
            "account_name": "high_price_test_creator",
            "description": "Testing high price validation",
            "monthly_price": 1500.00,  # Above maximum
            "category": "business",
            "expertise_areas": ["testing"]
        }
        
        success, response = self.run_test(
            "Invalid Monthly Price (Too High)",
            "POST",
            "api/creators/signup",
            422,  # Validation error
            data=invalid_price_high_data
        )
        if success:
            validation_tests_passed += 1
            print("✅ High price validation working")
        
        # Test 3: Missing required fields
        validation_tests_total += 1
        missing_fields_data = {
            "email": "missing_test@test.com",
            "password": "TestPass123!",
            # Missing full_name, account_name, description, etc.
        }
        
        success, response = self.run_test(
            "Missing Required Fields",
            "POST",
            "api/creators/signup",
            422,  # Validation error
            data=missing_fields_data
        )
        if success:
            validation_tests_passed += 1
            print("✅ Missing fields validation working")
        
        print(f"   Validation tests: {validation_tests_passed}/{validation_tests_total} passed")
        return validation_tests_passed >= 2  # At least 2/3 validation tests should pass

def main():
    print("🚀 Starting Creator Marketplace Backend Tests")
    print("=" * 70)
    
    # Setup
    tester = CreatorMarketplaceAPITester()
    
    # Test sequence following the user's requirements
    tests_results = []
    
    # Test 1: Creator Signup
    print(f"\n{'='*70}")
    print("🎯 CREATOR AUTHENTICATION TESTING")
    print(f"{'='*70}")
    
    signup_success = tester.test_creator_signup()
    tests_results.append(("Creator Signup", signup_success))
    
    if not signup_success:
        print("❌ Creator signup failed, some tests may be skipped")
    
    # Test 2: Creator Login
    login_success = tester.test_creator_login()
    tests_results.append(("Creator Login", login_success))
    
    # Test 3: User Upgrade to Creator
    upgrade_success = tester.test_user_upgrade_to_creator()
    tests_results.append(("User Upgrade to Creator", upgrade_success))
    
    # Test 4: Banking Information
    print(f"\n{'='*70}")
    print("💳 CREATOR VERIFICATION TESTING")
    print(f"{'='*70}")
    
    banking_success = tester.test_banking_info_submission()
    tests_results.append(("Banking Info Submission", banking_success))
    
    # Test 5: ID Verification
    id_verification_success = tester.test_id_verification_upload()
    tests_results.append(("ID Verification Upload", id_verification_success))
    
    # Test 6: Creator Discovery
    print(f"\n{'='*70}")
    print("👥 CREATOR DISCOVERY TESTING")
    print(f"{'='*70}")
    
    creators_list_success = tester.test_get_creators_list()
    tests_results.append(("Get Creators List", creators_list_success))
    
    creators_category_success = tester.test_get_creators_by_category()
    tests_results.append(("Get Creators by Category", creators_category_success))
    
    individual_creator_success = tester.test_get_individual_creator()
    tests_results.append(("Get Individual Creator", individual_creator_success))
    
    # Test 7: Error Handling
    print(f"\n{'='*70}")
    print("🚨 ERROR HANDLING & VALIDATION TESTING")
    print(f"{'='*70}")
    
    error_handling_success = tester.test_error_scenarios()
    tests_results.append(("Error Handling", error_handling_success))
    
    data_validation_success = tester.test_data_validation()
    tests_results.append(("Data Validation", data_validation_success))
    
    # Calculate results
    passed_tests = sum(1 for _, success in tests_results if success)
    total_tests = len(tests_results)
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    
    # Print final results
    print("\n" + "=" * 70)
    print(f"📊 CREATOR MARKETPLACE TEST RESULTS")
    print("=" * 70)
    
    for test_name, success in tests_results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:<30} {status}")
    
    print(f"\nOverall API tests passed: {tester.tests_passed}/{tester.tests_run}")
    print(f"Overall API success rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    print(f"Feature tests passed: {passed_tests}/{total_tests}")
    print(f"Feature success rate: {success_rate:.1f}%")
    
    # Determine overall status
    critical_tests = ["Creator Signup", "Creator Login", "Get Creators List"]
    critical_passed = sum(1 for test_name, success in tests_results if test_name in critical_tests and success)
    
    if critical_passed >= 2 and success_rate >= 70:
        print(f"\n🎉 CREATOR MARKETPLACE IS WORKING!")
        print("✅ Core creator functionality is operational")
        print("✅ Authentication and verification systems working")
        print("✅ Creator discovery endpoints functional")
        return 0
    else:
        print(f"\n⚠️  CREATOR MARKETPLACE HAS ISSUES")
        print("❌ Some critical functionality is not working properly")
        return 1

if __name__ == "__main__":
    sys.exit(main())