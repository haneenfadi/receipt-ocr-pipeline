import json
import os
import re

from dotenv import load_dotenv

load_dotenv(dotenv_path=r"src\.env")

api_key = os.getenv("GROQ_API_KEY")


def parse_receipt_with_groq(text_file_path, api_key):
  
    import requests

    with open(text_file_path, 'r', encoding='utf-8') as f:
        ocr_text = f.read()

    prompt = f"""Extract receipt information from the OCR text and return ONLY valid JSON with no additional text:

{{
  "store_name": "string or null",
  "receipt_number": "string or null",
  "date": "dd/mm/yyyy or null",
  "currency": "string or null",
  "items": [
    {{
      "item_name": "string or null",
      "quantity": "string or null"
    }}
  ],
  "taxes": "string or null",
  "total_amount": "string or null"
}}
Field-specific guidelines:
Store Name: Extract only if clearly presented in the receipt header or as part of the logo text.
Do not infer or guess based on products, context, or common brand recognition.
Prioritize the main brand or store name from the logo and disregard branch names or locations unless the main name is absent.
- receipt_number: Any identifier labeled as receipt number, invoice number, order number, or similar(only the number without extra text).
- date: The transaction date in dd/mm/yyyy format.
* Important: Fix malformed dates. Examples:
  - "2804-2022" → "28/04/2022"

- currency: The currency symbol or code (e.g., USD, JOD, $, €).
- items: List of purchased items.
  - item_name: The product or service name. 
  * Do NOT add placeholder items like "item_name": null, "quantity": null.
  - quantity: The quantity if explicitly mentioned(such as "2x" write it as 2).
- taxes: Extract from "ضريبة" field ONLY. If you see "خدمة: 34.95", that is service charge NOT tax. Example: "ضريبة: 0" means taxes=0.
  -Look for "ضريبة" or "ضريبة القيمة المضافة" followed by a number.

- total_amount: The final total amount paid, usually labeled as total, grand total, or amount due.
  - Look for keywords like "المجموع الكلي", "الإجمالي", "المبلغ الإجمالي", "Total", "Grand Total", or "Amount Due" followed by a number.
  
OCR Text:
{ocr_text}"""

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1
        }
    )

    result = response.json()
    content = result['choices'][0]['message']['content']

    # Extract JSON from response
    json_match = re.search(r'\{.*\}', content, re.DOTALL)
    if json_match:
        return json.loads(json_match.group())
    return None


# ============================================================================
# Helper Functions
# ============================================================================
def save_receipt_json(receipt_data, output_path):
    """Save parsed receipt data to JSON file"""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(receipt_data, f, indent=2, ensure_ascii=False)
    print(f"✓ Saved to {output_path}")


# ============================================================================
# Main Usage Example
# ============================================================================
if __name__ == "__main__":
    txt_file = r"test\ocr_outputs_txt\ar_image(28).txt"


    print("Parsing receipt with Groq...")
    receipt_data = parse_receipt_with_groq(txt_file, api_key)

    if receipt_data:
        save_receipt_json(
            receipt_data, r"test\json_outputs\ar_image(28).json")
        print(json.dumps(receipt_data, indent=2))
    else:
        print("Failed to parse receipt")
