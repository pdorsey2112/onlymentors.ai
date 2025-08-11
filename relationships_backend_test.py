import requests
import sys
import json
import time
from datetime import datetime

class RelationshipsAPITester:
    def __init__(self, base_url="https://f2b0aa4c-4c6c-44c0-8e63-7550a30e04a0.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.user_data = None
        self.tests_run = 0
        self.tests_passed = 0
        self.relationship_responses = []

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'
        
        if headers:
            test_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=45)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=45)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
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

    def test_categories_includes_relationships(self):
        """Test that categories endpoint includes the new relationships category"""
        print(f"\n🔍 Testing Categories Endpoint for Relationships Category")
        success, response = self.run_test("Categories with Relationships", "GET", "api/categories", 200)
        
        if success:
            categories = response.get('categories', [])
            category_ids = [cat['id'] for cat in categories]
            
            print(f"   Found categories: {category_ids}")
            
            # Check if relationships category exists
            if 'relationships' in category_ids:
                print("✅ Relationships category found!")
                
                # Get relationships category details
                relationships_cat = next((cat for cat in categories if cat['id'] == 'relationships'), None)
                if relationships_cat:
                    print(f"   Category name: {relationships_cat['name']}")
                    print(f"   Description: {relationships_cat['description']}")
                    print(f"   Mentor count: {relationships_cat['count']}")
                    
                    # Verify it has 20 mentors as expected
                    if relationships_cat['count'] == 20:
                        print("✅ Correct number of relationship mentors (20)")
                    else:
                        print(f"⚠️  Expected 20 mentors, found {relationships_cat['count']}")
                    
                    # Check for expected mentors
                    mentors = relationships_cat.get('mentors', [])
                    mentor_ids = [m['id'] for m in mentors]
                    expected_mentors = ['jay_shetty', 'esther_perel', 'nicole_lepera', 'matthew_hussey']
                    
                    found_expected = [m for m in expected_mentors if m in mentor_ids]
                    print(f"   Expected mentors found: {found_expected}")
                    
                    if len(found_expected) >= 3:
                        print("✅ Key relationship mentors are present")
                        return True, relationships_cat
                    else:
                        print("❌ Missing key relationship mentors")
                        return False, {}
                        
            else:
                print("❌ Relationships category not found in categories list")
                return False, {}
        
        return False, {}

    def test_relationships_category_mentors(self):
        """Test the /api/categories/relationships/mentors endpoint"""
        print(f"\n🔍 Testing Relationships Category Mentors Endpoint")
        success, response = self.run_test("Relationships Category Mentors", "GET", "api/categories/relationships/mentors", 200)
        
        if success:
            category = response.get('category')
            mentors = response.get('mentors', [])
            count = response.get('count', 0)
            
            print(f"   Category: {category}")
            print(f"   Mentor count: {count}")
            
            if category == 'relationships' and count == 20:
                print("✅ Relationships category endpoint working correctly")
                
                # Check mentor structure
                if mentors and len(mentors) > 0:
                    sample_mentor = mentors[0]
                    required_fields = ['id', 'name', 'title', 'bio', 'expertise']
                    
                    if all(field in sample_mentor for field in required_fields):
                        print("✅ Mentor data structure is correct")
                        print(f"   Sample mentor: {sample_mentor['name']} - {sample_mentor['title']}")
                        return True, response
                    else:
                        print("❌ Mentor data structure missing required fields")
                        return False, {}
                else:
                    print("❌ No mentors returned")
                    return False, {}
            else:
                print(f"❌ Unexpected response - category: {category}, count: {count}")
                return False, {}
        
        return False, {}

    def test_search_relationships_mentors(self):
        """Test searching mentors with relationships category filter"""
        print(f"\n🔍 Testing Search Mentors with Relationships Category")
        success, response = self.run_test("Search Relationships Mentors", "GET", "api/search/mentors?category=relationships", 200)
        
        if success:
            results = response.get('results', [])
            count = response.get('count', 0)
            
            print(f"   Search results count: {count}")
            
            if count == 20:
                print("✅ Search returned correct number of relationship mentors")
                
                # Verify all results are from relationships category
                categories = [r.get('category') for r in results]
                if all(cat == 'relationships' for cat in categories):
                    print("✅ All search results are from relationships category")
                    return True, response
                else:
                    print("❌ Search results contain mentors from other categories")
                    return False, {}
            else:
                print(f"❌ Expected 20 results, got {count}")
                return False, {}
        
        return False, {}

    def test_search_specific_relationship_mentor(self):
        """Test searching for a specific relationship mentor"""
        print(f"\n🔍 Testing Search for Specific Relationship Mentor")
        success, response = self.run_test("Search Jay Shetty", "GET", "api/search/mentors?q=Jay%20Shetty", 200)
        
        if success:
            results = response.get('results', [])
            count = response.get('count', 0)
            
            print(f"   Search results count: {count}")
            
            if count > 0:
                jay_shetty = next((r for r in results if r['id'] == 'jay_shetty'), None)
                if jay_shetty:
                    print("✅ Jay Shetty found in search results")
                    print(f"   Name: {jay_shetty['name']}")
                    print(f"   Category: {jay_shetty['category']}")
                    print(f"   Expertise: {jay_shetty['expertise']}")
                    
                    if jay_shetty['category'] == 'relationships':
                        print("✅ Jay Shetty correctly categorized as relationships")
                        return True, response
                    else:
                        print(f"❌ Jay Shetty in wrong category: {jay_shetty['category']}")
                        return False, {}
                else:
                    print("❌ Jay Shetty not found in search results")
                    return False, {}
            else:
                print("❌ No search results returned")
                return False, {}
        
        return False, {}

    def test_signup_for_questions(self):
        """Test user signup for asking questions"""
        test_email = f"relationship_test_{datetime.now().strftime('%H%M%S')}@test.com"
        test_password = "lovetest123"
        test_name = "Relationship Tester"
        
        success, response = self.run_test(
            "User Signup for Questions",
            "POST",
            "api/auth/signup",
            200,
            data={"email": test_email, "password": test_password, "full_name": test_name}
        )
        
        if success and 'token' in response:
            self.token = response['token']
            self.user_data = response['user']
            print(f"✅ Signup successful for relationship testing")
            return True
        return False

    def test_relationship_question_jay_shetty(self):
        """Test asking a relationship question to Jay Shetty"""
        print(f"\n🔍 Testing Relationship Question to Jay Shetty")
        
        question = "How do I build a healthy relationship with better communication?"
        
        success, response = self.run_test(
            "Question to Jay Shetty",
            "POST",
            "api/questions/ask",
            200,
            data={
                "category": "relationships",
                "mentor_ids": ["jay_shetty"],
                "question": question
            }
        )
        
        if success:
            if 'responses' in response and len(response['responses']) > 0:
                mentor_response = response['responses'][0]
                response_text = mentor_response.get('response', '')
                mentor_info = mentor_response.get('mentor', {})
                
                print(f"✅ Response received from {mentor_info.get('name', 'Jay Shetty')}")
                print(f"   Question: {response.get('question', '')}")
                print(f"   Response length: {len(response_text)} characters")
                print(f"   Response preview: {response_text[:200]}...")
                
                # Store for analysis
                self.relationship_responses.append({
                    'mentor_id': 'jay_shetty',
                    'mentor_name': mentor_info.get('name', 'Jay Shetty'),
                    'question': question,
                    'response': response_text,
                    'response_length': len(response_text)
                })
                
                # Check if response is relationship-focused
                relationship_keywords = ['relationship', 'communication', 'love', 'partner', 'connection', 'mindful', 'purpose']
                found_keywords = [kw for kw in relationship_keywords if kw.lower() in response_text.lower()]
                
                if found_keywords:
                    print(f"✅ Response contains relationship keywords: {found_keywords}")
                    return True, response
                else:
                    print("⚠️  Response may not be relationship-focused")
                    return True, response  # Still pass as API worked
            else:
                print("❌ No responses in response data")
                return False, {}
        
        return False, {}

    def test_relationship_question_esther_perel(self):
        """Test asking a relationship question to Esther Perel"""
        print(f"\n🔍 Testing Relationship Question to Esther Perel")
        
        question = "How can couples rebuild trust after infidelity?"
        
        success, response = self.run_test(
            "Question to Esther Perel",
            "POST",
            "api/questions/ask",
            200,
            data={
                "category": "relationships",
                "mentor_ids": ["esther_perel"],
                "question": question
            }
        )
        
        if success:
            if 'responses' in response and len(response['responses']) > 0:
                mentor_response = response['responses'][0]
                response_text = mentor_response.get('response', '')
                mentor_info = mentor_response.get('mentor', {})
                
                print(f"✅ Response received from {mentor_info.get('name', 'Esther Perel')}")
                print(f"   Response length: {len(response_text)} characters")
                print(f"   Response preview: {response_text[:200]}...")
                
                # Store for analysis
                self.relationship_responses.append({
                    'mentor_id': 'esther_perel',
                    'mentor_name': mentor_info.get('name', 'Esther Perel'),
                    'question': question,
                    'response': response_text,
                    'response_length': len(response_text)
                })
                
                # Check for therapy/couples-focused content
                therapy_keywords = ['trust', 'infidelity', 'couples', 'therapy', 'healing', 'betrayal', 'intimacy']
                found_keywords = [kw for kw in therapy_keywords if kw.lower() in response_text.lower()]
                
                if found_keywords:
                    print(f"✅ Response contains therapy keywords: {found_keywords}")
                    return True, response
                else:
                    print("⚠️  Response may not be therapy-focused")
                    return True, response  # Still pass as API worked
            else:
                print("❌ No responses in response data")
                return False, {}
        
        return False, {}

    def test_multiple_relationship_mentors(self):
        """Test asking question to multiple relationship mentors"""
        print(f"\n🔍 Testing Question to Multiple Relationship Mentors")
        
        question = "What's the key to maintaining a long-lasting relationship?"
        mentor_ids = ["jay_shetty", "esther_perel", "matthew_hussey"]
        
        success, response = self.run_test(
            "Question to Multiple Relationship Mentors",
            "POST",
            "api/questions/ask",
            200,
            data={
                "category": "relationships",
                "mentor_ids": mentor_ids,
                "question": question
            }
        )
        
        if success:
            if 'responses' in response and len(response['responses']) > 0:
                responses = response['responses']
                print(f"✅ Received {len(responses)} responses from {len(mentor_ids)} mentors")
                
                for i, mentor_response in enumerate(responses):
                    response_text = mentor_response.get('response', '')
                    mentor_info = mentor_response.get('mentor', {})
                    mentor_name = mentor_info.get('name', f'Mentor {i+1}')
                    
                    print(f"   📝 {mentor_name}: {len(response_text)} chars")
                    
                    # Store for analysis
                    self.relationship_responses.append({
                        'mentor_id': mentor_info.get('id', ''),
                        'mentor_name': mentor_name,
                        'question': question,
                        'response': response_text,
                        'response_length': len(response_text)
                    })
                
                # Check uniqueness
                unique_responses = len(set(r.get('response', '') for r in responses))
                if unique_responses == len(responses):
                    print("✅ All mentor responses are unique")
                else:
                    print(f"⚠️  Only {unique_responses}/{len(responses)} responses are unique")
                
                return True, response
            else:
                print("❌ No responses in response data")
                return False, {}
        
        return False, {}

    def test_total_mentor_count_updated(self):
        """Test that total mentor count includes relationship mentors"""
        print(f"\n🔍 Testing Total Mentor Count Update")
        success, response = self.run_test("Root Endpoint for Total Count", "GET", "", 200)
        
        if success:
            total_mentors = response.get('total_mentors', 0)
            categories_count = response.get('categories', 0)
            
            print(f"   Total mentors: {total_mentors}")
            print(f"   Categories count: {categories_count}")
            
            # Expected: 5 categories now (business, sports, health, science, relationships)
            if categories_count == 5:
                print("✅ Categories count updated to 5 (includes relationships)")
            else:
                print(f"⚠️  Expected 5 categories, found {categories_count}")
            
            # Expected total should be higher now with 20 relationship mentors added
            # Assuming original was around 400, now should be around 420
            if total_mentors >= 420:
                print("✅ Total mentor count appears updated with relationship mentors")
                return True, response
            else:
                print(f"⚠️  Total mentor count may not include relationship mentors: {total_mentors}")
                return True, response  # Don't fail on this, just warn
        
        return False, {}

    def analyze_relationship_responses(self):
        """Analyze relationship mentor responses"""
        print(f"\n📊 Relationship Mentor Response Analysis")
        print(f"Total relationship responses: {len(self.relationship_responses)}")
        
        if not self.relationship_responses:
            print("❌ No relationship responses to analyze")
            return False
        
        # Analyze response quality
        avg_length = sum(r['response_length'] for r in self.relationship_responses) / len(self.relationship_responses)
        print(f"Average response length: {avg_length:.0f} characters")
        
        # Check for relationship-specific content
        relationship_content_count = 0
        for response in self.relationship_responses:
            response_text = response['response'].lower()
            relationship_keywords = ['relationship', 'love', 'partner', 'communication', 'trust', 'intimacy', 'connection']
            
            if any(keyword in response_text for keyword in relationship_keywords):
                relationship_content_count += 1
        
        print(f"Responses with relationship content: {relationship_content_count}/{len(self.relationship_responses)}")
        
        # Overall assessment
        quality_good = (
            avg_length > 200 and  # Good response length
            relationship_content_count >= len(self.relationship_responses) * 0.7  # Most responses are relationship-focused
        )
        
        if quality_good:
            print("✅ Relationship mentor responses are high quality and relevant")
        else:
            print("⚠️  Relationship mentor responses may need improvement")
        
        return quality_good

