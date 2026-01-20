# import json
# import re
# from pathlib import Path

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
# # OPTION 2: Hugging Face Inference API (FREE)
# # ============================================================================
# def parse_receipt_with_huggingface(text_file_path, api_key):
#     """
#     Parse receipt using Hugging Face Inference API (FREE)
#     Get API key: https://huggingface.co/settings/tokens
#     """
#     import requests
    
#     with open(text_file_path, 'r', encoding='utf-8') as f:
#         ocr_text = f.read()
    
#     prompt = f"""Extract receipt data as JSON only:
# {{"store_name": null, "receipt_number": null, "date": "dd/mm/yyyy", "currency": null, "items": [{{"item_name": null, "quantity": null}}], "taxes": null, "total_amount": null}}

# OCR Text:
# {ocr_text}"""

#     API_URL = "https://api-inference.huggingface.co/models/meta-llama/Llama-3.2-3B-Instruct"
#     headers = {"Authorization": f"Bearer {api_key}"}
    
#     response = requests.post(
#         API_URL,
#         headers=headers,
#         json={"inputs": prompt, "parameters": {"max_new_tokens": 500, "temperature": 0.1}}
#     )
    
#     result = response.json()
#     if isinstance(result, list) and len(result) > 0:
#         content = result[0].get('generated_text', '')
#         json_match = re.search(r'\{.*\}', content, re.DOTALL)
#         if json_match:
#             return json.loads(json_match.group())
#     return None


# # ============================================================================
# # OPTION 3: LM Studio (FREE Local - Windows Compatible)
# # ============================================================================
# def parse_receipt_with_lmstudio(text_file_path, base_url="http://localhost:1234/v1"):
#     """
#     Parse receipt using LM Studio (FREE local server)
#     Download: https://lmstudio.ai
#     Start local server in LM Studio, then run this
#     """
#     import requests
    
#     with open(text_file_path, 'r', encoding='utf-8') as f:
#         ocr_text = f.read()
    
#     prompt = f"""Extract receipt information and return ONLY JSON:

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

#     try:
#         response = requests.post(
#             f"{base_url}/chat/completions",
#             json={
#                 "model": "local-model",
#                 "messages": [{"role": "user", "content": prompt}],
#                 "temperature": 0.1
#             },
#             timeout=60
#         )
        
#         result = response.json()
#         content = result['choices'][0]['message']['content']
        
#         json_match = re.search(r'\{.*\}', content, re.DOTALL)
#         if json_match:
#             return json.loads(json_match.group())
#     except requests.exceptions.ConnectionError:
#         raise Exception("LM Studio not running. Start the local server in LM Studio first.")
    
#     return None


# # ============================================================================
# # OPTION 4: OpenRouter (FREE tier with multiple models)
# # ============================================================================
# def parse_receipt_with_openrouter(text_file_path, api_key):
#     """
#     Parse receipt using OpenRouter (FREE tier available)
#     Get API key: https://openrouter.ai/keys
#     """
#     import requests
    
#     with open(text_file_path, 'r', encoding='utf-8') as f:
#         ocr_text = f.read()
    
#     prompt = f"""Extract receipt information and return ONLY valid JSON:

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
#         "https://openrouter.ai/api/v1/chat/completions",
#         headers={
#             "Authorization": f"Bearer {api_key}",
#             "Content-Type": "application/json"
#         },
#         json={
#             "model": "meta-llama/llama-3.2-3b-instruct:free",
#             "messages": [{"role": "user", "content": prompt}]
#         }
#     )
    
#     result = response.json()
#     content = result['choices'][0]['message']['content']
    
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
#     txt_file = "receipt.txt"  # Your Surya OCR output file
    
#     # ========================================================================
#     # RECOMMENDED FOR WINDOWS: Use Groq (Fastest & Easiest)
#     # ========================================================================
#     # Step 1: Get free API key from https://console.groq.com
#     # Step 2: Install requests: pip install requests
#     # Step 3: Uncomment and use:
    
#     GROQ_API_KEY = "gsk_YOUR_API_KEY_HERE"  # Replace with your key
    
#     print("Parsing receipt with Groq...")
#     receipt_data = parse_receipt_with_groq(txt_file, GROQ_API_KEY)
    
#     if receipt_data:
#         save_receipt_json(receipt_data, "receipt_output.json")
#         print(json.dumps(receipt_data, indent=2))
#     else:
#         print("Failed to parse receipt")
    
#     # ========================================================================
#     # Alternative Options (uncomment to use):
#     # ========================================================================
    
#     # Option 2: Hugging Face
#     # HF_API_KEY = "hf_YOUR_TOKEN"
#     # receipt_data = parse_receipt_with_huggingface(txt_file, HF_API_KEY)
    
#     # Option 3: LM Studio (local)
#     # Download from https://lmstudio.ai, load a model, start server
#     # receipt_data = parse_receipt_with_lmstudio(txt_file)
    
#     # Option 4: OpenRouter
#     # OPENROUTER_KEY = "sk-or-v1-YOUR_KEY"
#     # receipt_data = parse_receipt_with_openrouter(txt_file, OPENROUTER_KEY)
    
import json
import re
from pathlib import Path

# ============================================================================
# OPTION 1: Groq API (FREE - Easiest for Windows)
# ============================================================================


def parse_receipt_with_groq(text_file_path, api_key):
    """
    Parse receipt using Groq API (FREE tier available)
    Get API key: https://console.groq.com
    """
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
    txt_file = "pharmacy.txt"  # Your Surya OCR output file

    # ========================================================================
    # RECOMMENDED FOR WINDOWS: Use Groq (Fastest & Easiest)
    # ========================================================================
    # Step 1: Get free API key from https://console.groq.com
    # Step 2: Install requests: pip install requests
    # Step 3: Uncomment and use:

    GROQ_API_KEY = "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"  # Replace with your key

    print("Parsing receipt with Groq...")
    receipt_data = parse_receipt_with_groq(txt_file, GROQ_API_KEY)

    if receipt_data:
        save_receipt_json(receipt_data, "receipt_output.json")
        print(json.dumps(receipt_data, indent=2))
    else:
        print("Failed to parse receipt")
