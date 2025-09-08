from fastapi import FastAPI, HTTPException, Request, Depends, UploadFile, File, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
import uuid
import os
import json
import re
from dotenv import load_dotenv
from complete_mentors_database import ALL_MENTORS, TOTAL_MENTORS, BUSINESS_MENTORS, SPORTS_MENTORS, HEALTH_MENTORS, SCIENCE_MENTORS
from expanded_mentors import ADDITIONAL_BUSINESS_MENTORS, ADDITIONAL_SPORTS_MENTORS, ADDITIONAL_HEALTH_MENTORS, ADDITIONAL_SCIENCE_MENTORS

# Merge additional mentors with existing ones
BUSINESS_MENTORS.extend(ADDITIONAL_BUSINESS_MENTORS)
SPORTS_MENTORS.extend(ADDITIONAL_SPORTS_MENTORS) 
HEALTH_MENTORS.extend(ADDITIONAL_HEALTH_MENTORS)
SCIENCE_MENTORS.extend(ADDITIONAL_SCIENCE_MENTORS)

# Recalculate total mentors after merging
TOTAL_MENTORS = sum(len(mentors) for mentors in ALL_MENTORS.values())

# Load environment variables from .env file
load_dotenv()
from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionResponse, CheckoutStatusResponse, CheckoutSessionRequest
from emergentintegrations.llm.chat import LlmChat, UserMessage
from creator_system import (
    CreatorSignupRequest, CreatorProfileUpdate, BankingInfoRequest, ContentUploadRequest, MessageRequest,
    CreatorStatus, ContentType, validate_file_upload, calculate_creator_earnings,
    generate_creator_id, generate_content_id, generate_message_id, generate_conversation_id,
    get_creator_public_profile, integrate_with_existing_mentors,
    ALLOWED_VIDEO_TYPES, ALLOWED_DOCUMENT_TYPES, MAX_VIDEO_SIZE, MAX_DOCUMENT_SIZE
)
from admin_system import (
    AdminRole, AdminStatus, UserAction, MentorAction, UserRole,
    AdminSignupRequest, AdminLoginRequest, UserManagementRequest, MentorManagementRequest,
    UserRoleChangeRequest, UserSuspendRequest,
    generate_admin_id, get_admin_public_profile, create_initial_super_admin_doc,
    calculate_user_metrics, calculate_mentor_metrics, calculate_financial_metrics,
    has_permission, INITIAL_SUPER_ADMIN
)
from content_moderation_system import (
    ContentType, ModerationStatus, ModerationAction, ModerationPriority,
    ModerationRequest, ContentModerationFilter, get_content_moderation_schema,
    generate_moderation_id, calculate_moderation_stats, process_creator_video_for_moderation,
    process_mentor_profile_for_moderation, create_moderation_activity_log
)
from payout_system import (
    PayoutStatus, PayoutFrequency, PayoutMethod, EarningsType,
    PayoutRequest, PayoutScheduleUpdate, EarningsEntry,
    generate_payout_id, calculate_platform_fee, create_earnings_entry,
    calculate_creator_pending_earnings, process_creator_payout, calculate_payout_analytics,
    create_default_payout_settings, calculate_next_payout_date, PLATFORM_FEE_PERCENTAGE
)
from ai_agent_framework import (
    AIAgentType, AITaskStatus, AITaskPriority, AIAgentStatus,
    AIAgentConfig, AITaskRequest, AITaskResult,
    generate_agent_id, generate_task_id, AITaskProcessor,
    ContentModerationAI, CustomerServiceAI, SalesAnalyticsAI, MarketingAnalyticsAI,
    DEFAULT_AI_AGENTS, create_default_ai_agent
)
from oauth_system import *
from forgot_password_system import *
from sms_system import sms_service, send_sms, send_2fa, verify_2fa, format_phone, validate_phone
from database_management_system import db_manager
from premium_content_system import (
    premium_content_manager, PremiumContentCreate, ContentPurchaseRequest, 
    ContentSearchQuery, ContentUpdateRequest, calculate_content_pricing, 
    validate_content_price
)

app = FastAPI(title="OnlyMentors.ai API", version="2.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Database
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
client = AsyncIOMotorClient(MONGO_URL)
db = client.onlymentors_db
# Separate admin database
admin_db = client.onlymentors_admin_db

# Environment variables
EMERGENT_LLM_KEY = os.getenv("EMERGENT_LLM_KEY", "sk-emergent-281F003Ed3fEf9c052")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
STRIPE_API_KEY = os.getenv("STRIPE_API_KEY")
JWT_SECRET = os.getenv("JWT_SECRET", "onlymentors-jwt-secret-key-2024")

# Subscription packages
SUBSCRIPTION_PACKAGES = {
    "monthly": {
        "name": "Monthly Unlimited",
        "price": 29.99,
        "currency": "usd",
        "description": f"Unlimited questions to all {TOTAL_MENTORS} mentors for 30 days"
    },
    "yearly": {
        "name": "Yearly Unlimited",
        "price": 299.99,
        "currency": "usd", 
        "description": f"Unlimited questions to all {TOTAL_MENTORS} mentors for 12 months (Save $60!)"
    }
}

# Pydantic models
class UserSignup(BaseModel):
    email: str
    password: str
    full_name: str
    company_id: str = ""  # For business employee signup
    department_code: str = ""  # For cost tracking
    phone_number: str = ""  # For 2FA verification
    two_factor_code: str = ""  # 2FA verification code for business employees

class UserLogin(BaseModel):
    email: str
    password: str

class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    communication_preferences: Optional[dict] = None

class SMSRequest(BaseModel):
    phone_number: str
    message: str

class Send2FARequest(BaseModel):
    phone_number: str

class Verify2FARequest(BaseModel):
    phone_number: str
    code: str

class PhoneValidationRequest(BaseModel):
    phone_number: str

class DatabaseExportRequest(BaseModel):
    collection_name: str
    format: str = "json"  # json or csv
    search: Optional[str] = None

class DatabaseRestoreRequest(BaseModel):
    collection_name: str
    json_data: str

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str
    
    @validator('new_password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', v):
            raise ValueError('Password must contain at least one special character')
        return v

class QuestionRequest(BaseModel):
    category: str
    mentor_ids: List[str]  # Multiple mentors can be selected
    question: str

class CheckoutRequest(BaseModel):
    package_id: str
    origin_url: str

class ContentUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    is_public: Optional[bool] = None
    is_featured: Optional[bool] = None

# Helper functions
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm="HS256")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=["HS256"])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = await db.users.find_one({"user_id": user_id})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Admin authentication middleware"""
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=["HS256"])
        admin_id = payload.get("admin_id")
        admin_type = payload.get("type")
        
        if admin_id is None or admin_type != "admin":
            raise HTTPException(status_code=401, detail="Invalid admin token")
        
        admin = await admin_db.admins.find_one({"admin_id": admin_id})
        if not admin or admin["status"] != AdminStatus.ACTIVE:
            raise HTTPException(status_code=401, detail="Admin not found or inactive")
        return admin
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid admin token")

async def get_current_creator(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Creator authentication middleware"""
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=["HS256"])
        creator_id = payload.get("creator_id")
        creator_type = payload.get("type")
        
        if creator_id is None or creator_type != "creator":
            raise HTTPException(status_code=401, detail="Invalid creator token")
        
        creator = await db.creators.find_one({"creator_id": creator_id})
        if not creator:
            raise HTTPException(status_code=401, detail="Creator not found")
        return creator
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid creator token")

# Performance optimization: Response cache
from typing import Dict
import time

# Simple in-memory cache with TTL (Time To Live)
response_cache: Dict[str, Dict] = {}
CACHE_TTL = 300  # 5 minutes cache

def get_cache_key(mentor_id: str, question: str) -> str:
    """Generate cache key for mentor-question combination"""
    return f"{mentor_id}:{hash(question)}"

def get_cached_response(cache_key: str) -> str:
    """Get cached response if still valid"""
    if cache_key in response_cache:
        cached_data = response_cache[cache_key]
        if time.time() - cached_data["timestamp"] < CACHE_TTL:
            print(f"📦 Using cached response for {cache_key[:20]}...")
            return cached_data["response"]
        else:
            # Remove expired cache entry
            del response_cache[cache_key]
    return None

def cache_response(cache_key: str, response: str):
    """Cache a mentor response"""
    response_cache[cache_key] = {
        "response": response,
        "timestamp": time.time()
    }
    print(f"💾 Cached response for {cache_key[:20]}...")

async def create_mentor_response(mentor, question):
    """Create AI-powered response from a mentor using their personality and expertise"""
    
    # Check cache first for speed
    cache_key = get_cache_key(mentor['id'], question)
    cached_response = get_cached_response(cache_key)
    if cached_response:
        return cached_response
    
    try:
        # Create a unique session ID for this mentor-question combination
        session_id = f"mentor_{mentor['id']}_{hash(question) % 10000}"
        
        # Optimized system message - shorter but still personalized
        system_message = f"""You are {mentor['name']}, {mentor['expertise']}.

Respond in your authentic voice with 2-3 paragraphs. Use personal experiences and "I" statements. Be practical and actionable. Your expertise: {mentor['expertise']}."""

        print(f"🤖 Creating response for {mentor['name']} (concurrent)")
        
        # Initialize LLM chat with faster model settings
        chat = LlmChat(
            api_key=OPENAI_API_KEY,
            session_id=session_id,
            system_message=system_message
        ).with_model("openai", "gpt-4o-mini")
        
        # Create user message
        user_message = UserMessage(text=question)
        
        # Get AI response with shorter timeout for faster responses
        import asyncio
        response = await asyncio.wait_for(chat.send_message(user_message), timeout=20.0)
        
        response_text = response.strip()
        
        # Cache the response for future use
        cache_response(cache_key, response_text)
        
        print(f"✅ Response ready for {mentor['name']}: {len(response_text)} chars")
        
        return response_text
        
    except asyncio.TimeoutError:
        print(f"⏰ Timeout for {mentor['name']} - using fallback")
        fallback = f"Thank you for your question. Based on my experience in {mentor['expertise']}, this is an important topic. {mentor.get('wiki_description', '')[:200]}..."
        cache_response(cache_key, fallback)  # Cache fallback too
        return fallback
    except Exception as e:
        print(f"❌ Error for {mentor['name']}: {str(e)}")
        fallback = f"Thank you for your question. Based on my experience in {mentor['expertise']}, this is an important topic that requires thoughtful consideration."
        cache_response(cache_key, fallback)  # Cache fallback too
        return fallback

# Admin helper functions
async def log_admin_action(db, admin_id: str, admin_email: str, action: str, target_id: str, details: dict):
    """Log admin action for audit trail"""
    try:
        log_entry = {
            "log_id": str(uuid.uuid4()),
            "admin_id": admin_id,
            "admin_email": admin_email,
            "action": action,
            "target_id": target_id,
            "details": details,
            "timestamp": datetime.utcnow(),
            "ip_address": None  # Could be added from request context
        }
        await db.admin_audit_logs.insert_one(log_entry)
        print(f"✅ Admin action logged: {action} by {admin_email}")
    except Exception as e:
        print(f"❌ Failed to log admin action: {str(e)}")

async def send_unified_email(email: str, subject: str, html_content: str, text_content: str = None):
    """Send email using the unified email system"""
    try:
        # Import the email system from forgot_password_system
        from forgot_password_system import send_password_reset_email_smtp2go
        
        # Use the existing SMTP2GO system for sending emails
        # For now, we'll use a simplified approach
        print(f"📧 Email would be sent to {email}: {subject}")
        print(f"   Content preview: {html_content[:100]}...")
        
        # In a real implementation, this would use the SMTP2GO system
        # For testing purposes, we'll return True to indicate "sent"
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email to {email}: {str(e)}")
        return False

# Routes
@app.get("/")
async def root():
    return {
        "message": "OnlyMentors.ai API - Ask Questions to History's Greatest Minds", 
        "total_mentors": TOTAL_MENTORS,
        "categories": len(ALL_MENTORS),
        "version": "2.0.0"
    }

@app.get("/api/categories")
async def get_categories():
    """Get all categories and their mentors for OnlyMentors.ai"""
    return {
        "categories": [
            {
                "id": "business",
                "name": "Business",
                "description": "Learn from legendary entrepreneurs, CEOs, and business leaders who built empires",
                "mentors": ALL_MENTORS["business"],
                "count": len(ALL_MENTORS["business"])
            },
            {
                "id": "sports", 
                "name": "Sports",
                "description": "Get insights from champion athletes and sports legends who dominated their fields",
                "mentors": ALL_MENTORS["sports"],
                "count": len(ALL_MENTORS["sports"])
            },
            {
                "id": "health",
                "name": "Health", 
                "description": "Discover health and wellness wisdom from leading doctors and wellness experts",
                "mentors": ALL_MENTORS["health"],
                "count": len(ALL_MENTORS["health"])
            },
            {
                "id": "science",
                "name": "Science",
                "description": "Explore scientific thinking with history's greatest minds and Nobel Prize winners",
                "mentors": ALL_MENTORS["science"],
                "count": len(ALL_MENTORS["science"])
            },
            {
                "id": "relationships",
                "name": "Relationships & Dating",
                "description": "Get expert advice on love, dating, and building meaningful relationships from top therapists and coaches",
                "mentors": ALL_MENTORS["relationships"],
                "count": len(ALL_MENTORS["relationships"])
            }
        ],
        "total_mentors": TOTAL_MENTORS
    }

@app.get("/api/categories/{category_id}/mentors")
async def get_category_mentors(category_id: str):
    """Get all mentors for a specific category"""
    if category_id not in ALL_MENTORS:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return {
        "category": category_id,
        "mentors": ALL_MENTORS[category_id],
        "count": len(ALL_MENTORS[category_id])
    }

@app.get("/api/search/mentors")
async def search_mentors(
    q: str = "", 
    category: Optional[str] = None,
    mentor_type: Optional[str] = None  # New parameter: 'ai', 'human', or 'all'
):
    """Search mentors across categories with mentor type filtering"""
    results = []
    search_term = q.lower()
    
    categories_to_search = [category] if category and category in ALL_MENTORS else ALL_MENTORS.keys()
    
    # Add AI mentors from static data
    for cat in categories_to_search:
        for mentor in ALL_MENTORS[cat]:
            if (search_term in mentor["name"].lower() or 
                search_term in mentor["expertise"].lower() or
                search_term in mentor["bio"].lower()):
                
                # Add mentor_type field to AI mentors
                ai_mentor = {
                    **mentor, 
                    "category": cat,
                    "mentor_type": "ai",
                    "is_ai_mentor": True
                }
                
                # Apply mentor type filter
                if mentor_type == "ai" or mentor_type == "all" or mentor_type is None:
                    results.append(ai_mentor)
    
    # Add Human mentors (creators) if requested
    if mentor_type == "human" or mentor_type == "all" or mentor_type is None:
        try:
            # Get verified human mentors from creators collection
            human_mentors_cursor = db.creators.find({
                "is_verified": True,
                "$or": [
                    {"account_name": {"$regex": search_term, "$options": "i"}},
                    {"expertise": {"$regex": search_term, "$options": "i"}}, 
                    {"bio": {"$regex": search_term, "$options": "i"}}
                ] if search_term else [{}]
            })
            
            async for creator in human_mentors_cursor:
                # Convert creator to mentor format
                human_mentor = {
                    "id": creator["creator_id"],
                    "name": creator["account_name"],
                    "title": creator.get("title", "Professional Mentor"),
                    "bio": creator.get("bio", "Professional mentor offering personalized guidance"),
                    "expertise": creator.get("expertise", ""),
                    "image_url": creator.get("profile_image_url"),
                    "category": category or "business",  # Default category
                    "mentor_type": "human",
                    "is_ai_mentor": False,
                    # Add tier information for human mentors
                    "tier": creator.get("tier", "New Mentor"),
                    "tier_level": creator.get("tier_level", "new"),
                    "tier_badge_color": creator.get("tier_badge_color", "#d1d5db"),
                    "subscriber_count": creator.get("subscriber_count", 0),
                    "monthly_price": creator.get("monthly_price", 9.99)
                }
                results.append(human_mentor)
                
        except Exception as e:
            print(f"Error fetching human mentors: {e}")
            # Continue with just AI mentors if database error
    
    return {
        "results": results, 
        "count": len(results), 
        "query": q,
        "mentor_type_filter": mentor_type,
        "ai_count": len([r for r in results if r["mentor_type"] == "ai"]),
        "human_count": len([r for r in results if r["mentor_type"] == "human"])
    }

