import numpy as np
import cv2
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


def check_image_quality(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # sharpness check using Laplacian variance
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()

    print(f" Quality check: {os.path.basename(image_path)}")
    print(f"  Sharpness: {laplacian_var:.1f}")

    # use a threshold for blurriness
    if laplacian_var < 35:
        print(f"  →  Very blurry (< 35) - Using original image\n")
        return "original"

    # check brightness and contrast
    brightness = np.mean(gray)
    is_too_dark = brightness < 80
    is_too_bright = brightness > 180

    contrast = gray.std()
    is_low_contrast = contrast < 40

    needs_processing = is_too_dark or is_too_bright or is_low_contrast

    print(
        f"  Brightness: {brightness:.1f} {'!' if (is_too_dark or is_too_bright) else ''}")
    print(f"  Contrast: {contrast:.1f} {'!' if is_low_contrast else ''}")
    print(
        f"  → {'! Will preprocess' if needs_processing else ' Using original'}\n")

    if needs_processing:
        return "clahe"
    else:
        return "original"


def preprocess_clahe(image_path):
    """CLAHE"""
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(img)

    output_path = image_path.replace(
        '.jpg', '_processed.jpg').replace('.png', '_processed.png')
    cv2.imwrite(output_path, enhanced)

    return output_path


def smart_ocr(image_path):

    # check quality
    processing_mode = check_image_quality(image_path)

    # 3 cases
    if processing_mode == "original":
        print("Using ORIGINAL image (no processing)")
        final_path = image_path
    elif processing_mode == "clahe":
        print(" Preprocessing: CLAHE...")
        final_path = preprocess_clahe(image_path)

    # OCR
    print(f" Running OCR on: {os.path.basename(final_path)}")
    image_url = load_image(final_path)

    response = client.ocr.process(
        model="mistral-ocr-latest",
        document={
            "type": "image_url",
            "image_url": image_url
        }
    )

    return response, final_path


# use example
image_path = r"src\receipts\ar_image(28).jpg"

response, used_path = smart_ocr(image_path)


print("\n" + "="*50)
print(" OCR Result:")
print("="*50)
for page in response.pages:
    print(page.markdown)

# save the result as text file
output_filename = os.path.basename(image_path).replace(
    '.jpg', '.txt').replace('.png', '.txt')
output_path = os.path.join(r"test\ocr_outputs_txt", output_filename)

with open(output_path, "w", encoding="utf-8") as f:
    for page in response.pages:
        f.write(page.markdown)

print(f"\n Saved to: {output_path}")


def add(x, y): print(x + y)
