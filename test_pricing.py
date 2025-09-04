import asyncio
import aiohttp
import json
import uuid

async def test_pricing_validation():
    async with aiohttp.ClientSession() as session:
        # Create a creator first
        creator_data = {
            'email': f'testcreator_{uuid.uuid4().hex[:8]}@example.com',
            'password': 'TestPassword123!',
            'full_name': 'Test Creator',
            'account_name': 'TestCreator',
            'description': 'Test creator for premium content testing',
            'monthly_price': 150.0,
            'category': 'business',
            'expertise_areas': ['business strategy', 'entrepreneurship']
        }
        
        async with session.post('https://multi-tenant-ai.preview.emergentagent.com/api/creators/signup', json=creator_data) as response:
            if response.status == 200:
                data = await response.json()
                token = data.get('token')
                headers = {'Authorization': f'Bearer {token}'}
                
                # Test 1: Price too low
                print('Testing price too low (0.005)...')
                content_data = {
                    'title': 'Test Content',
                    'description': 'Test description',
                    'content_type': 'document',
                    'category': 'business',
                    'price': 0.005,
                    'tags': [],
                    'preview_available': False
                }
                
                async with session.post('https://multi-tenant-ai.preview.emergentagent.com/api/creator/content/upload', 
                                      json=content_data, headers=headers) as upload_response:
                    print(f'Status: {upload_response.status}')
                    text = await upload_response.text()
                    print(f'Response: {text}')
                
                # Test 2: Price too high
                print('\nTesting price too high (75.00)...')
                content_data['price'] = 75.00
                
                async with session.post('https://multi-tenant-ai.preview.emergentagent.com/api/creator/content/upload', 
                                      json=content_data, headers=headers) as upload_response:
                    print(f'Status: {upload_response.status}')
                    text = await upload_response.text()
                    print(f'Response: {text}')
                
                # Test 3: Minimum platform fee (5.00 should use 2.99 minimum)
                print('\nTesting minimum platform fee (5.00)...')
                content_data['price'] = 5.00
                
                async with session.post('https://multi-tenant-ai.preview.emergentagent.com/api/creator/content/upload', 
                                      json=content_data, headers=headers) as upload_response:
                    print(f'Status: {upload_response.status}')
                    if upload_response.status == 200:
                        data = await upload_response.json()
                        pricing = data.get('pricing_breakdown', {})
                        print(f'Pricing: {json.dumps(pricing, indent=2)}')
                        platform_fee = pricing.get('platform_fee', 0)
                        print(f'Platform fee: ${platform_fee:.2f} (should be $2.99 minimum)')

if __name__ == "__main__":
    asyncio.run(test_pricing_validation())