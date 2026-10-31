from pydantic import BaseModel, Field, field_validator


class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=500)

    @field_validator("question")
    @classmethod
    def validate_question(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Question cannot be empty.")
        return cleaned


class AskResponse(BaseModel):
    question: str
    intent: str
    answer: str
    data: dict
    supporting_figures: list
    methodology: str
    success: bool = True
    warning: str | None = None
