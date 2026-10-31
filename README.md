# AI Business Intelligence Assistant

A small Python-based business intelligence assistant that reads a sales CSV, validates the data, stores it in SQLite, and answers natural-language sales questions using a safe Gemini intent-classification layer backed by deterministic SQL analytics.

## Project overview

This project was built to satisfy a data and AI assessment that required:

- loading sales data from a source CSV file
- preserving raw records while tracking invalid or excluded transactions
- calculating revenue and trend metrics from SQLite
- allowing natural-language questions about sales performance
- returning answers grounded in database calculations rather than model-generated numbers
- providing a simple dashboard for users to interact with the assistant

The application intentionally keeps AI limited to intent detection. The real business numbers come from predefined SQL queries and Python analytics code.

## Problem statement

The business needs a lightweight way to answer core sales questions from a dataset with data-quality issues, including returned items, zero-quantity orders, and missing unit prices. The solution must:

- import and normalize the raw sales file
- identify and trace invalid records without deleting the original data
- calculate revenue correctly for completed, valid sales only
- answer business questions such as total revenue, top product, monthly trend, top region, and month-over-month comparisons
- present the results through a simple user interface

## Features and capabilities

- SQLite-backed transactional data storage
- CSV import and validation with issue tracking
- exclusion of invalid and returned revenue records
- five supported analytics intents:
  - total revenue
  - product revenue breakdown
  - monthly trend
  - region revenue breakdown
  - month-to-month comparison
- Gemini-based intent extraction with a strict allow-list
- deterministic fallback intent detection if the AI call fails
- FastAPI backend with JSON API endpoints
- HTML/CSS/JavaScript dashboard served by the same app
- automated pytest coverage for core analytics and API behavior

## Technology stack

- Python 3
- FastAPI
- Uvicorn
- SQLite
- Google Gen AI SDK (`google-genai`)
- HTML, CSS, JavaScript
- pytest

## Project folder structure

```text
ai-bi-assistant/
├── .gitignore
├── .pytest_cache/
├── .venv/
├── README.md
├── ARCHITECTURE.md
├── AI_DEVELOPMENT_NOTES.md
├── requirements.txt
├── backend/
│   ├── __init__.py
│   ├── ai_service.py
│   ├── analytics.py
│   ├── data_loader.py
│   ├── database.py
│   ├── main.py
│   └── models.py
├── data/
│   ├── sales_data.csv
│   └── sales_data.sqlite3
├── frontend/
│   ├── app.js
│   ├── index.html
│   └── style.css
└── tests/
    ├── test_ai_integration.py
    └── test_phase7_verification.py
```

## Setup and installation for Ubuntu

From the project root:

```bash
cd "/home/user/RSG/JD and Assessment for GETs/ai-bi-assistant"
python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

The project includes a local virtual environment in `.venv/` and a `requirements.txt` file with the runtime dependencies.

## Activate the virtual environment

```bash
cd "/home/user/RSG/JD and Assessment for GETs/ai-bi-assistant"
. .venv/bin/activate
```

## Configure the Gemini API key

The backend reads the Gemini API key from either:

- the environment variable `GEMINI_API_KEY`, or
- the existing file `/home/user/RSG/JD and Assessment for GETs/rsg.txt`

The application is designed to read the key from the existing assignment folder and does not require it to be embedded in source code.

Example:

```bash
export GEMINI_API_KEY="your-key-here"
```

If no environment variable is set, the project attempts to read the existing `rsg.txt` file.

## Start the FastAPI server

From the project root with the virtual environment active:

```bash
cd "/home/user/RSG/JD and Assessment for GETs/ai-bi-assistant"
. .venv/bin/activate
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

Then open the app in a browser at:

```text
http://127.0.0.1:8000/
```

## Open and use the dashboard

The dashboard is a simple sales analytics interface served by FastAPI.

Steps:

1. Open `http://127.0.0.1:8000/`
2. Type a question such as:
   - What is the total revenue?
   - Which product generated the highest revenue?
   - What is the monthly revenue trend?
   - Which region generated the highest sales?
   - Compare March and April.
