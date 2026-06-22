from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.app_pipeline import (
    analisar_feedbacks,
    gerar_feedbacks_aleatorios,
    limpar_feedbacks_texto,
)


app = FastAPI(title="TopicGraph EJ API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class GenerateRequest(BaseModel):
    quantidade: int = Field(default=90, ge=10, le=500)


class AnalyzeRequest(BaseModel):
    feedbacks: list[str]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze")
def analyze(payload: AnalyzeRequest):
    try:
        feedbacks = [feedback.strip() for feedback in payload.feedbacks if feedback.strip()]
        return analisar_feedbacks(feedbacks)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/upload")
async def upload_feedbacks(file: UploadFile = File(...)):
    conteudo = (await file.read()).decode("utf-8-sig")
    feedbacks = limpar_feedbacks_texto(conteudo)
    try:
        return analisar_feedbacks(feedbacks)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/generate")
def generate(payload: GenerateRequest):
    feedbacks = gerar_feedbacks_aleatorios(payload.quantidade)
    resultado = analisar_feedbacks(feedbacks)
    resultado["feedbacks_gerados"] = feedbacks
    return resultado
