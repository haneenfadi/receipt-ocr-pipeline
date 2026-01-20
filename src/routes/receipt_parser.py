from fastapi import APIRouter, UploadFile, File
# from src.ocr.surya_ocr_test import run_ocr
# from PIL import Image
# from io import BytesIO
import time
from loguru import logger
from src.ocr.mistral_ocr import ocr_from_uploaded_image
from src.parsing_mistral import parse_receipt_with_groq

router = APIRouter(
    prefix="/receipt",
    tags=["receipt"]
)

# @app.get("/", tags=["health"])
# def health_check():
#     return {"status": "ok"}

# for surya (try to make the loads at the start)
# @router.post("/upload")
# async def extract_text_from_receipt(file: UploadFile = File(...)):
#     start_time = time.perf_counter()
#     file_bytes = await file.read()
#     file = Image.open(BytesIO(file_bytes)).convert("RGB")

#     text = run_ocr(file)

#     end_time = time.perf_counter()  # End timer
#     elapsed_time = end_time - start_time

#     # Log the time taken

#     logger.info(f"OCR processing time: {elapsed_time:.3f} seconds")

#     return {"text": text, "processing_time": f"{elapsed_time:.3f} seconds"}


@router.post("/upload")
async def extract_text_from_receipt(file: UploadFile = File(...)):
    start_time = time.perf_counter()

    image_bytes = await file.read()
    
    text = ocr_from_uploaded_image(
        image_bytes=image_bytes,
        mime_type=file.content_type
    )
    result = parse_receipt_with_groq(text)
    end_time = time.perf_counter()  # End timer
    elapsed_time = end_time - start_time

    # Log the time taken

    logger.info(f"OCR processing time: {elapsed_time:.3f} seconds")

    return {"result": result, "processing_time": f"{elapsed_time:.3f} seconds"}
