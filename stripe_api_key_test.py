#!/usr/bin/env python3
"""
Stripe API Key Environment Variable Verification Test
====================================================

This test verifies that the STRIPE_API_KEY environment variable is properly loaded
and accessible to the payment system as requested in the review.

Test Focus:
1. Environment Variable Check - verify STRIPE_API_KEY is loaded from .env file
2. Stripe Integration Test - test basic Stripe functionality 
3. Configuration Validation - check no hardcoded keys exist
"""

import os
import sys
import asyncio
import requests
import json
from datetime import datetime

# Add the backend directory to Python path
sys.path.append('/app/backend')
sys.path.append('/app')

# Test configuration
BACKEND_URL = "https://enterprise-coach.preview.emergentagent.com/api"

class StripeAPIKeyVerificationTest:
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
        
    def test_environment_variable_loading(self):
        """Test 1: Verify STRIPE_API_KEY is loaded from .env file"""
        print("\n🔍 TEST 1: Environment Variable Loading")
        
        try:
            # Check if .env file exists
            env_file_path = "/app/backend/.env"
            if not os.path.exists(env_file_path):
                self.log_test("Environment File Existence", False, ".env file not found at /app/backend/.env")
                return
            
            # Read .env file content
            with open(env_file_path, 'r') as f:
                env_content = f.read()
            
            # Check if STRIPE_API_KEY is defined in .env
            if "STRIPE_API_KEY=" in env_content:
                self.log_test("STRIPE_API_KEY in .env file", True, "STRIPE_API_KEY found in .env file")
                
                # Extract the key value
                for line in env_content.split('\n'):
                    if line.startswith('STRIPE_API_KEY='):
                        key_value = line.split('=', 1)[1].strip()
                        if key_value and key_value != "your-stripe-api-key-here":
                            self.log_test("STRIPE_API_KEY has value", True, f"Key configured (length: {len(key_value)} chars)")
                        else:
                            self.log_test("STRIPE_API_KEY has value", False, "Key is placeholder or empty")
                        break
            else:
                self.log_test("STRIPE_API_KEY in .env file", False, "STRIPE_API_KEY not found in .env file")
                
        except Exception as e:
            self.log_test("Environment Variable Loading", False, f"Error reading .env file: {str(e)}")
    
    def test_backend_environment_access(self):
        """Test 2: Verify backend can access STRIPE_API_KEY environment variable"""
        print("\n🔍 TEST 2: Backend Environment Variable Access")
        
        try:
            # Import the backend server to check environment loading
            from dotenv import load_dotenv
            load_dotenv('/app/backend/.env')
            
            # Check if STRIPE_API_KEY is accessible via os.getenv
            stripe_key = os.getenv("STRIPE_API_KEY")
            
            if stripe_key:
                if stripe_key == "your-new-stripe-api-key-here":
                    self.log_test("Backend STRIPE_API_KEY Access", True, "Environment variable loaded (placeholder value)")
                elif stripe_key.startswith("sk_"):
                    # Check if it's a valid Stripe key format
                    if stripe_key.startswith("sk_test_") or stripe_key.startswith("sk_live_"):
                        self.log_test("Backend STRIPE_API_KEY Access", True, f"Valid Stripe key format detected ({stripe_key[:12]}...)")
                    else:
                        self.log_test("Backend STRIPE_API_KEY Access", True, f"Stripe key format detected ({stripe_key[:12]}...)")
                else:
                    self.log_test("Backend STRIPE_API_KEY Access", True, f"Key loaded but format unclear ({len(stripe_key)} chars)")
            else:
                self.log_test("Backend STRIPE_API_KEY Access", False, "STRIPE_API_KEY not accessible via os.getenv()")
                
        except Exception as e:
            self.log_test("Backend Environment Variable Access", False, f"Error accessing environment: {str(e)}")
    
    def test_stripe_integration_initialization(self):
        """Test 3: Verify StripeCheckout class can initialize with the API key"""
        print("\n🔍 TEST 3: Stripe Integration Initialization")
        
        try:
            # Import the StripeCheckout class
            from emergentintegrations.payments.stripe.checkout import StripeCheckout
            
            # Load environment
            from dotenv import load_dotenv
            load_dotenv('/app/backend/.env')
            
            stripe_key = os.getenv("STRIPE_API_KEY")
            
            if not stripe_key:
                self.log_test("StripeCheckout Initialization", False, "No STRIPE_API_KEY available for initialization")
                return
            
            # Try to initialize StripeCheckout
            try:
                stripe_checkout = StripeCheckout(api_key=stripe_key)
                self.log_test("StripeCheckout Initialization", True, "StripeCheckout class initialized successfully")
                
                # Check if the key is properly set
                if hasattr(stripe_checkout, 'api_key') or hasattr(stripe_checkout, '_api_key'):
                    self.log_test("StripeCheckout API Key Storage", True, "API key properly stored in StripeCheckout instance")
                else:
                    self.log_test("StripeCheckout API Key Storage", False, "API key storage method unclear")
                    
            except Exception as init_error:
                self.log_test("StripeCheckout Initialization", False, f"Failed to initialize StripeCheckout: {str(init_error)}")
                
        except ImportError as e:
            self.log_test("StripeCheckout Import", False, f"Cannot import StripeCheckout: {str(e)}")
        except Exception as e:
            self.log_test("Stripe Integration Initialization", False, f"Error testing Stripe integration: {str(e)}")
    
    def test_payment_endpoints_access_key(self):
        """Test 4: Verify payment endpoints can access the API key"""
        print("\n🔍 TEST 4: Payment Endpoints API Key Access")
        
        try:
            # Test if backend server has the STRIPE_API_KEY loaded
            response = requests.get(f"{BACKEND_URL}/", timeout=10)
            
            if response.status_code == 200:
                self.log_test("Backend Server Connectivity", True, "Backend server is accessible")
                
                # Try to access a payment endpoint to see if it can use the Stripe key
                # We'll test the checkout endpoint which should use the Stripe integration
                test_user_data = {
                    "email": "stripe.test@example.com",
                    "password": "TestPass123!",
                    "full_name": "Stripe Test User"
                }
                
                # Register a test user first
                register_response = requests.post(
                    f"{BACKEND_URL}/auth/signup",
                    json=test_user_data,
                    timeout=10
                )
                
                if register_response.status_code in [200, 201]:
                    token = register_response.json().get("token")
                    
                    if token:
                        # Test checkout endpoint with authentication
                        checkout_data = {
                            "package_id": "monthly",
                            "origin_url": BACKEND_URL
                        }
                        
                        headers = {"Authorization": f"Bearer {token}"}
                        checkout_response = requests.post(
                            f"{BACKEND_URL}/payments/checkout",
                            json=checkout_data,
                            headers=headers,
                            timeout=15
                        )
                        
                        if checkout_response.status_code == 200:
                            checkout_data = checkout_response.json()
                            if "checkout_url" in checkout_data:
                                self.log_test("Payment Endpoint Stripe Access", True, "Checkout endpoint successfully created Stripe session")
                            else:
                                self.log_test("Payment Endpoint Stripe Access", False, "Checkout endpoint response missing checkout_url")
                        elif checkout_response.status_code == 500:
                            # Check if it's a Stripe API key related error
                            error_text = checkout_response.text.lower()
                            if "stripe" in error_text or "api" in error_text:
                                self.log_test("Payment Endpoint Stripe Access", False, f"Stripe API error (likely key issue): {checkout_response.status_code}")
                            else:
                                self.log_test("Payment Endpoint Stripe Access", False, f"Server error: {checkout_response.status_code}")
                        else:
                            self.log_test("Payment Endpoint Stripe Access", False, f"Checkout endpoint error: {checkout_response.status_code}")
                    else:
                        self.log_test("Payment Endpoint Authentication", False, "No token received from registration")
                elif register_response.status_code == 400:
                    # User might already exist, try login
                    login_response = requests.post(
                        f"{BACKEND_URL}/auth/login",
                        json={"email": test_user_data["email"], "password": test_user_data["password"]},
                        timeout=10
                    )
                    
                    if login_response.status_code == 200:
                        self.log_test("Payment Endpoint User Setup", True, "Test user login successful")
                    else:
                        self.log_test("Payment Endpoint User Setup", False, f"Cannot setup test user: {register_response.status_code}")
                else:
                    self.log_test("Payment Endpoint User Setup", False, f"Cannot register test user: {register_response.status_code}")
            else:
                self.log_test("Backend Server Connectivity", False, f"Backend server not accessible: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            self.log_test("Payment Endpoints Network", False, f"Network error: {str(e)}")
        except Exception as e:
            self.log_test("Payment Endpoints API Key Access", False, f"Error testing payment endpoints: {str(e)}")
    
    def test_no_hardcoded_keys(self):
        """Test 5: Verify no hardcoded Stripe API keys exist in the code"""
        print("\n🔍 TEST 5: Hardcoded API Keys Check")
        
        try:
            # Check server.py for hardcoded keys
            server_file = "/app/backend/server.py"
            
            if os.path.exists(server_file):
                with open(server_file, 'r') as f:
                    server_content = f.read()
                
                # Look for hardcoded Stripe keys
                hardcoded_patterns = [
                    "sk_test_",
                    "sk_live_",
                    "stripe_api_key = \"sk_",
                    "STRIPE_API_KEY = \"sk_"
                ]
                
                hardcoded_found = False
                for pattern in hardcoded_patterns:
                    if pattern in server_content:
                        hardcoded_found = True
                        break
                
                if hardcoded_found:
                    self.log_test("No Hardcoded Keys", False, "Hardcoded Stripe API key found in server.py")
                else:
                    self.log_test("No Hardcoded Keys", True, "No hardcoded Stripe API keys found in server.py")
                
                # Check if environment variable is used correctly
                if "os.getenv(\"STRIPE_API_KEY\")" in server_content or "os.environ.get('STRIPE_API_KEY')" in server_content:
                    self.log_test("Environment Variable Usage", True, "Code properly uses environment variable for Stripe API key")
                else:
                    self.log_test("Environment Variable Usage", False, "Code may not be using environment variable for Stripe API key")
            else:
                self.log_test("Server File Check", False, "server.py file not found")
                
        except Exception as e:
            self.log_test("Hardcoded Keys Check", False, f"Error checking for hardcoded keys: {str(e)}")
    
    def test_stripe_key_format_validation(self):
        """Test 6: Validate Stripe API key format"""
        print("\n🔍 TEST 6: Stripe API Key Format Validation")
        
        try:
            from dotenv import load_dotenv
            load_dotenv('/app/backend/.env')
            
            stripe_key = os.getenv("STRIPE_API_KEY")
            
            if not stripe_key:
                self.log_test("Stripe Key Format", False, "No STRIPE_API_KEY found")
                return
            
            # Check key format
            if stripe_key == "your-new-stripe-api-key-here":
                self.log_test("Stripe Key Format", False, "Stripe API key is still placeholder value")
            elif stripe_key.startswith("sk_test_"):
                self.log_test("Stripe Key Format", True, "Valid Stripe test key format (sk_test_)")
            elif stripe_key.startswith("sk_live_"):
                self.log_test("Stripe Key Format", True, "Valid Stripe live key format (sk_live_)")
            elif stripe_key.startswith("sk_"):
                self.log_test("Stripe Key Format", True, "Valid Stripe key format (sk_)")
            else:
                self.log_test("Stripe Key Format", False, f"Invalid Stripe key format: {stripe_key[:10]}...")
                
        except Exception as e:
            self.log_test("Stripe Key Format Validation", False, f"Error validating key format: {str(e)}")
    
    def run_all_tests(self):
        """Run all Stripe API key verification tests"""
        print("🚀 STRIPE API KEY ENVIRONMENT VARIABLE VERIFICATION TEST")
        print("=" * 60)
        print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Backend URL: {BACKEND_URL}")
        
        # Run all tests
        self.test_environment_variable_loading()
        self.test_backend_environment_access()
        self.test_stripe_integration_initialization()
        self.test_payment_endpoints_access_key()
        self.test_no_hardcoded_keys()
        self.test_stripe_key_format_validation()
        
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
        if success_rate >= 80:
            print("✅ STRIPE API KEY CONFIGURATION: EXCELLENT")
            print("   The Stripe API key environment variable is properly configured and accessible.")
        elif success_rate >= 60:
            print("⚠️  STRIPE API KEY CONFIGURATION: GOOD WITH MINOR ISSUES")
            print("   Most Stripe configuration is working but some issues need attention.")
        else:
            print("❌ STRIPE API KEY CONFIGURATION: NEEDS ATTENTION")
            print("   Significant issues found with Stripe API key configuration.")
        
        return success_rate >= 60

if __name__ == "__main__":
    test_runner = StripeAPIKeyVerificationTest()
    success = test_runner.run_all_tests()
    
    if success:
        print("\n🎉 Stripe API key verification completed successfully!")
        exit(0)
    else:
        print("\n🚨 Stripe API key verification found critical issues!")
        exit(1)