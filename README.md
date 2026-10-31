# AI Business Intelligence Assistant

<p align="center">
  <strong>AI-powered natural-language sales analytics using Python, FastAPI, SQLite and Google Gemini</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/SQLite-Database-003B57?logo=sqlite" alt="SQLite">
  <img src="https://img.shields.io/badge/Google%20Gemini-AI-4285F4?logo=google" alt="Google Gemini">
  <img src="https://img.shields.io/badge/pytest-24%20passed-brightgreen" alt="Tests">
</p>

---

## 1. Project Overview

The **AI Business Intelligence Assistant** is a lightweight business analytics application that allows users to ask questions about sales transactions in natural English and receive answers supported by actual database calculations.

Instead of manually examining spreadsheets or writing SQL queries, business users can ask questions such as:

- What is the total revenue?
- Which product generated the highest revenue?
- What is the monthly revenue trend?
- Which region generated the highest sales?
- How did revenue change between two months?

The application uses **Google Gemini** to understand natural-language questions. Python validates the identified intent, and predefined SQL queries retrieve the actual figures from an SQLite database.

### Project Objective

To demonstrate how Generative AI can be integrated with traditional backend and database technologies to build a practical, reliable and explainable Business Intelligence application.

> **Core principle:** Gemini understands the question, Python validates the request, SQLite performs the calculations, and the frontend presents the results.

---

## 2. Key Features

| Feature | Description |
|---|---|
| Natural-language questions | Ask business questions using everyday English. |
| AI intent detection | Uses Gemini to identify the analytical intent. |
| CSV data import | Imports the supplied sales transaction dataset. |
| Data validation | Identifies missing and invalid transaction values. |
| SQLite database | Stores transaction records and validation information. |
| Total revenue analysis | Calculates total net revenue. |
| Product performance | Identifies and ranks products by revenue. |
| Monthly revenue trend | Displays revenue changes across months. |
| Regional performance | Compares revenue across regions. |
| Month comparison | Calculates absolute and percentage revenue changes. |
| Interactive dashboard | Displays answers and supporting figures. |
| Automated testing | Verifies application functionality using pytest. |

### Supported Business Questions

1. What is the total revenue?
2. Which product generated the highest revenue?
3. What is the monthly revenue trend?
4. Which region generated the highest sales?
5. How did revenue change between two months?

---

## 3. Technology Stack

| Component | Technology | Purpose |
|---|---|---|
| Programming language | Python | Application logic and calculations |
| Backend framework | FastAPI | REST API development |
| Application server | Uvicorn | Runs the backend application |
| Database | SQLite | Stores and retrieves sales transactions |
| AI model | Google Gemini | Understands natural-language questions |
| AI SDK | google-genai | Connects Python with Gemini |
| Frontend | HTML | Dashboard structure |
| Styling | CSS | User interface design |
| Client-side logic | JavaScript | Frontend and API communication |
| Testing | pytest | Automated testing |
| API testing | FastAPI TestClient | Tests backend endpoints |

---

## 4. Project Structure

```text
ai-bi-assistant/
│
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── analytics.py
│   ├── ai_service.py
│   └── data_loader.py
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
│
├── data/
│   └── sales_data.csv
│
├── tests/
│   ├── test_ai_integration.py
│   └── test_phase7_verification.py
│
├── .gitignore
├── requirements.txt
├── README.md
├── ARCHITECTURE.md
└── AI_DEVELOPMENT_NOTES.md
```

### Important Files

| File | Responsibility |
|---|---|
| `main.py` | Defines the FastAPI application and API endpoints. |
| `database.py` | Creates SQLite tables and handles database operations. |
| `models.py` | Defines request and response data models. |
| `analytics.py` | Implements predefined SQL-based analytical operations. |
| `ai_service.py` | Handles Gemini integration and intent identification. |
| `data_loader.py` | Imports and validates the sales CSV dataset. |
| `index.html` | Defines the dashboard structure. |
| `style.css` | Provides dashboard styling. |
| `app.js` | Handles user interactions and API communication. |

The SQLite database is generated locally when the application initializes. It is not required to be committed to GitHub because it can be recreated from the supplied CSV file.

---

## 5. Installation and Setup

### Prerequisites

Install the following:

- Python 3.10 or later
- pip
- Git

### Step 1: Clone the Repository

```bash
git clone https://github.com/BasvaThriveni/ai-bi-assistant.git
```

### Step 2: Navigate to the Project Directory

```bash
cd ai-bi-assistant
```

### Step 3: Create a Virtual Environment

```bash
python3 -m venv .venv
```

### Step 4: Activate the Virtual Environment

**Linux/macOS:**

```bash
source .venv/bin/activate
```

**Windows PowerShell:**

```powershell
.venv\Scripts\Activate.ps1
```

### Step 5: Install Dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

The required Python packages are listed in `requirements.txt`.

---

## 6. Gemini API Configuration

