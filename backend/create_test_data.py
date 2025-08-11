#!/usr/bin/env python3
"""
Test Data Generation Script for OnlyMentors.ai
Creates 100 test user accounts and 25 test creator accounts
"""

import asyncio
import sys
import os
sys.path.append('/app/backend')

from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
import bcrypt
import uuid
import random

# Import from existing systems
from creator_system import generate_creator_id, CreatorStatus
from payout_system import create_default_payout_settings, create_earnings_entry, EarningsType

# Database connection
MONGO_URL = "mongodb://localhost:27017"
client = AsyncIOMotorClient(MONGO_URL)
db = client.onlymentors_db
admin_db = client.onlymentors_admin_db

# Test account configurations
USER_PASSWORD = "TestUser123!"
CREATOR_PASSWORD = "Creator123!"

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def generate_test_user_data(index: int) -> dict:
    """Generate test user data"""
    user_id = str(uuid.uuid4())
    base_date = datetime.utcnow() - timedelta(days=random.randint(1, 180))
    
    return {
        "user_id": user_id,
        "email": f"testuser{index}@test.com",
        "password_hash": hash_password(USER_PASSWORD),
        "full_name": f"Test User {index}",
        "questions_asked": random.randint(0, 50),
        "is_subscribed": random.choice([True, False]),
        "subscription_expires": base_date + timedelta(days=30) if random.choice([True, False]) else None,
        "created_at": base_date,
        "last_active": base_date + timedelta(days=random.randint(0, 30)),
        "profile": {
            "bio": f"This is test user {index} for OnlyMentors.ai testing",
            "interests": random.sample(["business", "health", "sports", "science", "relationships"], random.randint(1, 3)),
            "timezone": random.choice(["UTC", "EST", "PST", "GMT"])
        }
    }

def generate_test_creator_data(index: int) -> dict:
    """Generate test creator data"""
    creator_id = generate_creator_id()
    base_date = datetime.utcnow() - timedelta(days=random.randint(30, 120))
    
    categories = ["business", "health", "sports", "science", "relationships"]
    expertise_areas = {
        "business": ["leadership", "entrepreneurship", "marketing", "finance", "strategy"],
        "health": ["nutrition", "fitness", "mental_health", "wellness", "yoga"],
        "sports": ["football", "basketball", "tennis", "fitness", "coaching"],
        "science": ["physics", "biology", "chemistry", "research", "technology"],
        "relationships": ["dating", "marriage", "communication", "psychology", "counseling"]
    }
    
    category = random.choice(categories)
    expertise = random.sample(expertise_areas[category], random.randint(2, 4))
    
    return {
        "creator_id": creator_id,
        "email": f"creator{index}@test.com",
        "password_hash": hash_password(CREATOR_PASSWORD),
        "full_name": f"Creator {index}",
        "account_name": f"creator{index}_mentor",
        "category": category,
        "expertise": expertise,
        "service_description": f"Professional {category} mentor with expertise in {', '.join(expertise)}. Offering personalized guidance and advice.",
        "monthly_price": random.choice([19.99, 29.99, 39.99, 49.99, 69.99]),
        "status": random.choice([CreatorStatus.APPROVED, CreatorStatus.PENDING]),
        "profile": {
            "bio": f"Experienced {category} professional with {random.randint(5, 20)} years of experience. Passionate about helping others achieve their goals.",
            "location": random.choice(["New York", "Los Angeles", "Chicago", "Miami", "Seattle", "Austin"]),
            "languages": ["English"],
            "social_media": {
                "twitter": f"@creator{index}",
                "linkedin": f"linkedin.com/in/creator{index}",
                "instagram": f"@creator{index}_mentor"
            }
        },
        "stats": {
            "subscriber_count": random.randint(0, 500),
            "total_earnings": random.uniform(0, 5000),
            "monthly_earnings": random.uniform(0, 1000),
            "content_count": random.randint(0, 100),
            "rating": random.uniform(4.0, 5.0),
            "total_reviews": random.randint(0, 50)
        },
        "verification": {
            "email_verified": True,
            "phone_verified": random.choice([True, False]),
            "id_verified": random.choice([True, False]),
            "bank_verified": random.choice([True, False])
        },
        "settings": {
            "notifications_enabled": True,
            "public_profile": True,
            "accept_new_subscribers": True
        },
        "created_at": base_date,
        "updated_at": base_date + timedelta(days=random.randint(0, 30)),
        "last_active": datetime.utcnow() - timedelta(days=random.randint(0, 7))
    }

