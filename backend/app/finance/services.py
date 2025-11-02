"""
Finance Module - Service Layer

Business logic for finance operations and analytics.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional, Dict, Any
from uuid import UUID
from calendar import monthrange

from app.db.supabase_client import supabase
from app.finance.models import (
    Account, AccountCreate, AccountUpdate,
    Transaction, TransactionCreate, TransactionUpdate, TransactionWithDetails,
    Category, CategoryCreate,
    MonthlyBurnRate, CategoryBreakdown, RunwayCalculation, FinancialSummary,
    TransactionFilters
)


class FinanceService:
    """Service class for all finance operations"""

    # ========================================================================
    # ACCOUNT OPERATIONS
    # ========================================================================

    @staticmethod
    def get_accounts(user_id: UUID, include_inactive: bool = False) -> List[Dict[str, Any]]:
        """Get all accounts for a user"""
        query = supabase.schema("finance").table("accounts").select("*").eq("user_id", str(user_id))
        
        if not include_inactive:
            query = query.eq("is_active", True)
        
        query = query.order("created_at", desc=False)
        response = query.execute()
        return response.data

    @staticmethod
    def get_account(account_id: UUID, user_id: UUID) -> Optional[Dict[str, Any]]:
        """Get a specific account"""
        response = (
            supabase.schema("finance")
            .table("accounts")
            .select("*")
            .eq("id", str(account_id))
            .eq("user_id", str(user_id))
            .execute()
        )
        return response.data[0] if response.data else None

    @staticmethod
    def create_account(user_id: UUID, account_data: AccountCreate) -> Dict[str, Any]:
        """Create a new account"""
        data = account_data.model_dump()
        data["user_id"] = str(user_id)
        data["balance"] = float(data.get("balance", 0))
        
        response = supabase.schema("finance").table("accounts").insert(data).execute()
        return response.data[0]

    @staticmethod
    def update_account(account_id: UUID, user_id: UUID, account_data: AccountUpdate) -> Optional[Dict[str, Any]]:
        """Update an account"""
        # First verify ownership
        existing = FinanceService.get_account(account_id, user_id)
        if not existing:
            return None
        
        # Prepare update data (only include non-None fields)
        update_data = {k: v for k, v in account_data.model_dump().items() if v is not None}
        if "balance" in update_data:
            update_data["balance"] = float(update_data["balance"])
        
        if not update_data:
            return existing
        
        response = (
            supabase.schema("finance")
            .table("accounts")
            .update(update_data)
            .eq("id", str(account_id))
            .eq("user_id", str(user_id))
            .execute()
        )
        return response.data[0] if response.data else None

    @staticmethod
    def delete_account(account_id: UUID, user_id: UUID) -> bool:
        """Delete an account (soft delete by marking inactive)"""
        result = FinanceService.update_account(
            account_id, user_id, AccountUpdate(is_active=False)
        )
        return result is not None

    # ========================================================================
    # CATEGORY OPERATIONS
    # ========================================================================

    @staticmethod
    def get_categories(user_id: Optional[UUID] = None, category_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get categories (system + user custom)"""
        query = supabase.schema("finance").table("categories").select("*")
        
        # Include system categories OR user's custom categories
        if user_id:
            query = query.or_(f"is_system.eq.true,user_id.eq.{str(user_id)}")
        else:
            query = query.eq("is_system", True)
        
        if category_type:
            query = query.eq("type", category_type)
        
        query = query.order("name", desc=False)
        response = query.execute()
        return response.data

    @staticmethod
    def create_category(user_id: UUID, category_data: CategoryCreate) -> Dict[str, Any]:
        """Create a custom category"""
        data = category_data.model_dump()
        data["user_id"] = str(user_id)
        data["is_system"] = False
        
        response = supabase.schema("finance").table("categories").insert(data).execute()
        return response.data[0]

    # ========================================================================
    # TRANSACTION OPERATIONS
    # ========================================================================

    @staticmethod
    def get_transactions(user_id: UUID, filters: TransactionFilters) -> List[Dict[str, Any]]:
        """Get transactions with filters"""
        query = (
            supabase.schema("finance")
            .table("transactions")
            .select("*, accounts(name), categories(name, color)")
            .eq("user_id", str(user_id))
        )
        
        # Apply filters
        if filters.account_id:
            query = query.eq("account_id", str(filters.account_id))
        
        if filters.category_id:
            query = query.eq("category_id", str(filters.category_id))
        
        if filters.start_date:
            query = query.gte("date", str(filters.start_date))
        
        if filters.end_date:
            query = query.lte("date", str(filters.end_date))
        
        if filters.source:
            query = query.eq("source", filters.source)
        
        if filters.search:
            # Search in merchant or description
            query = query.or_(f"merchant.ilike.%{filters.search}%,description.ilike.%{filters.search}%")
        
        # Order by date descending (most recent first)
        query = query.order("date", desc=True).order("created_at", desc=True)
        
        # Pagination
        query = query.range(filters.offset, filters.offset + filters.limit - 1)
        
        response = query.execute()
        return response.data

    @staticmethod
    def get_transaction(transaction_id: UUID, user_id: UUID) -> Optional[Dict[str, Any]]:
        """Get a specific transaction"""
        response = (
            supabase.schema("finance")
            .table("transactions")
            .select("*, accounts(name), categories(name, color)")
            .eq("id", str(transaction_id))
            .eq("user_id", str(user_id))
            .execute()
        )
        return response.data[0] if response.data else None

    @staticmethod
    def create_transaction(user_id: UUID, transaction_data: TransactionCreate) -> Dict[str, Any]:
        """Create a new transaction"""
        data = transaction_data.model_dump()
        data["user_id"] = str(user_id)
        data["amount"] = float(data["amount"])
        
        # Convert UUID fields to strings
        if data.get("account_id"):
            data["account_id"] = str(data["account_id"])
        if data.get("category_id"):
            data["category_id"] = str(data["category_id"])
        
        # Convert date to string
        if isinstance(data.get("date"), date):
            data["date"] = data["date"].isoformat()
        
        # Auto-calculate amount_cad if not provided
        if data.get("amount_cad") is None:
            if data["currency"] == "CAD":
                data["amount_cad"] = data["amount"]
            else:
                # For now, you'd need to fetch exchange rate
                # Simplified: just use amount as-is
                data["amount_cad"] = data["amount"]
        else:
            data["amount_cad"] = float(data["amount_cad"])
        
        response = supabase.schema("finance").table("transactions").insert(data).execute()
        return response.data[0]

    @staticmethod
    def update_transaction(transaction_id: UUID, user_id: UUID, transaction_data: TransactionUpdate) -> Optional[Dict[str, Any]]:
        """Update a transaction"""
        # Verify ownership
        existing = FinanceService.get_transaction(transaction_id, user_id)
        if not existing:
            return None
        
        # Prepare update data (exclude unset fields)
        update_data = transaction_data.model_dump(exclude_unset=True)
        
        # If account changes, update currency to match new account
        if "account_id" in update_data:
            account_id_value = update_data["account_id"]
            # Handle both UUID and string types
            if isinstance(account_id_value, str):
                account_id_value = UUID(account_id_value)
            new_account = FinanceService.get_account(account_id_value, user_id)
            if new_account:
                update_data["currency"] = new_account["default_currency"]
        
        if "amount" in update_data:
            update_data["amount"] = float(update_data["amount"])
            
            # Auto-calculate amount_cad when amount changes
            currency = update_data.get("currency", existing.get("currency", "CAD"))
            if currency == "CAD":
                update_data["amount_cad"] = update_data["amount"]
            elif currency == "KRW":
                # Use exchange rate 0.00098 for KRW to CAD
                update_data["amount_cad"] = update_data["amount"] * 0.00098
            else:
                # For other currencies, just use amount as-is for now
                update_data["amount_cad"] = update_data["amount"]
        
        if "amount_cad" in update_data:
            update_data["amount_cad"] = float(update_data["amount_cad"])
        
        # Convert UUID fields to strings
        if "account_id" in update_data:
            update_data["account_id"] = str(update_data["account_id"])
        if "category_id" in update_data:
            update_data["category_id"] = str(update_data["category_id"]) if update_data["category_id"] else None
        
        # Convert date to string
        if "date" in update_data and isinstance(update_data["date"], date):
            update_data["date"] = update_data["date"].isoformat()
        
        if not update_data:
            return existing
        
        # Update the transaction
        response = (
            supabase.schema("finance")
            .table("transactions")
            .update(update_data)
            .eq("id", str(transaction_id))
            .eq("user_id", str(user_id))
            .execute()
        )
        
        # Return fresh data with joins
        if response.data:
            return FinanceService.get_transaction(transaction_id, user_id)
        return None

    @staticmethod
    def delete_transaction(transaction_id: UUID, user_id: UUID) -> bool:
        """Delete a transaction"""
        # Verify ownership first
        existing = FinanceService.get_transaction(transaction_id, user_id)
        if not existing:
            return False
        
        response = (
            supabase.schema("finance")
            .table("transactions")
            .delete()
            .eq("id", str(transaction_id))
            .eq("user_id", str(user_id))
            .execute()
        )
        return len(response.data) > 0

    # ========================================================================
    # ANALYTICS OPERATIONS
    # ========================================================================

    @staticmethod
    def calculate_monthly_burn(user_id: UUID, year: int, month: int) -> MonthlyBurnRate:
        """Calculate monthly burn rate"""
        # Get date range for the month
        _, last_day = monthrange(year, month)
        start_date = date(year, month, 1)
        end_date = date(year, month, last_day)
        
        # Get all transactions for the month
        filters = TransactionFilters(start_date=start_date, end_date=end_date, limit=1000)
        transactions = FinanceService.get_transactions(user_id, filters)
        
        total_income = sum(
            Decimal(str(t["amount_cad"])) for t in transactions 
            if Decimal(str(t["amount_cad"])) > 0
        )
        total_expenses = sum(
            abs(Decimal(str(t["amount_cad"]))) for t in transactions 
            if Decimal(str(t["amount_cad"])) < 0
        )
        net_flow = total_income - total_expenses
        
        # Calculate daily burn rate
        days_in_month = last_day
        burn_rate = total_expenses / Decimal(str(days_in_month)) if days_in_month > 0 else Decimal("0")
        
        return MonthlyBurnRate(
            month=f"{year}-{month:02d}",
            total_income=total_income,
            total_expenses=total_expenses,
            net_flow=net_flow,
            burn_rate=burn_rate,
            transaction_count=len(transactions)
        )

    @staticmethod
    def calculate_category_breakdown(user_id: UUID, start_date: Optional[date] = None, 
                                     end_date: Optional[date] = None) -> List[CategoryBreakdown]:
        """Calculate spending breakdown by category"""
        filters = TransactionFilters(start_date=start_date, end_date=end_date, limit=1000)
        transactions = FinanceService.get_transactions(user_id, filters)
        
        # Filter only expenses
        expenses = [t for t in transactions if Decimal(str(t["amount_cad"])) < 0]
        
        # Group by category
        category_totals: Dict[str, Dict[str, Any]] = {}
        total_spending = Decimal("0")
        
        for txn in expenses:
            amount = abs(Decimal(str(txn["amount_cad"])))
            total_spending += amount
            
            cat_id = txn.get("category_id")
            cat_name = txn["categories"]["name"] if txn.get("categories") else "Uncategorized"
            cat_color = txn["categories"]["color"] if txn.get("categories") else "#6B7280"
            
            key = cat_id or "uncategorized"
            
            if key not in category_totals:
                category_totals[key] = {
                    "category_id": cat_id,
                    "category_name": cat_name,
                    "category_color": cat_color,
                    "total_amount": Decimal("0"),
                    "transaction_count": 0
                }
            
            category_totals[key]["total_amount"] += amount
            category_totals[key]["transaction_count"] += 1
        
        # Calculate percentages and create response
        breakdown = []
        for cat_data in category_totals.values():
            percentage = (float(cat_data["total_amount"]) / float(total_spending) * 100) if total_spending > 0 else 0
            breakdown.append(
                CategoryBreakdown(
                    category_id=cat_data["category_id"],
                    category_name=cat_data["category_name"],
                    category_color=cat_data["category_color"],
                    total_amount=cat_data["total_amount"],
                    transaction_count=cat_data["transaction_count"],
                    percentage=round(percentage, 2)
                )
            )
        
        # Sort by total amount descending
        breakdown.sort(key=lambda x: x.total_amount, reverse=True)
        return breakdown

    @staticmethod
    def calculate_runway(user_id: UUID, emergency_fund_target: Decimal = Decimal("50000")) -> RunwayCalculation:
        """Calculate runway to emergency fund"""
        # Get current balance across all accounts
        accounts = FinanceService.get_accounts(user_id, include_inactive=False)
        current_balance = sum(Decimal(str(acc.get("balance", 0))) for acc in accounts)
        
        # Get last 3 months burn rate for average
        today = date.today()
        year = today.year
        month = today.month
        
        burn_rates = []
        for i in range(3):
            m = month - i
            y = year
            if m <= 0:
                m += 12
                y -= 1
            
            burn_data = FinanceService.calculate_monthly_burn(user_id, y, m)
            burn_rates.append(burn_data.burn_rate)
        
        avg_monthly_burn = sum(burn_rates) / Decimal(str(len(burn_rates))) if burn_rates else Decimal("0")
        
        # Calculate runway
        if avg_monthly_burn > 0:
            months_of_runway = float(current_balance / avg_monthly_burn)
            days_of_runway = int(months_of_runway * 30)
        else:
            months_of_runway = None
            days_of_runway = None
        
        target_reached = current_balance >= emergency_fund_target
        
        return RunwayCalculation(
            current_balance=current_balance,
            monthly_burn_rate=avg_monthly_burn,
            emergency_fund_target=emergency_fund_target,
            months_of_runway=months_of_runway,
            days_of_runway=days_of_runway,
            target_reached=target_reached
        )

    @staticmethod
    def get_financial_summary(user_id: UUID) -> FinancialSummary:
        """Get high-level financial summary"""
        # Current month
        today = date.today()
        start_of_month = date(today.year, today.month, 1)
        
        # Get accounts
        accounts = FinanceService.get_accounts(user_id, include_inactive=False)
        total_balance = sum(Decimal(str(acc.get("balance", 0))) for acc in accounts)
        
        # Get month-to-date transactions
        filters = TransactionFilters(start_date=start_of_month, limit=1000)
        transactions = FinanceService.get_transactions(user_id, filters)
        
        total_income_mtd = sum(
            Decimal(str(t["amount_cad"])) for t in transactions 
            if Decimal(str(t["amount_cad"])) > 0
        )
        total_expenses_mtd = sum(
            abs(Decimal(str(t["amount_cad"]))) for t in transactions 
            if Decimal(str(t["amount_cad"])) < 0
        )
        net_flow_mtd = total_income_mtd - total_expenses_mtd
        
        # Get top spending category
        category_breakdown = FinanceService.calculate_category_breakdown(user_id, start_of_month)
        top_category = category_breakdown[0] if category_breakdown else None
        
        return FinancialSummary(
            total_balance=total_balance,
            total_income_mtd=total_income_mtd,
            total_expenses_mtd=total_expenses_mtd,
            net_flow_mtd=net_flow_mtd,
            account_count=len(accounts),
            transaction_count_mtd=len(transactions),
            top_category=top_category.category_name if top_category else None,
            top_category_amount=top_category.total_amount if top_category else None
        )
