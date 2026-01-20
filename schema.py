from pydantic import BaseModel
from typing import Optional, List


class ReceiptOCRResult (BaseModel):
    store_name: Optional[str] = None
    receipt_number: Optional[str] = None
    date: Optional[str] = None
    currency: Optional[str] = None,
    items: Optional[List[dict]] = []
    taxes: Optional[str] = None
    total_amount: Optional[str] = None
