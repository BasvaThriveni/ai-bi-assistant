from __future__ import annotations

import re
from calendar import month_name
from typing import Any

from backend.database import get_connection

ALLOWED_INTENTS = {
    "total_revenue",
    "product_revenue",
    "monthly_trend",
    "region_revenue",
    "monthly_comparison",
}

MONTHS = {name.lower(): idx for idx, name in enumerate(month_name) if idx > 0}


def _safe_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def get_total_revenue() -> dict:
    conn = get_connection()
    try:
        row = conn.execute(
            """
            SELECT
                COUNT(*) AS eligible_transactions,
                ROUND(COALESCE(SUM((quantity * unit_price) - discount_amount), 0), 2) AS total_revenue
            FROM transactions
            WHERE status = 'Completed' AND is_eligible_for_revenue = 1
            """
        ).fetchone()
        return {
            "total_revenue": _safe_float(row["total_revenue"]),
            "eligible_transactions": int(row["eligible_transactions"] or 0),
        }
    finally:
        conn.close()


def get_product_revenue_breakdown() -> dict:
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT
                product,
                ROUND(COALESCE(SUM((quantity * unit_price) - discount_amount), 0), 2) AS revenue,
                COUNT(*) AS transaction_count
            FROM transactions
            WHERE status = 'Completed' AND is_eligible_for_revenue = 1
            GROUP BY product
            ORDER BY revenue DESC, product ASC
            LIMIT 5
            """
        ).fetchall()
        return {
            "rows": [
                {
                    "product": r["product"],
                    "revenue": _safe_float(r["revenue"]),
                    "transaction_count": int(r["transaction_count"] or 0),
                }
                for r in rows
            ]
        }
    finally:
        conn.close()


def get_top_product() -> dict:
    breakdown = get_product_revenue_breakdown()["rows"]
    if not breakdown:
        return {"product": None, "revenue": 0.0, "rankings": []}
    top = breakdown[0]
    ranked = [
        {"rank": idx + 1, "product": item["product"], "revenue": item["revenue"]}
        for idx, item in enumerate(breakdown)
    ]
    return {
        "product": top["product"],
        "revenue": top["revenue"],
        "rankings": ranked,
        "breakdown": breakdown,
    }


def get_monthly_revenue() -> dict:
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT
                strftime('%Y-%m', order_date) AS month_key,
                COUNT(*) AS transaction_count,
                ROUND(COALESCE(SUM((quantity * unit_price) - discount_amount), 0), 2) AS revenue
            FROM transactions
            WHERE status = 'Completed' AND is_eligible_for_revenue = 1
            GROUP BY strftime('%Y-%m', order_date)
            ORDER BY month_key ASC
            """
        ).fetchall()
        formatted = []
        for r in rows:
            month_key = str(r["month_key"])
            year, month_num = month_key.split('-')
            month_name_value = month_name[int(month_num)]
            formatted.append(
                {
                    "month": f"{month_name_value} {year}",
                    "month_key": month_key,
                    "transaction_count": int(r["transaction_count"] or 0),
                    "revenue": _safe_float(r["revenue"]),
                }
            )
        return {"rows": formatted}
    finally:
        conn.close()


