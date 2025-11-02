"""
Finance Module - Pydantic Models

Data models for accounts, transactions, categories, and analytics.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


# ============================================================================
# ACCOUNT MODELS
# ============================================================================

class AccountBase(BaseModel):
    """Base account model"""
    name: str = Field(..., max_length=100)
    type: str = Field(..., pattern="^(checking|savings|credit|investment)$")
    default_currency: str = Field(default="CAD", max_length=3)
    balance: Decimal = Field(default=Decimal("0.00"))
    is_active: bool = True


class AccountCreate(AccountBase):
    """Model for creating an account"""
    pass


class AccountUpdate(BaseModel):
    """Model for updating an account (all fields optional)"""
    name: Optional[str] = Field(None, max_length=100)
    type: Optional[str] = Field(None, pattern="^(checking|savings|credit|investment)$")
    default_currency: Optional[str] = Field(None, max_length=3)
    balance: Optional[Decimal] = None
    is_active: Optional[bool] = None


class Account(AccountBase):
    """Complete account model with database fields"""
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# CATEGORY MODELS
# ============================================================================

class CategoryBase(BaseModel):
    """Base category model"""
    name: str = Field(..., max_length=100)
    type: str = Field(..., pattern="^(expense|income)$")
    parent_id: Optional[UUID] = None
    color: str = Field(default="#6B7280", max_length=7)
    icon: Optional[str] = Field(None, max_length=50)
    is_system: bool = False


class CategoryCreate(CategoryBase):
    """Model for creating a category"""
    pass


class Category(CategoryBase):
    """Complete category model with database fields"""
    id: UUID
    user_id: Optional[UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# TRANSACTION MODELS
# ============================================================================

class TransactionBase(BaseModel):
    """Base transaction model"""
    account_id: UUID
    date: date
    amount: Decimal = Field(..., description="Positive for income, negative for expenses")
    currency: str = Field(default="CAD", max_length=3)
    amount_cad: Optional[Decimal] = Field(None, description="Auto-calculated if not provided")
    category_id: Optional[UUID] = None
    merchant: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    source: str = Field(default="manual", pattern="^(manual|ocr|import)$")
    notes: Optional[str] = None


class TransactionCreate(TransactionBase):
    """Model for creating a transaction"""
    pass


class TransactionUpdate(BaseModel):
    """Model for updating a transaction (all fields optional)"""
    account_id: Optional[UUID] = None
    date: Optional[date] = None
    amount: Optional[Decimal] = None
    currency: Optional[str] = Field(None, max_length=3)
    amount_cad: Optional[Decimal] = None
    category_id: Optional[UUID] = None
    merchant: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    notes: Optional[str] = None


class Transaction(TransactionBase):
    """Complete transaction model with database fields"""
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TransactionWithDetails(Transaction):
    """Transaction with category and account details"""
    category_name: Optional[str] = None
    category_color: Optional[str] = None
    account_name: str


# ============================================================================
# ANALYTICS MODELS
# ============================================================================

class MonthlyBurnRate(BaseModel):
    """Monthly burn rate calculation"""
    month: str  # YYYY-MM format
    total_income: Decimal
    total_expenses: Decimal
    net_flow: Decimal
    burn_rate: Decimal  # Average daily spending
    transaction_count: int


class CategoryBreakdown(BaseModel):
    """Spending breakdown by category"""
    category_id: Optional[UUID]
    category_name: str
    category_color: str
    total_amount: Decimal
    transaction_count: int
    percentage: float


class RunwayCalculation(BaseModel):
    """Runway to emergency fund calculation"""
    current_balance: Decimal
    monthly_burn_rate: Decimal
    emergency_fund_target: Decimal
    months_of_runway: Optional[float]
    days_of_runway: Optional[int]
    target_reached: bool


class FinancialSummary(BaseModel):
    """High-level financial summary"""
    total_balance: Decimal
    total_income_mtd: Decimal  # Month to date
    total_expenses_mtd: Decimal
    net_flow_mtd: Decimal
    account_count: int
    transaction_count_mtd: int
    top_category: Optional[str] = None
    top_category_amount: Optional[Decimal] = None


# ============================================================================
# EXCHANGE RATE MODELS
# ============================================================================

class ExchangeRateBase(BaseModel):
    """Base exchange rate model"""
    from_currency: str = Field(..., max_length=3)
    to_currency: str = Field(..., max_length=3)
    rate: Decimal
    date: date
    source: str = Field(default="manual", max_length=50)


class ExchangeRateCreate(ExchangeRateBase):
    """Model for creating an exchange rate"""
    pass


class ExchangeRate(ExchangeRateBase):
    """Complete exchange rate model with database fields"""
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# FILTER MODELS
# ============================================================================

class TransactionFilters(BaseModel):
    """Filters for transaction queries"""
    account_id: Optional[UUID] = None
    category_id: Optional[UUID] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None
    search: Optional[str] = None  # Search merchant or description
    source: Optional[str] = None
    limit: int = Field(default=100, le=1000)
    offset: int = Field(default=0, ge=0)
