#!/usr/bin/env python3
"""
Content Upload Security Testing - Localhost Version
Testing the standard content upload endpoint security fixes using localhost.
"""

import requests
import tempfile
import os
import json
import time
from datetime import datetime

# Configuration - Use localhost for direct backend access
BACKEND_URL = "http://localhost:8001"
API_BASE = f"{BACKEND_URL}/api"

def create_test_file(content="Test content", filename="test.txt"):
    """Create a temporary test file"""
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix=f"_{filename}", delete=False)
    temp_file.write(content)
    temp_file.close()
    return temp_file.name

def create_test_creator():
    """Create a test creator for testing"""
    try:
        creator_email = f"testcreator_{int(time.time())}@example.com"
        creator_data = {
            "email": creator_email,
            "password": "TestPassword123!",
            "full_name": "Test Creator",
            "account_name": "testcreator",
            "category": "business",
            "hourly_rate": 100.0,
            "bio": "Test creator for security testing"
        }
        
        # Sign up creator
        response = requests.post(f"{API_BASE}/creators/signup", json=creator_data)
        if response.status_code in [200, 201]:
            signup_result = response.json()
            creator_id = signup_result["creator"]["creator_id"]
            
            # Login to get token
            login_response = requests.post(f"{API_BASE}/creators/login", json={
                "email": creator_email,
                "password": "TestPassword123!"
            })
            
            if login_response.status_code == 200:
                login_result = login_response.json()
                token = login_result["token"]
                
                return {
                    "creator_id": creator_id,
                    "token": token,
                    "email": creator_email
                }
        
        print(f"Creator signup failed: {response.status_code} - {response.text}")
        return None
        
    except Exception as e:
        print(f"Failed to create test creator: {str(e)}")
        return None

