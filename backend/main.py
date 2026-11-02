"""
Amershop — Backend con API FastAPI
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session

# Cargar entorno
_project_root = Path(__file__).resolve().parent
env_file_path = _project_root / ".env"

if env_file_path.exists():
    load_dotenv(dotenv_path=env_file_path)
else:
    load_dotenv()

from config import GOOGLE_API_KEY, DOCUMENTS_DIR
from vectorstore.chroma_store import VectorStoreManager
from agents.rag_agent import RAGAgent

# IMPORTAR COMPONENTES DE LA BASE DE DATOS
from db import (
    Base, engine, get_db, User, Message, 
    hash_password, verify_password, seed_corporate_users
)

# Crear las tablas en PostgreSQL si no existen
Base.metadata.create_all(bind=engine)

# Crear aplicación FastAPI
app = FastAPI(title="Amershop Backend API")

# Variables globales para los componentes
vector_store = None
agent = None

# --- Modelos Pydantic para recibir peticiones ---
class UserRegister(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class QueryRequest(BaseModel):
    prompt: str
    chat_history: List[dict] = []
    username: Optional[str] = None  # Permite asociar el chat a un usuario logueado


@app.on_event("startup")
def startup_event():
    """Inicializa la BD, usuarios por defecto y el agente al arrancar."""
    global vector_store, agent
    if not GOOGLE_API_KEY:
        raise RuntimeError("API Key de Google no configurada.")

    # 1. Sembrar usuarios corporativos en PostgreSQL
    db = next(get_db())
    try:
        seed_corporate_users(db)
    except Exception as e:
        print(f"Error al sembrar usuarios: {e}")

    # 2. Inicializar sistema RAG
    vector_store = VectorStoreManager()
    agent = RAGAgent(vector_store_manager=vector_store)

    # 3. Indexar documentos si está vacío
    if vector_store.get_document_count() == 0:
        docs_path = Path(DOCUMENTS_DIR)
        if docs_path.exists() and any(docs_path.iterdir()):
            vector_store.reindex_from_directory(str(docs_path))


@app.get("/")
def health_check():
    return {"status": "ok", "message": "Backend de Amershop activo"}


# --- Endpoints de Autenticación e Historial ---

@app.post("/register")
def register_endpoint(user: UserRegister, db: Session = Depends(get_db)):
    """Registra un nuevo usuario en la base de datos."""
    existing_user = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="El usuario o correo ya existe.")
    
    new_user = User(
        username=user.username,
        email=user.email,
        password_hash=hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    return {"message": "Usuario registrado exitosamente."}


@app.post("/login")
def login_endpoint(user: UserLogin, db: Session = Depends(get_db)):
    """Valida las credenciales del usuario."""
    db_user = db.query(User).filter(User.username == user.username).first()
    
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos.")
    
    return {
        "message": "Login exitoso", 
        "username": db_user.username, 
        "email": db_user.email
    }


@app.get("/history/{username}")
def get_history(username: str, db: Session = Depends(get_db)):
    """Devuelve el historial de chat de un usuario específico."""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return {"messages": []}
    
    messages = db.query(Message).filter(Message.user_id == user.id).order_by(Message.created_at.asc()).all()
    formatted_messages = [{"role": msg.role, "content": msg.content} for msg in messages]
    
    return {"messages": formatted_messages}


# --- Endpoint del Chat RAG ---

@app.post("/chat")
def chat_endpoint(request: QueryRequest, db: Session = Depends(get_db)):
    """Procesa preguntas del usuario y guarda el historial si está logueado."""
    global agent
    if not agent:
        raise HTTPException(status_code=500, detail="El agente RAG no está inicializado.")

    try:
        # Buscar el usuario en la BD (solo si no es invitado)
        user = None
        if request.username:
            user = db.query(User).filter(User.username == request.username).first()

        # Guardar la pregunta del usuario en la BD
        if user:
            user_msg = Message(user_id=user.id, role="user", content=request.prompt)
            db.add(user_msg)
            db.commit()

        # Formatear historial para el agente
        chat_history_formatted = [
            ("human" if m["role"] == "user" else "ai", m["content"])
            for m in request.chat_history[:-1]
        ][-10:]

        # Generar respuesta con IA
        result = agent.query(question=request.prompt, chat_history=chat_history_formatted)
        answer = result.get("answer", "Error al generar respuesta.")

        # Guardar la respuesta de la IA en la BD
        if user:
            ai_msg = Message(user_id=user.id, role="assistant", content=answer)
            db.add(ai_msg)
            db.commit()

        return {"answer": answer}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))