import os
import base64
import mimetypes
from dotenv import load_dotenv
from mistralai import Mistral

load_dotenv(dotenv_path=r"src\.env")

api_key = os.getenv("MISTRAL_API_KEY")
client = Mistral(api_key=api_key)


def load_image(image_path):
    mime_type, _ = mimetypes.guess_type(image_path)
    with open(image_path, "rb") as image_file:
        image_data = image_file.read()
        base64_encoded = base64.b64encode(image_data).decode('utf-8')
        base64_url = f"data:{mime_type};base64,{base64_encoded}"
    return base64_url


image_path = r"src\receipts\ar_image(4).png"

image_url = load_image(image_path)

# Call OCR
response = client.ocr.process(
    model="mistral-ocr-latest",
    document={
        "type": "image_url",
        "image_url": image_url
    }
)

# Print OCR text
for page in response.pages:
    print(page.markdown)

with open(r"test\ocr_outputs_txt\ar_image(4).txt", "w", encoding="utf-8") as f:
    for page in response.pages:
        f.write(page.markdown)
