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
