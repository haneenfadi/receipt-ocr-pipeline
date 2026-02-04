import numpy as np
import base64
import cv2

def check_image_quality(image_bytes: bytes) -> str:
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        return "original"

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # (Sharpness)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()

    if laplacian_var < 35:
        return "original"

    # brightness
    brightness = np.mean(gray)
    is_too_dark = brightness < 80
    is_too_bright = brightness > 180

    # contrast
    contrast = gray.std()
    is_low_contrast = contrast < 40

    # decide preprocessing method
    if is_too_dark or is_too_bright or is_low_contrast:
        return "clahe"

    return "original"


def preprocess_clahe(image_bytes: bytes) -> bytes:
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)

    # check to ensure image was loaded
    if img is None:
        return image_bytes

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(img)

    success, encoded_img = cv2.imencode(".png", enhanced)
    if not success:
        return image_bytes

    return encoded_img.tobytes()


def bytes_to_base64_url(image_bytes: bytes, mime_type: str) -> str:
    base64_encoded = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:{mime_type};base64,{base64_encoded}"
