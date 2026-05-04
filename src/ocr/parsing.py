import json
import os
import re
import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path=r"src\.env")

api_key = os.getenv("GROQ_API_KEY")


def parse_receipt_with_groq(ocr_text):
    """
    Parse receipt using Groq API (FREE tier available)
    Get API key: https://console.groq.com
    """
    

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
Extract the main store or brand name from the receipt header or logo.
   - **If the store name appears in both English and Arabic, always prefer the English version.**
   - Do not guess based on product names or context.
   - Ignore branch names, locations, or other extra text unless the main name is missing.
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

    try:
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
        },
        timeout=(10, 90),
      )
      response.raise_for_status()
      result = response.json()
      content = result["choices"][0]["message"]["content"]
    except requests.Timeout as exc:
      raise RuntimeError("Groq parsing request timed out") from exc
    except (requests.RequestException, KeyError, IndexError, ValueError) as exc:
      raise RuntimeError("Failed to parse receipt with Groq API") from exc

    # Extract JSON from response
    json_match = re.search(r'\{.*\}', content, re.DOTALL)
    if json_match:
        return json.loads(json_match.group())
    return None
