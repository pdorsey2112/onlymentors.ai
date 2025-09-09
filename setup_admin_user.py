#!/usr/bin/env python3
"""
Setup Admin User for Testing
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
import sys
from dotenv import load_dotenv

load_dotenv()

async def setup_admin_user(email=None):
    """Add admin role to test user"""
    MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.onlymentors_db
    
    if not email:
        email = "testadmin@onlymentors.ai"
    
    # Update the test admin user to have admin role
    result = await db.users.update_one(
        {"email": email},
        {"$set": {"role": "admin"}}
    )
    
    if result.modified_count > 0:
        print(f"✅ Admin role added to {email}")
    else:
        print(f"❌ User not found or already has admin role: {email}")
    
    # Check if user exists and show their data
    user = await db.users.find_one({"email": email})
    if user:
        print(f"User found: {user.get('email')} - Role: {user.get('role', 'No role set')}")
    else:
        print("User not found")
    
    client.close()

if __name__ == "__main__":
    email = sys.argv[1] if len(sys.argv) > 1 else None
    asyncio.run(setup_admin_user(email))