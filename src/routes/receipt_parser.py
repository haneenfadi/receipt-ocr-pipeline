from fastapi import APIRouter, UploadFile, File
import time
from loguru import logger
from src.ocr.mistral_ocr import smart_ocr
from src.ocr.parsing import parse_receipt_with_groq
from db.database import ReceiptDatabase
from datetime import datetime
import os
from src.utils.schema import ReceiptOCRResult
from fastapi import Depends
from src.routes.auth_router import get_current_user

router = APIRouter(
    prefix="/api/v1/receipt_parser",
    tags=["receipt_parser"]
)

db = ReceiptDatabase()
IMAGE_DIR = r"db\stored_receipts"
os.makedirs(IMAGE_DIR, exist_ok=True)


@router.post("/upload", response_model=ReceiptOCRResult)
async def extract_text_from_receipt(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
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
    receipt_id = db.save_receipt(current_user["user_id"], result)

    # then save the image path to the receipt record
    db.update_receipt_image(receipt_id, image_path, current_user["user_id"])

    logger.info(f"OCR processing time: {elapsed_time:.3f} seconds")

    return result
