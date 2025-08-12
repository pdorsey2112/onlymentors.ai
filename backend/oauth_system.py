# OAuth Authentication System for OnlyMentors.ai
# Handles Google OAuth 2.0 integration

import os
import uuid
import httpx
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException
from pydantic import BaseModel, EmailStr
import jwt

# OAuth Models
class GoogleOAuthResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    scope: str
    expires_in: int
    refresh_token: Optional[str] = None
    id_token: str

class GoogleUserInfo(BaseModel):
    id: str
    email: EmailStr
    verified_email: bool
    name: str
    given_name: str
    family_name: str
    picture: str
    locale: str

class FacebookUserInfo(BaseModel):
    id: str
    email: EmailStr
    name: str
    first_name: str
    last_name: str
    picture: Optional[Dict] = None

class SocialAuthRequest(BaseModel):
    provider: str  # "google", "facebook", "apple", "twitter"
    code: Optional[str] = None
    id_token: Optional[str] = None
    access_token: Optional[str] = None

class SocialAuthResponse(BaseModel):
    user_id: str
    email: str
    full_name: str
    profile_image_url: Optional[str] = None
    is_new_user: bool
    access_token: str
    provider: str

# OAuth Configuration
class OAuthConfig:
    def __init__(self):
        self.google_client_id = os.getenv("GOOGLE_CLIENT_ID")
        self.google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        self.google_redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:3000/auth/google")
        
        # Facebook OAuth Configuration
        self.facebook_app_id = os.getenv("FACEBOOK_APP_ID")
        self.facebook_app_secret = os.getenv("FACEBOOK_APP_SECRET")
        self.facebook_redirect_uri = os.getenv("FACEBOOK_REDIRECT_URI", "http://localhost:3000")
        
        self.jwt_secret = os.getenv("JWT_SECRET", "mentorship-jwt-secret-key-2024")
        
        # OAuth endpoints
        self.google_token_url = "https://oauth2.googleapis.com/token"
        self.google_userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
        
        # Facebook endpoints
        self.facebook_token_url = "https://graph.facebook.com/v18.0/oauth/access_token"
        self.facebook_userinfo_url = "https://graph.facebook.com/v18.0/me"
    
    def validate_google_config(self):
        """Validate Google OAuth configuration"""
        if not self.google_client_id or self.google_client_id == "your_google_client_id_here":
            raise ValueError("Google OAuth Client ID not configured")
        if not self.google_client_secret or self.google_client_secret == "your_google_client_secret_here":
            raise ValueError("Google OAuth Client Secret not configured")
        return True
    
    def validate_facebook_config(self):
        """Validate Facebook OAuth configuration"""
        if not self.facebook_app_id:
            raise ValueError("Facebook App ID not configured")
        if not self.facebook_app_secret:
            raise ValueError("Facebook App Secret not configured")
        return True

oauth_config = OAuthConfig()

def generate_user_id():
    """Generate a unique user ID"""
    return f"user_{uuid.uuid4().hex[:16]}"

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, oauth_config.jwt_secret, algorithm="HS256")
    return encoded_jwt

async def exchange_google_code_for_token(code: str) -> GoogleOAuthResponse:
    """Exchange Google OAuth code for access token"""
    try:
        oauth_config.validate_google_config()
        
        data = {
            "client_id": oauth_config.google_client_id,
            "client_secret": oauth_config.google_client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": oauth_config.google_redirect_uri,
        }
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                oauth_config.google_token_url, 
                data=data, 
                headers=headers, 
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Failed to exchange code for token: {response.text}"
                )
            
            token_data = response.json()
            return GoogleOAuthResponse(**token_data)
            
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OAuth token exchange failed: {str(e)}")

async def verify_google_id_token(id_token: str) -> GoogleUserInfo:
    """Verify Google ID token and extract user info"""
    try:
        oauth_config.validate_google_config()
        
        # Verify the ID token with Google
        verification_url = f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(verification_url, timeout=30.0)
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Failed to verify Google ID token: {response.text}"
                )
            
            token_data = response.json()
            
            # Verify the token is for our client
            if token_data.get("aud") != oauth_config.google_client_id:
                raise HTTPException(
                    status_code=400, 
                    detail="Invalid token audience"
                )
            
            # Map the token data to our GoogleUserInfo format
            user_info = GoogleUserInfo(
                id=token_data.get("sub"),
                email=token_data.get("email"),
                verified_email=token_data.get("email_verified", False),
                name=token_data.get("name"),
                given_name=token_data.get("given_name", ""),
                family_name=token_data.get("family_name", ""),
                picture=token_data.get("picture", ""),
                locale=token_data.get("locale", "en")
            )
            
            return user_info
            
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to verify Google ID token: {str(e)}")

async def get_google_user_info(access_token: str) -> GoogleUserInfo:
    """Get user information from Google using access token"""
    try:
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                oauth_config.google_userinfo_url, 
                headers=headers, 
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Failed to get user info: {response.text}"
                )
            
            user_data = response.json()
            return GoogleUserInfo(**user_data)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user info: {str(e)}")