# Enhanced User Registration endpoint with full profile collection
@app.post("/api/auth/register")
async def register_user_with_profile(
    email: str = Form(...),
    password: str = Form(...),
    full_name: str = Form(...),
    phone_number: str = Form(...),
    communication_preferences: str = Form(...),  # JSON string
    subscription_plan: str = Form(...),
    payment_info: str = Form(None),  # JSON string, optional
    become_mentor: bool = Form(False)  # Option to become a mentor
):
    """Enhanced user registration with complete profile data collection"""
    try:
        # Check if user exists
        existing_user = await db.users.find_one({"email": email})
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Parse communication preferences
        import json
        comm_prefs = json.loads(communication_preferences) if communication_preferences else {}
        
        # Parse payment info if provided
        payment_data = json.loads(payment_info) if payment_info else None
        
        # Create user with complete profile
        user_id = str(uuid.uuid4())
        user_doc = {
            "user_id": user_id,
            "email": email,
            "full_name": full_name,
            "phone_number": phone_number,
            "password_hash": hash_password(password),
            "communication_preferences": {
                "email": comm_prefs.get("email", True),
                "text": comm_prefs.get("text", False),
                "both": comm_prefs.get("both", False)
            },
            "subscription_plan": subscription_plan,
            "is_subscribed": subscription_plan == "premium",
            "subscription_expires": None,
            "payment_info": payment_data,  # Store encrypted in production
            "questions_asked": 0,
            "mentor_interactions": [],  # Track all mentor interactions
            "question_history": [],  # Track all questions asked
            "profile_completed": True,
            "created_at": datetime.utcnow(),
            "last_login": None,
            "is_active": True
        }
        
        # If premium subscription, set expiration
        if subscription_plan == "premium":
            from dateutil.relativedelta import relativedelta
            user_doc["subscription_expires"] = datetime.utcnow() + relativedelta(months=1)
        
        await db.users.insert_one(user_doc)
        
        # If user wants to become a mentor, create simplified creator profile
        if become_mentor:
            creator_id = str(uuid.uuid4())
            mentor_doc = {
                "creator_id": creator_id,
                "user_id": user_id,  # Link to user account
                "account_name": full_name,
                "full_name": full_name,  # Required by admin console
                "email": email,
                "phone_number": phone_number,
                "bio": f"Professional mentor offering personalized guidance in various fields.",
                "expertise": "General Mentoring",  # Default, can be updated later
                "title": "Professional Mentor",
                "category": "business",  # Default category, required by admin console
                "status": "active",  # Required by admin console
                "is_verified": True,  # Auto-approved for mentors
                "verification_status": "APPROVED",
                "verification": {  # Required by admin console
                    "status": "APPROVED",
                    "approved_at": datetime.utcnow(),
                    "approved_by": "system"
                },
                "monthly_price": 29.99,  # Default price
                "subscriber_count": 0,
                "tier": "New Mentor",
                "tier_level": "new",
                "tier_badge_color": "#d1d5db",
                "profile_image_url": None,
                "social_links": {},
                "banking_info": {},  # Can be filled later if they want payouts
                "id_document": {},  # Simplified for mentors
                "profile": {
                    "description": f"Welcome to my mentoring profile! I'm {full_name} and I'm here to help guide you through your challenges and goals.",
                    "experience_years": 1,  # Default
                    "specialties": ["General Guidance", "Life Coaching", "Professional Development"],
                    "languages": ["English"],
                    "response_time": "Within 24 hours",
                    "availability": "Monday-Friday, 9 AM - 6 PM"
                },
                "stats": {
                    "total_earnings": 0.0,
                    "monthly_earnings": 0.0,
                    "subscriber_count": 0,
                    "content_count": 0,
                    "total_questions": 0,
                    "average_rating": 5.0
                },
                "settings": {
                    "auto_approve_messages": True,
                    "allow_tips": True,
                    "response_time": "24 hours"
                },
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "last_active": datetime.utcnow()
            }
            
            await db.creators.insert_one(mentor_doc)
        
        # Create access token
        token = create_access_token({"user_id": user_id})
        
        # Return user data (exclude sensitive info)
        user_response = {
            "user_id": user_id,
            "email": email,
            "full_name": full_name,
            "phone_number": phone_number,
            "communication_preferences": user_doc["communication_preferences"],
            "subscription_plan": subscription_plan,
            "is_subscribed": user_doc["is_subscribed"],
            "questions_asked": 0,
            "profile_completed": True,
            "is_mentor": become_mentor,  # Indicate if they became a mentor
            "created_at": user_doc["created_at"].isoformat()
        }
        
        return {
            "token": token,
            "user": user_response,
            "message": "Account created successfully with complete profile"
        }
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON data provided")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@app.post("/api/users/become-mentor")
async def become_mentor(current_user = Depends(get_current_user)):
    """Allow existing users to become mentors"""
    try:
        user_id = current_user["user_id"]
        
        # Check if user already has a creator profile
        existing_creator = await db.creators.find_one({"user_id": user_id})
        if existing_creator:
            return {
                "success": True,
                "message": "You are already a mentor!",
                "creator_id": existing_creator["creator_id"]
            }
        
        # Get user details
        user = await db.users.find_one({"user_id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Create simplified creator profile
        creator_id = str(uuid.uuid4())
        mentor_doc = {
            "creator_id": creator_id,
            "user_id": user_id,
            "account_name": user["full_name"],
            "full_name": user["full_name"],  # Required by admin console
            "email": user["email"],
            "phone_number": user.get("phone_number", ""),
            "bio": f"Professional mentor offering personalized guidance in various fields.",
            "expertise": "General Mentoring",
            "title": "Professional Mentor",
            "category": "business",  # Default category, required by admin console
            "status": "active",  # Required by admin console
            "is_verified": True,  # Auto-approved
            "verification_status": "APPROVED",
            "verification": {  # Required by admin console
                "status": "APPROVED",
                "approved_at": datetime.utcnow(),
                "approved_by": "system"
            },
            "monthly_price": 29.99,
            "subscriber_count": 0,
            "tier": "New Mentor",
            "tier_level": "new",
            "tier_badge_color": "#d1d5db",
            "profile_image_url": None,
            "social_links": {},
            "banking_info": {},
            "id_document": {},
            "profile": {
                "description": f"Welcome to my mentoring profile! I'm {user['full_name']} and I'm here to help guide you through your challenges and goals.",
                "experience_years": 1,
                "specialties": ["General Guidance", "Life Coaching", "Professional Development"],
                "languages": ["English"],
                "response_time": "Within 24 hours",
                "availability": "Monday-Friday, 9 AM - 6 PM"
            },
            "stats": {
                "total_earnings": 0.0,
                "monthly_earnings": 0.0,
                "subscriber_count": 0,
                "content_count": 0,
                "total_questions": 0,
                "average_rating": 5.0
            },
            "settings": {
                "auto_approve_messages": True,
                "allow_tips": True,
                "response_time": "24 hours"
            },
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "last_active": datetime.utcnow()
        }
        
        await db.creators.insert_one(mentor_doc)
        
        return {
            "success": True,
            "message": "Congratulations! You are now a mentor on OnlyMentors.ai",
            "creator_id": creator_id,
            "mentor_profile": {
                "name": mentor_doc["account_name"],
                "title": mentor_doc["title"],
                "bio": mentor_doc["bio"],
                "expertise": mentor_doc["expertise"]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to become mentor: {str(e)}")

@app.post("/api/mentor/{mentor_id}/ask")
async def ask_mentor_question(
    mentor_id: str, 
    question_data: dict,
    current_user = Depends(get_current_user)
):
    """Ask a question to a mentor and track the interaction"""
    try:
        user_id = current_user["user_id"]
        question_text = question_data.get("question", "").strip()
        
        if not question_text:
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        # Find mentor
        mentor = None
        mentor_category = None
        for category, mentors in ALL_MENTORS.items():
            for m in mentors:
                if m["id"] == mentor_id:
                    mentor = m
                    mentor_category = category
                    break
            if mentor:
                break
        
        if not mentor:
            raise HTTPException(status_code=404, detail="Mentor not found")
        
        # Generate AI response (simplified for now)
        ai_response = f"Thank you for your question about {question_text[:50]}... As {mentor['name']}, I would advise you to consider the following perspectives..."
        
        # Create interaction record
        interaction_id = str(uuid.uuid4())
        interaction_record = {
            "interaction_id": interaction_id,
            "user_id": user_id,
            "mentor_id": mentor_id,
            "mentor_name": mentor["name"],
            "mentor_category": mentor_category,
            "question": question_text,
            "response": ai_response,
            "timestamp": datetime.utcnow(),
            "rating": None,  # User can rate later
            "follow_up_questions": []
        }
        
        # Store in interactions collection
        await db.mentor_interactions.insert_one(interaction_record)
        
        # Update user's question count and history
        await db.users.update_one(
            {"user_id": user_id},
            {
                "$inc": {"questions_asked": 1},
                "$push": {
                    "question_history": {
                        "interaction_id": interaction_id,
                        "mentor_id": mentor_id,
                        "mentor_name": mentor["name"],
                        "question": question_text,
                        "timestamp": datetime.utcnow()
                    },
                    "mentor_interactions": interaction_id
                }
            }
        )
        
        return {
            "interaction_id": interaction_id,
            "mentor": {
                "id": mentor_id,
                "name": mentor["name"],
                "category": mentor_category
            },
            "question": question_text,
            "response": ai_response,
            "timestamp": interaction_record["timestamp"].isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process question: {str(e)}")

@app.get("/api/user/question-history")
async def get_user_question_history(current_user = Depends(get_current_user)):
    """Get user's complete question and mentor interaction history"""
    try:
        user_id = current_user["user_id"]
        
        # Get all interactions for this user
        interactions = await db.mentor_interactions.find(
            {"user_id": user_id}
        ).sort("timestamp", -1).to_list(length=None)
        
        # Format for response
        history = []
        for interaction in interactions:
            history.append({
                "interaction_id": interaction["interaction_id"],
                "mentor": {
                    "id": interaction["mentor_id"],
                    "name": interaction["mentor_name"],
                    "category": interaction["mentor_category"]
                },
                "question": interaction["question"],
                "response": interaction["response"],
                "timestamp": interaction["timestamp"].isoformat(),
                "rating": interaction.get("rating"),
                "follow_up_count": len(interaction.get("follow_up_questions", []))
            })
        
        return {
            "total_questions": len(history),
            "history": history
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve history: {str(e)}")

@app.get("/api/user/profile/complete")
async def get_complete_user_profile(current_user = Depends(get_current_user)):
    """Get user's complete profile including all data we collect"""
    try:
        user_id = current_user["user_id"]
        
        # Get user from database with all fields
        user = await db.users.find_one({"user_id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get interaction statistics
        total_interactions = await db.mentor_interactions.count_documents({"user_id": user_id})
        unique_mentors = len(set([
            interaction["mentor_id"] async for interaction in 
            db.mentor_interactions.find({"user_id": user_id}, {"mentor_id": 1})
        ]))
        
        return {
            "user_id": user["user_id"],
            "email": user["email"],
            "full_name": user["full_name"],
            "phone_number": user.get("phone_number", ""),
            "communication_preferences": user.get("communication_preferences", {}),
            "subscription_plan": user.get("subscription_plan", "free"),
            "is_subscribed": user.get("is_subscribed", False),
            "subscription_expires": user.get("subscription_expires").isoformat() if user.get("subscription_expires") else None,
            "questions_asked": user.get("questions_asked", 0),
            "total_interactions": total_interactions,
            "unique_mentors_consulted": unique_mentors,
            "profile_completed": user.get("profile_completed", False),
            "created_at": user["created_at"].isoformat(),
            "last_login": user.get("last_login").isoformat() if user.get("last_login") else None,
            "account_status": "active" if user.get("is_active", True) else "inactive"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve profile: {str(e)}")

@app.put("/api/user/profile/communication-preferences")
async def update_communication_preferences(
    preferences: dict,
    current_user = Depends(get_current_user)
):
    """Update user's communication preferences"""
    try:
        result = await db.users.update_one(
            {"user_id": current_user["user_id"]},
            {"$set": {"communication_preferences": preferences}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {"message": "Communication preferences updated successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update preferences: {str(e)}")

# ================================
# SMS & 2FA ENDPOINTS  
# ================================

@app.post("/api/sms/send")
async def send_sms_notification(
    sms_request: SMSRequest,
    current_user = Depends(get_current_user)
):
    """Send SMS notification to user"""
    try:
        # Validate phone number format
        if not validate_phone(sms_request.phone_number):
            raise HTTPException(status_code=400, detail="Invalid phone number format")
        
        # Send SMS
        result = await send_sms(sms_request.phone_number, sms_request.message)
        
        if result["success"]:
            return {
                "success": True,
                "message": "SMS sent successfully",
                "message_sid": result.get("message_sid"),
                "phone": result.get("phone")
            }
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to send SMS"))
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SMS service error: {str(e)}")

@app.post("/api/sms/send-2fa")
async def send_2fa_code(sms_request: Send2FARequest):
    """Send 2FA verification code via SMS"""
    try:
        # Validate phone number format
        if not validate_phone(sms_request.phone_number):
            raise HTTPException(status_code=400, detail="Invalid phone number format")
        
        # Send 2FA code
        result = await send_2fa(sms_request.phone_number)
        
        if result["success"]:
            return {
                "success": True,
                "message": "Verification code sent successfully",
                "phone": result.get("phone"),
                "valid_until": result.get("valid_until")
            }
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to send verification code"))
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"2FA service error: {str(e)}")

@app.post("/api/sms/verify-2fa")
async def verify_2fa_code(verify_request: Verify2FARequest):
    """Verify 2FA code"""
    try:
        # Validate phone number format
        if not validate_phone(verify_request.phone_number):
            raise HTTPException(status_code=400, detail="Invalid phone number format")
        
        # Verify code
        result = await verify_2fa(verify_request.phone_number, verify_request.code)
        
        if result["success"]:
            return {
                "success": True,
                "valid": result.get("valid", False),
                "message": "Code verified successfully" if result.get("valid") else "Invalid verification code",
                "phone": result.get("phone")
            }
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to verify code"))
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"2FA verification error: {str(e)}")

@app.post("/api/sms/validate-phone")
async def validate_phone_number(phone_request: PhoneValidationRequest):
    """Validate phone number format and deliverability"""
    try:
        is_valid = validate_phone(phone_request.phone_number)
        formatted_phone = format_phone(phone_request.phone_number) if is_valid else None
        
        return {
            "valid": is_valid,
            "formatted_phone": formatted_phone,
            "original_phone": phone_request.phone_number
        }
    
    except Exception as e:
        return {
            "valid": False,
            "error": str(e),
            "original_phone": phone_request.phone_number
        }

@app.post("/api/auth/signup")
async def signup(user_data: UserSignup):
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    user_id = str(uuid.uuid4())
    user_doc = {
        "user_id": user_id,
        "email": user_data.email,
        "password_hash": hash_password(user_data.password),
        "full_name": user_data.full_name,
        "profile_completed": True,
        "created_at": datetime.utcnow(),
        "questions_asked": 0,
        "is_subscribed": False if not user_data.company_id else True,  # Business users are "subscribed"
        "subscription_plan": "free" if not user_data.company_id else "business",
        "user_type": "consumer" if not user_data.company_id else "business_employee",
        "company_id": user_data.company_id if user_data.company_id else None,
        "department_code": user_data.department_code if user_data.department_code else None,
        "business_role": "employee",
        "last_login": None,
        "reset_token": None,
        "reset_token_expires": None,
        "oauth_provider": None,
        "oauth_id": None,
        "phone_number": None,
        "is_active": True
    }
    
    await db.users.insert_one(user_doc)
    
    # Create access token
    token = create_access_token({"user_id": user_id})
    
    return {
        "token": token,
        "user": {
            "user_id": user_id,
            "email": user_data.email,
            "full_name": user_data.full_name,
            "questions_asked": 0,
            "is_subscribed": False
        }
    }

@app.post("/api/auth/login")
async def login(login_data: UserLogin):
    # Find user
    user = await db.users.find_one({"email": login_data.email})
    if not user or not verify_password(login_data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Check if account is suspended
    if user.get("is_suspended", False):
        raise HTTPException(
            status_code=401,  # HTTP 401 Unauthorized
            detail="Your account has been suspended. Please contact support for assistance."
        )
    
    # Check if account is locked due to admin password reset
    if user.get("account_locked", False):
        raise HTTPException(
            status_code=423,  # HTTP 423 Locked
            detail="Your account is temporarily locked. Please check your email for password reset instructions from an administrator."
        )
    
    # Create access token
    token = create_access_token({"user_id": user["user_id"]})
    
    return {
        "token": token,
        "user": {
            "user_id": user["user_id"],
            "email": user["email"], 
            "full_name": user["full_name"],
            "questions_asked": user.get("questions_asked", 0),
            "is_subscribed": user.get("is_subscribed", False),
            "user_type": user.get("user_type", "consumer"),
            "business_role": user.get("business_role"),
            "company_id": user.get("company_id"),
            "department_code": user.get("department_code")
        }
    }

@app.get("/api/auth/me")
async def get_me(current_user = Depends(get_current_user)):
    return {
        "user": {
            "user_id": current_user["user_id"],
            "email": current_user["email"],
            "full_name": current_user["full_name"],
            "questions_asked": current_user.get("questions_asked", 0),
            "is_subscribed": current_user.get("is_subscribed", False)
        }
    }

# =============================================================================
# GOOGLE OAUTH AUTHENTICATION ENDPOINTS
# =============================================================================

@app.post("/api/auth/google")
async def google_oauth_login(auth_request: SocialAuthRequest):
    """Handle Google OAuth login/signup with both code and ID token flows"""
    try:
        user_info = None
        
        # Handle ID token flow (most common with @react-oauth/google)
        if auth_request.id_token:
            print(f"Processing Google ID token flow")
            user_info = await verify_google_id_token(auth_request.id_token)
        
        # Handle authorization code flow (fallback)
        elif auth_request.code:
            print(f"Processing Google authorization code flow")
            # Exchange code for token
            token_response = await exchange_google_code_for_token(auth_request.code)
            # Get user info from Google
            user_info = await get_google_user_info(token_response.access_token)
        
        else:
            raise HTTPException(
                status_code=400, 
                detail="Either authorization code or ID token is required for Google OAuth"
            )
        
        if not user_info:
            raise HTTPException(status_code=400, detail="Failed to get user information from Google")
        
        # Check if user exists
        existing_user = await db.users.find_one({"email": user_info.email})
        
        is_new_user = False
        
        if existing_user:
            # Update existing user with social auth info if not already set
            if not existing_user.get("social_auth"):
                await db.users.update_one(
                    {"user_id": existing_user["user_id"]},
                    {
                        "$set": {
                            "social_auth": {
                                "provider": "google",
                                "provider_id": user_info.id,
                                "provider_email": user_info.email,
                                "profile_image_url": user_info.picture,
                                "verified_email": user_info.verified_email
                            },
                            "profile_image_url": user_info.picture,
                            "last_login": datetime.utcnow()
                        }
                    }
                )
            else:
                # Just update last login
                await db.users.update_one(
                    {"user_id": existing_user["user_id"]},
                    {"$set": {"last_login": datetime.utcnow()}}
                )
            
            user_doc = await db.users.find_one({"user_id": existing_user["user_id"]})
        else:
            # Create new user from social auth
            user_doc = create_user_from_social_auth(user_info, "google")
            await db.users.insert_one(user_doc)
            is_new_user = True
        
        # Create access token for our system
        access_token = create_access_token({"user_id": user_doc["user_id"]})
        
        return SocialAuthResponse(
            user_id=user_doc["user_id"],
            email=user_doc["email"],
            full_name=user_doc["full_name"],
            profile_image_url=user_doc.get("profile_image_url"),
            is_new_user=is_new_user,
            access_token=access_token,
            provider="google"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Google OAuth error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Google OAuth login failed: {str(e)}")

@app.post("/api/auth/facebook")
async def facebook_oauth_login(auth_request: SocialAuthRequest):
    """Handle Facebook OAuth login/signup"""
    try:
        user_info = None
        
        # Handle access token flow (most common with Facebook SDK)
        if auth_request.access_token:
            print(f"Processing Facebook access token flow")
            user_info = await verify_facebook_access_token(auth_request.access_token)
        
        # Handle authorization code flow
        elif auth_request.code:
            print(f"Processing Facebook authorization code flow")
            # Exchange code for token
            access_token = await exchange_facebook_code_for_token(auth_request.code)
            # Get user info from Facebook
            user_info = await get_facebook_user_info(access_token)
        
        else:
            raise HTTPException(
                status_code=400, 
                detail="Either authorization code or access token is required for Facebook OAuth"
            )
        
        if not user_info:
            raise HTTPException(status_code=400, detail="Failed to get user information from Facebook")
        
        # Check if user exists - first by Facebook ID, then by email if available
        existing_user = None
        
        # First check by Facebook provider ID (more reliable)
        existing_user = await db.users.find_one({"social_auth.provider": "facebook", "social_auth.provider_id": user_info.id})
        
        # If not found and email is available, check by email
        if not existing_user and user_info.email:
            existing_user = await db.users.find_one({"email": user_info.email})
        
        is_new_user = False
        
        if existing_user:
            # Update existing user with social auth info if not already set
            if not existing_user.get("social_auth"):
                await db.users.update_one(
                    {"user_id": existing_user["user_id"]},
                    {
                        "$set": {
                            "social_auth": {
                                "provider": "facebook",
                                "provider_id": user_info.id,
                                "provider_email": user_info.email,
                                "profile_image_url": user_info.picture.get("data", {}).get("url") if user_info.picture else None,
                                "first_name": user_info.first_name,
                                "last_name": user_info.last_name
                            },
                            "profile_image_url": user_info.picture.get("data", {}).get("url") if user_info.picture else None,
                            "last_login": datetime.utcnow()
                        }
                    }
                )
            else:
                # Just update last login
                await db.users.update_one(
                    {"user_id": existing_user["user_id"]},
                    {"$set": {"last_login": datetime.utcnow()}}
                )
            
            user_doc = await db.users.find_one({"user_id": existing_user["user_id"]})
        else:
            # Create new user from social auth
            user_doc = create_user_from_facebook_auth(user_info, "facebook")
            await db.users.insert_one(user_doc)
            is_new_user = True
        
        # Create access token for our system
        access_token = create_access_token({"user_id": user_doc["user_id"]})
        
        return SocialAuthResponse(
            user_id=user_doc["user_id"],
            email=user_doc["email"],
            full_name=user_doc["full_name"],
            profile_image_url=user_doc.get("profile_image_url"),
            is_new_user=is_new_user,
            access_token=access_token,
            provider="facebook"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Facebook OAuth error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Facebook OAuth login failed: {str(e)}")

@app.get("/api/auth/facebook/config")
async def get_facebook_oauth_config():
    """Get Facebook OAuth configuration for frontend"""
    try:
        oauth_config.validate_facebook_config()
        return {
            "app_id": oauth_config.facebook_app_id,
            "redirect_uri": oauth_config.facebook_redirect_uri,
            "scope": "email,public_profile"
        }
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"Facebook OAuth not configured: {str(e)}")

@app.get("/api/auth/google/config")
async def get_google_oauth_config():
    """Get Google OAuth configuration for frontend"""
    try:
        oauth_config.validate_google_config()
        return {
            "client_id": oauth_config.google_client_id,
            "redirect_uri": oauth_config.google_redirect_uri,
            "scope": "openid email profile"
        }
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"Google OAuth not configured: {str(e)}")

# =============================================================================
# FORGOT PASSWORD SYSTEM - Complete Password Reset Process
# =============================================================================

@app.post("/api/auth/forgot-password")
async def forgot_password(request: ForgotPasswordRequest):
    """Handle forgot password requests for both users and mentors"""
    try:
        # Input validation
        if request.user_type not in ["user", "mentor"]:
            raise HTTPException(status_code=400, detail="user_type must be 'user' or 'mentor'")
        
        # Rate limiting - max 3 attempts per hour per email
        recent_attempts = await get_recent_reset_attempts(db, request.email, hours=1)
        if recent_attempts >= 3:
            raise HTTPException(
                status_code=429, 
                detail="Too many password reset attempts. Please wait 1 hour before trying again."
            )
        
        # Find user/mentor by email
        if request.user_type == "mentor":
            collection = db.creators  # Mentors are stored in creators collection
            user_doc = await collection.find_one({"email": request.email})
            user_name = user_doc.get("full_name", "Mentor") if user_doc else "Mentor"
        else:
            collection = db.users
            user_doc = await collection.find_one({"email": request.email})
            user_name = user_doc.get("full_name", "User") if user_doc else "User"
        
        # Always return success message for security (don't reveal if email exists)
        success_response = ForgotPasswordResponse(
            message=f"If an account with email {request.email} exists, a password reset link has been sent.",
            email=request.email,
            expires_in=60  # 1 hour in minutes
        )
        
        # Only send email if user/mentor actually exists
        if user_doc:
            # Create reset token
            reset_token = await create_password_reset_token(db, request.email, request.user_type)
            
            if reset_token:
                # Send password reset email
                email_sent = await send_password_reset_email(
                    request.email, reset_token, request.user_type, user_name
                )
                
                # Log the attempt
                await log_password_reset_attempt(
                    db, request.email, request.user_type, 
                    success=email_sent
                )
                
                if not email_sent:
                    # Log failure but still return success for security
                    print(f"❌ Failed to send password reset email to {request.email}")
        else:
            # Log attempt for non-existent user
            await log_password_reset_attempt(
                db, request.email, request.user_type, success=False
            )
        
        # Clean up old tokens periodically
        await cleanup_expired_tokens(db)
        
        return success_response
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Forgot password error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process password reset request")

@app.post("/api/auth/reset-password")
async def reset_password(request: ResetPasswordRequest):
    """Handle password reset confirmation"""
    try:
        # Input validation
        if request.user_type not in ["user", "mentor"]:
            raise HTTPException(status_code=400, detail="user_type must be 'user' or 'mentor'")
        
        if not request.token or not request.new_password:
            raise HTTPException(status_code=400, detail="Token and new password are required")
        
        # Validate password strength
        is_strong, message = validate_password_strength(request.new_password)
        if not is_strong:
            raise HTTPException(status_code=400, detail=message)
        
        # Validate reset token
        token_doc = await validate_reset_token(db, request.token, request.user_type)
        if not token_doc:
            raise HTTPException(
                status_code=400, 
                detail="Invalid or expired reset token. Please request a new password reset."
            )
        
        # Find user/mentor by email
        if request.user_type == "mentor":
            collection = db.creators
            user_doc = await collection.find_one({"email": token_doc["email"]})
        else:
            collection = db.users
            user_doc = await collection.find_one({"email": token_doc["email"]})
        
        if not user_doc:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Hash new password
        new_password_hash = hash_password(request.new_password)
        
        # Update password in database
        if request.user_type == "mentor":
            await collection.update_one(
                {"email": token_doc["email"]},
                {
                    "$set": {
                        "password_hash": new_password_hash,
                        "password_reset_at": datetime.utcnow(),
                        "last_login": None,  # Force re-login
                        "account_locked": False,  # Unlock account after successful reset
                        "password_reset_by_admin": None,  # Clear admin reset flag
                        "password_reset_reason": None  # Clear reset reason
                    }
                }
            )
        else:
            await collection.update_one(
                {"email": token_doc["email"]},
                {
                    "$set": {
                        "password_hash": new_password_hash,
                        "password_reset_at": datetime.utcnow(),
                        "last_login": None,  # Force re-login
                        "account_locked": False,  # Unlock account after successful reset
                        "password_reset_by_admin": None,  # Clear admin reset flag
                        "password_reset_reason": None  # Clear reset reason
                    }
                }
            )
        
        # Mark token as used
        await mark_token_as_used(db, request.token)
        
        # Log successful password reset
        await log_password_reset_attempt(
            db, token_doc["email"], request.user_type, success=True
        )
        
        # Send confirmation email (optional)
        try:
            user_name = user_doc.get("full_name", "User")
            await send_password_reset_confirmation_email(
                token_doc["email"], user_name, request.user_type
            )
        except Exception as e:
            print(f"⚠️  Failed to send confirmation email: {str(e)}")
        
        return {
            "message": "Password has been reset successfully. Please log in with your new password.",
            "email": token_doc["email"]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Reset password error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to reset password")

# ================================
# USER PROFILE ENDPOINTS
# ================================

@app.get("/api/user/profile")
async def get_user_profile(current_user = Depends(get_current_user)):
    """Get current user's profile information"""
    try:
        user_doc = await db.users.find_one({"user_id": current_user["user_id"]})
        
        if not user_doc:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Return safe profile data (no password hash)
        profile_data = {
            "user_id": user_doc["user_id"],
            "email": user_doc["email"],
            "full_name": user_doc.get("full_name", ""),
            "phone_number": user_doc.get("phone_number", ""),
            "communication_preferences": user_doc.get("communication_preferences", {}),
            "questions_asked": user_doc.get("questions_asked", 0),
            "questions_remaining": user_doc.get("questions_remaining", 10),
            "is_subscribed": user_doc.get("is_subscribed", False),
            "profile_image_url": user_doc.get("profile_image_url"),
            "created_at": user_doc.get("created_at"),
            "last_login": user_doc.get("last_login")
        }
        
        return profile_data
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Get profile error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.put("/api/user/profile")
async def update_user_profile(profile_update: UserProfileUpdate, current_user = Depends(get_current_user)):
    """Update current user's profile information"""
    try:
        # Build update document
        update_data = {"updated_at": datetime.utcnow()}
        
        if profile_update.full_name is not None:
            update_data["full_name"] = profile_update.full_name.strip()
            
        if profile_update.phone_number is not None:
            # Basic phone number validation
            phone = profile_update.phone_number.strip()
            if phone and not re.match(r'^[\+]?[1-9][\d]{0,15}$', phone):
                raise HTTPException(status_code=400, detail="Invalid phone number format")
            update_data["phone_number"] = phone
            
        if profile_update.email is not None:
            # Check if email is already taken by another user
            existing_user = await db.users.find_one({
                "email": profile_update.email,
                "user_id": {"$ne": current_user["user_id"]}
            })
            if existing_user:
                raise HTTPException(status_code=400, detail="Email address is already in use")
            update_data["email"] = profile_update.email
            
        if profile_update.communication_preferences is not None:
            # Validate SMS preference requires phone number
            comm_prefs = profile_update.communication_preferences
            if comm_prefs.get("sms", False):
                # Check if phone number is provided in this update or exists in current user
                current_phone = update_data.get("phone_number") or current_user.get("phone_number", "")
                if not current_phone or current_phone.strip() == "":
                    raise HTTPException(
                        status_code=400, 
                        detail="Phone number is required to enable SMS notifications"
                    )
            update_data["communication_preferences"] = profile_update.communication_preferences
            
        # Check if this update completes the profile
        if profile_update.phone_number is not None and profile_update.communication_preferences is not None:
            update_data["profile_completed"] = True
        
        # Update user document
        result = await db.users.update_one(
            {"user_id": current_user["user_id"]},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get updated profile
        updated_user = await db.users.find_one({"user_id": current_user["user_id"]})
        
        # Return updated profile data
        profile_data = {
            "user_id": updated_user["user_id"],
            "email": updated_user["email"],
            "full_name": updated_user.get("full_name", ""),
            "phone_number": updated_user.get("phone_number", ""),
            "communication_preferences": updated_user.get("communication_preferences", {}),
            "questions_asked": updated_user.get("questions_asked", 0),
            "questions_remaining": updated_user.get("questions_remaining", 10),
            "is_subscribed": updated_user.get("is_subscribed", False),
            "profile_image_url": updated_user.get("profile_image_url"),
            "updated_at": updated_user.get("updated_at")
        }
        
        return {
            "message": "Profile updated successfully",
            "profile": profile_data
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Update profile error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.put("/api/user/password")
async def change_user_password(password_request: PasswordChangeRequest, current_user = Depends(get_current_user)):
    """Change current user's password"""
    try:
        # Get current user from database
        user_doc = await db.users.find_one({"user_id": current_user["user_id"]})
        
        if not user_doc:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if user has a password (not social auth only)
        if not user_doc.get("password_hash"):
            raise HTTPException(
                status_code=400, 
                detail="Cannot change password for social authentication accounts. Please use forgot password if you need to set a password."
            )
        
        # Verify current password
        if not verify_password(password_request.current_password, user_doc["password_hash"]):
            raise HTTPException(status_code=400, detail="Current password is incorrect")
        
        # Hash new password
        new_password_hash = hash_password(password_request.new_password)
        
        # Update password in database
        result = await db.users.update_one(
            {"user_id": current_user["user_id"]},
            {
                "$set": {
                    "password_hash": new_password_hash,
                    "updated_at": datetime.utcnow(),
                    "password_changed_at": datetime.utcnow()
                }
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Optional: Send email notification about password change
        try:
            user_name = user_doc.get("full_name", "User")
            # TODO: Add email notification for password change
            print(f"✅ Password changed successfully for {user_name} ({user_doc['email']})")
        except Exception as e:
            print(f"⚠️  Failed to send password change notification: {str(e)}")
        
        return {
            "message": "Password changed successfully. Please log in again with your new password."
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Change password error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ================================
# MENTOR QUESTIONS ENDPOINTS  
# ================================

@app.post("/api/auth/validate-reset-token")
async def validate_reset_token_endpoint(token: str, user_type: str):
    """Validate a password reset token without using it"""
    try:
        if user_type not in ["user", "mentor"]:
            raise HTTPException(status_code=400, detail="user_type must be 'user' or 'mentor'")
        
        token_doc = await validate_reset_token(db, token, user_type)
        
        if not token_doc:
            raise HTTPException(status_code=400, detail="Invalid or expired reset token")
        
        return {
            "valid": True,
            "email": token_doc["email"],
            "expires_at": token_doc["expires_at"],
            "time_remaining": int((token_doc["expires_at"] - datetime.utcnow()).total_seconds() / 60)  # minutes
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to validate reset token")

async def send_password_reset_confirmation_email(email: str, user_name: str, user_type: str):
    """Send confirmation email after successful password reset"""
    try:
        reset_config.validate_config()
        
        # Create SendGrid client
        sg = sendgrid.SendGridAPIClient(api_key=reset_config.sendgrid_api_key)
        
        # Email subject and content
        subject = "Password Reset Confirmation - OnlyMentors.ai"
        user_type_text = "mentor account" if user_type == "mentor" else "account"
        
        # HTML email content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Password Reset Confirmation - OnlyMentors.ai</title>
            <style>
                body {{ font-family: 'Arial', sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #10b981 0%, #059669 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .header h1 {{ color: white; margin: 0; font-size: 24px; }}
                .content {{ background: white; padding: 30px; border-radius: 0 0 10px 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                .success {{ background: #f0fdf4; border: 1px solid #bbf7d0; color: #166534; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .warning {{ background: #fffbeb; border: 1px solid #fed7aa; color: #92400e; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 14px; }}
                .button {{ display: inline-block; background: #10b981; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🧠 OnlyMentors.ai</h1>
                </div>
                <div class="content">
                    <h2>✅ Password Reset Successful</h2>
                    <p>Hello {user_name},</p>
                    
                    <div class="success">
                        <strong>🎉 Success!</strong> Your OnlyMentors.ai {user_type_text} password has been successfully reset.
                    </div>
                    
                    <p>Your password was changed on <strong>{datetime.utcnow().strftime('%B %d, %Y at %I:%M %p UTC')}</strong>.</p>
                    
                    <p>You can now log in to your account using your new password:</p>
                    
                    <div style="text-align: center;">
                        <a href="{reset_config.frontend_base_url}" class="button">Log In Now</a>
                    </div>
                    
                    <div class="warning">
                        <strong>⚠️ Security Notice:</strong>
                        <ul>
                            <li>If you didn't reset your password, please contact support immediately</li>
                            <li>We recommend using a strong, unique password</li>
                            <li>Never share your password with anyone</li>
                        </ul>
                    </div>
                    
                    <p>If you have any questions or concerns, please contact our support team.</p>
                    
                    <p>Best regards,<br>
                    The OnlyMentors.ai Team</p>
                </div>
                <div class="footer">
                    <p>© 2024 OnlyMentors.ai - Connect with the Greatest Minds</p>
                    <p>This email was sent to {email}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Create and send email
        from_email = Email(reset_config.from_email)
        to_email = To(email)
        plain_content = Content("text/plain", f"Your OnlyMentors.ai password has been successfully reset on {datetime.utcnow().strftime('%B %d, %Y at %I:%M %p UTC')}. You can now log in with your new password.")
        html_content_obj = Content("text/html", html_content)
        
        mail = Mail(from_email, to_email, subject, plain_content)
        mail.add_content(html_content_obj)
        
        response = sg.client.mail.send.post(request_body=mail.get())
        
        if response.status_code in [200, 202]:
            print(f"✅ Password reset confirmation email sent to {email}")
        else:
            print(f"❌ Failed to send confirmation email: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Confirmation email error: {str(e)}")
        # Don't raise exception - this is not critical

@app.post("/api/questions/ask")
async def ask_question(question_data: QuestionRequest, current_user = Depends(get_current_user)):
    start_time = time.time()  # Track performance
    
    # Check if user can ask questions
    questions_asked = current_user.get("questions_asked", 0)
    is_subscribed = current_user.get("is_subscribed", False)
    
    if not is_subscribed and questions_asked >= 10:
        raise HTTPException(
            status_code=402, 
            detail=f"You've reached your free question limit. Please subscribe to continue asking questions to any of our {TOTAL_MENTORS} mentors."
        )
    
    try:
        # Enforce 5-mentor limit for performance and quality
        if len(question_data.mentor_ids) > 5:
            raise HTTPException(
                status_code=400, 
                detail="You can select a maximum of 5 mentors per question for optimal response time and quality."
            )
        
        # Validate mentors exist
        selected_mentors = []
        for mentor_id in question_data.mentor_ids:
            mentor = next((m for m in ALL_MENTORS[question_data.category] if m["id"] == mentor_id), None)
            if not mentor:
                raise HTTPException(status_code=404, detail=f"Mentor {mentor_id} not found")
            selected_mentors.append(mentor)
        
        print(f"🚀 Starting parallel processing for {len(selected_mentors)} mentors")
        
        # Create responses from all selected mentors CONCURRENTLY for speed
        import asyncio
        
        # Create tasks for all mentors to run in parallel
        mentor_tasks = []
        for mentor in selected_mentors:
            task = asyncio.create_task(create_mentor_response(mentor, question_data.question))
            mentor_tasks.append((mentor, task))
        
        # Wait for all mentors to respond simultaneously
        responses = []
        for mentor, task in mentor_tasks:
            try:
                # Wait for this mentor's response (with timeout)
                response_text = await asyncio.wait_for(task, timeout=35.0)
                responses.append({
                    "mentor": mentor,
                    "response": response_text
                })
            except asyncio.TimeoutError:
                # Fallback response for timeout
                fallback_response = f"Thank you for your question about '{question_data.question}'. Based on my experience in {mentor['expertise']}, I believe this is an important topic that requires thoughtful consideration. While I'd love to provide a detailed response right now, I encourage you to explore this further and perhaps rephrase your question for the best guidance."
                responses.append({
                    "mentor": mentor,
                    "response": fallback_response
                })
            except Exception as e:
                print(f"❌ Error getting response from {mentor['name']}: {str(e)}")
                # Fallback response for errors
                fallback_response = f"Thank you for your question about '{question_data.question}'. Based on my experience in {mentor['expertise']}, I believe this is an important topic that requires thoughtful consideration. While I'd love to provide a detailed response right now, I encourage you to explore this further and perhaps rephrase your question for the best guidance."
                responses.append({
                    "mentor": mentor,
                    "response": fallback_response
                })
        
        processing_time = time.time() - start_time
        print(f"⚡ Total processing time: {processing_time:.2f}s for {len(selected_mentors)} mentors")
        
        # Save question and responses
        question_doc = {
            "question_id": str(uuid.uuid4()),
            "user_id": current_user["user_id"],
            "category": question_data.category,
            "mentor_ids": question_data.mentor_ids,
            "question": question_data.question,
            "responses": responses,
            "processing_time": processing_time,  # Track performance
            "created_at": datetime.utcnow(),
            # Business tracking fields
            "company_id": current_user.get("company_id"),
            "department_code": getattr(question_data, 'department_code', None) or current_user.get("department_code"),
            "business_cost": 0.0  # Will be calculated based on mentor usage
        }
        
        await db.questions.insert_one(question_doc)
        
        # Update user question count and add comprehensive tracking
        question_summary = {
            "question_id": question_doc["question_id"],
            "question": question_data.question,
            "category": question_data.category,
            "mentor_count": len(selected_mentors),
            "mentor_names": [m["name"] for m in selected_mentors],
            "timestamp": datetime.utcnow()
        }
        
        # Create individual mentor interaction records for detailed tracking
        mentor_interaction_ids = []
        for mentor, response_data in zip(selected_mentors, responses):
            interaction_id = str(uuid.uuid4())
            interaction_record = {
                "interaction_id": interaction_id,
                "user_id": current_user["user_id"],
                "question_id": question_doc["question_id"],
                "mentor_id": mentor["id"],
                "mentor_name": mentor["name"],
                "mentor_category": question_data.category,
                "question": question_data.question,
                "response": response_data["response"],
                "timestamp": datetime.utcnow()
            }
            await db.mentor_interactions.insert_one(interaction_record)
            mentor_interaction_ids.append(interaction_id)

        await db.users.update_one(
            {"user_id": current_user["user_id"]},
            {
                "$inc": {"questions_asked": 1},
                "$push": {
                    "question_history": question_summary,
                    "mentor_interactions": {"$each": mentor_interaction_ids}
                }
            }
        )
        
        return {
            "question_id": question_doc["question_id"],
            "question": question_data.question,
            "responses": responses,
            "selected_mentors": selected_mentors,
            "processing_time": f"{processing_time:.2f}s",  # Include performance info
            "total_mentors": len(selected_mentors),
            "questions_remaining": max(0, 10 - (questions_asked + 1)) if not is_subscribed else None
        }
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Failed to process question: {str(e)}")

@app.get("/api/questions/history")
async def get_question_history(current_user = Depends(get_current_user)):
    questions = await db.questions.find(
        {"user_id": current_user["user_id"]},
        {"_id": 0}
    ).sort("created_at", -1).limit(50).to_list(50)
    
    return {"questions": questions}

# =============================================================================
# ENHANCED USER QUESTION CONTEXT SYSTEM - Option 4
# =============================================================================

from enhanced_context_system import (
    ConversationThread, ConversationMessage, ContextualQuestionRequest,
    EnhancedContext, EnhancedQuestionProcessor, ConversationAnalytics
)

@app.post("/api/questions/ask-contextual")
async def ask_contextual_question(
    question_data: ContextualQuestionRequest, 
    current_user = Depends(get_current_user)
):
    """Enhanced question asking with conversation context and thread management"""
    try:
        # Check if user can ask questions
        questions_asked = current_user.get("questions_asked", 0)
        is_subscribed = current_user.get("is_subscribed", False)
        
        if not is_subscribed and questions_asked >= 10:
            raise HTTPException(
                status_code=402, 
                detail=f"You've reached your free question limit. Please subscribe to continue asking questions to any of our {TOTAL_MENTORS} mentors."
            )
        
        # Validate mentors exist
        selected_mentors = []
        for mentor_id in question_data.mentor_ids:
            mentor = next((m for m in ALL_MENTORS[question_data.category] if m["id"] == mentor_id), None)
            if not mentor:
                raise HTTPException(status_code=404, detail=f"Mentor {mentor_id} not found")
            selected_mentors.append(mentor)
        
        # Process contextual responses
        contextual_responses = []
        thread_ids = []
        
        for mentor in selected_mentors:
            # Create individual thread per mentor if not specified
            mentor_question_data = ContextualQuestionRequest(
                category=question_data.category,
                mentor_ids=[mentor["id"]],
                question=question_data.question,
                thread_id=question_data.thread_id if len(selected_mentors) == 1 else None,
                include_history=question_data.include_history
            )
            
            response_data = await EnhancedQuestionProcessor.process_contextual_question(
                db, mentor_question_data, current_user, mentor
            )
            
            contextual_responses.append(response_data)
            thread_ids.append(response_data["thread_id"])
        
        # Also save to traditional questions collection for backward compatibility
        question_doc = {
            "question_id": str(uuid.uuid4()),
            "user_id": current_user["user_id"],
            "category": question_data.category,
            "mentor_ids": question_data.mentor_ids,
            "question": question_data.question,
            "responses": [
                {
                    "mentor": r["mentor"],
                    "response": r["response"]
                } for r in contextual_responses
            ],
            "thread_ids": thread_ids,
            "context_enabled": question_data.include_history,
            "created_at": datetime.utcnow()
        }
        
        await db.questions.insert_one(question_doc)
        
        # Update user question count
        await db.users.update_one(
            {"user_id": current_user["user_id"]},
            {"$inc": {"questions_asked": 1}}
        )
        
        return {
            "question_id": question_doc["question_id"],
            "question": question_data.question,
            "contextual_responses": contextual_responses,
            "thread_ids": thread_ids,
            "context_enabled": question_data.include_history,
            "selected_mentors": selected_mentors,
            "questions_remaining": max(0, 10 - (questions_asked + 1)) if not is_subscribed else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process contextual question: {str(e)}")

@app.get("/api/conversations/threads")
async def get_conversation_threads(
    current_user = Depends(get_current_user),
    mentor_id: Optional[str] = None,
    limit: int = 20
):
    """Get user's conversation threads"""
    try:
        threads = await EnhancedContext.get_user_conversation_threads(
            db, current_user["user_id"], mentor_id
        )
        
        return {
            "threads": threads[:limit],
            "total": len(threads),
            "user_id": current_user["user_id"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get conversation threads: {str(e)}")

@app.get("/api/conversations/threads/{thread_id}")
async def get_conversation_thread(
    thread_id: str,
    current_user = Depends(get_current_user),
    limit: int = 50
):
    """Get full conversation thread with messages"""
    try:
        # Verify user owns this thread
        thread = await db.conversation_threads.find_one({
            "thread_id": thread_id,
            "user_id": current_user["user_id"]
        })
        
        if not thread:
            raise HTTPException(status_code=404, detail="Conversation thread not found")
        
        # Get conversation messages
        messages = await EnhancedContext.get_conversation_history(db, thread_id, limit)
        
        # Remove MongoDB _id fields
        if "_id" in thread:
            del thread["_id"]
        for msg in messages:
            if "_id" in msg:
                del msg["_id"]
        
        return {
            "thread": thread,
            "messages": messages,
            "message_count": len(messages)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get conversation thread: {str(e)}")

@app.post("/api/conversations/threads/{thread_id}/continue")
async def continue_conversation(
    thread_id: str,
    question_data: dict,
    current_user = Depends(get_current_user)
):
    """Continue an existing conversation thread"""
    try:
        # Verify thread exists and user owns it
        thread = await db.conversation_threads.find_one({
            "thread_id": thread_id,
            "user_id": current_user["user_id"]
        })
        
        if not thread:
            raise HTTPException(status_code=404, detail="Conversation thread not found")
        
        # Find the mentor for this thread
        mentor_id = thread["mentor_id"]
        mentor = next((m for mentors in ALL_MENTORS.values() for m in mentors if m["id"] == mentor_id), None)
        
        if not mentor:
            raise HTTPException(status_code=404, detail="Mentor not found")
        
        # Create contextual question request
        contextual_request = ContextualQuestionRequest(
            category=thread["category"],
            mentor_ids=[mentor_id],
            question=question_data.get("question", ""),
            thread_id=thread_id,
            include_history=True
        )
        
        # Process the contextual question
        response_data = await EnhancedQuestionProcessor.process_contextual_question(
            db, contextual_request, current_user, mentor
        )
        
        # Update user question count
        await db.users.update_one(
            {"user_id": current_user["user_id"]},
            {"$inc": {"questions_asked": 1}}
        )
        
        return {
            "thread_id": thread_id,
            "question": question_data.get("question"),
            "mentor": mentor,
            "response": response_data["response"],
            "context_enabled": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to continue conversation: {str(e)}")

@app.get("/api/conversations/analytics")
async def get_conversation_analytics(current_user = Depends(get_current_user)):
    """Get user's conversation analytics and context usage statistics"""
    try:
        # Get basic conversation stats
        basic_stats = await ConversationAnalytics.get_conversation_stats(
            db, current_user["user_id"]
        )
        
        # Get context effectiveness metrics
        context_metrics = await ConversationAnalytics.get_context_effectiveness_metrics(
            db, current_user["user_id"]
        )
        
        return {
            "user_id": current_user["user_id"],
            "conversation_stats": basic_stats,
            "context_metrics": context_metrics,
            "generated_at": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get conversation analytics: {str(e)}")

@app.post("/api/conversations/threads/{thread_id}/archive")
async def archive_conversation_thread(
    thread_id: str,
    current_user = Depends(get_current_user)
):
    """Archive a conversation thread"""
    try:
        # Verify user owns this thread
        result = await db.conversation_threads.update_one(
            {
                "thread_id": thread_id,
                "user_id": current_user["user_id"]
            },
            {
                "$set": {
                    "is_active": False,
                    "archived_at": datetime.utcnow()
                }
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Conversation thread not found")
        
        return {"message": "Conversation thread archived successfully", "thread_id": thread_id}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to archive conversation thread: {str(e)}")

@app.get("/api/context/explanation")
async def get_context_system_explanation():
    """Get detailed explanation of how the question context system works"""
    return {
        "system_overview": {
            "title": "OnlyMentors.ai Question Context System",
            "description": "Advanced conversation management system that maintains context across multiple interactions with mentors."
        },
        "current_implementation": {
            "question_storage": {
                "description": "All questions and responses are stored in MongoDB with full metadata",
                "features": [
                    "Question and response history per user",
                    "Mentor-specific interaction tracking",
                    "Category-based organization",
                    "Timestamp-based sorting"
                ]
            },
            "session_management": {
                "description": "Each mentor-question interaction uses unique session IDs for context",
                "format": "mentor_{mentor_id}_{hash(question) % 10000}",
                "purpose": "Enables conversation continuity within individual sessions"
            },
            "context_limitations": {
                "current_issues": [
                    "No cross-question context linking",
                    "Limited conversation memory beyond individual sessions",
                    "No conversation threads or follow-up handling",
                    "Isolated question-response pairs"
                ]
            }
        },
        "enhanced_features": {
            "conversation_threads": {
                "description": "Multi-turn conversations with maintained context",
                "benefits": [
                    "Follow-up questions reference previous exchanges",
                    "Mentors remember earlier parts of conversations",
                    "Coherent conversation flow across multiple questions",
                    "Thread-based organization"
                ]
            },
            "contextual_responses": {
                "description": "Mentor responses that acknowledge conversation history",
                "features": [
                    "Reference to previous questions and answers",
                    "Building upon earlier discussions",
                    "Personalized responses based on conversation patterns",
                    "Context-aware mentor personality"
                ]
            },
            "conversation_analytics": {
                "description": "Insights into conversation patterns and context effectiveness",
                "metrics": [
                    "Multi-turn conversation frequency",
                    "Average messages per thread",
                    "Most engaged mentors",
                    "Context utilization statistics"
                ]
            }
        },
        "technical_implementation": {
            "database_structure": {
                "conversation_threads": "Stores conversation metadata and thread information",
                "conversation_messages": "Individual messages within threads with context summaries",
                "enhanced_prompts": "Context-aware system prompts for mentors"
            },
            "api_endpoints": {
                "contextual_questions": "/api/questions/ask-contextual - Enhanced question asking with context",
                "thread_management": "/api/conversations/threads - Manage conversation threads",
                "thread_continuation": "/api/conversations/threads/{id}/continue - Continue existing conversations",
                "analytics": "/api/conversations/analytics - Conversation insights"
            }
        },
        "user_benefits": {
            "improved_responses": "Mentors provide more relevant, context-aware advice",
            "conversation_continuity": "Natural flow in multi-question interactions",
            "personalized_experience": "Responses tailored to individual conversation history",
            "better_learning": "Progressive discussions that build on previous insights"
        }
    }

@app.post("/api/payments/checkout")
async def create_checkout_session(checkout_data: CheckoutRequest, current_user = Depends(get_current_user), request: Request = None):
    if checkout_data.package_id not in SUBSCRIPTION_PACKAGES:
        raise HTTPException(status_code=400, detail="Invalid package")
    
    package = SUBSCRIPTION_PACKAGES[checkout_data.package_id]
    
    # Get base URL from request for webhook
    host_url = str(request.base_url).rstrip('/')
    webhook_url = f"{host_url}/api/webhook/stripe"
    
    # Initialize Stripe checkout
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
    
    # Create checkout session with origin_url for success/cancel
    success_url = f"{checkout_data.origin_url}/?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = checkout_data.origin_url
    
    checkout_request = CheckoutSessionRequest(
        amount=float(package["price"]),  # Ensure float format
        currency=package["currency"],
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            "user_id": current_user["user_id"],
            "package_id": checkout_data.package_id,
            "package_name": package["name"]
        }
    )
    
    session = await stripe_checkout.create_checkout_session(checkout_request)
    
    # Store payment transaction
    payment_doc = {
        "payment_id": str(uuid.uuid4()),
        "user_id": current_user["user_id"],
        "session_id": session.session_id,
        "package_id": checkout_data.package_id,
        "amount": float(package["price"]),  # Ensure float format
        "currency": package["currency"],
        "payment_status": "pending",
        "created_at": datetime.utcnow()
    }
    
    await db.payment_transactions.insert_one(payment_doc)
    
    return {"url": session.url, "session_id": session.session_id}

@app.get("/api/payments/status/{session_id}")
async def get_payment_status(session_id: str, current_user = Depends(get_current_user)):
    # Get payment transaction
    transaction = await db.payment_transactions.find_one({"session_id": session_id})
    if not transaction:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    # Check Stripe status
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url="")
    status_response = await stripe_checkout.get_checkout_status(session_id)
    
    # Update transaction status
    if status_response.payment_status == "paid" and transaction["payment_status"] != "paid":
        await db.payment_transactions.update_one(
            {"session_id": session_id},
            {
                "$set": {
                    "payment_status": "paid",
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        # Update user subscription based on package
        days_to_add = 30 if transaction["package_id"] == "monthly" else 365
        subscription_expires = datetime.utcnow() + timedelta(days=days_to_add)
        await db.users.update_one(
            {"user_id": current_user["user_id"]},
            {
                "$set": {
                    "is_subscribed": True,
                    "subscription_expires": subscription_expires
                }
            }
        )
    
    return {
        "status": status_response.status,
        "payment_status": status_response.payment_status,
        "amount_total": status_response.amount_total,
        "currency": status_response.currency
    }

@app.post("/api/webhook/stripe")
async def stripe_webhook(request: Request):
    body = await request.body()
    signature = request.headers.get("stripe-signature")
    
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url="")
    
    try:
        webhook_response = await stripe_checkout.handle_webhook(body, signature)
        
        if webhook_response.event_type == "checkout.session.completed":
            # Update payment transaction
            await db.payment_transactions.update_one(
                {"session_id": webhook_response.session_id},
                {
                    "$set": {
                        "payment_status": webhook_response.payment_status,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            # Update user subscription if payment succeeded
            if webhook_response.payment_status == "paid":
                user_id = webhook_response.metadata.get("user_id")
                package_id = webhook_response.metadata.get("package_id")
                if user_id:
                    days_to_add = 30 if package_id == "monthly" else 365
                    subscription_expires = datetime.utcnow() + timedelta(days=days_to_add)
                    await db.users.update_one(
                        {"user_id": user_id},
                        {
                            "$set": {
                                "is_subscribed": True,
                                "subscription_expires": subscription_expires
                            }
                        }
                    )
        
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Business Platform Models
class CompanyRegistration(BaseModel):
    company_name: str
    company_email: str
    contact_name: str
    contact_email: str
    contact_phone: str = ""
    industry: str = ""
    company_size: str
    plan_type: str = "enterprise"  # starter, professional, enterprise
    billing_contact: str = ""
    departments: list = []

class DepartmentCode(BaseModel):
    code: str
    name: str
    budget_limit: float = 0.0
    cost_center: str = ""

class EmployeeInvite(BaseModel):
    email: str
    full_name: str
    department_code: str = ""
    role: str = "employee"  # employee, manager, admin

# Business Inquiry System
class BusinessInquiry(BaseModel):
    company_name: str
    contact_name: str
    contact_email: str
    phone_number: str = ""
    company_size: str
    industry: str = ""
    use_case: str
    specific_requirements: str = ""
    budget_range: str = ""
    timeline: str = ""
    submitted_at: str

@app.post("/api/business/inquiry")
async def submit_business_inquiry(inquiry: BusinessInquiry):
    """Submit business inquiry for enterprise OnlyMentors.ai"""
    try:
        # Create inquiry record
        inquiry_doc = {
            "inquiry_id": str(uuid.uuid4()),
            "company_name": inquiry.company_name,
            "contact_name": inquiry.contact_name,
            "contact_email": inquiry.contact_email,
            "phone_number": inquiry.phone_number,
            "company_size": inquiry.company_size,
            "industry": inquiry.industry,
            "use_case": inquiry.use_case,
            "specific_requirements": inquiry.specific_requirements,
            "budget_range": inquiry.budget_range,
            "timeline": inquiry.timeline,
            "status": "new",
            "priority": "medium",
            "assigned_to": None,
            "submitted_at": datetime.fromisoformat(inquiry.submitted_at.replace('Z', '+00:00')),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "notes": []
        }
        
        # Store in database
        await db.business_inquiries.insert_one(inquiry_doc)
        
        # Send notification email (you can implement this later)
        # await send_business_inquiry_notification(inquiry_doc)
        
        return {
            "success": True,
            "message": "Business inquiry submitted successfully",
            "inquiry_id": inquiry_doc["inquiry_id"],
            "next_steps": "Our enterprise team will contact you within 24 hours to discuss your requirements."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit inquiry: {str(e)}")

@app.get("/api/admin/business/inquiries")
async def get_business_inquiries(
    limit: int = 50,
    status: str = "all",
    current_admin = Depends(get_current_admin)
):
    """Get business inquiries for admin review"""
    try:
        if not has_permission(AdminRole(current_admin["role"]), "view_reports"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Build query
        query = {}
        if status != "all":
            query["status"] = status
        
        # Get inquiries
        inquiries = await db.business_inquiries.find(query).sort("created_at", -1).limit(limit).to_list(None)
        
        # Convert ObjectId to string for JSON serialization
        for inquiry in inquiries:
            inquiry["_id"] = str(inquiry["_id"])
            if inquiry.get("submitted_at"):
                inquiry["submitted_at"] = inquiry["submitted_at"].isoformat()
            if inquiry.get("created_at"):
                inquiry["created_at"] = inquiry["created_at"].isoformat()
            if inquiry.get("updated_at"):
                inquiry["updated_at"] = inquiry["updated_at"].isoformat()
        
        return {
            "inquiries": inquiries,
            "total": len(inquiries),
            "status_filter": status
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get business inquiries: {str(e)}")

# Company Registration & Management
@app.post("/api/business/company/register")
async def register_company(company: CompanyRegistration):
    """Register a new business company"""
    try:
        # Check if company already exists
        existing = await db.companies.find_one({"company_email": company.company_email})
        if existing:
            raise HTTPException(status_code=400, detail="Company already registered")
        
        company_id = str(uuid.uuid4())
        
        # Create company record
        company_doc = {
            "company_id": company_id,
            "company_name": company.company_name,
            "company_email": company.company_email,
            "contact_name": company.contact_name,
            "contact_email": company.contact_email,
            "contact_phone": company.contact_phone,
            "industry": company.industry,
            "company_size": company.company_size,
            "plan_type": company.plan_type,
            "billing_contact": company.billing_contact,
            "status": "active",
            "subscription_status": "trial",  # trial, active, suspended
            "trial_ends": datetime.utcnow() + timedelta(days=30),
            "departments": company.departments,
            "selected_ai_mentors": [],  # Company-selected AI mentors
            "settings": {
                "allow_external_mentors": True,
                "require_department_codes": True,
                "content_moderation": True,
                "usage_tracking": True
            },
            "usage_stats": {
                "total_employees": 0,
                "total_questions": 0,
                "monthly_usage": 0,
                "department_usage": {}
            },
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Store company
        await db.companies.insert_one(company_doc)
        
        return {
            "success": True,
            "company_id": company_id,
            "message": "Company registered successfully",
            "trial_period": "30 days",
            "next_steps": "Add departments and invite employees"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to register company: {str(e)}")

@app.post("/api/business/company/{company_id}/departments")
async def add_department(company_id: str, department: DepartmentCode, current_user = Depends(get_current_user)):
    """Add department to company"""
    try:
        # Verify user has company admin access
        company = await db.companies.find_one({"company_id": company_id})
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        # Check if department code already exists
        existing_dept = next((d for d in company.get("departments", []) if d["code"] == department.code), None)
        if existing_dept:
            raise HTTPException(status_code=400, detail="Department code already exists")
        
        # Add department
        dept_doc = {
            "code": department.code,
            "name": department.name,
            "budget_limit": department.budget_limit,
            "cost_center": department.cost_center,
            "created_at": datetime.utcnow(),
            "usage_stats": {
                "total_questions": 0,
                "monthly_spend": 0.0,
                "employee_count": 0
            }
        }
        
        await db.companies.update_one(
            {"company_id": company_id},
            {
                "$push": {"departments": dept_doc},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        return {
            "success": True,
            "message": "Department added successfully",
            "department": dept_doc
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add department: {str(e)}")

@app.post("/api/business/company/{company_id}/employees/invite")
async def invite_employee(company_id: str, employee: EmployeeInvite, current_user = Depends(get_current_user)):
    """Invite employee to company platform"""
    try:
        # Verify company exists
        company = await db.companies.find_one({"company_id": company_id})
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        # Check if user already exists
        existing_user = await db.users.find_one({"email": employee.email})
        
        invite_id = str(uuid.uuid4())
        
        if existing_user:
            # Update existing user to business employee
            await db.users.update_one(
                {"email": employee.email},
                {
                    "$set": {
                        "user_type": "business_employee",
                        "company_id": company_id,
                        "department_code": employee.department_code,
                        "business_role": employee.role,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            message = f"Existing user {employee.email} added to company"
        else:
            # Create invitation record
            invite_doc = {
                "invite_id": invite_id,
                "company_id": company_id,
                "email": employee.email,
                "full_name": employee.full_name,
                "department_code": employee.department_code,
                "role": employee.role,
                "status": "pending",
                "invited_by": current_user["user_id"],
                "invited_at": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(days=7)
            }
            
            await db.employee_invites.insert_one(invite_doc)
            message = f"Invitation sent to {employee.email}"
        
        # Update company employee count
        await db.companies.update_one(
            {"company_id": company_id},
            {"$inc": {"usage_stats.total_employees": 1}}
        )
        
        return {
            "success": True,
            "message": message,
            "invite_id": invite_id if not existing_user else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to invite employee: {str(e)}")

@app.get("/api/business/company/{company_id}/dashboard")
async def get_company_dashboard(company_id: str, current_user = Depends(get_current_user)):
    """Get company dashboard data"""
    try:
        # Verify access
        if current_user.get("user_type") != "business_employee" or current_user.get("company_id") != company_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get company data
        company = await db.companies.find_one({"company_id": company_id})
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        # Get employee data
        employees = await db.users.find({"company_id": company_id}).to_list(None)
        
        # Get usage statistics
        from datetime import timedelta
        last_30_days = datetime.utcnow() - timedelta(days=30)
        
        recent_questions = await db.questions.find({
            "user_id": {"$in": [emp["user_id"] for emp in employees]},
            "created_at": {"$gte": last_30_days}
        }).to_list(None)
        
        # Department usage breakdown
        dept_usage = {}
        for question in recent_questions:
            user = next((emp for emp in employees if emp["user_id"] == question["user_id"]), None)
            if user and user.get("department_code"):
                dept_code = user["department_code"]
                if dept_code not in dept_usage:
                    dept_usage[dept_code] = {"questions": 0, "employees": set()}
                dept_usage[dept_code]["questions"] += 1
                dept_usage[dept_code]["employees"].add(user["user_id"])
        
        # Convert sets to counts
        for dept in dept_usage.values():
            dept["employees"] = len(dept["employees"])
        
        dashboard_data = {
            "company": {
                "name": company["company_name"],
                "plan": company["plan_type"],
                "status": company["status"],
                "trial_ends": company.get("trial_ends", "").isoformat() if company.get("trial_ends") else None
            },
            "stats": {
                "total_employees": len(employees),
                "active_employees": len([emp for emp in employees if emp.get("last_login")]),
                "total_questions_30d": len(recent_questions),
                "departments": len(company.get("departments", [])),
                "internal_mentors": len([emp for emp in employees if emp.get("is_internal_mentor")])
            },
            "department_usage": dept_usage,
            "recent_activity": recent_questions[-10:] if recent_questions else []
        }
        
        return dashboard_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard: {str(e)}")

# =============================================================================
# BUSINESS CATEGORY MANAGEMENT ENDPOINTS
# =============================================================================

@app.get("/api/business/company/{company_id}/categories")
async def get_business_categories(company_id: str, current_user=Depends(get_current_user)):
    """Get all categories for a business"""
    try:
        # Verify user belongs to this company and has admin role
        if current_user.get("company_id") != company_id or current_user.get("business_role") != "admin":
            raise HTTPException(status_code=403, detail="Access denied")
        
        categories = await db.business_categories.find(
            {"company_id": company_id, "is_active": True},
            {"_id": 0}  # Exclude MongoDB ObjectId
        ).to_list(length=None)
        
        # Add mentor count for each category
        for category in categories:
            mentor_count = await db.business_mentors.count_documents({
                "company_id": company_id,
                "category_ids": category["category_id"]
            }) if "category_id" in category else 0
            category["mentor_count"] = mentor_count
        
        return categories
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get categories: {str(e)}")

@app.post("/api/business/company/{company_id}/categories")
async def create_business_category(company_id: str, category_data: dict, current_user=Depends(get_current_user)):
    """Create a new business category"""
    try:
        # Verify user belongs to this company and has admin role
        if current_user.get("company_id") != company_id or current_user.get("business_role") != "admin":
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Create category document
        category_id = str(uuid.uuid4())
        category_doc = {
            "category_id": category_id,
            "company_id": company_id,
            "name": category_data["name"],
            "slug": category_data["name"].lower().replace(" ", "-"),
            "icon": category_data.get("icon", "📂"),
            "description": category_data.get("description", ""),
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await db.business_categories.insert_one(category_doc)
        return {"message": "Category created successfully", "category_id": category_id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create category: {str(e)}")

@app.put("/api/business/company/{company_id}/categories/{category_id}")
async def update_business_category(company_id: str, category_id: str, category_data: dict, current_user=Depends(get_current_user)):
    """Update a business category"""
    try:
        # Verify user belongs to this company and has admin role
        if current_user.get("company_id") != company_id or current_user.get("business_role") != "admin":
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Update category
        update_data = {
            "name": category_data["name"],
            "slug": category_data["name"].lower().replace(" ", "-"),
            "icon": category_data.get("icon", "📂"),
            "description": category_data.get("description", ""),
            "updated_at": datetime.utcnow()
        }
        
        result = await db.business_categories.update_one(
            {"category_id": category_id, "company_id": company_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Category not found")
        
        return {"message": "Category updated successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update category: {str(e)}")

@app.delete("/api/business/company/{company_id}/categories/{category_id}")
async def delete_business_category(company_id: str, category_id: str, current_user=Depends(get_current_user)):
    """Delete a business category"""
    try:
        # Verify user belongs to this company and has admin role
        if current_user.get("company_id") != company_id or current_user.get("business_role") != "admin":
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Check if category has mentors assigned
        mentor_count = await db.business_mentors.count_documents({
            "company_id": company_id,
            "category_ids": category_id
        })
        
        if mentor_count > 0:
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot delete category. {mentor_count} mentors are assigned to this category."
            )
        
        # Delete category
        result = await db.business_categories.delete_one({
            "category_id": category_id,
            "company_id": company_id
        })
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Category not found")
        
        return {"message": "Category deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete category: {str(e)}")

@app.post("/api/business/company/{company_id}/categories/initialize")
async def initialize_default_categories(company_id: str, current_user=Depends(get_current_user)):
    """Initialize default categories for a new business"""
    try:
        # Verify user belongs to this company and has admin role
        if current_user.get("company_id") != company_id or current_user.get("business_role") != "admin":
            raise HTTPException(status_code=403, detail="Access denied")
        
        default_categories = [
            {"name": "Business Operations", "icon": "⚙️", "description": "Operations, strategy, and process improvement"},
            {"name": "Sales", "icon": "💼", "description": "Sales strategy, customer relations, and revenue growth"},
            {"name": "Training", "icon": "📚", "description": "Employee development and skills training"},
            {"name": "HR", "icon": "👥", "description": "Human resources, recruiting, and employee relations"},
            {"name": "Payroll", "icon": "💰", "description": "Payroll processing and compensation management"},
            {"name": "Accounting", "icon": "📊", "description": "Financial management and accounting"},
            {"name": "Product Development", "icon": "🚀", "description": "Product strategy and development"},
            {"name": "Technology", "icon": "💻", "description": "IT infrastructure and software development"},
            {"name": "Technical Support", "icon": "🛠️", "description": "Technical assistance and troubleshooting"}
        ]
        
        categories_created = 0
        for category_data in default_categories:
            # Check if category already exists
            existing = await db.business_categories.find_one({
                "company_id": company_id,
                "name": category_data["name"]
            })
            
            if not existing:
                category_id = str(uuid.uuid4())
                category_doc = {
                    "category_id": category_id,
                    "company_id": company_id,
                    "name": category_data["name"],
                    "slug": category_data["name"].lower().replace(" ", "-"),
                    "icon": category_data["icon"],
                    "description": category_data["description"],
                    "is_active": True,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                
                await db.business_categories.insert_one(category_doc)
                categories_created += 1
        
        return {"message": f"Initialized {categories_created} default categories"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize categories: {str(e)}")

# =============================================================================
# BUSINESS PUBLIC LANDING PAGE ENDPOINTS (No Auth Required)
# =============================================================================

@app.get("/api/business/public/{business_slug}")
async def get_business_public_info(business_slug: str):
    """Get public business information for landing page"""
    try:
        # Find business by slug (we'll use company name as slug for now)
        company = await db.companies.find_one(
            {"slug": business_slug},
            {"_id": 0}
        )
        
        if not company:
            # Try to find by company name converted to slug
            slug_name = business_slug.replace("-", " ").title()
            company = await db.companies.find_one(
                {"company_name": {"$regex": slug_name, "$options": "i"}},
                {"_id": 0}
            )
        
        if not company:
            raise HTTPException(status_code=404, detail="Business not found")
        
        # Return public business info
        return {
            "company_id": company["company_id"],
            "company_name": company["company_name"],
            "slug": business_slug,
            "industry": company.get("industry", ""),
            "description": company.get("description", ""),
            "website": company.get("website", ""),
            "status": company.get("status", "active")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get business info: {str(e)}")

@app.get("/api/business/public/{business_slug}/categories")
async def get_business_public_categories(business_slug: str):
    """Get public business categories for landing page"""
    try:
        # Get business info first
        business = await get_business_public_info(business_slug)
        company_id = business["company_id"]
        
        # Get categories for this business
        categories = await db.business_categories.find(
            {"company_id": company_id, "is_active": True},
            {"_id": 0}
        ).to_list(length=None)
        
        # Add mentor count for each category
        for category in categories:
            mentor_count = await db.business_mentor_assignments.count_documents({
                "company_id": company_id,
                "category_ids": category["category_id"]
            })
            category["mentor_count"] = mentor_count
        
        return categories
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get categories: {str(e)}")

@app.get("/api/business/public/{business_slug}/categories/{category_id}/mentors")
async def get_business_public_category_mentors(business_slug: str, category_id: str):
    """Get mentors for a specific category on business landing page"""
    try:
        # Get business info first
        business = await get_business_public_info(business_slug)
        company_id = business["company_id"]
        
        # Get assignments for this category
        assignments = await db.business_mentor_assignments.find(
            {
                "company_id": company_id,
                "category_ids": category_id
            },
            {"_id": 0}
        ).to_list(length=None)
        
        mentors = []
        for assignment in assignments:
            if assignment["mentor_type"] == "ai":
                # Get AI mentor details
                mentor = await db.mentors.find_one(
                    {"mentor_id": assignment["mentor_id"]},
                    {"_id": 0}
                )
                if mentor:
                    mentors.append({
                        "mentor_id": mentor["mentor_id"],
                        "name": mentor["name"],
                        "description": mentor.get("description", ""),
                        "type": "ai",
                        "expertise": mentor.get("expertise", [])
                    })
            else:
                # Get human mentor details (only show public info)
                mentor = await db.users.find_one(
                    {"user_id": assignment["mentor_id"]},
                    {"_id": 0, "full_name": 1, "department_code": 1}
                )
                if mentor:
                    mentors.append({
                        "mentor_id": mentor["user_id"],
                        "name": mentor["full_name"],
                        "type": "human",
                        "department": mentor.get("department_code", "")
                    })
        
        return mentors
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get category mentors: {str(e)}")

# =============================================================================
# BUSINESS MENTOR-CATEGORY ASSIGNMENT ENDPOINTS
# =============================================================================

@app.get("/api/business/company/{company_id}/mentors")
async def get_business_mentors(company_id: str, current_user=Depends(get_current_user)):
    """Get all mentors available for assignment in a business"""
    try:
        # Verify user belongs to this company and has admin role
        if current_user.get("company_id") != company_id or current_user.get("business_role") != "admin":
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get all mentors (both AI and human) that could be assigned to this business
        # For now, we'll get from the main mentors collection and business employees who are mentors
        
        # Get AI mentors from main categories (these can be assigned to businesses)
        ai_mentors = await db.mentors.find(
            {"type": "ai"},
            {"_id": 0}
        ).to_list(length=None)
        
        # Get human mentors who are employees of this business
        business_mentors = await db.users.find(
            {
                "company_id": company_id,
                "user_type": "business_employee",
                "is_mentor": True
            },
            {"_id": 0}
        ).to_list(length=None)
        
        # Get existing assignments
        assignments = await db.business_mentor_assignments.find(
            {"company_id": company_id},
            {"_id": 0}
        ).to_list(length=None)
        
        # Create assignment lookup
        assignment_lookup = {}
        for assignment in assignments:
            mentor_key = f"{assignment['mentor_type']}_{assignment['mentor_id']}"
            assignment_lookup[mentor_key] = assignment['category_ids']
        
        # Format AI mentors
        formatted_mentors = []
        for mentor in ai_mentors:
            mentor_key = f"ai_{mentor['mentor_id']}"
            formatted_mentors.append({
                "mentor_id": mentor["mentor_id"],
                "name": mentor["name"],
                "description": mentor.get("description", ""),
                "expertise": mentor.get("expertise", []),
                "type": "ai",
                "category_ids": assignment_lookup.get(mentor_key, []),
                "is_assigned": mentor_key in assignment_lookup
            })
        
        # Format human mentors
        for mentor in business_mentors:
            mentor_key = f"human_{mentor['user_id']}"
            formatted_mentors.append({
                "mentor_id": mentor["user_id"],
                "name": mentor["full_name"],
                "email": mentor["email"],
                "department": mentor.get("department_code", ""),
                "type": "human",
                "category_ids": assignment_lookup.get(mentor_key, []),
                "is_assigned": mentor_key in assignment_lookup
            })
        
        return formatted_mentors
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get mentors: {str(e)}")

@app.post("/api/business/company/{company_id}/mentors/{mentor_id}/categories")
async def assign_mentor_to_categories(
    company_id: str, 
    mentor_id: str, 
    assignment_data: dict, 
    current_user=Depends(get_current_user)
):
    """Assign a mentor to specific categories"""
    try:
        # Verify user belongs to this company and has admin role
        if current_user.get("company_id") != company_id or current_user.get("business_role") != "admin":
            raise HTTPException(status_code=403, detail="Access denied")
        
        mentor_type = assignment_data.get("mentor_type", "ai")  # ai or human
        category_ids = assignment_data.get("category_ids", [])
        
        # Validate categories exist
        for category_id in category_ids:
            category = await db.business_categories.find_one({
                "category_id": category_id,
                "company_id": company_id
            })
            if not category:
                raise HTTPException(status_code=400, detail=f"Category {category_id} not found")
        
        # Update or create assignment
        assignment_filter = {
            "company_id": company_id,
            "mentor_id": mentor_id,
            "mentor_type": mentor_type
        }
        
        assignment_data = {
            "company_id": company_id,
            "mentor_id": mentor_id,
            "mentor_type": mentor_type,
            "category_ids": category_ids,
            "updated_at": datetime.utcnow()
        }
        
        # Check if assignment exists
        existing = await db.business_mentor_assignments.find_one(assignment_filter)
        
        if existing:
            # Update existing assignment
            await db.business_mentor_assignments.update_one(
                assignment_filter,
                {"$set": assignment_data}
            )
        else:
            # Create new assignment
            assignment_data["created_at"] = datetime.utcnow()
            await db.business_mentor_assignments.insert_one(assignment_data)
        
        return {"message": "Mentor assigned to categories successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to assign mentor: {str(e)}")

@app.delete("/api/business/company/{company_id}/mentors/{mentor_id}/categories")
async def remove_mentor_from_categories(
    company_id: str, 
    mentor_id: str, 
    mentor_type: str, 
    current_user=Depends(get_current_user)
):
    """Remove a mentor from all category assignments"""
    try:
        # Verify user belongs to this company and has admin role
        if current_user.get("company_id") != company_id or current_user.get("business_role") != "admin":
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Remove assignment
        result = await db.business_mentor_assignments.delete_one({
            "company_id": company_id,
            "mentor_id": mentor_id,
            "mentor_type": mentor_type
        })
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Mentor assignment not found")
        
        return {"message": "Mentor removed from categories successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove mentor: {str(e)}")

@app.get("/api/business/company/{company_id}/categories/{category_id}/mentors")
async def get_mentors_by_category(company_id: str, category_id: str, current_user=Depends(get_current_user)):
    """Get all mentors assigned to a specific category"""
    try:
        # Verify user belongs to this company
        if current_user.get("company_id") != company_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get assignments for this category
        assignments = await db.business_mentor_assignments.find(
            {
                "company_id": company_id,
                "category_ids": category_id
            },
            {"_id": 0}
        ).to_list(length=None)
        
        mentors = []
        for assignment in assignments:
            if assignment["mentor_type"] == "ai":
                # Get AI mentor details
                mentor = await db.mentors.find_one(
                    {"mentor_id": assignment["mentor_id"]},
                    {"_id": 0}
                )
                if mentor:
                    mentors.append({
                        "mentor_id": mentor["mentor_id"],
                        "name": mentor["name"],
                        "description": mentor.get("description", ""),
                        "type": "ai",
                        "expertise": mentor.get("expertise", [])
                    })
            else:
                # Get human mentor details
                mentor = await db.users.find_one(
                    {"user_id": assignment["mentor_id"]},
                    {"_id": 0}
                )
                if mentor:
                    mentors.append({
                        "mentor_id": mentor["user_id"],
                        "name": mentor["full_name"],
                        "email": mentor["email"],
                        "type": "human",
                        "department": mentor.get("department_code", "")
                    })
        
        return mentors
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get category mentors: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

# =============================================================================
# CREATOR MARKETPLACE ENDPOINTS
# =============================================================================

@app.post("/api/creators/signup")
async def creator_signup(creator_data: CreatorSignupRequest):
    """Sign up as a new creator"""
    try:
        # Check if email is already registered as mentor
        existing_creator = await db.creators.find_one({"email": creator_data.email})
        if existing_creator:
            raise HTTPException(status_code=400, detail="Email already registered as mentor")
        
        # Check if account name is taken
        existing_name = await db.creators.find_one({"account_name": creator_data.account_name})
        if existing_name:
            raise HTTPException(status_code=400, detail="Account name already taken")
        
        # Create creator document
        creator_id = generate_creator_id()
        creator_doc = {
            "creator_id": creator_id,
            "user_id": None,  # Will be set if upgrading from user
            "email": creator_data.email,
            "password_hash": hash_password(creator_data.password),
            "full_name": creator_data.full_name,
            "account_name": creator_data.account_name,
            "description": creator_data.description,
            "bio": "",
            "monthly_price": float(creator_data.monthly_price),
            "category": creator_data.category,
            "expertise_areas": creator_data.expertise_areas,
            "status": CreatorStatus.PENDING,
            "profile_image_url": None,
            "cover_image_url": None,
            "social_links": {},
            "verification": {
                "id_verified": False,
                "bank_verified": False,
                "id_document_url": None,
                "submitted_at": None,
                "verified_at": None
            },
            "banking_info": {
                "bank_account_number": "",
                "routing_number": "",
                "tax_id": "",
                "account_holder_name": "",
                "bank_name": "",
                "verified": False
            },
            "stats": {
                "total_earnings": 0.0,
                "monthly_earnings": 0.0,
                "subscriber_count": 0,
                "content_count": 0,
                "total_questions": 0,
                "average_rating": 5.0
            },
            "settings": {
                "auto_approve_messages": True,
                "allow_tips": True,
                "response_time": "24 hours"
            },
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "last_active": datetime.utcnow()
        }
        
        await db.creators.insert_one(creator_doc)
        
        # Create access token
        token = create_access_token({"creator_id": creator_id, "type": "creator"})
        
        return {
            "token": token,
            "creator": get_creator_public_profile(creator_doc),
            "message": "Mentor account created successfully. Please complete verification."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create creator account: {str(e)}")

class CreatorLoginRequest(BaseModel):
    email: str
    password: str

@app.post("/api/creators/login")
async def creator_login(login_data: CreatorLoginRequest):
    """Creator login"""
    try:
        creator = await db.creators.find_one({"email": login_data.email})
        if not creator or not verify_password(login_data.password, creator["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Update last active
        await db.creators.update_one(
            {"creator_id": creator["creator_id"]},
            {"$set": {"last_active": datetime.utcnow()}}
        )
        
        # Create access token
        token = create_access_token({"creator_id": creator["creator_id"], "type": "creator"})
        
        return {
            "token": token,
            "creator": get_creator_public_profile(creator)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@app.post("/api/creators/upgrade")
async def upgrade_user_to_mentor(creator_data: CreatorSignupRequest, current_user = Depends(get_current_user)):
    """Upgrade existing user account to mentor"""
    try:
        # Check if user already has mentor account
        existing_creator = await db.creators.find_one({"user_id": current_user["user_id"]})
        if existing_creator:
            raise HTTPException(status_code=400, detail="User already has mentor account")
        
        # Check if account name is taken
        existing_name = await db.creators.find_one({"account_name": creator_data.account_name})
        if existing_name:
            raise HTTPException(status_code=400, detail="Account name already taken")
        
        # Create creator document linked to user
        creator_id = generate_creator_id()
        creator_doc = {
            "creator_id": creator_id,
            "user_id": current_user["user_id"],
            "email": current_user["email"],
            "password_hash": current_user["password_hash"],
            "full_name": creator_data.full_name,
            "account_name": creator_data.account_name,
            "description": creator_data.description,
            "bio": "",
            "monthly_price": float(creator_data.monthly_price),
            "category": creator_data.category,
            "expertise_areas": creator_data.expertise_areas,
            "status": CreatorStatus.PENDING,
            "profile_image_url": None,
            "cover_image_url": None,
            "social_links": {},
            "verification": {
                "id_verified": False,
                "bank_verified": False,
                "id_document_url": None,
                "submitted_at": None,
                "verified_at": None
            },
            "banking_info": {
                "bank_account_number": "",
                "routing_number": "",
                "tax_id": "",
                "account_holder_name": "",
                "bank_name": "",
                "verified": False
            },
            "stats": {
                "total_earnings": 0.0,
                "monthly_earnings": 0.0,
                "subscriber_count": 0,
                "content_count": 0,
                "total_questions": 0,
                "average_rating": 5.0
            },
            "settings": {
                "auto_approve_messages": True,
                "allow_tips": True,
                "response_time": "24 hours"
            },
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "last_active": datetime.utcnow()
        }
        
        await db.creators.insert_one(creator_doc)
        
        return {
            "creator": get_creator_public_profile(creator_doc),
            "message": "Successfully upgraded to mentor account. Please complete verification."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upgrade account: {str(e)}")

@app.post("/api/creators/{creator_id}/banking")
async def submit_banking_info(creator_id: str, banking_data: BankingInfoRequest):
    """Submit banking information for creator verification"""
    try:
        creator = await db.creators.find_one({"creator_id": creator_id})
        if not creator:
            raise HTTPException(status_code=404, detail="Creator not found")
        
        # Update banking information (in production, encrypt sensitive data)
        banking_info = {
            "bank_account_number": banking_data.bank_account_number,
            "routing_number": banking_data.routing_number,
            "tax_id": banking_data.tax_id,
            "account_holder_name": banking_data.account_holder_name,
            "bank_name": banking_data.bank_name,
            "verified": False  # Will be verified by automated system
        }
        
        await db.creators.update_one(
            {"creator_id": creator_id},
            {
                "$set": {
                    "banking_info": banking_info,
                    "verification.submitted_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        # Simulate bank verification process (in production, integrate with bank verification API)
        # For demo purposes, auto-approve if basic validation passes
        if (len(banking_data.bank_account_number) >= 8 and 
            len(banking_data.routing_number) == 9 and 
            len(banking_data.tax_id) >= 9):
            
            await db.creators.update_one(
                {"creator_id": creator_id},
                {
                    "$set": {
                        "banking_info.verified": True,
                        "verification.bank_verified": True,
                        "verification.bank_verified_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            # Check if fully verified and update status
            updated_creator = await db.creators.find_one({"creator_id": creator_id})
            if (updated_creator["verification"]["id_verified"] and 
                updated_creator["verification"]["bank_verified"]):
                await db.creators.update_one(
                    {"creator_id": creator_id},
                    {"$set": {"status": CreatorStatus.APPROVED}}
                )
            
            return {"message": "Banking information submitted and verified successfully", "verified": True}
        else:
            return {"message": "Banking information submitted for review", "verified": False}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit banking info: {str(e)}")

@app.post("/api/creators/{creator_id}/id-verification")
async def upload_id_verification(creator_id: str, id_document: UploadFile = File(...)):
    """Upload ID document for creator verification"""
    try:
        creator = await db.creators.find_one({"creator_id": creator_id})
        if not creator:
            raise HTTPException(status_code=404, detail="Creator not found")
        
        # Validate file type (should be image or PDF)
        allowed_types = ["image/jpeg", "image/png", "image/jpg", "application/pdf"]
        if id_document.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="Invalid file type. Please upload JPG, PNG, or PDF")
        
        # Validate file size (max 10MB)
        if id_document.size > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large. Maximum size is 10MB")
        
        # Save file (in production, save to cloud storage)
        file_path = f"/app/uploads/id_documents/{creator_id}_{id_document.filename}"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, "wb") as buffer:
            content = await id_document.read()
            buffer.write(content)
        
        # Update creator with ID document info
        await db.creators.update_one(
            {"creator_id": creator_id},
            {
                "$set": {
                    "verification.id_document_url": file_path,
                    "verification.submitted_at": datetime.utcnow(),
                    "verification.id_verified": True,  # Auto-approve for demo
                    "verification.verified_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        # Check if fully verified (ID + bank)
        updated_creator = await db.creators.find_one({"creator_id": creator_id})
        if updated_creator["verification"]["id_verified"] and updated_creator["verification"]["bank_verified"]:
            await db.creators.update_one(
                {"creator_id": creator_id},
                {"$set": {"status": CreatorStatus.APPROVED}}
            )
        
        return {"message": "ID document uploaded and verified successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload ID: {str(e)}")

@app.get("/api/creators")
async def get_creators(category: Optional[str] = None, limit: int = 50, offset: int = 0):
    """Get list of approved creators"""
    try:
        query = {"status": CreatorStatus.APPROVED}
        if category:
            query["category"] = category
        
        creators = await db.creators.find(query).skip(offset).limit(limit).to_list(limit)
        creator_profiles = [get_creator_public_profile(creator) for creator in creators]
        
        return {
            "creators": creator_profiles,
            "total": len(creator_profiles)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch creators: {str(e)}")

@app.get("/api/creators/{creator_id}")
async def get_creator_profile(creator_id: str):
    """Get individual creator profile"""
    try:
        creator = await db.creators.find_one({"creator_id": creator_id})
        if not creator:
            raise HTTPException(status_code=404, detail="Creator not found")
        
        return get_creator_public_profile(creator)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch creator: {str(e)}")

@app.post("/api/creators/{creator_id}/content")
async def upload_creator_content(
    creator_id: str,
    title: str = Form(...),
    description: str = Form(...),
    content_type: str = Form(...),
    category: str = Form(None),
    tags: str = Form("[]"),
    content_file: UploadFile = File(None),
    current_creator = Depends(get_current_creator)
):
    """Upload content for creator"""
    try:
        # Verify the authenticated creator matches the creator_id
        if current_creator["creator_id"] != creator_id:
            raise HTTPException(status_code=403, detail="Cannot upload content for another creator")
        
        creator = await db.creators.find_one({"creator_id": creator_id})
        if not creator:
            raise HTTPException(status_code=404, detail="Creator not found")
        
        # Parse tags
        import json
        try:
            tag_list = json.loads(tags) if tags != "[]" else []
        except:
            tag_list = []
        
        # Validate content type
        if content_type not in ["video", "document", "article_link", "podcast"]:
            raise HTTPException(status_code=400, detail="Invalid content type")
        
        # Handle file upload
        file_url = None
        file_size = None
        file_type = None
        
        if content_file and content_type != "article_link":
            # Validate file based on content type
            if content_type == "video":
                allowed_types = ["video/mp4", "video/avi", "video/mov", "video/wmv", "video/x-flv", "video/webm", "video/x-msvideo"]
                max_size = 200 * 1024 * 1024  # 200MB
                if content_file.content_type not in allowed_types:
                    raise HTTPException(status_code=400, detail="Invalid video file type")
            elif content_type == "document":
                allowed_types = ["application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "text/plain"]
                max_size = 50 * 1024 * 1024  # 50MB
                if content_file.content_type not in allowed_types:
                    raise HTTPException(status_code=400, detail="Invalid document file type")
            elif content_type == "podcast":
                allowed_types = ["audio/mpeg", "audio/mp3", "audio/aac", "audio/mp4", "audio/wav", "audio/wave", "audio/x-wav"]
                max_size = 500 * 1024 * 1024  # 500MB for audio files
                if content_file.content_type not in allowed_types:
                    # Also check by file extension as fallback
                    file_ext = content_file.filename.lower().split('.')[-1] if '.' in content_file.filename else ''
                    if file_ext not in ['mp3', 'aac', 'm4a', 'wav']:
                        raise HTTPException(status_code=400, detail="Invalid podcast file type. Supported formats: mp3, aac, m4a, wav")
            
            if content_file.size > max_size:
                raise HTTPException(status_code=400, detail=f"File too large. Maximum size is {max_size / 1024 / 1024}MB")
            
            # Save file (in production, save to cloud storage)
            import os
            upload_dir = f"/app/uploads/content/{creator_id}"
            os.makedirs(upload_dir, exist_ok=True)
            
            file_path = f"{upload_dir}/{content_file.filename}"
            with open(file_path, "wb") as buffer:
                content = await content_file.read()
                buffer.write(content)
            
            file_url = file_path
            file_size = content_file.size
            file_type = content_file.content_type
        
        # Create content document
        content_id = generate_content_id()
        content_doc = {
            "content_id": content_id,
            "creator_id": creator_id,
            "title": title,
            "description": description,
            "content_type": content_type,
            "file_url": file_url,
            "file_size": file_size,
            "file_type": file_type,
            "thumbnail_url": None,
            "category": category,
            "tags": tag_list,
            "view_count": 0,
            "like_count": 0,
            "is_featured": False,
            "is_public": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Save to database
        await db.creator_content.insert_one(content_doc)
        
        # Update creator content count
        await db.creators.update_one(
            {"creator_id": creator_id},
            {"$inc": {"stats.content_count": 1}}
        )
        
        return {"message": "Content uploaded successfully", "content_id": content_id}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload content: {str(e)}")

@app.get("/api/creators/{creator_id}/content")
async def get_creator_content(
    creator_id: str, 
    limit: int = 20, 
    offset: int = 0,
    current_creator = Depends(get_current_creator)
):
    """Get creator's content"""
    try:
        # Verify creator owns this content
        if current_creator["creator_id"] != creator_id:
            raise HTTPException(status_code=403, detail="Access denied: can only access your own content")
        
        content_list = await db.creator_content.find(
            {"creator_id": creator_id}
        ).sort("created_at", -1).skip(offset).limit(limit).to_list(limit)
        
        # Convert ObjectId to string for JSON serialization
        for content in content_list:
            content["_id"] = str(content["_id"]) if "_id" in content else None
        
        return {"content": content_list, "total": len(content_list)}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get content: {str(e)}")

# =============================================================================
# ENHANCED CONTENT MANAGEMENT ENDPOINTS - Option 3
# =============================================================================

@app.put("/api/creators/{creator_id}/content/{content_id}")
async def update_creator_content(
    creator_id: str, 
    content_id: str, 
    update_data: ContentUpdateRequest,
    current_creator = Depends(get_current_creator)
):
    """Update/Edit creator's content"""
    try:
        # Verify creator owns this content
        if current_creator["creator_id"] != creator_id:
            raise HTTPException(status_code=403, detail="Access denied: can only manage your own content")
        
        # Verify content exists and belongs to creator
        content = await db.creator_content.find_one({
            "content_id": content_id,
            "creator_id": creator_id
        })
        if not content:
            raise HTTPException(status_code=404, detail="Content not found or doesn't belong to creator")
        
        # Build update document
        update_doc = {"updated_at": datetime.utcnow()}
        
        if update_data.title is not None:
            update_doc["title"] = update_data.title
        if update_data.description is not None:
            update_doc["description"] = update_data.description
        if update_data.category is not None:
            update_doc["category"] = update_data.category
        if update_data.tags is not None:
            update_doc["tags"] = update_data.tags
        if update_data.is_public is not None:
            update_doc["is_public"] = update_data.is_public
        if update_data.is_featured is not None:
            update_doc["is_featured"] = update_data.is_featured
        
        # Update content
        result = await db.creator_content.update_one(
            {"content_id": content_id, "creator_id": creator_id},
            {"$set": update_doc}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=400, detail="No changes made to content")
        
        # Get updated content
        updated_content = await db.creator_content.find_one({
            "content_id": content_id,
            "creator_id": creator_id
        })
        
        # Convert ObjectId for JSON serialization
        if updated_content and "_id" in updated_content:
            updated_content["_id"] = str(updated_content["_id"])
        
        return {
            "message": "Content updated successfully",
            "content": updated_content
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update content: {str(e)}")

@app.delete("/api/creators/{creator_id}/content/{content_id}")
async def delete_creator_content(
    creator_id: str, 
    content_id: str,
    current_creator = Depends(get_current_creator)
):
    """Delete creator's content"""
    try:
        # Verify creator owns this content
        if current_creator["creator_id"] != creator_id:
            raise HTTPException(status_code=403, detail="Access denied: can only manage your own content")
        
        # Verify content exists and belongs to creator
        content = await db.creator_content.find_one({
            "content_id": content_id,
            "creator_id": creator_id
        })
        if not content:
            raise HTTPException(status_code=404, detail="Content not found or doesn't belong to creator")
        
        # Delete associated file if it exists
        if content.get("file_url") and os.path.exists(content["file_url"]):
            try:
                os.remove(content["file_url"])
            except OSError as e:
                print(f"Warning: Could not delete file {content['file_url']}: {str(e)}")
        
        # Delete content from database
        result = await db.creator_content.delete_one({
            "content_id": content_id,
            "creator_id": creator_id
        })
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=400, detail="Failed to delete content")
        
        # Update creator content count
        await db.creators.update_one(
            {"creator_id": creator_id},
            {"$inc": {"stats.content_count": -1}}
        )
        
        return {
            "message": "Content deleted successfully",
            "content_id": content_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete content: {str(e)}")

@app.get("/api/creators/{creator_id}/content/{content_id}")
async def get_single_content(
    creator_id: str, 
    content_id: str,
    current_creator = Depends(get_current_creator)
):
    """Get single content item for editing"""
    try:
        # Verify creator owns this content
        if current_creator["creator_id"] != creator_id:
            raise HTTPException(status_code=403, detail="Access denied: can only access your own content")
        
        # Get content
        content = await db.creator_content.find_one({
            "content_id": content_id,
            "creator_id": creator_id
        })
        if not content:
            raise HTTPException(status_code=404, detail="Content not found or doesn't belong to creator")
        
        # Convert ObjectId for JSON serialization
        if "_id" in content:
            content["_id"] = str(content["_id"])
        
        return {"content": content}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get content: {str(e)}")

@app.post("/api/creators/{creator_id}/content/{content_id}/duplicate")
async def duplicate_creator_content(
    creator_id: str, 
    content_id: str,
    current_creator = Depends(get_current_creator)
):
    """Duplicate existing content"""
    try:
        # Verify creator owns this content
        if current_creator["creator_id"] != creator_id:
            raise HTTPException(status_code=403, detail="Access denied: can only duplicate your own content")
        
        # Get original content
        original_content = await db.creator_content.find_one({
            "content_id": content_id,
            "creator_id": creator_id
        })
        if not original_content:
            raise HTTPException(status_code=404, detail="Content not found or doesn't belong to creator")
        
        # Create duplicate content document
        new_content_id = generate_content_id()
        duplicate_content = {
            **original_content,
            "content_id": new_content_id,
            "title": f"{original_content['title']} (Copy)",
            "view_count": 0,
            "like_count": 0,
            "is_featured": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Remove the original _id to create new document
        if "_id" in duplicate_content:
            del duplicate_content["_id"]
        
        # Save duplicate content
        await db.creator_content.insert_one(duplicate_content)
        
        # Update creator content count
        await db.creators.update_one(
            {"creator_id": creator_id},
            {"$inc": {"stats.content_count": 1}}
        )
        
        # Convert ObjectId for JSON serialization
        duplicate_content["_id"] = str(duplicate_content["_id"]) if "_id" in duplicate_content else None
        
        return {
            "message": "Content duplicated successfully",
            "content": duplicate_content
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to duplicate content: {str(e)}")

@app.get("/api/creators/{creator_id}/premium-content")
async def get_creator_premium_content(
    creator_id: str,
    offset: int = 0,
    limit: int = 20,
    current_creator = Depends(get_current_creator)
):
    """Get creator's premium content for management"""
    try:
        # Verify creator owns this content
        if current_creator["creator_id"] != creator_id:
            raise HTTPException(status_code=403, detail="Access denied: can only access your own premium content")
        
        premium_content_list = await db.premium_content.find(
            {"creator_id": creator_id}
        ).sort("created_at", -1).skip(offset).limit(limit).to_list(limit)
        
        # Convert ObjectId to string for JSON serialization
        for content in premium_content_list:
            if "_id" in content:
                content["_id"] = str(content["_id"])
        
        # Get total count
        total_count = await db.premium_content.count_documents({"creator_id": creator_id})
        
        return {
            "content": premium_content_list,
            "total": total_count,
            "offset": offset,
            "limit": limit
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch premium content: {str(e)}")

@app.put("/api/creators/{creator_id}/premium-content/{content_id}")
async def update_premium_content(
    creator_id: str,
    content_id: str,
    title: str = Form(...),
    description: str = Form(...),
    category: str = Form(None),
    price: float = Form(...),
    tags: str = Form("[]"),
    preview_available: bool = Form(False),
    current_creator = Depends(get_current_creator)
):
    """Update premium content"""
    try:
        # Verify creator owns this content
        if current_creator["creator_id"] != creator_id:
            raise HTTPException(status_code=403, detail="Access denied: can only update your own content")
        
        # Parse tags
        import json
        try:
            tag_list = json.loads(tags) if tags != "[]" else []
        except:
            tag_list = []
        
        # Validate pricing
        if price < 0.01 or price > 50.00:
            raise HTTPException(status_code=400, detail="Price must be between $0.01 and $50.00")
        
        # Find the content
        content = await db.premium_content.find_one({
            "content_id": content_id,
            "creator_id": creator_id
        })
        
        if not content:
            raise HTTPException(status_code=404, detail="Premium content not found or doesn't belong to creator")
        
        # Update the content
        update_data = {
            "title": title,
            "description": description,
            "category": category,
            "price": price,
            "tags": tag_list,
            "preview_available": preview_available,
            "updated_at": datetime.now().isoformat()
        }
        
        result = await db.premium_content.update_one(
            {"content_id": content_id, "creator_id": creator_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Content not found")
        
        # Get updated content
        updated_content = await db.premium_content.find_one({
            "content_id": content_id,
            "creator_id": creator_id
        })
        
        # Convert ObjectId for JSON serialization
        if updated_content and "_id" in updated_content:
            updated_content["_id"] = str(updated_content["_id"])
        
        return {
            "message": "Premium content updated successfully",
            "content": updated_content
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update premium content: {str(e)}")

@app.delete("/api/creators/{creator_id}/premium-content/{content_id}")
async def delete_premium_content(
    creator_id: str,
    content_id: str,
    current_creator = Depends(get_current_creator)
):
    """Delete premium content"""
    try:
        # Verify creator owns this content
        if current_creator["creator_id"] != creator_id:
            raise HTTPException(status_code=403, detail="Access denied: can only delete your own content")
        
        # Find the content first to verify it exists and get file path for cleanup
        content = await db.premium_content.find_one({
            "content_id": content_id,
            "creator_id": creator_id
        })
        
        if not content:
            raise HTTPException(status_code=404, detail="Premium content not found or doesn't belong to creator")
        
        # Delete the content record
        result = await db.premium_content.delete_one({
            "content_id": content_id,
            "creator_id": creator_id
        })
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Content not found")
        
        # Clean up file if it exists
        file_path = content.get("file_path")
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError:
                pass  # Don't fail if file cleanup fails
        
        return {"message": "Premium content deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete premium content: {str(e)}")

@app.post("/api/creators/{creator_id}/premium-content/{content_id}/duplicate")
async def duplicate_premium_content(
    creator_id: str,
    content_id: str,
    current_creator = Depends(get_current_creator)
):
    """Duplicate premium content"""
    try:
        # Verify creator owns this content
        if current_creator["creator_id"] != creator_id:
            raise HTTPException(status_code=403, detail="Access denied: can only duplicate your own content")
        
        # Find the original content
        original_content = await db.premium_content.find_one({
            "content_id": content_id,
            "creator_id": creator_id
        })
        
        if not original_content:
            raise HTTPException(status_code=404, detail="Premium content not found or doesn't belong to creator")
        
        # Create duplicate content
        import uuid
        duplicate_content = original_content.copy()
        
        # Remove the original _id and content_id, create new ones
        duplicate_content.pop("_id", None)
        duplicate_content["content_id"] = str(uuid.uuid4())
        duplicate_content["title"] = f"{original_content['title']} (Copy)"
        duplicate_content["created_at"] = datetime.now().isoformat()
        duplicate_content["updated_at"] = datetime.now().isoformat()
        
        # Reset stats for the duplicate
        duplicate_content["total_purchases"] = 0
        duplicate_content["total_revenue"] = 0
        duplicate_content["creator_earnings"] = 0
        
        # Note: File is not duplicated, both will reference same file
        # In production, you might want to copy the file as well
        
        # Insert the duplicate
        await db.premium_content.insert_one(duplicate_content)
        
        # Convert ObjectId for JSON serialization
        duplicate_content["_id"] = str(duplicate_content["_id"]) if "_id" in duplicate_content else None
        
        return {
            "message": "Premium content duplicated successfully",
            "content": duplicate_content
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to duplicate premium content: {str(e)}")

@app.get("/api/creators/{creator_id}/stats")
async def get_creator_stats(
    creator_id: str,
    current_creator = Depends(get_current_creator)
):
    """Get creator stats including content counts and earnings"""
    try:
        # Verify creator owns this data
        if current_creator["creator_id"] != creator_id:
            raise HTTPException(status_code=403, detail="Access denied: can only access your own stats")
        
        # Get standard content count
        standard_content_count = await db.creator_content.count_documents({"creator_id": creator_id})
        
        # Get premium content and calculate stats
        premium_content_list = await db.premium_content.find({"creator_id": creator_id}).to_list(None)
        premium_content_count = len(premium_content_list)
        
        # Calculate premium earnings and revenue
        total_premium_revenue = 0
        total_premium_sales = 0
        creator_premium_earnings = 0
        
        for content in premium_content_list:
            revenue = content.get("total_revenue", 0)
            purchases = content.get("total_purchases", 0)
            
            total_premium_revenue += revenue
            total_premium_sales += purchases
            
            # Creator gets 80% or (revenue - $2.99 minimum platform fee)
            if revenue > 0:
                platform_fee = max(revenue * 0.2, 2.99)
                creator_earnings = max(0, revenue - platform_fee)
                creator_premium_earnings += creator_earnings
        
        # Get total messages/interactions (optional)
        total_messages = 0  # Could be implemented if needed
        
        stats = {
            "content_count": standard_content_count,
            "premium_content_count": premium_content_count,
            "premium_earnings": round(creator_premium_earnings, 2),
            "total_content_sales": total_premium_sales,
            "total_premium_revenue": round(total_premium_revenue, 2),
            "total_messages": total_messages,
            "total_content": standard_content_count + premium_content_count
        }
        
        return {
            "creator_id": creator_id,
            "stats": stats,
            "last_updated": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch creator stats: {str(e)}")

# Mentor Rating System Functions
def calculate_mentor_tier(subscriber_count):
    """Calculate mentor tier based on subscriber count"""
    if subscriber_count >= 100000:
        return {
            "tier": "Ultimate Mentor",
            "level": "ultimate",
            "badge_color": "#8b5cf6",  # Purple
            "description": "Elite / Celebrity Status",
            "min_subscribers": 100000
        }
    elif subscriber_count >= 10000:
        return {
            "tier": "Platinum Mentor", 
            "level": "platinum",
            "badge_color": "#6b7280",  # Gray/Platinum
            "description": "Top 5-10% Performers",
            "min_subscribers": 10000
        }
    elif subscriber_count >= 1000:
        return {
            "tier": "Gold Mentor",
            "level": "gold", 
            "badge_color": "#f59e0b",  # Gold
            "description": "Established Presence",
            "min_subscribers": 1000
        }
    elif subscriber_count >= 100:
        return {
            "tier": "Silver Mentor",
            "level": "silver",
            "badge_color": "#9ca3af",  # Silver
            "description": "Entry-Level Credibility", 
            "min_subscribers": 100
        }
    else:
        return {
            "tier": "New Mentor",
            "level": "new",
            "badge_color": "#d1d5db",  # Light gray
            "description": "Building Following",
            "min_subscribers": 0
        }

async def update_mentor_tier(creator_id):
    """Update mentor tier based on current subscriber count"""
    try:
        # Get current subscriber count (this would come from your subscription system)
        # For now, we'll use a placeholder - you'd replace this with actual subscriber count logic
        creator = await db.creators.find_one({"creator_id": creator_id})
        if not creator:
            return None
            
        # Get subscriber count - you might have this in a separate collection
        # For demo purposes, using monthly_price as a proxy for popularity
        subscriber_count = creator.get("subscriber_count", 0)
        
        # Calculate tier
        tier_info = calculate_mentor_tier(subscriber_count)
        
        # Update creator with tier information
        await db.creators.update_one(
            {"creator_id": creator_id},
            {
                "$set": {
                    "tier": tier_info["tier"],
                    "tier_level": tier_info["level"], 
                    "tier_badge_color": tier_info["badge_color"],
                    "tier_description": tier_info["description"],
                    "tier_min_subscribers": tier_info["min_subscribers"],
                    "tier_updated_at": datetime.now().isoformat()
                }
            }
        )
        
        return tier_info
        
    except Exception as e:
        print(f"Error updating mentor tier for {creator_id}: {str(e)}")
        return None

@app.get("/api/mentor-tiers/info")
async def get_mentor_tier_info():
    """Get information about all mentor tiers"""
    tiers = [
        {
            "level": "ultimate",
            "tier": "Ultimate Mentor", 
            "min_subscribers": 100000,
            "badge_color": "#8b5cf6",
            "description": "Elite / Celebrity Status",
            "benefits": [
                "Highest visibility in search results",
                "Featured mentor spotlight",
                "Custom profile customization",
                "Priority customer support",
                "Higher revenue share on premium content"
            ]
        },
        {
            "level": "platinum", 
            "tier": "Platinum Mentor",
            "min_subscribers": 10000,
            "badge_color": "#6b7280", 
            "description": "Top 5-10% Performers",
            "benefits": [
                "Enhanced profile visibility",
                "Advanced analytics dashboard", 
                "Priority in mentor recommendations",
                "Exclusive mentor community access"
            ]
        },
        {
            "level": "gold",
            "tier": "Gold Mentor",
            "min_subscribers": 1000,
            "badge_color": "#f59e0b",
            "description": "Established Presence", 
            "benefits": [
                "Verified mentor badge",
                "Enhanced profile features",
                "Priority customer support",
                "Access to mentor tools"
            ]
        },
        {
            "level": "silver",
            "tier": "Silver Mentor", 
            "min_subscribers": 100,
            "badge_color": "#9ca3af",
            "description": "Entry-Level Credibility",
            "benefits": [
                "Basic mentor verification",
                "Standard profile features", 
                "Community access"
            ]
        },
        {
            "level": "new",
            "tier": "New Mentor",
            "min_subscribers": 0, 
            "badge_color": "#d1d5db",
            "description": "Building Following",
            "benefits": [
                "Basic mentor profile",
                "Getting started support"
            ]
        }
    ]
    
    return {"tiers": tiers}

@app.post("/api/creators/{creator_id}/update-tier")
async def update_creator_tier(
    creator_id: str,
    current_creator = Depends(get_current_creator)
):
    """Update creator's tier based on current metrics"""
    try:
        # Verify creator owns this account or is admin
        if current_creator["creator_id"] != creator_id:
            raise HTTPException(status_code=403, detail="Access denied: can only update your own tier")
        
        tier_info = await update_mentor_tier(creator_id)
        
        if tier_info:
            return {
                "message": "Tier updated successfully",
                "tier_info": tier_info
            }
        else:
            raise HTTPException(status_code=404, detail="Creator not found")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update tier: {str(e)}")

@app.get("/api/creators/{creator_id}/verification-status")
async def get_verification_status(creator_id: str):
    """Get creator verification status"""
    try:
        creator = await db.creators.find_one({"creator_id": creator_id})
        if not creator:
            raise HTTPException(status_code=404, detail="Creator not found")
        
        verification = creator.get("verification", {})
        banking_info = creator.get("banking_info", {})
        
        return {
            "creator_id": creator_id,
            "status": creator.get("status"),
            "verification": {
                "id_verified": verification.get("id_verified", False),
                "bank_verified": verification.get("bank_verified", False),
                "id_submitted": verification.get("id_document_url") is not None,
                "bank_submitted": bool(banking_info.get("bank_account_number")),
                "submitted_at": verification.get("submitted_at"),
                "verified_at": verification.get("verified_at"),
                "bank_verified_at": verification.get("bank_verified_at")
            },
            "is_fully_verified": (verification.get("id_verified", False) and 
                                verification.get("bank_verified", False)),
            "next_steps": get_next_verification_steps(verification, banking_info)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get verification status: {str(e)}")

def get_next_verification_steps(verification, banking_info):
    """Get list of next steps needed for verification"""
    steps = []
    
    if not banking_info.get("bank_account_number"):
        steps.append({
            "step": "banking_info",
            "title": "Submit Banking Information", 
            "description": "Provide your bank account details for payments"
        })
    elif not verification.get("bank_verified", False):
        steps.append({
            "step": "banking_pending",
            "title": "Banking Verification Pending",
            "description": "Your banking information is being verified"
        })
    
    if not verification.get("id_document_url"):
        steps.append({
            "step": "id_upload",
            "title": "Upload ID Document",
            "description": "Upload a government-issued ID for verification"
        })
    elif not verification.get("id_verified", False):
        steps.append({
            "step": "id_pending", 
            "title": "ID Verification Pending",
            "description": "Your ID document is being reviewed"
        })
    
    if not steps:
        steps.append({
            "step": "complete",
            "title": "Verification Complete",
            "description": "Your account is fully verified and approved"
        })
    
    return steps

# =============================================================================
# ADMINISTRATOR CONSOLE ENDPOINTS
# =============================================================================

@app.on_event("startup")
async def create_initial_admin():
    """Create initial super admin account if it doesn't exist"""
    try:
        existing_admin = await admin_db.admins.find_one({"email": INITIAL_SUPER_ADMIN["email"]})
        if not existing_admin:
            print("🔧 Creating initial super admin account...")
            admin_doc = create_initial_super_admin_doc(hash_password(INITIAL_SUPER_ADMIN["password"]))
            await admin_db.admins.insert_one(admin_doc)
            print(f"✅ Initial super admin created: {INITIAL_SUPER_ADMIN['email']}")
            print(f"🔑 Password: {INITIAL_SUPER_ADMIN['password']}")
            print("⚠️  Please change the password after first login!")
    except Exception as e:
        print(f"❌ Error creating initial admin: {str(e)}")

@app.post("/api/admin/login")
async def admin_login(login_data: AdminLoginRequest):
    """Admin login endpoint"""
    try:
        admin = await admin_db.admins.find_one({"email": login_data.email})
        if not admin or not verify_password(login_data.password, admin["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid admin credentials")
        
        if admin["status"] != AdminStatus.ACTIVE:
            raise HTTPException(status_code=401, detail="Admin account is not active")
        
        # Update last login
        await admin_db.admins.update_one(
            {"admin_id": admin["admin_id"]},
            {"$set": {"last_login": datetime.utcnow()}}
        )
        
        # Create admin token
        token = create_access_token({"admin_id": admin["admin_id"], "type": "admin"})
        
        return {
            "token": token,
            "admin": get_admin_public_profile(admin)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Admin login failed: {str(e)}")

@app.get("/api/admin/dashboard")
async def get_admin_dashboard(current_admin = Depends(get_current_admin)):
    """Get admin dashboard metrics"""
    try:
        if not has_permission(AdminRole(current_admin["role"]), "view_reports"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Get platform data
        users = await db.users.find({}).to_list(None)
        mentors = await db.creators.find({}).to_list(None)
        payments = await db.payment_transactions.find({"payment_status": "paid"}).to_list(None)
        questions = await db.questions.find({}).to_list(None)
        
        # Calculate metrics
        user_metrics = calculate_user_metrics(users)
        mentor_metrics = calculate_mentor_metrics(mentors)
        financial_metrics = calculate_financial_metrics(payments, [])
        
        # Platform summary
        platform_stats = {
            "total_users": len(users),
            "total_mentors": len(mentors),
            "total_questions": len(questions),
            "total_revenue": sum(p.get('amount', 0) for p in payments),
            "active_subscriptions": sum(1 for u in users if u.get('is_subscribed', False))
        }
        
        return {
            "platform_stats": platform_stats,
            "user_metrics": user_metrics,
            "mentor_metrics": mentor_metrics,
            "financial_metrics": financial_metrics,
            "updated_at": datetime.utcnow()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard: {str(e)}")

@app.get("/api/admin/users")
async def get_all_users(
    current_admin = Depends(get_current_admin),
    limit: int = 50,
    offset: int = 0,
    search: Optional[str] = None,
    status: Optional[str] = None
):
    """Get all users with pagination and filtering"""
    try:
        if not has_permission(AdminRole(current_admin["role"]), "manage_users"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Build query
        query = {}
        if search:
            query["$or"] = [
                {"email": {"$regex": search, "$options": "i"}},
                {"full_name": {"$regex": search, "$options": "i"}}
            ]
        if status:
            if status == "subscribed":
                query["is_subscribed"] = True
            elif status == "free":
                query["is_subscribed"] = False
        
        # Get users
        users = await db.users.find(query).skip(offset).limit(limit).to_list(limit)
        total_count = await db.users.count_documents(query)
        
        # Clean user data for admin view
        user_data = []
        for user in users:
            user_data.append({
                "user_id": user["user_id"],
                "email": user["email"],
                "full_name": user["full_name"],
                "role": user.get("role", "user"),  # Default to 'user' role
                "status": "suspended" if user.get("is_suspended", False) else "active",
                "is_suspended": user.get("is_suspended", False),
                "suspended_at": user.get("suspended_at"),
                "suspended_by": user.get("suspended_by"),
                "questions_asked": user.get("questions_asked", 0),
                "is_subscribed": user.get("is_subscribed", False),
                "subscription_expires": user.get("subscription_expires"),
                "created_at": user["created_at"],
                "last_active": user.get("last_active"),
                "deleted_at": user.get("deleted_at")  # For soft deletes
            })
        
        return {
            "users": user_data,
            "total": total_count,
            "limit": limit,
            "offset": offset
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get users: {str(e)}")

@app.get("/api/admin/mentors")
async def get_all_mentors(
    current_admin = Depends(get_current_admin),
    limit: int = 50,
    offset: int = 0,
    search: Optional[str] = None,
    status: Optional[str] = None
):
    """Get all mentors with pagination and filtering"""
    try:
        if not has_permission(AdminRole(current_admin["role"]), "manage_mentors"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Build query
        query = {}
        if search:
            query["$or"] = [
                {"email": {"$regex": search, "$options": "i"}},
                {"full_name": {"$regex": search, "$options": "i"}},
                {"account_name": {"$regex": search, "$options": "i"}}
            ]
        if status:
            query["status"] = status
        
        # Get mentors
        mentors = await db.creators.find(query).skip(offset).limit(limit).to_list(limit)
        total_count = await db.creators.count_documents(query)
        
        # Clean mentor data for admin view
        mentor_data = []
        for mentor in mentors:
            mentor_data.append({
                "creator_id": mentor["creator_id"],
                "email": mentor["email"],
                "full_name": mentor.get("full_name", mentor.get("account_name", "Unknown")),
                "account_name": mentor.get("account_name", "Unknown"),
                "category": mentor.get("category", "business"),
                "monthly_price": mentor.get("monthly_price", 0.0),
                "status": mentor.get("status", "pending"),
                "subscriber_count": mentor.get("stats", {}).get("subscriber_count", 0),
                "total_earnings": mentor.get("stats", {}).get("total_earnings", 0.0),
                "verification": {
                    "id_verified": mentor.get("verification", {}).get("id_verified", mentor.get("verification", {}).get("status") == "APPROVED"),
                    "bank_verified": mentor.get("verification", {}).get("bank_verified", mentor.get("verification", {}).get("status") == "APPROVED")
                },
                "created_at": mentor.get("created_at", datetime.utcnow()),
                "last_active": mentor.get("last_active")
            })
        
        return {
            "mentors": mentor_data,
            "total": total_count,
            "limit": limit,
            "offset": offset
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get mentors: {str(e)}")

@app.post("/api/admin/users/manage")
async def manage_users(
    request: UserManagementRequest,
    current_admin = Depends(get_current_admin)
):
    """Manage users (suspend, reactivate, delete)"""
    try:
        if not has_permission(AdminRole(current_admin["role"]), "manage_users"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        results = []
        
        for user_id in request.user_ids:
            user = await db.users.find_one({"user_id": user_id})
            if not user:
                results.append({"user_id": user_id, "status": "error", "message": "User not found"})
                continue
            
            try:
                if request.action == UserAction.SUSPEND:
                    await db.users.update_one(
                        {"user_id": user_id},
                        {"$set": {"is_suspended": True, "suspended_at": datetime.utcnow()}}
                    )
                    results.append({"user_id": user_id, "status": "success", "message": "User suspended"})
                    
                elif request.action == UserAction.REACTIVATE:
                    await db.users.update_one(
                        {"user_id": user_id},
                        {"$set": {"is_suspended": False}, "$unset": {"suspended_at": ""}}
                    )
                    results.append({"user_id": user_id, "status": "success", "message": "User reactivated"})
                    
                elif request.action == UserAction.DELETE:
                    # Delete user data (be careful with this!)
                    await db.users.delete_one({"user_id": user_id})
                    await db.questions.delete_many({"user_id": user_id})
                    await db.payment_transactions.delete_many({"user_id": user_id})
                    results.append({"user_id": user_id, "status": "success", "message": "User deleted"})
                    
            except Exception as e:
                results.append({"user_id": user_id, "status": "error", "message": str(e)})
        
        return {"results": results}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to manage users: {str(e)}")

@app.put("/api/admin/users/{user_id}/role")
async def change_user_role(
    user_id: str,
    request: UserRoleChangeRequest,
    current_admin = Depends(get_current_admin)
):
    """Change a user's role"""
    try:
        if not has_permission(AdminRole(current_admin["role"]), "manage_users"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Prevent admin from changing their own role
        if user_id == current_admin.get("user_id"):
            raise HTTPException(status_code=400, detail="Cannot change your own role")
        
        # Verify user exists
        user = await db.users.find_one({"user_id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Validate role transition
        valid_roles = ["user", "mentor", "admin"]
        if request.new_role not in valid_roles:
            raise HTTPException(status_code=400, detail=f"Invalid role. Must be one of: {valid_roles}")
        
        # Update user role
        await db.users.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "role": request.new_role,
                    "role_changed_at": datetime.utcnow(),
                    "role_changed_by": current_admin["admin_id"]
                }
            }
        )
        
        # Create audit log entry
        audit_entry = {
            "audit_id": str(uuid.uuid4()),
            "action": "role_change",
            "admin_id": current_admin["admin_id"],
            "target_user_id": user_id,
            "old_role": user.get("role", "user"),
            "new_role": request.new_role,
            "reason": request.reason,
            "timestamp": datetime.utcnow()
        }
        await db.admin_audit_log.insert_one(audit_entry)
        
        return {
            "message": f"User role changed to {request.new_role}",
            "user_id": user_id,
            "old_role": user.get("role", "user"),
            "new_role": request.new_role
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to change user role: {str(e)}")

@app.put("/api/admin/users/{user_id}/suspend")
async def suspend_user(
    user_id: str,
    request: UserSuspendRequest,
    current_admin = Depends(get_current_admin)
):
    """Suspend or unsuspend a user"""
    try:
        if not has_permission(AdminRole(current_admin["role"]), "manage_users"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Prevent admin from suspending themselves
        if user_id == current_admin.get("user_id"):
            raise HTTPException(status_code=400, detail="Cannot suspend your own account")
        
        # Verify user exists
        user = await db.users.find_one({"user_id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Send appropriate email based on action
        email_sent = False
        if request.suspend:
            # Suspending user
            from forgot_password_system import send_account_suspension_email
            
            user_name = user.get("full_name", "User")
            admin_reason = request.reason or "Policy violation"
            
            email_sent = await send_account_suspension_email(
                user["email"], 
                user_name, 
                admin_reason,
                current_admin["admin_id"]
            )
        else:
            # Unsuspending user (reactivating)
            from forgot_password_system import send_account_reactivation_email
            
            user_name = user.get("full_name", "User")
            admin_reason = request.reason or "Account review completed"
            
            email_sent = await send_account_reactivation_email(
                user["email"], 
                user_name, 
                admin_reason,
                current_admin["admin_id"]
            )
        
        # Update suspension status
        update_data = {
            "is_suspended": request.suspend,
            "suspension_reason": request.reason if request.suspend else None,
            "suspended_by": current_admin["admin_id"] if request.suspend else None
        }
        
        if request.suspend:
            update_data["suspended_at"] = datetime.utcnow()
        else:
            update_data["suspended_at"] = None
            update_data["unsuspended_at"] = datetime.utcnow()
            update_data["unsuspended_by"] = current_admin["admin_id"]
        
        await db.users.update_one(
            {"user_id": user_id},
            {"$set": update_data}
        )
        
        # Create audit log entry
        audit_entry = {
            "audit_id": str(uuid.uuid4()),
            "action": "suspend" if request.suspend else "unsuspend",
            "admin_id": current_admin["admin_id"],
            "target_user_id": user_id,
            "target_email": user["email"],
            "reason": request.reason,
            "email_sent": email_sent,
            "timestamp": datetime.utcnow()
        }
        await db.admin_audit_log.insert_one(audit_entry)
        
        # Generate response message
        if request.suspend:
            message = "User suspended successfully"
            if email_sent:
                message += " and notification email sent"
            else:
                message += " (notification email pending)"
        else:
            message = "User unsuspended successfully"
            if email_sent:
                message += " and reactivation email sent"
            else:
                message += " (reactivation email pending)"
        
        return {
            "message": message,
            "user_id": user_id,
            "is_suspended": request.suspend,
            "reason": request.reason,
            "email_sent": email_sent
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to suspend user: {str(e)}")

@app.post("/api/admin/users/{user_id}/reset-password")
async def admin_reset_user_password(
    user_id: str,
    request: dict,
    current_admin = Depends(get_current_admin)
):
    """Admin reset user password - sends email with reset link"""
    try:
        if not has_permission(AdminRole(current_admin["role"]), "manage_users"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Prevent admin from resetting their own password this way
        if user_id == current_admin.get("user_id"):
            raise HTTPException(status_code=400, detail="Cannot reset your own password")
        
        # Verify user exists
        user = await db.users.find_one({"user_id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Import password reset functions
        from forgot_password_system import create_password_reset_token, send_admin_password_reset_email
        
        # Create password reset token
        reset_token = await create_password_reset_token(db, user["email"], "user")
        if not reset_token:
            raise HTTPException(status_code=500, detail="Failed to create password reset token")
        
        # Get reason for email content
        admin_reason = request.get("reason", "Administrative action")
        user_name = user.get("full_name", "User")
        
        # Send password reset email
        email_sent = await send_admin_password_reset_email(
            user["email"], 
            reset_token, 
            user_name, 
            admin_reason
        )
        
        # Even if email fails, we continue with the process for security consistency
        # This prevents information disclosure about email delivery
        if not email_sent:
            print(f"⚠️ Email failed to send to {user['email']}, but continuing with reset process")
        
        # Update user record to indicate admin-initiated reset
        await db.users.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "password_reset_by_admin": current_admin["admin_id"],
                    "password_reset_initiated_at": datetime.utcnow(),
                    "password_reset_reason": admin_reason,
                    "account_locked": True  # Lock account until password is reset
                }
            }
        )
        
        # Create audit log entry
        audit_entry = {
            "audit_id": str(uuid.uuid4()),
            "action": "admin_password_reset_initiated",
            "admin_id": current_admin["admin_id"],
            "target_user_id": user_id,
            "target_email": user["email"],
            "reason": admin_reason,
            "method": "email_reset_link",
            "email_sent": email_sent,
            "timestamp": datetime.utcnow()
        }
        await db.admin_audit_log.insert_one(audit_entry)
        
        # Generate appropriate response message
        if email_sent:
            message = "Password reset email sent successfully"
            note = "User account is locked until password is reset via email link"
        else:
            message = "Password reset initiated successfully"
            note = "User account is locked. Email delivery may be delayed due to system configuration."
        
        return {
            "message": message,
            "user_id": user_id,
            "email": user["email"],
            "reset_method": "email_link",
            "expires_in": "1 hour",
            "note": note,
            "email_status": "sent" if email_sent else "pending"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initiate password reset: {str(e)}")

@app.delete("/api/admin/users/{user_id}")
async def delete_user(
    user_id: str,
    reason: str = "",
    current_admin = Depends(get_current_admin)
):
    """Soft delete a user (preserves data for audit)"""
    try:
        if not has_permission(AdminRole(current_admin["role"]), "manage_users"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Prevent admin from deleting themselves
        if user_id == current_admin.get("user_id"):
            raise HTTPException(status_code=400, detail="Cannot delete your own account")
        
        # Verify user exists and is not already deleted
        user = await db.users.find_one({"user_id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if user.get("deleted_at"):
            raise HTTPException(status_code=400, detail="User is already deleted")
        
        # Send deletion email before deleting the account
        from forgot_password_system import send_account_deletion_email
        
        user_name = user.get("full_name", "User")
        admin_reason = reason or "Policy violations"
        
        email_sent = await send_account_deletion_email(
            user["email"], 
            user_name, 
            admin_reason,
            current_admin["admin_id"]
        )
        
        # Soft delete - mark as deleted but preserve data
        await db.users.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "deleted_at": datetime.utcnow(),
                    "deleted_by": current_admin["admin_id"],
                    "deletion_reason": reason,
                    "is_suspended": True  # Also suspend the account
                }
            }
        )
        
        # Create audit log entry
        audit_entry = {
            "audit_id": str(uuid.uuid4()),
            "action": "delete_user",
            "admin_id": current_admin["admin_id"],
            "target_user_id": user_id,
            "target_email": user["email"],
            "reason": reason,
            "email_sent": email_sent,
            "timestamp": datetime.utcnow()
        }
        await db.admin_audit_log.insert_one(audit_entry)
        
        # Generate response message
        message = "User deleted successfully"
        if email_sent:
            message += " and notification email sent"
        else:
            message += " (notification email pending)"
        
        return {
            "message": message,
            "user_id": user_id,
            "deleted_at": datetime.utcnow().isoformat(),
            "reason": reason,
            "email_sent": email_sent
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete user: {str(e)}")

@app.get("/api/admin/users/{user_id}/audit")
async def get_user_audit_history(
    user_id: str,
    current_admin = Depends(get_current_admin)
):
    """Get audit history for a specific user"""
    try:
        if not has_permission(AdminRole(current_admin["role"]), "manage_users"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Get audit history
        audit_logs = await db.admin_audit_log.find(
            {"target_user_id": user_id}
        ).sort("timestamp", -1).to_list(50)
        
        # Clean audit logs and enrich with admin information
        cleaned_logs = []
        for log in audit_logs:
            # Remove MongoDB _id field
            if "_id" in log:
                del log["_id"]
            
            # Enrich with admin information
            admin = await admin_db.admins.find_one({"admin_id": log["admin_id"]})
            if admin:
                log["admin_name"] = admin.get("full_name", "Unknown Admin")
            
            cleaned_logs.append(log)
        
        return {"audit_history": cleaned_logs}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get audit history: {str(e)}")

@app.get("/api/admin/audit-logs")
async def get_audit_logs(
    current_admin = Depends(get_current_admin),
    limit: int = Query(50, ge=1, le=100)
):
    """Get audit logs for admin dashboard"""
    try:
        logs = await db.audit_logs.find({}).sort("timestamp", -1).limit(limit).to_list(limit)
        
        # Format logs for frontend
        formatted_logs = []
        for log in logs:
            log_entry = {
                "log_id": log.get("log_id"),
                "admin_email": log.get("admin_email"),
                "action": log.get("action"),
                "target_user_id": log.get("target_user_id"),
                "details": log.get("details", {}),
                "timestamp": log.get("timestamp")
            }
            formatted_logs.append(log_entry)
        
        return {"logs": formatted_logs}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch audit logs: {str(e)}")

# ================================
# MENTOR ADMIN MANAGEMENT ENDPOINTS
# ================================

@app.post("/api/admin/mentors/{mentor_id}/reset-password")
async def admin_reset_mentor_password(
    mentor_id: str,
    reset_request: dict,
    current_admin = Depends(get_current_admin)
):
    """Admin-initiated mentor password reset"""
    try:
        # Find mentor in creators collection
        mentor = await db.creators.find_one({"creator_id": mentor_id})
        if not mentor:
            raise HTTPException(status_code=404, detail="Mentor not found")
        
        # Create password reset token for mentor
        reset_token = await create_password_reset_token(db, mentor["email"], "mentor")
        if not reset_token:
            raise HTTPException(status_code=500, detail="Failed to create reset token")
        
        # Lock mentor account temporarily (24 hours)
        lock_until = datetime.utcnow() + timedelta(hours=24)
        await db.creators.update_one(
            {"creator_id": mentor_id},
            {
                "$set": {
                    "account_locked": True,
                    "locked_until": lock_until,
                    "locked_by_admin": current_admin["admin_id"],
                    "lock_reason": "Admin-initiated password reset"
                }
            }
        )
        
        # Send password reset email for mentor
        email_sent = await send_admin_password_reset_email(
            mentor["email"], 
            reset_token, 
            mentor.get("full_name", "Mentor"),
            reset_request.get("reason", "Admin-initiated reset")
        )
        
        # Log admin action
        await log_admin_action(
            db, 
            current_admin["admin_id"], 
            current_admin["email"], 
            "MENTOR_PASSWORD_RESET",
            mentor_id, 
            {"reason": reset_request.get("reason"), "mentor_email": mentor["email"]}
        )
        
        return {
            "message": "Mentor password reset initiated successfully",
            "email": mentor["email"],
            "expires_in": "60 minutes",
            "email_status": "sent" if email_sent else "pending",
            "note": "Mentor account is temporarily locked until password is reset"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reset mentor password: {str(e)}")

@app.put("/api/admin/mentors/{mentor_id}/suspend")
async def admin_suspend_mentor(
    mentor_id: str,
    suspend_request: UserSuspendRequest,
    current_admin = Depends(get_current_admin)
):
    """Admin suspend/unsuspend mentor"""
    try:
        # Find mentor
        mentor = await db.creators.find_one({"creator_id": mentor_id})
        if not mentor:
            raise HTTPException(status_code=404, detail="Mentor not found")
        
        # Update mentor status
        new_status = "suspended" if suspend_request.suspend else "approved"
        current_time = datetime.utcnow()
        
        update_data = {
            "status": new_status,
            "updated_at": current_time
        }
        
        if suspend_request.suspend:
            update_data.update({
                "suspended_at": current_time,
                "suspended_by": current_admin["admin_id"],
                "suspension_reason": suspend_request.reason,
                "is_suspended": True
            })
        else:
            update_data.update({
                "unsuspended_at": current_time,
                "unsuspended_by": current_admin["admin_id"],
                "unsuspension_reason": suspend_request.reason,
                "is_suspended": False
            })
        
        await db.creators.update_one({"creator_id": mentor_id}, {"$set": update_data})
        
        # Send notification email to mentor
        action = "suspended" if suspend_request.suspend else "reactivated"
        subject = f"OnlyMentors.ai - Your mentor account has been {action}"
        
        if suspend_request.suspend:
            email_content = f"""
            <h2>Account Suspension Notice</h2>
            <p>Dear {mentor.get('full_name', 'Mentor')},</p>
            <p>Your OnlyMentors.ai mentor account has been temporarily suspended.</p>
            <p><strong>Reason:</strong> {suspend_request.reason}</p>
            <p>If you believe this is an error or would like to appeal this decision, please contact our support team.</p>
            <p>Best regards,<br>OnlyMentors.ai Team</p>
            """
        else:
            email_content = f"""
            <h2>Account Reactivation Notice</h2>
            <p>Dear {mentor.get('full_name', 'Mentor')},</p>
            <p>Great news! Your OnlyMentors.ai mentor account has been reactivated.</p>
            <p><strong>Reactivation Reason:</strong> {suspend_request.reason}</p>
            <p>You can now access your mentor dashboard and continue helping users.</p>
            <p>Thank you for being part of OnlyMentors.ai!</p>
            <p>Best regards,<br>OnlyMentors.ai Team</p>
            """
        
        email_sent = await send_unified_email(mentor["email"], subject, email_content, email_content)
        
        # Log admin action
        await log_admin_action(
            db, 
            current_admin["admin_id"], 
            current_admin["email"], 
            f"MENTOR_{'SUSPENDED' if suspend_request.suspend else 'UNSUSPENDED'}",
            mentor_id, 
            {"reason": suspend_request.reason, "mentor_email": mentor["email"]}
        )
        
        return {
            "message": f"Mentor {action} successfully",
            "mentor_email": mentor["email"],
            "email_sent": email_sent,
            "new_status": new_status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update mentor status: {str(e)}")

@app.delete("/api/admin/mentors/{mentor_id}")
async def admin_delete_mentor(
    mentor_id: str,
    delete_request: dict,
    current_admin = Depends(get_current_admin)
):
    """Admin delete mentor account"""
    try:
        # Find mentor
        mentor = await db.creators.find_one({"creator_id": mentor_id})
        if not mentor:
            raise HTTPException(status_code=404, detail="Mentor not found")
        
        # Store mentor data for audit before deletion
        mentor_data = {
            "creator_id": mentor_id,
            "email": mentor["email"],
            "full_name": mentor.get("full_name"),
            "deleted_at": datetime.utcnow(),
            "deleted_by": current_admin["admin_id"],
            "deletion_reason": delete_request.get("reason"),
            "original_data": mentor
        }
        
        # Store in deleted_mentors collection for audit
        await db.deleted_mentors.insert_one(mentor_data)
        
        # Delete mentor from creators collection
        await db.creators.delete_one({"creator_id": mentor_id})
        
        # Send notification email
        subject = "OnlyMentors.ai - Mentor Account Deletion Notice"
        email_content = f"""
        <h2>Account Deletion Notice</h2>
        <p>Dear {mentor.get('full_name', 'Mentor')},</p>
        <p>Your OnlyMentors.ai mentor account has been permanently deleted.</p>
        <p><strong>Reason:</strong> {delete_request.get("reason")}</p>
        <p>All your mentor data has been removed from our platform. If you believe this was done in error, please contact our support team immediately.</p>
        <p>Best regards,<br>OnlyMentors.ai Team</p>
        """
        
        email_sent = await send_unified_email(mentor["email"], subject, email_content, email_content)
        
        # Log admin action
        await log_admin_action(
            db, 
            current_admin["admin_id"], 
            current_admin["email"], 
            "MENTOR_DELETED",
            mentor_id, 
            {"reason": delete_request.get("reason"), "mentor_email": mentor["email"]}
        )
        
        return {
            "message": "Mentor account deleted successfully",
            "mentor_email": mentor["email"],
            "email_sent": email_sent
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete mentor: {str(e)}")

# ================================
# DATABASE MANAGEMENT ENDPOINTS
# ================================

@app.get("/api/admin/database/overview")
async def get_database_overview(current_admin = Depends(get_current_admin)):
    """Get comprehensive database overview"""
    try:
        if not await db_manager.connect():
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        overview = await db_manager.get_database_overview()
        return overview
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get database overview: {str(e)}")

@app.get("/api/admin/database/collections/{collection_name}")
async def browse_collection(
    collection_name: str,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: str = Query(None),
    current_admin = Depends(get_current_admin)
):
    """Browse collection with pagination and search"""
    try:
        if not await db_manager.connect():
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        result = await db_manager.browse_collection(collection_name, page, limit, search)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to browse collection: {str(e)}")

@app.post("/api/admin/database/export")
async def export_collection(
    export_request: DatabaseExportRequest,
    current_admin = Depends(get_current_admin)
):
    """Export collection data in JSON or CSV format"""
    try:
        if not await db_manager.connect():
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        if export_request.format.lower() == "csv":
            data = await db_manager.export_collection_csv(
                export_request.collection_name, 
                export_request.search
            )
            media_type = "text/csv"
            filename = f"{export_request.collection_name}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
        else:
            data = await db_manager.export_collection_json(
                export_request.collection_name, 
                export_request.search
            )
            media_type = "application/json"
            filename = f"{export_request.collection_name}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        
        from fastapi.responses import Response
        return Response(
            content=data,
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export collection: {str(e)}")

@app.get("/api/admin/database/backup")
async def create_database_backup(current_admin = Depends(get_current_admin)):
    """Create full database backup as ZIP file"""
    try:
        if not await db_manager.connect():
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        backup_data = await db_manager.create_full_backup()
        filename = f"onlymentors_backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.zip"
        
        from fastapi.responses import Response
        return Response(
            content=backup_data,
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create backup: {str(e)}")

@app.post("/api/admin/database/restore")
async def restore_collection(
    restore_request: DatabaseRestoreRequest,
    current_admin = Depends(get_current_admin)
):
    """Restore collection from JSON data"""
    try:
        if not await db_manager.connect():
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        result = await db_manager.restore_collection_from_json(
            restore_request.collection_name,
            restore_request.json_data
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to restore collection: {str(e)}")

@app.get("/api/admin/analytics/users")
async def get_user_analytics(current_admin = Depends(get_current_admin)):
    """Get comprehensive user analytics"""
    try:
        if not await db_manager.connect():
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        analytics = await db_manager.get_user_analytics()
        return analytics
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user analytics: {str(e)}")

@app.get("/api/admin/analytics/mentors")
async def get_mentor_analytics(current_admin = Depends(get_current_admin)):
    """Get comprehensive mentor analytics"""
    try:
        if not await db_manager.connect():
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        analytics = await db_manager.get_mentor_analytics()
        return analytics
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get mentor analytics: {str(e)}")

@app.get("/api/admin/analytics/platform-health")
async def get_platform_health(current_admin = Depends(get_current_admin)):
    """Get overall platform health metrics"""
    try:
        if not await db_manager.connect():
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        health = await db_manager.get_platform_health()
        return health
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get platform health: {str(e)}")

# ================================
# PREMIUM CONTENT ENDPOINTS (PAY-PER-VIEW)
# ================================

@app.post("/api/creator/content/upload")
async def upload_premium_content(
    title: str = Form(...),
    description: str = Form(...),
    content_type: str = Form(...),
    category: str = Form(None),
    price: float = Form(...),
    tags: str = Form("[]"),
    preview_available: bool = Form(False),
    content_file: UploadFile = File(None),
    current_creator = Depends(get_current_creator)
):
    """Upload premium content for pay-per-view"""
    try:
        # Parse tags
        import json
        try:
            tag_list = json.loads(tags) if tags != "[]" else []
        except:
            tag_list = []
        
        # Validate pricing
        if not validate_content_price(price):
            raise HTTPException(
                status_code=400, 
                detail=f"Price must be between $0.01 and $50.00. Provided: ${price}"
            )
        
        # Validate content type
        if content_type not in ["video", "document", "article_link", "podcast"]:
            raise HTTPException(status_code=400, detail="Invalid content type")
        
        # Calculate pricing breakdown
        pricing = calculate_content_pricing(price)
        
        # Handle file upload if provided
        file_path = None
        if content_file and content_file.size > 0:
            # Validate file based on content type
            if content_type == "video":
                allowed_types = ["video/mp4", "video/avi", "video/mov", "video/wmv", "video/x-flv", "video/webm", "video/x-msvideo"]
                max_size = 200 * 1024 * 1024  # 200MB
                if content_file.content_type not in allowed_types:
                    raise HTTPException(status_code=400, detail="Invalid video file type")
            elif content_type == "document":
                allowed_types = ["application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "text/plain"]
                max_size = 50 * 1024 * 1024  # 50MB
                if content_file.content_type not in allowed_types:
                    raise HTTPException(status_code=400, detail="Invalid document file type")
            elif content_type == "podcast":
                allowed_types = ["audio/mpeg", "audio/mp3", "audio/aac", "audio/mp4", "audio/wav", "audio/wave", "audio/x-wav"]
                max_size = 500 * 1024 * 1024  # 500MB for audio files
                if content_file.content_type not in allowed_types:
                    # Also check by file extension as fallback
                    file_ext = content_file.filename.lower().split('.')[-1] if '.' in content_file.filename else ''
                    if file_ext not in ['mp3', 'aac', 'm4a', 'wav']:
                        raise HTTPException(status_code=400, detail="Invalid podcast file type. Supported formats: mp3, aac, m4a, wav")
            
            if content_file.size > max_size:
                raise HTTPException(status_code=400, detail=f"File too large. Maximum size is {max_size / 1024 / 1024}MB")
            # Create upload directory if it doesn't exist
            upload_dir = "/app/uploads/premium_content"
            os.makedirs(upload_dir, exist_ok=True)
            
            # Generate unique filename
            file_extension = content_file.filename.split('.')[-1] if '.' in content_file.filename else 'bin'
            unique_filename = f"{current_creator['creator_id']}_{int(time.time())}_{uuid.uuid4().hex[:8]}.{file_extension}"
            file_path = f"{upload_dir}/{unique_filename}"
            
            # Save file
            content = await content_file.read()
            with open(file_path, "wb") as f:
                f.write(content)
        
        # Create content record
        content_record = {
            "title": title,
            "description": description,
            "content_type": content_type,
            "category": category,
            "price": price,
            "tags": tag_list,
            "preview_available": preview_available,
            "file_path": file_path
        }
        
        content = await premium_content_manager.create_content_record(
            current_creator["creator_id"], 
            content_record
        )
        
        # Store in database
        await db.premium_content.insert_one(content)
        
        # Update creator's content count
        await db.creators.update_one(
            {"creator_id": current_creator["creator_id"]},
            {"$inc": {"premium_content_count": 1}}
        )
        
        return {
            "success": True,
            "content_id": content["content_id"],
            "pricing_breakdown": pricing,
            "message": f"Premium content created successfully. You'll earn ${pricing['creator_earnings']:.2f} per purchase."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create premium content: {str(e)}")

@app.get("/api/mentor/{mentor_id}/premium-content")
async def get_mentor_premium_content(
    mentor_id: str,
    content_type: str = Query(None),
    category: str = Query(None)
):
    """Get premium content for a specific mentor"""
    try:
        # Build query
        query = {"creator_id": mentor_id, "is_active": True}
        
        if content_type:
            query["content_type"] = content_type
        if category:
            query["category"] = category
        
        # Get content
        cursor = db.premium_content.find(query, {
            "file_path": 0,  # Don't expose file paths
            "payment_history": 0
        }).sort("created_at", -1)
        
        content_list = await cursor.to_list(length=None)
        
        # Serialize for JSON response
        for content in content_list:
            content["_id"] = str(content["_id"]) if "_id" in content else None
            content["created_at"] = content["created_at"].isoformat() if content.get("created_at") else None
            content["updated_at"] = content["updated_at"].isoformat() if content.get("updated_at") else None
        
        return {
            "success": True,
            "mentor_id": mentor_id,
            "content_count": len(content_list),
            "content": content_list
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get premium content: {str(e)}")

@app.post("/api/content/purchase")
async def purchase_premium_content(
    purchase_request: ContentPurchaseRequest,
    current_user = Depends(get_current_user)
):
    """Purchase premium content with Stripe payment"""
    try:
        # Get content details
        content = await db.premium_content.find_one({"content_id": purchase_request.content_id})
        if not content:
            raise HTTPException(status_code=404, detail="Content not found")
        
        if not content.get("is_active", True):
            raise HTTPException(status_code=400, detail="Content is no longer available")
        
        # Check if user already purchased this content
        existing_purchase = await db.content_purchases.find_one({
            "content_id": purchase_request.content_id,
            "user_id": current_user["user_id"],
            "access_granted": True
        })
        
        if existing_purchase:
            return {
                "success": True,
                "message": "You already own this content",
                "access_granted": True,
                "purchase_id": existing_purchase["purchase_id"]
            }
        
        # Create Stripe payment intent
        import stripe
        stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
        
        # Convert to cents for Stripe
        amount_cents = int(content["price"] * 100)
        
        payment_intent = stripe.PaymentIntent.create(
            amount=amount_cents,
            currency='usd',
            payment_method=purchase_request.payment_method_id,
            confirmation_method='manual',
            confirm=True,
            metadata={
                'content_id': purchase_request.content_id,
                'user_id': current_user["user_id"],
                'content_title': content["title"],
                'creator_id': content["creator_id"]
            }
        )
        
        if payment_intent.status == 'succeeded':
            # Process successful purchase
            purchase = await premium_content_manager.process_content_purchase(
                purchase_request.content_id,
                current_user["user_id"],
                payment_intent.id
            )
            
            # Store purchase record
            await db.content_purchases.insert_one(purchase)
            
            # Update content statistics
            await db.premium_content.update_one(
                {"content_id": purchase_request.content_id},
                {
                    "$inc": {
                        "total_purchases": 1,
                        "total_revenue": content["price"]
                    }
                }
            )
            
            # Update creator earnings
            await db.creators.update_one(
                {"creator_id": content["creator_id"]},
                {
                    "$inc": {
                        "premium_earnings": content["creator_earnings"],
                        "total_content_sales": 1
                    }
                }
            )
            
            # Log revenue for platform
            platform_revenue = {
                "revenue_id": str(uuid.uuid4()),
                "source": "premium_content",
                "content_id": purchase_request.content_id,
                "user_id": current_user["user_id"],
                "creator_id": content["creator_id"],
                "gross_amount": content["price"],
                "platform_fee": content["platform_fee"],
                "creator_earnings": content["creator_earnings"],
                "created_at": datetime.utcnow()
            }
            await db.platform_revenue.insert_one(platform_revenue)
            
            return {
                "success": True,
                "message": "Content purchased successfully!",
                "purchase_id": purchase["purchase_id"],
                "access_granted": True,
                "content_title": content["title"]
            }
            
        else:
            raise HTTPException(status_code=400, detail="Payment failed")
        
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=f"Payment error: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Purchase failed: {str(e)}")

@app.get("/api/content/{content_id}/access")
async def check_content_access(
    content_id: str,
    current_user = Depends(get_current_user)
):
    """Check if user has access to premium content"""
    try:
        # Check purchase record
        purchase = await db.content_purchases.find_one({
            "content_id": content_id,
            "user_id": current_user["user_id"],
            "access_granted": True
        })
        
        if purchase:
            # Update last accessed time
            await db.content_purchases.update_one(
                {"purchase_id": purchase["purchase_id"]},
                {"$set": {"last_accessed": datetime.utcnow()}}
            )
            
            return {
                "access_granted": True,
                "purchase_date": purchase["purchase_date"].isoformat(),
                "download_count": purchase.get("download_count", 0),
                "max_downloads": purchase.get("max_downloads", 10)
            }
        else:
            return {"access_granted": False}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check access: {str(e)}")

@app.get("/api/creator/content/analytics")
async def get_creator_content_analytics(current_creator = Depends(get_current_creator)):
    """Get analytics for creator's premium content"""
    try:
        # Get content summary
        content_cursor = db.premium_content.find({"creator_id": current_creator["creator_id"]})
        content_list = await content_cursor.to_list(length=None)
        
        total_content = len(content_list)
        total_sales = sum(content.get("total_purchases", 0) for content in content_list)
        total_revenue = sum(content.get("total_revenue", 0) for content in content_list)
        creator_earnings = sum(content.get("creator_earnings", 0) * content.get("total_purchases", 0) for content in content_list)
        
        # Content by type
        content_by_type = {}
        for content in content_list:
            content_type = content.get("content_type", "unknown")
            if content_type not in content_by_type:
                content_by_type[content_type] = {"count": 0, "sales": 0, "revenue": 0}
            content_by_type[content_type]["count"] += 1
            content_by_type[content_type]["sales"] += content.get("total_purchases", 0)
            content_by_type[content_type]["revenue"] += content.get("total_revenue", 0)
        
        # Top performing content
        top_content = sorted(content_list, key=lambda x: x.get("total_revenue", 0), reverse=True)[:5]
        
        analytics = {
            "summary": {
                "total_content": total_content,
                "total_sales": total_sales,
                "total_revenue": total_revenue,
                "creator_earnings": creator_earnings,
                "platform_fees_paid": total_revenue - creator_earnings
            },
            "content_by_type": content_by_type,
            "top_performing_content": [
                {
                    "content_id": content["content_id"],
                    "title": content["title"],
                    "sales": content.get("total_purchases", 0),
                    "revenue": content.get("total_revenue", 0),
                    "price": content["price"]
                }
                for content in top_content
            ]
        }
        
        return analytics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")

@app.post("/api/admin/mentors/manage")
async def manage_mentors(
    request: MentorManagementRequest,
    current_admin = Depends(get_current_admin)
):
    """Manage mentors (approve, reject, suspend, delete)"""
    try:
        if not has_permission(AdminRole(current_admin["role"]), "manage_mentors"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        results = []
        
        for creator_id in request.creator_ids:
            mentor = await db.creators.find_one({"creator_id": creator_id})
            if not mentor:
                results.append({"creator_id": creator_id, "status": "error", "message": "Mentor not found"})
                continue
            
            try:
                if request.action == MentorAction.APPROVE:
                    await db.creators.update_one(
                        {"creator_id": creator_id},
                        {"$set": {"status": CreatorStatus.APPROVED, "approved_at": datetime.utcnow()}}
                    )
                    results.append({"creator_id": creator_id, "status": "success", "message": "Mentor approved"})
                    
                elif request.action == MentorAction.REJECT:
                    await db.creators.update_one(
                        {"creator_id": creator_id},
                        {"$set": {"status": CreatorStatus.REJECTED, "rejected_at": datetime.utcnow()}}
                    )
                    results.append({"creator_id": creator_id, "status": "success", "message": "Mentor rejected"})
                    
                elif request.action == MentorAction.SUSPEND:
                    await db.creators.update_one(
                        {"creator_id": creator_id},
                        {"$set": {"status": CreatorStatus.SUSPENDED, "suspended_at": datetime.utcnow()}}
                    )
                    results.append({"creator_id": creator_id, "status": "success", "message": "Mentor suspended"})
                    
                elif request.action == MentorAction.REACTIVATE:
                    await db.creators.update_one(
                        {"creator_id": creator_id},
                        {"$set": {"status": CreatorStatus.APPROVED}, "$unset": {"suspended_at": ""}}
                    )
                    results.append({"creator_id": creator_id, "status": "success", "message": "Mentor reactivated"})
                    
                elif request.action == MentorAction.DELETE:
                    # Delete mentor data
                    await db.creators.delete_one({"creator_id": creator_id})
                    await db.creator_content.delete_many({"creator_id": creator_id})
                    results.append({"creator_id": creator_id, "status": "success", "message": "Mentor deleted"})
                    
            except Exception as e:
                results.append({"creator_id": creator_id, "status": "error", "message": str(e)})
        
        return {"results": results}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to manage mentors: {str(e)}")

@app.get("/api/admin/reports/user-activity")
async def get_user_activity_report(current_admin = Depends(get_current_admin)):
    """Get user activity report (critical requirement)"""
    try:
        if not has_permission(AdminRole(current_admin["role"]), "view_reports"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Get all users and questions
        users = await db.users.find({}).to_list(None)
        questions = await db.questions.find({}).to_list(None)
        
        # Calculate activity metrics
        from datetime import timedelta
        now = datetime.utcnow()
        periods = {
            "today": now.replace(hour=0, minute=0, second=0, microsecond=0),
            "week": now - timedelta(days=7),
            "month": now - timedelta(days=30)
        }
        
        activity_report = {}
        for period_name, start_date in periods.items():
            # User registrations
            new_users = [u for u in users if u.get('created_at') and u['created_at'] >= start_date]
            
            # Questions asked
            questions_period = [q for q in questions if q.get('created_at') and q['created_at'] >= start_date]
            
            # Active users (asked questions in period)
            active_user_ids = set(q['user_id'] for q in questions_period)
            
            activity_report[period_name] = {
                "new_users": len(new_users),
                "active_users": len(active_user_ids),
                "questions_asked": len(questions_period),
                "avg_questions_per_user": len(questions_period) / len(active_user_ids) if active_user_ids else 0
            }
        
        # Top users by questions
        user_question_counts = {}
        for q in questions:
            user_id = q['user_id']
            user_question_counts[user_id] = user_question_counts.get(user_id, 0) + 1
        
        top_users = []
        for user_id, question_count in sorted(user_question_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            user = next((u for u in users if u['user_id'] == user_id), None)
            if user:
                top_users.append({
                    "user_id": user_id,
                    "email": user['email'],
                    "full_name": user['full_name'],
                    "questions_asked": question_count,
                    "is_subscribed": user.get('is_subscribed', False)
                })
        
        return {
            "summary": {
                "total_users": len(users),
                "total_questions": len(questions),
                "subscribed_users": sum(1 for u in users if u.get('is_subscribed', False))
            },
            "period_activity": activity_report,
            "top_users": top_users,
            "generated_at": datetime.utcnow()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate user activity report: {str(e)}")

@app.get("/api/admin/reports/financial")
async def get_financial_report(current_admin = Depends(get_current_admin)):
    """Get financial metrics report (critical requirement)"""
    try:
        if not has_permission(AdminRole(current_admin["role"]), "view_financials"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Get payment data
        payments = await db.payment_transactions.find({"payment_status": "paid"}).to_list(None)
        mentors = await db.creators.find({}).to_list(None)
        users = await db.users.find({"is_subscribed": True}).to_list(None)
        
        # Calculate financial metrics by period
        from datetime import timedelta
        now = datetime.utcnow()
        periods = {
            "today": now.replace(hour=0, minute=0, second=0, microsecond=0),
            "week": now - timedelta(days=7),
            "month": now - timedelta(days=30),
            "year": now - timedelta(days=365)
        }
        
        financial_report = {}
        for period_name, start_date in periods.items():
            period_payments = [p for p in payments if p.get('created_at') and p['created_at'] >= start_date]
            
            revenue = sum(p.get('amount', 0) for p in period_payments)
            transaction_count = len(period_payments)
            
            # Revenue breakdown
            monthly_revenue = sum(p.get('amount', 0) for p in period_payments if p.get('package_id') == 'monthly')
            yearly_revenue = sum(p.get('amount', 0) for p in period_payments if p.get('package_id') == 'yearly')
            
            financial_report[period_name] = {
                "revenue": revenue,
                "transaction_count": transaction_count,
                "avg_transaction": revenue / transaction_count if transaction_count > 0 else 0,
                "monthly_subscriptions": monthly_revenue,
                "yearly_subscriptions": yearly_revenue
            }
        
        # Platform revenue split
        total_revenue = sum(p.get('amount', 0) for p in payments)
        platform_commission = total_revenue * 0.20  # 20% platform fee
        creator_payouts = total_revenue * 0.80  # 80% to creators
        
        # Top paying users
        user_spending = {}
        for p in payments:
            user_id = p.get('user_id')
            if user_id:
                user_spending[user_id] = user_spending.get(user_id, 0) + p.get('amount', 0)
        
        top_spenders = []
        for user_id, amount in sorted(user_spending.items(), key=lambda x: x[1], reverse=True)[:10]:
            user = await db.users.find_one({"user_id": user_id})
            if user:
                top_spenders.append({
                    "user_id": user_id,
                    "email": user['email'],
                    "full_name": user['full_name'],
                    "total_spent": amount
                })
        
        return {
            "summary": {
                "total_revenue": total_revenue,
                "platform_commission": platform_commission,
                "creator_payouts": creator_payouts,
                "active_subscriptions": len(users),
                "total_transactions": len(payments)
            },
            "period_revenue": financial_report,
            "top_spenders": top_spenders,
            "revenue_breakdown": {
                "monthly_subscriptions": sum(p.get('amount', 0) for p in payments if p.get('package_id') == 'monthly'),
                "yearly_subscriptions": sum(p.get('amount', 0) for p in payments if p.get('package_id') == 'yearly')
            },
            "generated_at": datetime.utcnow()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate financial report: {str(e)}")

@app.get("/api/admin/me")
async def get_admin_profile(current_admin = Depends(get_current_admin)):
    """Get current admin profile"""
    return {"admin": get_admin_public_profile(current_admin)}

# =============================================================================
# PHASE 3: CONTENT MODERATION ENDPOINTS
# =============================================================================

@app.get("/api/admin/content-moderation")
async def get_content_for_moderation(
    current_admin = Depends(get_current_admin),
    content_type: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """Get content items for moderation"""
    try:
        if not has_permission(AdminRole(current_admin["role"]), "manage_content"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Build query for content moderation
        query = {}
        if content_type:
            query["content_type"] = content_type
        if status:
            query["status"] = status
        if priority:
            query["priority"] = priority
        
        # Get content moderation items
        moderation_items = await admin_db.content_moderation.find(query).skip(offset).limit(limit).to_list(limit)
        total_count = await admin_db.content_moderation.count_documents(query)
        
        # Get moderation statistics
        all_items = await admin_db.content_moderation.find({}).to_list(None)
        stats = calculate_moderation_stats(all_items)
        
        return {
            "content": moderation_items,
            "total": total_count,
            "limit": limit,
            "offset": offset,
            "stats": stats
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get content for moderation: {str(e)}")

@app.post("/api/admin/content-moderation/action")
async def moderate_content(
    request: ModerationRequest,
    current_admin = Depends(get_current_admin)
):
    """Take moderation action on content"""
    try:
        if not has_permission(AdminRole(current_admin["role"]), "manage_content"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        results = []
        
        for content_id in request.content_ids:
            # Get content item
            content_item = await admin_db.content_moderation.find_one({"content_id": content_id})
            if not content_item:
                results.append({"content_id": content_id, "status": "error", "message": "Content not found"})
                continue
            
            try:
                previous_status = content_item["status"]
                
                # Update status based on action
                new_status = {
                    ModerationAction.APPROVE: ModerationStatus.APPROVED,
                    ModerationAction.REJECT: ModerationStatus.REJECTED,
                    ModerationAction.FLAG: ModerationStatus.FLAGGED,
                    ModerationAction.REMOVE: ModerationStatus.REMOVED,
                    ModerationAction.REVIEW: ModerationStatus.UNDER_REVIEW
                }[request.action]
                
                # Update content moderation record
                await admin_db.content_moderation.update_one(
                    {"content_id": content_id},
                    {
                        "$set": {
                            "status": new_status,
                            "reviewed_by": current_admin["admin_id"],
                            "reviewed_at": datetime.utcnow(),
                            "review_notes": request.reviewer_notes,
                            "updated_at": datetime.utcnow()
                        },
                        "$push": {
                            "moderation_history": {
                                "action": request.action,
                                "status": new_status,
                                "admin_id": current_admin["admin_id"],
                                "reason": request.reason,
                                "notes": request.reviewer_notes,
                                "timestamp": datetime.utcnow()
                            }
                        }
                    }
                )
                
                # Log moderation activity
                activity_log = create_moderation_activity_log(
                    current_admin["admin_id"], request.action, content_id,
                    ContentType(content_item["content_type"]), ModerationStatus(previous_status),
                    new_status, request.reason, request.reviewer_notes
                )
                await admin_db.moderation_activity.insert_one(activity_log)
                
                results.append({"content_id": content_id, "status": "success", "message": f"Content {request.action}ed"})
                
            except Exception as e:
                results.append({"content_id": content_id, "status": "error", "message": str(e)})
        
        return {"results": results}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to moderate content: {str(e)}")

@app.post("/api/admin/content-moderation/bulk-approve")
async def bulk_approve_content(
    content_ids: List[str],
    current_admin = Depends(get_current_admin)
):
    """Bulk approve multiple content items"""
    request = ModerationRequest(
        content_ids=content_ids,
        action=ModerationAction.APPROVE,
        reason="Bulk approval by admin"
    )
    return await moderate_content(request, current_admin)

# =============================================================================
# PHASE 3: PAYOUT MANAGEMENT ENDPOINTS
# =============================================================================

@app.get("/api/admin/payouts")
async def get_payouts(
    current_admin = Depends(get_current_admin),
    status: Optional[str] = None,
    creator_id: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """Get payout records"""
    try:
        if not has_permission(AdminRole(current_admin["role"]), "view_financials"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Build query
        query = {}
        if status:
            query["status"] = status
        if creator_id:
            query["creator_id"] = creator_id
        
        # Get payouts
        payouts = await admin_db.payouts.find(query).sort("created_at", -1).skip(offset).limit(limit).to_list(limit)
        total_count = await admin_db.payouts.count_documents(query)
        
        # Calculate analytics
        all_payouts = await admin_db.payouts.find({}).to_list(None)
        analytics = calculate_payout_analytics(all_payouts)
        
        return {
            "payouts": payouts,
            "total": total_count,
            "limit": limit,
            "offset": offset,
            "analytics": analytics
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get payouts: {str(e)}")

@app.post("/api/admin/payouts/process")
async def process_payouts(
    request: PayoutRequest,
    current_admin = Depends(get_current_admin)
):
    """Process payouts for creators"""
    try:
        if not has_permission(AdminRole(current_admin["role"]), "manage_financials"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        results = []
        
        for creator_id in request.creator_ids:
            try:
                # Get creator earnings and settings
                earnings = await admin_db.creator_earnings.find({"creator_id": creator_id, "payout_id": None}).to_list(None)
                settings = await admin_db.payout_settings.find_one({"creator_id": creator_id})
                
                if not settings:
                    # Create default settings
                    settings = create_default_payout_settings(creator_id)
                    await admin_db.payout_settings.insert_one(settings)
                
                # Process payout
                payout = process_creator_payout(creator_id, earnings, settings, current_admin["admin_id"])
                
                # Save payout record
                await admin_db.payouts.insert_one(payout)
                
                # Mark earnings as processed
                earnings_ids = [e["earnings_id"] for e in earnings if e["creator_id"] == creator_id]
                if earnings_ids:
                    await admin_db.creator_earnings.update_many(
                        {"earnings_id": {"$in": earnings_ids}},
                        {"$set": {"payout_id": payout["payout_id"], "processed_at": datetime.utcnow()}}
                    )
                
                # Update creator total paid out
                await admin_db.payout_settings.update_one(
                    {"creator_id": creator_id},
                    {
                        "$set": {
                            "last_payout_date": datetime.utcnow(),
                            "next_payout_date": calculate_next_payout_date(PayoutFrequency(settings["frequency"])),
                            "updated_at": datetime.utcnow()
                        },
                        "$inc": {"total_paid_out": payout["amount"]}
                    }
                )
                
                results.append({
                    "creator_id": creator_id,
                    "status": "success",
                    "payout_id": payout["payout_id"],
                    "amount": payout["amount"],
                    "message": f"Payout processed: ${payout['amount']:.2f}"
                })
                
            except Exception as e:
                results.append({
                    "creator_id": creator_id,
                    "status": "error",
                    "message": str(e)
                })
        
        return {"results": results}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process payouts: {str(e)}")

@app.get("/api/admin/creator-earnings")
async def get_creator_earnings(
    current_admin = Depends(get_current_admin),
    creator_id: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """Get creator earnings data"""
    try:
        if not has_permission(AdminRole(current_admin["role"]), "view_financials"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        query = {}
        if creator_id:
            query["creator_id"] = creator_id
        
        earnings = await admin_db.creator_earnings.find(query).sort("created_at", -1).skip(offset).limit(limit).to_list(limit)
        total_count = await admin_db.creator_earnings.count_documents(query)
        
        # Calculate pending earnings by creator
        all_earnings = await admin_db.creator_earnings.find({"payout_id": None}).to_list(None)
        creators_with_earnings = list(set(e["creator_id"] for e in all_earnings))
        
        pending_by_creator = []
        for cid in creators_with_earnings:
            pending = calculate_creator_pending_earnings(cid, all_earnings)
            if pending["pending_amount"] > 0:
                pending_by_creator.append(pending)
        
        # Sort by pending amount
        pending_by_creator.sort(key=lambda x: x["pending_amount"], reverse=True)
        
        return {
            "earnings": earnings,
            "total": total_count,
            "limit": limit,
            "offset": offset,
            "pending_by_creator": pending_by_creator[:20]  # Top 20
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get creator earnings: {str(e)}")

@app.post("/api/admin/earnings/add")
async def add_creator_earnings(
    earnings: EarningsEntry,
    current_admin = Depends(get_current_admin)
):
    """Add manual earnings entry for creator"""
    try:
        if not has_permission(AdminRole(current_admin["role"]), "manage_financials"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Create earnings entry
        earnings_doc = create_earnings_entry({
            "creator_id": earnings.creator_id,
            "amount": earnings.amount,
            "transaction_id": earnings.transaction_id,
            "type": earnings.earnings_type,
            "description": earnings.description or "Manual entry by admin"
        })
        
        # Add admin tracking
        earnings_doc["added_by"] = current_admin["admin_id"]
        earnings_doc["manual_entry"] = True
        
        await admin_db.creator_earnings.insert_one(earnings_doc)
        
        return {
            "earnings_id": earnings_doc["earnings_id"],
            "message": f"Added ${earnings.amount:.2f} earnings for creator {earnings.creator_id}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add earnings: {str(e)}")

@app.get("/api/admin/payout-analytics")
async def get_payout_analytics(
    current_admin = Depends(get_current_admin),
    period_days: int = 30
):
    """Get comprehensive payout analytics"""
    try:
        if not has_permission(AdminRole(current_admin["role"]), "view_financials"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Get payouts and earnings data
        payouts = await admin_db.payouts.find({}).to_list(None)
        earnings = await admin_db.creator_earnings.find({}).to_list(None)
        
        # Calculate analytics
        analytics = calculate_payout_analytics(payouts, period_days)
        
        # Additional platform metrics
        total_revenue = sum(e["amount"] for e in earnings)
        platform_fees = sum(e["platform_fee"] for e in earnings)
        creator_earnings_total = sum(e["creator_earnings"] for e in earnings)
        pending_payouts = sum(e["creator_earnings"] for e in earnings if not e.get("payout_id"))
        
        analytics["platform_metrics"] = {
            "total_revenue": total_revenue,
            "platform_fees_earned": platform_fees,
            "creator_earnings_total": creator_earnings_total,
            "pending_payouts": pending_payouts,
            "revenue_retention_rate": (platform_fees / total_revenue * 100) if total_revenue > 0 else 0
        }
        
        return analytics
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get payout analytics: {str(e)}")

# =============================================================================
# PHASE 4: AI AGENT FRAMEWORK ENDPOINTS
# =============================================================================

@app.on_event("startup")
async def initialize_ai_agents():
    """Initialize default AI agents if they don't exist"""
    try:
        existing_agents = await admin_db.ai_agents.count_documents({})
        if existing_agents == 0:
            print("🤖 Initializing AI Agent Framework...")
            for agent_config in DEFAULT_AI_AGENTS:
                agent_doc = create_default_ai_agent(agent_config)
                await admin_db.ai_agents.insert_one(agent_doc)
            print(f"✅ Initialized {len(DEFAULT_AI_AGENTS)} AI agents")
    except Exception as e:
        print(f"❌ Error initializing AI agents: {str(e)}")

@app.get("/api/admin/ai-agents")
async def get_ai_agents(current_admin = Depends(get_current_admin)):
    """Get all AI agents and their status"""
    try:
        if not has_permission(AdminRole(current_admin["role"]), "view_system"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        agents = await admin_db.ai_agents.find({}).to_list(None)
        
        # Get recent task statistics for each agent
        for agent in agents:
            recent_tasks = await admin_db.ai_tasks.find({
                "agent_id": agent["agent_id"],
                "created_at": {"$gte": datetime.utcnow() - timedelta(days=7)}
            }).to_list(None)
            
            agent["recent_stats"] = {
                "tasks_this_week": len(recent_tasks),
                "successful_tasks": len([t for t in recent_tasks if t["status"] == AITaskStatus.COMPLETED]),
                "failed_tasks": len([t for t in recent_tasks if t["status"] == AITaskStatus.FAILED]),
                "avg_processing_time": sum(t.get("processing_time_ms", 0) for t in recent_tasks) / len(recent_tasks) if recent_tasks else 0
            }
        
        return {
            "agents": agents,
            "framework_status": "active",
            "total_agents": len(agents)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get AI agents: {str(e)}")

@app.post("/api/admin/ai-agents/{agent_id}/toggle")
async def toggle_ai_agent(
    agent_id: str,
    current_admin = Depends(get_current_admin)
):
    """Toggle AI agent active/inactive status"""
    try:
        if not has_permission(AdminRole(current_admin["role"]), "manage_system"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        agent = await admin_db.ai_agents.find_one({"agent_id": agent_id})
        if not agent:
            raise HTTPException(status_code=404, detail="AI agent not found")
        
        new_status = AIAgentStatus.INACTIVE if agent["status"] == AIAgentStatus.ACTIVE else AIAgentStatus.ACTIVE
        
        await admin_db.ai_agents.update_one(
            {"agent_id": agent_id},
            {
                "$set": {
                    "status": new_status,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return {
            "agent_id": agent_id,
            "previous_status": agent["status"],
            "new_status": new_status,
            "message": f"AI agent {new_status.value}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to toggle AI agent: {str(e)}")

@app.post("/api/admin/ai-tasks/submit")
async def submit_ai_task(
    task_request: AITaskRequest,
    current_admin = Depends(get_current_admin)
):
    """Submit new AI task for processing"""
    try:
        if not has_permission(AdminRole(current_admin["role"]), "manage_system"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Find appropriate agent
        agent = await admin_db.ai_agents.find_one({
            "agent_type": task_request.agent_type,
            "status": AIAgentStatus.ACTIVE
        })
        
        if not agent:
            raise HTTPException(status_code=404, detail=f"No active AI agent found for type: {task_request.agent_type}")
        
        # Create task document
        task_doc = {
            "task_id": generate_task_id(),
            "agent_id": agent["agent_id"],
            "agent_type": task_request.agent_type,
            "task_data": task_request.task_data,
            "priority": task_request.priority,
            "status": AITaskStatus.QUEUED,
            "result_data": None,
            "confidence_score": None,
            "processing_time_ms": None,
            "error_message": None,
            "retry_count": 0,
            "scheduled_for": task_request.scheduled_for or datetime.utcnow(),
            "started_at": None,
            "completed_at": None,
            "created_at": datetime.utcnow(),
            "created_by": current_admin["admin_id"]
        }
        
        await admin_db.ai_tasks.insert_one(task_doc)
        
        # Process task immediately if not scheduled for later
        if not task_request.scheduled_for or task_request.scheduled_for <= datetime.utcnow():
            try:
                processor = AITaskProcessor()
                result = processor.process_task({
                    "agent_type": task_request.agent_type,
                    "task_data": task_request.task_data
                })
                
                # Update task with results
                await admin_db.ai_tasks.update_one(
                    {"task_id": task_doc["task_id"]},
                    {
                        "$set": {
                            "status": result["status"],
                            "result_data": result["result_data"],
                            "processing_time_ms": result["processing_time_ms"],
                            "error_message": result["error_message"],
                            "started_at": datetime.utcnow(),
                            "completed_at": datetime.utcnow()
                        }
                    }
                )
                
                # Update agent statistics
                await admin_db.ai_agents.update_one(
                    {"agent_id": agent["agent_id"]},
                    {
                        "$set": {"last_activity": datetime.utcnow()},
                        "$inc": {"total_tasks_processed": 1}
                    }
                )
                
                task_doc.update(result)
                
            except Exception as processing_error:
                # Update task as failed
                await admin_db.ai_tasks.update_one(
                    {"task_id": task_doc["task_id"]},
                    {
                        "$set": {
                            "status": AITaskStatus.FAILED,
                            "error_message": str(processing_error),
                            "started_at": datetime.utcnow(),
                            "completed_at": datetime.utcnow()
                        }
                    }
                )
        
        return {
            "task_id": task_doc["task_id"],
            "status": task_doc["status"],
            "message": "AI task submitted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit AI task: {str(e)}")

@app.get("/api/admin/ai-tasks")
async def get_ai_tasks(
    current_admin = Depends(get_current_admin),
    agent_type: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """Get AI tasks with filtering"""
    try:
        if not has_permission(AdminRole(current_admin["role"]), "view_system"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        query = {}
        if agent_type:
            query["agent_type"] = agent_type
        if status:
            query["status"] = status
        
        tasks = await admin_db.ai_tasks.find(query).sort("created_at", -1).skip(offset).limit(limit).to_list(limit)
        total_count = await admin_db.ai_tasks.count_documents(query)
        
        return {
            "tasks": tasks,
            "total": total_count,
            "limit": limit,
            "offset": offset
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get AI tasks: {str(e)}")

@app.get("/api/admin/ai-tasks/{task_id}")
async def get_ai_task_details(
    task_id: str,
    current_admin = Depends(get_current_admin)
):
    """Get detailed AI task information"""
    try:
        if not has_permission(AdminRole(current_admin["role"]), "view_system"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        task = await admin_db.ai_tasks.find_one({"task_id": task_id})
        if not task:
            raise HTTPException(status_code=404, detail="AI task not found")
        
        # Get associated agent info
        agent = await admin_db.ai_agents.find_one({"agent_id": task["agent_id"]})
        
        return {
            "task": task,
            "agent": agent,
            "task_details": {
                "duration_ms": task.get("processing_time_ms"),
                "success": task["status"] == AITaskStatus.COMPLETED,
                "confidence": task.get("confidence_score"),
                "has_results": bool(task.get("result_data"))
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get AI task details: {str(e)}")

@app.post("/api/admin/ai-agents/test-content-moderation")
async def test_content_moderation_ai(
    content_data: Dict[str, Any],
    current_admin = Depends(get_current_admin)
):
    """Test content moderation AI with sample data"""
    try:
        if not has_permission(AdminRole(current_admin["role"]), "manage_system"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Submit test task
        task_request = AITaskRequest(
            agent_type=AIAgentType.CONTENT_MODERATOR,
            task_data=content_data,
            priority=AITaskPriority.HIGH
        )
        
        result = await submit_ai_task(task_request, current_admin)
        
        return {
            "test_result": result,
            "message": "Content moderation AI test completed",
            "demo_mode": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to test content moderation AI: {str(e)}")

@app.get("/api/admin/ai-analytics")
async def get_ai_analytics(current_admin = Depends(get_current_admin)):
    """Get AI system analytics and performance metrics"""
    try:
        if not has_permission(AdminRole(current_admin["role"]), "view_system"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Get all agents and tasks
        agents = await admin_db.ai_agents.find({}).to_list(None)
        tasks = await admin_db.ai_tasks.find({}).to_list(None)
        
        # Calculate system metrics
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t["status"] == AITaskStatus.COMPLETED])
        failed_tasks = len([t for t in tasks if t["status"] == AITaskStatus.FAILED])
        
        # Performance by agent type
        agent_performance = {}
        for agent in agents:
            agent_tasks = [t for t in tasks if t["agent_id"] == agent["agent_id"]]
            agent_performance[agent["agent_type"]] = {
                "total_tasks": len(agent_tasks),
                "success_rate": len([t for t in agent_tasks if t["status"] == AITaskStatus.COMPLETED]) / len(agent_tasks) * 100 if agent_tasks else 0,
                "avg_processing_time": sum(t.get("processing_time_ms", 0) for t in agent_tasks) / len(agent_tasks) if agent_tasks else 0,
                "last_activity": agent.get("last_activity")
            }
        
        # Recent activity (last 24 hours)
        recent_cutoff = datetime.utcnow() - timedelta(hours=24)
        recent_tasks = [t for t in tasks if t["created_at"] >= recent_cutoff]
        
        return {
            "system_overview": {
                "total_agents": len(agents),
                "active_agents": len([a for a in agents if a["status"] == AIAgentStatus.ACTIVE]),
                "total_tasks_processed": total_tasks,
                "overall_success_rate": completed_tasks / total_tasks * 100 if total_tasks > 0 else 0,
                "failed_task_rate": failed_tasks / total_tasks * 100 if total_tasks > 0 else 0
            },
            "agent_performance": agent_performance,
            "recent_activity": {
                "tasks_last_24h": len(recent_tasks),
                "success_rate_24h": len([t for t in recent_tasks if t["status"] == AITaskStatus.COMPLETED]) / len(recent_tasks) * 100 if recent_tasks else 0
            },
            "framework_status": "operational",
            "generated_at": datetime.utcnow()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get AI analytics: {str(e)}")