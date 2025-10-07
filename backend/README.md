
# Prueba de Galilei de implementación de API - Backend (FastAPI)

Backend para:
1) Buscar por palabra en **Wikilibros**.
2) Obtener HTML y **texto** del mejor match.
3) Generar **preguntas tipo test** con **OpenRouter** (modelo `:free`).

## Arranque rápido
Agregar APIKEY en .env.example

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env


uvicorn app.main:app --reload
# Docs: http://localhost:8000/docs
```

## Endpoints
- `GET /search?q=palabra` → mejor match `{title,key,url}`
- `GET /book?q=palabra` → `{title,key,url,html,text}`
- `POST /quiz` → body `{ "q": "palabra", "n": 6 }` **o** `{ "text": "...", "n": 6 }` (+ opcional `"model"`)


