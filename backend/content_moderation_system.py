# Content Moderation System for Administrator Console
# Handles moderation of videos, user-generated content, and profiles

from fastapi import HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
from enum import Enum

class ContentType(str, Enum):
    VIDEO = "video"
    DOCUMENT = "document"
    PROFILE = "profile"
    USER_COMMENT = "user_comment"
    USER_REVIEW = "user_review"
    MENTOR_DESCRIPTION = "mentor_description"

class ModerationStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    FLAGGED = "flagged"
    REMOVED = "removed"
    UNDER_REVIEW = "under_review"

class ModerationAction(str, Enum):
    APPROVE = "approve"
    REJECT = "reject"
    FLAG = "flag"
    REMOVE = "remove"
    REVIEW = "review"

class ModerationPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

# Pydantic Models
class ModerationRequest(BaseModel):
    content_ids: List[str]
    action: ModerationAction
    reason: Optional[str] = None
    reviewer_notes: Optional[str] = None

class ContentModerationFilter(BaseModel):
    content_type: Optional[ContentType] = None
    status: Optional[ModerationStatus] = None
    priority: Optional[ModerationPriority] = None
    creator_id: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None

# Database Schemas
def get_content_moderation_schema():
    """Content moderation document schema for MongoDB"""
    return {
        "moderation_id": str,
        "content_id": str,
        "content_type": ContentType,
        "creator_id": Optional[str],
        "user_id": Optional[str],
        "title": str,
        "description": Optional[str],
        "file_url": Optional[str],
        "file_size": Optional[int],
        "file_type": Optional[str],
        "content_preview": Optional[str],
        "status": ModerationStatus,
        "priority": ModerationPriority,
        "flagged_reasons": List[str],
        "auto_flags": Dict[str, Any],  # AI-generated flags
        "manual_flags": Dict[str, Any],  # Admin manual flags
        "moderation_history": List[Dict[str, Any]],
        "assigned_moderator": Optional[str],
        "reviewed_by": Optional[str],
        "reviewed_at": Optional[datetime],
        "review_notes": Optional[str],
        "created_at": datetime,
        "updated_at": datetime
    }

def get_moderation_activity_log_schema():
    """Moderation activity logging schema"""
    return {
        "activity_id": str,
        "admin_id": str,
        "action": ModerationAction,
        "content_id": str,
        "content_type": ContentType,
        "previous_status": ModerationStatus,
        "new_status": ModerationStatus,
        "reason": Optional[str],
        "reviewer_notes": Optional[str],
        "ip_address": Optional[str],
        "user_agent": Optional[str],
        "timestamp": datetime
    }

# Helper Functions
def generate_moderation_id() -> str:
    """Generate unique moderation ID"""
    return f"mod_{uuid.uuid4().hex[:12]}"

def generate_activity_id() -> str:
    """Generate unique activity ID"""
    return f"act_{uuid.uuid4().hex[:12]}"

def calculate_content_priority(content_data: dict) -> ModerationPriority:
    """Calculate content moderation priority based on various factors"""
    # High priority for explicit content or large files
    if content_data.get('file_size', 0) > 100 * 1024 * 1024:  # 100MB+
        return ModerationPriority.HIGH
    
    # Medium priority for video content
    if content_data.get('content_type') == ContentType.VIDEO:
        return ModerationPriority.MEDIUM
    
    # High priority for profiles (user safety)
    if content_data.get('content_type') == ContentType.PROFILE:
        return ModerationPriority.HIGH
    
    return ModerationPriority.LOW

def get_auto_moderation_flags(content_data: dict) -> Dict[str, Any]:
    """Generate automatic moderation flags (placeholder for AI integration)"""
    flags = {
        "inappropriate_content": False,
        "violence_detected": False,
        "adult_content": False,
        "spam_detected": False,
        "duplicate_content": False,
        "copyright_violation": False,
        "confidence_scores": {},
        "ai_review_needed": False
    }
    
    # Simple rule-based checks (would be replaced with AI)
    if content_data.get('file_size', 0) < 1000:  # Very small files
        flags["spam_detected"] = True
    
    if content_data.get('content_type') == ContentType.VIDEO:
        flags["ai_review_needed"] = True
    
    return flags

def create_moderation_activity_log(admin_id: str, action: ModerationAction, content_id: str, 
                                 content_type: ContentType, previous_status: ModerationStatus,
                                 new_status: ModerationStatus, reason: str = None,
                                 reviewer_notes: str = None) -> dict:
    """Create moderation activity log entry"""
    return {
        "activity_id": generate_activity_id(),
        "admin_id": admin_id,
        "action": action,
        "content_id": content_id,
        "content_type": content_type,
        "previous_status": previous_status,
        "new_status": new_status,
        "reason": reason,
        "reviewer_notes": reviewer_notes,
        "ip_address": None,  # Will be populated by endpoint
        "user_agent": None,  # Will be populated by endpoint
        "timestamp": datetime.utcnow()
    }