def generate_test_earnings_for_creator(creator_id: str, creator_data: dict) -> list:
    """Generate test earnings data for a creator"""
    if creator_data["status"] != CreatorStatus.APPROVED:
        return []
    
    earnings = []
    num_earnings = random.randint(0, 20)
    
    for i in range(num_earnings):
        amount = random.uniform(10, 200)
        earning = create_earnings_entry({
            "creator_id": creator_id,
            "amount": amount,
            "transaction_id": f"test_txn_{creator_id}_{i}",
            "type": random.choice(list(EarningsType)),
            "description": f"Test earnings entry {i+1} for creator"
        })
        earning["created_at"] = datetime.utcnow() - timedelta(days=random.randint(0, 90))
        earnings.append(earning)
    
    return earnings

def generate_sample_content_for_moderation(creator_ids: list) -> list:
    """Generate sample content for moderation testing"""
    content_items = []
    
    for i, creator_id in enumerate(creator_ids[:10]):  # Only first 10 creators
        # Video content
        video_content = {
            "moderation_id": f"mod_video_{i}",
            "content_id": f"video_{creator_id}_{i}",
            "content_type": "video",
            "creator_id": creator_id,
            "user_id": None,
            "title": f"Sample Video Content {i+1}",
            "description": f"This is sample video content for testing content moderation system",
            "file_url": f"https://example.com/videos/{creator_id}/video_{i}.mp4",
            "file_size": random.randint(50000000, 200000000),  # 50MB to 200MB
            "file_type": "mp4",
            "content_preview": f"https://example.com/thumbnails/{creator_id}/thumb_{i}.jpg",
            "status": "pending",
            "priority": random.choice(["low", "medium", "high"]),
            "flagged_reasons": [],
            "auto_flags": {
                "inappropriate_content": False,
                "violence_detected": False,
                "adult_content": False,
                "spam_detected": False,
                "confidence_scores": {"safe_content": random.uniform(0.7, 0.99)}
            },
            "manual_flags": {},
            "moderation_history": [],
            "assigned_moderator": None,
            "reviewed_by": None,
            "reviewed_at": None,
            "review_notes": None,
            "created_at": datetime.utcnow() - timedelta(days=random.randint(0, 30)),
            "updated_at": datetime.utcnow()
        }
        content_items.append(video_content)
    
    return content_items

async def create_test_users():
    """Create 100 test user accounts"""
    print("🔄 Creating 100 test user accounts...")
    
    users = []
    for i in range(1, 101):
        user_data = generate_test_user_data(i)
        users.append(user_data)
    
    # Insert users in batches
    batch_size = 20
    for i in range(0, len(users), batch_size):
        batch = users[i:i+batch_size]
        await db.users.insert_many(batch)
        print(f"✅ Created users {i+1} to {min(i+batch_size, len(users))}")
    
    print(f"✅ Successfully created {len(users)} test user accounts")
    return [user["user_id"] for user in users]

async def create_test_creators():
    """Create 25 test creator accounts"""
    print("🔄 Creating 25 test creator accounts...")
    
    creators = []
    for i in range(1, 26):
        creator_data = generate_test_creator_data(i)
        creators.append(creator_data)
    
    # Insert creators
    await db.creators.insert_many(creators)
    print(f"✅ Successfully created {len(creators)} test creator accounts")
    
    return [(creator["creator_id"], creator) for creator in creators]

async def create_test_earnings(creators_data):
    """Create test earnings data for creators"""
    print("🔄 Creating test earnings data...")
    
    all_earnings = []
    payout_settings = []
    
    for creator_id, creator_data in creators_data:
        # Create earnings
        earnings = generate_test_earnings_for_creator(creator_id, creator_data)
        if earnings:
            all_earnings.extend(earnings)
        
        # Create payout settings
        settings = create_default_payout_settings(creator_id)
        payout_settings.append(settings)
    
    # Insert earnings and settings
    if all_earnings:
        await admin_db.creator_earnings.insert_many(all_earnings)
        print(f"✅ Created {len(all_earnings)} earnings records")
    
    await admin_db.payout_settings.insert_many(payout_settings)
    print(f"✅ Created {len(payout_settings)} payout settings")

async def create_sample_content_moderation(creator_ids):
    """Create sample content for moderation"""
    print("🔄 Creating sample content for moderation...")
    
    content_items = generate_sample_content_for_moderation(creator_ids)
    
    if content_items:
        await admin_db.content_moderation.insert_many(content_items)
        print(f"✅ Created {len(content_items)} content items for moderation")

