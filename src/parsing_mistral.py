
# import json
# import os
# import re
# from pathlib import Path

# from dotenv import load_dotenv

# load_dotenv(dotenv_path=r"src\.env")

# api_key = os.getenv("GROQ_API_KEY")


# # ============================================================================
# # OPTION 1: Groq API (FREE - Easiest for Windows)
# # ============================================================================


# def parse_receipt_with_groq(text_file_path, api_key):
#     """
#     Parse receipt using Groq API (FREE tier available)
#     Get API key: https://console.groq.com
#     """
#     import requests

#     with open(text_file_path, 'r', encoding='utf-8') as f:
#         ocr_text = f.read()

#     prompt = f"""Extract receipt information from the OCR text and return ONLY valid JSON with no additional text:

# {{
#   "store_name": "string or null",
#   "receipt_number": "string or null",
#   "date": "dd/mm/yyyy or null",
#   "currency": "string or null",
#   "items": [
#     {{
#       "item_name": "string or null",
#       "quantity": "string or null"
#     }}
#   ],
#   "taxes": "string or null",
#   "total_amount": "string or null"
# }}

# OCR Text:
# {ocr_text}"""

#     response = requests.post(
#         "https://api.groq.com/openai/v1/chat/completions",
#         headers={
#             "Authorization": f"Bearer {api_key}",
#             "Content-Type": "application/json"
#         },
#         json={
#             "model": "llama-3.3-70b-versatile",
#             "messages": [{"role": "user", "content": prompt}],
#             "temperature": 0.1
#         }
#     )

#     result = response.json()
#     content = result['choices'][0]['message']['content']

#     # Extract JSON from response
#     json_match = re.search(r'\{.*\}', content, re.DOTALL)
#     if json_match:
#         return json.loads(json_match.group())
#     return None


# # ============================================================================
# # Helper Functions
# # ============================================================================
# def save_receipt_json(receipt_data, output_path):
#     """Save parsed receipt data to JSON file"""
#     with open(output_path, 'w', encoding='utf-8') as f:
#         json.dump(receipt_data, f, indent=2, ensure_ascii=False)
#     print(f"✓ Saved to {output_path}")


# # ============================================================================
# # Main Usage Example
# # ============================================================================
# if __name__ == "__main__":
#     txt_file = "pharmacy.txt"  # Your Surya OCR output file

#     # ========================================================================
#     # RECOMMENDED FOR WINDOWS: Use Groq (Fastest & Easiest)
#     # ========================================================================
#     # Step 1: Get free API key from https://console.groq.com
#     # Step 2: Install requests: pip install requests
#     # Step 3: Uncomment and use:

#     # Replace with your key
#     GROQ_API_KEY = "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"

#     print("Parsing receipt with Groq...")
#     receipt_data = parse_receipt_with_groq(txt_file, GROQ_API_KEY)

#     if receipt_data:
#         save_receipt_json(receipt_data, "receipt_output.json")
#         print(json.dumps(receipt_data, indent=2))
#     else:
#         print("Failed to parse receipt")


import json
import os
import re
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(dotenv_path=r"src\.env")

api_key = os.getenv("GROQ_API_KEY")


def parse_receipt_with_groq(ocr_text):
    """
    Parse receipt using Groq API (FREE tier available)
    Get API key: https://console.groq.com
    """
    import requests

    
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