def test_content_upload_security():
    """Test content upload security comprehensively"""
    print("🔒 CONTENT UPLOAD SECURITY TESTING (LOCALHOST)")
    print("=" * 60)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Testing Time: {datetime.now().isoformat()}")
    print()
    
    # Create test creator
    print("🧪 Setting up test creator...")
    creator = create_test_creator()
    if not creator:
        print("❌ CRITICAL: Could not create test creator!")
        return
    
    creator_id = creator["creator_id"]
    token = creator["token"]
    print(f"✅ Created test creator: {creator_id}")
    print()
    
    # Test data
    upload_data = {
        "title": "Security Test Content",
        "description": "Testing content upload security",
        "content_type": "document",
        "category": "business",
        "tags": '["test", "security"]'
    }
    
    test_results = []
    
    # Test 1: Authenticated Upload (Should Work)
    print("🧪 Test 1: Authenticated Upload (Should Work)")
    print("-" * 50)
    
    test_file_path = create_test_file("Authenticated test content", "auth_test.txt")
    
    try:
        with open(test_file_path, 'rb') as f:
            files = {'content_file': ('auth_test.txt', f, 'text/plain')}
            headers = {'Authorization': f'Bearer {token}'}
            
            response = requests.post(
                f"{API_BASE}/creators/{creator_id}/content",
                data=upload_data,
                files=files,
                headers=headers
            )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:300]}...")
        
        if response.status_code in [200, 201]:
            print("✅ PASS: Authenticated upload successful")
            test_results.append(("Authenticated Upload", True))
            
            # Store content ID for later tests
            try:
                result = response.json()
                content_id = result.get("content_id")
                print(f"   Content ID: {content_id}")
            except:
                pass
        else:
            print("❌ FAIL: Authenticated upload should work!")
            test_results.append(("Authenticated Upload", False))
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        test_results.append(("Authenticated Upload", False))
    
    os.unlink(test_file_path)
    print()
    
    # Test 2: Unauthenticated Upload (Should Fail)
    print("🧪 Test 2: Unauthenticated Upload (Should Fail)")
    print("-" * 50)
    
    test_file_path = create_test_file("Unauthenticated test content", "unauth_test.txt")
    
    try:
        with open(test_file_path, 'rb') as f:
            files = {'content_file': ('unauth_test.txt', f, 'text/plain')}
            # No Authorization header
            
            response = requests.post(
                f"{API_BASE}/creators/{creator_id}/content",
                data=upload_data,
                files=files
            )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:300]}...")
        
        if response.status_code in [401, 403]:
            print("✅ PASS: Unauthenticated upload correctly rejected")
            test_results.append(("Unauthenticated Upload", True))
        else:
            print("❌ FAIL: Unauthenticated upload should be rejected!")
            test_results.append(("Unauthenticated Upload", False))
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        test_results.append(("Unauthenticated Upload", False))
    
    os.unlink(test_file_path)
    print()
    
    # Test 3: Invalid Token Upload (Should Fail)
    print("🧪 Test 3: Invalid Token Upload (Should Fail)")
    print("-" * 50)
    
    test_file_path = create_test_file("Invalid token test content", "invalid_test.txt")
    
    try:
        with open(test_file_path, 'rb') as f:
            files = {'content_file': ('invalid_test.txt', f, 'text/plain')}
            headers = {'Authorization': 'Bearer invalid_token_12345'}
            
            response = requests.post(
                f"{API_BASE}/creators/{creator_id}/content",
                data=upload_data,
                files=files,
                headers=headers
            )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:300]}...")
        
        if response.status_code == 401:
            print("✅ PASS: Invalid token upload correctly rejected")
            test_results.append(("Invalid Token Upload", True))
        else:
            print("❌ FAIL: Invalid token upload should be rejected!")
            test_results.append(("Invalid Token Upload", False))
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        test_results.append(("Invalid Token Upload", False))
    
    os.unlink(test_file_path)
    print()
    
    # Test 4: Cross-Creator Upload (Should Fail)
    print("🧪 Test 4: Cross-Creator Upload Protection (Should Fail)")
    print("-" * 50)
    
    # Create second creator
    creator2 = create_test_creator()
    if creator2:
        creator2_id = creator2["creator_id"]
        
        test_file_path = create_test_file("Cross-creator test content", "cross_test.txt")
        
        try:
            with open(test_file_path, 'rb') as f:
                files = {'content_file': ('cross_test.txt', f, 'text/plain')}
                headers = {'Authorization': f'Bearer {token}'}  # creator1's token
                
                response = requests.post(
                    f"{API_BASE}/creators/{creator2_id}/content",  # creator2's endpoint
                    data=upload_data,
                    files=files,
                    headers=headers
                )
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text[:300]}...")
            
            if response.status_code == 403:
                print("✅ PASS: Cross-creator upload correctly rejected")
                test_results.append(("Cross-Creator Protection", True))
            else:
                print("❌ FAIL: Cross-creator upload should be rejected!")
                test_results.append(("Cross-Creator Protection", False))
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            test_results.append(("Cross-Creator Protection", False))
        
        os.unlink(test_file_path)
    else:
        print("⚠️  SKIP: Could not create second creator for cross-creator test")
        test_results.append(("Cross-Creator Protection", False))
    
    print()
    
    # Test 5: Content Retrieval (Should Work)
    print("🧪 Test 5: Content Retrieval (Should Work)")
    print("-" * 50)
    
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f"{API_BASE}/creators/{creator_id}/content", headers=headers)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:300]}...")
        
        if response.status_code == 200:
            print("✅ PASS: Content retrieval successful")
            test_results.append(("Content Retrieval", True))
            
            # Check if our test content is there
            try:
                content_list = response.json()
                content_items = content_list.get("content", [])
                print(f"   Found {len(content_items)} content items")
            except:
                pass
        else:
            print("❌ FAIL: Content retrieval should work!")
            test_results.append(("Content Retrieval", False))
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        test_results.append(("Content Retrieval", False))
    
    print()
    
    # Summary
    print("=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    total_tests = len(test_results)
    passed_tests = sum(1 for _, success in test_results if success)
    failed_tests = total_tests - passed_tests
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"Total Tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_tests}")
    print(f"📈 Success Rate: {success_rate:.1f}%")
    print()
    
    print("📋 DETAILED RESULTS:")
    for test_name, success in test_results:
        status = "✅" if success else "❌"
        print(f"{status} {test_name}")
    
    print()
    print("🔒 SECURITY ASSESSMENT:")
    
    # Check critical security tests
    auth_passed = any(name == "Authenticated Upload" and success for name, success in test_results)
    unauth_passed = any(name == "Unauthenticated Upload" and success for name, success in test_results)
    cross_creator_passed = any(name == "Cross-Creator Protection" and success for name, success in test_results)
    
    if auth_passed:
        print("✅ Authenticated uploads working correctly")
    else:
        print("❌ CRITICAL: Authenticated uploads not working")
        
    if unauth_passed:
        print("✅ Unauthenticated uploads properly blocked")
    else:
        print("❌ CRITICAL SECURITY ISSUE: Unauthenticated uploads not blocked!")
        
    if cross_creator_passed:
        print("✅ Cross-creator upload protection working")
    else:
        print("❌ CRITICAL SECURITY ISSUE: Cross-creator uploads not blocked!")
    
    print()
    
    if success_rate >= 80:
        print("🎉 CONTENT UPLOAD SECURITY: EXCELLENT")
    elif success_rate >= 60:
        print("⚠️  CONTENT UPLOAD SECURITY: GOOD (some issues)")
    else:
        print("🚨 CONTENT UPLOAD SECURITY: NEEDS ATTENTION")
    
    return test_results

if __name__ == "__main__":
    test_content_upload_security()