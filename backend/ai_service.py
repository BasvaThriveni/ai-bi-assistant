import json
import os
from pathlib import Path
from typing import Any

from google import genai

from backend.analytics import ALLOWED_INTENTS, detect_intent_from_question, execute_intent

BASE_DIR = Path(__file__).resolve().parents[1]


class UnsupportedQuestionError(ValueError):
    pass


def read_api_key() -> str | None:
    env_key = os.getenv("GEMINI_API_KEY", "").strip()
    if env_key:
        return env_key

    candidate_paths = [
        Path("/home/user/RSG/JD and Assessment for GETs/rsg.txt"),
        Path("/home/user/rsg.txt"),
        BASE_DIR / "rsg.txt",
    ]
    for path in candidate_paths:
        if path.exists():
            key = path.read_text(encoding="utf-8").strip()
            if key:
                return key
    return None


def get_model_name() -> str:
    configured = os.getenv("GEMINI_MODEL", "gemini-3.5-flash").strip()
    return configured or "gemini-3.5-flash"


def _validate_ai_payload(payload: Any) -> dict:
    if not isinstance(payload, dict):
        raise ValueError("Gemini response is not a JSON object.")

    intent = str(payload.get("intent", "")).strip()
    if intent not in ALLOWED_INTENTS:
        raise ValueError(f"Unsupported intent from Gemini: {intent}")

    parameters = payload.get("parameters", {})
    if parameters is None:
        parameters = {}
    if not isinstance(parameters, dict):
        raise ValueError("Gemini parameters must be a JSON object.")

    if intent == "monthly_comparison":
        required = ["month1", "month2"]
        for key in required:
            if not str(parameters.get(key, "")).strip():
                raise ValueError(f"Missing required parameter for monthly comparison: {key}")

    return {"intent": intent, "parameters": parameters}


def extract_intent_from_ai(question: str) -> dict:
    key = read_api_key()
    if not key:
        raise RuntimeError("Gemini API key is missing or unreadable.")

    prompt = f"""
You are a safe business-intelligence intent classifier.
Return ONLY valid JSON and no markdown.
Allowed intents:
- total_revenue
- product_revenue
- monthly_trend
- region_revenue
- monthly_comparison

Rules:
- Do not generate SQL.
- Do not invent metrics.
- Only return a valid JSON object with keys: intent and parameters.
- For monthly_comparison, provide month1, month2, and year if present.

Question: {question}
JSON:
"""
    try:
        client = genai.Client(api_key=key)
        response = client.models.generate_content(
            model=get_model_name(),
            contents=prompt,
            config={"temperature": 0.1},
        )
        raw_text = (getattr(response, "text", "") or "").strip()
        if not raw_text:
            raise ValueError("Gemini returned no text.")

        candidate = raw_text
        if candidate.startswith("```"):
            candidate = candidate.strip("`")
            candidate = candidate.replace("json\n", "", 1).strip()

        parsed = json.loads(candidate)
        return _validate_ai_payload(parsed)
    except Exception as exc:
        raise RuntimeError(f"Gemini intent extraction failed: {exc}") from exc


def build_business_answer(intent: str, data: dict) -> str:
    if intent == "total_revenue":
        revenue = float(data.get("total_revenue", 0.0) or 0.0)
        transactions = int(data.get("eligible_transactions", 0) or 0)
        return (
            f"The total net revenue is {revenue:,.2f} across {transactions} eligible Completed transactions."
        )

    if intent == "product_revenue":
        product = data.get("product")
        revenue = float(data.get("revenue", 0.0) or 0.0)
        if not product:
            return "No eligible product revenue data is available."
        return f"The highest-revenue product is {product} with {revenue:,.2f} in revenue."

    if intent == "monthly_trend":
        rows = data.get("rows", [])
        if not rows:
            return "No monthly revenue data is available."
        peak = max(rows, key=lambda item: float(item.get("revenue", 0.0) or 0.0))
        return (
            f"The strongest month was {peak['month']} with {float(peak['revenue']):,.2f} in revenue."
        )

    if intent == "region_revenue":
        region = data.get("region")
        revenue = float(data.get("revenue", 0.0) or 0.0)
        if not region:
            return "No regional revenue data is available."
        return f"The highest-revenue region is {region}, generating {revenue:,.2f} in net revenue."

    if intent == "monthly_comparison":
        month1 = data.get("month1")
        month2 = data.get("month2")
        first = float(data.get("month1_revenue", 0.0) or 0.0)
        second = float(data.get("month2_revenue", 0.0) or 0.0)
        diff = float(data.get("absolute_difference", 0.0) or 0.0)
        pct = float(data.get("percentage_change", 0.0) or 0.0)
        direction = data.get("direction", "remained unchanged")
        return (
            f"Revenue {direction} from {month1} to {month2}: "
            f"{first:,.2f} to {second:,.2f}, a difference of {diff:,.2f} "
            f"({pct:,.2f}% change)."
        )

    return "The requested analysis is not available."


def ask_question(question: str) -> dict:
    if not isinstance(question, str) or not question.strip():
        raise ValueError("Question must be a non-empty string.")

    normalized_question = question.strip()

    try:
        intent_data = extract_intent_from_ai(normalized_question)
    except Exception:
        try:
            intent_data = detect_intent_from_question(normalized_question)
        except ValueError as exc:
            raise UnsupportedQuestionError(str(exc)) from exc

    intent = intent_data["intent"]
    parameters = intent_data.get("parameters", {})
    data_response = execute_intent(intent, parameters)
    answer = build_business_answer(intent, data_response["data"])

    if intent == "product_revenue":
        supporting = data_response["data"].get("breakdown", [])
    elif intent == "monthly_trend":
        supporting = data_response["data"].get("rows", [])
    elif intent == "region_revenue":
        supporting = data_response["data"].get("rows", [])
    elif intent == "total_revenue":
        supporting = [
            {
                "metric": "total_revenue",
                "value": data_response["data"].get("total_revenue", 0.0),
                "eligible_transactions": data_response["data"].get("eligible_transactions", 0),
            }
        ]
    else:
        supporting = [
            {
                "month1": data_response["data"].get("month1"),
                "month2": data_response["data"].get("month2"),
                "month1_revenue": data_response["data"].get("month1_revenue"),
                "month2_revenue": data_response["data"].get("month2_revenue"),
                "absolute_difference": data_response["data"].get("absolute_difference"),
                "percentage_change": data_response["data"].get("percentage_change"),
            }
        ]

    return {
        "question": normalized_question,
        "intent": intent,
        "answer": answer,
        "data": data_response["data"],
        "supporting_figures": supporting,
        "methodology": "Net revenue = (Quantity × Unit_price) − Discount_amount. Only Completed transactions with valid data are included.",
        "success": True,
        "warning": None,
    }
