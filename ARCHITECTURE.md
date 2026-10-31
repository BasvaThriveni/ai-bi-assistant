# Architecture Overview

This project is a lightweight AI business-intelligence assistant for sales analytics. It reads a CSV sales dataset, validates and imports the rows into SQLite, exposes deterministic analytics through a FastAPI backend, and uses Gemini only to classify the user’s intent before running predefined SQL-backed calculations.

## 1. Overall architecture

The application follows a straightforward three-layer design:

1. Frontend layer
   - A small HTML/CSS/JavaScript dashboard served by FastAPI.
   - The user enters a natural-language sales question.
   - The browser sends the request to the backend API and renders the answer plus supporting figures.

2. Backend layer
   - FastAPI application exposes `/health`, `/api/summary`, and `/api/ask`.
   - Business logic lives in `backend/analytics.py`, `backend/database.py`, `backend/data_loader.py`, and `backend/ai_service.py`.
   - The backend performs validation, loads data, resolves intents, and executes safe analytics queries.

3. Data layer
   - SQLite database at `data/sales_data.sqlite3` stores raw transaction records, validation issues, and import metadata.
   - All required revenue and trend calculations are performed through SQL queries against this database.

Text-based architecture diagram:

```text
Browser UI
  |
  v
FastAPI app (backend/main.py)
  |-- /api/ask --> ai_service.ask_question()
  |-- /api/summary --> database.get_summary()
  |-- static files --> frontend/index.html, style.css, app.js
  |
  v
Intent classifier
  - Gemini JSON output (preferred)
  - fallback regex-based intent detection
  |
  v
Analytics layer
  - backend/analytics.py
  - predefined SQL queries
  |
  v
SQLite database
  - transactions
  - validation_issues
  - import_runs
```

## 2. Frontend-to-backend communication

The UI is served directly by the FastAPI app at the root path. The browser asks questions by posting JSON to `/api/ask`.

Example flow:

- User enters: "What is the total revenue?"
- Frontend sends `{"question": "What is the total revenue?"}` to the backend.
- FastAPI validates the request using the `QuestionRequest` model.
- `backend.ai_service.ask_question()` resolves the user intent.
- The analytics layer executes the matching query and sends a response containing:
  - `answer`
  - `intent`
  - `data`
  - `supporting_figures`
  - `methodology`
  - `success`

## 3. FastAPI endpoints

The application exposes the following endpoints:

- `GET /health`
  - Returns a simple status object.

- `GET /api/summary`
  - Returns counts for total rows, accepted revenue records, excluded records, and validation issues.

- `POST /api/ask`
  - Accepts a question string.
  - Uses Gemini or a safe fallback to determine the question intent.
  - Executes a safe, predefined analytics operation.
  - Returns a structured answer and supporting figures.

- `GET /`
  - Serves the dashboard page.

- `GET /style.css`
  - Serves the dashboard CSS.

- `GET /app.js`
  - Serves the frontend JavaScript.

## 4. SQLite database design

The project creates and maintains a local SQLite database in `data/sales_data.sqlite3`.

### Tables

#### `transactions`
Stores one row per source record, including:

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

This table preserves the original data while tracking whether a row should contribute to revenue.

#### `validation_issues`
Stores data-quality problems detected during CSV import, such as:

- missing transaction ID
- invalid date
- invalid quantity
- zero quantity
- missing or invalid unit price
- returned order

#### `import_runs`
Records import metadata such as:

- source CSV path
- total row count
- imported records
- accepted-for-revenue count
- excluded count
- duplicate rows
- import notes

## 5. CSV import and validation flow

The CSV import is implemented in `backend/data_loader.py`.

Flow:

1. The application ensures the local `data/sales_data.csv` copy exists.
2. It validates the required columns.
3. Each row is normalized and checked for missing or invalid values.
4. Validation issues are written to `validation_issues`.
5. Rows are marked as eligible or excluded from revenue.
6. Excluded records are still preserved in the database for traceability.
7. Import summary is saved to `import_runs`.

Important rules enforced:

- `Returned` transactions are excluded.
- `Quantity` must be present and non-zero.
- `Unit_price` must be present and greater than zero.
- `Completed` orders with valid data are revenue-eligible.
- Original rows remain in the database and are not deleted.

## 6. Gemini integration

The Gemini layer is intentionally narrow and safe. It is used only to classify the user’s business question into one of a fixed set of supported intents:

- `total_revenue`
- `product_revenue`
- `monthly_trend`
- `region_revenue`
- `monthly_comparison`

The project reads the API key from the existing `rsg.txt` file in the parent assignment folder or from the environment variable `GEMINI_API_KEY`.

The code does not send raw SQL or arbitrary user input as executable SQL. Instead, it sends a constrained prompt and validates the JSON response. The actual calculations are performed by Python and SQLite.

## 7. Natural-language question processing

`ask_question()` in `backend/ai_service.py` follows this flow:

1. Reject empty or invalid input.
2. Try Gemini-based intent extraction.
3. If Gemini is unavailable or returns invalid output, fall back to `detect_intent_from_question()`.
4. Validate that the intent is allow-listed.
5. Call `execute_intent()`.
6. Query the database with a predefined SQL operation.
7. Format the answer and supporting figures.
8. Return the result to the dashboard.

This design prevents the model from becoming the source of business truth.

## 8. How analytics results reach the frontend

The analytics layer implements the following calculations:

- `get_total_revenue()`
- `get_product_revenue_breakdown()`
- `get_top_product()`
- `get_monthly_revenue()`
- `get_region_revenue()`
- `get_top_region()`
- `get_month_comparison()`

These functions return Python dictionaries that are serialized to JSON by FastAPI. The frontend renders the answer text, support cards, and the monthly bar chart from those values.

## 9. Workflow summary

A typical request follows this sequence:

1. User enters a question in the browser.
2. Browser posts JSON to `/api/ask`.
3. FastAPI validates the request.
4. The AI service determines intent.
5. The analytics layer calculates the answer using SQLite.
6. A human-readable result is composed.
7. Supporting figures are returned to the UI.
8. The dashboard renders the final output.

This keeps the system explainable, deterministic, and verifiable.