async def exchange_facebook_code_for_token(code: str) -> str:
    """Exchange Facebook OAuth code for access token"""
    try:
        oauth_config.validate_facebook_config()
        
        params = {
            "client_id": oauth_config.facebook_app_id,
            "client_secret": oauth_config.facebook_app_secret,
            "code": code,
            "redirect_uri": oauth_config.facebook_redirect_uri,
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                oauth_config.facebook_token_url, 
                params=params, 
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Failed to exchange Facebook code for token: {response.text}"
                )
            
            token_data = response.json()
            return token_data.get("access_token")
            
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Facebook OAuth token exchange failed: {str(e)}")

async def get_facebook_user_info(access_token: str) -> FacebookUserInfo:
    """Get user information from Facebook using access token"""
    try:
        params = {
            "access_token": access_token,
            "fields": "id,email,name,first_name,last_name,picture.type(large)"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                oauth_config.facebook_userinfo_url, 
                params=params, 
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Failed to get Facebook user info: {response.text}"
                )
            
            user_data = response.json()
            
            # Handle email not provided case
            if "email" not in user_data:
                raise HTTPException(
                    status_code=400,
                    detail="Email permission required for Facebook login. Please grant email access."
                )
            
            return FacebookUserInfo(**user_data)
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get Facebook user info: {str(e)}")

async def verify_facebook_access_token(access_token: str) -> FacebookUserInfo:
    """Verify Facebook access token and get user info"""
    try:
        oauth_config.validate_facebook_config()
        
        # First, validate the token with Facebook
        params = {
            "input_token": access_token,
            "access_token": f"{oauth_config.facebook_app_id}|{oauth_config.facebook_app_secret}"
        }
        
        async with httpx.AsyncClient() as client:
            # Verify token
            response = await client.get(
                "https://graph.facebook.com/debug_token",
                params=params,
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to verify Facebook token: {response.text}"
                )
            
            token_info = response.json()
            
            # Check if token is valid
            if not token_info.get("data", {}).get("is_valid", False):
                raise HTTPException(
                    status_code=400,
                    detail="Invalid Facebook access token"
                )
            
            # Verify the token is for our app
            if token_info.get("data", {}).get("app_id") != oauth_config.facebook_app_id:
                raise HTTPException(
                    status_code=400,
                    detail="Facebook token is not for this application"
                )
            
            # Get user info
            return await get_facebook_user_info(access_token)
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to verify Facebook token: {str(e)}")

def create_user_from_facebook_auth(user_info: FacebookUserInfo, provider: str) -> Dict[str, Any]:
    """Create user document from Facebook authentication data"""
    user_id = generate_user_id()
    
    # Extract profile picture URL
    profile_image_url = None
    if user_info.picture and isinstance(user_info.picture, dict):
        profile_image_url = user_info.picture.get("data", {}).get("url")
    
    user_doc = {
        "user_id": user_id,
        "email": user_info.email,
        "full_name": user_info.name,
        "password_hash": None,  # Social auth users don't have passwords
        "is_subscribed": False,
        "subscription_expires": None,
        "subscription_package": None,
        "questions_asked": 0,
        "questions_remaining": 10,  # Free questions for new users
        "social_auth": {
            "provider": provider,
            "provider_id": user_info.id,
            "provider_email": user_info.email,
            "profile_image_url": profile_image_url,
            "first_name": user_info.first_name,
            "last_name": user_info.last_name
        },
        "profile_image_url": profile_image_url,
        "created_at": datetime.utcnow(),
        "last_login": datetime.utcnow(),
        "last_active": datetime.utcnow()
    }
    
    return user_doc

def create_user_from_social_auth(user_info: GoogleUserInfo, provider: str) -> Dict[str, Any]:
    """Create user document from social authentication data"""
    user_id = generate_user_id()
    
    user_doc = {
        "user_id": user_id,
        "email": user_info.email,
        "full_name": user_info.name,
        "password_hash": None,  # Social auth users don't have passwords
        "is_subscribed": False,
        "subscription_expires": None,
        "subscription_package": None,
        "questions_asked": 0,
        "questions_remaining": 10,  # Free questions for new users
        "social_auth": {
            "provider": provider,
            "provider_id": user_info.id,
            "provider_email": user_info.email,
            "profile_image_url": user_info.picture,
            "verified_email": user_info.verified_email
        },
        "profile_image_url": user_info.picture,
        "created_at": datetime.utcnow(),
        "last_login": datetime.utcnow(),
        "last_active": datetime.utcnow()
    }
    
    return user_doc

def get_user_public_profile(user_doc: Dict[str, Any]) -> Dict[str, Any]:
    """Get user's public profile data"""
    return {
        "user_id": user_doc["user_id"],
        "email": user_doc["email"],
        "full_name": user_doc["full_name"],
        "is_subscribed": user_doc.get("is_subscribed", False),
        "subscription_expires": user_doc.get("subscription_expires"),
        "questions_asked": user_doc.get("questions_asked", 0),
        "questions_remaining": user_doc.get("questions_remaining", 10),
        "profile_image_url": user_doc.get("profile_image_url"),
        "social_auth": {
            "provider": user_doc.get("social_auth", {}).get("provider"),
            "profile_image_url": user_doc.get("social_auth", {}).get("profile_image_url")
        } if user_doc.get("social_auth") else None,
        "created_at": user_doc["created_at"],
        "last_login": user_doc.get("last_login")
    }