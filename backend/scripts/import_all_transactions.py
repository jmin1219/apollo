"""
APOLLO Finance - Complete Transaction Import
Imports all transactions from bank statements (Aug-Nov 2025)

Usage: python scripts/import_all_transactions.py
"""

import os
import sys
from datetime import datetime, date
from decimal import Decimal
from pathlib import Path
from typing import Dict, List, Optional

sys.path.append(str(Path(__file__).parent.parent))

from app.db.supabase_client import supabase
from dotenv import load_dotenv

load_dotenv()

USER_ID = os.getenv("TEST_USER_ID", "80107cd3-82b9-4c36-9981-00418f9b63f8")
KRW_TO_CAD_RATE = 0.00098  # Exchange rate

# Get category IDs
def get_category_map():
    """Load category name -> ID mapping"""
    response = supabase.schema("finance").table("categories").select("id, name, type").eq("is_system", True).execute()
    
    category_map = {}
    for cat in response.data:
        category_map[cat["name"].lower()] = cat["id"]
    
    return category_map

# Get account IDs
def get_account_map():
    """Load account name -> ID mapping"""
    response = supabase.schema("finance").table("accounts").select("id, name").eq("user_id", USER_ID).execute()
    
    account_map = {}
    for acc in response.data:
        # Map by partial name for easier matching
        if "Scotia" in acc["name"]:
            account_map["scotiabank"] = acc["id"]
        elif "Toss" in acc["name"]:
            account_map["toss"] = acc["id"]
        elif "Cash" in acc["name"]:
            account_map["cash"] = acc["id"]
        elif "ISA" in acc["name"]:
            account_map["isa"] = acc["id"]
    
    return account_map


# ============================================================================
# SCOTIABANK TRANSACTIONS (Aug 25 - Nov 1, 2025)
# ============================================================================

SCOTIABANK_TRANSACTIONS = [
    # === AUGUST 2025 ===
    {"date": "2025-08-25", "amount": 8700.00, "merchant": "Wire Transfer", "description": "Initial deposit", "category": "other income"},
    {"date": "2025-08-26", "amount": 990.00, "merchant": "Chang Wonjae", "description": "Wire Payment - Allowance", "category": "other income"},
    {"date": "2025-08-26", "amount": -15.00, "merchant": "Scotiabank", "description": "ScotiaWire/MTS Fee", "category": "utilities"},
    {"date": "2025-08-26", "amount": -100.00, "merchant": "Uber Canada", "description": "Uber Cash", "category": "transit"},
    {"date": "2025-08-27", "amount": -704.45, "merchant": "Guard.Me International", "description": "Insurance", "category": "insurance"},
    {"date": "2025-08-28", "amount": -1.44, "merchant": "Apple.com/bill", "description": "Apple subscription", "category": "subscriptions"},
    {"date": "2025-08-30", "amount": -5.00, "merchant": "Uber Eats", "description": "Food delivery", "category": "dining out"},
    
    # === SEPTEMBER 2025 ===
    {"date": "2025-09-02", "amount": -30.70, "merchant": "Uber Eats", "description": "Food delivery", "category": "dining out"},
    {"date": "2025-09-02", "amount": -3000.00, "merchant": "Interac e-Transfer", "description": "Rent payment 1/2", "category": "rent"},
    {"date": "2025-09-02", "amount": -700.00, "merchant": "Interac e-Transfer", "description": "Rent payment 2/2", "category": "rent"},
    {"date": "2025-09-02", "amount": -147.17, "merchant": "Telus Corp", "description": "Phone bill", "category": "utilities"},
    {"date": "2025-09-03", "amount": 87990.00, "merchant": "Chang Wonjae", "description": "Wire Payment - Family Support", "category": "other income"},
    {"date": "2025-09-03", "amount": -15.00, "merchant": "Scotiabank", "description": "ScotiaWire/MTS Fee", "category": "utilities"},
    {"date": "2025-09-03", "amount": -284.69, "merchant": "BC Hydro", "description": "Electricity bill", "category": "utilities"},
    {"date": "2025-09-05", "amount": 10174.62, "merchant": "ISP International", "description": "Tuition reimbursement 1/2", "category": "other income"},
    {"date": "2025-09-05", "amount": 10174.62, "merchant": "ISP International", "description": "Tuition reimbursement 2/2", "category": "other income"},
    {"date": "2025-09-06", "amount": -43.29, "merchant": "Uber Eats", "description": "Food delivery", "category": "dining out"},
    {"date": "2025-09-08", "amount": -29.36, "merchant": "DoorDash", "description": "Food delivery", "category": "dining out"},
    {"date": "2025-09-08", "amount": -138.09, "merchant": "BC Liquor #233", "description": "Alcohol", "category": "shopping"},
    {"date": "2025-09-08", "amount": -727.99, "merchant": "Amazon", "description": "Online shopping", "category": "electronics"},
    {"date": "2025-09-08", "amount": -144.70, "merchant": "Uber", "description": "Transportation", "category": "transit"},
    {"date": "2025-09-15", "amount": -1.00, "merchant": "Google YouTube Premium", "description": "YouTube subscription (error then corrected)", "category": "subscriptions"},
    {"date": "2025-09-15", "amount": 1.00, "merchant": "Google YouTube Premium", "description": "Error correction", "category": "subscriptions"},
    {"date": "2025-09-20", "amount": -8.95, "merchant": "Google YouTube Premium", "description": "YouTube subscription", "category": "subscriptions"},
    {"date": "2025-09-27", "amount": -2000.00, "merchant": "Interac e-Transfer", "description": "Rent payment 1/2", "category": "rent"},
    {"date": "2025-09-29", "amount": -1.44, "merchant": "Apple.com/bill", "description": "Apple subscription", "category": "subscriptions"},
    {"date": "2025-09-29", "amount": -1700.00, "merchant": "Interac e-Transfer", "description": "Rent payment 2/2", "category": "rent"},
    
    # === OCTOBER 2025 (Oct 21-31 from screenshots) ===
    # Oct 1-20 already in database via CSV import
    {"date": "2025-10-20", "amount": -30.10, "merchant": "Coal Harbour Liquor", "description": "Alcohol", "category": "shopping"},
    {"date": "2025-10-20", "amount": -8.95, "merchant": "Google YouTube Premium", "description": "YouTube subscription", "category": "subscriptions"},
    {"date": "2025-10-22", "amount": -7.00, "merchant": "Famous Player", "description": "Movie theater", "category": "entertainment"},
    {"date": "2025-10-23", "amount": -25.21, "merchant": "Cineplex Entertainment", "description": "Movie theater", "category": "entertainment"},
    {"date": "2025-10-27", "amount": -1850.00, "merchant": "Interac e-Transfer", "description": "Rent payment 1/2", "category": "rent"},
    {"date": "2025-10-27", "amount": -1850.00, "merchant": "Interac e-Transfer", "description": "Rent payment 2/2", "category": "rent"},
    {"date": "2025-10-27", "amount": -150.16, "merchant": "Swapped.com", "description": "Gambling", "category": "entertainment"},
    {"date": "2025-10-28", "amount": -1.44, "merchant": "Apple.com/bill", "description": "Apple subscription", "category": "subscriptions"},
    {"date": "2025-10-28", "amount": -45.00, "merchant": "BC Hydro", "description": "Electricity bill", "category": "utilities"},
    
    # === NOVEMBER 2025 ===
    {"date": "2025-11-01", "amount": -10.49, "merchant": "DoorDash", "description": "DoorDash Pass subscription", "category": "subscriptions"},
]

