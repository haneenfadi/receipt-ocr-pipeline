from pydantic import BaseModel
from typing import Optional, List

class ReceiptItem(BaseModel):
    item_name: Optional[str] = None
    quantity: Optional[str] = None
class ReceiptOCRResult(BaseModel):
    store_name: Optional[str] = None
    receipt_number: Optional[str] = None
    date: Optional[str] = None
    currency: Optional[str] = None
    items: Optional[List[ReceiptItem]] = None
    taxes: Optional[str] = None
    total_amount: Optional[str] = None
class RegisterRequest(BaseModel):
    email: str
    password: str
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    has_data: bool           # key flag: does the user have receipts?
    receipt_count: int
    
class QuestionRequest(BaseModel):
    question: str