# Configuración centralizada del agente AmershOp
"""
Módulo de configuración centralizada para el agente IA de AmershOp.
Todas las constantes y configuraciones del proyecto se manejan desde aquí.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno desde .env (usando ruta relativa a este archivo)
_env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=_env_path)

# --- Configuración General ---
STORE_NAME = os.getenv("STORE_NAME", "Amershop")
APP_TITLE = f"🛒 {STORE_NAME} — Asistente IA Corporativo"
APP_ICON = "🛒"
APP_DESCRIPTION = (
    f"Asistente virtual de {STORE_NAME} para colaboradores. "
    "Responde preguntas basándose en los documentos internos de la empresa."
)

# --- Configuración del LLM y OAuth ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
HF_TOKEN = os.getenv("HF_TOKEN", "")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
LLM_MODEL_AGENT = os.getenv("LLM_MODEL_AGENT", "gemini-3.5-flash")
LLM_MODEL_GRADER = os.getenv("LLM_MODEL_GRADER", "gemini-3.5-flash")


# --- Configuración del Vector Store ---
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "models/embedding-001")  
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "amershop_docs")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
SEARCH_K = int(os.getenv("SEARCH_K", "8"))

# --- Configuración de Documentos ---
DOCUMENTS_DIR = os.getenv("DOCUMENTS_DIR", "./documents")
SUPPORTED_EXTENSIONS = {
    ".pdf", ".docx", ".xlsx", ".pptx",
    ".md", ".csv", ".json", ".html"
}

# --- Configuración de Autenticación ---
# Usuarios autorizados: {usuario: contraseña}
# En producción, esto debería estar en una base de datos o servicio de autenticación
AUTH_USERS = {
    "admin": os.getenv("ADMIN_PASSWORD", "amershop2024"),
    "colaborador1": os.getenv("USER1_PASSWORD", "collab001"),
    "colaborador2": os.getenv("USER2_PASSWORD", "collab002"),
    "rrhh": os.getenv("RRHH_PASSWORD", "recursosh01"),
    "ventas": os.getenv("VENTAS_PASSWORD", "ventas2024"),
    "soporte": os.getenv("SOPORTE_PASSWORD", "soporte01"),
}

# --- Prompt del Sistema ---
SYSTEM_PROMPT = f"""Eres el asistente virtual corporativo de {STORE_NAME}, una tienda online de tecnología.
Tu rol es responder preguntas de los colaboradores basándote ÚNICAMENTE en los documentos internos de la empresa proporcionados como contexto.

Reglas:
- Responde siempre en español
- Cita el documento fuente entre corchetes [nombre_archivo] al final de cada afirmación relevante
- Si no encuentras la información en el contexto, responde: 'No encontré información sobre este tema en los documentos disponibles. Te sugiero consultar con el área correspondiente.'
- Sé conciso pero completo en tus respuestas
- No inventes información que no esté en los documentos
- Si la pregunta es un saludo, responde amablemente y ofrece tu ayuda
- Formatea tus respuestas con markdown cuando sea apropiado (listas, negritas, etc.)
"""