# Content Processing Functions
def process_creator_video_for_moderation(video_data: dict) -> dict:
    """Process creator video upload for moderation"""
    moderation_doc = {
        "moderation_id": generate_moderation_id(),
        "content_id": video_data["content_id"],
        "content_type": ContentType.VIDEO,
        "creator_id": video_data["creator_id"],
        "user_id": None,
        "title": video_data.get("title", "Untitled Video"),
        "description": video_data.get("description"),
        "file_url": video_data["file_url"],
        "file_size": video_data.get("file_size"),
        "file_type": video_data.get("file_type"),
        "content_preview": video_data.get("thumbnail_url"),
        "status": ModerationStatus.PENDING,
        "priority": calculate_content_priority(video_data),
        "flagged_reasons": [],
        "auto_flags": get_auto_moderation_flags(video_data),
        "manual_flags": {},
        "moderation_history": [],
        "assigned_moderator": None,
        "reviewed_by": None,
        "reviewed_at": None,
        "review_notes": None,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    return moderation_doc

def process_mentor_profile_for_moderation(profile_data: dict) -> dict:
    """Process mentor profile for moderation"""
    moderation_doc = {
        "moderation_id": generate_moderation_id(),
        "content_id": f"profile_{profile_data['creator_id']}",
        "content_type": ContentType.PROFILE,
        "creator_id": profile_data["creator_id"],
        "user_id": None,
        "title": f"Profile: {profile_data.get('account_name', 'Unknown')}",
        "description": profile_data.get("service_description"),
        "file_url": profile_data.get("profile_image_url"),
        "file_size": None,
        "file_type": "profile",
        "content_preview": profile_data.get("account_name"),
        "status": ModerationStatus.PENDING,
        "priority": ModerationPriority.HIGH,  # Profiles are high priority
        "flagged_reasons": [],
        "auto_flags": get_auto_moderation_flags(profile_data),
        "manual_flags": {},
        "moderation_history": [],
        "assigned_moderator": None,
        "reviewed_by": None,
        "reviewed_at": None,
        "review_notes": None,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    return moderation_doc

def process_user_comment_for_moderation(comment_data: dict) -> dict:
    """Process user comment for moderation"""
    moderation_doc = {
        "moderation_id": generate_moderation_id(),
        "content_id": comment_data["comment_id"],
        "content_type": ContentType.USER_COMMENT,
        "creator_id": None,
        "user_id": comment_data["user_id"],
        "title": f"Comment by {comment_data.get('user_name', 'Unknown')}",
        "description": comment_data["comment_text"],
        "file_url": None,
        "file_size": None,
        "file_type": "text",
        "content_preview": comment_data["comment_text"][:200],
        "status": ModerationStatus.PENDING,
        "priority": calculate_content_priority(comment_data),
        "flagged_reasons": [],
        "auto_flags": get_auto_moderation_flags(comment_data),
        "manual_flags": {},
        "moderation_history": [],
        "assigned_moderator": None,
        "reviewed_by": None,
        "reviewed_at": None,
        "review_notes": None,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    return moderation_doc

# Statistics and Analytics
def calculate_moderation_stats(moderation_data: List[dict]) -> Dict[str, Any]:
    """Calculate moderation statistics for admin dashboard"""
    total_content = len(moderation_data)
    
    if total_content == 0:
        return {
            "total_content": 0,
            "pending_review": 0,
            "approved": 0,
            "rejected": 0,
            "flagged": 0,
            "removed": 0,
            "approval_rate": 0,
            "avg_review_time": 0,
            "by_content_type": {},
            "by_priority": {},
            "recent_activity": []
        }
    
    stats = {
        "total_content": total_content,
        "pending_review": sum(1 for item in moderation_data if item["status"] == ModerationStatus.PENDING),
        "approved": sum(1 for item in moderation_data if item["status"] == ModerationStatus.APPROVED),
        "rejected": sum(1 for item in moderation_data if item["status"] == ModerationStatus.REJECTED),
        "flagged": sum(1 for item in moderation_data if item["status"] == ModerationStatus.FLAGGED),
        "removed": sum(1 for item in moderation_data if item["status"] == ModerationStatus.REMOVED),
    }
    
    # Calculate approval rate
    reviewed = stats["approved"] + stats["rejected"]
    stats["approval_rate"] = (stats["approved"] / reviewed * 100) if reviewed > 0 else 0
    
    # Group by content type
    content_types = {}
    for item in moderation_data:
        content_type = item["content_type"]
        if content_type not in content_types:
            content_types[content_type] = 0
        content_types[content_type] += 1
    stats["by_content_type"] = content_types
    
    # Group by priority
    priorities = {}
    for item in moderation_data:
        priority = item["priority"]
        if priority not in priorities:
            priorities[priority] = 0
        priorities[priority] += 1
    stats["by_priority"] = priorities
    
    # Recent activity (placeholder)
    stats["recent_activity"] = []
    stats["avg_review_time"] = 0  # Would calculate based on review timestamps
    
    return stats

# Flag Management
COMMON_FLAG_REASONS = [
    "Inappropriate content",
    "Violent content", 
    "Adult/explicit content",
    "Spam or misleading",
    "Copyright violation",
    "Harassment or bullying",
    "False information",
    "Privacy violation",
    "Terms of service violation",
    "Other"
]

def get_content_moderation_summary(content_id: str, moderation_data: dict) -> str:
    """Generate human-readable summary for moderation item"""
    content_type = moderation_data["content_type"]
    status = moderation_data["status"]
    priority = moderation_data["priority"]
    
    summary = f"{content_type.title()} content "
    
    if moderation_data.get("creator_id"):
        summary += f"by creator {moderation_data['creator_id'][:8]}... "
    elif moderation_data.get("user_id"):
        summary += f"by user {moderation_data['user_id'][:8]}... "
    
    summary += f"({status}, {priority} priority)"
    
    if moderation_data.get("flagged_reasons"):
        summary += f" - Flagged: {', '.join(moderation_data['flagged_reasons'])}"
    
    return summary