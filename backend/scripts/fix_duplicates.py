"""
APOLLO Finance - Remove Duplicate Transactions and Recalculate Balances

This script removes duplicate transactions that were imported twice
and recalculates account balances correctly.

Usage: python scripts/fix_duplicates.py
"""

import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.db.supabase_client import supabase
from dotenv import load_dotenv

load_dotenv()

USER_ID = os.getenv("TEST_USER_ID", "80107cd3-82b9-4c36-9981-00418f9b63f8")
KRW_TO_CAD_RATE = 0.00098


def get_account_map():
    """Load account name -> ID mapping"""
    response = supabase.schema("finance").table("accounts").select("id, name").eq("user_id", USER_ID).execute()
    
    account_map = {}
    for acc in response.data:
        if "Scotia" in acc["name"]:
            account_map["scotiabank"] = {"id": acc["id"], "name": acc["name"]}
        elif "Toss" in acc["name"]:
            account_map["toss"] = {"id": acc["id"], "name": acc["name"]}
        elif "Cash" in acc["name"]:
            account_map["cash"] = {"id": acc["id"], "name": acc["name"]}
        elif "ISA" in acc["name"]:
            account_map["isa"] = {"id": acc["id"], "name": acc["name"]}
    
    return account_map


def remove_duplicate_transactions():
    """Find and remove duplicate transactions"""
    print("\n🔍 Searching for duplicate transactions...")
    
    # Get all transactions grouped by date and merchant
    response = supabase.schema("finance").table("transactions").select("*").eq("user_id", USER_ID).order("date").order("created_at").execute()
    
    transactions = response.data
    print(f"Total transactions: {len(transactions)}")
    
    # Find duplicates (same date + similar merchant + same amount)
    seen = {}
    duplicates = []
    
    for txn in transactions:
        key = f"{txn['date']}_{txn['merchant']}_{txn['amount_cad']}"
        
        if key in seen:
            # Duplicate found - keep the older one, mark newer for deletion
            duplicates.append(txn['id'])
            print(f"  🔁 Duplicate: {txn['date']} | {txn['merchant']} | ${txn['amount_cad']}")
        else:
            seen[key] = txn['id']
    
    if len(duplicates) == 0:
        print("✅ No duplicates found!")
        return 0
    
    print(f"\n⚠️  Found {len(duplicates)} duplicate transactions")
    confirm = input("Delete duplicates? (yes/no): ")
    
    if confirm.lower() != "yes":
        print("❌ Cancelled")
        return 0
    
    # Delete duplicates
    for dup_id in duplicates:
        supabase.schema("finance").table("transactions").delete().eq("id", dup_id).execute()
    
    print(f"✅ Deleted {len(duplicates)} duplicate transactions")
    return len(duplicates)


def recalculate_balances():
    """Recalculate all account balances from transactions"""
    print("\n💰 Recalculating account balances...")
    
    account_map = get_account_map()
    
    # Scotiabank
    scotiabank_id = account_map["scotiabank"]["id"]
    response = supabase.schema("finance").table("transactions").select("amount_cad").eq("user_id", USER_ID).eq("account_id", scotiabank_id).execute()
    scotia_balance = sum(float(t["amount_cad"]) for t in response.data)
    supabase.schema("finance").table("accounts").update({"balance": round(scotia_balance, 2)}).eq("id", scotiabank_id).execute()
    print(f"  ✓ {account_map['scotiabank']['name']}: ${scotia_balance:,.2f} CAD ({len(response.data)} transactions)")
    
    # Toss Bank
    toss_id = account_map["toss"]["id"]
    response = supabase.schema("finance").table("transactions").select("amount_cad").eq("user_id", USER_ID).eq("account_id", toss_id).execute()
    toss_balance = sum(float(t["amount_cad"]) for t in response.data)
    supabase.schema("finance").table("accounts").update({"balance": round(toss_balance, 2)}).eq("id", toss_id).execute()
    print(f"  ✓ {account_map['toss']['name']}: ${toss_balance:,.2f} CAD ({len(response.data)} transactions)")
    
    # Cash (static)
    cash_id = account_map["cash"]["id"]
    supabase.schema("finance").table("accounts").update({"balance": 9065.00}).eq("id", cash_id).execute()
    print(f"  ✓ {account_map['cash']['name']}: $9,065.00 CAD (no transactions)")
    
    # Korean ISA (static)
    isa_id = account_map["isa"]["id"]
    isa_balance = round(60770230 * KRW_TO_CAD_RATE, 2)
    supabase.schema("finance").table("accounts").update({"balance": isa_balance}).eq("id", isa_id).execute()
    print(f"  ✓ {account_map['isa']['name']}: ${isa_balance:,.2f} CAD (60,770,230 KRW)")
    
    # Calculate total
    response = supabase.schema("finance").table("accounts").select("balance").eq("user_id", USER_ID).execute()
    total = sum(float(acc["balance"]) for acc in response.data)
    
    print(f"\n  🎯 Total Net Worth: ${total:,.2f} CAD")


if __name__ == "__main__":
    print("=" * 60)
    print("APOLLO Finance - Fix Duplicates & Recalculate Balances")
    print("=" * 60)
    
    # Remove duplicates
    deleted = remove_duplicate_transactions()
    
    # Recalculate balances
    recalculate_balances()
    
    print("\n" + "=" * 60)
    print("✅ Cleanup complete!")
    print("=" * 60)
