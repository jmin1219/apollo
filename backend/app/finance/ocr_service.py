"""
Finance Module - OCR Service
Extracts transactions from bank statements (images or PDFs) using OpenAI API
"""

import base64
import os
import io
from typing import List, Dict, Any, Optional

from openai import OpenAI
from pydantic import BaseModel
import PyPDF2

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class ExtractedTransaction(BaseModel):
    """Single transaction extracted from OCR"""
    date: str  # YYYY-MM-DD format
    amount: float  # Negative for expenses
    merchant: str
    description: Optional[str] = None
    confidence: float = 1.0  # 0-1 confidence score
    category_id: Optional[str] = None  # Auto-assigned category


class OCRResult(BaseModel):
    """Result from OCR analysis"""
    transactions: List[ExtractedTransaction]
    total_found: int
    currency: str = "CAD"
    analysis_notes: Optional[str] = None


class OCRService:
    """Service for extracting transactions from images and PDFs"""
    
    @staticmethod
    def encode_image(image_bytes: bytes) -> str:
        """Convert image bytes to base64"""
        return base64.b64encode(image_bytes).decode('utf-8')
    
    @staticmethod
    def extract_pdf_text(pdf_bytes: bytes) -> str:
        """Extract text from PDF"""
        try:
            pdf_file = io.BytesIO(pdf_bytes)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return text
        except Exception as e:
            print(f"PDF extraction error: {e}")
            return ""
    
    @staticmethod
    def create_extraction_prompt() -> str:
        """Create prompt for transaction extraction"""
        return """Analyze this bank statement and extract ALL transactions.

For each transaction, identify:
- Date (YYYY-MM-DD format)
- Amount (negative for expenses/withdrawals, positive for deposits/income)
- Merchant name
- Brief description

Return ONLY valid JSON in this exact format:
{
  "transactions": [
    {
      "date": "2025-10-27",
      "amount": -1850.00,
      "merchant": "Interac e-Transfer",
      "description": "Rent payment",
      "confidence": 0.95
    }
  ],
  "currency": "CAD",
  "total_found": 1,
  "analysis_notes": "Scotiabank statement for October 2025"
}

Rules:
- Use negative amounts for expenses/withdrawals
- Use positive amounts for income/deposits
- Date must be YYYY-MM-DD format
- Amount must be a number (not string)
- Confidence: 1.0 = certain, 0.5 = unsure
- Include ALL transactions, even small ones
- Skip bank fees like "Service charge" unless they're actual purchases
- For "Error correction" entries, ignore them (they reverse other transactions)

Return only the JSON, no other text."""

    @staticmethod
    async def analyze_image(image_bytes: bytes, file_type: str = "image/png") -> OCRResult:
        """
        Analyze bank statement (image or PDF) and extract transactions
        
        Args:
            image_bytes: File bytes
            file_type: MIME type
            
        Returns:
            OCRResult with extracted transactions
        """
        try:
            # Handle PDFs differently (text extraction instead of vision)
            if file_type == "application/pdf":
                return await OCRService.analyze_pdf_text(image_bytes)
            
            # For images, use Vision API
            base64_image = OCRService.encode_image(image_bytes)
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": OCRService.create_extraction_prompt()
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{file_type};base64,{base64_image}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=2000,
                temperature=0.1
            )
            
            content = response.choices[0].message.content
            return OCRService.parse_response(content)
            
        except Exception as e:
            print(f"OCR Error: {e}")
            return OCRResult(
                transactions=[],
                total_found=0,
                currency="CAD",
                analysis_notes=f"Error: {str(e)}"
            )
    
    @staticmethod
    async def analyze_pdf_text(pdf_bytes: bytes) -> OCRResult:
        """
        Analyze PDF by extracting text and using GPT-4 (non-vision)
        
        Args:
            pdf_bytes: PDF file bytes
            
        Returns:
            OCRResult with extracted transactions
        """
        try:
            # Extract text from PDF
            text = OCRService.extract_pdf_text(pdf_bytes)
            
            if not text:
                return OCRResult(
                    transactions=[],
                    total_found=0,
                    currency="CAD",
                    analysis_notes="Error: Could not extract text from PDF"
                )
            
            # Use GPT-4 to parse the text
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": f"""{OCRService.create_extraction_prompt()}

Here is the bank statement text:

{text}
"""
                    }
                ],
                max_tokens=2000,
                temperature=0.1
            )
            
            content = response.choices[0].message.content
            return OCRService.parse_response(content)
            
        except Exception as e:
            print(f"PDF OCR Error: {e}")
            return OCRResult(
                transactions=[],
                total_found=0,
                currency="CAD",
                analysis_notes=f"Error: {str(e)}"
            )
    
    @staticmethod
    def parse_response(content: str) -> OCRResult:
        """Parse OpenAI response into OCRResult"""
        import json
        
        # Extract JSON from response (handle markdown code blocks)
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        # Parse JSON
        result_data = json.loads(content)
        
        # Validate and return
        return OCRResult(**result_data)
    
    @staticmethod
    def infer_category(merchant: str, amount: float, existing_categories: Dict[str, str]) -> Optional[str]:
        """
        Infer category from merchant name using keyword matching
        
        Args:
            merchant: Merchant name
            amount: Transaction amount
            existing_categories: Dict of category_name -> category_id
            
        Returns:
            Category ID or None
        """
        merchant_lower = merchant.lower()
        
        # Income categories
        if amount > 0:
            if any(word in merchant_lower for word in ["salary", "paycheck", "employer", "wage"]):
                return existing_categories.get("salary")
            elif any(word in merchant_lower for word in ["investment", "dividend", "interest", "toss bank"]):
                return existing_categories.get("investment income")
            else:
                return existing_categories.get("other income")
        
        # Expense categories
        if any(word in merchant_lower for word in ["rent", "lease", "landlord", "interac e-transfer", "interac"]):
            return existing_categories.get("rent")
        elif any(word in merchant_lower for word in ["hydro", "electricity", "telus", "utilities"]):
            return existing_categories.get("utilities")
        elif any(word in merchant_lower for word in ["grocery", "safeway", "costco", "walmart"]):
            return existing_categories.get("groceries")
        elif any(word in merchant_lower for word in ["doordash", "uber eats", "restaurant", "dining"]):
            return existing_categories.get("dining out")
        elif any(word in merchant_lower for word in ["starbucks", "coffee", "tim hortons"]):
            return existing_categories.get("coffee & drinks")
        elif any(word in merchant_lower for word in ["uber", "transit", "compass"]):
            return existing_categories.get("transit")
        elif any(word in merchant_lower for word in ["netflix", "spotify", "youtube", "apple.com", "apple"]):
            return existing_categories.get("subscriptions")
        elif any(word in merchant_lower for word in ["gym", "fitness", "sports"]):
            return existing_categories.get("gym & sports")
        elif any(word in merchant_lower for word in ["pharmacy", "medical", "doctor"]):
            return existing_categories.get("medical")
        elif any(word in merchant_lower for word in ["amazon", "electronics", "best buy", "ikea"]):
            return existing_categories.get("electronics")
        elif any(word in merchant_lower for word in ["cinema", "movie", "entertainment", "cineplex"]):
            return existing_categories.get("entertainment")
        
        # Default
        return existing_categories.get("food & dining")
