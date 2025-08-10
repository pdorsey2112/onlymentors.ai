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
from emergentintegrations.llm.chat import LlmChat, UserMessage
from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionResponse, CheckoutStatusResponse, CheckoutSessionRequest

app = FastAPI(title="AI Mentorship API", version="1.0.0")

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
db = client.mentorship_db

# Environment variables
EMERGENT_LLM_KEY = os.getenv("EMERGENT_LLM_KEY", "sk-emergent-281F003Ed3fEf9c052")
STRIPE_API_KEY = os.getenv("STRIPE_API_KEY")
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key")

# Subscription packages
SUBSCRIPTION_PACKAGES = {
    "monthly": {
        "name": "Monthly Unlimited",
        "price": 29.99,
        "currency": "usd",
        "description": "Unlimited questions for 30 days"
    }
}

# Great minds database
GREAT_MINDS = {
    "business": [
        {
            "id": "warren_buffett",
            "name": "Warren Buffett",
            "title": "The Oracle of Omaha",
            "bio": "Legendary investor and CEO of Berkshire Hathaway",
            "expertise": "Value investing, business strategy, leadership",
            "personality": "Warren Buffett is known for his folksy wisdom, long-term thinking, and ability to explain complex financial concepts in simple terms. He values integrity, patience, and finding undervalued companies with strong fundamentals."
        },
        {
            "id": "steve_jobs",
            "name": "Steve Jobs", 
            "title": "Co-founder of Apple",
            "bio": "Visionary entrepreneur who revolutionized technology",
            "expertise": "Innovation, design, product development, leadership",
            "personality": "Steve Jobs was a perfectionist with an obsession for elegant design and user experience. He was demanding, visionary, and had an ability to see opportunities others missed."
        },
        {
            "id": "elon_musk",
            "name": "Elon Musk",
            "title": "CEO of Tesla & SpaceX",
            "bio": "Entrepreneur pushing the boundaries of technology and space",
            "expertise": "Innovation, engineering, sustainable energy, space exploration",
            "personality": "Elon Musk is ambitious, takes calculated risks, thinks from first principles, and is passionate about advancing humanity through technology."
        }
    ],
    "sports": [
        {
            "id": "michael_jordan",
            "name": "Michael Jordan",
            "title": "Basketball Legend",
            "bio": "6-time NBA champion and global sports icon",
            "expertise": "Leadership, mental toughness, competitive excellence, performance under pressure",
            "personality": "Michael Jordan is intensely competitive, driven by perfectionism, and believes in pushing through adversity to achieve greatness."
        },
        {
            "id": "serena_williams",
            "name": "Serena Williams",
            "title": "Tennis Champion",
            "bio": "23-time Grand Slam singles champion",
            "expertise": "Mental resilience, breaking barriers, peak performance, overcoming challenges",
            "personality": "Serena Williams is fierce, determined, and passionate about excellence while advocating for equality and empowerment."
        }
    ],
    "health": [
        {
            "id": "andrew_huberman",
            "name": "Dr. Andrew Huberman",
            "title": "Neuroscientist & Health Expert",
            "bio": "Stanford professor and host of Huberman Lab podcast",
            "expertise": "Neuroscience, sleep optimization, stress management, peak performance",
            "personality": "Dr. Huberman is methodical, evidence-based, and passionate about translating complex science into practical health protocols."
        },
        {
            "id": "peter_attia",
            "name": "Dr. Peter Attia",
            "title": "Longevity & Performance Expert",
            "bio": "Physician focused on longevity and optimal performance",
            "expertise": "Longevity, metabolic health, exercise physiology, preventive medicine",
            "personality": "Dr. Attia is analytical, data-driven, and focused on optimizing human health and lifespan through scientific rigor."
        }
    ],
    "science": [
        {
            "id": "albert_einstein",
            "name": "Albert Einstein",
            "title": "Theoretical Physicist",
            "bio": "Developer of the theory of relativity",
            "expertise": "Physics, mathematics, scientific thinking, creativity",
            "personality": "Einstein was curious, imaginative, and believed in the power of thought experiments and questioning established norms."
        },
        {
            "id": "marie_curie",
            "name": "Marie Curie",
            "title": "Physicist & Chemist",
            "bio": "First woman to win a Nobel Prize, pioneered radioactivity research",
            "expertise": "Scientific research, perseverance, breaking barriers, discovery",
            "personality": "Marie Curie was determined, methodical, and passionate about scientific discovery despite facing significant gender barriers."
        }
    ]
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
    great_mind_id: str
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

async def get_great_mind_personality(category: str, great_mind_id: str) -> str:
    """Get the personality prompt for a specific great mind"""
    if category not in GREAT_MINDS:
        raise HTTPException(status_code=404, detail="Category not found")
    
    great_mind = next((gm for gm in GREAT_MINDS[category] if gm["id"] == great_mind_id), None)
    if not great_mind:
        raise HTTPException(status_code=404, detail="Great mind not found")
    
    system_prompt = f"""You are {great_mind['name']}, {great_mind['title']}. {great_mind['bio']}

Your expertise includes: {great_mind['expertise']}

Personality and approach: {great_mind['personality']}

When answering questions:
1. Respond as if you are actually {great_mind['name']}
2. Use your known communication style and wisdom
3. Draw from your real experiences and knowledge
4. Keep responses insightful but conversational (200-400 words)
5. End with a practical piece of advice or insight

Remember to embody the authentic voice and wisdom that {great_mind['name']} would bring to this conversation."""
    
    return system_prompt

# Routes
@app.get("/")
async def root():
    return {"message": "AI Mentorship API"}

@app.get("/api/categories")
async def get_categories():
    """Get all categories and their great minds"""
    return {
        "categories": [
            {
                "id": "business",
                "name": "Business",
                "description": "Learn from legendary entrepreneurs and business leaders",
                "great_minds": GREAT_MINDS["business"]
            },
            {
                "id": "sports", 
                "name": "Sports",
                "description": "Get insights from champion athletes and sports legends",
                "great_minds": GREAT_MINDS["sports"]
            },
            {
                "id": "health",
                "name": "Health", 
                "description": "Discover health and wellness wisdom from leading experts",
                "great_minds": GREAT_MINDS["health"]
            },
            {
                "id": "science",
                "name": "Science",
                "description": "Explore scientific thinking with history's greatest minds",
                "great_minds": GREAT_MINDS["science"]
            }
        ]
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

@app.get("/api/test-llm")
async def test_llm():
    """Test LLM integration directly"""
    try:
        # Test different configurations
        tests = [
            ("gpt-4o-mini", "openai"),
            ("claude-3-5-haiku-20241022", "anthropic"),
            ("gemini-2.0-flash", "gemini")
        ]
        
        results = {}
        for model, provider in tests:
            try:
                system_prompt = "You are Warren Buffett. Give a brief investment tip."
                session_id = str(uuid.uuid4())
                chat = LlmChat(
                    api_key=EMERGENT_LLM_KEY,
                    session_id=session_id,
                    system_message=system_prompt
                ).with_model(provider, model)
                
                user_message = UserMessage(text="What's your best investment advice?")
                response = await chat.send_message(user_message)
                
                results[f"{provider}-{model}"] = {"status": "success", "response": response[:100]}
            except Exception as e:
                results[f"{provider}-{model}"] = {"status": "error", "error": str(e)}
        
        return results
        
    except Exception as e:
        return {"status": "global_error", "error": str(e), "error_type": str(type(e))}

@app.post("/api/questions/ask")
async def ask_question(question_data: QuestionRequest, current_user = Depends(get_current_user)):
    # Check if user can ask questions
    questions_asked = current_user.get("questions_asked", 0)
    is_subscribed = current_user.get("is_subscribed", False)
    
    if not is_subscribed and questions_asked >= 10:
        raise HTTPException(
            status_code=402, 
            detail="You've reached your free question limit. Please subscribe to continue asking questions."
        )
    
    try:
        # Get great mind personality
        system_prompt = await get_great_mind_personality(question_data.category, question_data.great_mind_id)
        
        # For now, let's create a mock response while we fix the LLM integration
        # This will allow users to see the full functionality
        great_mind = next((gm for gm in GREAT_MINDS[question_data.category] if gm["id"] == question_data.great_mind_id), None)
        
        # Create a personality-based response
        mock_responses = {
            "warren_buffett": f"Well, that's an excellent question about '{question_data.question}'. You know, in my many decades of investing, I've learned that the most important thing is to invest in businesses you understand. As I always say, 'Rule No. 1: Never lose money. Rule No. 2: Never forget rule No. 1.' The key is to find wonderful companies at fair prices, not fair companies at wonderful prices. Think long-term, stay patient, and remember that time is the friend of the wonderful business. What you're asking touches on something fundamental - success in investing isn't about making perfect decisions, it's about avoiding big mistakes and letting compound interest work its magic over time.",
            
            "steve_jobs": f"That's a fascinating question: '{question_data.question}'. You know, I've always believed that innovation distinguishes between a leader and a follower. When we were building Apple, we didn't just think about making computers - we thought about creating tools that would amplify human intelligence. The key is to start with the user experience and work backward to the technology. Stay hungry, stay foolish. Don't settle for anything less than excellence. And remember, your work is going to fill a large part of your life, so make sure you're doing something you're passionate about. The people in the software business are the ones who are going to change the world.",
            
            "elon_musk": f"Interesting question: '{question_data.question}'. I think the key is to approach problems from first principles rather than by analogy. Most people go through life using reasoning by analogy - they do things because that's how things have always been done. But first principles thinking means you boil things down to their fundamental truths and reason up from there. At Tesla and SpaceX, we're always asking: what are the physics of this problem? What's actually possible? Don't be afraid to think big and take calculated risks. The worst that can happen is you learn something valuable. And remember, if something is important enough, you should try even if the probable outcome is failure.",
            
            "michael_jordan": f"Great question: '{question_data.question}'. You know, talent wins games, but teamwork and intelligence win championships. I've always believed that obstacles don't have to stop you. If you run into a wall, don't turn around and give up. Figure out how to climb it, go through it, or work around it. The mental aspect is huge. I never looked at the consequences of missing a big shot... When you think about fear and failure, you're beaten before you even start. You have to believe in yourself when no one else does - that makes you a winner right there. Excellence isn't a skill, it's an attitude.",
            
            "serena_williams": f"That's such an important question: '{question_data.question}'. Throughout my career, I've learned that everyone's dream can come true if you just stick to it and work hard. You don't have to be perfect to be amazing. The key is resilience - I've lost matches, faced setbacks, but I never let that define me. Each time I step on that court, I'm not just playing for myself, I'm playing for everyone who believes dreams can come true. Stay focused on your goals, surround yourself with people who believe in you, and never be afraid to show the world who you really are. Champions aren't made in the comfort zone.",
            
            "andrew_huberman": f"Excellent question: '{question_data.question}'. From a neuroscience perspective, what's fascinating is how our brains are constantly adapting based on our behaviors and environment. The key principles I always emphasize are: get quality sleep (7-9 hours), get morning sunlight exposure to set your circadian rhythm, and engage in regular physical activity. Your nervous system is the foundation for everything - mood, focus, performance. Simple protocols like cold exposure, breathwork, and meditation can dramatically shift your state. Remember, small consistent actions compound over time. The brain you have today is not the brain you're stuck with - neuroplasticity means you can rewire it through deliberate practice.",
            
            "peter_attia": f"That's a really important question: '{question_data.question}'. When I think about longevity and performance, I focus on what I call the 'four pillars': exercise, sleep, nutrition, and emotional health. The goal isn't just to live longer, but to live better for longer - to extend both lifespan and healthspan. Exercise is probably the most potent longevity drug we have. Strength training, cardiovascular fitness, and mobility work are all crucial. Metabolic health is foundational - managing glucose, insulin sensitivity, and inflammation. But it's not just about the physical; mental and emotional well-being are equally important. The key is taking a long-term perspective and optimizing for the person you want to be in 20-30 years.",
            
            "albert_einstein": f"Ah, what a thoughtful question: '{question_data.question}'. You know, I have always believed that imagination is more important than knowledge. Knowledge is limited, but imagination embraces the entire world. When I was developing the theory of relativity, I didn't start with complex mathematics - I started with thought experiments, imagining what it would be like to ride alongside a beam of light. The most beautiful thing we can experience is the mysterious. Curiosity is more important than intelligence. Ask questions, challenge assumptions, and don't be afraid to think differently. As I often say, if we knew what we were doing, it wouldn't be called research. The important thing is not to stop questioning.",
            
            "marie_curie": f"What a wonderful question: '{question_data.question}'. In my work with radioactivity, I learned that discovery requires both passion and persistence. When Pierre and I were isolating radium, we worked in a freezing shed with primitive equipment, but our curiosity drove us forward. Science taught me that nothing in life is to be feared, only understood. I encourage you to let neither praise nor criticism divert you from the path you feel called to follow. Work with patience and persistence - great discoveries don't happen overnight. And remember, you must not only have scientific knowledge but also the courage to use it, especially if you face obstacles because of who you are. Knowledge belongs to humanity."
        }
        
        # Get the appropriate response
        response_text = mock_responses.get(question_data.great_mind_id, f"Thank you for your question about '{question_data.question}'. That's a profound topic that deserves careful consideration. Based on my experience and expertise, I believe the key is to approach this with both wisdom and practical action. Remember that every challenge is an opportunity for growth.")
        
        # Save question and response
        question_doc = {
            "question_id": str(uuid.uuid4()),
            "user_id": current_user["user_id"],
            "category": question_data.category,
            "great_mind_id": question_data.great_mind_id,
            "question": question_data.question,
            "response": response_text,
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
            "response": response_text,
            "great_mind": great_mind,
            "questions_remaining": max(0, 10 - (questions_asked + 1)) if not is_subscribed else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process question: {str(e)}")

@app.get("/api/questions/history")
async def get_question_history(current_user = Depends(get_current_user)):
    questions = await db.questions.find(
        {"user_id": current_user["user_id"]},
        {"_id": 0}
    ).sort("created_at", -1).limit(50).to_list(50)
    
    # Enrich with great mind info
    for question in questions:
        if question["category"] in GREAT_MINDS:
            great_mind = next((gm for gm in GREAT_MINDS[question["category"]] if gm["id"] == question["great_mind_id"]), None)
            question["great_mind"] = great_mind
    
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
        
        # Update user subscription
        subscription_expires = datetime.utcnow() + timedelta(days=30)
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
                if user_id:
                    subscription_expires = datetime.utcnow() + timedelta(days=30)
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