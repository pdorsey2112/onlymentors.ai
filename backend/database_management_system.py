"""
OnlyMentors.ai Database Management System
Comprehensive MongoDB management, analytics, and backup functionality
"""

import os
import json
import csv
import io
import zipfile
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
import pymongo
from bson import ObjectId
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
        self.db_name = os.getenv("DB_NAME", "onlymentors_db")
        self.client = None
        self.db = None
        
    async def connect(self):
        """Initialize database connection"""
        try:
            self.client = AsyncIOMotorClient(self.mongo_url)
            await self.client.admin.command('ping')
            self.db = self.client[self.db_name]
            logger.info("✅ Database Manager connected successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Database connection failed: {str(e)}")
            return False

    def serialize_document(self, doc):
        """Convert MongoDB document to JSON serializable format"""
        if isinstance(doc, dict):
            return {key: self.serialize_document(value) for key, value in doc.items()}
        elif isinstance(doc, list):
            return [self.serialize_document(item) for item in doc]
        elif isinstance(doc, ObjectId):
            return str(doc)
        elif isinstance(doc, datetime):
            return doc.isoformat()
        else:
            return doc

    # ================================
    # 1. VISUAL DASHBOARD FUNCTIONALITY
    # ================================

    async def get_database_overview(self) -> Dict[str, Any]:
        """Get comprehensive database overview for dashboard"""
        try:
            overview = {
                "database_name": self.db_name,
                "timestamp": datetime.utcnow().isoformat(),
                "collections": [],
                "total_documents": 0,
                "database_size_mb": 0,
                "status": "healthy"
            }

            # Get database stats
            try:
                db_stats = await self.db.command("dbStats")
                overview["database_size_mb"] = round(db_stats.get("dataSize", 0) / (1024 * 1024), 2)
                overview["storage_size_mb"] = round(db_stats.get("storageSize", 0) / (1024 * 1024), 2)
                overview["index_size_mb"] = round(db_stats.get("indexSize", 0) / (1024 * 1024), 2)
            except:
                pass

            # Get collection information
            collection_names = await self.db.list_collection_names()
            
            for collection_name in collection_names:
                try:
                    count = await self.db[collection_name].count_documents({})
                    overview["collections"].append({
                        "name": collection_name,
                        "document_count": count,
                        "status": "active" if count > 0 else "empty"
                    })
                    overview["total_documents"] += count
                except Exception as e:
                    overview["collections"].append({
                        "name": collection_name,
                        "document_count": 0,
                        "status": "error",
                        "error": str(e)
                    })

            return overview

        except Exception as e:
            logger.error(f"Failed to get database overview: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Database overview failed: {str(e)}")

    async def browse_collection(self, collection_name: str, page: int = 1, limit: int = 20, search: str = None) -> Dict[str, Any]:
        """Browse collection with pagination and search"""
        try:
            collection = self.db[collection_name]
            
            # Build search query
            query = {}
            if search and search.strip():
                # Search in text fields - basic text search
                query = {"$or": [
                    {"email": {"$regex": search, "$options": "i"}},
                    {"full_name": {"$regex": search, "$options": "i"}},
                    {"account_name": {"$regex": search, "$options": "i"}},
                    {"name": {"$regex": search, "$options": "i"}},
                    {"category": {"$regex": search, "$options": "i"}},
                    {"question": {"$regex": search, "$options": "i"}}
                ]}

            # Get total count
            total_count = await collection.count_documents(query)
            
            # Calculate pagination
            skip = (page - 1) * limit
            total_pages = (total_count + limit - 1) // limit

            # Get documents
            cursor = collection.find(query).skip(skip).limit(limit)
            documents = await cursor.to_list(length=None)

            # Serialize documents
            serialized_docs = [self.serialize_document(doc) for doc in documents]

            # Get sample document structure
            sample_doc = await collection.find_one({})
            schema = {}
            if sample_doc:
                schema = {key: type(value).__name__ for key, value in sample_doc.items()}

            return {
                "collection_name": collection_name,
                "total_documents": total_count,
                "page": page,
                "limit": limit,
                "total_pages": total_pages,
                "documents": serialized_docs,
                "schema": schema,
                "search_query": search or ""
            }

        except Exception as e:
            logger.error(f"Failed to browse collection {collection_name}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Collection browsing failed: {str(e)}")

    # ================================
    # 2. DATA EXPORT FUNCTIONALITY
    # ================================

    async def export_collection_json(self, collection_name: str, search: str = None) -> str:
        """Export collection to JSON format"""
        try:
            collection = self.db[collection_name]
            
            # Build search query
            query = {}
            if search and search.strip():
                query = {"$or": [
                    {"email": {"$regex": search, "$options": "i"}},
                    {"full_name": {"$regex": search, "$options": "i"}},
                    {"account_name": {"$regex": search, "$options": "i"}},
                    {"name": {"$regex": search, "$options": "i"}}
                ]}

            # Get all documents
            cursor = collection.find(query)
            documents = await cursor.to_list(length=None)

            # Serialize documents
            serialized_docs = [self.serialize_document(doc) for doc in documents]

            # Create export metadata
            export_data = {
                "export_info": {
                    "collection": collection_name,
                    "exported_at": datetime.utcnow().isoformat(),
                    "document_count": len(serialized_docs),
                    "search_filter": search or "none"
                },
                "documents": serialized_docs
            }

            return json.dumps(export_data, indent=2, ensure_ascii=False)

        except Exception as e:
            logger.error(f"Failed to export collection {collection_name} to JSON: {str(e)}")
            raise HTTPException(status_code=500, detail=f"JSON export failed: {str(e)}")

    async def export_collection_csv(self, collection_name: str, search: str = None) -> str:
        """Export collection to CSV format"""
        try:
            collection = self.db[collection_name]
            
            # Build search query
            query = {}
            if search and search.strip():
                query = {"$or": [
                    {"email": {"$regex": search, "$options": "i"}},
                    {"full_name": {"$regex": search, "$options": "i"}},
                    {"account_name": {"$regex": search, "$options": "i"}},
                    {"name": {"$regex": search, "$options": "i"}}
                ]}

            # Get all documents
            cursor = collection.find(query)
            documents = await cursor.to_list(length=None)

            if not documents:
                return "No data found to export"

            # Serialize documents
            serialized_docs = [self.serialize_document(doc) for doc in documents]

            # Get all unique keys for CSV headers
            all_keys = set()
            for doc in serialized_docs:
                if isinstance(doc, dict):
                    all_keys.update(doc.keys())

            # Create CSV
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=sorted(all_keys))
            writer.writeheader()

            for doc in serialized_docs:
                if isinstance(doc, dict):
                    # Flatten complex objects for CSV
                    flattened = {}
                    for key, value in doc.items():
                        if isinstance(value, (dict, list)):
                            flattened[key] = json.dumps(value)
                        else:
                            flattened[key] = value
                    writer.writerow(flattened)

            return output.getvalue()

        except Exception as e:
            logger.error(f"Failed to export collection {collection_name} to CSV: {str(e)}")
            raise HTTPException(status_code=500, detail=f"CSV export failed: {str(e)}")

    async def create_full_backup(self) -> bytes:
        """Create complete database backup as ZIP file"""
        try:
            # Create ZIP file in memory
            zip_buffer = io.BytesIO()
            
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                # Add backup metadata
                backup_info = {
                    "backup_created": datetime.utcnow().isoformat(),
                    "database_name": self.db_name,
                    "backup_type": "full_database",
                    "collections": []
                }

                # Get all collections
                collection_names = await self.db.list_collection_names()
                
                for collection_name in collection_names:
                    try:
                        # Export each collection as JSON
                        json_data = await self.export_collection_json(collection_name)
                        zip_file.writestr(f"{collection_name}.json", json_data)
                        
                        # Add to backup info
                        count = await self.db[collection_name].count_documents({})
                        backup_info["collections"].append({
                            "name": collection_name,
                            "document_count": count
                        })
                        
                    except Exception as e:
                        logger.warning(f"Failed to backup collection {collection_name}: {str(e)}")

                # Add backup metadata file
                zip_file.writestr("backup_info.json", json.dumps(backup_info, indent=2))

            zip_buffer.seek(0)
            return zip_buffer.getvalue()

        except Exception as e:
            logger.error(f"Failed to create full backup: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Backup creation failed: {str(e)}")

    # ================================
    # 3. DATABASE RESTORE FUNCTIONALITY
    # ================================

    async def restore_collection_from_json(self, collection_name: str, json_data: str) -> Dict[str, Any]:
        """Restore collection from JSON data"""
        try:
            # Parse JSON data
            data = json.loads(json_data)
            
            # Extract documents
            documents = data.get("documents", [])
            if not documents and isinstance(data, list):
                documents = data

            if not documents:
                return {"success": False, "message": "No documents found in JSON data"}

            # Get collection
            collection = self.db[collection_name]

            # Insert documents
            if len(documents) == 1:
                await collection.insert_one(documents[0])
            else:
                await collection.insert_many(documents)

            return {
                "success": True,
                "collection": collection_name,
                "documents_restored": len(documents),
                "restored_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to restore collection {collection_name}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Collection restore failed: {str(e)}")

    # ================================
    # 4. ADVANCED ANALYTICS FUNCTIONALITY
    # ================================

    async def get_user_analytics(self) -> Dict[str, Any]:
        """Get comprehensive user analytics"""
        try:
            analytics = {
                "timestamp": datetime.utcnow().isoformat(),
                "user_metrics": {},
                "engagement_metrics": {},
                "subscription_metrics": {},
                "growth_metrics": {}
            }

            users_collection = self.db.users

            # Basic user metrics
            total_users = await users_collection.count_documents({})
            active_users = await users_collection.count_documents({"is_active": {"$ne": False}})
            subscribed_users = await users_collection.count_documents({"is_subscribed": True})
            completed_profiles = await users_collection.count_documents({"profile_completed": True})

            analytics["user_metrics"] = {
                "total_users": total_users,
                "active_users": active_users,
                "subscribed_users": subscribed_users,
                "free_users": total_users - subscribed_users,
                "completed_profiles": completed_profiles,
                "completion_rate": round((completed_profiles / total_users * 100), 2) if total_users > 0 else 0,
                "subscription_rate": round((subscribed_users / total_users * 100), 2) if total_users > 0 else 0
            }

            # Engagement metrics
            questions_collection = self.db.questions
            total_questions = await questions_collection.count_documents({})
            
            # Users with questions
            users_with_questions = await users_collection.count_documents({"questions_asked": {"$gt": 0}})
            
            analytics["engagement_metrics"] = {
                "total_questions": total_questions,
                "users_with_questions": users_with_questions,
                "engagement_rate": round((users_with_questions / total_users * 100), 2) if total_users > 0 else 0,
                "avg_questions_per_user": round(total_questions / total_users, 2) if total_users > 0 else 0
            }

            # Growth metrics (last 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            seven_days_ago = datetime.utcnow() - timedelta(days=7)

            new_users_30d = await users_collection.count_documents({
                "created_at": {"$gte": thirty_days_ago}
            })
            new_users_7d = await users_collection.count_documents({
                "created_at": {"$gte": seven_days_ago}
            })

            new_questions_30d = await questions_collection.count_documents({
                "created_at": {"$gte": thirty_days_ago}
            })
            new_questions_7d = await questions_collection.count_documents({
                "created_at": {"$gte": seven_days_ago}
            })

            analytics["growth_metrics"] = {
                "new_users_30d": new_users_30d,
                "new_users_7d": new_users_7d,
                "new_questions_30d": new_questions_30d,
                "new_questions_7d": new_questions_7d
            }

            # Subscription analytics
            payment_transactions = self.db.payment_transactions
            total_revenue = 0
            
            try:
                # Calculate revenue from transactions
                async for transaction in payment_transactions.find({"status": "completed"}):
                    amount = transaction.get("amount", 0)
                    if isinstance(amount, (int, float)):
                        total_revenue += amount
            except:
                pass

            analytics["subscription_metrics"] = {
                "total_revenue": total_revenue,
                "monthly_revenue_estimate": subscribed_users * 9.99,
                "average_revenue_per_user": round(total_revenue / total_users, 2) if total_users > 0 else 0
            }

            return analytics

        except Exception as e:
            logger.error(f"Failed to get user analytics: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Analytics generation failed: {str(e)}")

    async def get_mentor_analytics(self) -> Dict[str, Any]:
        """Get comprehensive mentor analytics"""
        try:
            analytics = {
                "timestamp": datetime.utcnow().isoformat(),
                "mentor_metrics": {},
                "performance_metrics": {},
                "category_metrics": {}
            }

            creators_collection = self.db.creators

            # Basic mentor metrics
            total_mentors = await creators_collection.count_documents({})
            approved_mentors = await creators_collection.count_documents({"status": "approved"})
            pending_mentors = await creators_collection.count_documents({"status": "pending"})
            suspended_mentors = await creators_collection.count_documents({"status": "suspended"})

            analytics["mentor_metrics"] = {
                "total_mentors": total_mentors,
                "approved_mentors": approved_mentors,
                "pending_mentors": pending_mentors,
                "suspended_mentors": suspended_mentors,
                "approval_rate": round((approved_mentors / total_mentors * 100), 2) if total_mentors > 0 else 0
            }

            # Category distribution
            categories = await creators_collection.distinct("category")
            category_counts = {}
            
            for category in categories:
                if category:
                    count = await creators_collection.count_documents({"category": category})
                    category_counts[category] = count

            analytics["category_metrics"] = {
                "total_categories": len(categories),
                "category_distribution": category_counts
            }

            # Earnings analytics
            earnings_collection = self.db.creator_earnings
            total_earnings = 0
            
            try:
                async for earning in earnings_collection.find({}):
                    amount = earning.get("total_earned", 0)
                    if isinstance(amount, (int, float)):
                        total_earnings += amount
            except:
                pass

            analytics["performance_metrics"] = {
                "total_platform_earnings": total_earnings,
                "average_earnings_per_mentor": round(total_earnings / approved_mentors, 2) if approved_mentors > 0 else 0
            }

            return analytics

        except Exception as e:
            logger.error(f"Failed to get mentor analytics: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Mentor analytics generation failed: {str(e)}")

    async def get_platform_health(self) -> Dict[str, Any]:
        """Get overall platform health metrics"""
        try:
            health = {
                "timestamp": datetime.utcnow().isoformat(),
                "overall_health": "excellent",
                "health_score": 0,
                "components": {},
                "recommendations": []
            }

            # Check database connectivity
            try:
                await self.db.command("ping")
                health["components"]["database"] = {"status": "healthy", "score": 25}
            except:
                health["components"]["database"] = {"status": "unhealthy", "score": 0}

            # Check user engagement
            users_collection = self.db.users
            total_users = await users_collection.count_documents({})
            engaged_users = await users_collection.count_documents({"questions_asked": {"$gt": 0}})
            
            engagement_rate = (engaged_users / total_users * 100) if total_users > 0 else 0
            
            if engagement_rate > 10:
                health["components"]["user_engagement"] = {"status": "excellent", "score": 25}
            elif engagement_rate > 5:
                health["components"]["user_engagement"] = {"status": "good", "score": 20}
            else:
                health["components"]["user_engagement"] = {"status": "needs_attention", "score": 10}
                health["recommendations"].append("Consider implementing user activation campaigns")

            # Check subscription health
            subscribed_users = await users_collection.count_documents({"is_subscribed": True})
            subscription_rate = (subscribed_users / total_users * 100) if total_users > 0 else 0
            
            if subscription_rate > 20:
                health["components"]["subscriptions"] = {"status": "excellent", "score": 25}
            elif subscription_rate > 10:
                health["components"]["subscriptions"] = {"status": "good", "score": 20}
            else:
                health["components"]["subscriptions"] = {"status": "needs_attention", "score": 15}

            # Check data quality
            completed_profiles = await users_collection.count_documents({"profile_completed": True})
            completion_rate = (completed_profiles / total_users * 100) if total_users > 0 else 0
            
            if completion_rate > 50:
                health["components"]["data_quality"] = {"status": "excellent", "score": 25}
            elif completion_rate > 25:
                health["components"]["data_quality"] = {"status": "good", "score": 20}
            else:
                health["components"]["data_quality"] = {"status": "needs_attention", "score": 10}
                health["recommendations"].append("Implement profile completion incentives")

            # Calculate overall health score
            total_score = sum(component["score"] for component in health["components"].values())
            health["health_score"] = total_score

            # Determine overall health status
            if total_score >= 90:
                health["overall_health"] = "excellent"
            elif total_score >= 70:
                health["overall_health"] = "good"
            elif total_score >= 50:
                health["overall_health"] = "fair"
            else:
                health["overall_health"] = "needs_attention"

            return health

        except Exception as e:
            logger.error(f"Failed to get platform health: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

# Initialize database manager
db_manager = DatabaseManager()