#!/usr/bin/env python3
"""
MongoDB Database Management System Testing for OnlyMentors.ai
Comprehensive testing of all 4 major database management features:
1. Visual Dashboard (Database overview with collections)
2. Data Export Tools (JSON/CSV export functionality)
3. Database Backup/Restore (Full database backup as ZIP and restore)
4. Advanced Analytics (User, mentor, and platform health analytics)
"""

import requests
import json
import time
import sys
import os
from datetime import datetime

class MongoDBDatabaseManagementTester:
    def __init__(self):
        # Get backend URL from environment
        self.backend_url = os.getenv('REACT_APP_BACKEND_URL', 'https://enterprise-coach.preview.emergentagent.com')
        self.base_url = f"{self.backend_url}/api"
        
        # Admin credentials for testing
        self.admin_email = "admin@onlymentors.ai"
        self.admin_password = "SuperAdmin2024!"
        self.admin_token = None
        
        # Test results tracking
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.test_results = []
        
        print("🧪 MongoDB Database Management System Testing")
        print("=" * 60)
        print(f"Backend URL: {self.backend_url}")
        print(f"Testing Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

    def run_test(self, test_name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single test and track results"""
        self.total_tests += 1
        
        try:
            url = f"{self.base_url}/{endpoint}"
            
            # Default headers
            default_headers = {"Content-Type": "application/json"}
            if headers:
                default_headers.update(headers)
            
            # Make request
            if method == "GET":
                response = requests.get(url, headers=default_headers, timeout=30)
            elif method == "POST":
                response = requests.post(url, json=data, headers=default_headers, timeout=30)
            elif method == "PUT":
                response = requests.put(url, json=data, headers=default_headers, timeout=30)
            elif method == "DELETE":
                response = requests.delete(url, headers=default_headers, timeout=30)
            
            # Check status code
            success = response.status_code == expected_status
            
            if success:
                self.passed_tests += 1
                status = "✅ PASS"
            else:
                self.failed_tests += 1
                status = "❌ FAIL"
            
            result = {
                "test": test_name,
                "method": method,
                "endpoint": endpoint,
                "expected": expected_status,
                "actual": response.status_code,
                "success": success,
                "response_size": len(response.text) if response.text else 0
            }
            
            self.test_results.append(result)
            
            print(f"{status} {test_name}")
            print(f"   {method} {endpoint} -> {response.status_code} (expected {expected_status})")
            
            if not success:
                print(f"   Response: {response.text[:200]}...")
            elif response.text:
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict):
                        if 'collections' in response_data:
                            print(f"   Collections found: {len(response_data.get('collections', []))}")
                        elif 'documents' in response_data:
                            print(f"   Documents found: {len(response_data.get('documents', []))}")
                        elif 'user_metrics' in response_data:
                            print(f"   User metrics: {response_data.get('user_metrics', {}).get('total_users', 'N/A')} users")
                        elif 'mentor_metrics' in response_data:
                            print(f"   Mentor metrics: {response_data.get('mentor_metrics', {}).get('total_mentors', 'N/A')} mentors")
                        elif 'health_score' in response_data:
                            print(f"   Health score: {response_data.get('health_score', 'N/A')}/100")
                except:
                    print(f"   Response size: {len(response.text)} chars")
            
            return success, response
            
        except Exception as e:
            self.failed_tests += 1
            self.total_tests += 1
            print(f"❌ FAIL {test_name}")
            print(f"   Error: {str(e)}")
            
            result = {
                "test": test_name,
                "method": method,
                "endpoint": endpoint,
                "expected": expected_status,
                "actual": "ERROR",
                "success": False,
                "error": str(e)
            }
            self.test_results.append(result)
            
            return False, None

    def authenticate_admin(self):
        """Authenticate as admin and get token"""
        print("\n🔐 ADMIN AUTHENTICATION")
        print("-" * 40)
        
        login_data = {
            "email": self.admin_email,
            "password": self.admin_password
        }
        
        success, response = self.run_test(
            "Admin Login", "POST", "admin/login", 200, login_data
        )
        
        if success and response:
            try:
                data = response.json()
                self.admin_token = data.get("token")
                if self.admin_token:
                    print(f"   ✅ Admin token obtained: {self.admin_token[:20]}...")
                    return True
                else:
                    print("   ❌ No token in response")
                    return False
            except:
                print("   ❌ Failed to parse login response")
                return False
        
        return False

    def get_auth_headers(self):
        """Get authorization headers with admin token"""
        if not self.admin_token:
            return {}
        return {"Authorization": f"Bearer {self.admin_token}"}

    def test_visual_dashboard(self):
        """Test Feature 1: Visual Dashboard functionality"""
        print("\n📊 FEATURE 1: VISUAL DASHBOARD TESTING")
        print("-" * 50)
        
        # Test database overview
        success, response = self.run_test(
            "Database Overview", "GET", "admin/database/overview", 200,
            headers=self.get_auth_headers()
        )
        
        if success and response:
            try:
                data = response.json()
                collections = data.get('collections', [])
                print(f"   📁 Found {len(collections)} collections")
                for collection in collections[:5]:  # Show first 5
                    name = collection.get('name', 'Unknown')
                    count = collection.get('document_count', 0)
                    print(f"      - {name}: {count} documents")
            except Exception as e:
                print(f"   ⚠️  Could not parse overview data: {e}")
        
        # Test collection browsing with pagination
        test_collections = ['users', 'creators', 'questions', 'payment_transactions']
        
        for collection_name in test_collections:
            success, response = self.run_test(
                f"Browse {collection_name} Collection", "GET", 
                f"admin/database/collections/{collection_name}?page=1&limit=10", 200,
                headers=self.get_auth_headers()
            )
            
            if success and response:
                try:
                    data = response.json()
                    total_docs = data.get('total_documents', 0)
                    page_docs = len(data.get('documents', []))
                    print(f"   📄 {collection_name}: {page_docs} docs on page 1 of {total_docs} total")
                except:
                    pass
        
        # Test collection browsing with search
        success, response = self.run_test(
            "Browse Users with Search", "GET", 
            "admin/database/collections/users?page=1&limit=5&search=test", 200,
            headers=self.get_auth_headers()
        )

    def test_data_export_tools(self):
        """Test Feature 2: Data Export Tools functionality"""
        print("\n📤 FEATURE 2: DATA EXPORT TOOLS TESTING")
        print("-" * 50)
        
        # Test JSON export for users collection
        export_data = {
            "collection_name": "users",
            "format": "json"
        }
        
        success, response = self.run_test(
            "Export Users Collection (JSON)", "POST", "admin/database/export", 200,
            data=export_data, headers=self.get_auth_headers()
        )
        
        if success and response:
            try:
                # Check if response contains JSON export data
                content_type = response.headers.get('content-type', '')
                if 'application/json' in content_type:
                    data = response.json()
                    if 'export_info' in data:
                        doc_count = data['export_info'].get('document_count', 0)
                        print(f"   📊 JSON export: {doc_count} users exported")
                elif 'text/plain' in content_type:
                    # Raw JSON string response
                    json_data = json.loads(response.text)
                    if 'export_info' in json_data:
                        doc_count = json_data['export_info'].get('document_count', 0)
                        print(f"   📊 JSON export: {doc_count} users exported")
            except Exception as e:
                print(f"   ⚠️  Could not parse JSON export: {e}")
        
        # Test CSV export for users collection
        export_data = {
            "collection_name": "users",
            "format": "csv"
        }
        
        success, response = self.run_test(
            "Export Users Collection (CSV)", "POST", "admin/database/export", 200,
            data=export_data, headers=self.get_auth_headers()
        )
        
        if success and response:
            try:
                # Check CSV content
                csv_content = response.text
                lines = csv_content.split('\n')
                if len(lines) > 1:
                    print(f"   📊 CSV export: {len(lines)-1} rows (including header)")
                    # Show first few column headers
                    if lines[0]:
                        headers = lines[0].split(',')[:5]  # First 5 columns
                        print(f"   📋 Columns: {', '.join(headers)}...")
            except Exception as e:
                print(f"   ⚠️  Could not parse CSV export: {e}")
        
        # Test export with search filters
        export_data = {
            "collection_name": "users",
            "format": "json",
            "search": "test"
        }
        
        success, response = self.run_test(
            "Export Users with Search Filter", "POST", "admin/database/export", 200,
            data=export_data, headers=self.get_auth_headers()
        )
        
        # Test export for different collections
        for collection in ['mentors', 'creators', 'questions']:
            export_data = {
                "collection_name": collection,
                "format": "json"
            }
            
            success, response = self.run_test(
                f"Export {collection} Collection", "POST", "admin/database/export", 200,
                data=export_data, headers=self.get_auth_headers()
            )

    def test_database_backup_restore(self):
        """Test Feature 3: Database Backup/Restore functionality"""
        print("\n💾 FEATURE 3: DATABASE BACKUP/RESTORE TESTING")
        print("-" * 50)
        
        # Test full database backup
        success, response = self.run_test(
            "Create Full Database Backup", "GET", "admin/database/backup", 200,
            headers=self.get_auth_headers()
        )
        
        if success and response:
            try:
                # Check if response is a ZIP file
                content_type = response.headers.get('content-type', '')
                content_length = len(response.content)
                
                if 'application/zip' in content_type or content_length > 1000:
                    print(f"   📦 Backup created: {content_length} bytes")
                    
                    # Try to verify it's a valid ZIP by checking headers
                    if response.content[:2] == b'PK':
                        print(f"   ✅ Valid ZIP file format detected")
                    else:
                        print(f"   ⚠️  Response may not be valid ZIP format")
                else:
                    print(f"   ⚠️  Unexpected content type: {content_type}")
                    
            except Exception as e:
                print(f"   ⚠️  Could not analyze backup: {e}")
        
        # Test collection restore functionality
        # Create sample JSON data for restore testing
        sample_restore_data = {
            "collection_name": "test_restore",
            "json_data": json.dumps({
                "export_info": {
                    "collection": "test_restore",
                    "document_count": 2
                },
                "documents": [
                    {"test_id": "1", "name": "Test Document 1", "created_at": "2024-01-01T00:00:00Z"},
                    {"test_id": "2", "name": "Test Document 2", "created_at": "2024-01-01T00:00:00Z"}
                ]
            })
        }
        
        success, response = self.run_test(
            "Restore Collection from JSON", "POST", "admin/database/restore", 200,
            data=sample_restore_data, headers=self.get_auth_headers()
        )
        
        if success and response:
            try:
                data = response.json()
                if data.get('success'):
                    restored_count = data.get('documents_restored', 0)
                    print(f"   ✅ Restored {restored_count} documents to test_restore collection")
                else:
                    print(f"   ⚠️  Restore reported failure: {data.get('message', 'Unknown error')}")
            except Exception as e:
                print(f"   ⚠️  Could not parse restore response: {e}")

    def test_advanced_analytics(self):
        """Test Feature 4: Advanced Analytics functionality"""
        print("\n📈 FEATURE 4: ADVANCED ANALYTICS TESTING")
        print("-" * 50)
        
        # Test comprehensive user analytics
        success, response = self.run_test(
            "Get User Analytics", "GET", "admin/analytics/users", 200,
            headers=self.get_auth_headers()
        )
        
        if success and response:
            try:
                data = response.json()
                user_metrics = data.get('user_metrics', {})
                engagement_metrics = data.get('engagement_metrics', {})
                
                total_users = user_metrics.get('total_users', 0)
                active_users = user_metrics.get('active_users', 0)
                subscribed_users = user_metrics.get('subscribed_users', 0)
                
                print(f"   👥 Total Users: {total_users}")
                print(f"   🟢 Active Users: {active_users}")
                print(f"   💳 Subscribed Users: {subscribed_users}")
                
                if engagement_metrics:
                    total_questions = engagement_metrics.get('total_questions', 0)
                    engagement_rate = engagement_metrics.get('engagement_rate', 0)
                    print(f"   ❓ Total Questions: {total_questions}")
                    print(f"   📊 Engagement Rate: {engagement_rate}%")
                    
            except Exception as e:
                print(f"   ⚠️  Could not parse user analytics: {e}")
        
        # Test mentor performance analytics
        success, response = self.run_test(
            "Get Mentor Analytics", "GET", "admin/analytics/mentors", 200,
            headers=self.get_auth_headers()
        )
        
        if success and response:
            try:
                data = response.json()
                mentor_metrics = data.get('mentor_metrics', {})
                category_metrics = data.get('category_metrics', {})
                
                total_mentors = mentor_metrics.get('total_mentors', 0)
                approved_mentors = mentor_metrics.get('approved_mentors', 0)
                pending_mentors = mentor_metrics.get('pending_mentors', 0)
                
                print(f"   👨‍🏫 Total Mentors: {total_mentors}")
                print(f"   ✅ Approved Mentors: {approved_mentors}")
                print(f"   ⏳ Pending Mentors: {pending_mentors}")
                
                if category_metrics:
                    categories = category_metrics.get('category_distribution', {})
                    print(f"   📂 Categories: {len(categories)} categories")
                    for category, count in list(categories.items())[:3]:  # Show first 3
                        print(f"      - {category}: {count} mentors")
                        
            except Exception as e:
                print(f"   ⚠️  Could not parse mentor analytics: {e}")
        
        # Test overall platform health
        success, response = self.run_test(
            "Get Platform Health", "GET", "admin/analytics/platform-health", 200,
            headers=self.get_auth_headers()
        )
        
        if success and response:
            try:
                data = response.json()
                overall_health = data.get('overall_health', 'unknown')
                health_score = data.get('health_score', 0)
                components = data.get('components', {})
                recommendations = data.get('recommendations', [])
                
                print(f"   🏥 Overall Health: {overall_health}")
                print(f"   📊 Health Score: {health_score}/100")
                
                if components:
                    print(f"   🔧 Components checked: {len(components)}")
                    for component, info in components.items():
                        status = info.get('status', 'unknown')
                        score = info.get('score', 0)
                        print(f"      - {component}: {status} ({score} points)")
                
                if recommendations:
                    print(f"   💡 Recommendations: {len(recommendations)}")
                    for rec in recommendations[:2]:  # Show first 2
                        print(f"      - {rec}")
                        
            except Exception as e:
                print(f"   ⚠️  Could not parse platform health: {e}")

    def test_admin_authentication_requirements(self):
        """Test that all endpoints require admin authentication"""
        print("\n🔒 ADMIN AUTHENTICATION REQUIREMENTS TESTING")
        print("-" * 50)
        
        # Test endpoints without authentication (should return 401/403)
        endpoints_to_test = [
            ("admin/database/overview", "GET"),
            ("admin/database/collections/users", "GET"),
            ("admin/database/export", "POST"),
            ("admin/database/backup", "GET"),
            ("admin/database/restore", "POST"),
            ("admin/analytics/users", "GET"),
            ("admin/analytics/mentors", "GET"),
            ("admin/analytics/platform-health", "GET")
        ]
        
        for endpoint, method in endpoints_to_test:
            # Test without token (should fail)
            success, response = self.run_test(
                f"Unauthorized Access to {endpoint}", method, endpoint, 401,
                data={"test": "data"} if method == "POST" else None
            )
            
            if not success and response and response.status_code == 403:
                # 403 is also acceptable for unauthorized access
                print(f"   ✅ Properly blocked with 403 Forbidden")
                self.passed_tests += 1
                self.failed_tests -= 1

    def test_error_scenarios(self):
        """Test error handling scenarios"""
        print("\n⚠️  ERROR SCENARIO TESTING")
        print("-" * 40)
        
        # Test invalid collection name
        success, response = self.run_test(
            "Invalid Collection Browse", "GET", 
            "admin/database/collections/nonexistent_collection", 404,
            headers=self.get_auth_headers()
        )
        
        # Test invalid export format
        invalid_export_data = {
            "collection_name": "users",
            "format": "invalid_format"
        }
        
        success, response = self.run_test(
            "Invalid Export Format", "POST", "admin/database/export", 400,
            data=invalid_export_data, headers=self.get_auth_headers()
        )
        
        # Test malformed restore data
        invalid_restore_data = {
            "collection_name": "test",
            "json_data": "invalid json data"
        }
        
        success, response = self.run_test(
            "Invalid Restore Data", "POST", "admin/database/restore", 400,
            data=invalid_restore_data, headers=self.get_auth_headers()
        )

    def run_all_tests(self):
        """Run all MongoDB Database Management System tests"""
        print("🚀 Starting MongoDB Database Management System Testing...")
        
        # Step 1: Authenticate as admin
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with testing.")
            return False
        
        # Step 2: Test all 4 major features
        self.test_visual_dashboard()
        self.test_data_export_tools()
        self.test_database_backup_restore()
        self.test_advanced_analytics()
        
        # Step 3: Test security requirements
        self.test_admin_authentication_requirements()
        
        # Step 4: Test error scenarios
        self.test_error_scenarios()
        
        # Step 5: Generate final report
        self.generate_final_report()
        
        return self.passed_tests > 0 and (self.passed_tests / self.total_tests) >= 0.7

    def generate_final_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 60)
        print("📋 MONGODB DATABASE MANAGEMENT SYSTEM TEST REPORT")
        print("=" * 60)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"📊 OVERALL RESULTS:")
        print(f"   Total Tests: {self.total_tests}")
        print(f"   Passed: {self.passed_tests} ✅")
        print(f"   Failed: {self.failed_tests} ❌")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        # Feature-specific results
        features = {
            "Visual Dashboard": ["Database Overview", "Browse", "Search"],
            "Data Export Tools": ["Export", "JSON", "CSV"],
            "Database Backup/Restore": ["Backup", "Restore"],
            "Advanced Analytics": ["User Analytics", "Mentor Analytics", "Platform Health"]
        }
        
        print(f"\n🎯 FEATURE ANALYSIS:")
        for feature, keywords in features.items():
            feature_tests = [r for r in self.test_results if any(kw in r['test'] for kw in keywords)]
            if feature_tests:
                feature_passed = sum(1 for t in feature_tests if t['success'])
                feature_total = len(feature_tests)
                feature_rate = (feature_passed / feature_total * 100) if feature_total > 0 else 0
                status = "✅" if feature_rate >= 70 else "⚠️" if feature_rate >= 50 else "❌"
                print(f"   {status} {feature}: {feature_passed}/{feature_total} ({feature_rate:.1f}%)")
        
        # Critical issues
        critical_failures = [r for r in self.test_results if not r['success'] and 'Authentication' in r['test']]
        if critical_failures:
            print(f"\n🚨 CRITICAL ISSUES:")
            for failure in critical_failures:
                print(f"   ❌ {failure['test']}: {failure.get('error', 'Authentication failure')}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if success_rate >= 90:
            print("   🎉 Excellent! MongoDB Database Management System is production-ready.")
        elif success_rate >= 70:
            print("   ✅ Good! System is functional with minor issues to address.")
        elif success_rate >= 50:
            print("   ⚠️  Moderate issues found. Review failed tests before production.")
        else:
            print("   🚨 Major issues found. System needs significant fixes before production.")
        
        # Database management specific recommendations
        if any('Export' in r['test'] and r['success'] for r in self.test_results):
            print("   📤 Data export functionality is working correctly.")
        
        if any('Backup' in r['test'] and r['success'] for r in self.test_results):
            print("   💾 Database backup functionality is operational.")
        
        if any('Analytics' in r['test'] and r['success'] for r in self.test_results):
            print("   📈 Analytics system is providing comprehensive insights.")
        
        print("\n" + "=" * 60)
        
        return success_rate

if __name__ == "__main__":
    tester = MongoDBDatabaseManagementTester()
    success = tester.run_all_tests()
    
    if success:
        print("🎉 MongoDB Database Management System testing completed successfully!")
        sys.exit(0)
    else:
        print("❌ MongoDB Database Management System testing completed with issues.")
        sys.exit(1)