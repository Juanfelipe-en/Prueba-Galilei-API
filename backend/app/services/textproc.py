"""
Limpieza y particionado de texto para enviar al LLM.
"""
import re

def clean_text(t: str) -> str:
    """Quita espacios raros, normaliza saltos de línea y elimina ruido simple."""
    t = t or ""
    t = t.replace("\r\n", "\n").replace("\r", "\n") 
    t = re.sub(r"\n{3,}", "\n\n", t)                 
    return t.strip()

def chunk_text(t: str, max_chars=1200):
    """
    Parte el texto en trozos de tamaño máximo 'max_chars' sin romper demasiado
    el contexto. Aquí es simple por caracteres (se puede mejorar por párrafos).
    """
    paras = [p.strip() for p in (t or "").split("\n") if p.strip()]
    chunks, cur = [], ""
    for p in paras:
        if len(cur) + len(p) + 1 <= max_chars:
            cur += ("\n" if cur else "") + p
        else:
            if cur: chunks.append(cur)
            cur = p
    if cur: chunks.append(cur)
    return chunks
