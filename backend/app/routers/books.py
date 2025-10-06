
from fastapi import APIRouter, HTTPException, Query
from ..services.wikibooks import get_text_from_word

router = APIRouter(prefix="/book", tags=["book"])

@router.get("")
def book(q: str = Query(..., description="Palabra a buscar en Wikilibros")):
    data = get_text_from_word(q)
    if not data:
        raise HTTPException(404, "No se encontró contenido")
    return data
