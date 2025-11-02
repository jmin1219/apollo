"""
APOLLO Finance Module - Category Seed Data
Seeds system categories with colors, icons, and hierarchy

Usage: python scripts/seed_categories.py

This will populate the finance.categories table with default categories.
"""

import sys
from pathlib import Path
from typing import List, Dict

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from app.db.supabase_client import supabase
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# System categories with colors
# Color families:
# 🏠 Housing: Red tones
# 🍽️ Food: Orange/Yellow tones  
# 🚗 Transportation: Blue tones
# 🎮 Entertainment: Purple tones
# 🏥 Health: Green tones
# 💼 Income: Emerald tones
# 📚 Education: Indigo tones
# 🛍️ Shopping: Pink tones
# 💰 Utilities: Gray tones

SYSTEM_CATEGORIES = [
    # ========== EXPENSE CATEGORIES ==========
    
    # Housing (red tones)
    {
        "name": "Housing",
        "type": "expense",
        "color": "#ef4444",  # red-500
        "icon": "🏠",
        "parent_id": None,
        "is_system": True
    },
    {
        "name": "Rent",
        "type": "expense",
        "color": "#dc2626",  # red-600
        "icon": "🏠",
        "parent_id": None,  # Will be set to Housing ID
        "is_system": True
    },
    {
        "name": "Utilities",
        "type": "expense",
        "color": "#64748b",  # slate-500
        "icon": "💡",
        "parent_id": None,
        "is_system": True
    },
    
    # Food & Dining (orange/yellow tones)
    {
        "name": "Food & Dining",
        "type": "expense",
        "color": "#f97316",  # orange-500
        "icon": "🍽️",
        "parent_id": None,
        "is_system": True
    },
    {
        "name": "Groceries",
        "type": "expense",
        "color": "#fb923c",  # orange-400
        "icon": "🛒",
        "parent_id": None,  # Will be set to Food & Dining ID
        "is_system": True
    },
    {
        "name": "Dining Out",
        "type": "expense",
        "color": "#fdba74",  # orange-300
        "icon": "🍴",
        "parent_id": None,  # Will be set to Food & Dining ID
        "is_system": True
    },
    {
        "name": "Coffee & Drinks",
        "type": "expense",
        "color": "#f59e0b",  # amber-500
        "icon": "☕",
        "parent_id": None,  # Will be set to Food & Dining ID
        "is_system": True
    },
    
    # Transportation (blue tones)
    {
        "name": "Transportation",
        "type": "expense",
        "color": "#3b82f6",  # blue-500
        "icon": "🚗",
        "parent_id": None,
        "is_system": True
    },
    {
        "name": "Transit",
        "type": "expense",
        "color": "#60a5fa",  # blue-400
        "icon": "🚇",
        "parent_id": None,  # Will be set to Transportation ID
        "is_system": True
    },
    {
        "name": "Gas & Fuel",
        "type": "expense",
        "color": "#2563eb",  # blue-600
        "icon": "⛽",
        "parent_id": None,  # Will be set to Transportation ID
        "is_system": True
    },
    
    # Entertainment (purple tones)
    {
        "name": "Entertainment",
        "type": "expense",
        "color": "#a855f7",  # purple-500
        "icon": "🎮",
        "parent_id": None,
        "is_system": True
    },
    {
        "name": "Subscriptions",
        "type": "expense",
        "color": "#c084fc",  # purple-400
        "icon": "📺",
        "parent_id": None,  # Will be set to Entertainment ID
        "is_system": True
    },
    {
        "name": "Hobbies",
        "type": "expense",
        "color": "#d8b4fe",  # purple-300
        "icon": "🎨",
        "parent_id": None,  # Will be set to Entertainment ID
        "is_system": True
    },
    
    # Health & Fitness (green tones)
    {
        "name": "Health & Fitness",
        "type": "expense",
        "color": "#10b981",  # emerald-500
        "icon": "🏥",
        "parent_id": None,
        "is_system": True
    },
    {
        "name": "Medical",
        "type": "expense",
        "color": "#34d399",  # emerald-400
        "icon": "💊",
        "parent_id": None,  # Will be set to Health & Fitness ID
        "is_system": True
    },
    {
        "name": "Gym & Sports",
        "type": "expense",
        "color": "#059669",  # emerald-600
        "icon": "💪",
        "parent_id": None,  # Will be set to Health & Fitness ID
        "is_system": True
    },
    
    # Education (indigo tones)
    {
        "name": "Education",
        "type": "expense",
        "color": "#6366f1",  # indigo-500
        "icon": "📚",
        "parent_id": None,
        "is_system": True
    },
    {
        "name": "Books & Courses",
        "type": "expense",
        "color": "#818cf8",  # indigo-400
        "icon": "📖",
        "parent_id": None,  # Will be set to Education ID
        "is_system": True
    },
    
    # Shopping (pink tones)
    {
        "name": "Shopping",
        "type": "expense",
        "color": "#ec4899",  # pink-500
        "icon": "🛍️",
        "parent_id": None,
        "is_system": True
    },
    {
        "name": "Clothing",
        "type": "expense",
        "color": "#f472b6",  # pink-400
        "icon": "👕",
        "parent_id": None,  # Will be set to Shopping ID
        "is_system": True
    },
    {
        "name": "Electronics",
        "type": "expense",
        "color": "#db2777",  # pink-600
        "icon": "💻",
        "parent_id": None,  # Will be set to Shopping ID
        "is_system": True
    },
    
    # Personal Care (rose tones)
    {
        "name": "Personal Care",
        "type": "expense",
        "color": "#f43f5e",  # rose-500
        "icon": "💇",
        "parent_id": None,
        "is_system": True
    },
    
    # Travel (cyan tones)
    {
        "name": "Travel",
        "type": "expense",
        "color": "#06b6d4",  # cyan-500
        "icon": "✈️",
        "parent_id": None,
        "is_system": True
    },
    
    # Insurance (gray tones)
    {
        "name": "Insurance",
        "type": "expense",
        "color": "#6b7280",  # gray-500
        "icon": "🛡️",
        "parent_id": None,
        "is_system": True
    },
    
    # ========== INCOME CATEGORIES ==========
    
    # Salary & Wages (emerald tones)
    {
        "name": "Salary",
        "type": "income",
        "color": "#059669",  # emerald-600
        "icon": "💼",
        "parent_id": None,
        "is_system": True
    },
    
    # Investment Income (teal tones)
    {
        "name": "Investment Income",
        "type": "income",
        "color": "#14b8a6",  # teal-500
        "icon": "📈",
        "parent_id": None,
        "is_system": True
    },
    
    # Other Income
    {
        "name": "Other Income",
        "type": "income",
        "color": "#10b981",  # emerald-500
        "icon": "💰",
        "parent_id": None,
        "is_system": True
    },
]


