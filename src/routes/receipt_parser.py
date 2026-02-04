from fastapi import APIRouter, UploadFile, File
import time
from loguru import logger
from src.ocr.mistral_ocr import  smart_ocr
from src.ocr.parsing import parse_receipt_with_groq
from db.database import ReceiptDatabase
from datetime import datetime
import os
from src.utils.schema import ReceiptOCRResult
from fastapi import Header, HTTPException
from dotenv import load_dotenv

load_dotenv()

AUTH_PASSWORD = os.environ.get("API_AUTH_PASSWORD", "")

router = APIRouter(
    prefix="/api/v1/receipt_parser",
    tags=["receipt_parser"]
)

db = ReceiptDatabase()
IMAGE_DIR = r"db\stored_receipts"
os.makedirs(IMAGE_DIR, exist_ok=True)


@router.post("/upload", response_model=ReceiptOCRResult)
async def extract_text_from_receipt(file: UploadFile = File(...), x_api_password: str = Header(...)):
    
    if x_api_password != AUTH_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")
    start_time = time.perf_counter()

    file_bytes = await file.read()   

    # save image
    file_ext = os.path.splitext(file.filename)[1].lower()
    file_name = f"receipt_{int(datetime.now().timestamp())}{file_ext}"
    image_path = os.path.join(IMAGE_DIR, file_name)

    with open(image_path, "wb") as f:
        f.write(file_bytes)

    # OCR
    text = smart_ocr(
        image_bytes=file_bytes,
        mime_type=file.content_type
    )

    result = parse_receipt_with_groq(text)

    end_time = time.perf_counter()
    elapsed_time = end_time - start_time

    # first save receipt without image 
    receipt_id = db.save_receipt(result)
    # then save the image and update the receipt record
    db.update_receipt_image(receipt_id, image_path)

    logger.info(f"OCR processing time: {elapsed_time:.3f} seconds")

    return result
    
