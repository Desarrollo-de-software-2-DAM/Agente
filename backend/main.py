"""
Amershop — Backend con API FastAPI
Soporta Agente Local sin tokens (Ollama) y búsqueda híbrida con FAISS.
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Cargar entorno
_project_root = Path(__file__).resolve().parent
env_file_path = _project_root / ".env"
_parent_env = _project_root.parent / ".env"

if _parent_env.exists():
    load_dotenv(dotenv_path=_parent_env)
elif env_file_path.exists():
    load_dotenv(dotenv_path=env_file_path)
else:
    load_dotenv()

from config import (
    DOCUMENTS_DIR, LLM_PROVIDER, OLLAMA_MODEL, OLLAMA_BASE_URL,
    STORE_NAME, APP_TITLE
)
from vectorstore.chroma_store import VectorStoreManager
from agents.rag_agent import RAGAgent

# IMPORTAR COMPONENTES DE LA BASE DE DATOS
from db import (
    Base, engine, get_db, User, Message, 
    hash_password, verify_password, seed_corporate_users
)

# Crear las tablas en PostgreSQL si no existen
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Tablas de base de datos verificadas/creadas con éxito.")
except Exception as e:
    logger.warning(f"No se pudieron crear las tablas al importar (se reintentará en startup): {e}")

# Crear aplicación FastAPI
app = FastAPI(
    title="Amershop Backend API",
    description="API REST corporativa para Amershop con Agente RAG local",
    version="2.0.0"
)

# Permitir CORS para cualquier cliente frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    """Inicializa la BD, usuarios por defecto y el agente RAG al arrancar."""
    global vector_store, agent

    # 1. Crear tablas si no estaban listas y sembrar usuarios corporativos
    try:
        Base.metadata.create_all(bind=engine)
        db = next(get_db())
        seed_corporate_users(db)
        logger.info("Usuarios corporativos sembrados correctamente.")
    except Exception as e:
        logger.warning(f"Aviso al inicializar base de datos / usuarios: {e}")

    # 2. Inicializar sistema RAG
    try:
        vector_store = VectorStoreManager()
        agent = RAGAgent(vector_store_manager=vector_store)
        logger.info(f"Agente RAG inicializado con proveedor: {LLM_PROVIDER} ({OLLAMA_MODEL})")
    except Exception as e:
        logger.error(f"Error al inicializar agente RAG: {e}")

    # 3. Indexar documentos si está vacío
    try:
        if vector_store and vector_store.get_document_count() == 0:
            docs_path = Path(DOCUMENTS_DIR)
            if docs_path.exists() and any(docs_path.iterdir()):
                logger.info(f"Indexando documentos desde {docs_path}...")
                count = vector_store.reindex_from_directory(str(docs_path))
                logger.info(f"Indexación inicial completada: {count} fragmentos.")
    except Exception as e:
        logger.error(f"Error al indexar documentos iniciales: {e}")


@app.get("/")
def health_check():
    """Health check general del backend."""
    doc_count = vector_store.get_document_count() if vector_store else 0
    return {
        "status": "ok",
        "message": f"Backend de {STORE_NAME} activo",
        "llm_provider": LLM_PROVIDER,
        "model": OLLAMA_MODEL if LLM_PROVIDER == "ollama" else "gemini",
        "documents_indexed": doc_count
    }


@app.get("/status")
def system_status(db: Session = Depends(get_db)):
    """Estado detallado del sistema para la Landing Page y monitoreo."""
    users_count = 0
    messages_count = 0
    db_ok = False
    try:
        users_count = db.query(User).count()
        messages_count = db.query(Message).count()
        db_ok = True
    except Exception:
        db_ok = False

    doc_count = vector_store.get_document_count() if vector_store else 0
    sources = vector_store.get_indexed_sources() if vector_store else []

    return {
        "status": "healthy" if db_ok else "degraded",
        "store_name": STORE_NAME,
        "llm_provider": LLM_PROVIDER,
        "llm_model": OLLAMA_MODEL if LLM_PROVIDER == "ollama" else "gemini",
        "llm_local": LLM_PROVIDER == "ollama",
        "database_connected": db_ok,
        "total_users": users_count,
        "total_messages": messages_count,
        "documents_indexed": doc_count,
        "indexed_sources": sources,
    }


# --- Endpoints de Autenticación e Historial ---

@app.post("/register")
def register_endpoint(user: UserRegister, db: Session = Depends(get_db)):
    """Registra un nuevo usuario en la base de datos."""
    clean_username = user.username.strip().lower()
    clean_email = user.email.strip().lower()

    if not clean_username or not user.password:
        raise HTTPException(status_code=400, detail="Usuario y contraseña no pueden estar vacíos.")

    existing_user = db.query(User).filter(
        (User.username == clean_username) | (User.email == clean_email)
    ).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="El usuario o correo ya existe.")
    
    new_user = User(
        username=clean_username,
        email=clean_email,
        password_hash=hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    return {"message": "Usuario registrado exitosamente.", "username": clean_username}


@app.post("/login")
def login_endpoint(user: UserLogin, db: Session = Depends(get_db)):
    """Valida las credenciales del usuario."""
    clean_username = user.username.strip().lower()
    db_user = db.query(User).filter(User.username == clean_username).first()
    
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
    clean_username = username.strip().lower()
    user = db.query(User).filter(User.username == clean_username).first()
    if not user:
        return {"messages": []}
    
    messages = db.query(Message).filter(Message.user_id == user.id).order_by(Message.created_at.asc()).all()
    formatted_messages = [{"role": msg.role, "content": msg.content} for msg in messages]
    
    return {"messages": formatted_messages}


# --- Endpoint del Chat RAG ---

@app.post("/chat")
def chat_endpoint(request: QueryRequest, db: Session = Depends(get_db)):
    """Procesa preguntas del usuario y guarda el historial si está logueado."""
    global agent, vector_store
    
    # Lazy init si por alguna razón no se inicializó en startup
    if not agent:
        try:
            if not vector_store:
                vector_store = VectorStoreManager()
            agent = RAGAgent(vector_store_manager=vector_store)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"No se pudo inicializar el agente RAG: {e}")

    try:
        # Buscar el usuario en la BD (solo si no es invitado)
        user = None
        if request.username:
            clean_username = request.username.strip().lower()
            user = db.query(User).filter(User.username == clean_username).first()

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

        # Generar respuesta con IA Local / RAG
        result = agent.query(question=request.prompt, chat_history=chat_history_formatted)
        answer = result.get("answer", "Error al generar respuesta.")

        # Guardar la respuesta de la IA en la BD
        if user:
            ai_msg = Message(user_id=user.id, role="assistant", content=answer)
            db.add(ai_msg)
            db.commit()

        return {
            "answer": answer,
            "sources": result.get("sources", [])
        }
    
    except Exception as e:
        logger.error(f"Error en chat_endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))
