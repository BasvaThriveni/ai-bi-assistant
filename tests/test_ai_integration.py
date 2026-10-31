import pytest
from fastapi.testclient import TestClient

from backend.ai_service import ask_question, extract_intent_from_ai, UnsupportedQuestionError
from backend.analytics import detect_intent_from_question, get_total_revenue, get_top_product, get_monthly_revenue, get_region_revenue, get_month_comparison
from backend.main import app

client = TestClient(app)


def test_total_revenue_calculation():
    result = get_total_revenue()
    assert result["total_revenue"] == 1439200.0
    assert result["eligible_transactions"] == 48


def test_top_product_calculation():
    result = get_top_product()
    assert result["product"] == "Monitor"
    assert result["revenue"] == 473000.0
    assert len(result["rankings"]) >= 1


def test_monthly_trend_calculation():
    result = get_monthly_revenue()["rows"]
    months = {item["month_key"]: item["revenue"] for item in result}
    assert months["2026-01"] == 210250.0
    assert months["2026-02"] == 234600.0
    assert months["2026-03"] == 223900.0
    assert months["2026-04"] == 240700.0
    assert months["2026-05"] == 318500.0
    assert months["2026-06"] == 211250.0


def test_region_revenue_calculation():
    result = get_region_revenue()["rows"]
    region_map = {item["region"]: item["revenue"] for item in result}
    assert region_map["South"] == 411200.0
    assert region_map["North"] == 384450.0


def test_month_comparison_calculation():
    result = get_month_comparison("March", "April", 2026)
    assert result["month1_revenue"] == 223900.0
    assert result["month2_revenue"] == 240700.0
    assert result["absolute_difference"] == 16800.0
    assert round(result["percentage_change"], 4) == 7.5033
    assert result["direction"] == "increased"


def test_detect_intent_rejects_sql_injection(monkeypatch):
    with pytest.raises(ValueError):
        detect_intent_from_question("DROP TABLE transactions;")


def test_gemini_json_validation(monkeypatch):
    class FakeClient:
        class models:
            @staticmethod
            def generate_content(model, contents, config=None):
                class Response:
                    text = '{"intent":"monthly_comparison","parameters":{"month1":"January","month2":"February","year":2026}}'
                return Response()

    monkeypatch.setattr("backend.ai_service.genai.Client", lambda api_key: FakeClient())
    result = extract_intent_from_ai("Compare January and February")
    assert result["intent"] == "monthly_comparison"
    assert result["parameters"]["month1"] == "January"


def test_ask_question_uses_ai_result(monkeypatch):
    monkeypatch.setattr(
        "backend.ai_service.extract_intent_from_ai",
        lambda question: {"intent": "total_revenue", "parameters": {}},
    )
    result = ask_question("What is the total revenue?")
    assert result["success"] is True
    assert result["intent"] == "total_revenue"
    assert result["data"]["total_revenue"] == 1439200.0


def test_api_unsupported_question(monkeypatch):
    monkeypatch.setattr("backend.ai_service.extract_intent_from_ai", lambda question: (_ for _ in ()).throw(RuntimeError("quota limit")))
    monkeypatch.setattr("backend.analytics.detect_intent_from_question", lambda question: (_ for _ in ()).throw(ValueError("Unsupported or irrelevant question.")))

    response = client.post("/api/ask", json={"question": "Delete all records"})
    assert response.status_code == 400
    assert "Unsupported or irrelevant question" in response.json()["detail"]


def test_api_question_success(monkeypatch):
    monkeypatch.setattr(
        "backend.ai_service.extract_intent_from_ai",
        lambda question: {"intent": "product_revenue", "parameters": {}},
    )
    response = client.post("/api/ask", json={"question": "Which product generated the highest revenue?"})
    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "product_revenue"
    assert body["data"]["product"] == "Monitor"
