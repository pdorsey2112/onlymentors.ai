from fastapi import FastAPI, HTTPException, Request, Depends
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
from complete_mentors_database import ALL_MENTORS, TOTAL_MENTORS
from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionResponse, CheckoutStatusResponse, CheckoutSessionRequest
from emergentintegrations.llm.chat import LlmChat, UserMessage

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

def create_mentor_response(mentor, question):
    """Create personality-based response for a mentor"""
    
    # Enhanced responses with more personality variation
    personality_responses = {
        "warren_buffett": f"Well, that's an excellent question about '{question}'. You know, in my many decades of investing, I've learned that the most important thing is to invest in businesses you understand. As I always say, 'Rule No. 1: Never lose money. Rule No. 2: Never forget rule No. 1.' The key is to find wonderful companies at fair prices, not fair companies at wonderful prices. Think long-term, stay patient, and remember that time is the friend of the wonderful business. What you're asking touches on something fundamental - success in investing isn't about making perfect decisions, it's about avoiding big mistakes and letting compound interest work its magic over time.",
        
        "steve_jobs": f"That's a fascinating question: '{question}'. You know, I've always believed that innovation distinguishes between a leader and a follower. When we were building Apple, we didn't just think about making computers - we thought about creating tools that would amplify human intelligence. The key is to start with the user experience and work backward to the technology. Stay hungry, stay foolish. Don't settle for anything less than excellence. And remember, your work is going to fill a large part of your life, so make sure you're doing something you're passionate about.",
        
        "elon_musk": f"Interesting question: '{question}'. I think the key is to approach problems from first principles rather than by analogy. Most people go through life using reasoning by analogy - they do things because that's how things have always been done. But first principles thinking means you boil things down to their fundamental truths and reason up from there. At Tesla and SpaceX, we're always asking: what are the physics of this problem? What's actually possible? Don't be afraid to think big and take calculated risks. The worst that can happen is you learn something valuable.",
        
        "michael_jordan": f"Great question: '{question}'. You know, talent wins games, but teamwork and intelligence win championships. I've always believed that obstacles don't have to stop you. If you run into a wall, don't turn around and give up. Figure out how to climb it, go through it, or work around it. The mental aspect is huge. I never looked at the consequences of missing a big shot... When you think about fear and failure, you're beaten before you even start. You have to believe in yourself when no one else does - that makes you a winner right there.",
        
        "andrew_huberman": f"Excellent question: '{question}'. From a neuroscience perspective, what's fascinating is how our brains are constantly adapting based on our behaviors and environment. The key principles I always emphasize are: get quality sleep (7-9 hours), get morning sunlight exposure to set your circadian rhythm, and engage in regular physical activity. Your nervous system is the foundation for everything - mood, focus, performance. Simple protocols like cold exposure, breathwork, and meditation can dramatically shift your state. Remember, small consistent actions compound over time.",
        
        "albert_einstein": f"Ah, what a thoughtful question: '{question}'. You know, I have always believed that imagination is more important than knowledge. Knowledge is limited, but imagination embraces the entire world. When I was developing the theory of relativity, I didn't start with complex mathematics - I started with thought experiments, imagining what it would be like to ride alongside a beam of light. The most beautiful thing we can experience is the mysterious. Curiosity is more important than intelligence. Ask questions, challenge assumptions, and don't be afraid to think differently.",
        
        "marie_curie": f"What a wonderful question: '{question}'. In my work with radioactivity, I learned that discovery requires both passion and persistence. When Pierre and I were isolating radium, we worked in a freezing shed with primitive equipment, but our curiosity drove us forward. Science taught me that nothing in life is to be feared, only understood. I encourage you to let neither praise nor criticism divert you from the path you feel called to follow. Work with patience and persistence - great discoveries don't happen overnight.",
        
        "usain_bolt": f"Great question: '{question}'. You know, I've always believed in having fun while pursuing excellence. When I step on the track, I'm not just running for myself - I'm running to inspire others to chase their dreams. The key is preparation meets opportunity. I trained for years, focusing on technique, speed, and mental preparation. But confidence is everything - you have to believe you're the best before anyone else will. Stay relaxed under pressure, enjoy the moment, and remember that champions are made in training, not on race day."
    }
    
    # Get specific response or create generic one based on expertise
    if mentor["id"] in personality_responses:
        return personality_responses[mentor["id"]]
    else:
        # Create response based on mentor's expertise and category
        expertise_keywords = mentor['expertise'].lower()
        response_templates = {
            "business": f"Thank you for asking about '{question}'. In my experience in {mentor['expertise']}, I've learned that success comes from understanding your market, staying persistent, and always putting your customers first. {mentor['wiki_description']} My advice is to focus on solving real problems, build strong relationships, and never stop learning. Remember, every setback is a setup for a comeback.",
            
            "sports": f"That's a great question: '{question}'. In my athletic career focused on {mentor['expertise']}, I've discovered that physical talent is just the starting point. Mental toughness, consistent training, and the ability to perform under pressure are what separate good athletes from champions. {mentor['wiki_description']} My advice is to set clear goals, embrace the grind, and never give up when things get tough. Champions are made when nobody is watching.",
            
            "health": f"Excellent question about '{question}'. Based on my expertise in {mentor['expertise']}, I believe that health is our most valuable asset. {mentor['wiki_description']} The key principles I focus on are prevention over treatment, understanding the root causes of health issues, and taking a holistic approach to wellness. My advice is to prioritize sleep, nutrition, exercise, and stress management. Small consistent changes lead to remarkable transformations over time.",
            
            "science": f"What a fascinating question: '{question}'. In my work with {mentor['expertise']}, I've learned that scientific discovery requires both rigorous methodology and creative thinking. {mentor['wiki_description']} The most important thing is to remain curious and question everything. My advice is to observe carefully, form hypotheses, test them systematically, and be prepared to have your assumptions challenged. Science progresses when we embrace uncertainty and keep asking 'why?'"
        }
        
        # Determine category from mentor data (this would be passed in real implementation)
        category = "business"  # Default
        for cat, mentors in ALL_MENTORS.items():
            if any(m["id"] == mentor["id"] for m in mentors):
                category = cat
                break
                
        return response_templates.get(category, 
            f"Thank you for your thoughtful question: '{question}'. Based on my experience and expertise in {mentor['expertise']}, I believe the key is to approach this with both wisdom and practical action. Remember that every challenge is an opportunity for growth, and success comes to those who persist through difficulties while staying true to their values.")

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
            response_text = create_mentor_response(mentor, question_data.question)
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
async def create_checkout_session(checkout_data: CheckoutRequest, current_user = Depends(get_current_user)):
    if checkout_data.package_id not in SUBSCRIPTION_PACKAGES:
        raise HTTPException(status_code=400, detail="Invalid package")
    
    package = SUBSCRIPTION_PACKAGES[checkout_data.package_id]
    
    # Initialize Stripe checkout
    webhook_url = f"{checkout_data.origin_url}/api/webhook/stripe"
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
    
    # Create checkout session
    success_url = f"{checkout_data.origin_url}/?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = checkout_data.origin_url
    
    checkout_request = CheckoutSessionRequest(
        amount=package["price"],
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
        "amount": package["price"],
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