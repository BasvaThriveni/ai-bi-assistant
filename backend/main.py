from __future__ import annotations

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path

from backend.ai_service import ask_question
from backend.database import get_summary, init_db
from backend.data_loader import import_sales_csv
from backend.models import QuestionRequest

BASE_DIR = Path(__file__).resolve().parents[1]
FRONTEND_DIR = BASE_DIR / "frontend"

app = FastAPI(title="AI Business Intelligence Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event() -> None:
    init_db()
    if get_summary()["total_records"] == 0:
        import_sales_csv()


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "ai-bi-assistant"}


@app.get("/api/summary")
def summary() -> dict:
    return get_summary()


@app.post("/api/ask")
def ask(request: QuestionRequest) -> dict:
    try:
        result = ask_question(request.question)
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get("/")
def index() -> FileResponse:
    return FileResponse(FRONTEND_DIR / 'index.html')


@app.get("/style.css")
def style_css() -> FileResponse:
    return FileResponse(FRONTEND_DIR / 'style.css')


@app.get("/app.js")
def app_js() -> FileResponse:
    return FileResponse(FRONTEND_DIR / 'app.js')


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    message = "Question cannot be empty."
    if exc.errors():
        for error in exc.errors():
            if error.get("loc") and error["loc"][-1] == "question":
                message = "Question cannot be empty."
                break
    return JSONResponse(status_code=400, content={"detail": message})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
