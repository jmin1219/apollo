"""
APOLLO Finance Module - Data Migration Script
Migrates data from CSV files to PostgreSQL database via Supabase client

Usage: python scripts/migrate_finance_data.py

Prerequisites:
- Finance schema and tables created in database
- CSV files in /Documents/professional/finance-tracker/data/
"""

import csv
import os
import sys
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Dict, List, Optional

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from app.db.supabase_client import supabase
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# User ID for all finance data (your test user)
USER_ID = os.getenv("TEST_USER_ID", "80107cd3-82b9-4c36-9981-00418f9b63f8")

# CSV file paths
CSV_BASE_PATH = Path.home() / "Documents" / "professional" / "finance-tracker" / "data"
ACCOUNTS_CSV = CSV_BASE_PATH / "accounts.csv"
EXCHANGE_RATES_CSV = CSV_BASE_PATH / "exchange_rates.csv"
TRANSACTIONS_CSV = CSV_BASE_PATH / "transactions.csv"

# Category mapping (CSV name -> DB category name)
CATEGORY_MAPPING = {
    "Food": "Food & Dining",
    "Income": None,  # Multiple income types, handle specially
    "Entertainment": "Entertainment",
    "Home": "Housing",
    "Development": "Education",  # Map development to education
    "Groceries": "Food & Dining",
    "Utilities": "Utilities",
    "Recreation": "Entertainment",
    "Personal": "Personal Care",
    "Housing": "Housing",
    "Subscriptions": "Entertainment",  # Or could be Education
}

# Income subcategory mapping
INCOME_MAPPING = {
    "interest": "Investment Income",
    "allowance": "Other Income",
    "promo": "Other Income",
    "income": "Other Income",
}


