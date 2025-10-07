
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from ..services import wikibooks, llm, textproc

router = APIRouter(prefix="/quiz", tags=["quiz"])

class QuizRequest(BaseModel):
    """
    Petición para generar preguntas.
    - q: palabra/tema a buscar en Wikilibros (opcional si ya envías 'text')
    - text: texto ya provisto (omitir 'q' en ese caso)
    - n: número objetivo de preguntas a generar
    - model: modelo OpenRouter
    """
    q: Optional[str] = Field(None, description="Palabra de búsqueda en Wikilibros")
    text: Optional[str] = Field(None, description="Texto ya provisto")
    n: int = Field(None, description="Número objetivo de preguntas")
    model: Optional[str] = Field(None, description="Modelo OpenRouter (e.g., google/gemma-3-12b-it:free)")

class Question(BaseModel):
    """Estructura de una pregunta de opción múltiple."""
    question: str
    choices: List[str]
    correctIndex: int

class QuizResponse(BaseModel):
    """Respuesta de la API con metadatos de la fuente y la lista de preguntas."""
    title: Optional[str] = None
    url: Optional[str] = None
    questions: List[Question]

@router.post("", response_model=QuizResponse)
def make_quiz(req: QuizRequest):

    """
    Flujo:
    1) Si viene 'q', busca el texto en Wikilibros; si viene 'text', lo usamos tal cual.
    2) Limpia el texto y lo "parte" en 1–2 chunks cortos para el LLM.
    3) Pedimos al LLM N preguntas (repartidas por chunk).
    4) Normaliza/valida la estructura.
    """
    if not req.q and not req.text:
        raise HTTPException(400, "Provee 'q' o 'text'")

    # Texto y metadatos de la fuente (para mostrar al usuario)    
    text = req.text
    title = None
    url = None
    
    # Si la búsqueda es por palabra, trae el texto desde Wikilibros
    if req.q and not text:
        data = wikibooks.get_text_from_word(req.q)
        if not data:
            raise HTTPException(404, "No se encontró contenido para la búsqueda")
        text = data["text"]
        title = data["title"]
        url = data["url"]

   
    
    # Limpieza de texto (espacios, saltos, etc.)
    text = textproc.clean_text(text or "")
    if not text:
        raise HTTPException(422, "Texto vacío tras limpieza")

    # Partimos el texto en trozos razonables (máx ~1000 chars) ya que al ser un modelo de AI gratis y ser una prueba, está muy limitado; tomamos hasta 3 en diferentes secciones del texto para más variedad.    
    all_chunks = textproc.chunk_text(text, max_chars=1000)

    if not all_chunks:
        chunks = []
    elif len(all_chunks) <= 3:
        chunks = all_chunks
    else:
        L = len(all_chunks)
        # índices repartidos: inicio, medio y fin
        indices = [0, round((L - 1) / 2), L - 1]
        chunks = [all_chunks[i] for i in indices]
    
    
    # Acumula preguntas de todos los chunks
    questions = []
    
    # Reparto simple: al menos 3 por chunk; evita división por cero
    per_chunk = max(3, req.n // len(chunks) if chunks else req.n)


    # Por cada chunk, pide preguntas al LLM
    for ch in (chunks or [text]):
        qs = llm.generate_mcq(ch, n=per_chunk, model_override=req.model)
        # El servicio puede devolver lista o una sola pregunta; normaliza a lista
        if isinstance(qs, list):
            questions.extend(qs)
        elif isinstance(qs, dict):
            questions.append(qs)

    # Normaliza/valida estructura
    normalized = []
    for q in questions:
        if isinstance(q, dict) and {"question", "choices", "correctIndex"} <= set(q.keys()):
            normalized.append(Question(**q))

    if not normalized:
        raise HTTPException(500, "No se pudieron generar preguntas")

    # NO devolver más de req.n en caso de que el modelo AI falle.
    n_int = max(1, int(req.n))
    normalized = normalized[:n_int]

    return QuizResponse(title=title, url=url, questions=normalized)
