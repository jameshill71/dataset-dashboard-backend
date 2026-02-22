# Dataset Dashboard Backend (FastAPI)

A lightweight FastAPI service that exposes **dataset metadata** (filename, row count, columns) for CSV files stored in the project’s `data/` directory.

Designed as a small, “real-world” backend demonstration: clean structure, streaming file inspection, and a proper readiness-style `/health` endpoint.

---

## What it does

- Scans the `data/` folder for `*.csv` files
- For each CSV, returns:
  - `name` (filename)
  - `row_count` (data rows only, excluding header)
  - `columns` (cleaned header fields)
- Provides a readiness-style health endpoint that verifies:
  - `data/` exists and is a directory
  - at least one CSV exists
  - each CSV is readable and has a header row

---

## Project Structure
# Dataset Dashboard Backend (FastAPI)

A lightweight FastAPI service that exposes **dataset metadata** (filename, row count, columns) for CSV files stored in the project’s `data/` directory.

Designed as a small, “real-world” backend demonstration: clean structure, streaming file inspection, and a proper readiness-style `/health` endpoint.

---

## What it does

- Scans the `data/` folder for `*.csv` files
- For each CSV, returns:
  - `name` (filename)
  - `row_count` (data rows only, excluding header)
  - `columns` (cleaned header fields)
- Provides a readiness-style health endpoint that verifies:
  - `data/` exists and is a directory
  - at least one CSV exists
  - each CSV is readable and has a header row

---

## Project Structure
```bash
dataset-dashboard-backend/
├─ app/
│ ├─ main.py
│ └─ services/
│ └─ datasets.py
├─ data/
│ └─ inventory.csv
├─ requirements.txt
└─ README.md
```

---

## Requirements

- Python 3.10+
- Dependencies (standard library + FastAPI + Uvicorn)

`requirements.txt` should include:

- `fastapi`
- `uvicorn` (recommended: `uvicorn[standard]`)

---

## Setup

Create a virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run the API

From the project root:
```bash
uvicorn app.main:app --reload
```
Then open:

API docs (Swagger UI): http://127.0.0.1:8000/docs

ReDoc: http://127.0.0.1:8000/redoc

Endpoints
GET /datasets

Returns metadata for all CSV datasets in data/.

Example:

```bash
curl -s http://127.0.0.1:8000/datasets | python3 -m json.tool
```
Example response:
```JSON
{
  "datasets": [
    {
      "name": "inventory.csv",
      "row_count": 20,
      "columns": ["item_id", "name", "category", "price", "quantity", "supplier"]
    }
  ]
}
```
GET /health

Readiness-style health endpoint.

Returns 200 OK when the service is ready (data folder exists, CSVs present and readable)

Returns 503 Service Unavailable when not ready

Always returns a structured report describing what it checked

Example:
```bash
curl -i http://127.0.0.1:8000/health
```
Example response (ready):
```JSON
{
  "status": "ok",
  "ready": true,
  "datasets_found": 1,
  "checks": {
    "data_dir_exists": true,
    "data_dir_is_dir": true,
    "csv_count": 1,
    "csv_readable": 1,
    "csv_unreadable": 0,
    "errors": []
  }
}
```
Example response (not ready):
```JSON
{
  "status": "degraded",
  "ready": false,
  "datasets_found": 0,
  "checks": {
    "data_dir_exists": true,
    "data_dir_is_dir": true,
    "csv_count": 0,
    "csv_readable": 0,
    "csv_unreadable": 0,
    "errors": ["No CSV files found in data/ (expected at least one)."]
  }
}
```

## Notes on Implementation

* Robust path handling: datasets.py locates data/ relative to the project root using Path(__file__).resolve(), so it works even if you run uvicorn from different directories.

* Streaming inspection: CSV files are read line-by-line, avoiding loading full files into memory.

* Defensive behavior: missing folders, empty files, or unreadable CSVs do not crash the service; they are reported in /health.

## Future Enhancements (nice next steps)

* Add GET /datasets/{name} to fetch metadata for a single dataset

* Add column type inference (int/float/string sampling)

* Add pagination and/or dataset preview endpoints

* Add JSON/CSV export of dataset summaries

* Add Dockerfile + container healthcheck wiring

## License

MIT