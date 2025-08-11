# Administrator Console System for OnlyMentors.ai
# Separate admin authentication and management system

from fastapi import HTTPException
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
import os
from enum import Enum

class AdminRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN_MANAGER = "admin_manager" 
    REPORTS_VIEWER = "reports_viewer"
    AI_AGENT = "ai_agent"

class AdminStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    INACTIVE = "inactive"

class UserAction(str, Enum):
    SUSPEND = "suspend"
    REACTIVATE = "reactivate"
    DELETE = "delete"

class MentorAction(str, Enum):
    APPROVE = "approve"
    REJECT = "reject"
    SUSPEND = "suspend"
    REACTIVATE = "reactivate"
    DELETE = "delete"

# Pydantic Models
class AdminSignupRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: AdminRole = AdminRole.ADMIN_MANAGER

class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserManagementRequest(BaseModel):
    user_ids: List[str]
    action: UserAction
    reason: Optional[str] = None

class MentorManagementRequest(BaseModel):
    creator_ids: List[str] 
    action: MentorAction
    reason: Optional[str] = None

# Database Schemas
def get_admin_document_schema():
    """Admin account document schema for MongoDB"""
    return {
        "admin_id": str,
        "email": str,
        "password_hash": str,
        "full_name": str,
        "role": AdminRole,
        "status": AdminStatus,
        "permissions": List[str],
        "created_by": Optional[str],  # admin_id who created this admin
        "created_at": datetime,
        "updated_at": datetime,
        "last_login": Optional[datetime],
        "login_attempts": int,
        "locked_until": Optional[datetime]
    }

def get_admin_activity_log_schema():
    """Admin activity logging schema"""
    return {
        "log_id": str,
        "admin_id": str,
        "action": str,
        "target_type": str,  # "user", "mentor", "system"
        "target_id": Optional[str],
        "details": Dict[str, Any],
        "ip_address": Optional[str],
        "user_agent": Optional[str],
        "timestamp": datetime
    }

def get_platform_metrics_schema():
    """Platform-wide metrics for admin dashboard"""
    return {
        "metrics_id": str,
        "date": datetime,
        "total_users": int,
        "active_users": int,
        "new_users": int,
        "total_mentors": int,
        "active_mentors": int,
        "new_mentors": int,
        "total_questions": int,
        "questions_today": int,
        "total_revenue": float,
        "revenue_today": float,
        "monthly_revenue": float,
        "subscription_count": int,
        "created_at": datetime
    }

# Helper Functions
def generate_admin_id() -> str:
    """Generate unique admin ID"""
    return f"admin_{uuid.uuid4().hex[:12]}"

def generate_log_id() -> str:
    """Generate unique log ID"""
    return f"log_{uuid.uuid4().hex[:12]}"

def get_admin_public_profile(admin_doc: dict) -> dict:
    """Get safe admin profile (hide sensitive info)"""
    return {
        "admin_id": admin_doc["admin_id"],
        "email": admin_doc["email"],
        "full_name": admin_doc["full_name"],
        "role": admin_doc["role"],
        "status": admin_doc["status"],
        "created_at": admin_doc["created_at"],
        "last_login": admin_doc.get("last_login")
    }

# Role Permissions
ROLE_PERMISSIONS = {
    AdminRole.SUPER_ADMIN: [
        "create_admin", "delete_admin", "manage_users", "manage_mentors", 
        "view_reports", "manage_system", "view_financials", "export_data"
    ],
    AdminRole.ADMIN_MANAGER: [
        "manage_users", "manage_mentors", "view_reports", "view_financials"
    ],
    AdminRole.REPORTS_VIEWER: [
        "view_reports", "view_financials", "export_reports"
    ],
    AdminRole.AI_AGENT: [
        "manage_content_moderation", "automated_tasks", "view_reports"
    ]
}

def has_permission(admin_role: AdminRole, required_permission: str) -> bool:
    """Check if admin role has required permission"""
    return required_permission in ROLE_PERMISSIONS.get(admin_role, [])

# Analytics Helper Functions
def calculate_user_metrics(users: List[dict]) -> Dict[str, Any]:
    """Calculate user activity metrics"""
    now = datetime.utcnow()
    today = now.date()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    
    total_users = len(users)
    active_users = sum(1 for u in users if u.get('last_active') and u['last_active'] >= week_ago)
    new_users_today = sum(1 for u in users if u.get('created_at') and u['created_at'].date() == today)
    new_users_week = sum(1 for u in users if u.get('created_at') and u['created_at'] >= week_ago)
    new_users_month = sum(1 for u in users if u.get('created_at') and u['created_at'] >= month_ago)
    
    subscribed_users = sum(1 for u in users if u.get('is_subscribed', False))
    subscription_revenue = subscribed_users * 29.99  # Estimate based on monthly
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "new_users_today": new_users_today,
        "new_users_week": new_users_week,
        "new_users_month": new_users_month,
        "subscribed_users": subscribed_users,
        "subscription_revenue": subscription_revenue
    }

