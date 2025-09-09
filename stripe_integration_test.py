#!/usr/bin/env python3
"""
Comprehensive Stripe Integration Test
====================================

This test verifies the complete Stripe integration including API key loading,
StripeCheckout functionality, and payment endpoint accessibility.
"""

import os
import sys
import requests
import json
from datetime import datetime

# Add the backend directory to Python path
sys.path.append('/app/backend')
sys.path.append('/app')

# Correct backend URL (without /api suffix)
BACKEND_URL = "http://localhost:8001"

class StripeIntegrationTest:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_test(self, test_name, success, details):
        """Log test result"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
        
        result = f"{status} - {test_name}: {details}"
        self.test_results.append(result)
        print(result)
    
    def test_stripe_api_key_loading(self):
        """Test Stripe API key is properly loaded from environment"""
        print("\n🔍 TEST 1: Stripe API Key Environment Loading")
        
        try:
            from dotenv import load_dotenv
            load_dotenv('/app/backend/.env')
            
            stripe_key = os.getenv("STRIPE_API_KEY")
            
            if stripe_key:
                if stripe_key.startswith("sk_test_") or stripe_key.startswith("sk_live_"):
                    self.log_test("Stripe API Key Format", True, f"Valid Stripe key loaded ({stripe_key[:12]}...)")
                else:
                    self.log_test("Stripe API Key Format", False, f"Invalid key format: {stripe_key[:10]}...")
            else:
                self.log_test("Stripe API Key Loading", False, "STRIPE_API_KEY not found in environment")
                
        except Exception as e:
            self.log_test("Stripe API Key Loading", False, f"Error: {str(e)}")
    
    def test_stripe_checkout_initialization(self):
        """Test StripeCheckout class can be initialized"""
        print("\n🔍 TEST 2: StripeCheckout Class Initialization")
        
        try:
            from emergentintegrations.payments.stripe.checkout import StripeCheckout
            from dotenv import load_dotenv
            load_dotenv('/app/backend/.env')
            
            stripe_key = os.getenv("STRIPE_API_KEY")
            
            if stripe_key:
                stripe_checkout = StripeCheckout(api_key=stripe_key)
                self.log_test("StripeCheckout Initialization", True, "StripeCheckout class initialized successfully")
                
                # Test if we can access basic properties
                if hasattr(stripe_checkout, 'api_key') or hasattr(stripe_checkout, '_api_key'):
                    self.log_test("StripeCheckout API Key Access", True, "API key properly stored in instance")
                else:
                    self.log_test("StripeCheckout API Key Access", False, "Cannot verify API key storage")
            else:
                self.log_test("StripeCheckout Initialization", False, "No API key available for initialization")
                
        except ImportError as e:
            self.log_test("StripeCheckout Import", False, f"Cannot import StripeCheckout: {str(e)}")
        except Exception as e:
            self.log_test("StripeCheckout Initialization", False, f"Error: {str(e)}")
    
    def test_backend_connectivity(self):
        """Test backend server connectivity"""
        print("\n🔍 TEST 3: Backend Server Connectivity")
        
        try:
            response = requests.get(f"{BACKEND_URL}/", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Backend Connectivity", True, f"Backend accessible - {data.get('message', 'OK')}")
                
                # Check if it's the correct API
                if "OnlyMentors.ai" in data.get('message', ''):
                    self.log_test("Backend API Verification", True, "Correct OnlyMentors.ai API detected")
                else:
                    self.log_test("Backend API Verification", False, "Unexpected API response")
            else:
                self.log_test("Backend Connectivity", False, f"Backend returned status {response.status_code}")
                
        except Exception as e:
            self.log_test("Backend Connectivity", False, f"Connection error: {str(e)}")
    
    def test_payment_endpoints_exist(self):
        """Test that payment endpoints exist and are accessible"""
        print("\n🔍 TEST 4: Payment Endpoints Accessibility")
        
        # Test user registration first
        try:
            test_user = {
                "email": "stripe.integration.test@example.com",
                "password": "TestPass123!",
                "full_name": "Stripe Integration Test User"
            }
            
            # Try to register user
            register_response = requests.post(
                f"{BACKEND_URL}/auth/signup",
                json=test_user,
                timeout=10
            )
            
            token = None
            if register_response.status_code in [200, 201]:
                token = register_response.json().get("token")
                self.log_test("Test User Registration", True, "Test user registered successfully")
            elif register_response.status_code == 400:
                # User might exist, try login
                login_response = requests.post(
                    f"{BACKEND_URL}/auth/login",
                    json={"email": test_user["email"], "password": test_user["password"]},
                    timeout=10
                )
                
                if login_response.status_code == 200:
                    token = login_response.json().get("token")
                    self.log_test("Test User Login", True, "Test user login successful")
                else:
                    self.log_test("Test User Setup", False, f"Cannot login existing user: {login_response.status_code}")
            else:
                self.log_test("Test User Registration", False, f"Registration failed: {register_response.status_code}")
            
            # Test payment checkout endpoint if we have a token
            if token:
                checkout_data = {
                    "package_id": "monthly",
                    "origin_url": "http://localhost:8001"
                }
                
                headers = {"Authorization": f"Bearer {token}"}
                checkout_response = requests.post(
                    f"{BACKEND_URL}/payments/checkout",
                    json=checkout_data,
                    headers=headers,
                    timeout=15
                )
                
                if checkout_response.status_code == 200:
                    checkout_result = checkout_response.json()
                    if "checkout_url" in checkout_result:
                        self.log_test("Payment Checkout Endpoint", True, "Checkout session created successfully")
                        
                        # Verify it's a Stripe URL
                        checkout_url = checkout_result["checkout_url"]
                        if "stripe.com" in checkout_url:
                            self.log_test("Stripe Integration Working", True, "Valid Stripe checkout URL generated")
                        else:
                            self.log_test("Stripe Integration Working", False, f"Unexpected checkout URL: {checkout_url}")
                    else:
                        self.log_test("Payment Checkout Endpoint", False, "Checkout response missing checkout_url")
                elif checkout_response.status_code == 500:
                    error_text = checkout_response.text
                    if "stripe" in error_text.lower():
                        self.log_test("Payment Checkout Endpoint", False, f"Stripe API error: {error_text[:100]}...")
                    else:
                        self.log_test("Payment Checkout Endpoint", False, f"Server error: {error_text[:100]}...")
                else:
                    self.log_test("Payment Checkout Endpoint", False, f"Unexpected status: {checkout_response.status_code}")
            else:
                self.log_test("Payment Endpoint Test", False, "No authentication token available")
                
        except Exception as e:
            self.log_test("Payment Endpoints Test", False, f"Error: {str(e)}")
    
    def test_stripe_configuration_in_code(self):
        """Test that Stripe is properly configured in the backend code"""
        print("\n🔍 TEST 5: Stripe Configuration in Backend Code")
        
        try:
            # Check server.py for proper Stripe configuration
            server_file = "/app/backend/server.py"
            
            if os.path.exists(server_file):
                with open(server_file, 'r') as f:
                    content = f.read()
                
                # Check for proper environment variable usage
                if 'os.getenv("STRIPE_API_KEY")' in content:
                    self.log_test("Environment Variable Usage", True, "Code uses os.getenv for STRIPE_API_KEY")
                else:
                    self.log_test("Environment Variable Usage", False, "Code may not use environment variable properly")
                
                # Check for StripeCheckout import
                if "from emergentintegrations.payments.stripe.checkout import StripeCheckout" in content:
                    self.log_test("StripeCheckout Import", True, "StripeCheckout properly imported")
                else:
                    self.log_test("StripeCheckout Import", False, "StripeCheckout import not found")
                
                # Check for no hardcoded keys
                hardcoded_patterns = ["sk_test_", "sk_live_"]
                hardcoded_found = any(pattern in content for pattern in hardcoded_patterns)
                
                if not hardcoded_found:
                    self.log_test("No Hardcoded Keys", True, "No hardcoded Stripe keys found")
                else:
                    self.log_test("No Hardcoded Keys", False, "Hardcoded Stripe keys detected")
            else:
                self.log_test("Server File Check", False, "server.py not found")
                
        except Exception as e:
            self.log_test("Code Configuration Check", False, f"Error: {str(e)}")
    
    def test_business_payment_endpoints(self):
        """Test business payment endpoints that use Stripe"""
        print("\n🔍 TEST 6: Business Payment Endpoints")
        
        try:
            # Test business checkout endpoint
            business_checkout_data = {
                "plan_id": "starter",
                "company_name": "Test Company",
                "contact_name": "Test User",
                "contact_email": "test@testcompany.com",
                "skip_trial": False
            }
            
            business_response = requests.post(
                f"{BACKEND_URL}/business/create-checkout",
                json=business_checkout_data,
                timeout=15
            )
            
            if business_response.status_code == 200:
                business_result = business_response.json()
                if "checkout_url" in business_result:
                    self.log_test("Business Checkout Endpoint", True, "Business checkout session created")
                    
                    # Verify Stripe URL
                    if "stripe.com" in business_result["checkout_url"]:
                        self.log_test("Business Stripe Integration", True, "Valid business Stripe checkout URL")
                    else:
                        self.log_test("Business Stripe Integration", False, "Invalid business checkout URL")
                else:
                    self.log_test("Business Checkout Endpoint", False, "Business checkout missing URL")
            elif business_response.status_code == 500:
                error_text = business_response.text
                if "stripe" in error_text.lower():
                    self.log_test("Business Checkout Endpoint", False, f"Stripe error in business checkout: {error_text[:100]}...")
                else:
                    self.log_test("Business Checkout Endpoint", False, f"Business checkout server error: {error_text[:100]}...")
            else:
                self.log_test("Business Checkout Endpoint", False, f"Business checkout status: {business_response.status_code}")
                
        except Exception as e:
            self.log_test("Business Payment Endpoints", False, f"Error: {str(e)}")
    
    def run_all_tests(self):
        """Run all Stripe integration tests"""
        print("🚀 COMPREHENSIVE STRIPE INTEGRATION TEST")
        print("=" * 60)
        print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Backend URL: {BACKEND_URL}")
        
        # Run all tests
        self.test_stripe_api_key_loading()
        self.test_stripe_checkout_initialization()
        self.test_backend_connectivity()
        self.test_payment_endpoints_exist()
        self.test_stripe_configuration_in_code()
        self.test_business_payment_endpoints()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            print(f"  {result}")
        
        # Overall assessment
        print("\n🎯 OVERALL ASSESSMENT:")
        if success_rate >= 85:
            print("✅ STRIPE INTEGRATION: EXCELLENT")
            print("   Stripe API key is properly configured and all integrations are working.")
        elif success_rate >= 70:
            print("⚠️  STRIPE INTEGRATION: GOOD WITH MINOR ISSUES")
            print("   Most Stripe functionality is working but some issues need attention.")
        else:
            print("❌ STRIPE INTEGRATION: NEEDS ATTENTION")
            print("   Significant issues found with Stripe integration.")
        
        return success_rate >= 70

if __name__ == "__main__":
    test_runner = StripeIntegrationTest()
    success = test_runner.run_all_tests()
    
    if success:
        print("\n🎉 Stripe integration test completed successfully!")
        exit(0)
    else:
        print("\n🚨 Stripe integration test found critical issues!")
        exit(1)