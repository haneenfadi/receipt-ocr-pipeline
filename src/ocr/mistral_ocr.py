# import os
# import base64
# import mimetypes
# from dotenv import load_dotenv
# from mistralai import Mistral

# load_dotenv(dotenv_path=r"src\.env")

# api_key = os.getenv("MISTRAL_API_KEY")

# client = Mistral(api_key=api_key)

# def load_image(image_path):
#     mime_type, _ = mimetypes.guess_type(image_path)
#     with open(image_path, "rb") as image_file:
#         image_data = image_file.read()
#         base64_encoded = base64.b64encode(image_data).decode('utf-8')
#         base64_url = f"data:{mime_type};base64,{base64_encoded}"
#     return base64_url


# # Load the image
# # image_path = r"images\80f5e8cd-19cc-4015-988e-89b6d55186a8.jpg"
# # image_path = r"images\173a22cc-33a2-413b-93c9-a99e099b17f8.jpg"
# image_path = "pharmacy.jpg"
# image_url = load_image(image_path)

# # Call OCR
# response = client.ocr.process(
#     model="mistral-ocr-latest",
#     document={
#         "type": "image_url",
#         "image_url": image_url
#     }
# )

# # Print OCR text - CORRECT WAY
# for page in response.pages:
#     print(page.markdown)

# with open("pharmacy.txt", "w", encoding="utf-8") as f:
#     for page in response.pages:
#         f.write(page.markdown)


import os
import base64
import mimetypes
from dotenv import load_dotenv
from mistralai import Mistral
from PIL import Image
load_dotenv(dotenv_path=r"src\.env")

api_key = os.getenv("MISTRAL_API_KEY")

client = Mistral(api_key=api_key)


def ocr_from_uploaded_image(
    image_bytes: bytes,
    mime_type: str = "image/jpeg"
) -> str:
    """
    Performs OCR on uploaded image bytes.
    :param image_bytes: image file bytes
    :param mime_type: image mime type (image/jpeg, image/png, ...)
    :return: OCR text
    """

    base64_encoded = base64.b64encode(image_bytes).decode("utf-8")
    image_url = f"data:{mime_type};base64,{base64_encoded}"

    response = client.ocr.process(
        model="mistral-ocr-latest",
        document={
            "type": "image_url",
            "image_url": image_url
        }
    )

    return "\n".join(page.markdown for page in response.pages)

with open("pharmacy.jpg", "rb") as f:
    image_bytes = f.read()

text = ocr_from_uploaded_image(image_bytes, mime_type="image/jpeg")
print(text)
