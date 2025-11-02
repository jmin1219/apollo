"""
APOLLO Finance - Set Current Account Balances
Sets account balances to their actual current values from bank statements

Usage: python scripts/set_balances.py
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

# Current balances from bank statements
CURRENT_BALANCES = {
    "Scotiabank (Canada)": {
        "balance_cad": 62877.66,  # From Oct 28 screenshot
        "currency": "CAD"
    },
    "Toss (Korea)": {
        "balance_krw": 116904,
        "balance_cad": round(116904 * KRW_TO_CAD_RATE, 2),
        "currency": "KRW"
    },
    "Cash": {
        "balance_cad": 8965.00,  # $9,065 - $100 cannabis = $8,965
        "currency": "CAD"
    },
    "Korean ISA": {
        "balance_krw": 60770230,
        "balance_cad": round(60770230 * KRW_TO_CAD_RATE, 2),
        "currency": "KRW"
    }
}


def set_balances():
    """Set current account balances"""
    print("\n💰 Setting current account balances...")
    
    # Get all accounts
    response = supabase.schema("finance").table("accounts").select("id, name").eq("user_id", USER_ID).execute()
    accounts = response.data
    
    for acc in accounts:
        # Find matching balance
        balance_data = None
        for name_key, data in CURRENT_BALANCES.items():
            if name_key in acc["name"]:
                balance_data = data
                break
        
        if balance_data:
            balance_cad = balance_data["balance_cad"]
            
            # Update balance
            supabase.schema("finance").table("accounts").update({
                "balance": balance_cad
            }).eq("id", acc["id"]).execute()
            
            if "balance_krw" in balance_data:
                print(f"  ✓ {acc['name']}: ${balance_cad:,.2f} CAD ({balance_data['balance_krw']:,} {balance_data['currency']})")
            else:
                print(f"  ✓ {acc['name']}: ${balance_cad:,.2f} {balance_data['currency']}")
    
    # Calculate total
    response = supabase.schema("finance").table("accounts").select("balance").eq("user_id", USER_ID).execute()
    total = round(sum(float(acc["balance"]) for acc in response.data), 2)
    
    print(f"\n  🎯 Total Net Worth: ${total:,.2f} CAD")
    
    return total


if __name__ == "__main__":
    print("=" * 60)
    print("APOLLO Finance - Set Current Balances")
    print("=" * 60)
    
    total = set_balances()
    
    print("\n" + "=" * 60)
    print("✅ Balances updated!")
    print("=" * 60)
