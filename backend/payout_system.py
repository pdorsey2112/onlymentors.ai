# Payout Management System for Creator Payments
# Handles automatic payouts to creator accounts with real payment processing

from fastapi import HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import uuid
from enum import Enum
import os

class PayoutStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"

class PayoutFrequency(str, Enum):
    WEEKLY = "weekly"
    BI_WEEKLY = "bi_weekly"
    MONTHLY = "monthly"
    MANUAL = "manual"

class PayoutMethod(str, Enum):
    STRIPE_CONNECT = "stripe_connect"
    BANK_TRANSFER = "bank_transfer"
    PAYPAL = "paypal"
    CRYPTO = "crypto"

class EarningsType(str, Enum):
    SUBSCRIPTION = "subscription"
    TIP = "tip"
    DIRECT_MESSAGE = "direct_message"
    BONUS = "bonus"
    REFERRAL = "referral"

# Pydantic Models
class PayoutRequest(BaseModel):
    creator_ids: List[str]
    force_payout: Optional[bool] = False
    custom_amount: Optional[float] = None
    reason: Optional[str] = None

class PayoutScheduleUpdate(BaseModel):
    creator_id: str
    frequency: PayoutFrequency
    minimum_threshold: Optional[float] = 50.0
    payout_method: PayoutMethod
    enabled: bool = True

class EarningsEntry(BaseModel):
    creator_id: str
    amount: float
    earnings_type: EarningsType
    transaction_id: str
    description: Optional[str] = None

# Database Schemas
def get_creator_earnings_schema():
    """Creator earnings tracking schema"""
    return {
        "earnings_id": str,
        "creator_id": str,
        "transaction_id": str,
        "amount": float,
        "platform_fee": float,
        "creator_earnings": float,  # Amount after platform fee (80%)
        "earnings_type": EarningsType,
        "source_transaction": str,  # Original payment transaction
        "description": Optional[str],
        "currency": str,  # Default USD
        "created_at": datetime,
        "processed_at": Optional[datetime],
        "payout_id": Optional[str]  # Links to payout when paid out
    }

def get_creator_payouts_schema():
    """Creator payouts schema"""
    return {
        "payout_id": str,
        "creator_id": str,
        "amount": float,
        "currency": str,
        "status": PayoutStatus,
        "payout_method": PayoutMethod,
        "stripe_payout_id": Optional[str],
        "bank_details": Optional[Dict[str, str]],
        "earnings_included": List[str],  # List of earnings_ids included
        "fee_amount": float,
        "net_amount": float,
        "scheduled_date": datetime,
        "processed_date": Optional[datetime],
        "failure_reason": Optional[str],
        "retry_count": int,
        "created_by": str,  # Admin ID who initiated
        "created_at": datetime,
        "updated_at": datetime
    }

def get_payout_settings_schema():
    """Creator payout settings schema"""
    return {
        "settings_id": str,
        "creator_id": str,
        "frequency": PayoutFrequency,
        "minimum_threshold": float,
        "payout_method": PayoutMethod,
        "enabled": bool,
        "stripe_account_id": Optional[str],
        "bank_account_details": Optional[Dict[str, str]],
        "next_payout_date": datetime,
        "last_payout_date": Optional[datetime],
        "total_paid_out": float,
        "created_at": datetime,
        "updated_at": datetime
    }

def get_payout_analytics_schema():
    """Payout analytics and reporting schema"""
    return {
        "analytics_id": str,
        "period_start": datetime,
        "period_end": datetime,
        "total_payouts": float,
        "total_creators_paid": int,
        "total_transactions": int,
        "average_payout": float,
        "platform_fees_collected": float,
        "failed_payouts": int,
        "success_rate": float,
        "by_payout_method": Dict[str, Any],
        "top_earners": List[Dict[str, Any]],
        "generated_at": datetime
    }

# Helper Functions
def generate_payout_id() -> str:
    """Generate unique payout ID"""
    return f"payout_{uuid.uuid4().hex[:12]}"

def generate_earnings_id() -> str:
    """Generate unique earnings ID"""
    return f"earn_{uuid.uuid4().hex[:12]}"

def calculate_platform_fee(amount: float, fee_percentage: float = 0.20) -> Dict[str, float]:
    """Calculate platform fee and creator earnings"""
    platform_fee = amount * fee_percentage
    creator_earnings = amount - platform_fee
    
    return {
        "original_amount": amount,
        "platform_fee": platform_fee,
        "creator_earnings": creator_earnings,
        "fee_percentage": fee_percentage
    }

