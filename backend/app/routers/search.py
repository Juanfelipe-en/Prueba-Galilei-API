
from fastapi import APIRouter, HTTPException, Query
from ..services.wikibooks import search_top

router = APIRouter(prefix="/search", tags=["search"])

@router.get("")
def search(q: str = Query(..., description="Palabra a buscar en Wikilibros"), limit: int = 1):
    hit = search_top(q, limit=limit)
    if not hit:
        raise HTTPException(404, "Sin resultados")
    return hit
