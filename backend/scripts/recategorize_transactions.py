"""
APOLLO Finance Module - Re-categorize Transactions
Maps transactions to new category IDs after category re-seeding

Usage: python scripts/recategorize_transactions.py
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.db.supabase_client import supabase
from dotenv import load_dotenv

load_dotenv()

USER_ID = os.getenv("TEST_USER_ID", "80107cd3-82b9-4c36-9981-00418f9b63f8")


def get_category_map():
    """Get mapping of category names to IDs"""
    response = supabase.schema("finance").table("categories").select("id, name, type").eq("is_system", True).execute()
    
    category_map = {}
    for cat in response.data:
        category_map[cat["name"].lower()] = cat["id"]
    
    return category_map


def infer_category(transaction, category_map):
    """Infer category from merchant/description"""
    merchant = (transaction.get("merchant") or "").lower()
    description = (transaction.get("description") or "").lower()
    amount = float(transaction.get("amount_cad", 0))
    
    # Income categories
    if amount > 0:
        if any(word in merchant or word in description for word in ["salary", "paycheck", "employer", "wage"]):
            return category_map.get("salary")
        elif any(word in merchant or word in description for word in ["investment", "dividend", "interest"]):
            return category_map.get("investment income")
        else:
            return category_map.get("other income")
    
    # Expense categories - match by keywords
    combined = f"{merchant} {description}"
    
    # Housing
    if any(word in combined for word in ["rent", "lease", "landlord"]):
        return category_map.get("rent")
    elif any(word in combined for word in ["utilities", "hydro", "electricity", "water", "gas bill", "internet", "phone"]):
        return category_map.get("utilities")
    
    # Food
    elif any(word in combined for word in ["grocery", "supermarket", "safeway", "whole foods", "trader joe", "costco", "walmart"]):
        return category_map.get("groceries")
    elif any(word in combined for word in ["restaurant", "cafe", "coffee", "starbucks", "tim hortons", "mcdonald", "burger", "pizza", "sushi", "doordash", "uber eats", "skip the dishes"]):
        # Check if it's coffee specifically
        if any(word in combined for word in ["coffee", "starbucks", "tim hortons", "cafe"]):
            return category_map.get("coffee & drinks")
        else:
            return category_map.get("dining out")
    
    # Transportation
    elif any(word in combined for word in ["transit", "subway", "bus", "skytrain", "compass", "translink", "ttc", "metro"]):
        return category_map.get("transit")
    elif any(word in combined for word in ["gas", "fuel", "petro", "shell", "chevron", "esso"]):
        return category_map.get("gas & fuel")
    elif any(word in combined for word in ["uber", "lyft", "taxi", "cab"]):
        return category_map.get("transportation")
    
    # Entertainment
    elif any(word in combined for word in ["netflix", "spotify", "youtube", "disney", "hulu", "hbo", "subscription", "prime video"]):
        return category_map.get("subscriptions")
    elif any(word in combined for word in ["movie", "cinema", "theatre", "concert", "game", "entertainment", "hobby"]):
        return category_map.get("entertainment")
    
    # Health
    elif any(word in combined for word in ["pharmacy", "drug", "medicine", "cvs", "walgreens", "shoppers", "medical", "doctor", "clinic", "hospital"]):
        return category_map.get("medical")
    elif any(word in combined for word in ["gym", "fitness", "yoga", "sport"]):
        return category_map.get("gym & sports")
    
    # Education
    elif any(word in combined for word in ["book", "course", "udemy", "coursera", "tuition", "education", "school"]):
        return category_map.get("books & courses")
    
    # Shopping
    elif any(word in combined for word in ["amazon", "ebay", "target", "best buy", "apple store", "electronics"]):
        return category_map.get("electronics")
    elif any(word in combined for word in ["clothing", "fashion", "zara", "h&m", "uniqlo", "nike", "adidas"]):
        return category_map.get("clothing")
    
    # Personal Care
    elif any(word in combined for word in ["haircut", "salon", "spa", "barber"]):
        return category_map.get("personal care")
    
    # Travel
    elif any(word in combined for word in ["flight", "airline", "hotel", "airbnb", "travel", "booking"]):
        return category_map.get("travel")
    
    # Default to general categories
    return category_map.get("food & dining")  # Default fallback


def recategorize_transactions():
    """Re-categorize all uncategorized transactions"""
    print("\n📊 Re-categorizing transactions...")
    
    # Get category mapping
    category_map = get_category_map()
    print(f"✅ Loaded {len(category_map)} categories")
    
    # Get all transactions with no category
    response = supabase.schema("finance").table("transactions").select("*").eq("user_id", USER_ID).is_("category_id", "null").execute()
    
    uncategorized = response.data
    print(f"📝 Found {len(uncategorized)} uncategorized transactions")
    
    if len(uncategorized) == 0:
        print("✅ All transactions are already categorized!")
        return
    
    # Categorize each transaction
    updates = []
    for txn in uncategorized:
        category_id = infer_category(txn, category_map)
        
        if category_id:
            updates.append({
                "id": txn["id"],
                "category_id": category_id
            })
    
    print(f"\n🔄 Updating {len(updates)} transactions...")
    
    # Update in batches
    batch_size = 10
    success_count = 0
    
    for i in range(0, len(updates), batch_size):
        batch = updates[i:i + batch_size]
        
        for update in batch:
            try:
                supabase.schema("finance").table("transactions").update({"category_id": update["category_id"]}).eq("id", update["id"]).execute()
                success_count += 1
            except Exception as e:
                print(f"  ⚠️  Failed to update transaction {update['id']}: {e}")
        
        print(f"  Progress: {min(i + batch_size, len(updates))}/{len(updates)}")
    
    print(f"\n✅ Successfully re-categorized {success_count}/{len(uncategorized)} transactions!")
    
    # Show remaining uncategorized
    response = supabase.schema("finance").table("transactions").select("id", count="exact").eq("user_id", USER_ID).is_("category_id", "null").execute()
    remaining = response.count
    
    if remaining > 0:
        print(f"⚠️  {remaining} transactions remain uncategorized (may need manual categorization)")
    else:
        print("🎉 All transactions now have categories!")


if __name__ == "__main__":
    print("=" * 60)
    print("APOLLO Finance - Transaction Re-categorization")
    print("=" * 60)
    
    print("\n🔌 Testing database connection...")
    try:
        test = supabase.schema("finance").table("categories").select("id", count="exact").limit(1).execute()
        print("✅ Connected to database")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        sys.exit(1)
    
    recategorize_transactions()
    
    print("\n" + "=" * 60)
    print("✅ Re-categorization complete!")
    print("=" * 60)
