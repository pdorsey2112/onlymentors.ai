#!/usr/bin/env python3
"""
MongoDB Database Analysis for OnlyMentors.ai
============================================

This script provides comprehensive analysis of the MongoDB database contents
including collection overview, sample data review, health checks, and data structure analysis.
"""

import os
import sys
import json
import asyncio
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class MongoDBAnalyzer:
    def __init__(self):
        self.mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
        self.client = None
        self.db = None
        self.admin_db = None
        
    async def connect(self):
        """Connect to MongoDB"""
        try:
            print(f"🔌 Connecting to MongoDB at: {self.mongo_url}")
            self.client = AsyncIOMotorClient(self.mongo_url)
            
            # Test connection
            await self.client.admin.command('ping')
            print("✅ MongoDB connection successful!")
            
            # Connect to main database
            self.db = self.client.onlymentors_db
            self.admin_db = self.client.onlymentors_admin_db
            
            return True
        except Exception as e:
            print(f"❌ MongoDB connection failed: {str(e)}")
            return False
    
    async def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            print("🔌 MongoDB connection closed")
    
    async def get_database_info(self):
        """Get basic database information"""
        print(f"\n{'='*80}")
        print("📊 DATABASE OVERVIEW")
        print(f"{'='*80}")
        
        try:
            # Get database stats
            main_stats = await self.db.command("dbStats")
            admin_stats = await self.admin_db.command("dbStats")
            
            print(f"\n🗄️  Main Database (onlymentors_db):")
            print(f"   Database Size: {main_stats.get('dataSize', 0) / (1024*1024):.2f} MB")
            print(f"   Storage Size: {main_stats.get('storageSize', 0) / (1024*1024):.2f} MB")
            print(f"   Index Size: {main_stats.get('indexSize', 0) / (1024*1024):.2f} MB")
            print(f"   Collections: {main_stats.get('collections', 0)}")
            print(f"   Objects: {main_stats.get('objects', 0)}")
            
            print(f"\n🔐 Admin Database (onlymentors_admin_db):")
            print(f"   Database Size: {admin_stats.get('dataSize', 0) / (1024*1024):.2f} MB")
            print(f"   Storage Size: {admin_stats.get('storageSize', 0) / (1024*1024):.2f} MB")
            print(f"   Collections: {admin_stats.get('collections', 0)}")
            print(f"   Objects: {admin_stats.get('objects', 0)}")
            
            return True
        except Exception as e:
            print(f"❌ Failed to get database info: {str(e)}")
            return False
    
    async def analyze_collections(self):
        """Analyze all collections in both databases"""
        print(f"\n{'='*80}")
        print("📋 COLLECTION ANALYSIS")
        print(f"{'='*80}")
        
        try:
            # Main database collections
            print(f"\n🗄️  Main Database Collections:")
            main_collections = await self.db.list_collection_names()
            
            collection_info = []
            for collection_name in main_collections:
                try:
                    count = await self.db[collection_name].count_documents({})
                    collection_info.append({
                        'name': collection_name,
                        'count': count,
                        'database': 'main'
                    })
                    print(f"   📁 {collection_name}: {count:,} documents")
                except Exception as e:
                    print(f"   📁 {collection_name}: Error counting - {str(e)}")
            
            # Admin database collections
            print(f"\n🔐 Admin Database Collections:")
            admin_collections = await self.admin_db.list_collection_names()
            
            for collection_name in admin_collections:
                try:
                    count = await self.admin_db[collection_name].count_documents({})
                    collection_info.append({
                        'name': collection_name,
                        'count': count,
                        'database': 'admin'
                    })
                    print(f"   📁 {collection_name}: {count:,} documents")
                except Exception as e:
                    print(f"   📁 {collection_name}: Error counting - {str(e)}")
            
            # Summary
            total_documents = sum(info['count'] for info in collection_info)
            print(f"\n📊 Collection Summary:")
            print(f"   Total Collections: {len(collection_info)}")
            print(f"   Total Documents: {total_documents:,}")
            
            # Identify main collections
            main_collections_list = [info for info in collection_info if info['count'] > 0]
            main_collections_list.sort(key=lambda x: x['count'], reverse=True)
            
            print(f"\n🎯 Main Collections (by document count):")
            for info in main_collections_list[:10]:  # Top 10
                db_label = "📊" if info['database'] == 'main' else "🔐"
                print(f"   {db_label} {info['name']}: {info['count']:,} documents")
            
            return collection_info
            
        except Exception as e:
            print(f"❌ Failed to analyze collections: {str(e)}")
            return []
    
    async def sample_users_collection(self):
        """Show sample documents from users collection"""
        print(f"\n{'='*80}")
        print("👥 USERS COLLECTION SAMPLE DATA")
        print(f"{'='*80}")
        
        try:
            users_count = await self.db.users.count_documents({})
            print(f"\n📊 Total Users: {users_count:,}")
            
            if users_count == 0:
                print("   No users found in database")
                return
            
            # Get sample users (first 3, excluding sensitive data)
            users = await self.db.users.find({}, {
                'password_hash': 0,  # Exclude sensitive data
                'social_auth': 0     # Exclude OAuth tokens
            }).limit(3).to_list(length=None)
            
            print(f"\n📋 Sample User Documents (first 3, sensitive data excluded):")
            for i, user in enumerate(users, 1):
                print(f"\n   👤 User {i}:")
                print(f"      User ID: {user.get('user_id', 'N/A')}")
                print(f"      Email: {user.get('email', 'N/A')}")
                print(f"      Full Name: {user.get('full_name', 'N/A')}")
                print(f"      Questions Asked: {user.get('questions_asked', 0)}")
                print(f"      Is Subscribed: {user.get('is_subscribed', False)}")
                print(f"      Created At: {user.get('created_at', 'N/A')}")
                print(f"      Profile Completed: {user.get('profile_completed', False)}")
                
                # Show additional fields if present
                if user.get('phone_number'):
                    print(f"      Phone Number: {user.get('phone_number')}")
                if user.get('subscription_plan'):
                    print(f"      Subscription Plan: {user.get('subscription_plan')}")
                if user.get('communication_preferences'):
                    print(f"      Communication Prefs: {user.get('communication_preferences')}")
            
            # User statistics
            print(f"\n📈 User Statistics:")
            
            # Count by subscription status
            subscribed_count = await self.db.users.count_documents({'is_subscribed': True})
            print(f"   Subscribed Users: {subscribed_count:,}")
            print(f"   Free Users: {users_count - subscribed_count:,}")
            
            # Count by profile completion
            completed_profiles = await self.db.users.count_documents({'profile_completed': True})
            print(f"   Completed Profiles: {completed_profiles:,}")
            
            # Recent signups (last 7 days)
            from datetime import timedelta
            week_ago = datetime.utcnow() - timedelta(days=7)
            recent_signups = await self.db.users.count_documents({
                'created_at': {'$gte': week_ago}
            })
            print(f"   Recent Signups (7 days): {recent_signups:,}")
            
        except Exception as e:
            print(f"❌ Failed to analyze users collection: {str(e)}")
    
    async def sample_creators_collection(self):
        """Show sample documents from creators/mentors collection"""
        print(f"\n{'='*80}")
        print("🎓 CREATORS/MENTORS COLLECTION SAMPLE DATA")
        print(f"{'='*80}")
        
        try:
            creators_count = await self.db.creators.count_documents({})
            print(f"\n📊 Total Creators: {creators_count:,}")
            
            if creators_count == 0:
                print("   No creators found in database")
                return
            
            # Get sample creators (first 3, excluding sensitive data)
            creators = await self.db.creators.find({}, {
                'password_hash': 0,  # Exclude sensitive data
                'banking_info': 0,   # Exclude banking details
                'tax_info': 0        # Exclude tax information
            }).limit(3).to_list(length=None)
            
            print(f"\n📋 Sample Creator Documents (first 3, sensitive data excluded):")
            for i, creator in enumerate(creators, 1):
                print(f"\n   🎓 Creator {i}:")
                print(f"      Creator ID: {creator.get('creator_id', 'N/A')}")
                print(f"      Email: {creator.get('email', 'N/A')}")
                print(f"      Full Name: {creator.get('full_name', 'N/A')}")
                print(f"      Account Name: {creator.get('account_name', 'N/A')}")
                print(f"      Category: {creator.get('category', 'N/A')}")
                print(f"      Status: {creator.get('status', 'N/A')}")
                print(f"      Verification Status: {creator.get('verification_status', 'N/A')}")
                print(f"      Created At: {creator.get('created_at', 'N/A')}")
                
                # Show pricing if available
                if creator.get('pricing'):
                    pricing = creator.get('pricing', {})
                    print(f"      Pricing: ${pricing.get('per_question', 0)}/question")
                
                # Show earnings if available
                if creator.get('earnings'):
                    earnings = creator.get('earnings', {})
                    print(f"      Total Earnings: ${earnings.get('total', 0)}")
            
            # Creator statistics
            print(f"\n📈 Creator Statistics:")
            
            # Count by status
            approved_count = await self.db.creators.count_documents({'status': 'APPROVED'})
            pending_count = await self.db.creators.count_documents({'status': 'PENDING'})
            print(f"   Approved Creators: {approved_count:,}")
            print(f"   Pending Creators: {pending_count:,}")
            
            # Count by verification status
            verified_count = await self.db.creators.count_documents({'verification_status': 'VERIFIED'})
            print(f"   Verified Creators: {verified_count:,}")
            
            # Count by category
            categories = await self.db.creators.distinct('category')
            print(f"   Categories: {', '.join(categories) if categories else 'None'}")
            
        except Exception as e:
            print(f"❌ Failed to analyze creators collection: {str(e)}")
    
    async def sample_questions_collection(self):
        """Show sample documents from questions/interactions collection"""
        print(f"\n{'='*80}")
        print("❓ QUESTIONS/INTERACTIONS COLLECTION SAMPLE DATA")
        print(f"{'='*80}")
        
        try:
            # Check mentor_interactions collection
            interactions_count = await self.db.mentor_interactions.count_documents({})
            print(f"\n📊 Total Mentor Interactions: {interactions_count:,}")
            
            if interactions_count > 0:
                # Get sample interactions (first 2)
                interactions = await self.db.mentor_interactions.find({}).limit(2).to_list(length=None)
                
                print(f"\n📋 Sample Mentor Interaction Documents (first 2):")
                for i, interaction in enumerate(interactions, 1):
                    print(f"\n   ❓ Interaction {i}:")
                    print(f"      Interaction ID: {interaction.get('interaction_id', 'N/A')}")
                    print(f"      User ID: {interaction.get('user_id', 'N/A')}")
                    print(f"      Mentor ID: {interaction.get('mentor_id', 'N/A')}")
                    print(f"      Mentor Name: {interaction.get('mentor_name', 'N/A')}")
                    print(f"      Category: {interaction.get('mentor_category', 'N/A')}")
                    print(f"      Question: {interaction.get('question', 'N/A')[:100]}...")
                    print(f"      Response Length: {len(interaction.get('response', ''))}")
                    print(f"      Timestamp: {interaction.get('timestamp', 'N/A')}")
                    print(f"      Rating: {interaction.get('rating', 'Not rated')}")
            
            # Check questions collection (if exists)
            questions_count = await self.db.questions.count_documents({})
            if questions_count > 0:
                print(f"\n📊 Total Questions: {questions_count:,}")
                
                questions = await self.db.questions.find({}).limit(2).to_list(length=None)
                print(f"\n📋 Sample Question Documents (first 2):")
                for i, question in enumerate(questions, 1):
                    print(f"\n   ❓ Question {i}:")
                    print(f"      Question ID: {question.get('question_id', 'N/A')}")
                    print(f"      User ID: {question.get('user_id', 'N/A')}")
                    print(f"      Category: {question.get('category', 'N/A')}")
                    print(f"      Question Text: {question.get('question', 'N/A')[:100]}...")
                    print(f"      Timestamp: {question.get('timestamp', 'N/A')}")
            
            # Interaction statistics
            if interactions_count > 0:
                print(f"\n📈 Interaction Statistics:")
                
                # Most active mentors
                pipeline = [
                    {'$group': {'_id': '$mentor_name', 'count': {'$sum': 1}}},
                    {'$sort': {'count': -1}},
                    {'$limit': 5}
                ]
                top_mentors = await self.db.mentor_interactions.aggregate(pipeline).to_list(length=None)
                
                print(f"   Top Mentors by Questions:")
                for mentor in top_mentors:
                    print(f"      {mentor['_id']}: {mentor['count']} questions")
                
                # Most active users
                pipeline = [
                    {'$group': {'_id': '$user_id', 'count': {'$sum': 1}}},
                    {'$sort': {'count': -1}},
                    {'$limit': 3}
                ]
                top_users = await self.db.mentor_interactions.aggregate(pipeline).to_list(length=None)
                
                print(f"   Most Active Users:")
                for user in top_users:
                    print(f"      User {user['_id']}: {user['count']} questions")
            
        except Exception as e:
            print(f"❌ Failed to analyze questions collection: {str(e)}")
    
    async def analyze_other_collections(self):
        """Analyze other important collections"""
        print(f"\n{'='*80}")
        print("📚 OTHER COLLECTIONS ANALYSIS")
        print(f"{'='*80}")
        
        try:
            # Check for other important collections
            collections_to_check = [
                'payments', 'transactions', 'subscriptions', 'content',
                'messages', 'notifications', 'audit_logs', 'sessions',
                'password_resets', 'verification_codes'
            ]
            
            found_collections = []
            
            for collection_name in collections_to_check:
                try:
                    count = await self.db[collection_name].count_documents({})
                    if count > 0:
                        found_collections.append((collection_name, count))
                        print(f"\n📁 {collection_name.title()} Collection:")
                        print(f"   Document Count: {count:,}")
                        
                        # Get sample document
                        sample = await self.db[collection_name].find_one({})
                        if sample:
                            # Show structure (keys only, not values for privacy)
                            keys = list(sample.keys())
                            print(f"   Document Structure: {', '.join(keys[:10])}")
                            if len(keys) > 10:
                                print(f"   ... and {len(keys) - 10} more fields")
                except Exception as e:
                    # Collection doesn't exist or error accessing it
                    pass
            
            # Check admin collections
            admin_collections_to_check = ['admins', 'admin_audit_logs', 'admin_sessions']
            
            for collection_name in admin_collections_to_check:
                try:
                    count = await self.admin_db[collection_name].count_documents({})
                    if count > 0:
                        found_collections.append((f"admin.{collection_name}", count))
                        print(f"\n🔐 Admin {collection_name.title()} Collection:")
                        print(f"   Document Count: {count:,}")
                        
                        # Get sample document (excluding sensitive data)
                        exclude_fields = {'password_hash': 0, 'auth_token': 0}
                        sample = await self.admin_db[collection_name].find_one({}, exclude_fields)
                        if sample:
                            keys = list(sample.keys())
                            print(f"   Document Structure: {', '.join(keys[:10])}")
                            if len(keys) > 10:
                                print(f"   ... and {len(keys) - 10} more fields")
                except Exception as e:
                    pass
            
            if not found_collections:
                print("\n   No additional collections with data found")
            else:
                print(f"\n📊 Additional Collections Summary:")
                for name, count in found_collections:
                    print(f"   {name}: {count:,} documents")
            
        except Exception as e:
            print(f"❌ Failed to analyze other collections: {str(e)}")
    
    async def analyze_data_structure(self):
        """Analyze the schema/structure of key documents"""
        print(f"\n{'='*80}")
        print("🏗️  DATA STRUCTURE ANALYSIS")
        print(f"{'='*80}")
        
        try:
            # Analyze user document structure
            print(f"\n👤 User Document Structure:")
            user_sample = await self.db.users.find_one({})
            if user_sample:
                self.print_document_structure(user_sample, "User", exclude_fields=['password_hash'])
            else:
                print("   No user documents found")
            
            # Analyze creator document structure
            print(f"\n🎓 Creator Document Structure:")
            creator_sample = await self.db.creators.find_one({})
            if creator_sample:
                self.print_document_structure(creator_sample, "Creator", exclude_fields=['password_hash', 'banking_info'])
            else:
                print("   No creator documents found")
            
            # Analyze interaction document structure
            print(f"\n❓ Mentor Interaction Document Structure:")
            interaction_sample = await self.db.mentor_interactions.find_one({})
            if interaction_sample:
                self.print_document_structure(interaction_sample, "Interaction")
            else:
                print("   No interaction documents found")
            
            # Analyze admin document structure
            print(f"\n🔐 Admin Document Structure:")
            admin_sample = await self.admin_db.admins.find_one({})
            if admin_sample:
                self.print_document_structure(admin_sample, "Admin", exclude_fields=['password_hash'])
            else:
                print("   No admin documents found")
            
        except Exception as e:
            print(f"❌ Failed to analyze data structure: {str(e)}")
    
    def print_document_structure(self, document, doc_type, exclude_fields=None):
        """Print the structure of a document"""
        if exclude_fields is None:
            exclude_fields = []
        
        print(f"   📋 {doc_type} Fields:")
        for key, value in document.items():
            if key in exclude_fields:
                print(f"      {key}: [EXCLUDED - Sensitive Data]")
                continue
            
            value_type = type(value).__name__
            
            if isinstance(value, dict):
                print(f"      {key}: {value_type} ({len(value)} fields)")
                # Show nested structure for important objects
                if len(value) <= 5:
                    for nested_key in value.keys():
                        print(f"         └─ {nested_key}: {type(value[nested_key]).__name__}")
            elif isinstance(value, list):
                print(f"      {key}: {value_type} ({len(value)} items)")
                if value and len(value) > 0:
                    print(f"         └─ Item type: {type(value[0]).__name__}")
            else:
                # Show sample value for non-sensitive fields
                if key not in ['_id', 'user_id', 'creator_id', 'admin_id', 'email']:
                    sample_value = str(value)[:50]
                    if len(str(value)) > 50:
                        sample_value += "..."
                    print(f"      {key}: {value_type} ('{sample_value}')")
                else:
                    print(f"      {key}: {value_type}")
    
    async def health_check(self):
        """Perform database health check"""
        print(f"\n{'='*80}")
        print("🏥 DATABASE HEALTH CHECK")
        print(f"{'='*80}")
        
        try:
            # Connection test
            print(f"\n🔌 Connection Health:")
            await self.client.admin.command('ping')
            print("   ✅ MongoDB connection: Healthy")
            
            # Server status
            server_status = await self.client.admin.command('serverStatus')
            print(f"   ✅ MongoDB version: {server_status.get('version', 'Unknown')}")
            print(f"   ✅ Uptime: {server_status.get('uptime', 0)} seconds")
            
            # Database accessibility
            print(f"\n🗄️  Database Accessibility:")
            try:
                await self.db.command('ping')
                print("   ✅ Main database (onlymentors_db): Accessible")
            except Exception as e:
                print(f"   ❌ Main database: Error - {str(e)}")
            
            try:
                await self.admin_db.command('ping')
                print("   ✅ Admin database (onlymentors_admin_db): Accessible")
            except Exception as e:
                print(f"   ❌ Admin database: Error - {str(e)}")
            
            # Expected collections check
            print(f"\n📋 Expected Collections Check:")
            expected_collections = {
                'users': 'User accounts and profiles',
                'creators': 'Creator/mentor accounts',
                'mentor_interactions': 'User-mentor question interactions'
            }
            
            for collection, description in expected_collections.items():
                try:
                    count = await self.db[collection].count_documents({})
                    if count > 0:
                        print(f"   ✅ {collection}: {count:,} documents ({description})")
                    else:
                        print(f"   ⚠️  {collection}: Empty ({description})")
                except Exception as e:
                    print(f"   ❌ {collection}: Error - {str(e)}")
            
            # Index health (basic check)
            print(f"\n📊 Index Health:")
            try:
                # Check if collections have indexes
                for collection in ['users', 'creators', 'mentor_interactions']:
                    indexes = await self.db[collection].list_indexes().to_list(length=None)
                    print(f"   📁 {collection}: {len(indexes)} indexes")
            except Exception as e:
                print(f"   ⚠️  Index check failed: {str(e)}")
            
            # Data consistency checks
            print(f"\n🔍 Data Consistency Checks:")
            
            # Check for orphaned interactions (interactions without valid users)
            try:
                total_interactions = await self.db.mentor_interactions.count_documents({})
                if total_interactions > 0:
                    # Sample check - get unique user IDs from interactions
                    user_ids_in_interactions = await self.db.mentor_interactions.distinct('user_id')
                    existing_users = await self.db.users.count_documents({
                        'user_id': {'$in': user_ids_in_interactions[:100]}  # Check first 100
                    })
                    
                    if len(user_ids_in_interactions) > 0:
                        consistency_rate = (existing_users / min(len(user_ids_in_interactions), 100)) * 100
                        print(f"   📊 User-Interaction consistency: {consistency_rate:.1f}%")
                    else:
                        print(f"   📊 User-Interaction consistency: No data to check")
                else:
                    print(f"   📊 User-Interaction consistency: No interactions to check")
            except Exception as e:
                print(f"   ⚠️  Consistency check failed: {str(e)}")
            
            print(f"\n✅ Database health check completed")
            
        except Exception as e:
            print(f"❌ Health check failed: {str(e)}")
    
    async def generate_summary_report(self):
        """Generate a comprehensive summary report"""
        print(f"\n{'='*80}")
        print("📋 COMPREHENSIVE DATABASE SUMMARY REPORT")
        print(f"{'='*80}")
        
        try:
            # Collect key metrics
            users_count = await self.db.users.count_documents({})
            creators_count = await self.db.creators.count_documents({})
            interactions_count = await self.db.mentor_interactions.count_documents({})
            
            # Get database sizes
            main_stats = await self.db.command("dbStats")
            admin_stats = await self.admin_db.command("dbStats")
            
            print(f"\n📊 KEY METRICS:")
            print(f"   👥 Total Users: {users_count:,}")
            print(f"   🎓 Total Creators: {creators_count:,}")
            print(f"   ❓ Total Interactions: {interactions_count:,}")
            print(f"   💾 Main DB Size: {main_stats.get('dataSize', 0) / (1024*1024):.2f} MB")
            print(f"   🔐 Admin DB Size: {admin_stats.get('dataSize', 0) / (1024*1024):.2f} MB")
            
            # User engagement metrics
            if users_count > 0 and interactions_count > 0:
                avg_questions_per_user = interactions_count / users_count
                print(f"   📈 Avg Questions per User: {avg_questions_per_user:.2f}")
            
            # Active users (users with interactions)
            active_users = len(await self.db.mentor_interactions.distinct('user_id'))
            if users_count > 0:
                engagement_rate = (active_users / users_count) * 100
                print(f"   🎯 User Engagement Rate: {engagement_rate:.1f}% ({active_users:,} active users)")
            
            # Subscription metrics
            subscribed_users = await self.db.users.count_documents({'is_subscribed': True})
            if users_count > 0:
                subscription_rate = (subscribed_users / users_count) * 100
                print(f"   💳 Subscription Rate: {subscription_rate:.1f}% ({subscribed_users:,} subscribed)")
            
            # Creator metrics
            if creators_count > 0:
                approved_creators = await self.db.creators.count_documents({'status': 'APPROVED'})
                approval_rate = (approved_creators / creators_count) * 100
                print(f"   ✅ Creator Approval Rate: {approval_rate:.1f}% ({approved_creators:,} approved)")
            
            # Data quality assessment
            print(f"\n🔍 DATA QUALITY ASSESSMENT:")
            
            # Profile completion rate
            completed_profiles = await self.db.users.count_documents({'profile_completed': True})
            if users_count > 0:
                completion_rate = (completed_profiles / users_count) * 100
                print(f"   📝 Profile Completion Rate: {completion_rate:.1f}%")
            
            # Recent activity (last 30 days)
            from datetime import timedelta
            month_ago = datetime.utcnow() - timedelta(days=30)
            recent_interactions = await self.db.mentor_interactions.count_documents({
                'timestamp': {'$gte': month_ago}
            })
            print(f"   📅 Recent Activity (30 days): {recent_interactions:,} interactions")
            
            # Platform health summary
            print(f"\n🏥 PLATFORM HEALTH SUMMARY:")
            
            health_score = 0
            total_checks = 5
            
            # Check 1: Database connectivity
            try:
                await self.client.admin.command('ping')
                print(f"   ✅ Database Connectivity: Healthy")
                health_score += 1
            except:
                print(f"   ❌ Database Connectivity: Issues detected")
            
            # Check 2: Core collections exist and have data
            core_collections_healthy = all([
                users_count > 0,
                creators_count > 0 or interactions_count > 0  # Either creators or interactions should exist
            ])
            if core_collections_healthy:
                print(f"   ✅ Core Collections: Healthy")
                health_score += 1
            else:
                print(f"   ❌ Core Collections: Missing or empty")
            
            # Check 3: User engagement
            if users_count > 0 and (active_users / users_count) > 0.1:  # At least 10% engagement
                print(f"   ✅ User Engagement: Healthy")
                health_score += 1
            else:
                print(f"   ⚠️  User Engagement: Low or no engagement")
            
            # Check 4: Data consistency
            if interactions_count == 0 or active_users > 0:  # If no interactions, that's ok; if interactions exist, should have active users
                print(f"   ✅ Data Consistency: Good")
                health_score += 1
            else:
                print(f"   ❌ Data Consistency: Issues detected")
            
            # Check 5: Recent activity
            if recent_interactions > 0 or users_count < 10:  # Recent activity or small user base (testing)
                print(f"   ✅ Platform Activity: Active")
                health_score += 1
            else:
                print(f"   ⚠️  Platform Activity: Low recent activity")
            
            # Overall health score
            health_percentage = (health_score / total_checks) * 100
            print(f"\n🎯 OVERALL PLATFORM HEALTH: {health_percentage:.0f}% ({health_score}/{total_checks} checks passed)")
            
            if health_percentage >= 80:
                print(f"   🎉 Platform Status: EXCELLENT - Ready for production")
            elif health_percentage >= 60:
                print(f"   ✅ Platform Status: GOOD - Minor issues to address")
            elif health_percentage >= 40:
                print(f"   ⚠️  Platform Status: FAIR - Several issues need attention")
            else:
                print(f"   ❌ Platform Status: POOR - Critical issues require immediate attention")
            
        except Exception as e:
            print(f"❌ Failed to generate summary report: {str(e)}")

async def main():
    """Main function to run the MongoDB analysis"""
    print("🔍 OnlyMentors.ai MongoDB Database Analysis")
    print("=" * 80)
    print(f"Analysis started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    analyzer = MongoDBAnalyzer()
    
    try:
        # Connect to MongoDB
        if not await analyzer.connect():
            print("❌ Failed to connect to MongoDB. Exiting.")
            return 1
        
        # Run all analysis components
        await analyzer.get_database_info()
        collection_info = await analyzer.analyze_collections()
        await analyzer.sample_users_collection()
        await analyzer.sample_creators_collection()
        await analyzer.sample_questions_collection()
        await analyzer.analyze_other_collections()
        await analyzer.analyze_data_structure()
        await analyzer.health_check()
        await analyzer.generate_summary_report()
        
        print(f"\n{'='*80}")
        print("✅ DATABASE ANALYSIS COMPLETED SUCCESSFULLY")
        print(f"{'='*80}")
        print(f"Analysis completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Analysis failed with error: {str(e)}")
        return 1
    
    finally:
        await analyzer.close()

if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))