The application integrates Google Gemini through the official `google-genai` Python SDK.

A valid Gemini API key is required for live AI-based question interpretation.

### Configure the API Key

The backend supports reading the API key from the `GEMINI_API_KEY` environment variable.

**Linux/macOS:**

```bash
export GEMINI_API_KEY="your-gemini-api-key"
```

**Windows PowerShell:**

```powershell
$env:GEMINI_API_KEY="your-gemini-api-key"
```

Replace the placeholder with your own Gemini API key.

### Security Practices

- API keys are not hardcoded into application source files.
- API keys are not included in the GitHub repository.
- The application reads the key from local configuration or an environment variable.
- Missing or invalid API-key errors are handled without exposing sensitive information.
- API errors and quota limitations are handled by the backend.

**Note:** Gemini model availability, free-tier access and request quotas depend on Google's current API policies and account limits.

---

## 7. Database Design and CSV Import

The application uses **SQLite** as its database.

The supplied sales dataset is included in:

```text
data/sales_data.csv
```

The database is generated locally at:

```text
data/sales_data.sqlite3
```

### Automatic Database Initialization

When the application starts:

1. The required database tables are initialized.
2. The application checks whether transaction records already exist.
3. If the database is empty, the supplied CSV is imported.
4. Transaction values are validated.
5. Records and validation information are stored in SQLite.

### Manual CSV Import

To manually import the dataset or initialize the database before running tests, execute:

```bash
python -m backend.data_loader
```

### Database Tables

**1. transactions**

Stores the imported transaction records, including:

- Transaction ID
- Order date
- Product
- Category
- Region
- Sales channel
- Quantity
- Unit price
- Discount amount
- Transaction status
- Revenue eligibility
- Exclusion reason
- Original row information

**2. validation_issues**

Stores data-quality issues identified during CSV import.

**3. import_runs**

Stores import information, including record counts and accepted or excluded transaction totals.

---

## 8. Data Cleaning and Revenue Calculation

The supplied dataset contains **51 sales transactions** from January to June 2026.

### Identified Data-Quality Issues

| Transaction ID | Issue | Treatment |
|---|---|---|
| TXN0051 | Missing unit price | Excluded from revenue |
| TXN0034 | Zero quantity | Excluded from revenue |
| TXN0033 | Returned transaction | Excluded from revenue |

### Data Validation Rules

- Original transaction information is preserved.
- Missing and invalid values are tracked.
- Returned transactions are excluded from completed-sales revenue.
- Transactions with missing or invalid unit prices are excluded.
- Zero-quantity transactions are excluded.
- Duplicate transaction IDs are prevented.
- Validation issues and exclusion reasons are recorded.

### Revenue Calculation Formula

Net transaction revenue is calculated using:

$$
\text{Net Revenue}
=
(\text{Quantity} \times \text{Unit Price})
-
\text{Discount Amount}
$$

**Important assumption:** The discount amount is treated as a transaction-level discount, not a per-unit discount.

Only completed transactions with valid data are included in revenue calculations.

### Data Import Summary

| Metric | Result |
|---|---:|
| Total transactions | 51 |
| Accepted for revenue | 48 |
| Excluded from revenue | 3 |
| Validation issues | 3 |

---

## 9. Analytics Implemented

The application supports five predefined analytical operations.

### 9.1 Total Revenue

Calculates the total net revenue generated from eligible completed transactions.

**Formula:**

**Formula:**

`Total Net Revenue = SUM(Net Transaction Revenue)`

Displays:

- Total net revenue.
- Number of eligible transactions.
- Supporting figures.

### 9.2 Highest-Revenue Product

Identifies the product that generated the highest net revenue.

Displays:

- Highest-revenue product.
- Its total revenue.
- Product-wise revenue breakdown.
- Revenue ranking.

### 9.3 Monthly Revenue Trend

Calculates revenue for each month.

Displays:

- Month.
- Total monthly revenue.
- Transaction counts.
- Monthly revenue chart.

Months are displayed chronologically.

### 9.4 Highest-Revenue Region

Compares revenue generated across different regions.

Displays:

- Highest-performing region.
- Revenue by region.
- Transaction counts.
- Units sold.

Sales performance is interpreted using net revenue.

### 9.5 Month-to-Month Comparison

Compares revenue between two selected months.

**Absolute Difference:**

**Difference:**

`Revenue Difference = Revenue in Month 2 − Revenue in Month 1`

**Percentage Change:**

**Percentage Change:**

`Percentage Change = ((Revenue in Month 2 − Revenue in Month 1) / Revenue in Month 1) × 100`

The result indicates whether revenue increased, decreased or remained unchanged.

Zero-revenue comparison periods are handled without division-by-zero errors.

---

## 10. AI Integration and Request Workflow

Google Gemini is used for natural-language understanding.

It identifies what type of analytical question the user is asking. It does not directly calculate revenue or execute SQL queries.

