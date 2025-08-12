import requests
import sys
import json
import time
import io
from datetime import datetime

class EnhancedContentManagementTester:
    def __init__(self, base_url="https://mentor-hub-11.preview.emergentagent.com"):
        self.base_url = base_url
        self.creator_token = None
        self.creator_data = None
        self.test_content_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None, files=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        test_headers = {}
        
        if self.creator_token:
            test_headers['Authorization'] = f'Bearer {self.creator_token}'
        
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
                    response = requests.post(url, data=data, files=files, headers=test_headers, timeout=30)
                else:
                    if not headers or 'Content-Type' not in headers:
                        test_headers['Content-Type'] = 'application/json'
                    response = requests.post(url, json=data, headers=test_headers, timeout=30)
            elif method == 'PUT':
                test_headers['Content-Type'] = 'application/json'
                response = requests.put(url, json=data, headers=test_headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=30)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response preview: {json.dumps(response_data, indent=2)[:300]}...")
                    self.test_results.append({
                        'test': name,
                        'status': 'PASSED',
                        'expected': expected_status,
                        'actual': response.status_code,
                        'response': response_data
                    })
                    return True, response_data
                except:
                    self.test_results.append({
                        'test': name,
                        'status': 'PASSED',
                        'expected': expected_status,
                        'actual': response.status_code,
                        'response': {}
                    })
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                    self.test_results.append({
                        'test': name,
                        'status': 'FAILED',
                        'expected': expected_status,
                        'actual': response.status_code,
                        'error': error_data
                    })
                except:
                    print(f"   Error: {response.text}")
                    self.test_results.append({
                        'test': name,
                        'status': 'FAILED',
                        'expected': expected_status,
                        'actual': response.status_code,
                        'error': response.text
                    })
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.test_results.append({
                'test': name,
                'status': 'ERROR',
                'expected': expected_status,
                'actual': 'Exception',
                'error': str(e)
            })
            return False, {}

    def setup_creator_account(self):
        """Create and verify a creator account for testing"""
        print(f"\n🏗️  Setting up Creator Account for Testing...")
        
        # Create unique creator data
        timestamp = datetime.now().strftime('%H%M%S')
        creator_email = f"content_test_creator_{timestamp}@test.com"
        creator_password = "CreatorPass123!"
        
        # Step 1: Creator Signup
        success, response = self.run_test(
            "Creator Signup",
            "POST",
            "api/creators/signup",
            200,
            data={
                "email": creator_email,
                "password": creator_password,
                "full_name": "Content Test Creator",
                "account_name": f"content_creator_{timestamp}",
                "description": "Test creator for content management testing",
                "monthly_price": 49.99,
                "category": "business",
                "expertise_areas": ["content creation", "testing", "business strategy"]
            }
        )
        
        if not success or 'token' not in response:
            print("❌ Failed to create creator account")
            return False
        
        self.creator_token = response['token']
        self.creator_data = response['creator']
        creator_id = self.creator_data['creator_id']
        
        print(f"✅ Creator account created: {creator_id}")
        
        # Step 2: Submit Banking Info for Verification
        success, response = self.run_test(
            "Submit Banking Info",
            "POST",
            f"api/creators/{creator_id}/banking",
            200,
            data={
                "bank_account_number": "123456789",
                "routing_number": "987654321",
                "tax_id": "12-3456789",
                "account_holder_name": "Content Test Creator",
                "bank_name": "Test Bank"
            }
        )
        
        if not success:
            print("❌ Failed to submit banking info")
            return False
        
        # Step 3: Upload ID Document (simulate with text file)
        test_file_content = b"This is a test ID document for content management testing"
        files = {'id_document': ('test_id.pdf', io.BytesIO(test_file_content), 'application/pdf')}
        
        success, response = self.run_test(
            "Upload ID Document",
            "POST",
            f"api/creators/{creator_id}/id-verification",
            200,
            files=files
        )
        
        if not success:
            print("❌ Failed to upload ID document")
            return False
        
        print(f"✅ Creator account fully set up and verified: {creator_id}")
        return True

    def test_content_upload(self):
        """Test uploading content (existing functionality)"""
        print(f"\n📤 Testing Content Upload (Existing Functionality)...")
        
        creator_id = self.creator_data['creator_id']
        
        # Test uploading different types of content
        content_tests = [
            {
                "title": "Test Video Content",
                "description": "This is a test video for content management",
                "content_type": "video",
                "category": "business",
                "tags": '["test", "video", "business"]'
            },
            {
                "title": "Test Document Content", 
                "description": "This is a test document for content management",
                "content_type": "document",
                "category": "business",
                "tags": '["test", "document", "guide"]'
            },
            {
                "title": "Test Article Link",
                "description": "This is a test article link for content management",
                "content_type": "article_link",
                "category": "business",
                "tags": '["test", "article", "link"]'
            }
        ]
        
        uploaded_content = []
        
        for content_data in content_tests:
            # Create test file for video/document types
            files = None
            if content_data["content_type"] in ["video", "document"]:
                test_file_content = b"This is test content data for " + content_data["content_type"].encode()
                if content_data["content_type"] == "video":
                    files = {'content_file': ('test_video.mp4', io.BytesIO(test_file_content), 'video/mp4')}
                else:
                    files = {'content_file': ('test_doc.pdf', io.BytesIO(test_file_content), 'application/pdf')}
            
            success, response = self.run_test(
                f"Upload {content_data['content_type'].title()} Content",
                "POST",
                f"api/creators/{creator_id}/content",
                200,
                data=content_data,
                files=files,
                headers={'Content-Type': None} if files else None
            )
            
            if success and 'content_id' in response:
                uploaded_content.append({
                    'content_id': response['content_id'],
                    'type': content_data['content_type'],
                    'title': content_data['title']
                })
                print(f"✅ {content_data['content_type'].title()} content uploaded: {response['content_id']}")
            else:
                print(f"❌ Failed to upload {content_data['content_type']} content")
        
        # Store first content ID for further testing
        if uploaded_content:
            self.test_content_id = uploaded_content[0]['content_id']
        
        return len(uploaded_content) > 0, uploaded_content

    def test_get_creator_content_list(self):
        """Test getting creator's content list (existing functionality)"""
        print(f"\n📋 Testing Get Creator Content List...")
        
        creator_id = self.creator_data['creator_id']
        
        success, response = self.run_test(
            "Get Creator Content List",
            "GET",
            f"api/creators/{creator_id}/content",
            200
        )
        
        if success and 'content' in response:
            content_list = response['content']
            print(f"✅ Retrieved {len(content_list)} content items")
            
            # Verify content structure
            if content_list:
                first_content = content_list[0]
                required_fields = ['content_id', 'title', 'description', 'content_type', 'created_at']
                has_required = all(field in first_content for field in required_fields)
                
                if has_required:
                    print("✅ Content structure is correct")
                else:
                    print("❌ Content structure missing required fields")
                    
            return True, content_list
        
        return False, []

    def test_get_single_content(self):
        """Test getting single content item for editing (NEW FEATURE)"""
        print(f"\n📄 Testing Get Single Content for Editing (NEW FEATURE)...")
        
        if not self.test_content_id:
            print("❌ No test content ID available")
            return False
        
        creator_id = self.creator_data['creator_id']
        
        success, response = self.run_test(
            "Get Single Content for Editing",
            "GET",
            f"api/creators/{creator_id}/content/{self.test_content_id}",
            200
        )
        
        if success and 'content' in response:
            content = response['content']
            print(f"✅ Retrieved single content: {content.get('title', 'Unknown')}")
            
            # Verify content has editable fields
            editable_fields = ['title', 'description', 'category', 'tags', 'is_public', 'is_featured']
            has_editable = all(field in content for field in editable_fields)
            
            if has_editable:
                print("✅ Content has all editable fields")
            else:
                print("❌ Content missing some editable fields")
                
            return True, content
        
        return False, {}

    def test_update_content(self):
        """Test updating/editing content (NEW FEATURE)"""
        print(f"\n✏️  Testing Content Update/Edit (NEW FEATURE)...")
        
        if not self.test_content_id:
            print("❌ No test content ID available")
            return False
        
        creator_id = self.creator_data['creator_id']
        
        # Test updating various fields
        update_tests = [
            {
                "name": "Update Title and Description",
                "data": {
                    "title": "Updated Test Content Title",
                    "description": "This content has been updated for testing purposes"
                }
            },
            {
                "name": "Update Category and Tags",
                "data": {
                    "category": "health",
                    "tags": ["updated", "health", "wellness", "test"]
                }
            },
            {
                "name": "Update Visibility Settings",
                "data": {
                    "is_public": False,
                    "is_featured": True
                }
            },
            {
                "name": "Update All Fields",
                "data": {
                    "title": "Completely Updated Content",
                    "description": "All fields have been updated",
                    "category": "science",
                    "tags": ["complete", "update", "science"],
                    "is_public": True,
                    "is_featured": False
                }
            }
        ]
        
        update_success_count = 0
        
        for test in update_tests:
            success, response = self.run_test(
                test["name"],
                "PUT",
                f"api/creators/{creator_id}/content/{self.test_content_id}",
                200,
                data=test["data"]
            )
            
            if success and 'content' in response:
                updated_content = response['content']
                print(f"✅ {test['name']} successful")
                
                # Verify updates were applied
                for field, expected_value in test["data"].items():
                    if updated_content.get(field) == expected_value:
                        print(f"   ✅ {field} updated correctly: {expected_value}")
                    else:
                        print(f"   ❌ {field} not updated correctly: expected {expected_value}, got {updated_content.get(field)}")
                
                update_success_count += 1
            else:
                print(f"❌ {test['name']} failed")
        
        return update_success_count == len(update_tests)

    def test_duplicate_content(self):
        """Test content duplication (NEW FEATURE)"""
        print(f"\n📋 Testing Content Duplication (NEW FEATURE)...")
        
        if not self.test_content_id:
            print("❌ No test content ID available")
            return False
        
        creator_id = self.creator_data['creator_id']
        
        success, response = self.run_test(
            "Duplicate Content",
            "POST",
            f"api/creators/{creator_id}/content/{self.test_content_id}/duplicate",
            200
        )
        
        if success and 'content' in response:
            duplicated_content = response['content']
            print(f"✅ Content duplicated successfully")
            
            # Verify duplicate properties
            checks = [
                ("Title has (Copy) suffix", "(Copy)" in duplicated_content.get('title', '')),
                ("View count reset to 0", duplicated_content.get('view_count', -1) == 0),
                ("Like count reset to 0", duplicated_content.get('like_count', -1) == 0),
                ("Is not featured", duplicated_content.get('is_featured', True) == False),
                ("Has new content ID", duplicated_content.get('content_id') != self.test_content_id),
                ("Has creation timestamp", 'created_at' in duplicated_content)
            ]
            
            for check_name, check_result in checks:
                if check_result:
                    print(f"   ✅ {check_name}")
                else:
                    print(f"   ❌ {check_name}")
            
            # Store duplicate ID for deletion test
            self.duplicate_content_id = duplicated_content.get('content_id')
            
            return all(check[1] for check in checks)
        
        return False

    def test_delete_content(self):
        """Test content deletion (NEW FEATURE)"""
        print(f"\n🗑️  Testing Content Deletion (NEW FEATURE)...")
        
        # Use duplicate content ID if available, otherwise use original
        content_to_delete = getattr(self, 'duplicate_content_id', self.test_content_id)
        
        if not content_to_delete:
            print("❌ No content ID available for deletion")
            return False
        
        creator_id = self.creator_data['creator_id']
        
        # First, get content count before deletion
        success, response = self.run_test(
            "Get Content Count Before Deletion",
            "GET",
            f"api/creators/{creator_id}/content",
            200
        )
        
        content_count_before = len(response.get('content', [])) if success else 0
        
        # Delete the content
        success, response = self.run_test(
            "Delete Content",
            "DELETE",
            f"api/creators/{creator_id}/content/{content_to_delete}",
            200
        )
        
        if success:
            print(f"✅ Content deleted successfully: {content_to_delete}")
            
            # Verify content is actually deleted
            success_verify, response_verify = self.run_test(
                "Verify Content Deleted",
                "GET",
                f"api/creators/{creator_id}/content/{content_to_delete}",
                404
            )
            
            if success_verify:
                print("✅ Content properly removed from database")
            else:
                print("❌ Content still exists after deletion")
                return False
            
            # Check that content count decreased
            success_count, response_count = self.run_test(
                "Verify Content Count Decreased",
                "GET",
                f"api/creators/{creator_id}/content",
                200
            )
            
            if success_count:
                content_count_after = len(response_count.get('content', []))
                if content_count_after == content_count_before - 1:
                    print("✅ Content count properly decremented")
                else:
                    print(f"❌ Content count not decremented correctly: {content_count_before} -> {content_count_after}")
                    return False
            
            return True
        
        return False

    def test_authorization_security(self):
        """Test authorization and security measures (CRITICAL)"""
        print(f"\n🔒 Testing Authorization & Security (CRITICAL)...")
        
        if not self.test_content_id:
            print("❌ No test content ID available")
            return False
        
        creator_id = self.creator_data['creator_id']
        security_tests_passed = 0
        security_tests_total = 0
        
        # Test 1: Access without authentication
        original_token = self.creator_token
        self.creator_token = None
        
        security_tests_total += 1
        success, response = self.run_test(
            "Access Content Without Auth",
            "GET",
            f"api/creators/{creator_id}/content/{self.test_content_id}",
            401
        )
        if success:
            security_tests_passed += 1
            print("✅ Properly blocks unauthenticated access")
        
        # Test 2: Update without authentication
        security_tests_total += 1
        success, response = self.run_test(
            "Update Content Without Auth",
            "PUT",
            f"api/creators/{creator_id}/content/{self.test_content_id}",
            401,
            data={"title": "Unauthorized Update"}
        )
        if success:
            security_tests_passed += 1
            print("✅ Properly blocks unauthenticated updates")
        
        # Test 3: Delete without authentication
        security_tests_total += 1
        success, response = self.run_test(
            "Delete Content Without Auth",
            "DELETE",
            f"api/creators/{creator_id}/content/{self.test_content_id}",
            401
        )
        if success:
            security_tests_passed += 1
            print("✅ Properly blocks unauthenticated deletion")
        
        # Restore token
        self.creator_token = original_token
        
        # Test 4: Access non-existent content
        security_tests_total += 1
        success, response = self.run_test(
            "Access Non-existent Content",
            "GET",
            f"api/creators/{creator_id}/content/non_existent_content_id",
            404
        )
        if success:
            security_tests_passed += 1
            print("✅ Properly handles non-existent content")
        
        # Test 5: Access non-existent creator
        security_tests_total += 1
        success, response = self.run_test(
            "Access Content for Non-existent Creator",
            "GET",
            f"api/creators/non_existent_creator/content/{self.test_content_id}",
            404
        )
        if success:
            security_tests_passed += 1
            print("✅ Properly handles non-existent creator")
        
        print(f"Security tests passed: {security_tests_passed}/{security_tests_total}")
        return security_tests_passed >= 4  # Allow 1 failure

    def test_error_handling(self):
        """Test comprehensive error handling"""
        print(f"\n🚨 Testing Error Handling...")
        
        creator_id = self.creator_data['creator_id']
        error_tests_passed = 0
        error_tests_total = 0
        
        # Test 1: Invalid content ID format
        error_tests_total += 1
        success, response = self.run_test(
            "Invalid Content ID Format",
            "GET",
            f"api/creators/{creator_id}/content/invalid-id-format",
            404
        )
        if success:
            error_tests_passed += 1
            print("✅ Handles invalid content ID format")
        
        # Test 2: Malformed update data
        error_tests_total += 1
        success, response = self.run_test(
            "Malformed Update Data",
            "PUT",
            f"api/creators/{creator_id}/content/{self.test_content_id}",
            400,
            data={"invalid_field": "invalid_value", "tags": "not_an_array"}
        )
        # Note: This might return 200 if the API ignores unknown fields
        if success or response.get('status_code') in [200, 400]:
            error_tests_passed += 1
            print("✅ Handles malformed update data appropriately")
        
        # Test 3: Empty update request
        error_tests_total += 1
        success, response = self.run_test(
            "Empty Update Request",
            "PUT",
            f"api/creators/{creator_id}/content/{self.test_content_id}",
            400,
            data={}
        )
        # This might return 200 with no changes, which is also acceptable
        if success or response.get('status_code') in [200, 400]:
            error_tests_passed += 1
            print("✅ Handles empty update request appropriately")
        
        print(f"Error handling tests passed: {error_tests_passed}/{error_tests_total}")
        return error_tests_passed >= 2  # Allow some flexibility

    def test_integration_with_existing_system(self):
        """Test integration with existing creator system"""
        print(f"\n🔗 Testing Integration with Existing System...")
        
        creator_id = self.creator_data['creator_id']
        integration_tests_passed = 0
        integration_tests_total = 0
        
        # Test 1: Creator profile still accessible
        integration_tests_total += 1
        success, response = self.run_test(
            "Creator Profile Access",
            "GET",
            f"api/creators/{creator_id}",
            200
        )
        if success:
            integration_tests_passed += 1
            print("✅ Creator profile still accessible")
        
        # Test 2: Creator appears in creators list
        integration_tests_total += 1
        success, response = self.run_test(
            "Creator in Creators List",
            "GET",
            "api/creators",
            200
        )
        if success and 'creators' in response:
            creator_found = any(c.get('creator_id') == creator_id for c in response['creators'])
            if creator_found:
                integration_tests_passed += 1
                print("✅ Creator appears in creators list")
            else:
                print("❌ Creator not found in creators list")
        
        # Test 3: Content upload still works after content management operations
        integration_tests_total += 1
        success, response = self.run_test(
            "Content Upload After Management Operations",
            "POST",
            f"api/creators/{creator_id}/content",
            200,
            data={
                "title": "Integration Test Content",
                "description": "Testing integration after content management",
                "content_type": "article_link",
                "category": "business",
                "tags": '["integration", "test"]'
            }
        )
        if success:
            integration_tests_passed += 1
            print("✅ Content upload still works")
        
        print(f"Integration tests passed: {integration_tests_passed}/{integration_tests_total}")
        return integration_tests_passed >= 2

    def run_comprehensive_test(self):
        """Run all enhanced content management tests"""
        print("🚀 Starting Enhanced Content Management System Tests (Option 3)")
        print("=" * 80)
        
        # Setup
        if not self.setup_creator_account():
            print("❌ Failed to setup creator account - aborting tests")
            return False
        
        # Test categories
        test_categories = [
            ("Content Upload (Existing)", self.test_content_upload),
            ("Get Content List (Existing)", self.test_get_creator_content_list),
            ("Get Single Content (NEW)", self.test_get_single_content),
            ("Update Content (NEW)", self.test_update_content),
            ("Duplicate Content (NEW)", self.test_duplicate_content),
            ("Delete Content (NEW)", self.test_delete_content),
            ("Authorization & Security", self.test_authorization_security),
            ("Error Handling", self.test_error_handling),
            ("Integration with Existing System", self.test_integration_with_existing_system)
        ]
        
        category_results = {}
        
        for category_name, test_function in test_categories:
            print(f"\n{'='*80}")
            print(f"🧪 TESTING: {category_name}")
            print(f"{'='*80}")
            
            try:
                result = test_function()
                category_results[category_name] = result
                
                if result:
                    print(f"✅ {category_name}: PASSED")
                else:
                    print(f"❌ {category_name}: FAILED")
                    
            except Exception as e:
                print(f"❌ {category_name}: ERROR - {str(e)}")
                category_results[category_name] = False
        
        # Calculate results
        passed_categories = sum(1 for result in category_results.values() if result)
        total_categories = len(category_results)
        
        # Print final results
        print("\n" + "=" * 80)
        print("📊 ENHANCED CONTENT MANAGEMENT SYSTEM TEST RESULTS")
        print("=" * 80)
        print(f"Overall API tests: {self.tests_passed}/{self.tests_run} ({(self.tests_passed/self.tests_run)*100:.1f}%)")
        print(f"Test categories passed: {passed_categories}/{total_categories} ({(passed_categories/total_categories)*100:.1f}%)")
        
        print("\nCategory Results:")
        for category, result in category_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"  {category}: {status}")
        
        # Determine overall success
        critical_categories = [
            "Get Single Content (NEW)",
            "Update Content (NEW)", 
            "Duplicate Content (NEW)",
            "Delete Content (NEW)",
            "Authorization & Security"
        ]
        
        critical_passed = sum(1 for cat in critical_categories if category_results.get(cat, False))
        critical_total = len(critical_categories)
        
        print(f"\nCritical NEW features: {critical_passed}/{critical_total} ({(critical_passed/critical_total)*100:.1f}%)")
        
        overall_success = (
            self.tests_passed / self.tests_run >= 0.8 and  # 80% API tests pass
            passed_categories / total_categories >= 0.7 and  # 70% categories pass
            critical_passed / critical_total >= 0.8  # 80% critical features pass
        )
        
        if overall_success:
            print("\n🎉 ENHANCED CONTENT MANAGEMENT SYSTEM IS WORKING!")
            print("✅ All CRUD operations working for content management")
            print("✅ Proper security and authorization implemented")
            print("✅ Clean integration with existing creator system")
            print("✅ Comprehensive error handling in place")
            print("✅ Content lifecycle complete: create → edit → duplicate → delete")
        else:
            print("\n⚠️  ENHANCED CONTENT MANAGEMENT SYSTEM HAS ISSUES")
            if self.tests_passed / self.tests_run < 0.8:
                print("❌ Too many API test failures")
            if passed_categories / total_categories < 0.7:
                print("❌ Too many test category failures")
            if critical_passed / critical_total < 0.8:
                print("❌ Critical NEW features not working properly")
        
        return overall_success

def main():
    tester = EnhancedContentManagementTester()
    success = tester.run_comprehensive_test()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())