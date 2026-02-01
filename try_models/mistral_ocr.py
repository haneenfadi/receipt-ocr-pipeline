import os
import base64
import mimetypes
from mistralai import Mistral

api_key = os.getenv("MISTRAL_API_KEY")
client = Mistral(api_key=api_key)

# Function to load local image as base64 data URL


def load_image(image_path):
    mime_type, _ = mimetypes.guess_type(image_path)
    with open(image_path, "rb") as image_file:
        image_data = image_file.read()
        base64_encoded = base64.b64encode(image_data).decode('utf-8')
        base64_url = f"data:{mime_type};base64,{base64_encoded}"
    return base64_url


# Load the image
image_path = r"src\test_images\ar_image(2).jpg"
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
