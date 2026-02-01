import os
import json
import glob
from difflib import SequenceMatcher


# ------------------------
# Helper functions
# ------------------------


def safe_lower(x):
    return x.lower() if isinstance(x, str) else ""


def safe_str(x):
    return x if isinstance(x, str) else ""


def string_similarity(a, b):
    """Calculate similarity between two strings (0-1)"""
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def is_equal(a, b):
    
    if a is None and b is None:
        return True

    if a is None or b is None:
        return False

    return a == b


def is_equal_numeric(a, b, tolerance=0.01):
   
    # if the both are None → True
    if a is None and b is None:
        return True

    # if one is None → False
    if a is None or b is None:
        return False

    #convert to float and compare with tolerance
    try:
        a_num = float(a)
        b_num = float(b)
        return abs(a_num - b_num) <= tolerance
    except:
        # if conversion fails, do normal comparison
        return a == b


def normalize_image_name(name):
    if not name:
        return None
    base = os.path.basename(name)
    name_only, _ = os.path.splitext(base)
    return name_only


def items_are_similar(gt_item_name, pred_item_name, threshold=0.90):
    
    if not gt_item_name or not pred_item_name:
        return False

    similarity = string_similarity(
        gt_item_name.strip(), pred_item_name.strip())
    return similarity >= threshold


# ------------------------
# Load predictions with image names
# ------------------------


def load_predictions(folder_path):
    """Load predictions and add image field based on filename"""
    predictions = []

    for file_path in glob.glob(os.path.join(folder_path, "*.json")):
        filename = os.path.basename(file_path)  # ar_image(1).json
        image_name = filename.replace('.json', '.jpg')  # ar_image(1).jpg

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

            # If the JSON contains a list of predictions    
            if isinstance(data, list):
                for item in data:
                    item['image'] = image_name # Add the image name to each prediction
                    predictions.append(item)
                    
                # If the JSON contains a single object   
            else:
                data['image'] = image_name
                predictions.append(data)

    return predictions


# ------------------------
# Error detection function
# ------------------------
def get_receipt_errors(ground_truth, predictions, item_similarity_threshold=0.90):
    errors_per_image = []

    pred_by_image = {
        normalize_image_name(p.get("image")): p
        for p in predictions
        if normalize_image_name(p.get("image"))
    }

    print(f"\n Debug Info:")
    print(f"Ground truth images: {len(ground_truth)}")
    print(f"Predictions found: {len(pred_by_image)}")
    print(f"Prediction keys: {list(pred_by_image.keys())}\n")

    for gt in ground_truth:
        image_key = normalize_image_name(gt.get("image"))
        pred = pred_by_image.get(image_key)

        if not pred:
            errors_per_image.append({
                "image": gt.get("image"),
                "error": "missing_prediction"
            })
            continue

        image_errors = {}

        # -------- Store name --------
        if not is_equal(gt.get("store_name"), pred.get("store_name")):
            image_errors["store_name"] = {
                "gt": gt.get("store_name"),
                "pred": pred.get("store_name")
            }

        # -------- Total (tolerance) --------
        if not is_equal_numeric(gt.get("total_amount"), pred.get("total_amount"), tolerance=0.01):
            image_errors["total_amount"] = {
                "gt": gt.get("total_amount"),
                "pred": pred.get("total_amount")
            }

        # -------- Date --------
        if not is_equal(gt.get("date"), pred.get("date")):
            image_errors["date"] = {
                "gt": gt.get("date"),
                "pred": pred.get("date")
            }

        # -------- Receipt Number --------
        if not is_equal(gt.get("receipt_number"), pred.get("receipt_number")):
            image_errors["receipt_number"] = {
                "gt": gt.get("receipt_number"),
                "pred": pred.get("receipt_number")
            }

        # -------- Currency --------
        if not is_equal(gt.get("currency"), pred.get("currency")):
            image_errors["currency"] = {
                "gt": gt.get("currency"),
                "pred": pred.get("currency")
            }

        # -------- Taxes --------
        if not is_equal_numeric(gt.get("taxes"), pred.get("taxes"), tolerance=0.01):
            image_errors["taxes"] = {
                "gt": gt.get("taxes"),
                "pred": pred.get("taxes")
            }

        # -------- Items --------
        item_errors = []
        gt_items = gt.get("items", [])
        pred_items = pred.get("items", [])

        if len(gt_items) != len(pred_items):
            image_errors["items_count_mismatch"] = {
                "gt_count": len(gt_items),
                "pred_count": len(pred_items)
            }

        for i, (gt_item, pred_item) in enumerate(zip(gt_items, pred_items)):
            gt_name = gt_item.get("item_name")
            pred_name = pred_item.get("item_name")

            if not items_are_similar(gt_name, pred_name, threshold=item_similarity_threshold):
                item_errors.append({
                    "index": i,
                    "field": "item_name",
                    "gt": gt_name,
                    "pred": pred_name
                })

            if gt_item.get("quantity") != pred_item.get("quantity"):
                item_errors.append({
                    "index": i,
                    "field": "quantity",
                    "gt": gt_item.get("quantity"),
                    "pred": pred_item.get("quantity")
                })

        if item_errors:
            image_errors["items"] = item_errors

        if image_errors:
            errors_per_image.append({
                "image": gt.get("image"),
                "errors": image_errors
            })

    return errors_per_image



# ------------------------
# Evaluation function
# ------------------------

