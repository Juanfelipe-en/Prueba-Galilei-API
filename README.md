# Galilei Quiz
Backend (FastAPI) + Frontend (React) para buscar en Wikilibros y generar preguntas con OpenRouter.

## Estructura
- backend/: API (FastAPI) y servicios (Wikilibros, LLM)
- frontend/: React (Vite) que consume `/quiz`

## Desarrollo
### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Win: .venv\\Scripts\\Activate
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --env-file .env
```
### Frontend
```bash
cd frontend
npm i
npm run dev
```