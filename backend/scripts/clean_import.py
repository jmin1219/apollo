"""
APOLLO Finance - Clean Slate Import
Deletes all existing transactions and re-imports from scratch

This ensures no duplicates and correct balances.

Usage: python scripts/clean_import.py
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

def get_category_map():
    """Load category name -> ID mapping"""
    response = supabase.schema("finance").table("categories").select("id, name, type").eq("is_system", True).execute()
    
    category_map = {}
    for cat in response.data:
        category_map[cat["name"].lower()] = cat["id"]
    
    return category_map

def get_account_map():
    """Load account name -> ID mapping"""
    response = supabase.schema("finance").table("accounts").select("id, name").eq("user_id", USER_ID).execute()
    
    account_map = {}
    for acc in response.data:
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
# ALL TRANSACTIONS (No duplicates - single source of truth)
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
    {"date": "2025-09-15", "amount": -1.00, "merchant": "Google YouTube Premium", "description": "YouTube subscription (error)", "category": "subscriptions"},
    {"date": "2025-09-15", "amount": 1.00, "merchant": "Google YouTube Premium", "description": "Error correction", "category": "subscriptions"},
    {"date": "2025-09-20", "amount": -8.95, "merchant": "Google YouTube Premium", "description": "YouTube subscription", "category": "subscriptions"},
    {"date": "2025-09-27", "amount": -2000.00, "merchant": "Interac e-Transfer", "description": "Rent payment 1/2", "category": "rent"},
    {"date": "2025-09-29", "amount": -1.44, "merchant": "Apple.com/bill", "description": "Apple subscription", "category": "subscriptions"},
    {"date": "2025-09-29", "amount": -1700.00, "merchant": "Interac e-Transfer", "description": "Rent payment 2/2", "category": "rent"},
    
    # === OCTOBER 2025 (from CSV + screenshots) ===
    {"date": "2025-10-01", "amount": -10.49, "merchant": "DoorDash", "description": "DoorDash", "category": "dining out"},
    {"date": "2025-10-02", "amount": -8.79, "merchant": "Uber", "description": "Uber", "category": "transit"},
    {"date": "2025-10-02", "amount": -8.50, "merchant": "Uber", "description": "Uber", "category": "transit"},
    {"date": "2025-10-03", "amount": -8.51, "merchant": "Uber", "description": "Uber", "category": "transit"},
    {"date": "2025-10-03", "amount": -7.98, "merchant": "Uber", "description": "Uber", "category": "transit"},
    {"date": "2025-10-03", "amount": -225.85, "merchant": "Teamstake", "description": "Torra fantasy league", "category": "entertainment"},
    {"date": "2025-10-07", "amount": -8.79, "merchant": "Uber", "description": "Uber", "category": "transit"},
    {"date": "2025-10-11", "amount": -181.38, "merchant": "IKEA", "description": "IKEA", "category": "housing"},
    {"date": "2025-10-14", "amount": -152.32, "merchant": "Telus", "description": "Telus Comm", "category": "utilities"},
    {"date": "2025-10-16", "amount": -59.36, "merchant": "Telus Mobility", "description": "Telus Mobility", "category": "utilities"},
    {"date": "2025-10-17", "amount": -34.76, "merchant": "City of Vancouver Parks", "description": "Parks", "category": "entertainment"},
    {"date": "2025-10-20", "amount": -30.10, "merchant": "Coal Harbour Liquor", "description": "Alcohol", "category": "shopping"},
    {"date": "2025-10-20", "amount": -8.95, "merchant": "Google YouTube Premium", "description": "YouTube subscription", "category": "subscriptions"},
    {"date": "2025-10-22", "amount": -7.00, "merchant": "Famous Player", "description": "Movie theater", "category": "entertainment"},
    {"date": "2025-10-23", "amount": -25.21, "merchant": "Cineplex Entertainment", "description": "Movie theater", "category": "entertainment"},
    {"date": "2025-10-27", "amount": -1850.00, "merchant": "Interac e-Transfer", "description": "Rent payment 1/2", "category": "rent"},
    {"date": "2025-10-27", "amount": -1850.00, "merchant": "Interac e-Transfer", "description": "Rent payment 2/2", "category": "rent"},
    {"date": "2025-10-27", "amount": -150.16, "merchant": "Swapped.com", "description": "Gambling", "category": "entertainment"},
    {"date": "2025-10-28", "amount": -1.44, "merchant": "Apple.com/bill", "description": "Apple subscription", "category": "subscriptions"},
    {"date": "2025-10-28", "amount": -45.00, "merchant": "BC Hydro", "description": "BC Hydro bill", "category": "utilities"},
    
    # === NOVEMBER 2025 ===
    {"date": "2025-11-01", "amount": -10.49, "merchant": "DoorDash", "description": "DoorDash Pass subscription", "category": "subscriptions"},
]

TOSS_TRANSACTIONS = [
    # === SEPTEMBER 2025 ===
    {"date": "2025-09-13", "amount": -39149, "merchant": "DoorDash", "description": "DD/DOORDASHBIG", "category": "dining out"},
    {"date": "2025-09-13", "amount": 13469, "merchant": "Currency Exchange", "description": "USD sale", "category": "other income"},
    {"date": "2025-09-13", "amount": -502355, "merchant": "Currency Exchange", "description": "CAD purchase", "category": "other income"},
    {"date": "2025-09-19", "amount": 2, "merchant": "Toss Bank", "description": "Cash Back", "category": "other income"},
    {"date": "2025-09-21", "amount": -17821, "merchant": "DoorDash", "description": "DD/DOORDASHDON", "category": "dining out"},
    {"date": "2025-09-21", "amount": -83690, "merchant": "Basketball Monthly", "description": "BASKETBALL MON", "category": "gym & sports"},
    {"date": "2025-09-22", "amount": 248, "merchant": "Toss Bank", "description": "Interest", "category": "investment income"},
    {"date": "2025-09-22", "amount": -10372, "merchant": "Perfecto Coffee", "description": "SQ *PERFECTO C", "category": "coffee & drinks"},
    {"date": "2025-09-23", "amount": 1000000, "merchant": "Chang Wonjae", "description": "Allowance", "category": "other income"},
    {"date": "2025-09-25", "amount": 75, "merchant": "Toss Bank", "description": "Interest", "category": "investment income"},
    {"date": "2025-09-25", "amount": 2, "merchant": "Toss Bank", "description": "Cash Back", "category": "other income"},
    {"date": "2025-09-25", "amount": -40825, "merchant": "DoorDash", "description": "DD/DOORDASHTHA", "category": "dining out"},
    {"date": "2025-09-26", "amount": -153947, "merchant": "DoorDash", "description": "DD/DOORDASHYOU", "category": "dining out"},
    {"date": "2025-09-26", "amount": -56838, "merchant": "Safeway", "description": "SAFEWAY #4908", "category": "groceries"},
    {"date": "2025-09-26", "amount": -29665, "merchant": "BC Liquor", "description": "BC LIQUOR#233", "category": "shopping"},
    {"date": "2025-09-30", "amount": -261798, "merchant": "Uniqlo Canada", "description": "UniqloCanada", "category": "clothing"},
    {"date": "2025-09-30", "amount": -123961, "merchant": "DoorDash", "description": "DD/DOORDASHYOU", "category": "dining out"},
    
    # === OCTOBER 2025 (from CSV only - avoid duplicates) ===
    {"date": "2025-10-01", "amount": 155, "merchant": "Toss Bank", "description": "Interest", "category": "investment income"},
    {"date": "2025-10-03", "amount": -7327, "merchant": "DoorDash", "description": "DD/DOORDASHFIE", "category": "dining out"},
    {"date": "2025-10-04", "amount": 106000, "merchant": "Friend", "description": "Payment from friend", "category": "other income"},
    {"date": "2025-10-04", "amount": 57, "merchant": "Toss Bank", "description": "Interest", "category": "investment income"},
    {"date": "2025-10-05", "amount": -9047, "merchant": "Netflix", "description": "NETFLIX.COM", "category": "subscriptions"},
    {"date": "2025-10-09", "amount": 1000000, "merchant": "Chang Wonjae", "description": "Allowance", "category": "other income"},
    {"date": "2025-10-10", "amount": -61746, "merchant": "Canucks Sports", "description": "CANUCKS SPORTS", "category": "entertainment"},
    {"date": "2025-10-10", "amount": -11334, "merchant": "7-Eleven", "description": "7 ELEVEN STORE", "category": "groceries"},
    {"date": "2025-10-10", "amount": -44345, "merchant": "Van Vapes", "description": "VAN VAPES", "category": "personal care"},
    {"date": "2025-10-11", "amount": 8, "merchant": "Toss Bank", "description": "Cash Back", "category": "other income"},
    {"date": "2025-10-11", "amount": -227830, "merchant": "Umbra", "description": "SPCA.UMBRA.CO", "category": "housing"},
    {"date": "2025-10-12", "amount": -16029, "merchant": "OpenAI", "description": "OPENAI", "category": "education"},
    {"date": "2025-10-12", "amount": -54136, "merchant": "DoorDash", "description": "DD/DOORDASHSAH", "category": "dining out"},
    {"date": "2025-10-12", "amount": -157819, "merchant": "DoorDash", "description": "DD/DOORDASHYOU - Groceries", "category": "groceries"},
    {"date": "2025-10-12", "amount": -35934, "merchant": "DoorDash", "description": "DD/DOORDASHSUS", "category": "dining out"},
    {"date": "2025-10-13", "amount": 1, "merchant": "K-Bank", "description": "K-Bank promo", "category": "other income"},
    {"date": "2025-10-13", "amount": -500000, "merchant": "Transfer", "description": "Transfer to friend", "category": "other income"},
    {"date": "2025-10-13", "amount": 246, "merchant": "Toss Bank", "description": "Interest", "category": "investment income"},
    {"date": "2025-10-13", "amount": -7995, "merchant": "Anthropic", "description": "ANTHROPIC", "category": "education"},
    {"date": "2025-10-13", "amount": -40005, "merchant": "Anthropic", "description": "ANTHROPIC", "category": "education"},
    {"date": "2025-10-13", "amount": 11, "merchant": "Lottery", "description": "Cash Back", "category": "other income"},
    {"date": "2025-10-14", "amount": 1, "merchant": "K-Bank", "description": "K-Bank promo", "category": "other income"},
    {"date": "2025-10-14", "amount": 17, "merchant": "Toss Bank", "description": "Interest", "category": "investment income"},
    {"date": "2025-10-14", "amount": -39969, "merchant": "Anthropic", "description": "ANTHROPIC", "category": "education"},
    {"date": "2025-10-15", "amount": -49650, "merchant": "DoorDash", "description": "DD/DOORDASHYOU", "category": "dining out"},
    {"date": "2025-10-15", "amount": -39853, "merchant": "Anthropic", "description": "ANTHROPIC", "category": "education"},
    {"date": "2025-10-16", "amount": -39829, "merchant": "Anthropic", "description": "ANTHROPIC", "category": "education"},
    {"date": "2025-10-16", "amount": -120824, "merchant": "DoorDash", "description": "DD/DOORDASHIGA - Groceries", "category": "groceries"},
    {"date": "2025-10-16", "amount": -39724, "merchant": "Anthropic", "description": "ANTHROPIC", "category": "education"},
    {"date": "2025-10-16", "amount": -40406, "merchant": "Anthropic", "description": "ANTHROPIC", "category": "education"},
    {"date": "2025-10-17", "amount": 9, "merchant": "Lottery", "description": "Cash Back", "category": "other income"},
    {"date": "2025-10-17", "amount": -41698, "merchant": "DoorDash", "description": "DD/DOORDASHNOO", "category": "dining out"},
    {"date": "2025-10-18", "amount": -40260, "merchant": "Anthropic", "description": "ANTHROPIC", "category": "education"},
    {"date": "2025-10-18", "amount": -40146, "merchant": "Anthropic", "description": "ANTHROPIC", "category": "education"},
    {"date": "2025-10-18", "amount": -40006, "merchant": "Anthropic", "description": "ANTHROPIC", "category": "education"},
    {"date": "2025-10-19", "amount": -21280, "merchant": "DoorDash", "description": "DD/DOORDASHSTA", "category": "dining out"},
    {"date": "2025-10-19", "amount": -40988, "merchant": "Anthropic", "description": "ANTHROPIC", "category": "education"},
    {"date": "2025-10-19", "amount": -40803, "merchant": "Anthropic", "description": "ANTHROPIC", "category": "education"},
    {"date": "2025-10-23", "amount": 1000000, "merchant": "Chang Wonjae", "description": "Allowance", "category": "other income"},
    {"date": "2025-10-23", "amount": -121809, "merchant": "DoorDash", "description": "DD/DOORDASHIGA - Groceries", "category": "groceries"},
    {"date": "2025-10-24", "amount": -37864, "merchant": "DoorDash", "description": "DD/DOORDASHVON", "category": "dining out"},
    {"date": "2025-10-26", "amount": -123390, "merchant": "DoorDash", "description": "DD/DOORDASHIGA - Groceries", "category": "groceries"},
    {"date": "2025-10-26", "amount": -2780, "merchant": "DoorDash", "description": "DD/DOORDASHIGA", "category": "groceries"},
    {"date": "2025-10-26", "amount": -57565, "merchant": "DoorDash", "description": "DD/DOORDASHBRO", "category": "dining out"},
    {"date": "2025-10-28", "amount": -1433, "merchant": "Render.com", "description": "RENDER.COM - APOLLO", "category": "education"},
    {"date": "2025-10-29", "amount": -58263, "merchant": "Van Vapes", "description": "VAN VAPES", "category": "personal care"},
    {"date": "2025-10-29", "amount": -316308, "merchant": "Able Carry", "description": "SP ABLE CARRY", "category": "shopping"},
    {"date": "2025-10-30", "amount": -44662, "merchant": "DoorDash", "description": "DD/DOORDASHDON", "category": "dining out"},
    {"date": "2025-10-30", "amount": -50811, "merchant": "5 Star Barber", "description": "5 STARBARBER", "category": "personal care"},
    {"date": "2025-10-31", "amount": -43841, "merchant": "OpenAI", "description": "OPENAI", "category": "education"},
    
    # === NOVEMBER 2025 ===
    {"date": "2025-11-01", "amount": 169, "merchant": "Toss Bank", "description": "Interest", "category": "investment income"},
    {"date": "2025-11-02", "amount": -29367, "merchant": "DoorDash", "description": "DD/DOORDASHPHN", "category": "dining out"},
]

# Cash transactions (from CSV)
CASH_TRANSACTIONS = [
    {"date": "2025-10-24", "amount": -100.00, "merchant": "Cannabis Store", "description": "Cannabis cartridges", "category": "personal care"},
]


def clean_import():
    """Delete all transactions and re-import cleanly"""
    print("\n⚠️  This will DELETE all existing transactions and re-import from scratch!")
    confirm = input("Are you sure? (yes/no): ")
    
    if confirm.lower() != "yes":
        print("❌ Cancelled")
        return
    
    # Get mappings
    category_map = get_category_map()
    account_map = get_account_map()
    
    print(f"\n✅ Loaded {len(category_map)} categories")
    print(f"✅ Loaded {len(account_map)} accounts")
    
    # Delete all existing transactions
    print("\n🗑️  Deleting all existing transactions...")
    response = supabase.schema("finance").table("transactions").delete().eq("user_id", USER_ID).execute()
    print(f"✅ Deleted all transactions")
    
    # Import Scotiabank
    print("\n🏦 Importing Scotiabank transactions...")
    scotiabank_id = account_map["scotiabank"]
    
    for idx, txn in enumerate(SCOTIABANK_TRANSACTIONS):
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
            "source": "import"
        }
        
        supabase.schema("finance").table("transactions").insert(txn_data).execute()
        
        if (idx + 1) % 10 == 0:
            print(f"  Progress: {idx + 1}/{len(SCOTIABANK_TRANSACTIONS)}")
    
    print(f"✅ Imported {len(SCOTIABANK_TRANSACTIONS)} Scotiabank transactions")
    
    # Import Toss Bank
    print("\n🇰🇷 Importing Toss Bank transactions...")
    toss_id = account_map["toss"]
    
    for idx, txn in enumerate(TOSS_TRANSACTIONS):
        category_id = category_map.get(txn["category"].lower())
        amount_krw = float(txn["amount"])
        amount_cad = round(amount_krw * KRW_TO_CAD_RATE, 2)
        
        txn_data = {
            "user_id": USER_ID,
            "account_id": toss_id,
            "date": txn["date"],
            "amount": amount_krw,
            "currency": "KRW",
            "amount_cad": amount_cad,
            "category_id": category_id,
            "merchant": txn["merchant"],
            "description": txn["description"],
            "source": "import"
        }
        
        supabase.schema("finance").table("transactions").insert(txn_data).execute()
        
        if (idx + 1) % 10 == 0:
            print(f"  Progress: {idx + 1}/{len(TOSS_TRANSACTIONS)}")
    
    print(f"✅ Imported {len(TOSS_TRANSACTIONS)} Toss Bank transactions")
    
    # Import Cash
    print("\n💵 Importing Cash transactions...")
    cash_id = account_map["cash"]
    
    for txn in CASH_TRANSACTIONS:
        category_id = category_map.get(txn["category"].lower())
        
        txn_data = {
            "user_id": USER_ID,
            "account_id": cash_id,
            "date": txn["date"],
            "amount": float(txn["amount"]),
            "currency": "CAD",
            "amount_cad": float(txn["amount"]),
            "category_id": category_id,
            "merchant": txn["merchant"],
            "description": txn["description"],
            "source": "import"
        }
        
        supabase.schema("finance").table("transactions").insert(txn_data).execute()
    
    print(f"✅ Imported {len(CASH_TRANSACTIONS)} Cash transactions")
    
    # Recalculate balances
    print("\n💰 Calculating final balances...")
    
    # Scotiabank
    response = supabase.schema("finance").table("transactions").select("amount_cad").eq("user_id", USER_ID).eq("account_id", scotiabank_id).execute()
    scotia_balance = round(sum(float(t["amount_cad"]) for t in response.data), 2)
    supabase.schema("finance").table("accounts").update({"balance": scotia_balance}).eq("id", scotiabank_id).execute()
    print(f"  ✓ Scotiabank: ${scotia_balance:,.2f} CAD ({len(response.data)} transactions)")
    
    # Toss
    response = supabase.schema("finance").table("transactions").select("amount_cad").eq("user_id", USER_ID).eq("account_id", toss_id).execute()
    toss_balance = round(sum(float(t["amount_cad"]) for t in response.data), 2)
    supabase.schema("finance").table("accounts").update({"balance": toss_balance}).eq("id", toss_id).execute()
    print(f"  ✓ Toss Korea: ${toss_balance:,.2f} CAD ({len(response.data)} transactions)")
    
    # Cash (calculated from transaction)
    response = supabase.schema("finance").table("transactions").select("amount_cad").eq("user_id", USER_ID).eq("account_id", cash_id).execute()
    cash_balance = 9065.00 + sum(float(t["amount_cad"]) for t in response.data)  # Current cash + transaction
    supabase.schema("finance").table("accounts").update({"balance": round(cash_balance, 2)}).eq("id", cash_id).execute()
    print(f"  ✓ Cash: ${cash_balance:,.2f} CAD")
    
    # ISA
    isa_id = account_map["isa"]
    isa_balance = round(60770230 * KRW_TO_CAD_RATE, 2)
    supabase.schema("finance").table("accounts").update({"balance": isa_balance}).eq("id", isa_id).execute()
    print(f"  ✓ Korean ISA: ${isa_balance:,.2f} CAD (60,770,230 KRW)")
    
    # Total
    response = supabase.schema("finance").table("accounts").select("balance").eq("user_id", USER_ID).execute()
    total = round(sum(float(acc["balance"]) for acc in response.data), 2)
    
    print(f"\n  🎯 Total Net Worth: ${total:,.2f} CAD")
    
    # Final count
    response = supabase.schema("finance").table("transactions").select("id", count="exact").eq("user_id", USER_ID).execute()
    print(f"  📊 Total transactions: {response.count}")


if __name__ == "__main__":
    print("=" * 60)
    print("APOLLO Finance - Clean Slate Import")
    print("=" * 60)
    
    clean_import()
    
    print("\n" + "=" * 60)
    print("✅ Clean import complete!")
    print("=" * 60)
