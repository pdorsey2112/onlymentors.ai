#!/usr/bin/env python3
"""
OAuth Configuration Verification Test
Quick verification test of Google and Facebook OAuth configuration after backend restart
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL from frontend .env
BACKEND_URL = "https://multi-tenant-ai.preview.emergentagent.com"

def test_google_oauth_config():
    """Test Google OAuth Configuration endpoint"""
    print("🔍 Testing Google OAuth Configuration...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/auth/google/config", timeout=10)
        
        if response.status_code == 200:
            config = response.json()
            print(f"✅ Google OAuth Config Response: {response.status_code}")
            print(f"   Client ID: {config.get('client_id', 'Not found')}")
            print(f"   Redirect URI: {config.get('redirect_uri', 'Not found')}")
            print(f"   Scope: {config.get('scope', 'Not found')}")
            
            # Verify redirect URI is properly set to current domain
            redirect_uri = config.get('redirect_uri', '')
            if 'user-data-restore.preview.emergentagent.com' in redirect_uri:
                print("✅ Redirect URI properly set to current domain")
                return True
            else:
                print(f"❌ Redirect URI issue: {redirect_uri}")
                return False
        else:
            print(f"❌ Google OAuth Config Failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Google OAuth Config Error: {str(e)}")
        return False

def test_facebook_oauth_config():
    """Test Facebook OAuth Configuration endpoint"""
    print("\n🔍 Testing Facebook OAuth Configuration...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/auth/facebook/config", timeout=10)
        
        if response.status_code == 200:
            config = response.json()
            print(f"✅ Facebook OAuth Config Response: {response.status_code}")
            print(f"   App ID: {config.get('app_id', 'Not found')}")
            print(f"   Redirect URI: {config.get('redirect_uri', 'Not found')}")
            print(f"   Scope: {config.get('scope', 'Not found')}")
            
            # Verify Facebook config has required fields
            if config.get('app_id') and config.get('redirect_uri'):
                print("✅ Facebook OAuth configuration is complete")
                return True
            else:
                print("❌ Facebook OAuth configuration incomplete")
                return False
        else:
            print(f"❌ Facebook OAuth Config Failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Facebook OAuth Config Error: {str(e)}")
        return False

def test_google_oauth_endpoint():
    """Test Google OAuth authentication endpoint accessibility"""
    print("\n🔍 Testing Google OAuth Authentication Endpoint...")
    
    try:
        # Test with empty request to verify endpoint is accessible
        response = requests.post(f"{BACKEND_URL}/api/auth/google", 
                               json={}, 
                               timeout=10)
        
        # We expect a 400 error for missing data, which means endpoint is accessible
        if response.status_code == 400:
            print("✅ Google OAuth endpoint is accessible")
            print(f"   Expected 400 response: {response.json().get('detail', 'No detail')}")
            return True
        elif response.status_code == 422:
            print("✅ Google OAuth endpoint is accessible")
            print(f"   Validation error (expected): {response.json().get('detail', 'No detail')}")
            return True
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Google OAuth Endpoint Error: {str(e)}")
        return False

def test_facebook_oauth_endpoint():
    """Test Facebook OAuth authentication endpoint accessibility"""
    print("\n🔍 Testing Facebook OAuth Authentication Endpoint...")
    
    try:
        # Test with empty request to verify endpoint is accessible
        response = requests.post(f"{BACKEND_URL}/api/auth/facebook", 
                               json={}, 
                               timeout=10)
        
        # We expect a 400 error for missing data, which means endpoint is accessible
        if response.status_code == 400:
            print("✅ Facebook OAuth endpoint is accessible")
            print(f"   Expected 400 response: {response.json().get('detail', 'No detail')}")
            return True
        elif response.status_code == 422:
            print("✅ Facebook OAuth endpoint is accessible")
            print(f"   Validation error (expected): {response.json().get('detail', 'No detail')}")
            return True
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Facebook OAuth Endpoint Error: {str(e)}")
        return False

def main():
    """Run OAuth verification tests"""
    print("=" * 80)
    print("🔐 OAUTH CONFIGURATION VERIFICATION TEST")
    print("=" * 80)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    results = []
    
    # Test Google OAuth Configuration
    results.append(("Google OAuth Config", test_google_oauth_config()))
    
    # Test Facebook OAuth Configuration  
    results.append(("Facebook OAuth Config", test_facebook_oauth_config()))
    
    # Test Google OAuth Endpoint
    results.append(("Google OAuth Endpoint", test_google_oauth_endpoint()))
    
    # Test Facebook OAuth Endpoint
    results.append(("Facebook OAuth Endpoint", test_facebook_oauth_endpoint()))
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<30} {status}")
        if result:
            passed += 1
    
    print("-" * 80)
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ALL OAUTH VERIFICATION TESTS PASSED!")
        print("✅ Google and Facebook OAuth configurations are working correctly")
        print("✅ All OAuth endpoints are accessible")
        return True
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        print("⚠️  OAuth configuration may need attention")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)