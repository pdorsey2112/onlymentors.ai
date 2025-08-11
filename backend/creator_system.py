# Creator System for OnlyMentors.ai
# Two-sided marketplace with creator onboarding, verification, and dashboard

from fastapi import HTTPException, UploadFile, File, Form
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
import os
from enum import Enum

class CreatorStatus(str, Enum):
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUSPENDED = "suspended"

class ContentType(str, Enum):
    VIDEO = "video"
    DOCUMENT = "document"
    ARTICLE_LINK = "article_link"

class CreatorSignupRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    account_name: str
    description: str
    monthly_price: float = Field(ge=1.0, le=1000.0)  # $1-$1000 per month
    category: str
    expertise_areas: List[str]
    
class CreatorProfileUpdate(BaseModel):
    account_name: Optional[str] = None
    description: Optional[str] = None
    monthly_price: Optional[float] = Field(None, ge=1.0, le=1000.0)
    expertise_areas: Optional[List[str]] = None
    bio: Optional[str] = None
    social_links: Optional[Dict[str, str]] = None

class BankingInfoRequest(BaseModel):
    bank_account_number: str
    routing_number: str
    tax_id: str
    account_holder_name: str
    bank_name: str

class ContentUploadRequest(BaseModel):
    title: str
    description: str
    content_type: ContentType
    category: Optional[str] = None
    tags: Optional[List[str]] = None

class MessageRequest(BaseModel):
    recipient_id: str
    content: str
    message_type: str = "text"  # text, file, etc.

# Database schemas for creators
def get_creator_document_schema():
    """Creator document schema for MongoDB"""
    return {
        "creator_id": str,
        "user_id": str,  # Link to regular user account if upgraded
        "email": str,
        "full_name": str,
        "account_name": str,  # Display name
        "description": str,
        "bio": str,
        "monthly_price": float,
        "category": str,
        "expertise_areas": List[str],
        "status": CreatorStatus,
        "profile_image_url": Optional[str],
        "cover_image_url": Optional[str],
        "social_links": Dict[str, str],
        "verification": {
            "id_verified": bool,
            "bank_verified": bool,
            "id_document_url": Optional[str],
            "submitted_at": Optional[datetime],
            "verified_at": Optional[datetime]
        },
        "banking_info": {
            "bank_account_number": str,  # Encrypted
            "routing_number": str,
            "tax_id": str,  # Encrypted
            "account_holder_name": str,
            "bank_name": str,
            "verified": bool
        },
        "stats": {
            "total_earnings": float,
            "monthly_earnings": float,
            "subscriber_count": int,
            "content_count": int,
            "total_questions": int,
            "average_rating": float
        },
        "settings": {
            "auto_approve_messages": bool,
            "allow_tips": bool,
            "response_time": str  # "24 hours", "instant", etc.
        },
        "created_at": datetime,
        "updated_at": datetime,
        "last_active": datetime
    }

def get_creator_content_schema():
    """Creator content document schema"""
    return {
        "content_id": str,
        "creator_id": str,
        "title": str,
        "description": str,
        "content_type": ContentType,
        "file_url": Optional[str],
        "file_size": Optional[int],
        "file_type": Optional[str],
        "thumbnail_url": Optional[str],
        "category": Optional[str],
        "tags": List[str],
        "view_count": int,
        "like_count": int,
        "is_featured": bool,
        "is_public": bool,
        "created_at": datetime,
        "updated_at": datetime
    }

def get_creator_message_schema():
    """Direct message schema between creators and users"""
    return {
        "message_id": str,
        "conversation_id": str,
        "sender_id": str,
        "recipient_id": str,
        "sender_type": str,  # "creator" or "user"
        "content": str,
        "message_type": str,  # "text", "file", "tip"
        "file_url": Optional[str],
        "read": bool,
        "created_at": datetime
    }

def get_creator_subscription_schema():
    """User subscriptions to creators"""
    return {
        "subscription_id": str,
        "user_id": str,
        "creator_id": str,
        "status": str,  # "active", "cancelled", "expired"
        "monthly_price": float,
        "start_date": datetime,
        "end_date": datetime,
        "auto_renew": bool,
        "payment_method_id": str,
        "created_at": datetime,
        "updated_at": datetime
    }

def get_creator_analytics_schema():
    """Creator analytics and earnings"""
    return {
        "analytics_id": str,
        "creator_id": str,
        "date": datetime,
        "earnings": float,
        "subscribers_gained": int,
        "subscribers_lost": int,
        "content_views": int,
        "messages_sent": int,
        "messages_received": int,
        "questions_answered": int,
        "average_response_time": float,  # in hours
        "created_at": datetime
    }

