# Docker Guide

This project runs two containers:

- `receipt-parser`: FastAPI backend on port `8000`
- `streamlit-ui`: Streamlit frontend on port `8501`

## Prerequisites

- Docker Desktop installed
- A `.env` file at `src/.env`

The compose file loads environment variables from `src/.env`.

## Build and Run

From the project root:

```bash
docker compose up --build
```

To run in the background:

```bash
docker compose up -d --build
```

## Stop Containers

```bash
docker compose down
```

## View Logs

Backend logs:

```bash
docker compose logs -f receipt-parser
```

Streamlit logs:

```bash
docker compose logs -f streamlit-ui
```

All logs:

```bash
docker compose logs -f
```

## Test the App

After the containers start, open:

- FastAPI docs: http://localhost:8000/docs
- Streamlit app: http://localhost:8501

