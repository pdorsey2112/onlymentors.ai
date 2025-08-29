"""
OnlyMentors.ai Premium Content System (Pay-Per-View)
Handles creator content uploads, pricing, payments, and access control
"""

import os
import uuid
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from fastapi import HTTPException, UploadFile
from pydantic import BaseModel, EmailStr
import logging
from decimal import Decimal, ROUND_UP
import mimetypes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PremiumContentManager:
    def __init__(self):
        self.platform_commission_rate = 0.20  # 20%
        self.minimum_platform_fee = 2.99  # Minimum $2.99 fee
        self.max_content_price = 50.00  # Maximum $50 per content
        self.content_storage_path = "/app/content_storage"
        
    def calculate_platform_fee(self, content_price: float) -> Dict[str, float]:
        """Calculate platform fee: 20% OR $2.99 minimum (whichever is higher)"""
        price = Decimal(str(content_price))
        commission = price * Decimal(str(self.platform_commission_rate))
        minimum_fee = Decimal(str(self.minimum_platform_fee))
        
        platform_fee = max(commission, minimum_fee)
        creator_earnings = price - platform_fee
        
        return {
            "content_price": float(price),
            "platform_fee": float(platform_fee),
            "creator_earnings": float(creator_earnings),
            "commission_rate": self.platform_commission_rate * 100
        }
    
    def validate_content_price(self, price: float) -> bool:
        """Validate content pricing is within acceptable range"""
        return 0.01 <= price <= self.max_content_price
    
    def get_content_type_category(self, filename: str) -> str:
        """Determine content category based on file type"""
        mime_type, _ = mimetypes.guess_type(filename)
        
        if not mime_type:
            return "document"
        
        if mime_type.startswith('video/'):
            return "video"
        elif mime_type.startswith('audio/'):
            return "audio"
        elif mime_type in ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
            return "document"
        elif mime_type.startswith('image/'):
            return "image"
        else:
            return "document"
    
    async def create_content_record(self, creator_id: str, content_data: dict) -> dict:
        """Create premium content record in database"""
        content_id = str(uuid.uuid4())
        
        # Calculate pricing breakdown
        pricing = self.calculate_platform_fee(content_data['price'])
        
        content_record = {
            "content_id": content_id,
            "creator_id": creator_id,
            "title": content_data['title'],
            "description": content_data['description'],
            "content_type": content_data['content_type'],
            "category": content_data.get('category', 'general'),
            "price": pricing['content_price'],
            "platform_fee": pricing['platform_fee'],
            "creator_earnings": pricing['creator_earnings'],
            "file_path": content_data.get('file_path'),
            "file_size": content_data.get('file_size', 0),
            "thumbnail_path": content_data.get('thumbnail_path'),
            "duration": content_data.get('duration'),  # For videos/audio
            "page_count": content_data.get('page_count'),  # For documents
            "preview_available": content_data.get('preview_available', False),
            "tags": content_data.get('tags', []),
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "total_views": 0,
            "total_purchases": 0,
            "total_revenue": 0.0
        }
        
        return content_record
    
    async def process_content_purchase(self, content_id: str, user_id: str, payment_intent_id: str) -> dict:
        """Process successful content purchase and grant access"""
        purchase_id = str(uuid.uuid4())
        
        purchase_record = {
            "purchase_id": purchase_id,
            "content_id": content_id,
            "user_id": user_id,
            "payment_intent_id": payment_intent_id,
            "purchase_date": datetime.utcnow(),
            "access_granted": True,
            "access_expires": None,  # Lifetime access for pay-per-view
            "download_count": 0,
            "max_downloads": 10,  # Allow up to 10 downloads
            "last_accessed": None
        }
        
        return purchase_record
    
    def get_allowed_file_types(self) -> Dict[str, List[str]]:
        """Get allowed file types for different content categories"""
        return {
            "document": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt"],
            "video": [".mp4", ".avi", ".mov", ".wmv", ".flv", ".webm"],
            "audio": [".mp3", ".wav", ".aac", ".ogg", ".flac"],
            "image": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg"],
            "interactive": [".html", ".zip", ".scorm"]
        }
    
    def validate_file_upload(self, file: UploadFile, content_type: str) -> Dict[str, Any]:
        """Validate uploaded file meets requirements"""
        allowed_types = self.get_allowed_file_types()
        
        # Check file extension
        filename = file.filename.lower()
        file_ext = os.path.splitext(filename)[1]
        
        if content_type not in allowed_types:
            return {"valid": False, "error": f"Invalid content type: {content_type}"}
        
        if file_ext not in allowed_types[content_type]:
            return {
                "valid": False, 
                "error": f"Invalid file type {file_ext} for {content_type}. Allowed: {allowed_types[content_type]}"
            }
        
        # Check file size (max 500MB)
        max_size = 500 * 1024 * 1024  # 500MB
        if hasattr(file, 'size') and file.size > max_size:
            return {"valid": False, "error": "File too large. Maximum size is 500MB"}
        
        return {"valid": True, "file_extension": file_ext, "content_category": self.get_content_type_category(filename)}

# Pydantic models for API endpoints
class PremiumContentCreate(BaseModel):
    title: str
    description: str
    content_type: str  # document, video, audio, image, interactive
    category: str
    price: float
    tags: Optional[List[str]] = []
    preview_available: bool = False

class ContentPurchaseRequest(BaseModel):
    content_id: str
    payment_method_id: str

class ContentSearchQuery(BaseModel):
    creator_id: Optional[str] = None
    category: Optional[str] = None
    content_type: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    tags: Optional[List[str]] = []
    search_term: Optional[str] = None

class ContentUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    is_active: Optional[bool] = None

# Initialize premium content manager
premium_content_manager = PremiumContentManager()

# Helper functions for easy import
def calculate_content_pricing(price: float) -> Dict[str, float]:
    """Calculate pricing breakdown for content"""
    return premium_content_manager.calculate_platform_fee(price)

def validate_content_price(price: float) -> bool:
    """Validate if price is within acceptable range"""
    return premium_content_manager.validate_content_price(price)

async def create_premium_content(creator_id: str, content_data: dict) -> dict:
    """Create new premium content record"""
    return await premium_content_manager.create_content_record(creator_id, content_data)

async def process_purchase(content_id: str, user_id: str, payment_intent_id: str) -> dict:
    """Process content purchase"""
    return await premium_content_manager.process_content_purchase(content_id, user_id, payment_intent_id)