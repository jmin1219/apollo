# Finance Module - Category Colors Reference

## 🎨 Color Palette

This document shows the color scheme for all system categories.

### Color Philosophy
- **Related categories** share similar color families
- **Parent categories** use the base color
- **Child categories** use lighter/darker shades
- All colors are from Tailwind CSS palette for consistency

---

## Expense Categories

### 🏠 Housing (Red Tones)
- **Housing** - `#ef4444` (red-500)
- Rent - `#dc2626` (red-600)

### 💡 Utilities (Gray Tones)
- **Utilities** - `#64748b` (slate-500)

### 🍽️ Food & Dining (Orange/Yellow Tones)
- **Food & Dining** - `#f97316` (orange-500)
- Groceries - `#fb923c` (orange-400)
- Dining Out - `#fdba74` (orange-300)
- Coffee & Drinks - `#f59e0b` (amber-500)

### 🚗 Transportation (Blue Tones)
- **Transportation** - `#3b82f6` (blue-500)
- Transit - `#60a5fa` (blue-400)
- Gas & Fuel - `#2563eb` (blue-600)

### 🎮 Entertainment (Purple Tones)
- **Entertainment** - `#a855f7` (purple-500)
- Subscriptions - `#c084fc` (purple-400)
- Hobbies - `#d8b4fe` (purple-300)

### 🏥 Health & Fitness (Green Tones)
- **Health & Fitness** - `#10b981` (emerald-500)
- Medical - `#34d399` (emerald-400)
- Gym & Sports - `#059669` (emerald-600)

### 📚 Education (Indigo Tones)
- **Education** - `#6366f1` (indigo-500)
- Books & Courses - `#818cf8` (indigo-400)

### 🛍️ Shopping (Pink Tones)
- **Shopping** - `#ec4899` (pink-500)
- Clothing - `#f472b6` (pink-400)
- Electronics - `#db2777` (pink-600)

### 💇 Personal Care (Rose Tones)
- **Personal Care** - `#f43f5e` (rose-500)

### ✈️ Travel (Cyan Tones)
- **Travel** - `#06b6d4` (cyan-500)

### 🛡️ Insurance (Gray Tones)
- **Insurance** - `#6b7280` (gray-500)

---

## Income Categories

### 💼 Salary & Wages (Emerald Tones)
- **Salary** - `#059669` (emerald-600)

### 📈 Investment Income (Teal Tones)
- **Investment Income** - `#14b8a6` (teal-500)

### 💰 Other Income (Emerald Tones)
- **Other Income** - `#10b981` (emerald-500)

---

## Badge Display

Each category badge will display with:
- **Background**: Color at 15% opacity (e.g., `#ef444415`)
- **Text**: Full color (e.g., `#ef4444`)
- **Border**: Color at 30% opacity (e.g., `#ef444430`)
- **Icon**: Category emoji

Example: `🏠 Housing` badge will have a subtle red background with red text.

---

## Usage in Components

```tsx
import { Badge } from '@/components/ui/badge';

// Category badge with color
<Badge variant="custom" color={category.color}>
  {category.icon && <span className="mr-1">{category.icon}</span>}
  {category.name}
</Badge>

// Uncategorized (fallback)
<Badge variant="outline" className="text-gray-400 font-normal">
  Uncategorized
</Badge>
```
