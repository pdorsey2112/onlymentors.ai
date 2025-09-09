#!/usr/bin/env python3
"""
Setup Admin User for Testing
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

async def setup_admin_user():
    """Add admin role to test user"""
    MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.onlymentors_db
    
    # Update the test admin user to have admin role
    result = await db.users.update_one(
        {"email": "testadmin@onlymentors.ai"},
        {"$set": {"role": "admin"}}
    )
    
    if result.modified_count > 0:
        print("✅ Admin role added to testadmin@onlymentors.ai")
    else:
        print("❌ User not found or already has admin role")
    
    # Check if user exists and show their data
    user = await db.users.find_one({"email": "testadmin@onlymentors.ai"})
    if user:
        print(f"User found: {user.get('email')} - Role: {user.get('role', 'No role set')}")
    else:
        print("User not found")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(setup_admin_user())