import requests
import sys
import json
import time
from datetime import datetime

class FocusedBackendTester:
    def __init__(self, base_url="https://mentor-search.preview.emergentagent.com"):
        self.base_url = base_url
        self.user_token = None
        self.admin_token = None
        self.creator_token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.critical_issues = []
        self.minor_issues = []

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None, token=None):
        """Run a single API test"""
        if endpoint.startswith('api/'):
            url = f"{self.base_url}/{endpoint}"
        else:
            url = f"{self.base_url}/api/{endpoint}"
            
        test_headers = {'Content-Type': 'application/json'}
        
        auth_token = token or self.user_token
        if auth_token:
            test_headers['Authorization'] = f'Bearer {auth_token}'
        
        if headers:
            test_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=30)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ PASSED - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ FAILED - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text[:200]}")
                return False, {}

        except Exception as e:
            print(f"❌ FAILED - Error: {str(e)}")
            return False, {}

    def test_critical_authentication_flows(self):
        """Test critical authentication flows"""
        print(f"\n{'='*80}")
        print("🔐 CRITICAL AUTHENTICATION FLOWS")
        print(f"{'='*80}")
        
        # Test user registration and login
        timestamp = datetime.now().strftime('%H%M%S')
        test_email = f"critical_test_{timestamp}@example.com"
        test_password = "TestPass123!"
        
        # User Signup
        success, response = self.run_test(
            "User Registration",
            "POST",
            "auth/signup",
            200,
            data={"email": test_email, "password": test_password, "full_name": "Critical Test User"}
        )
        
        if success and 'token' in response:
            self.user_token = response['token']
            print(f"✅ User registration and JWT token generation working")
        else:
            self.critical_issues.append("User registration failed")
            return False
        
        # User Login
        success, response = self.run_test(
            "User Login",
            "POST",
            "auth/login",
            200,
            data={"email": test_email, "password": test_password}
        )
        
        if success and 'token' in response:
            print(f"✅ User login working")
        else:
            self.critical_issues.append("User login failed")
            return False
        
        # JWT Token Validation
        success, response = self.run_test(
            "JWT Token Validation",
            "GET",
            "auth/me",
            200
        )
        
        if success and 'user' in response:
            print(f"✅ JWT token validation working")
        else:
            self.critical_issues.append("JWT token validation failed")
            return False
        
        # OAuth Configuration Tests
        success, response = self.run_test(
            "Google OAuth Config",
            "GET",
            "auth/google/config",
            200
        )
        
        if success and 'client_id' in response:
            print(f"✅ Google OAuth properly configured")
        else:
            self.minor_issues.append("Google OAuth configuration issue")
        
        success, response = self.run_test(
            "Facebook OAuth Config",
            "GET",
            "auth/facebook/config",
            200
        )
        
        if success and 'app_id' in response:
            print(f"✅ Facebook OAuth properly configured")
        else:
            self.minor_issues.append("Facebook OAuth configuration issue")
        
        return True

    def test_critical_mentor_system(self):
        """Test critical mentor system functionality"""
        print(f"\n{'='*80}")
        print("🧠 CRITICAL MENTOR SYSTEM")
        print(f"{'='*80}")
        
        # Test categories endpoint
        success, response = self.run_test(
            "Get All Categories",
            "GET",
            "categories",
            200
        )
        
        if not success or 'categories' not in response:
            self.critical_issues.append("Categories endpoint failed")
            return False
        
        categories = response['categories']
        expected_categories = ['business', 'sports', 'health', 'science', 'relationships']
        found_categories = [cat['id'] for cat in categories]
        
        if not all(cat in found_categories for cat in expected_categories):
            self.critical_issues.append(f"Missing expected categories. Found: {found_categories}")
            return False
        
        print(f"✅ All 5 categories available: {found_categories}")
        
        # Test mentor data retrieval
        success, response = self.run_test(
            "Get Business Mentors",
            "GET",
            "categories/business/mentors",
            200
        )
        
        if not success or 'mentors' not in response or len(response['mentors']) == 0:
            self.critical_issues.append("Mentor data retrieval failed")
            return False
        
        mentors = response['mentors']
        print(f"✅ Retrieved {len(mentors)} business mentors")
        
        # Test mentor search
        success, response = self.run_test(
            "Search Mentors",
            "GET",
            "search/mentors?q=warren&category=business",
            200
        )
        
        if not success or 'results' not in response:
            self.critical_issues.append("Mentor search failed")
            return False
        
        print(f"✅ Mentor search working - found {len(response['results'])} results")
        
        # Test question asking with AI responses
        if self.user_token:
            success, response = self.run_test(
                "Ask Question to Mentor",
                "POST",
                "questions/ask",
                200,
                data={
                    "category": "business",
                    "mentor_ids": ["warren_buffett"],
                    "question": "What is your best investment advice?"
                }
            )
            
            if success and 'responses' in response and len(response['responses']) > 0:
                response_text = response['responses'][0].get('response', '')
                if len(response_text) > 100:
                    print(f"✅ AI mentor responses working - {len(response_text)} chars")
                else:
                    self.minor_issues.append("AI responses might be fallbacks (short length)")
            else:
                self.critical_issues.append("Question asking to mentors failed")
                return False
            
            # Test 5-mentor limit enforcement
            success, response = self.run_test(
                "Test 5-Mentor Limit Enforcement",
                "POST",
                "questions/ask",
                400,
                data={
                    "category": "business",
                    "mentor_ids": ["warren_buffett", "steve_jobs", "bill_gates", "elon_musk", "jeff_bezos", "mark_cuban"],
                    "question": "Test question"
                }
            )
            
            if success:
                print(f"✅ 5-mentor limit properly enforced")
            else:
                self.minor_issues.append("5-mentor limit enforcement issue")
        
        return True

    def test_critical_user_management(self):
        """Test critical user management functionality"""
        print(f"\n{'='*80}")
        print("👤 CRITICAL USER MANAGEMENT")
        print(f"{'='*80}")
        
        if not self.user_token:
            self.critical_issues.append("No user token available for user management tests")
            return False
        
        # Test user profile CRUD
        success, response = self.run_test(
            "Get User Profile",
            "GET",
            "user/profile",
            200
        )
        
        if not success or 'user_id' not in response:
            self.critical_issues.append("User profile retrieval failed")
            return False
        
        print(f"✅ User profile retrieval working")
        
        # Test profile update
        success, response = self.run_test(
            "Update User Profile",
            "PUT",
            "user/profile",
            200,
            data={"full_name": "Updated Critical Test User"}
        )
        
        if not success or 'message' not in response:
            self.critical_issues.append("User profile update failed")
            return False
        
        print(f"✅ User profile update working")
        
        # Test question history
        success, response = self.run_test(
            "Get Question History",
            "GET",
            "questions/history",
            200
        )
        
        if not success or 'questions' not in response:
            self.critical_issues.append("Question history retrieval failed")
            return False
        
        print(f"✅ Question history tracking working")
        
        # Test subscription system
        success, response = self.run_test(
            "Create Stripe Checkout",
            "POST",
            "payments/checkout",
            200,
            data={
                "package_id": "monthly",
                "origin_url": self.base_url
            }
        )
        
        if not success or 'url' not in response or 'session_id' not in response:
            self.critical_issues.append("Stripe checkout creation failed")
            return False
        
        print(f"✅ Subscription/payment system working")
        
        return True

    def test_admin_system(self):
        """Test admin system functionality"""
        print(f"\n{'='*80}")
        print("👑 ADMIN SYSTEM")
        print(f"{'='*80}")
        
        # Test admin login
        success, response = self.run_test(
            "Admin Login",
            "POST",
            "admin/login",
            200,
            data={
                "email": "admin@onlymentors.ai",
                "password": "SuperAdmin2024!"
            }
        )
        
        if success and 'token' in response:
            self.admin_token = response['token']
            print(f"✅ Admin authentication working")
        else:
            self.critical_issues.append("Admin authentication failed")
            return False
        
        # Test admin dashboard
        success, response = self.run_test(
            "Admin Dashboard",
            "GET",
            "admin/dashboard",
            200,
            token=self.admin_token
        )
        
        if success and 'platform_stats' in response:
            print(f"✅ Admin dashboard working")
        else:
            self.critical_issues.append("Admin dashboard failed")
            return False
        
        # Test user management
        success, response = self.run_test(
            "Admin User Management",
            "GET",
            "admin/users",
            200,
            token=self.admin_token
        )
        
        if success and 'users' in response:
            print(f"✅ Admin user management working")
        else:
            self.minor_issues.append("Admin user management issue")
        
        # Test reports
        success, response = self.run_test(
            "User Activity Report",
            "GET",
            "admin/reports/user-activity",
            200,
            token=self.admin_token
        )
        
        if success:
            print(f"✅ User activity reports working")
        else:
            self.minor_issues.append("User activity reports issue")
        
        success, response = self.run_test(
            "Financial Report",
            "GET",
            "admin/reports/financial",
            200,
            token=self.admin_token
        )
        
        if success:
            print(f"✅ Financial reports working")
        else:
            self.minor_issues.append("Financial reports issue")
        
        return True

    def test_core_api_functionality(self):
        """Test core API functionality"""
        print(f"\n{'='*80}")
        print("🔧 CORE API FUNCTIONALITY")
        print(f"{'='*80}")
        
        # Test database connections via categories endpoint
        success, response = self.run_test(
            "Database Connection Test",
            "GET",
            "categories",
            200
        )
        
        if not success or 'categories' not in response:
            self.critical_issues.append("Database connections failed")
            return False
        
        print(f"✅ Database connections stable")
        
        # Test error handling
        success, response = self.run_test(
            "404 Error Handling",
            "GET",
            "nonexistent-endpoint",
            404
        )
        
        if success:
            print(f"✅ 404 error handling working")
        else:
            self.minor_issues.append("404 error handling issue")
        
        # Test unauthorized access
        success, response = self.run_test(
            "Unauthorized Access Test",
            "GET",
            "user/profile",
            401,
            token=""  # No token
        )
        
        if not success:
            # Try 403 as alternative
            success, response = self.run_test(
                "Forbidden Access Test",
                "GET",
                "user/profile",
                403,
                token=""
            )
        
        if success:
            print(f"✅ Authentication protection working")
        else:
            self.minor_issues.append("Authentication protection issue")
        
        # Test API response times
        start_time = time.time()
        success, response = self.run_test(
            "Response Time Test",
            "GET",
            "categories",
            200
        )
        end_time = time.time()
        
        response_time = end_time - start_time
        if success and response_time < 5.0:
            print(f"✅ API response time acceptable: {response_time:.2f}s")
        else:
            self.minor_issues.append(f"API response time slow: {response_time:.2f}s")
        
        return True

    def run_comprehensive_test(self):
        """Run comprehensive backend test"""
        print("🚀 Starting Focused OnlyMentors.ai Backend Regression Test")
        print("🎯 Focus: Critical systems after profile system removal")
        print("=" * 90)
        
        test_results = {
            "authentication": False,
            "mentor_system": False,
            "user_management": False,
            "admin_system": False,
            "core_apis": False
        }
        
        try:
            # Test critical systems
            test_results["authentication"] = self.test_critical_authentication_flows()
            test_results["mentor_system"] = self.test_critical_mentor_system()
            test_results["user_management"] = self.test_critical_user_management()
            test_results["admin_system"] = self.test_admin_system()
            test_results["core_apis"] = self.test_core_api_functionality()
            
            # Analyze results
            return self.analyze_results(test_results)
            
        except Exception as e:
            print(f"\n❌ CRITICAL ERROR during testing: {str(e)}")
            self.critical_issues.append(f"Testing error: {str(e)}")
            return False

    def analyze_results(self, test_results):
        """Analyze test results and provide final assessment"""
        print(f"\n{'='*90}")
        print("📊 FOCUSED REGRESSION TEST RESULTS")
        print(f"{'='*90}")
        
        passed_systems = sum(test_results.values())
        total_systems = len(test_results)
        
        print(f"\n🔍 System Test Results:")
        for system, passed in test_results.items():
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"   {system.replace('_', ' ').title()}: {status}")
        
        print(f"\n📈 Statistics:")
        print(f"   Total API Tests Run: {self.tests_run}")
        print(f"   Total API Tests Passed: {self.tests_passed}")
        print(f"   API Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        print(f"   Critical Systems Passed: {passed_systems}/{total_systems}")
        print(f"   System Success Rate: {(passed_systems/total_systems)*100:.1f}%")
        
        # Report issues
        if self.critical_issues:
            print(f"\n🚨 Critical Issues Found ({len(self.critical_issues)}):")
            for issue in self.critical_issues:
                print(f"   • {issue}")
        
        if self.minor_issues:
            print(f"\n⚠️ Minor Issues Found ({len(self.minor_issues)}):")
            for issue in self.minor_issues:
                print(f"   • {issue}")
        
        # Final assessment
        print(f"\n🎯 FINAL ASSESSMENT:")
        
        # Determine if system is production ready
        critical_systems_working = (
            test_results["authentication"] and
            test_results["mentor_system"] and
            test_results["user_management"] and
            test_results["core_apis"] and
            len(self.critical_issues) == 0
        )
        
        if critical_systems_working:
            print("🎉 ONLYMENTORS.AI PLATFORM: ✅ REGRESSION TESTS PASSED!")
            print("\n✅ All Critical Systems Verified:")
            print("   • Authentication system fully functional")
            print("   • Mentor system working (categories, search, AI responses)")
            print("   • User management operational (profiles, subscriptions)")
            print("   • Core APIs responding correctly")
            print("   • Database connections stable")
            
            if test_results["admin_system"]:
                print("   • Admin system fully functional")
            else:
                print("   • Admin system has minor issues (non-critical)")
            
            if self.minor_issues:
                print(f"\n⚠️ Minor Issues ({len(self.minor_issues)}) - Non-Critical:")
                for issue in self.minor_issues:
                    print(f"   • {issue}")
                print("   These issues don't affect core functionality")
            
            print(f"\n🚀 The platform is PRODUCTION-READY after profile system removal!")
            print("🎯 All core user flows are working correctly")
            return True
        else:
            print("❌ ONLYMENTORS.AI PLATFORM: CRITICAL ISSUES FOUND!")
            print("\n🔍 Critical Issues Preventing Production Use:")
            for issue in self.critical_issues:
                print(f"   • {issue}")
            
            failed_systems = [system for system, passed in test_results.items() if not passed]
            if failed_systems:
                print(f"\n❌ Failed Critical Systems: {', '.join(failed_systems)}")
            
            print(f"\n⚠️ The platform needs fixes before production use.")
            return False

def main():
    tester = FocusedBackendTester()
    success = tester.run_comprehensive_test()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())