# File upload validation
ALLOWED_VIDEO_TYPES = [
    "video/mp4", "video/avi", "video/mov", "video/wmv", 
    "video/flv", "video/webm", "video/mkv"
]

ALLOWED_DOCUMENT_TYPES = [
    "application/pdf",
    "application/msword", 
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
    "application/vnd.google-apps.document"
]

MAX_VIDEO_SIZE = 200 * 1024 * 1024  # 200MB
MAX_DOCUMENT_SIZE = 50 * 1024 * 1024  # 50MB

def validate_file_upload(file: UploadFile, content_type: ContentType) -> bool:
    """Validate uploaded file based on content type"""
    if content_type == ContentType.VIDEO:
        return (
            file.content_type in ALLOWED_VIDEO_TYPES and
            file.size <= MAX_VIDEO_SIZE
        )
    elif content_type == ContentType.DOCUMENT:
        return (
            file.content_type in ALLOWED_DOCUMENT_TYPES and
            file.size <= MAX_DOCUMENT_SIZE
        )
    return False

# Revenue sharing configuration
PLATFORM_COMMISSION = 0.20  # 20% platform fee
CREATOR_PAYOUT = 0.80  # 80% to creator

# Payout thresholds and schedules
MIN_PAYOUT_AMOUNT = 50.00  # Minimum $50 for payout
PAYOUT_SCHEDULE = "monthly"  # weekly, bi-weekly, monthly

def calculate_creator_earnings(gross_amount: float) -> Dict[str, float]:
    """Calculate creator earnings after platform commission"""
    platform_fee = gross_amount * PLATFORM_COMMISSION
    creator_earnings = gross_amount * CREATOR_PAYOUT
    
    return {
        "gross_amount": gross_amount,
        "platform_fee": platform_fee,
        "creator_earnings": creator_earnings
    }

# Helper functions for creator operations
def generate_creator_id() -> str:
    """Generate unique creator ID"""
    return f"creator_{uuid.uuid4().hex[:12]}"

def generate_content_id() -> str:
    """Generate unique content ID"""
    return f"content_{uuid.uuid4().hex[:12]}"

def generate_message_id() -> str:
    """Generate unique message ID"""
    return f"msg_{uuid.uuid4().hex[:12]}"

def generate_conversation_id(user_id: str, creator_id: str) -> str:
    """Generate conversation ID between user and creator"""
    return f"conv_{hash(f'{user_id}_{creator_id}') % 1000000}"

# Creator verification helpers
def mask_sensitive_data(data: str, show_last: int = 4) -> str:
    """Mask sensitive banking information"""
    if len(data) <= show_last:
        return "*" * len(data)
    return "*" * (len(data) - show_last) + data[-show_last:]

def get_creator_public_profile(creator_doc: dict) -> dict:
    """Get public creator profile (hide sensitive info)"""
    return {
        "creator_id": creator_doc["creator_id"],
        "account_name": creator_doc["account_name"],
        "description": creator_doc["description"],
        "bio": creator_doc.get("bio"),
        "monthly_price": creator_doc["monthly_price"],
        "category": creator_doc["category"],
        "expertise_areas": creator_doc["expertise_areas"],
        "profile_image_url": creator_doc.get("profile_image_url"),
        "cover_image_url": creator_doc.get("cover_image_url"),
        "social_links": creator_doc.get("social_links", {}),
        "stats": {
            "subscriber_count": creator_doc["stats"]["subscriber_count"],
            "content_count": creator_doc["stats"]["content_count"],
            "average_rating": creator_doc["stats"]["average_rating"]
        },
        "is_verified": creator_doc["verification"]["id_verified"] and creator_doc["verification"]["bank_verified"],
        "created_at": creator_doc["created_at"]
    }

# Integration with existing mentor system
def integrate_with_existing_mentors(category_mentors: List[dict], creator_mentors: List[dict]) -> List[dict]:
    """Integrate creator mentors with existing top mentors"""
    # Take top 20 existing mentors
    top_existing = category_mentors[:20]
    
    # Convert creator profiles to mentor format
    creator_mentors_formatted = []
    for creator in creator_mentors:
        mentor_format = {
            "id": creator["creator_id"],
            "name": creator["account_name"],
            "title": f"Creator - {creator['category'].title()}",
            "bio": creator["description"],
            "expertise": ", ".join(creator["expertise_areas"]),
            "image_url": creator.get("profile_image_url"),
            "wiki_description": creator.get("bio", creator["description"]),
            "is_creator": True,
            "monthly_price": creator["monthly_price"],
            "subscriber_count": creator["stats"]["subscriber_count"],
            "average_rating": creator["stats"]["average_rating"]
        }
        creator_mentors_formatted.append(mentor_format)
    
    # Return top 20 existing + creators
    return top_existing + creator_mentors_formatted