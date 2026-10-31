import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "data" / "sales_data.sqlite3"


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id TEXT PRIMARY KEY,
                order_date TEXT NOT NULL,
                product TEXT NOT NULL,
                category TEXT NOT NULL,
                region TEXT NOT NULL,
                sales_channel TEXT NOT NULL,
                quantity INTEGER,
                unit_price REAL,
                discount_amount REAL,
                status TEXT NOT NULL,
                is_eligible_for_revenue INTEGER NOT NULL DEFAULT 0,
                exclusion_reason TEXT,
                raw_row_json TEXT,
                imported_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS validation_issues (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_id TEXT,
                issue_code TEXT NOT NULL,
                issue_detail TEXT NOT NULL,
                severity TEXT NOT NULL DEFAULT 'warning',
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS import_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_file TEXT NOT NULL,
                imported_at TEXT NOT NULL,
                total_rows INTEGER NOT NULL,
                imported_records INTEGER NOT NULL,
                accepted_for_revenue INTEGER NOT NULL,
                excluded_for_revenue INTEGER NOT NULL,
                duplicate_rows INTEGER NOT NULL,
                notes TEXT
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def get_summary() -> dict:
    conn = get_connection()
    try:
        total = conn.execute("SELECT COUNT(*) AS c FROM transactions").fetchone()["c"]
        accepted = conn.execute(
            "SELECT COUNT(*) AS c FROM transactions WHERE is_eligible_for_revenue = 1 AND status = 'Completed'"
        ).fetchone()["c"]
        excluded = conn.execute(
            "SELECT COUNT(*) AS c FROM transactions WHERE is_eligible_for_revenue = 0"
        ).fetchone()["c"]
        issues = conn.execute("SELECT COUNT(*) AS c FROM validation_issues").fetchone()["c"]
        return {
            "total_records": total,
            "accepted_for_revenue": accepted,
            "excluded_from_revenue": excluded,
            "validation_issues": issues,
        }
    finally:
        conn.close()


def save_import_summary(source_file: str, total_rows: int, imported_records: int, accepted_for_revenue: int, excluded_for_revenue: int, duplicate_rows: int, notes: str) -> None:
    conn = get_connection()
    try:
        conn.execute(
            """
            INSERT INTO import_runs (source_file, imported_at, total_rows, imported_records, accepted_for_revenue, excluded_for_revenue, duplicate_rows, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                source_file,
                datetime.now(timezone.utc).isoformat(),
                total_rows,
                imported_records,
                accepted_for_revenue,
                excluded_for_revenue,
                duplicate_rows,
                notes,
            ),
        )
        conn.commit()
    finally:
        conn.close()


def insert_validation_issue(transaction_id: str | None, issue_code: str, issue_detail: str, severity: str = "warning") -> None:
    conn = get_connection()
    try:
        conn.execute(
            """
            INSERT INTO validation_issues (transaction_id, issue_code, issue_detail, severity, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                transaction_id,
                issue_code,
                issue_detail,
                severity,
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        conn.commit()
    finally:
        conn.close()


def upsert_transaction(raw: dict) -> None:
    conn = get_connection()
    try:
        conn.execute(
            """
            INSERT INTO transactions (
                transaction_id, order_date, product, category, region, sales_channel,
                quantity, unit_price, discount_amount, status,
                is_eligible_for_revenue, exclusion_reason, raw_row_json, imported_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(transaction_id) DO NOTHING
            """,
            (
                raw["transaction_id"],
                raw["order_date"],
                raw["product"],
                raw["category"],
                raw["region"],
                raw["sales_channel"],
                raw["quantity"],
                raw["unit_price"],
                raw["discount_amount"],
                raw["status"],
                int(raw["is_eligible_for_revenue"]),
                raw.get("exclusion_reason"),
                json.dumps(raw, ensure_ascii=True),
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        conn.commit()
    finally:
        conn.close()


def reset_import_state() -> None:
    conn = get_connection()
    try:
        conn.execute("DELETE FROM transactions")
        conn.execute("DELETE FROM validation_issues")
        conn.execute("DELETE FROM import_runs")
        conn.commit()
    finally:
        conn.close()