def calculate_mentor_metrics(mentors: List[dict]) -> Dict[str, Any]:
    """Calculate mentor activity metrics"""
    from datetime import timedelta
    
    now = datetime.utcnow()
    today = now.date()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    
    total_mentors = len(mentors)
    active_mentors = sum(1 for m in mentors if m.get('last_active') and m['last_active'] >= week_ago)
    approved_mentors = sum(1 for m in mentors if m.get('status') == 'approved')
    pending_mentors = sum(1 for m in mentors if m.get('status') == 'pending')
    
    new_mentors_today = sum(1 for m in mentors if m.get('created_at') and m['created_at'].date() == today)
    new_mentors_week = sum(1 for m in mentors if m.get('created_at') and m['created_at'] >= week_ago)
    new_mentors_month = sum(1 for m in mentors if m.get('created_at') and m['created_at'] >= month_ago)
    
    # Calculate earnings
    total_earnings = sum(m.get('stats', {}).get('total_earnings', 0) for m in mentors)
    monthly_earnings = sum(m.get('stats', {}).get('monthly_earnings', 0) for m in mentors)
    
    return {
        "total_mentors": total_mentors,
        "active_mentors": active_mentors,
        "approved_mentors": approved_mentors,
        "pending_mentors": pending_mentors,
        "new_mentors_today": new_mentors_today,
        "new_mentors_week": new_mentors_week,
        "new_mentors_month": new_mentors_month,
        "total_earnings": total_earnings,
        "monthly_earnings": monthly_earnings
    }

def calculate_financial_metrics(payments: List[dict], subscriptions: List[dict]) -> Dict[str, Any]:
    """Calculate financial metrics for admin dashboard"""
    from datetime import timedelta
    
    now = datetime.utcnow()
    today = now.date()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    
    # Payment metrics
    total_revenue = sum(p.get('amount', 0) for p in payments if p.get('payment_status') == 'paid')
    revenue_today = sum(p.get('amount', 0) for p in payments 
                       if p.get('payment_status') == 'paid' and 
                       p.get('created_at') and p['created_at'].date() == today)
    revenue_week = sum(p.get('amount', 0) for p in payments 
                      if p.get('payment_status') == 'paid' and 
                      p.get('created_at') and p['created_at'] >= week_ago)
    revenue_month = sum(p.get('amount', 0) for p in payments 
                       if p.get('payment_status') == 'paid' and 
                       p.get('created_at') and p['created_at'] >= month_ago)
    
    # Subscription metrics
    active_subscriptions = sum(1 for s in subscriptions if s.get('status') == 'active')
    monthly_recurring = sum(s.get('monthly_price', 0) for s in subscriptions if s.get('status') == 'active')
    
    # Platform commission (20%)
    platform_revenue = total_revenue * 0.20
    creator_payouts = total_revenue * 0.80
    
    return {
        "total_revenue": total_revenue,
        "revenue_today": revenue_today,
        "revenue_week": revenue_week,
        "revenue_month": revenue_month,
        "active_subscriptions": active_subscriptions,
        "monthly_recurring_revenue": monthly_recurring,
        "platform_revenue": platform_revenue,
        "creator_payouts": creator_payouts,
        "avg_transaction_value": total_revenue / len(payments) if payments else 0
    }

# Initial Super Admin Creation
INITIAL_SUPER_ADMIN = {
    "email": "admin@onlymentors.ai",
    "password": "SuperAdmin2024!",  # Change in production
    "full_name": "Super Administrator",
    "role": AdminRole.SUPER_ADMIN
}

def create_initial_super_admin_doc(password_hash: str) -> dict:
    """Create initial super admin document"""
    admin_id = generate_admin_id()
    return {
        "admin_id": admin_id,
        "email": INITIAL_SUPER_ADMIN["email"],
        "password_hash": password_hash,
        "full_name": INITIAL_SUPER_ADMIN["full_name"],
        "role": INITIAL_SUPER_ADMIN["role"],
        "status": AdminStatus.ACTIVE,
        "permissions": ROLE_PERMISSIONS[AdminRole.SUPER_ADMIN],
        "created_by": None,  # Initial admin
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "last_login": None,
        "login_attempts": 0,
        "locked_until": None
    }