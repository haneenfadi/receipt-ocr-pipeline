import os
from dotenv import load_dotenv
from mistralai import Mistral
from src.config.settings import settings
from src.utils.image_preprocessing import preprocess_clahe, check_image_quality, bytes_to_base64_url

load_dotenv(dotenv_path=r"src\.env")

api_key = os.getenv("MISTRAL_API_KEY")

client = Mistral(api_key=api_key)

def smart_ocr(image_bytes: bytes, mime_type: str):
    """Smart OCR with automatic preprocessing"""

    if mime_type not in settings.ALLOWED_MIME_TYPES:
        raise ValueError(f"Unsupported mime type: {mime_type}")

    processing_mode = check_image_quality(image_bytes)

    if processing_mode == "clahe":
        final_image = preprocess_clahe(image_bytes)
        mime_type = "image/png"
    else:
        final_image = image_bytes

    image_url = bytes_to_base64_url(final_image, mime_type)

    response = client.ocr.process(
        model="mistral-ocr-latest",
        document={
            "type": "image_url",
            "image_url": image_url
        }
    )
    print("ocr text:", "\n".join(page.markdown for page in response.pages))
    return response, processing_mode

#NOTE: Update MIME type to "image/png" only when CLAHE is applied; otherwise keep the original MIME type.