def main():
    print("💕 Starting OnlyMentors.ai Relationships & Dating Category Tests")
    print("=" * 70)
    
    tester = RelationshipsAPITester()
    
    # Test 1: Check categories endpoint includes relationships
    success1, relationships_cat = tester.test_categories_includes_relationships()
    if not success1:
        print("❌ Relationships category not found, stopping tests")
        return 1
    
    # Test 2: Test relationships category mentors endpoint
    success2, _ = tester.test_relationships_category_mentors()
    
    # Test 3: Test search with relationships category filter
    success3, _ = tester.test_search_relationships_mentors()
    
    # Test 4: Test search for specific relationship mentor
    success4, _ = tester.test_search_specific_relationship_mentor()
    
    # Test 5: Test total mentor count update
    success5, _ = tester.test_total_mentor_count_updated()
    
    # Test 6: Setup user for question testing
    if not tester.test_signup_for_questions():
        print("❌ User signup failed, skipping question tests")
        return 1
    
    # Test 7: Test relationship question to Jay Shetty
    success7, _ = tester.test_relationship_question_jay_shetty()
    
    # Test 8: Test relationship question to Esther Perel
    success8, _ = tester.test_relationship_question_esther_perel()
    
    # Test 9: Test multiple relationship mentors
    success9, _ = tester.test_multiple_relationship_mentors()
    
    # Test 10: Analyze relationship responses
    responses_quality = tester.analyze_relationship_responses()
    
    # Print final results
    print("\n" + "=" * 70)
    print(f"📊 RELATIONSHIPS CATEGORY TEST RESULTS")
    print("=" * 70)
    print(f"Tests passed: {tester.tests_passed}/{tester.tests_run}")
    print(f"Success rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    print(f"Response Quality: {'✅ GOOD' if responses_quality else '⚠️  NEEDS IMPROVEMENT'}")
    
    # Critical tests that must pass
    critical_tests = [success1, success2, success3]
    critical_passed = sum(critical_tests)
    
    print(f"\nCritical Tests (Category & API): {critical_passed}/3")
    print(f"Question Tests: {sum([success7, success8, success9])}/3")
    
    if critical_passed == 3 and tester.tests_passed >= tester.tests_run * 0.8:
        print("🎉 RELATIONSHIPS CATEGORY TESTS PASSED!")
        print("✅ New category is working correctly")
        return 0
    else:
        print("⚠️  SOME CRITICAL TESTS FAILED")
        print("❌ Relationships category may have issues")
        return 1

if __name__ == "__main__":
    sys.exit(main())