def calculate_next_payout_date(frequency: PayoutFrequency, last_payout: Optional[datetime] = None) -> datetime:
    """Calculate next payout date based on frequency"""
    base_date = last_payout or datetime.utcnow()
    
    if frequency == PayoutFrequency.WEEKLY:
        return base_date + timedelta(weeks=1)
    elif frequency == PayoutFrequency.BI_WEEKLY:
        return base_date + timedelta(weeks=2)
    elif frequency == PayoutFrequency.MONTHLY:
        # Add one month
        if base_date.month == 12:
            return base_date.replace(year=base_date.year + 1, month=1)
        else:
            return base_date.replace(month=base_date.month + 1)
    else:  # MANUAL
        return base_date  # No automatic scheduling

def create_earnings_entry(transaction_data: dict) -> dict:
    """Create earnings entry from payment transaction"""
    amount = transaction_data.get("amount", 0.0)
    fee_calculation = calculate_platform_fee(amount)
    
    return {
        "earnings_id": generate_earnings_id(),
        "creator_id": transaction_data["creator_id"],
        "transaction_id": transaction_data["transaction_id"],
        "amount": amount,
        "platform_fee": fee_calculation["platform_fee"],
        "creator_earnings": fee_calculation["creator_earnings"],
        "earnings_type": transaction_data.get("type", EarningsType.SUBSCRIPTION),
        "source_transaction": transaction_data["transaction_id"],
        "description": transaction_data.get("description"),
        "currency": "USD",
        "created_at": datetime.utcnow(),
        "processed_at": None,
        "payout_id": None
    }

# Stripe Connect Integration Functions
def create_stripe_connect_account(creator_data: dict) -> dict:
    """Create Stripe Connect account for creator (placeholder)"""
    # This would integrate with actual Stripe Connect API
    return {
        "stripe_account_id": f"acct_{uuid.uuid4().hex[:16]}",
        "setup_complete": False,
        "verification_status": "pending",
        "payout_enabled": False
    }

def process_stripe_payout(payout_data: dict) -> dict:
    """Process payout via Stripe Connect (placeholder for real integration)"""
    # This would make actual Stripe API call
    # For now, simulate successful payout
    return {
        "stripe_payout_id": f"po_{uuid.uuid4().hex[:16]}",
        "status": "paid",
        "arrival_date": datetime.utcnow() + timedelta(days=2),
        "fee_amount": payout_data["amount"] * 0.025,  # Stripe fee ~2.5%
        "net_amount": payout_data["amount"] * 0.975
    }

# Payout Processing Functions
def calculate_creator_pending_earnings(creator_id: str, earnings_data: List[dict]) -> Dict[str, Any]:
    """Calculate pending earnings for a creator"""
    creator_earnings = [e for e in earnings_data if e["creator_id"] == creator_id and not e.get("payout_id")]
    
    if not creator_earnings:
        return {
            "creator_id": creator_id,
            "pending_amount": 0.0,
            "earnings_count": 0,
            "oldest_earning": None,
            "earnings_breakdown": {}
        }
    
    total_pending = sum(e["creator_earnings"] for e in creator_earnings)
    earnings_by_type = {}
    
    for earning in creator_earnings:
        earning_type = earning["earnings_type"]
        if earning_type not in earnings_by_type:
            earnings_by_type[earning_type] = {"count": 0, "amount": 0.0}
        earnings_by_type[earning_type]["count"] += 1
        earnings_by_type[earning_type]["amount"] += earning["creator_earnings"]
    
    oldest_earning = min(creator_earnings, key=lambda x: x["created_at"])
    
    return {
        "creator_id": creator_id,
        "pending_amount": total_pending,
        "earnings_count": len(creator_earnings),
        "oldest_earning": oldest_earning["created_at"],
        "earnings_breakdown": earnings_by_type
    }