# ============================================================================
# TOSS BANK TRANSACTIONS (Sep 10 - Nov 2, 2025)
# ============================================================================

TOSS_TRANSACTIONS = [
    # === SEPTEMBER 2025 ===
    {"date": "2025-09-13", "amount": -39149, "merchant": "DoorDash", "description": "DD/DOORDASHBIG", "category": "dining out"},
    {"date": "2025-09-13", "amount": 13469, "merchant": "Currency Exchange", "description": "USD 팔기 (Sell USD)", "category": "other income"},
    {"date": "2025-09-13", "amount": -502355, "merchant": "Currency Exchange", "description": "CAD 사기 (Buy CAD)", "category": "other income"},  # Net neutral with above
    {"date": "2025-09-19", "amount": 2, "merchant": "Toss Bank", "description": "Cash Back", "category": "other income"},
    {"date": "2025-09-21", "amount": -17821, "merchant": "DoorDash", "description": "DD/DOORDASHDON", "category": "dining out"},
    {"date": "2025-09-21", "amount": -83690, "merchant": "Basketball Monthly", "description": "BASKETBALL MON", "category": "gym & sports"},
    {"date": "2025-09-22", "amount": 248, "merchant": "Toss Bank", "description": "Interest", "category": "investment income"},
    {"date": "2025-09-22", "amount": -10372, "merchant": "Perfecto Coffee", "description": "SQ *PERFECTO C", "category": "coffee & drinks"},
    {"date": "2025-09-23", "amount": 1000000, "merchant": "Chang Wonjae", "description": "장원재 - Allowance", "category": "other income"},
    {"date": "2025-09-25", "amount": 75, "merchant": "Toss Bank", "description": "Interest", "category": "investment income"},
    {"date": "2025-09-25", "amount": 2, "merchant": "Toss Bank", "description": "Cash Back", "category": "other income"},
    {"date": "2025-09-25", "amount": -40825, "merchant": "DoorDash", "description": "DD/DOORDASHTHA", "category": "dining out"},
    {"date": "2025-09-26", "amount": -153947, "merchant": "DoorDash", "description": "DD/DOORDASHYOU", "category": "dining out"},
    {"date": "2025-09-26", "amount": -56838, "merchant": "Safeway", "description": "SAFEWAY #4908", "category": "groceries"},
    {"date": "2025-09-26", "amount": -29665, "merchant": "BC Liquor", "description": "BC LIQUOR#233", "category": "shopping"},
    {"date": "2025-09-30", "amount": -261798, "merchant": "Uniqlo Canada", "description": "UniqloCanada", "category": "clothing"},
    {"date": "2025-09-30", "amount": -123961, "merchant": "DoorDash", "description": "DD/DOORDASHYOU", "category": "dining out"},
    
    # === OCTOBER 2025 ===
    # Oct 1-20 already in database via CSV
    # Adding Oct 21-31 + early Nov from Toss statement
    {"date": "2025-10-19", "amount": 2, "merchant": "Toss Bank", "description": "Cash Back", "category": "other income"},
    {"date": "2025-10-23", "amount": 1000000, "merchant": "Chang Wonjae", "description": "장원재 - Allowance", "category": "other income"},
    {"date": "2025-10-26", "amount": -123390, "merchant": "DoorDash", "description": "DD/DOORDASHIGA - Groceries", "category": "groceries"},
    {"date": "2025-10-26", "amount": -2780, "merchant": "DoorDash", "description": "DD/DOORDASHIGA - Groceries", "category": "groceries"},
    {"date": "2025-10-26", "amount": -57565, "merchant": "DoorDash", "description": "DD/DOORDASHBRO", "category": "dining out"},
    
    # === NOVEMBER 2025 ===
    {"date": "2025-11-01", "amount": 169, "merchant": "Toss Bank", "description": "Interest", "category": "investment income"},
    {"date": "2025-11-02", "amount": -29367, "merchant": "DoorDash", "description": "DD/DOORDASHPHN", "category": "dining out"},
]