def seed_categories():
    """Seed system categories with colors"""
    print("\n🎨 Seeding system categories with colors...")
    
    try:
        # Check if categories already exist
        response = supabase.schema("finance").table("categories").select("id", count="exact").eq("is_system", True).execute()
        existing_count = response.count
        
        if existing_count > 0:
            print(f"⚠️  Found {existing_count} existing system categories")
            confirm = input("Delete and re-seed? (yes/no): ")
            if confirm.lower() != "yes":
                print("❌ Seeding cancelled")
                return
            
            # Delete existing system categories
            supabase.schema("finance").table("categories").delete().eq("is_system", True).execute()
            print(f"🗑️  Deleted {existing_count} existing categories")
        
        # Insert categories in two passes (parents first, then children)
        parent_categories = [cat for cat in SYSTEM_CATEGORIES if cat["parent_id"] is None and not cat["name"] in ["Rent", "Groceries", "Dining Out", "Coffee & Drinks", "Transit", "Gas & Fuel", "Subscriptions", "Hobbies", "Medical", "Gym & Sports", "Books & Courses", "Clothing", "Electronics"]]
        
        category_id_map = {}
        
        # First pass: Insert parent categories
        print("\n📁 Creating parent categories...")
        for cat in parent_categories:
            cat_data = {
                "name": cat["name"],
                "type": cat["type"],
                "color": cat["color"],
                "icon": cat["icon"],
                "parent_id": None,
                "is_system": True,
                "user_id": None
            }
            
            response = supabase.schema("finance").table("categories").insert(cat_data).execute()
            new_id = response.data[0]["id"]
            category_id_map[cat["name"]] = new_id
            print(f"  ✓ {cat['icon']} {cat['name']} ({cat['color']})")
        
        # Second pass: Insert child categories with parent references
        child_map = {
            "Rent": "Housing",
            "Groceries": "Food & Dining",
            "Dining Out": "Food & Dining",
            "Coffee & Drinks": "Food & Dining",
            "Transit": "Transportation",
            "Gas & Fuel": "Transportation",
            "Subscriptions": "Entertainment",
            "Hobbies": "Entertainment",
            "Medical": "Health & Fitness",
            "Gym & Sports": "Health & Fitness",
            "Books & Courses": "Education",
            "Clothing": "Shopping",
            "Electronics": "Shopping",
        }
        
        child_categories = [cat for cat in SYSTEM_CATEGORIES if cat["name"] in child_map]
        
        print("\n📂 Creating child categories...")
        for cat in child_categories:
            parent_name = child_map[cat["name"]]
            parent_id = category_id_map.get(parent_name)
            
            cat_data = {
                "name": cat["name"],
                "type": cat["type"],
                "color": cat["color"],
                "icon": cat["icon"],
                "parent_id": parent_id,
                "is_system": True,
                "user_id": None
            }
            
            response = supabase.schema("finance").table("categories").insert(cat_data).execute()
            print(f"  ✓ {cat['icon']} {cat['name']} ({cat['color']}) → {parent_name}")
        
        # Verify
        response = supabase.schema("finance").table("categories").select("id", count="exact").eq("is_system", True).execute()
        final_count = response.count
        
        print(f"\n✅ Seeded {final_count} system categories successfully!")
        
        # Show breakdown
        expense_response = supabase.schema("finance").table("categories").select("id", count="exact").eq("is_system", True).eq("type", "expense").execute()
        income_response = supabase.schema("finance").table("categories").select("id", count="exact").eq("is_system", True).eq("type", "income").execute()
        
        print(f"  • Expense categories: {expense_response.count}")
        print(f"  • Income categories: {income_response.count}")
        
    except Exception as e:
        print(f"\n❌ Seeding failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("=" * 60)
    print("APOLLO Finance Module - Category Seeding")
    print("=" * 60)
    
    print("\n🔌 Testing database connection...")
    try:
        test = supabase.schema("finance").table("categories").select("id", count="exact").limit(1).execute()
        print("✅ Connected to database")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        sys.exit(1)
    
    seed_categories()
    
    print("\n" + "=" * 60)
    print("✅ Category seeding complete!")
    print("=" * 60)
