import os
import json
import glob
from difflib import SequenceMatcher

GROUND_TRUTH_PATH = r"test\ground_truth.json"
PREDICTIONS_FOLDER = r"test\json_outputs"
PREDICTIONS_OUTPUT_PATH = r"test\predictions.json"
RESULTS_OUTPUT_PATH = r"test\results.md"

# ------------------------
# Helper functions
# ------------------------


def safe_lower(x):
    return x.lower() if isinstance(x, str) else ""


def safe_str(x):
    return x if isinstance(x, str) else ""


def string_similarity(a, b):
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
    if a is None and b is None:
        return True
    if a is None or b is None:
        return False
    try:
        return abs(float(a) - float(b)) <= tolerance
    except:
        return a == b


def normalize_image_name(name):
    if not name:
        return None
    base = os.path.basename(name)
    name_only, _ = os.path.splitext(base)
    return name_only

# ------------------------
# normalization + matching
# ------------------------


def normalize_name(value):
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v).strip().lower() for v in value if v]
    return [str(value).strip().lower()]


def match_any(gt_values, pred_values, threshold=0.90):
    gt_list = normalize_name(gt_values)
    pred_list = normalize_name(pred_values)

    for gt in gt_list:
        for pred in pred_list:
            if string_similarity(gt, pred) >= threshold:
                return True
    return False


def match_items_unordered(gt_items, pred_items, threshold=0.90):
    """
    Greedy order-independent matching
    """
    matched_pred = set()
    results = []

    for gt_idx, gt_item in enumerate(gt_items):
        best_score = 0
        best_pred_idx = None

        for pred_idx, pred_item in enumerate(pred_items):
            if pred_idx in matched_pred:
                continue

            sim = 0
            for g in normalize_name(gt_item.get("item_name")):
                for p in normalize_name(pred_item.get("item_name")):
                    sim = max(sim, string_similarity(g, p))

            if sim > best_score:
                best_score = sim
                best_pred_idx = pred_idx

        if best_pred_idx is not None and best_score >= threshold:
            matched_pred.add(best_pred_idx)
            results.append((gt_idx, best_pred_idx, best_score))
        else:
            results.append((gt_idx, best_pred_idx, 0))

    return results

# ------------------------
# Load predictions
# ------------------------


def load_predictions(folder_path):
    predictions = []

    for file_path in glob.glob(os.path.join(folder_path, "*.json")):
        filename = os.path.basename(file_path)
        image_name = filename.replace('.json', '.jpg')

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

            if isinstance(data, list):
                for item in data:
                    item['image'] = image_name
                    predictions.append(item)
            else:
                data['image'] = image_name
                predictions.append(data)

    return predictions

# ------------------------
# Error analysis
# ------------------------


