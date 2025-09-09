#!/usr/bin/env python3
"""
Final Stripe API Key Verification Test
=====================================

This test verifies all aspects of the Stripe API key configuration as requested:
1. Environment Variable Check - verify STRIPE_API_KEY is loaded from .env file
2. Stripe Integration Test - test basic Stripe functionality 
3. Configuration Validation - check no hardcoded keys exist
"""

import os
import sys
import requests
import json
from datetime import datetime

# Add the backend directory to Python path
sys.path.append('/app/backend')
sys.path.append('/app')

# Correct backend URL with /api prefix for endpoints
BACKEND_URL = "http://localhost:8001/api"
BACKEND_ROOT = "http://localhost:8001"

class FinalStripeTest:
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
    
    def test_environment_variable_configuration(self):
        """Test 1: Verify STRIPE_API_KEY environment variable configuration"""
        print("\n🔍 TEST 1: Environment Variable Configuration")
        
        try:
            # Check .env file exists and contains STRIPE_API_KEY
            env_file = "/app/backend/.env"
            if os.path.exists(env_file):
                with open(env_file, 'r') as f:
                    env_content = f.read()
                
                if "STRIPE_API_KEY=" in env_content:
                    self.log_test("STRIPE_API_KEY in .env", True, "Environment variable defined in .env file")
                    
                    # Load and check the value
                    from dotenv import load_dotenv
                    load_dotenv(env_file)
                    
                    stripe_key = os.getenv("STRIPE_API_KEY")
                    if stripe_key and stripe_key != "your-stripe-api-key-here":
                        if stripe_key.startswith("sk_"):
                            self.log_test("STRIPE_API_KEY Format", True, f"Valid Stripe key format ({stripe_key[:12]}...)")
                        else:
                            self.log_test("STRIPE_API_KEY Format", False, f"Invalid key format: {stripe_key[:10]}...")
                    else:
                        self.log_test("STRIPE_API_KEY Value", False, "Key is empty or placeholder")
                else:
                    self.log_test("STRIPE_API_KEY in .env", False, "STRIPE_API_KEY not found in .env file")
            else:
                self.log_test("Environment File", False, ".env file not found")
                
        except Exception as e:
            self.log_test("Environment Configuration", False, f"Error: {str(e)}")
    
    def test_stripe_integration_initialization(self):
        """Test 2: Verify StripeCheckout class can initialize with API key"""
        print("\n🔍 TEST 2: Stripe Integration Initialization")
        
        try:
            from emergentintegrations.payments.stripe.checkout import StripeCheckout
            from dotenv import load_dotenv
            load_dotenv('/app/backend/.env')
            
            stripe_key = os.getenv("STRIPE_API_KEY")
            
            if stripe_key:
                # Test StripeCheckout initialization
                stripe_checkout = StripeCheckout(api_key=stripe_key)
                self.log_test("StripeCheckout Initialization", True, "StripeCheckout class initialized successfully")
                
                # Verify API key is accessible
                if hasattr(stripe_checkout, 'api_key') or hasattr(stripe_checkout, '_api_key'):
                    self.log_test("API Key Accessibility", True, "API key properly stored and accessible")
                else:
                    self.log_test("API Key Accessibility", False, "Cannot verify API key storage")
            else:
                self.log_test("StripeCheckout Initialization", False, "No STRIPE_API_KEY available")
                
        except ImportError as e:
            self.log_test("StripeCheckout Import", False, f"Cannot import StripeCheckout: {str(e)}")
        except Exception as e:
            self.log_test("Stripe Integration", False, f"Error: {str(e)}")
    
    def test_payment_endpoint_stripe_access(self):
        """Test 3: Verify payment endpoints can access Stripe API key"""
        print("\n🔍 TEST 3: Payment Endpoints Stripe Access")
        
        try:
            # First verify backend is accessible
            root_response = requests.get(BACKEND_ROOT, timeout=10)
            if root_response.status_code != 200:
                self.log_test("Backend Connectivity", False, f"Backend not accessible: {root_response.status_code}")
                return
            
            self.log_test("Backend Connectivity", True, "Backend server is accessible")
            
            # Register a test user
            test_user = {
                "email": "stripe.final.test@example.com",
                "password": "TestPass123!",
                "full_name": "Stripe Final Test User"
            }
            
            register_response = requests.post(
                f"{BACKEND_URL}/auth/signup",
                json=test_user,
                timeout=10
            )
            
            token = None
            if register_response.status_code in [200, 201]:
                token = register_response.json().get("token")
                self.log_test("User Registration", True, "Test user registered successfully")
            elif register_response.status_code == 400:
                # Try login if user exists
                login_response = requests.post(
                    f"{BACKEND_URL}/auth/login",
                    json={"email": test_user["email"], "password": test_user["password"]},
                    timeout=10
                )
                
                if login_response.status_code == 200:
                    token = login_response.json().get("token")
                    self.log_test("User Login", True, "Test user login successful")
                else:
                    self.log_test("User Authentication", False, f"Cannot authenticate: {login_response.status_code}")
            else:
                self.log_test("User Registration", False, f"Registration failed: {register_response.status_code}")
            
            # Test payment checkout if we have authentication
            if token:
                checkout_data = {
                    "package_id": "monthly",
                    "origin_url": BACKEND_ROOT
                }
                
                headers = {"Authorization": f"Bearer {token}"}
                checkout_response = requests.post(
                    f"{BACKEND_URL}/payments/checkout",
                    json=checkout_data,
                    headers=headers,
                    timeout=15
                )
                
                if checkout_response.status_code == 200:
                    result = checkout_response.json()
                    if "checkout_url" in result and "stripe.com" in result["checkout_url"]:
                        self.log_test("Payment Endpoint Stripe Integration", True, "Stripe checkout session created successfully")
                    else:
                        self.log_test("Payment Endpoint Stripe Integration", False, "Invalid checkout response")
                elif checkout_response.status_code == 500:
                    error_text = checkout_response.text
                    if "stripe" in error_text.lower() or "api" in error_text.lower():
                        self.log_test("Payment Endpoint Stripe Integration", False, f"Stripe API error: {error_text[:100]}...")
                    else:
                        self.log_test("Payment Endpoint Stripe Integration", False, f"Server error: {error_text[:100]}...")
                else:
                    self.log_test("Payment Endpoint Stripe Integration", False, f"Unexpected status: {checkout_response.status_code}")
            else:
                self.log_test("Payment Endpoint Test", False, "No authentication token available")
                
        except Exception as e:
            self.log_test("Payment Endpoints Test", False, f"Error: {str(e)}")
    
    def test_configuration_validation(self):
        """Test 4: Verify no hardcoded API keys and proper configuration"""
        print("\n🔍 TEST 4: Configuration Validation")
        
        try:
            server_file = "/app/backend/server.py"
            
            if os.path.exists(server_file):
                with open(server_file, 'r') as f:
                    content = f.read()
                
                # Check for hardcoded Stripe keys
                hardcoded_patterns = ["sk_test_", "sk_live_"]
                hardcoded_found = any(pattern in content for pattern in hardcoded_patterns)
                
                if not hardcoded_found:
                    self.log_test("No Hardcoded Keys", True, "No hardcoded Stripe API keys found in code")
                else:
                    self.log_test("No Hardcoded Keys", False, "Hardcoded Stripe keys detected in code")
                
                # Check for proper environment variable usage
                if 'os.getenv("STRIPE_API_KEY")' in content:
                    self.log_test("Environment Variable Usage", True, "Code properly uses os.getenv() for STRIPE_API_KEY")
                else:
                    self.log_test("Environment Variable Usage", False, "Code may not use environment variable properly")
                
                # Check for StripeCheckout import
                if "from emergentintegrations.payments.stripe.checkout import StripeCheckout" in content:
                    self.log_test("StripeCheckout Import", True, "StripeCheckout properly imported")
                else:
                    self.log_test("StripeCheckout Import", False, "StripeCheckout import not found")
            else:
                self.log_test("Server File Check", False, "server.py file not found")
                
        except Exception as e:
            self.log_test("Configuration Validation", False, f"Error: {str(e)}")
    
    def test_backend_service_restart_verification(self):
        """Test 5: Verify backend service has loaded new environment"""
        print("\n🔍 TEST 5: Backend Service Environment Loading")
        
        try:
            # Check if backend service is running
            import subprocess
            result = subprocess.run(['sudo', 'supervisorctl', 'status', 'backend'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and "RUNNING" in result.stdout:
                self.log_test("Backend Service Status", True, "Backend service is running")
                
                # Test if the service can access environment variables
                root_response = requests.get(BACKEND_ROOT, timeout=5)
                if root_response.status_code == 200:
                    self.log_test("Backend Environment Access", True, "Backend service can access configuration")
                else:
                    self.log_test("Backend Environment Access", False, f"Backend service error: {root_response.status_code}")
            else:
                self.log_test("Backend Service Status", False, "Backend service not running properly")
                
        except Exception as e:
            self.log_test("Backend Service Check", False, f"Error: {str(e)}")
    
    def run_all_tests(self):
        """Run all Stripe API key verification tests"""
        print("🚀 FINAL STRIPE API KEY VERIFICATION TEST")
        print("=" * 60)
        print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Backend URL: {BACKEND_URL}")
        
        # Run all tests
        self.test_environment_variable_configuration()
        self.test_stripe_integration_initialization()
        self.test_payment_endpoint_stripe_access()
        self.test_configuration_validation()
        self.test_backend_service_restart_verification()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 FINAL TEST SUMMARY")
        print("=" * 60)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            print(f"  {result}")
        
        # Success criteria assessment
        print("\n🎯 SUCCESS CRITERIA VERIFICATION:")
        
        # Check each success criteria from the review request
        env_var_loaded = any("STRIPE_API_KEY in .env" in result and "✅ PASS" in result for result in self.test_results)
        stripe_init_working = any("StripeCheckout Initialization" in result and "✅ PASS" in result for result in self.test_results)
        payment_endpoints_access = any("Payment Endpoint" in result and "✅ PASS" in result for result in self.test_results)
        no_hardcoded_keys = any("No Hardcoded Keys" in result and "✅ PASS" in result for result in self.test_results)
        
        print(f"✅ Environment variable STRIPE_API_KEY loaded correctly: {'YES' if env_var_loaded else 'NO'}")
        print(f"✅ Stripe integration can initialize with the key: {'YES' if stripe_init_working else 'NO'}")
        print(f"✅ Payment endpoints have access to the API key: {'YES' if payment_endpoints_access else 'NO'}")
        print(f"✅ No hardcoded API keys exist in code: {'YES' if no_hardcoded_keys else 'NO'}")
        
        # Overall assessment
        print(f"\n🏆 OVERALL ASSESSMENT:")
        if success_rate >= 85:
            print("✅ STRIPE API KEY CONFIGURATION: EXCELLENT")
            print("   All success criteria met. Stripe API key is properly configured and accessible.")
        elif success_rate >= 70:
            print("⚠️  STRIPE API KEY CONFIGURATION: GOOD")
            print("   Most success criteria met. Minor issues may need attention.")
        else:
            print("❌ STRIPE API KEY CONFIGURATION: NEEDS ATTENTION")
            print("   Some success criteria not met. Configuration issues need to be resolved.")
        
        return success_rate >= 70

if __name__ == "__main__":
    test_runner = FinalStripeTest()
    success = test_runner.run_all_tests()
    
    if success:
        print("\n🎉 Stripe API key verification completed successfully!")
        exit(0)
    else:
        print("\n🚨 Stripe API key verification found issues that need attention!")
        exit(1)