def get_region_revenue() -> dict:
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT
                region,
                ROUND(COALESCE(SUM((quantity * unit_price) - discount_amount), 0), 2) AS revenue,
                COUNT(*) AS transaction_count,
                COALESCE(SUM(quantity), 0) AS units_sold
            FROM transactions
            WHERE status = 'Completed' AND is_eligible_for_revenue = 1
            GROUP BY region
            ORDER BY revenue DESC, region ASC
            """
        ).fetchall()
        return {
            "rows": [
                {
                    "region": r["region"],
                    "revenue": _safe_float(r["revenue"]),
                    "transaction_count": int(r["transaction_count"] or 0),
                    "units_sold": int(r["units_sold"] or 0),
                }
                for r in rows
            ]
        }
    finally:
        conn.close()


def get_top_region() -> dict:
    rows = get_region_revenue()["rows"]
    if not rows:
        return {"region": None, "revenue": 0.0, "rows": []}
    top = rows[0]
    return {"region": top["region"], "revenue": top["revenue"], "rows": rows}


def _month_key(month_name_value: str, year: int) -> str:
    month_name_value = (month_name_value or '').strip()
    month_index = MONTHS.get(month_name_value.lower())
    if month_index is None:
        raise ValueError(f"Unsupported month: {month_name_value}")
    return f"{year}-{month_index:02d}"


def get_month_comparison(month1: str, month2: str, year: int = 2026) -> dict:
    month1_key = _month_key(month1, year)
    month2_key = _month_key(month2, year)

    conn = get_connection()
    try:
        first = conn.execute(
            """
            SELECT
                ROUND(COALESCE(SUM((quantity * unit_price) - discount_amount), 0), 2) AS revenue,
                COUNT(*) AS transaction_count
            FROM transactions
            WHERE status = 'Completed'
              AND is_eligible_for_revenue = 1
              AND strftime('%Y-%m', order_date) = ?
            """,
            (month1_key,),
        ).fetchone()
        second = conn.execute(
            """
            SELECT
                ROUND(COALESCE(SUM((quantity * unit_price) - discount_amount), 0), 2) AS revenue,
                COUNT(*) AS transaction_count
            FROM transactions
            WHERE status = 'Completed'
              AND is_eligible_for_revenue = 1
              AND strftime('%Y-%m', order_date) = ?
            """,
            (month2_key,),
        ).fetchone()

        first_revenue = _safe_float(first["revenue"])
        second_revenue = _safe_float(second["revenue"])
        absolute_diff = second_revenue - first_revenue

        if abs(first_revenue) < 1e-9:
            percentage_change = 0.0 if abs(second_revenue) < 1e-9 else 100.0
        else:
            percentage_change = ((second_revenue - first_revenue) / first_revenue) * 100

        if absolute_diff > 0:
            direction = "increased"
        elif absolute_diff < 0:
            direction = "decreased"
        else:
            direction = "remained unchanged"

        return {
            "month1": month1.title(),
            "month2": month2.title(),
            "year": year,
            "month1_revenue": first_revenue,
            "month2_revenue": second_revenue,
            "absolute_difference": absolute_diff,
            "percentage_change": percentage_change,
            "direction": direction,
        }
    finally:
        conn.close()


def detect_intent_from_question(question: str) -> dict:
    q = (question or '').strip().lower()
    if not q:
        raise ValueError("Question is empty.")

    if any(term in q for term in ["total revenue", "overall sales", "how much revenue", "show me overall sales"]):
        return {"intent": "total_revenue", "parameters": {}}

    if any(term in q for term in ["highest revenue", "best-performing product", "best product", "rank products", "which product generated"]):
        return {"intent": "product_revenue", "parameters": {}}

    if any(term in q for term in ["monthly revenue", "monthly sales trend", "revenue trend", "over the months", "monthly trend", "show monthly"]):
        return {"intent": "monthly_trend", "parameters": {}}

    if any(term in q for term in ["region generated the highest", "highest sales", "best region", "regional revenue", "which region"]):
        return {"intent": "region_revenue", "parameters": {}}

    if any(term in q for term in ["compare", "between", "change between", "increased or decreased", "did revenue increase"]) and re.search(r"(january|february|march|april|may|june)", q):
        months = re.findall(r"(january|february|march|april|may|june)", q)
        if len(months) >= 2:
            return {"intent": "monthly_comparison", "parameters": {"month1": months[0].title(), "month2": months[1].title(), "year": 2026}}

    raise ValueError("Unsupported or irrelevant question.")


def execute_intent(intent: str, parameters: dict | None = None) -> dict:
    params = parameters or {}
    if intent not in ALLOWED_INTENTS:
        raise ValueError(f"Unsupported intent: {intent}")

    if intent == "total_revenue":
        return {"answer": "Total revenue", "data": get_total_revenue()}

    if intent == "product_revenue":
        return {"answer": "Highest revenue product", "data": get_top_product()}

    if intent == "monthly_trend":
        return {"answer": "Monthly revenue trend", "data": get_monthly_revenue()}

    if intent == "region_revenue":
        return {"answer": "Highest revenue region", "data": get_top_region()}

    if intent == "monthly_comparison":
        month1 = str(params.get("month1", "")).strip()
        month2 = str(params.get("month2", "")).strip()
        year = int(params.get("year", 2026))
        return {"answer": "Monthly comparison", "data": get_month_comparison(month1, month2, year)}

    raise ValueError(f"Execution not implemented for intent: {intent}")