async def create_sample_questions(user_ids, creator_ids):
    """Create sample questions and interactions"""
    print("🔄 Creating sample questions and interactions...")
    
    questions = []
    num_questions = min(50, len(user_ids) * 2)  # Up to 50 sample questions
    
    for i in range(num_questions):
        user_id = random.choice(user_ids)
        selected_mentors = random.sample(creator_ids, random.randint(1, 3))
        
        question_doc = {
            "question_id": str(uuid.uuid4()),
            "user_id": user_id,
            "question": f"This is sample question {i+1} for testing purposes. What advice do you have?",
            "selected_mentors": selected_mentors,
            "responses": [
                {
                    "mentor_id": mentor_id,
                    "mentor_name": f"Creator {mentor_id[:8]}",
                    "response": f"This is a sample AI response from mentor {mentor_id[:8]} for question {i+1}.",
                    "timestamp": datetime.utcnow() - timedelta(minutes=random.randint(5, 1440))
                }
                for mentor_id in selected_mentors
            ],
            "created_at": datetime.utcnow() - timedelta(days=random.randint(0, 30)),
            "session_id": f"session_{user_id}_{i}"
        }
        questions.append(question_doc)
    
    if questions:
        await db.questions.insert_many(questions)
        print(f"✅ Created {len(questions)} sample questions")

async def create_sample_payments(user_ids):
    """Create sample payment transactions"""
    print("🔄 Creating sample payment transactions...")
    
    payments = []
    num_payments = min(30, len(user_ids) // 3)  # About 1/3 of users have payments
    
    for i in range(num_payments):
        user_id = random.choice(user_ids)
        payment_doc = {
            "transaction_id": f"test_payment_{i+1}",
            "user_id": user_id,
            "amount": random.choice([29.99, 299.99]),  # Monthly or yearly
            "package_id": random.choice(["monthly", "yearly"]),
            "payment_status": random.choice(["paid", "pending", "failed"]),
            "stripe_session_id": f"test_session_{i+1}",
            "created_at": datetime.utcnow() - timedelta(days=random.randint(0, 60))
        }
        payments.append(payment_doc)
    
    if payments:
        await db.payment_transactions.insert_many(payments)
        print(f"✅ Created {len(payments)} sample payment transactions")

async def print_test_account_summary():
    """Print summary of created test accounts"""
    print("\n" + "="*60)
    print("🎉 TEST ACCOUNT CREATION COMPLETE!")
    print("="*60)
    
    print("\n📊 ACCOUNT SUMMARY:")
    user_count = await db.users.count_documents({"email": {"$regex": "testuser.*@test.com"}})
    creator_count = await db.creators.count_documents({"email": {"$regex": "creator.*@test.com"}})
    earnings_count = await admin_db.creator_earnings.count_documents({})
    content_count = await admin_db.content_moderation.count_documents({})
    questions_count = await db.questions.count_documents({})
    payments_count = await db.payment_transactions.count_documents({"transaction_id": {"$regex": "test_payment.*"}})
    
    print(f"👥 Test Users Created: {user_count}")
    print(f"🎓 Test Creators Created: {creator_count}")
    print(f"💰 Earnings Records: {earnings_count}")
    print(f"🔍 Content Items for Moderation: {content_count}")
    print(f"❓ Sample Questions: {questions_count}")
    print(f"💳 Sample Payments: {payments_count}")
    
    print("\n🔐 LOGIN CREDENTIALS:")
    print("📧 Test Users: testuser1@test.com to testuser100@test.com")
    print(f"🔑 User Password: {USER_PASSWORD}")
    print("📧 Test Creators: creator1@test.com to creator25@test.com")
    print(f"🔑 Creator Password: {CREATOR_PASSWORD}")
    
    print("\n🧪 TESTING NOTES:")
    print("• All test accounts have realistic data variations")
    print("• Creators span all 5 categories (business, health, sports, science, relationships)")
    print("• Some creators have earnings data and subscribers")
    print("• Sample content is available for moderation testing")
    print("• Payment transactions include both monthly and yearly subscriptions")
    print("• Questions demonstrate the Q&A functionality")
    
    print("\n🚀 You can now test the complete OnlyMentors.ai platform with real data!")
    print("="*60 + "\n")

async def main():
    """Main test data generation function"""
    try:
        print("🚀 Starting test data generation for OnlyMentors.ai...")
        print("This will create 100 users and 25 creators with sample data.\n")
        
        # Create test users
        user_ids = await create_test_users()
        
        # Create test creators
        creators_data = await create_test_creators()
        creator_ids = [creator[0] for creator in creators_data]
        
        # Create earnings data for creators
        await create_test_earnings(creators_data)
        
        # Create sample content for moderation
        await create_sample_content_moderation(creator_ids)
        
        # Create sample questions
        await create_sample_questions(user_ids, creator_ids)
        
        # Create sample payment transactions
        await create_sample_payments(user_ids)
        
        # Print summary
        await print_test_account_summary()
        
    except Exception as e:
        print(f"❌ Error creating test data: {str(e)}")
        raise
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(main())