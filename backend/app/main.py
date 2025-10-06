
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import search, books, quiz

app = FastAPI(title="Galilei Quiz API (mínimo)", version="0.1.0")

# CORS abierto para facilitar desarrollo de frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rutas
app.include_router(search.router)
app.include_router(books.router)
app.include_router(quiz.router)