3. Submit the question.
4. Review the answer, supporting figures, and methodology.

The frontend calls the API at `/api/ask` and renders the results using the JSON returned by the backend.

## API endpoints

### `GET /health`
Returns a basic health status object.

Example response:

```json
{"status": "ok", "service": "ai-bi-assistant"}
```

### `GET /api/summary`
Returns summary counts for the imported data set.

Example fields:

- `total_records`
- `accepted_for_revenue`
- `excluded_from_revenue`
- `validation_issues`

### `POST /api/ask`
Accepts:

```json
{"question": "What is the total revenue?"}
```

Returns:

- `question`
- `intent`
- `answer`
- `data`
- `supporting_figures`
- `methodology`
- `success`
- `warning`

## Database schema and import process

The project creates a SQLite database at `data/sales_data.sqlite3`.

### Tables

#### `transactions`
Stores each imported sales record and its calculated eligibility status.

Key fields:

- `transaction_id`
- `order_date`
- `product`
- `category`
- `region`
- `sales_channel`
- `quantity`
- `unit_price`
- `discount_amount`
- `status`
- `is_eligible_for_revenue`
- `exclusion_reason`
- `raw_row_json`
- `imported_at`

#### `validation_issues`
Logs problems found during validation, such as invalid dates, zero quantities, or invalid pricing.

#### `import_runs`
Tracks metadata for each import event, including row counts and accepted/excluded totals.

### Import flow

1. The source CSV is read from the assignment folder.
2. A project-local copy is stored in `data/sales_data.csv`.
3. Required columns are validated.
4. Every row is normalized and checked for invalid values.
5. Problems are recorded in `validation_issues`.
6. Eligible completed orders remain revenue-eligible.
7. The import summary is saved to the database.

## Five analytics questions implemented

The application supports the following controlled business questions:

1. Total revenue
   - Calculates net revenue from all valid `Completed` orders.
   - Query formula: `(quantity * unit_price) - discount_amount`

2. Highest-revenue product
   - Determines the top product by total eligible revenue.

3. Monthly revenue trend
   - Summarizes revenue month by month across the dataset.

4. Highest-revenue region
   - Identifies the region with the largest revenue contribution.

5. Month-over-month comparison
   - Compares two months and calculates the absolute difference and percentage change.

The actual calculations are performed through SQLite queries in `backend/analytics.py`.

## Data-quality handling and revenue calculation

The project includes explicit validation rules for incomplete or invalid rows:

- `Returned` orders are excluded from revenue.
- zero quantity rows are excluded
- missing or invalid `Unit_price` rows are excluded
- rows with missing or invalid required values are logged as validation issues
- data is retained in the database for traceability and auditing

Revenue is calculated as:

```text
net revenue = (Quantity × Unit_price) − Discount_amount
```

Only `Completed` rows with valid values and a positive quantity and unit price are counted toward revenue.

## How to run automated tests

With the virtual environment active:

```bash
cd "/home/user/RSG/JD and Assessment for GETs/ai-bi-assistant"
. .venv/bin/activate
pytest -q
```

The project currently includes automated tests for:

- revenue calculations
- top product and region analytics
- monthly trend analysis
- month comparison logic
- invalid questions and edge cases
- API validation behavior
- Gemini failure handling

## Known limitations and assumptions

- The project is designed for the provided dataset and is not a general-purpose ERP analytics engine.
- Only the supported five intents are available for natural-language question handling.
- Gemini is treated as an intent classifier, not as a calculator or SQL executor.
- The app does not generate or execute arbitrary SQL from user input.
- The source CSV and assignment document remain in the parent project folder and are not modified.
- The application assumes the dataset fields and revenue logic match the implementation described in this project.

## Notes on security

- The API key is not stored in application source code.
- It is read from `rsg.txt` or an environment variable.
- The project avoids exposing the key in logs, API responses, or repository files.
- The AI layer validates JSON responses and only accepts an allow-listed set of intents.

## Final note

This project demonstrates a working AI-assisted sales analytics application that is deterministic, auditable, and safe. Its business insight logic is grounded in SQLite and validated Python code rather than opportunistic model output.
