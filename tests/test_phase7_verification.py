import pytest
from fastapi.testclient import TestClient

from backend.ai_service import ask_question
from backend.analytics import (
    detect_intent_from_question,
    get_month_comparison,
    get_monthly_revenue,
    get_product_revenue_breakdown,
    get_region_revenue,
    get_total_revenue,
    get_top_product,
)
from backend.main import app

client = TestClient(app)


def test_total_revenue_value():
    result = get_total_revenue()
    assert result["total_revenue"] == 1439200.0
    assert result["eligible_transactions"] == 48


def test_top_five_products():
    rows = get_product_revenue_breakdown()["rows"]
    assert len(rows) == 5
    assert [item["product"] for item in rows] == [
        "Monitor",
        "Desk",
        "Office Chair",
        "USB-C Hub",
        "Wireless Mouse",
    ]
    assert rows[0]["revenue"] == 473000.0


def test_monthly_revenue_values():
    rows = get_monthly_revenue()["rows"]
    month_map = {item["month_key"]: item["revenue"] for item in rows}
    assert month_map["2026-01"] == 210250.0
    assert month_map["2026-02"] == 234600.0
    assert month_map["2026-03"] == 223900.0
    assert month_map["2026-04"] == 240700.0
    assert month_map["2026-05"] == 318500.0
    assert month_map["2026-06"] == 211250.0


def test_region_revenue_values():
    rows = get_region_revenue()["rows"]
    region_map = {item["region"]: item["revenue"] for item in rows}
    assert region_map["South"] == 411200.0
    assert region_map["North"] == 384450.0
    assert region_map["East"] == 346700.0
    assert region_map["West"] == 296850.0


def test_month_comparison_values():
    result = get_month_comparison("March", "April", 2026)
    assert result["month1_revenue"] == 223900.0
    assert result["month2_revenue"] == 240700.0
    assert result["absolute_difference"] == 16800.0
    assert round(result["percentage_change"], 2) == 7.5
    assert result["direction"] == "increased"


def test_empty_question_rejected():
    with pytest.raises(ValueError):
        ask_question("   ")


def test_unsupported_question_rejected():
    with pytest.raises(ValueError):
        detect_intent_from_question("Delete all rows from database")


def test_returned_transaction_excluded():
    from backend.database import get_connection
    conn = get_connection()
    row = conn.execute("SELECT is_eligible_for_revenue, exclusion_reason FROM transactions WHERE transaction_id = 'TXN0033'").fetchone()
    conn.close()
    assert row[0] == 0
    assert "Returned" in (row[1] or "")


def test_zero_quantity_transaction_excluded():
    from backend.database import get_connection
    conn = get_connection()
    row = conn.execute("SELECT is_eligible_for_revenue, exclusion_reason FROM transactions WHERE transaction_id = 'TXN0034'").fetchone()
    conn.close()
    assert row[0] == 0
    assert "Zero quantity" in (row[1] or "")


def test_missing_unit_price_transaction_excluded():
    from backend.database import get_connection
    conn = get_connection()
    row = conn.execute("SELECT is_eligible_for_revenue, exclusion_reason FROM transactions WHERE transaction_id = 'TXN0051'").fetchone()
    conn.close()
    assert row[0] == 0
    assert "unit price" in (row[1] or "")


def test_api_empty_question_returns_400():
    response = client.post("/api/ask", json={"question": "   "})
    assert response.status_code == 400


def test_api_unsupported_question_returns_400():
    response = client.post("/api/ask", json={"question": "DROP TABLE transactions"})
    assert response.status_code == 400


def test_api_health_and_summary():
    health = client.get("/health")
    summary = client.get("/api/summary")
    assert health.status_code == 200
    assert summary.status_code == 200
    assert summary.json()["total_records"] == 51


def test_gemini_unavailable_service_error_handled(monkeypatch):
    import backend.ai_service as ai

    def fail(*args, **kwargs):
        raise RuntimeError("Gemini service unavailable")

    monkeypatch.setattr(ai, "extract_intent_from_ai", fail)
    with pytest.raises(RuntimeError):
        ai.extract_intent_from_ai("What is the total revenue?")
