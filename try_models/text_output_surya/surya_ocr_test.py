from io import BytesIO
from PIL import Image
from surya.foundation import FoundationPredictor
from surya.recognition import RecognitionPredictor
from surya.detection import DetectionPredictor

from PIL import Image

# ---- INIT ONCE ----
foundation_predictor = FoundationPredictor(device="cpu")

detection_predictor = DetectionPredictor(device="cpu")

recognition_predictor = RecognitionPredictor(
    foundation_predictor
)

def resize_image(img: Image.Image, max_side=1600):
    # img = Image.open(BytesIO(file_bytes)).convert("RGB")
    w, h = img.size
    scale = max_side / max(w, h)
    if scale < 1:
        img = img.resize((int(w*scale), int(h*scale)), Image.BILINEAR)
    return img


def run_ocr(img: Image.Image):
    image = resize_image(img, max_side=1200)
    # Initialize predictors
    foundation_predictor = FoundationPredictor()
    recognition_predictor = RecognitionPredictor(foundation_predictor)
    detection_predictor = DetectionPredictor()
    
    # Run OCR
    predictions = recognition_predictor(
        [image], det_predictor=detection_predictor)

    for text_line in predictions[0].text_lines:
        (text_line.text)
    all_text_lines = [line.text for line in predictions[0].text_lines]

    return "\n".join(all_text_lines)