class FinanceMigration:
    """Handles migration of finance data from CSV to PostgreSQL"""

    def __init__(self):
        self.category_id_map: Dict[str, str] = {}
        self.account_id_map: Dict[str, str] = {}

    def load_categories(self):
        """Load category IDs from database"""
        print("\n📂 Loading categories from database...")
        
        # Access finance schema tables using .schema()
        response = supabase.schema("finance").table("categories").select("id, name, type").eq("is_system", True).execute()
        categories = response.data
        
        for cat in categories:
            # Store by name for easy lookup
            self.category_id_map[cat["name"]] = cat["id"]
        
        print(f"✅ Loaded {len(categories)} system categories")
        return categories

    def get_category_id(self, csv_category: str, tags: str = "") -> Optional[str]:
        """Map CSV category string to database category ID"""
        
        # Handle income specially (check tags for specific type)
        if csv_category == "Income":
            tags_lower = tags.lower()
            for keyword, income_type in INCOME_MAPPING.items():
                if keyword in tags_lower:
                    return self.category_id_map.get(income_type)
            # Default to "Other Income"
            return self.category_id_map.get("Other Income")
        
        # Map to database category name
        db_category_name = CATEGORY_MAPPING.get(csv_category)
        
        if db_category_name:
            return self.category_id_map.get(db_category_name)
        
        # If no mapping found, return None (will be uncategorized)
        print(f"⚠️  No category mapping for: {csv_category}")
        return None

    def migrate_accounts(self):
        """Migrate accounts from CSV to database"""
        print("\n💳 Migrating accounts...")
        
        with open(ACCOUNTS_CSV, "r") as f:
            reader = csv.DictReader(f)
            accounts = list(reader)
        
        for acc in accounts:
            # Map account type
            account_type_map = {
                "bank": "checking",
                "investment": "investment",
                "cash": "savings"  # Treat cash as savings
            }
            
            db_type = account_type_map.get(acc["account_type"], "checking")
            
            account_data = {
                "user_id": USER_ID,
                "name": acc["account_name"],
                "type": db_type,
                "default_currency": acc["default_currency"],
                "is_active": True
            }
            
            response = supabase.schema("finance").table("accounts").insert(account_data).execute()
            
            new_id = response.data[0]["id"]
            self.account_id_map[acc["account_id"]] = new_id
            
            print(f"  ✓ Created account: {acc['account_name']} → {new_id}")
        
        print(f"✅ Migrated {len(accounts)} accounts")

    def migrate_exchange_rates(self):
        """Migrate exchange rates from CSV to database"""
        print("\n💱 Migrating exchange rates...")
        
        with open(EXCHANGE_RATES_CSV, "r") as f:
            reader = csv.DictReader(f)
            rates = list(reader)
        
        for rate in rates:
            rate_data = {
                "from_currency": rate["from_currency"],
                "to_currency": rate["to_currency"],
                "rate": float(rate["rate"]),
                "date": rate["date"],
                "source": rate["source"]
            }
            
            # Use upsert to handle duplicates
            response = supabase.schema("finance").table("exchange_rates").upsert(rate_data).execute()
            
            print(f"  ✓ Added rate: {rate['from_currency']} → {rate['to_currency']} = {rate['rate']}")
        
        print(f"✅ Migrated {len(rates)} exchange rates")

    def migrate_transactions(self):
        """Migrate transactions from CSV to database"""
        print("\n💸 Migrating transactions...")
        
        with open(TRANSACTIONS_CSV, "r") as f:
            reader = csv.DictReader(f)
            transactions = list(reader)
        
        # Get exchange rate for KRW→CAD conversion
        krw_to_cad = 0.00098  # From your CSV
        
        success_count = 0
        batch = []
        
        for idx, txn in enumerate(transactions):
            # Get account ID
            account_id = self.account_id_map.get(txn["account_id"])
            if not account_id:
                print(f"  ⚠️  Skipping transaction {txn['id']}: Unknown account {txn['account_id']}")
                continue
            
            # Get category ID
            category_id = self.get_category_id(txn["category"], txn.get("tags", ""))
            
            # Calculate CAD amount
            amount = float(txn["amount"])
            currency = txn["currency"]
            
            if currency == "CAD":
                amount_cad = amount
            elif currency == "KRW":
                amount_cad = amount * krw_to_cad
            else:
                amount_cad = amount  # Default
            
            # Determine merchant/description
            merchant = txn["description"]
            
            txn_data = {
                "user_id": USER_ID,
                "account_id": account_id,
                "date": txn["date"],
                "amount": amount,
                "currency": currency,
                "amount_cad": round(amount_cad, 2),
                "category_id": category_id,
                "merchant": merchant,
                "description": txn["description"],
                "source": "import",  # Mark as imported from CSV
                "notes": txn.get("notes", "")
            }
            
            batch.append(txn_data)
            success_count += 1
            
            # Insert in batches of 10
            if len(batch) >= 10:
                supabase.schema("finance").table("transactions").insert(batch).execute()
                print(f"  📊 Progress: {idx + 1}/{len(transactions)} transactions")
                batch = []
        
        # Insert remaining transactions
        if batch:
            supabase.schema("finance").table("transactions").insert(batch).execute()
        
        print(f"✅ Migrated {success_count}/{len(transactions)} transactions")

    def verify_migration(self):
        """Verify the migration was successful"""
        print("\n🔍 Verifying migration...")
        
        # Check accounts
        response = supabase.schema("finance").table("accounts").select("id", count="exact").eq("user_id", USER_ID).execute()
        account_count = response.count
        print(f"  ✓ Accounts: {account_count}")
        
        # Check transactions
        response = supabase.schema("finance").table("transactions").select("id", count="exact").eq("user_id", USER_ID).execute()
        txn_count = response.count
        print(f"  ✓ Transactions: {txn_count}")
        
        # Check exchange rates
        response = supabase.schema("finance").table("exchange_rates").select("id", count="exact").execute()
        rate_count = response.count
        print(f"  ✓ Exchange rates: {rate_count}")
        
        # Show total spending
        response = supabase.schema("finance").table("transactions").select("amount_cad").eq("user_id", USER_ID).execute()
        transactions = response.data
        
        total_expenses = sum(float(t["amount_cad"]) for t in transactions if float(t["amount_cad"]) < 0)
        total_income = sum(float(t["amount_cad"]) for t in transactions if float(t["amount_cad"]) > 0)
        
        print(f"  ✓ Total expenses: ${abs(total_expenses):,.2f} CAD")
        print(f"  ✓ Total income: ${total_income:,.2f} CAD")
        print(f"  ✓ Net flow: ${total_income + total_expenses:,.2f} CAD")
        
        print("\n✅ Migration verification complete!")

    def run(self):
        """Run the full migration"""
        try:
            print("🔌 Testing database connection...")
            # Test connection by fetching categories from finance schema
            test = supabase.schema("finance").table("categories").select("id", count="exact").limit(1).execute()
            print(f"✅ Connected to database (found {test.count} categories in finance schema)")
            
            self.load_categories()
            self.migrate_accounts()
            self.migrate_exchange_rates()
            self.migrate_transactions()
            self.verify_migration()
        except Exception as e:
            print(f"\n❌ Migration failed: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    print("=" * 60)
    print("APOLLO Finance Module - Data Migration")
    print("=" * 60)
    
    # Check if CSV files exist
    if not ACCOUNTS_CSV.exists():
        print(f"❌ Accounts CSV not found: {ACCOUNTS_CSV}")
        sys.exit(1)
    
    if not TRANSACTIONS_CSV.exists():
        print(f"❌ Transactions CSV not found: {TRANSACTIONS_CSV}")
        sys.exit(1)
    
    print(f"\n📂 CSV files found:")
    print(f"  • Accounts: {ACCOUNTS_CSV}")
    print(f"  • Exchange rates: {EXCHANGE_RATES_CSV}")
    print(f"  • Transactions: {TRANSACTIONS_CSV}")
    
    # Confirm before proceeding
    response = input("\n⚠️  This will import data into the database. Continue? (yes/no): ")
    
    if response.lower() != "yes":
        print("❌ Migration cancelled")
        sys.exit(0)
    
    # Run migration
    migration = FinanceMigration()
    migration.run()
    
    print("\n" + "=" * 60)
    print("✅ Migration complete!")
    print("=" * 60)
