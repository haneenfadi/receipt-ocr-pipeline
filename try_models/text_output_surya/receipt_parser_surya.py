from fastapi import APIRouter, UploadFile, File
from src.ocr.surya_ocr_test import run_ocr
from PIL import Image
from io import BytesIO
import time
from loguru import logger

router = APIRouter(
    prefix="/receipt",
    tags=["receipt"]
)

# @app.get("/", tags=["health"])
# def health_check():
#     return {"status": "ok"}

# for surya (try to make the loads at the start)
@router.post("/upload")
async def extract_text_from_receipt(file: UploadFile = File(...)):
    start_time = time.perf_counter()
    file_bytes = await file.read()
    file = Image.open(BytesIO(file_bytes)).convert("RGB")

    text = run_ocr(file)

    end_time = time.perf_counter()  
    elapsed_time = end_time - start_time


    logger.info(f"OCR processing time: {elapsed_time:.3f} seconds")

    return {"text": text, "processing_time": f"{elapsed_time:.3f} seconds"}

