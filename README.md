# Prueba de Galilei de implementación de API
Backend (FastAPI) + Frontend (React) para buscar en Wikilibros y generar preguntas con la API de IA de OpenRouter.

## Estructura
- backend/: API (FastAPI) y servicios (Wikilibros, LLM)
- frontend/: React (Vite) que consume `/quiz`

## Requisitos
- Python 3.11+
- Node 18+
## Como Ejecutar:
### Backend
agregar APIKEY a .env.example

```bash
cd backend
cp .env.example .env
python -m venv .venv
source .venv/bin/activate   # Win: .venv\\Scripts\\Activate
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```
### Frontend
```bash
cd frontend
npm i
npm run dev
```
