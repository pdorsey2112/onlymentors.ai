import requests
import sys
import json
import time
from datetime import datetime

class DetailedPerformanceTester:
    def __init__(self, base_url="https://admin-console-4.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        
    def setup_auth(self):
        """Setup authentication"""
        test_email = f"detailed_test_{datetime.now().strftime('%H%M%S')}@test.com"
        response = requests.post(
            f"{self.base_url}/api/auth/signup",
            json={"email": test_email, "password": "password123", "full_name": "Detailed Test User"},
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        if response.status_code == 200:
            self.token = response.json()['token']
            return True
        return False
    
    def test_cache_behavior_detailed(self):
        """Test caching behavior with detailed analysis"""
        print("\n" + "="*70)
        print("🔍 DETAILED CACHE BEHAVIOR ANALYSIS")
        print("="*70)
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }
        
        # Test same question to same mentor multiple times
        question_data = {
            "category": "business",
            "mentor_ids": ["warren_buffett"],
            "question": "What is your most important investment principle for beginners?"
        }
        
        print("🔄 Testing cache behavior with 5 consecutive requests...")
        
        times = []
        responses = []
        
        for i in range(5):
            print(f"\n📊 Request {i+1}/5...")
            start_time = time.time()
            
            response = requests.post(
                f"{self.base_url}/api/questions/ask",
                json=question_data,
                headers=headers,
                timeout=60
            )
            
            end_time = time.time()
            request_time = end_time - start_time
            times.append(request_time)
            
            if response.status_code == 200:
                data = response.json()
                processing_time = data.get('processing_time', 'N/A')
                response_text = data['responses'][0]['response']
                responses.append(response_text)
                
                print(f"   ✅ Request time: {request_time:.3f}s")
                print(f"   Backend processing: {processing_time}")
                print(f"   Response length: {len(response_text)} chars")
                print(f"   Response preview: {response_text[:80]}...")
            else:
                print(f"   ❌ Failed: {response.status_code}")
                return False
            
            # Small delay between requests
            time.sleep(0.5)
        
        # Analyze results
        print(f"\n📈 CACHE ANALYSIS RESULTS:")
        print(f"   Request times: {[f'{t:.3f}s' for t in times]}")
        print(f"   Average time: {sum(times)/len(times):.3f}s")
        print(f"   Fastest request: {min(times):.3f}s")
        print(f"   Slowest request: {max(times):.3f}s")
        
        # Check if responses are identical (cache hits)
        unique_responses = len(set(responses))
        print(f"   Unique responses: {unique_responses}/5")
        
        if unique_responses == 1:
            print("   ✅ All responses identical - caching working!")
        else:
            print("   ⚠️  Responses differ - cache may not be working")
        
        # Check for speed improvement pattern
        if len(times) >= 2:
            first_time = times[0]
            subsequent_avg = sum(times[1:]) / len(times[1:])
            improvement = first_time / subsequent_avg if subsequent_avg > 0 else 0
            
            print(f"   First request: {first_time:.3f}s")
            print(f"   Subsequent avg: {subsequent_avg:.3f}s")
            print(f"   Speed improvement: {improvement:.1f}x")
            
            if improvement >= 1.5:
                print("   ✅ Cache providing speed improvement!")
                return True
            else:
                print("   ⚠️  Limited cache speed improvement")
        
        return False
    
    def test_parallel_vs_sequential_detailed(self):
        """Test parallel processing with detailed timing"""
        print("\n" + "="*70)
        print("🚀 DETAILED PARALLEL VS SEQUENTIAL ANALYSIS")
        print("="*70)
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }
        
        # Test with different numbers of mentors
        mentor_counts = [1, 2, 3, 5]
        business_mentors = ["warren_buffett", "steve_jobs", "bill_gates", "elon_musk", "jeff_bezos"]
        
        question = "What are the key factors for building a successful technology company in today's competitive market?"
        
        results = {}
        
        for count in mentor_counts:
            print(f"\n📊 Testing with {count} mentor(s)...")
            
            question_data = {
                "category": "business",
                "mentor_ids": business_mentors[:count],
                "question": question
            }
            
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/api/questions/ask",
                json=question_data,
                headers=headers,
                timeout=120
            )
            end_time = time.time()
            
            request_time = end_time - start_time
            
            if response.status_code == 200:
                data = response.json()
                processing_time = data.get('processing_time', 'N/A')
                responses = data.get('responses', [])
                
                print(f"   ✅ Request time: {request_time:.3f}s")
                print(f"   Backend processing: {processing_time}")
                print(f"   Responses received: {len(responses)}")
                
                # Check response quality
                avg_length = sum(len(r['response']) for r in responses) / len(responses) if responses else 0
                unique_responses = len(set(r['response'] for r in responses))
                
                print(f"   Average response length: {avg_length:.0f} chars")
                print(f"   Unique responses: {unique_responses}/{len(responses)}")
                
                results[count] = {
                    'request_time': request_time,
                    'processing_time': processing_time,
                    'response_count': len(responses),
                    'avg_length': avg_length,
                    'unique_responses': unique_responses
                }
            else:
                print(f"   ❌ Failed: {response.status_code}")
                results[count] = None
        
        # Analyze parallel processing efficiency
        print(f"\n📈 PARALLEL PROCESSING EFFICIENCY:")
        print(f"   {'Mentors':<8} {'Time':<8} {'Processing':<12} {'Responses':<10} {'Avg Length':<12} {'Unique':<8}")
        print(f"   {'-'*8} {'-'*8} {'-'*12} {'-'*10} {'-'*12} {'-'*8}")
        
        for count in mentor_counts:
            if results[count]:
                r = results[count]
                print(f"   {count:<8} {r['request_time']:.3f}s   {str(r['processing_time']):<12} {r['response_count']:<10} {r['avg_length']:<12.0f} {r['unique_responses']:<8}")
        
        # Calculate efficiency metrics
        if results[1] and results[5]:
            single_time = results[1]['request_time']
            five_time = results[5]['request_time']
            expected_sequential = single_time * 5
            efficiency = expected_sequential / five_time if five_time > 0 else 0
            
            print(f"\n🎯 EFFICIENCY METRICS:")
            print(f"   Single mentor time: {single_time:.3f}s")
            print(f"   Five mentors time: {five_time:.3f}s")
            print(f"   Expected sequential: {expected_sequential:.3f}s")
            print(f"   Parallel efficiency: {efficiency:.1f}x faster")
            
            if efficiency >= 3.0:
                print("   🏆 EXCELLENT parallel processing!")
                return True
            elif efficiency >= 2.0:
                print("   ✅ GOOD parallel processing")
                return True
            else:
                print("   ⚠️  Limited parallel processing benefit")
        
        return False
    
    def test_backend_logs_analysis(self):
        """Check if we can see cache indicators in responses"""
        print("\n" + "="*70)
        print("🔍 BACKEND BEHAVIOR ANALYSIS")
        print("="*70)
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }
        
        # Test question that should show cache behavior
        question_data = {
            "category": "business",
            "mentor_ids": ["warren_buffett"],
            "question": "What is your advice for young entrepreneurs starting their first business?"
        }
        
        print("📊 First request (should create cache)...")
        start1 = time.time()
        response1 = requests.post(
            f"{self.base_url}/api/questions/ask",
            json=question_data,
            headers=headers,
            timeout=60
        )
        end1 = time.time()
        
        if response1.status_code == 200:
            data1 = response1.json()
            print(f"   ✅ Time: {end1-start1:.3f}s")
            print(f"   Processing time: {data1.get('processing_time', 'N/A')}")
            print(f"   Response: {data1['responses'][0]['response'][:100]}...")
        
        print("\n⏳ Waiting 1 second...")
        time.sleep(1)
        
        print("📊 Second request (should use cache)...")
        start2 = time.time()
        response2 = requests.post(
            f"{self.base_url}/api/questions/ask",
            json=question_data,
            headers=headers,
            timeout=60
        )
        end2 = time.time()
        
        if response2.status_code == 200:
            data2 = response2.json()
            print(f"   ✅ Time: {end2-start2:.3f}s")
            print(f"   Processing time: {data2.get('processing_time', 'N/A')}")
            print(f"   Response: {data2['responses'][0]['response'][:100]}...")
            
            # Compare responses
            if data1['responses'][0]['response'] == data2['responses'][0]['response']:
                print("   ✅ Responses identical - cache hit confirmed!")
                
                time_improvement = (end1-start1) / (end2-start2) if (end2-start2) > 0 else 0
                print(f"   Speed improvement: {time_improvement:.1f}x")
                
                return True
            else:
                print("   ❌ Responses different - cache miss")
        
        return False

