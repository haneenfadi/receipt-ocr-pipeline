# ReceiptVision 

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-FF4B4B.svg)](https://streamlit.io/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)

AI-powered receipt data extraction system that converts images into structured data. Built with FastAPI and Streamlit, containerized with Docker for seamless deployment.

---

## Technical Features

- **Smart Image Processing:** Automatic quality enhancement before OCR
- **Structured Data Output:** Clean JSON format for easy integration
- **Instant Results:** Upload and extract in seconds
- **Auto-Save:** Direct database storage without manual steps
- **Dual Interface:** RESTful API for integration, Streamlit UI for interactive use
- **Container Support:** Docker and Docker Compose ready

---

## Architecture

```
┌─────────────┐      ┌──────────────┐      ┌──────────────┐
│  Streamlit  │ ───> │   FastAPI    │ ───> │  Image Pre-  │
│     UI      │      │   Backend    │      │  processing  │
└─────────────┘      └──────────────┘      └──────────────┘
                            │                      │
                            │                      ▼
                            │               ┌─────────────┐
                            │               │ OCR Engine  │
                            │               └─────────────┘
                            │                      │
                            │                      ▼
                            │               ┌─────────────┐
                            │───────────────│ LLM Parser  │
                            │               │   (JSON)    │
                            │               └─────────────┘
                            ▼                     
                     ┌──────────────┐ 
                     │   Database   │
                     │   Storage    │
                     └──────────────┘
```

**Pipeline Stages:**
1. Upload receipt image via Streamlit UI
2. Image gets preprocessed for better quality
3. OCR engine extracts text from the image
4. LLM parses text into structured JSON
5. Data automatically saves to database

---

## Demo

### Streamlit Interface
![Web Interface using streamlit](./aux-files/streamlit_app.PNG)


---

**Extraction Schema:**

| Field | Description |
|-------|-------------|
| store_name | Name of the store/merchant |
| receipt_number | Receipt or invoice number |
| date | Transaction date |
| currency | Currency code (USD, EUR, etc.) |
| items | List of purchased items with quantities  |
| taxes | Tax amount |
| total_amount | Total transaction amount |

---

## Data Format

### Input
Receipt image in JPG, PNG, or JPEG format

### Output

```json
{
    "store_name": "Caribou Coffee",
    "receipt_number": "90535",
    "date": "23/10/2021",
    "currency": "LE",
    "items": [
        {
            "item_name": "Espresso L",
            "quantity": "1"
        }
    ],
    "taxes": "4.67",
    "total_amount": "38.00"
}
```

---

## Installation

Clone the repository and set up environment:

```bash
git clone https://github.com/haneenfadi/receipt-ocr-pipeline.git

```

### Environment Configuration

```bash
cp .env.example .env
```

Edit `.env`:
```dotenv
API_AUTH_PASSWORD="your-auth-password"
GROQ_API_KEY="your-groq-api-key"
MISTRAL_API_KEY="your-mistral-api-key"
APP_ENV="dev"
```

---

### Local Development

```bash
python -m venv ocr
source ocr/bin/activate  # Windows: ocr\Scripts\activate
pip install -r requirements.txt
```

### Docker Deployment

```bash
docker-compose up -d
```

---

## Usage

### Streamlit Interface

```bash
streamlit run src/app/streamlit.py
```

Access at `http://localhost:8501`

### FastAPI Endpoint

```bash
uvicorn src.app.api:app --reload --host 0.0.0.0 --port 8000
```

API available at `http://localhost:8000`  
Interactive documentation: `http://localhost:8000/docs`


**Request Example:**

```bash
curl -X POST "http://localhost:8000/api/v1/receipt_parser/upload" \
  -H "accept: application/json" \
  -H "X-API-Password: your-auth-password" \
  -F "file=@/path/to/receipt.jpg"
```

---

### Testing with Postman

**Endpoint:** `POST http://localhost:8000/api/v1/receipt_parser/upload`

**Request:**
- Method: `POST`
- Body: `form-data`
- Key: `file` (type: File)
- Value: Select your receipt image

**Headers:**
```
Content-Type: multipart/form-data
```

**Response:** JSON with extracted receipt data

---
## Project Structure
```
OCR/
│
├── Dockerfile                      # Container definition
├── docker-compose.yml              # Multi-container orchestration
├── .dockerignore                   # Docker build exclusions
├── .gitignore                      # Git tracking exclusions
├── .env.example                    # Environment variables template
├── requirements.txt                # Python dependencies
├── README.md                       # Project documentation
│
├── aux-files/                      # Auxiliary files
│   └── streamlit_app.PNG           # UI screenshot
│
├── db/                             # Database layer
│   ├── database.py                 # Database tables creation
│   ├── db_maintenance.py           # Database maintenance
│   └── stored_receipts/            # Stored receipt images
│   
└── src/                            # Source code
    │
    ├── app/
    │   ├── api.py                  # FastAPI backend
    │   └── streamlit.py            # Streamlit interface
    │
    ├── assets/
    │   └── streamlit.css           # Streamlit styling
    │
    ├── config/
    │   └── settings.py             # Application configuration
    │
    ├── ocr/      
    │   ├── mistral_ocr.py          # OCR engine
    │   └── parsing.py              # LLM JSON parser
    │
    ├── receipts/                   # Receipt samples
    │
    ├── routes/
    │   ├── base.py                 # Base routes
    │   └── receipt_parser.py       # Receipt parsing endpoints
    │
    ├── utils/
    │   ├── image_preprocessing.py  # Image enhancement
    │   ├── ip_whitelist.py         # IP filtering
    │   └── schema.py               # Pydantic schemas
    │
    └── test/                       # Testing suite
        ├── evaluate.py             # Model evaluation script
        ├── test_images_original_ocr.py   # Test OCR on original images
        ├── test_images_processed_ocr.py  # Test OCR on preprocessed images
        ├── test_parsing_one_file.py      # Single file parsing test
        │
        ├── ground_truth.json       # Ground truth labels
        ├── predictions.json        # Model predictions
        ├── evaluated_results.md    # Evaluation metrics
        ├── results.md              # Test results summary
        ├── image_processing.md     # Image processing notes
        │
        ├── json_outputs/           # Parsed JSON outputs
        │   ├── ar_image(1-8).json
        │   └── ar_image(15-16).json
        │
        └── ocr_outputs_txt/        # Raw OCR text outputs
            ├── ar_image(1-16).txt
            └── en_image(1,7).txt
```

---

## Best Practices

-  Use clear, well-lit images 
-  The system automatically handles most quality issues through preprocessing
-  All extracted data is saved immediately to the database

---



## Security

- Environment variables stored in `.env` 
- API authentication support

---

## Author

**Haneen Fadi**  
GitHub: [@haneenfadi](https://github.com/haneenfadi)  
Email: haneenqutishat03@gmail.com

---