def get_receipt_errors(ground_truth, predictions, item_similarity_threshold=0.90):

    errors_per_image = []

    pred_by_image = {
        normalize_image_name(p.get("image")): p
        for p in predictions
        if normalize_image_name(p.get("image"))
    }

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

        if not match_any(gt.get("store_name"), pred.get("store_name")):
            image_errors["store_name"] = {
                "gt": gt.get("store_name"),
                "pred": pred.get("store_name")
            }

        if not is_equal_numeric(gt.get("total_amount"), pred.get("total_amount")):
            image_errors["total_amount"] = {
                "gt": gt.get("total_amount"),
                "pred": pred.get("total_amount")
            }

        if not is_equal(gt.get("date"), pred.get("date")):
            image_errors["date"] = {
                "gt": gt.get("date"),
                "pred": pred.get("date")
            }

        if not is_equal(gt.get("receipt_number"), pred.get("receipt_number")):
            image_errors["receipt_number"] = {
                "gt": gt.get("receipt_number"),
                "pred": pred.get("receipt_number")
            }

        if not is_equal(gt.get("currency"), pred.get("currency")):
            image_errors["currency"] = {
                "gt": gt.get("currency"),
                "pred": pred.get("currency")
            }

        if not is_equal_numeric(gt.get("taxes"), pred.get("taxes")):
            image_errors["taxes"] = {
                "gt": gt.get("taxes"),
                "pred": pred.get("taxes")
            }

        # ---------------- ITEMS----------------
        item_errors = []
        gt_items = gt.get("items", [])
        pred_items = pred.get("items", [])

        matches = match_items_unordered(
            gt_items, pred_items, item_similarity_threshold)

        if len(gt_items) != len(pred_items):
            image_errors["items_count_mismatch"] = {
                "gt_count": len(gt_items),
                "pred_count": len(pred_items)
            }

        for gt_idx, pred_idx, sim in matches:
            gt_item = gt_items[gt_idx]

            if pred_idx is None:
                item_errors.append({
                    "index": gt_idx,
                    "field": "item_name",
                    "gt": gt_item.get("item_name"),
                    "pred": None
                })
                continue

            pred_item = pred_items[pred_idx]

            if sim < item_similarity_threshold:
                item_errors.append({
                    "index": gt_idx,
                    "field": "item_name",
                    "gt": gt_item.get("item_name"),
                    "pred": pred_item.get("item_name")
                })

            if gt_item.get("quantity") != pred_item.get("quantity"):
                item_errors.append({
                    "index": gt_idx,
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
# Evaluation
# ------------------------


def evaluate_ocr(ground_truth, predictions, item_similarity_threshold=0.90):

    pred_by_image = {
        normalize_image_name(p.get("image")): p
        for p in predictions
        if normalize_image_name(p.get("image"))
    }

    metrics = {
        "store_name_exact_match": 0,
        "total_amount_accuracy": 0,
        "date_exact_match": 0,
        "item_name_accuracy": [],
        "item_name_similarity_match": 0,
        "total_items": 0,
        "quantity_accuracy": [],
        "receipt_number_match": 0,
        "currency_match": 0,
        "taxes_match": 0,
        "matched_receipts": 0
    }

    for gt in ground_truth:
        pred = pred_by_image.get(normalize_image_name(gt.get("image")))
        if not pred:
            continue

        metrics["matched_receipts"] += 1

        if match_any(gt.get("store_name"), pred.get("store_name")):
            metrics["store_name_exact_match"] += 1

        if gt.get("total_amount") == pred.get("total_amount"):
            metrics["total_amount_accuracy"] += 1

        if gt.get("date") == pred.get("date"):
            metrics["date_exact_match"] += 1

        if gt.get("receipt_number") == pred.get("receipt_number"):
            metrics["receipt_number_match"] += 1

        if gt.get("currency") == pred.get("currency"):
            metrics["currency_match"] += 1

        if gt.get("taxes") == pred.get("taxes"):
            metrics["taxes_match"] = metrics.get("taxes_match", 0) + 1

        # ITEMS FIXED
        gt_items = gt.get("items", [])
        pred_items = pred.get("items", [])

        matches = match_items_unordered(
            gt_items, pred_items, item_similarity_threshold)

        for gt_idx, pred_idx, sim in matches:

            gt_item = gt_items[gt_idx]

            if pred_idx is None:
                continue

            pred_item = pred_items[pred_idx]

            metrics["item_name_accuracy"].append(sim)
            metrics["total_items"] += 1

            if sim >= item_similarity_threshold:
                metrics["item_name_similarity_match"] += 1

            if gt_item.get("quantity") == pred_item.get("quantity"):
                metrics["quantity_accuracy"].append(True)

    n = metrics["matched_receipts"] or 1

    return {
        "total_receipts": len(ground_truth),
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
        )
    }

# ------------------------
# Main
# ------------------------


if __name__ == "__main__":

    with open(GROUND_TRUTH_PATH, "r", encoding="utf-8") as f:
        ground_truth = json.load(f)

    predictions = load_predictions(PREDICTIONS_FOLDER)

    results = evaluate_ocr(ground_truth, predictions)
    print(json.dumps(results, indent=2, ensure_ascii=False))

    errors = get_receipt_errors(ground_truth, predictions)
    print(json.dumps(errors, indent=2, ensure_ascii=False))

    with open(PREDICTIONS_OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(predictions, f, indent=2, ensure_ascii=False)

    with open(RESULTS_OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(json.dumps(results, indent=2, ensure_ascii=False))
        f.write("\n\n")
        f.write(json.dumps(errors, indent=2, ensure_ascii=False))