### Request-to-Response Workflow

```text
          User enters a question
                    |
                    v
          Frontend (JavaScript)
                    |
                    v
              FastAPI Backend
                    |
                    v
          Gemini Intent Detection
                    |
                    v
          Structured JSON Response
                    |
                    v
        Intent and Parameter Validation
                    |
                    v
        Predefined SQL Query Selection
                    |
                    v
              SQLite Database
                    |
                    v
        Actual Analytical Calculations
                    |
                    v
          Business Answer Preparation
                    |
                    v
             Frontend Dashboard
```

### Example

**User Question:**

```text
Which product generated the highest revenue?
```

Gemini identifies the analytical intent and returns structured JSON:

```json
{
  "intent": "product_revenue",
  "parameters": {}
}
```

The backend validates the response and selects the corresponding predefined SQL query.

SQLite calculates the actual product revenues.

Python prepares the result, which is displayed on the dashboard.

### Security and Accuracy

- Gemini does not generate executable SQL.
- Only predefined analytical intents are accepted.
- Parameters are validated before database queries.
- SQL queries use parameterized inputs.
- Destructive database operations are not permitted through the question-answering interface.
- Actual analytical figures come from SQLite calculations.

The application also provides deterministic fallback intent detection for supported questions when the Gemini API is unavailable.

---

## 11. Running the Application

After completing installation and API-key configuration, start the FastAPI server from the project root:

```bash
uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Open the application in your browser:

**http://127.0.0.1:8000/**

The dashboard allows users to enter business questions and view the corresponding analytical results.

---

## 12. API Endpoints

The application exposes the following endpoints.

### GET `/health`

Checks whether the backend application is running.

### GET `/api/summary`

Returns the dataset summary, including:

- Total transaction records.
- Accepted revenue records.
- Excluded records.
- Number of validation issues.

### POST `/api/ask`

Accepts natural-language business questions.

**Example Request:**

```json
{
  "question": "What is the total revenue?"
}
```

**Response Structure:**

```json
{
  "question": "What is the total revenue?",
  "intent": "total_revenue",
  "answer": "The total net revenue is calculated from eligible completed transactions.",
  "data": {},
  "supporting_figures": [],
  "methodology": "Net revenue = (Quantity × Unit Price) − Discount Amount",
  "success": true
}
```

The actual response contains the calculated figures returned by the analytical functions.

---

## 13. Running Automated Tests

The project uses **pytest** and **FastAPI TestClient**.

### Step 1: Activate the Virtual Environment

```bash
source .venv/bin/activate
```

For Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### Step 2: Initialize the Database

For a fresh clone, initialize the database and import the CSV before running the test suite:

```bash
python -m backend.data_loader
```

### Step 3: Run the Tests

```bash
pytest -q
```

### Test Coverage

The automated tests cover:

1. Total revenue calculation.
2. Highest-revenue product calculation.
3. Monthly revenue aggregation.
4. Highest-revenue region calculation.
5. Month-to-month comparison.
6. Unsupported questions.
7. Invalid input handling.
8. Missing unit-price handling.
9. Returned transaction exclusion.
10. Zero-quantity transaction handling.
11. API validation and error handling.
12. AI integration behavior.

### Verification Result

**24 tests passed** in the previously completed test run.

The automated test suite does not require live Gemini API calls.

---

## 14. Known Limitations

- The application is designed primarily for the supplied assessment dataset.
- Only five predefined analytical intents are currently supported.
- Gemini API availability and request quotas depend on the configured account.
- The application does not generate or execute arbitrary SQL.
- SQLite is used for lightweight local database storage.
- The application is intended as an assessment-scale business analytics demonstration rather than a full enterprise BI platform.

---

## 15. Security Considerations

Security measures implemented in the application include:

- API keys are not hardcoded in source files.
- Sensitive configuration files are excluded through `.gitignore`.
- SQL queries use parameterized inputs.
- AI-generated intents are validated against an allow-list.
- Arbitrary SQL execution is not permitted.
- Database modification is restricted to the controlled data-import process.
- Internal errors and sensitive information are not intentionally exposed through API responses.

---

## 16. Additional Documentation

| Document | Description |
|---|---|
| `ARCHITECTURE.md` | Explains the application architecture and request-to-response workflow. |
| `AI_DEVELOPMENT_NOTES.md` | Documents AI-assisted development, implementation challenges and possible improvements. |

---

## 17. Conclusion

The AI Business Intelligence Assistant demonstrates how Generative AI can be integrated with Python, FastAPI and SQLite to create a practical business analytics application.

By separating AI-based question understanding from deterministic database calculations, the application provides a controlled, explainable and reliable approach to natural-language business intelligence.

**The primary objective is simple: allow users to ask business questions naturally and receive answers supported by actual database calculations.**

---

<p align="center">
  <strong>Developed as part of the RSG Engineering Recruitment Assessment.</strong>
</p>