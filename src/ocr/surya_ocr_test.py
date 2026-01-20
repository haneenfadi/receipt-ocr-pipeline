# from PIL import Image
# from surya.foundation import FoundationPredictor
# from surya.recognition import RecognitionPredictor
# from surya.detection import DetectionPredictor

# image = Image.open(r"src\test_images\ar_image(1).jpg")
# foundation_predictor = FoundationPredictor()
# recognition_predictor = RecognitionPredictor(foundation_predictor)
# detection_predictor = DetectionPredictor()

# predictions = recognition_predictor([image], det_predictor=detection_predictor)
# print(predictions)


# the final code
# from PIL import Image
# from surya.foundation import FoundationPredictor
# from surya.recognition import RecognitionPredictor
# from surya.detection import DetectionPredictor

# from PIL import Image


# def resize_image(img, max_side=1600):
#     w, h = img.size
#     scale = max_side / max(w, h)
#     if scale < 1:
#         img = img.resize((int(w*scale), int(h*scale)), Image.BILINEAR)
#     return img


# image = Image.open(r"src\test_images\ar_image(7).jpg").convert("RGB")
# image = resize_image(image, max_side=1600)


# # Initialize predictors
# foundation_predictor = FoundationPredictor()
# recognition_predictor = RecognitionPredictor(foundation_predictor)
# detection_predictor = DetectionPredictor()

# # Run OCR
# predictions = recognition_predictor([image], det_predictor=detection_predictor)

# # Print extracted text in a clean format
# print("\n=== Extracted Text ===\n")
# for text_line in predictions[0].text_lines:
#     print(f"{text_line.text} (Confidence: {text_line.confidence:.2f})")

# # Or just the text without confidence
# print("\n=== Clean Text Only ===\n")
# for text_line in predictions[0].text_lines:
#     print(text_line.text)

# with open("text_output/ara_7_surya_ocr.txt", "w", encoding="utf-8") as f:
#     for text_line in predictions[0].text_lines:
#         f.write(text_line.text + "\n")


# from PIL import Image
# from surya.table_rec import TableRecPredictor

# image = Image.open(r"src\test_images\en_image(2).jpg")
# table_rec_predictor = TableRecPredictor()

# table_predictions = table_rec_predictor([image])

# # with open("table_predictions.txt", 'w', encoding="utf-8") as f:
# #     f.write(table_predictions)

# print(table_predictions)


from io import BytesIO
from PIL import Image
from surya.foundation import FoundationPredictor
from surya.recognition import RecognitionPredictor
from surya.detection import DetectionPredictor

from PIL import Image


def resize_image(img: Image.Image, max_side=1600):
    # img = Image.open(BytesIO(file_bytes)).convert("RGB")
    w, h = img.size
    scale = max_side / max(w, h)
    if scale < 1:
        img = img.resize((int(w*scale), int(h*scale)), Image.BILINEAR)
    return img


def run_ocr(img: Image.Image):
    image = resize_image(img, max_side=1600)
    # Initialize predictors
    foundation_predictor = FoundationPredictor()
    recognition_predictor = RecognitionPredictor(foundation_predictor)
    detection_predictor = DetectionPredictor()

    # Run OCR
    predictions = recognition_predictor(
        [image], det_predictor=detection_predictor)

    # Or just the text without confidence
    # for text_line in predictions[0].text_lines:
    #     (text_line.text)
    all_text_lines = [line.text for line in predictions[0].text_lines]

    return "\n".join(all_text_lines)


# # Open the image as bytes
# with open(r"src\test_images\ar_image(7).jpg", "rb") as f:
#     img = BytesIO(f.read())

# # Pass this to run_ocr
# text = run_ocr(img.fileno())

# print("OCR Result from file-like object:\n", text)
