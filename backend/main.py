"""
Amershop — Backend con API FastAPI
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Tuple

# Cargar entorno
_project_root = Path(__file__).resolve().parent
env_file_path = _project_root / ".env"

if env_file_path.exists():
    load_dotenv(dotenv_path=env_file_path)
else:
    load_dotenv()

from config import COHERE_API_KEY, DOCUMENTS_DIR
from vectorstore.chroma_store import VectorStoreManager
from agents.rag_agent import RAGAgent

# Crear aplicación FastAPI
app = FastAPI(title="Amershop Backend API")

# Variables globales para los componentes
vector_store = None
agent = None


# Modelo para recibir peticiones
class QueryRequest(BaseModel):
    prompt: str
    chat_history: List[dict] = []


@app.on_event("startup")
def startup_event():
    """Inicializa la base de datos y el agente al arrancar el contenedor del backend."""
    global vector_store, agent
    if not COHERE_API_KEY:
        raise RuntimeError("API Key de Cohere/Groq no configurada.")

    vector_store = VectorStoreManager()
    agent = RAGAgent(vector_store_manager=vector_store)

    # Indexar si está vacío
    if vector_store.get_document_count() == 0:
        docs_path = Path(DOCUMENTS_DIR)
        if docs_path.exists() and any(docs_path.iterdir()):
            vector_store.reindex_from_directory(str(docs_path))


@app.get("/")
def health_check():
    return {"status": "ok", "message": "Backend de Amershop activo"}


@app.post("/chat")
def chat_endpoint(request: QueryRequest):
    """Endpoint principal para procesar preguntas del usuario."""
    global agent
    if not agent:
        raise HTTPException(status_code=500, detail="El agente RAG no está inicializado.")

    try:
        # Formatear historial
        chat_history_formatted = [
            ("human" if m["role"] == "user" else "ai", m["content"])
            for m in request.chat_history[:-1]
        ][-10:]

        result = agent.query(question=request.prompt, chat_history=chat_history_formatted)
        answer = result.get("answer", "Error al generar respuesta.")

        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))