def main():
    print("🔍 OnlyMentors.ai Detailed Performance Analysis")
    print("=" * 70)
    
    tester = DetailedPerformanceTester()
    
    if not tester.setup_auth():
        print("❌ Authentication failed")
        return 1
    
    print("✅ Authentication successful")
    
    # Run detailed tests
    cache_working = tester.test_cache_behavior_detailed()
    parallel_working = tester.test_parallel_vs_sequential_detailed()
    backend_analysis = tester.test_backend_logs_analysis()
    
    # Final summary
    print("\n" + "="*70)
    print("📋 DETAILED ANALYSIS SUMMARY")
    print("="*70)
    
    print(f"Cache System: {'✅ Working' if cache_working else '⚠️  Needs attention'}")
    print(f"Parallel Processing: {'✅ Working' if parallel_working else '⚠️  Needs attention'}")
    print(f"Backend Analysis: {'✅ Working' if backend_analysis else '⚠️  Needs attention'}")
    
    working_count = sum([cache_working, parallel_working, backend_analysis])
    print(f"\nOverall Performance: {working_count}/3 systems working optimally")
    
    if working_count >= 2:
        print("🎉 Performance improvements are working well!")
        return 0
    else:
        print("⚠️  Performance improvements need attention")
        return 1

if __name__ == "__main__":
    sys.exit(main())