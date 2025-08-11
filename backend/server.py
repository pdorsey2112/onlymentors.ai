from fastapi import FastAPI, HTTPException, Request, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
import uuid
import os
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

class UserLogin(BaseModel):
    email: str
    password: str

class QuestionRequest(BaseModel):
    category: str
    mentor_ids: List[str]  # Multiple mentors can be selected
    question: str

class CheckoutRequest(BaseModel):
    package_id: str
    origin_url: str

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

async def create_mentor_response(mentor, question):
    """Create AI-powered response from a mentor using their personality and expertise"""
    try:
        # Create a unique session ID for this mentor-question combination
        session_id = f"mentor_{mentor['id']}_{hash(question) % 10000}"
        
        # Build system message based on mentor's personality and expertise
        system_message = f"""You are {mentor['name']}, {mentor['expertise']}. {mentor['wiki_description']}

Personality and Communication Style:
- Respond as if you are actually {mentor['name']}
- Use your authentic voice, personality, and speaking patterns
- Draw from your real-life experiences, achievements, and philosophy
- Provide practical, actionable based on your expertise
- Keep responses conversational yet insightful (2-3 paragraphs)
- Use "I" statements and personal anecdotes where appropriate
- Reflect your known values, beliefs, and approach to life/work

Areas of Expertise: {mentor['expertise']}

Your response should feel authentic to who you are as a person and thought leader."""

        print(f"🤖 Attempting LLM call for {mentor['name']} with session {session_id}")
        
        # Initialize LLM chat with additional debugging
        chat = LlmChat(
            api_key=OPENAI_API_KEY,
            session_id=session_id,
            system_message=system_message
        ).with_model("openai", "gpt-4o-mini")
        
        print(f"🤖 LlmChat initialized for {mentor['name']}")
        
        # Create user message
        user_message = UserMessage(text=question)
        
        print(f"🤖 Sending message to LLM for {mentor['name']}")
        
        # Get AI response with timeout handling
        import asyncio
        response = await asyncio.wait_for(chat.send_message(user_message), timeout=30.0)
        
        print(f"✅ LLM response received for {mentor['name']}: {len(response)} chars")
        
        return response.strip()
        
    except asyncio.TimeoutError:
        print(f"⏰ LLM API Timeout for {mentor['name']}")
        return f"Thank you for your question about '{question}'. Based on my experience in {mentor['expertise']}, I believe this is an important topic that requires thoughtful consideration. While I'd love to provide a detailed response right now, I encourage you to explore this further and perhaps rephrase your question for the best guidance. {mentor['wiki_description']}"
    except Exception as e:
        # Fallback to a generic response if LLM fails
        print(f"❌ LLM API Error for {mentor['name']}: {str(e)}")
        print(f"❌ Error type: {type(e).__name__}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return f"Thank you for your question about '{question}'. Based on my experience in {mentor['expertise']}, I believe this is an important topic that requires thoughtful consideration. While I'd love to provide a detailed response right now, I encourage you to explore this further and perhaps rephrase your question for the best guidance. {mentor['wiki_description']}"

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
async def search_mentors(q: str = "", category: Optional[str] = None):
    """Search mentors across categories"""
    results = []
    search_term = q.lower()
    
    categories_to_search = [category] if category and category in ALL_MENTORS else ALL_MENTORS.keys()
    
    for cat in categories_to_search:
        for mentor in ALL_MENTORS[cat]:
            if (search_term in mentor["name"].lower() or 
                search_term in mentor["expertise"].lower() or
                search_term in mentor["bio"].lower()):
                results.append({**mentor, "category": cat})
    
    return {"results": results, "count": len(results), "query": q}

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
        "full_name": user_data.full_name,
        "password_hash": hash_password(user_data.password),
        "questions_asked": 0,
        "is_subscribed": False,
        "subscription_expires": None,
        "created_at": datetime.utcnow()
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
    
    # Create access token
    token = create_access_token({"user_id": user["user_id"]})
    
    return {
        "token": token,
        "user": {
            "user_id": user["user_id"],
            "email": user["email"], 
            "full_name": user["full_name"],
            "questions_asked": user.get("questions_asked", 0),
            "is_subscribed": user.get("is_subscribed", False)
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

@app.post("/api/questions/ask")
async def ask_question(question_data: QuestionRequest, current_user = Depends(get_current_user)):
    # Check if user can ask questions
    questions_asked = current_user.get("questions_asked", 0)
    is_subscribed = current_user.get("is_subscribed", False)
    
    if not is_subscribed and questions_asked >= 10:
        raise HTTPException(
            status_code=402, 
            detail=f"You've reached your free question limit. Please subscribe to continue asking questions to any of our {TOTAL_MENTORS} mentors."
        )
    
    try:
        # Validate mentors exist
        selected_mentors = []
        for mentor_id in question_data.mentor_ids:
            mentor = next((m for m in ALL_MENTORS[question_data.category] if m["id"] == mentor_id), None)
            if not mentor:
                raise HTTPException(status_code=404, detail=f"Mentor {mentor_id} not found")
            selected_mentors.append(mentor)
        
        # Create responses from all selected mentors
        responses = []
        for mentor in selected_mentors:
            response_text = await create_mentor_response(mentor, question_data.question)
            responses.append({
                "mentor": mentor,
                "response": response_text
            })
        
        # Save question and responses
        question_doc = {
            "question_id": str(uuid.uuid4()),
            "user_id": current_user["user_id"],
            "category": question_data.category,
            "mentor_ids": question_data.mentor_ids,
            "question": question_data.question,
            "responses": responses,
            "created_at": datetime.utcnow()
        }
        
        await db.questions.insert_one(question_doc)
        
        # Update user question count (count as one question regardless of number of mentors)
        await db.users.update_one(
            {"user_id": current_user["user_id"]},
            {"$inc": {"questions_asked": 1}}
        )
        
        return {
            "question_id": question_doc["question_id"],
            "question": question_data.question,
            "responses": responses,
            "selected_mentors": selected_mentors,
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
    content_file: UploadFile = File(None)
):
    """Upload content for creator"""
    try:
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
        if content_type not in ["video", "document", "article_link"]:
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
async def get_creator_content(creator_id: str, limit: int = 20, offset: int = 0):
    """Get creator's content"""
    try:
        creator = await db.creators.find_one({"creator_id": creator_id})
        if not creator:
            raise HTTPException(status_code=404, detail="Creator not found")
        
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