def import_transactions():
    """Import all transactions and calculate balances"""
    print("\n📊 Starting complete transaction import...")
    
    # Get mappings
    category_map = get_category_map()
    account_map = get_account_map()
    
    print(f"✅ Loaded {len(category_map)} categories")
    print(f"✅ Loaded {len(account_map)} accounts")
    
    # Check what's already in database
    response = supabase.schema("finance").table("transactions").select("date, merchant, amount_cad", count="exact").eq("user_id", USER_ID).execute()
    existing_count = response.count
    print(f"\n📝 Current database: {existing_count} transactions")
    
    # Confirm before proceeding
    print("\n⚠️  This will import:")
    print(f"  • {len(SCOTIABANK_TRANSACTIONS)} Scotiabank transactions (Aug 25 - Nov 1)")
    print(f"  • {len(TOSS_TRANSACTIONS)} Toss Bank transactions (Sep 10 - Nov 2)")
    print(f"  • Skip duplicates that already exist")
    
    confirm = input("\nContinue? (yes/no): ")
    if confirm.lower() != "yes":
        print("❌ Import cancelled")
        return
    
    # Import Scotiabank transactions
    print("\n🏦 Importing Scotiabank transactions...")
    scotiabank_id = account_map["scotiabank"]
    imported_scotia = 0
    skipped_scotia = 0
    
    for txn in SCOTIABANK_TRANSACTIONS:
        category_id = category_map.get(txn["category"].lower())
        
        txn_data = {
            "user_id": USER_ID,
            "account_id": scotiabank_id,
            "date": txn["date"],
            "amount": float(txn["amount"]),
            "currency": "CAD",
            "amount_cad": float(txn["amount"]),
            "category_id": category_id,
            "merchant": txn["merchant"],
            "description": txn["description"],
            "source": "import",
            "notes": ""
        }
        
        try:
            supabase.schema("finance").table("transactions").insert(txn_data).execute()
            imported_scotia += 1
            if imported_scotia % 5 == 0:
                print(f"  Progress: {imported_scotia}/{len(SCOTIABANK_TRANSACTIONS)}")
        except Exception as e:
            # Likely duplicate - skip
            if "duplicate" in str(e).lower() or "unique" in str(e).lower():
                skipped_scotia += 1
            else:
                print(f"  ❌ Error: {txn['date']} {txn['merchant']} - {e}")
    
    print(f"✅ Imported {imported_scotia} new Scotiabank transactions")
    if skipped_scotia > 0:
        print(f"  ⏭️  Skipped {skipped_scotia} duplicates")
    
    # Import Toss Bank transactions
    print("\n🇰🇷 Importing Toss Bank transactions...")
    toss_id = account_map["toss"]
    imported_toss = 0
    skipped_toss = 0
    
    for txn in TOSS_TRANSACTIONS:
        category_id = category_map.get(txn["category"].lower())
        amount_krw = float(txn["amount"])
        amount_cad = amount_krw * KRW_TO_CAD_RATE
        
        txn_data = {
            "user_id": USER_ID,
            "account_id": toss_id,
            "date": txn["date"],
            "amount": amount_krw,
            "currency": "KRW",
            "amount_cad": round(amount_cad, 2),
            "category_id": category_id,
            "merchant": txn["merchant"],
            "description": txn["description"],
            "source": "import",
            "notes": ""
        }
        
        try:
            supabase.schema("finance").table("transactions").insert(txn_data).execute()
            imported_toss += 1
        except Exception as e:
            if "duplicate" in str(e).lower() or "unique" in str(e).lower():
                skipped_toss += 1
            else:
                print(f"  ❌ Error: {txn['date']} {txn['merchant']} - {e}")
    
    print(f"✅ Imported {imported_toss} new Toss Bank transactions")
    if skipped_toss > 0:
        print(f"  ⏭️  Skipped {skipped_toss} duplicates")
    
    # Calculate and update balances
    print("\n💰 Calculating account balances from transactions...")
    
    # Scotiabank balance (sum of all CAD transactions)
    response = supabase.schema("finance").table("transactions").select("amount_cad").eq("user_id", USER_ID).eq("account_id", scotiabank_id).execute()
    scotia_balance = sum(float(t["amount_cad"]) for t in response.data)
    
    supabase.schema("finance").table("accounts").update({"balance": round(scotia_balance, 2)}).eq("id", scotiabank_id).execute()
    print(f"  ✓ Scotiabank: ${scotia_balance:,.2f} CAD (calculated from {len(response.data)} transactions)")
    
    # Toss Bank balance (sum of all KRW transactions converted to CAD)
    response = supabase.schema("finance").table("transactions").select("amount_cad").eq("user_id", USER_ID).eq("account_id", toss_id).execute()
    toss_balance = sum(float(t["amount_cad"]) for t in response.data)
    
    supabase.schema("finance").table("accounts").update({"balance": round(toss_balance, 2)}).eq("id", toss_id).execute()
    print(f"  ✓ Toss Korea: ${toss_balance:,.2f} CAD (calculated from {len(response.data)} transactions)")
    print(f"    (Actual KRW balance: 116,904 ≈ ${116904 * KRW_TO_CAD_RATE:,.2f} CAD)")
    
    # Cash balance (static, current value)
    cash_id = account_map["cash"]
    supabase.schema("finance").table("accounts").update({"balance": 9065.00}).eq("id", cash_id).execute()
    print(f"  ✓ Cash: $9,065.00 CAD (current, no transaction history)")
    
    # Korean ISA (investment account)
    isa_id = account_map["isa"]
    isa_balance_cad = round(60770230 * KRW_TO_CAD_RATE, 2)
    supabase.schema("finance").table("accounts").update({"balance": isa_balance_cad}).eq("id", isa_id).execute()
    print(f"  ✓ Korean ISA: ${isa_balance_cad:,.2f} CAD (60,770,230 KRW)")
    print(f"    Initial investment: 53,042,135 KRW | Gain: +14.6% 📈")
    
    # Final verification
    print("\n🔍 Final verification...")
    response = supabase.schema("finance").table("transactions").select("id", count="exact").eq("user_id", USER_ID).execute()
    final_count = response.count
    print(f"  ✓ Total transactions: {final_count}")
    
    response = supabase.schema("finance").table("accounts").select("name, balance, default_currency").eq("user_id", USER_ID).execute()
    total_balance = sum(float(acc["balance"]) for acc in response.data)
    
    print(f"\n💎 Account Summary:")
    for acc in response.data:
        print(f"  • {acc['name']}: ${float(acc['balance']):,.2f} {acc['default_currency']}")
    
    print(f"\n  🎯 Total Net Worth: ${total_balance:,.2f} CAD")
    
    print("\n✅ Import complete!")


if __name__ == "__main__":
    print("=" * 60)
    print("APOLLO Finance - Complete Transaction Import")
    print("=" * 60)
    
    print("\n🔌 Testing database connection...")
    try:
        test = supabase.schema("finance").table("categories").select("id", count="exact").limit(1).execute()
        print("✅ Connected to database")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        sys.exit(1)
    
    import_transactions()
    
    print("\n" + "=" * 60)
    print("✅ All transactions imported and balances calculated!")
    print("=" * 60)
