
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from ..services import wikibooks, llm, textproc

router = APIRouter(prefix="/quiz", tags=["quiz"])

class QuizRequest(BaseModel):
    q: Optional[str] = Field(None, description="Palabra de búsqueda en Wikilibros")
    text: Optional[str] = Field(None, description="Texto ya provisto")
    n: int = Field(5, description="Número objetivo de preguntas")
    model: Optional[str] = Field(None, description="Modelo OpenRouter (e.g., google/gemma-3-12b-it:free)")

class Question(BaseModel):
    question: str
    choices: List[str]
    correctIndex: int

class QuizResponse(BaseModel):
    title: Optional[str] = None
    url: Optional[str] = None
    questions: List[Question]

@router.post("", response_model=QuizResponse)
def make_quiz(req: QuizRequest):
    if not req.q and not req.text:
        raise HTTPException(400, "Provee 'q' o 'text'")
    text = req.text
    title = None
    url = None

    if req.q and not text:
        data = wikibooks.get_text_from_word(req.q)
        if not data:
            raise HTTPException(404, "No se encontró contenido para la búsqueda")
        text = data["text"]
        title = data["title"]
        url = data["url"]

    text = textproc.clean_text(text or "")
    if not text:
        raise HTTPException(422, "Texto vacío tras limpieza")

    chunks = textproc.chunk_text(text, max_chars=1000)[:2]
    questions = []
    per_chunk = max(3, req.n // len(chunks) if chunks else req.n)
    for ch in chunks or [text]:
        qs = llm.generate_mcq(ch, n=per_chunk, model_override=req.model)
        if isinstance(qs, list):
            questions.extend(qs)
        else:
            questions.append(qs)

    normalized = []
    for q in questions:
        if {"question","choices","correctIndex"} <= set(q.keys()):
            normalized.append(Question(**q))
    if not normalized:
        raise HTTPException(500, "No se pudieron generar preguntas")
    return QuizResponse(title=title, url=url, questions=normalized)
