
import re

def clean_text(t: str) -> str:
    t = t or ""
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()

def chunk_text(t: str, max_chars=1200):
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