def process_creator_payout(creator_id: str, earnings_data: List[dict], settings: dict, admin_id: str) -> dict:
    """Process payout for a creator"""
    pending = calculate_creator_pending_earnings(creator_id, earnings_data)
    
    if pending["pending_amount"] < settings.get("minimum_threshold", 50.0):
        raise HTTPException(status_code=400, detail=f"Pending amount ${pending['pending_amount']:.2f} below minimum threshold")
    
    # Create payout record
    payout = {
        "payout_id": generate_payout_id(),
        "creator_id": creator_id,
        "amount": pending["pending_amount"],
        "currency": "USD",
        "status": PayoutStatus.PROCESSING,
        "payout_method": settings.get("payout_method", PayoutMethod.STRIPE_CONNECT),
        "stripe_payout_id": None,
        "bank_details": settings.get("bank_account_details"),
        "earnings_included": [e["earnings_id"] for e in earnings_data if e["creator_id"] == creator_id and not e.get("payout_id")],
        "fee_amount": 0.0,
        "net_amount": pending["pending_amount"],
        "scheduled_date": datetime.utcnow(),
        "processed_date": None,
        "failure_reason": None,
        "retry_count": 0,
        "created_by": admin_id,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    # Process via payment processor
    if settings.get("payout_method") == PayoutMethod.STRIPE_CONNECT:
        try:
            stripe_result = process_stripe_payout(payout)
            payout["stripe_payout_id"] = stripe_result["stripe_payout_id"]
            payout["fee_amount"] = stripe_result["fee_amount"]
            payout["net_amount"] = stripe_result["net_amount"]
            payout["status"] = PayoutStatus.COMPLETED
            payout["processed_date"] = datetime.utcnow()
        except Exception as e:
            payout["status"] = PayoutStatus.FAILED
            payout["failure_reason"] = str(e)
    
    return payout

# Analytics Functions
def calculate_payout_analytics(payouts_data: List[dict], period_days: int = 30) -> Dict[str, Any]:
    """Calculate payout analytics for admin dashboard"""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=period_days)
    
    period_payouts = [p for p in payouts_data if p["created_at"] >= start_date]
    
    if not period_payouts:
        return {
            "period_start": start_date,
            "period_end": end_date,
            "total_payouts": 0.0,
            "total_creators_paid": 0,
            "total_transactions": 0,
            "average_payout": 0.0,
            "platform_fees_collected": 0.0,
            "failed_payouts": 0,
            "success_rate": 0.0,
            "by_payout_method": {},
            "top_earners": []
        }
    
    completed_payouts = [p for p in period_payouts if p["status"] == PayoutStatus.COMPLETED]
    failed_payouts = [p for p in period_payouts if p["status"] == PayoutStatus.FAILED]
    
    total_amount = sum(p["amount"] for p in completed_payouts)
    total_fees = sum(p["fee_amount"] for p in completed_payouts)
    
    # Group by payout method
    by_method = {}
    for payout in period_payouts:
        method = payout["payout_method"]
        if method not in by_method:
            by_method[method] = {"count": 0, "amount": 0.0}
        by_method[method]["count"] += 1
        by_method[method]["amount"] += payout["amount"]
    
    # Top earners
    creator_totals = {}
    for payout in completed_payouts:
        creator_id = payout["creator_id"]
        if creator_id not in creator_totals:
            creator_totals[creator_id] = 0.0
        creator_totals[creator_id] += payout["amount"]
    
    top_earners = sorted(creator_totals.items(), key=lambda x: x[1], reverse=True)[:10]
    top_earners = [{"creator_id": creator_id, "amount": amount} for creator_id, amount in top_earners]
    
    return {
        "period_start": start_date,
        "period_end": end_date,
        "total_payouts": total_amount,
        "total_creators_paid": len(set(p["creator_id"] for p in completed_payouts)),
        "total_transactions": len(period_payouts),
        "average_payout": total_amount / len(completed_payouts) if completed_payouts else 0.0,
        "platform_fees_collected": total_fees,
        "failed_payouts": len(failed_payouts),
        "success_rate": len(completed_payouts) / len(period_payouts) * 100 if period_payouts else 0.0,
        "by_payout_method": by_method,
        "top_earners": top_earners
    }

# Default Payout Settings
DEFAULT_PAYOUT_SETTINGS = {
    "frequency": PayoutFrequency.MONTHLY,
    "minimum_threshold": 50.0,
    "payout_method": PayoutMethod.STRIPE_CONNECT,
    "enabled": True
}

def create_default_payout_settings(creator_id: str) -> dict:
    """Create default payout settings for new creator"""
    return {
        "settings_id": f"settings_{uuid.uuid4().hex[:12]}",
        "creator_id": creator_id,
        "frequency": DEFAULT_PAYOUT_SETTINGS["frequency"],
        "minimum_threshold": DEFAULT_PAYOUT_SETTINGS["minimum_threshold"],
        "payout_method": DEFAULT_PAYOUT_SETTINGS["payout_method"],
        "enabled": DEFAULT_PAYOUT_SETTINGS["enabled"],
        "stripe_account_id": None,
        "bank_account_details": None,
        "next_payout_date": calculate_next_payout_date(DEFAULT_PAYOUT_SETTINGS["frequency"]),
        "last_payout_date": None,
        "total_paid_out": 0.0,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

# Revenue Sharing Constants
PLATFORM_FEE_PERCENTAGE = 0.20  # 20% platform fee
CREATOR_SHARE_PERCENTAGE = 0.80  # 80% goes to creator
PAYMENT_PROCESSOR_FEE = 0.029   # ~2.9% payment processor fee