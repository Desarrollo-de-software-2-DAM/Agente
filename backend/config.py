# Configuración centralizada del agente Amershop
"""
Módulo de configuración centralizada para el agente IA de Amershop.
Todas las constantes y configuraciones del proyecto se manejan desde aquí.
Soporta LLM Local (Ollama - 100% gratuito y sin tokens) y Gemini como opción secundaria.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno desde .env (usando ruta relativa a este archivo o la raíz)
_backend_dir = Path(__file__).resolve().parent
_root_dir = _backend_dir.parent

if (_root_dir / ".env").exists():
    load_dotenv(dotenv_path=_root_dir / ".env")
elif (_backend_dir / ".env").exists():
    load_dotenv(dotenv_path=_backend_dir / ".env")
else:
    load_dotenv()

# --- Configuración General ---
STORE_NAME = os.getenv("STORE_NAME", "Amershop")
APP_TITLE = f"🛒 {STORE_NAME} — Asistente IA Corporativo"
APP_ICON = "🛒"
APP_DESCRIPTION = (
    f"Asistente virtual de {STORE_NAME} para colaboradores y clientes. "
    "Responde preguntas basándose en los documentos internos de la empresa."
)

# --- Configuración del Proveedor LLM ---
# "ollama" (Local, sin tokens, sin costo) o "gemini" (API externa)
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower().strip()

# --- Configuración de Ollama (Agente Local) ---
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
OLLAMA_TEMPERATURE = float(os.getenv("OLLAMA_TEMPERATURE", "0.1"))

# --- Configuración de Google Gemini (Opcional / Fallback) ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
HF_TOKEN = os.getenv("HF_TOKEN", "")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
LLM_MODEL_AGENT = os.getenv("LLM_MODEL_AGENT", "gemini-1.5-flash")
LLM_MODEL_GRADER = os.getenv("LLM_MODEL_GRADER", "gemini-1.5-flash")

# --- Configuración del Vector Store ---
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "fastembed")
FAISS_PERSIST_DIR = os.getenv("FAISS_PERSIST_DIR", "./faiss_db")
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
Tu rol es responder preguntas de los colaboradores y clientes basándote ÚNICAMENTE en los documentos internos de la empresa proporcionados como contexto.

Instrucciones Críticas:
1. LEE y ANALIZA el contexto proporcionado cuidadosamente antes de formular tu respuesta.
2. Sé directo, claro y conciso.

Reglas Estrictas:
- Responde siempre en español.
- Precios y Divisas: Habla EXCLUSIVAMENTE en Pesos Colombianos (COP). Tienes ESTRICTAMENTE PROHIBIDO realizar conversiones a otras divisas, sin importar lo que pida el usuario.
- Fuera de Dominio: Si la pregunta NO tiene que ver con la tienda {STORE_NAME}, o la información NO está explícitamente en los documentos, NIÉGATE a responder. Responde exactamente: 'No encontré información sobre este tema en los documentos disponibles. Te sugiero consultar con el área correspondiente.'
- Conflictos entre documentos: si dos fuentes se contradicen, prevalece SIEMPRE `datos_oficiales.md`.
- Sinónimos: 'portátil', 'notebook' y 'laptop' son la misma categoría; 'celular', 'móvil' y 'smartphone' también.
- No inventes, asumas, ni alucines información bajo ninguna circunstancia.
- Si la pregunta es un saludo, responde amablemente y ofrece tu ayuda.
"""