def evaluate_ocr(ground_truth, predictions, item_similarity_threshold=0.90):
    
    pred_by_image = {
        normalize_image_name(p.get("image")): p
        for p in predictions
        if normalize_image_name(p.get("image"))
    }

    # created ordered list of predictions matching ground truth
    matched_predictions = []
    for gt in ground_truth:
        image_key = normalize_image_name(gt.get("image"))
        pred = pred_by_image.get(image_key)
        if pred:
            matched_predictions.append(pred)
        else:
            matched_predictions.append({})

    metrics = {
        "total_amount_receipts": len(ground_truth),
        "matched_receipts": len([p for p in matched_predictions if p]),
        "store_name_exact_match": 0,
        "store_name_fuzzy_match": 0,
        "total_amount_accuracy": 0,
        "date_exact_match": 0,
        "item_name_accuracy": [],
        "item_name_similarity_match": 0,
        "total_items": 0,
        "quantity_accuracy": [],
        "receipt_number_match": 0,
        "currency_match": 0,
        "taxes_match": 0
    }

    for gt, pred in zip(ground_truth, matched_predictions):
        if not pred:
            continue

        # ---------------- Store Name ----------------
        gt_store = safe_str(gt.get("store_name"))
        pred_store = safe_str(pred.get("store_name"))

        if gt_store and pred_store and safe_lower(gt_store) == safe_lower(pred_store):
            metrics["store_name_exact_match"] += 1

        if gt_store and pred_store:
            similarity = string_similarity(gt_store, pred_store)
            if similarity > 0.8:
                metrics["store_name_fuzzy_match"] += 1

        # ---------------- Total Amount ----------------
        if gt.get("total_amount") is not None and gt.get("total_amount") == pred.get("total_amount"):
            metrics["total_amount_accuracy"] += 1

        # ---------------- Date ----------------
        if gt.get("date") and gt.get("date") == pred.get("date"):
            metrics["date_exact_match"] += 1

        # ---------------- Items ----------------
        for gt_item, pred_item in zip(gt.get("items", []), pred.get("items", [])):
            gt_name = safe_str(gt_item.get("item_name"))
            pred_name = safe_str(pred_item.get("item_name"))

            if gt_name and pred_name:
                sim = string_similarity(gt_name, pred_name)
                metrics["item_name_accuracy"].append(sim)
                metrics["total_items"] += 1

                if sim >= item_similarity_threshold:
                    metrics["item_name_similarity_match"] += 1

            gt_qty = gt_item.get("quantity")
            pred_qty = pred_item.get("quantity")

            if gt_qty is not None and pred_qty is not None:
                metrics["quantity_accuracy"].append(gt_qty == pred_qty)

        # ---------------- Receipt Number ----------------
        if gt.get("receipt_number") == pred.get("receipt_number"):
            metrics["receipt_number_match"] += 1

        # ---------------- Currency ----------------
        if gt.get("currency") == pred.get("currency"):
            metrics["currency_match"] += 1

        # ---------------- Taxes ----------------
        if gt.get("taxes") == pred.get("taxes"):
            metrics["taxes_match"] += 1

    n = metrics["matched_receipts"] or 1

    return {
        "total_receipts": metrics["total_amount_receipts"],
        "store_name_accuracy": f"{metrics['store_name_exact_match']/n*100:.1f}%",
        "receipt_number_accuracy": f"{metrics['receipt_number_match']/n*100:.1f}%",
        "date_accuracy": f"{metrics['date_exact_match']/n*100:.1f}%",
        "currency_accuracy": f"{metrics['currency_match']/n*100:.1f}%",
        "item_name_accuracy": (
            f"{sum(metrics['item_name_accuracy'])/len(metrics['item_name_accuracy'])*100:.1f}%"
            if metrics["item_name_accuracy"] else "N/A"
        ),
        "quantity_accuracy": (
            f"{sum(metrics['quantity_accuracy'])/len(metrics['quantity_accuracy'])*100:.1f}%"
            if metrics["quantity_accuracy"] else "N/A"
        ),
        "taxes_accuracy": f"{metrics['taxes_match']/n*100:.1f}%",
        "total_amount_accuracy": f"{metrics['total_amount_accuracy']/n*100:.1f}%"
    }



# ------------------------
# Main execution
# ------------------------

if __name__ == "__main__":

    # Load ground truth
    with open(r"test\ground_truth.json", "r", encoding="utf-8") as f:
        ground_truth = json.load(f)

    # Load predictions 
    predictions = load_predictions(r"test\json_outputs")

    print("="*50)
    print("OCR Evaluation Results")
    print("="*50)

    # Run evaluation 
    results = evaluate_ocr(ground_truth, predictions,
                           item_similarity_threshold=0.90)
    print(json.dumps(results, indent=2, ensure_ascii=False))

    print("\n" + "="*50)
    print(" Detailed Errors Per Image")
    print("="*50)

    # Get detailed errors per image
    errors = get_receipt_errors(
        ground_truth, predictions, item_similarity_threshold=0.90)
    print(json.dumps(errors, indent=2, ensure_ascii=False))

with open(r"test\predictions.json", "w", encoding="utf-8") as f:
    f.write(json.dumps(predictions, indent=2, ensure_ascii=False))
    
with open(r"test\results.md", "w", encoding="utf-8") as f:
    f.write("## OCR Evaluation Results\n")
    f.write("```\n")
    f.write(json.dumps(results, indent=2, ensure_ascii=False))
    f.write("\n```\n")
    f.write("## Detailed Errors Per Image\n")
    f.write("```\n")
    f.write(json.dumps(errors, indent=2, ensure_ascii=False))
    f.write("\n```\n")