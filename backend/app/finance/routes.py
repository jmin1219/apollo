"""
Finance Module - API Routes

RESTful endpoints for finance operations.
"""

from datetime import date
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File

from app.auth.dependencies import get_current_user
from app.finance.models import (
    Account, AccountCreate, AccountUpdate,
    Transaction, TransactionCreate, TransactionUpdate,
    Category, CategoryCreate,
    MonthlyBurnRate, CategoryBreakdown, RunwayCalculation, FinancialSummary,
    TransactionFilters
)
from app.finance.services import FinanceService
from app.finance.ocr_service import OCRService, OCRResult
from app.models.user import User

# Create router
router = APIRouter(prefix="/finance", tags=["finance"])


# ============================================================================
# ACCOUNT ENDPOINTS
# ============================================================================

@router.get("/accounts", response_model=List[Account])
async def list_accounts(
    include_inactive: bool = Query(default=False),
    current_user: User = Depends(get_current_user)
):
    """
    Get all accounts for the current user.
    
    - **include_inactive**: Include inactive accounts in results
    """
    accounts = FinanceService.get_accounts(current_user.id, include_inactive)
    return accounts


@router.get("/accounts/{account_id}", response_model=Account)
async def get_account(
    account_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """Get a specific account by ID"""
    account = FinanceService.get_account(account_id, current_user.id)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    return account


@router.post("/accounts", response_model=Account, status_code=status.HTTP_201_CREATED)
async def create_account(
    account: AccountCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new account.
    
    - **name**: Account name (e.g., "Scotiabank Checking")
    - **type**: checking, savings, credit, or investment
    - **default_currency**: ISO currency code (default: CAD)
    - **balance**: Initial balance (default: 0.00)
    """
    new_account = FinanceService.create_account(current_user.id, account)
    return new_account


@router.patch("/accounts/{account_id}", response_model=Account)
async def update_account(
    account_id: UUID,
    account: AccountUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update an account (partial update supported)"""
    updated_account = FinanceService.update_account(account_id, current_user.id, account)
    if not updated_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    return updated_account


@router.delete("/accounts/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    account_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """Delete an account (soft delete - marks as inactive)"""
    success = FinanceService.delete_account(account_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )


# ============================================================================
# CATEGORY ENDPOINTS
# ============================================================================

@router.get("/categories", response_model=List[Category])
async def list_categories(
    category_type: Optional[str] = Query(None, pattern="^(expense|income)$"),
    current_user: User = Depends(get_current_user)
):
    """
    Get all categories (system + user custom).
    
    - **category_type**: Filter by expense or income (optional)
    """
    categories = FinanceService.get_categories(current_user.id, category_type)
    return categories


@router.post("/categories", response_model=Category, status_code=status.HTTP_201_CREATED)
async def create_category(
    category: CategoryCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a custom category.
    
    - **name**: Category name
    - **type**: expense or income
    - **color**: Hex color code (default: #6B7280)
    - **icon**: Emoji or icon identifier (optional)
    """
    new_category = FinanceService.create_category(current_user.id, category)
    return new_category


# ============================================================================
# TRANSACTION ENDPOINTS
# ============================================================================

@router.get("/transactions")
async def list_transactions(
    account_id: Optional[UUID] = None,
    category_id: Optional[UUID] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    min_amount: Optional[Decimal] = None,
    max_amount: Optional[Decimal] = None,
    search: Optional[str] = None,
    source: Optional[str] = Query(None, pattern="^(manual|ocr|import)$"),
    limit: int = Query(default=100, le=1000),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user)
):
    """
    Get transactions with flexible filtering.
    
    - **account_id**: Filter by account
    - **category_id**: Filter by category
    - **start_date**: Filter from date (YYYY-MM-DD)
    - **end_date**: Filter to date (YYYY-MM-DD)
    - **search**: Search merchant or description
    - **source**: Filter by source (manual, ocr, import)
    - **limit**: Max results (default: 100, max: 1000)
    - **offset**: Pagination offset
    """
    filters = TransactionFilters(
        account_id=account_id,
        category_id=category_id,
        start_date=start_date,
        end_date=end_date,
        min_amount=min_amount,
        max_amount=max_amount,
        search=search,
        source=source,
        limit=limit,
        offset=offset
    )
    transactions = FinanceService.get_transactions(current_user.id, filters)
    return transactions


@router.get("/transactions/{transaction_id}")
async def get_transaction(
    transaction_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """Get a specific transaction by ID"""
    transaction = FinanceService.get_transaction(transaction_id, current_user.id)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    return transaction


@router.post("/transactions", response_model=Transaction, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction: TransactionCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new transaction.
    
    - **account_id**: Account UUID
    - **date**: Transaction date (YYYY-MM-DD)
    - **amount**: Amount (positive for income, negative for expenses)
    - **currency**: ISO currency code (default: CAD)
    - **category_id**: Category UUID (optional)
    - **merchant**: Merchant name (optional)
    - **description**: Transaction description (optional)
    - **source**: manual, ocr, or import (default: manual)
    """
    new_transaction = FinanceService.create_transaction(current_user.id, transaction)
    return new_transaction


@router.patch("/transactions/{transaction_id}", response_model=Transaction)
async def update_transaction(
    transaction_id: UUID,
    transaction: TransactionUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update a transaction (partial update supported)"""
    updated_transaction = FinanceService.update_transaction(
        transaction_id, current_user.id, transaction
    )
    if not updated_transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    return updated_transaction


@router.delete("/transactions/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """Delete a transaction"""
    success = FinanceService.delete_transaction(transaction_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )


# ============================================================================
# ANALYTICS ENDPOINTS
# ============================================================================

@router.get("/analytics/summary", response_model=FinancialSummary)
async def get_financial_summary(
    current_user: User = Depends(get_current_user)
):
    """
    Get high-level financial summary.
    
    Includes:
    - Total balance across all accounts
    - Month-to-date income, expenses, and net flow
    - Account and transaction counts
    - Top spending category
    """
    summary = FinanceService.get_financial_summary(current_user.id)
    return summary


@router.get("/analytics/monthly-burn", response_model=MonthlyBurnRate)
async def get_monthly_burn_rate(
    year: int = Query(..., ge=2000, le=2100),
    month: int = Query(..., ge=1, le=12),
    current_user: User = Depends(get_current_user)
):
    """
    Calculate monthly burn rate for a specific month.
    
    - **year**: Year (e.g., 2025)
    - **month**: Month (1-12)
    
    Returns income, expenses, net flow, and daily burn rate.
    """
    burn_data = FinanceService.calculate_monthly_burn(current_user.id, year, month)
    return burn_data


@router.get("/analytics/category-breakdown", response_model=List[CategoryBreakdown])
async def get_category_breakdown(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Get spending breakdown by category.
    
    - **start_date**: Filter from date (optional, YYYY-MM-DD)
    - **end_date**: Filter to date (optional, YYYY-MM-DD)
    
    Returns categories sorted by spending amount with percentages.
    """
    breakdown = FinanceService.calculate_category_breakdown(
        current_user.id, start_date, end_date
    )
    return breakdown


@router.get("/analytics/runway", response_model=RunwayCalculation)
async def get_runway_calculation(
    emergency_fund_target: Decimal = Query(default=Decimal("50000")),
    current_user: User = Depends(get_current_user)
):
    """
    Calculate runway to emergency fund.
    
    - **emergency_fund_target**: Target amount (default: 50,000 CAD)
    
    Returns current balance, monthly burn rate, and months/days of runway.
    """
    runway = FinanceService.calculate_runway(current_user.id, emergency_fund_target)
    return runway


@router.get("/analytics/average-burn")
async def get_average_burn_rate(
    months: int = Query(default=3, ge=1, le=12),
    current_user: User = Depends(get_current_user)
):
    """
    Calculate average burn rate over last N months.
    
    - **months**: Number of months to average (default: 3)
    
    Returns average daily and monthly spending rate.
    """
    from app.finance.models import AverageBurnRate
    burn_rate = FinanceService.calculate_average_burn_rate(current_user.id, months)
    return burn_rate


@router.get("/analytics/top-discretionary")
async def get_top_discretionary_category(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Get top discretionary spending category (excludes fixed costs like rent, utilities).
    
    - **start_date**: Filter from date (optional)
    - **end_date**: Filter to date (optional)
    
    Returns top category excluding fixed expenses.
    """
    from app.finance.models import TopDiscretionaryCategory
    top_cat = FinanceService.get_top_discretionary_category(current_user.id, start_date, end_date)
    return top_cat


@router.get("/analytics/net-worth-history")
async def get_net_worth_history(
    months: int = Query(default=12, ge=1, le=24),
    current_user: User = Depends(get_current_user)
):
    """
    Get monthly net worth history for last N months.
    
    - **months**: Number of months (default: 12)
    
    Returns monthly net worth snapshots.
    """
    from app.finance.models import NetWorthSnapshot
    history = FinanceService.get_net_worth_history(current_user.id, months)
    return history


# ============================================================================
# HEALTH CHECK
# ============================================================================

@router.get("/health")
async def finance_health_check():
    """Health check endpoint for finance module"""
    return {
        "status": "healthy",
        "module": "finance",
        "version": "1.0.0"
    }


# ============================================================================
# OCR ENDPOINTS
# ============================================================================

@router.post("/ocr/analyze", response_model=OCRResult)
async def analyze_bank_statement(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Upload and analyze bank statement image/PDF to extract transactions.
    
    Accepts: PNG, JPG, JPEG, PDF
    Returns: Proposed transactions with category suggestions
    """
    # Validate file type
    allowed_types = ["image/png", "image/jpeg", "image/jpg", "application/pdf"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_types)}"
        )
    
    # Read file
    file_bytes = await file.read()
    
    # Analyze with OCR
    result = await OCRService.analyze_image(file_bytes, file.content_type)
    
    # Get category map for auto-assignment
    categories = FinanceService.get_categories(current_user.id)
    category_map = {cat["name"].lower(): cat["id"] for cat in categories}
    
    # Assign categories to each transaction
    for txn in result.transactions:
        suggested_category_id = OCRService.infer_category(
            txn.merchant,
            txn.amount,
            category_map
        )
        # Add category_id to transaction (will be in response)
        txn.category_id = suggested_category_id
    
    return result


@router.post("/transactions/batch", response_model=List[Transaction])
async def create_transactions_batch(
    transactions: List[TransactionCreate],
    current_user: User = Depends(get_current_user)
):
    """
    Create multiple transactions at once (batch import).
    
    Used after OCR analysis to import confirmed transactions.
    Updates account balances automatically.
    """
    created_transactions = []
    accounts_to_update = {}  # Track balance changes per account
    
    for txn_data in transactions:
        try:
            new_txn = FinanceService.create_transaction(current_user.id, txn_data)
            created_transactions.append(new_txn)
            
            # Track account balance change
            account_id = str(txn_data.account_id)
            if account_id not in accounts_to_update:
                accounts_to_update[account_id] = Decimal("0")
            
            # Add amount_cad to account balance change
            amount = Decimal(str(new_txn.get("amount_cad", 0)))
            accounts_to_update[account_id] += amount
            
        except Exception as e:
            print(f"Failed to create transaction: {e}")
            continue
    
    # Update account balances
    for account_id, balance_change in accounts_to_update.items():
        try:
            # Get current balance
            account = FinanceService.get_account(UUID(account_id), current_user.id)
            if account:
                current_balance = Decimal(str(account.get("balance", 0)))
                new_balance = current_balance + balance_change
                
                # Update account
                from app.finance.models import AccountUpdate
                FinanceService.update_account(
                    UUID(account_id),
                    current_user.id,
                    AccountUpdate(balance=new_balance)
                )
                print(f"Updated account {account_id} balance: {current_balance} → {new_balance}")
        except Exception as e:
            print(f"Failed to update account balance: {e}")
    
    return created_transactions
