import logging
import re
from typing import Dict, Any, Optional, List
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from config import (
    LLM_PROVIDER, OLLAMA_BASE_URL, OLLAMA_MODEL, OLLAMA_TEMPERATURE,
    LLM_MODEL_AGENT, GOOGLE_API_KEY, SEARCH_K, STORE_NAME, SYSTEM_PROMPT
)
from utils.text_normalize import normalize

logger = logging.getLogger(__name__)

NO_DOCUMENTS_ANSWER = (
    "No encontré información sobre este tema en los documentos disponibles. "
    "Te sugiero consultar con el área correspondiente."
)
_GREETING_WORDS = {
    "buenas", "buenos", "dia", "dias", "hola", "hey", "noches", "saludos", "tardes"
}
_GREETING_STARTS = {"buenas", "buenos", "hola", "hey", "saludos"}


def _is_greeting(question: str) -> bool:
    words = set(re.findall(r"[a-z]+", normalize(question)))
    return bool(words) and words.issubset(_GREETING_WORDS) and bool(
        words.intersection(_GREETING_STARTS)
    )


def create_llm_instance():
    """
    Crea la instancia del modelo de lenguaje según la configuración.
    Por defecto usa Ollama (100% local, sin tokens ni costos).
    """
    if LLM_PROVIDER == "ollama":
        logger.info(f"Inicializando Agente con LLM Local Ollama (modelo: {OLLAMA_MODEL}, url: {OLLAMA_BASE_URL})")
        try:
            from langchain_ollama import ChatOllama
            return ChatOllama(
                model=OLLAMA_MODEL,
                base_url=OLLAMA_BASE_URL,
                temperature=OLLAMA_TEMPERATURE,
            )
        except (ImportError, Exception) as e:
            logger.warning(f"langchain_ollama falló ({e}). Intentando langchain_community...")
            from langchain_community.chat_models import ChatOllama
            return ChatOllama(
                model=OLLAMA_MODEL,
                base_url=OLLAMA_BASE_URL,
                temperature=OLLAMA_TEMPERATURE,
            )
    elif LLM_PROVIDER == "gemini":
        logger.info(f"Inicializando Agente con Google Gemini (modelo: {LLM_MODEL_AGENT})")
        from langchain_google_genai import ChatGoogleGenerativeAI
        if not GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY es requerida para el proveedor 'gemini'.")
        return ChatGoogleGenerativeAI(
            model=LLM_MODEL_AGENT,
            google_api_key=GOOGLE_API_KEY,
            temperature=0.1,
        )
    else:
        # Fallback predeterminado a Ollama
        logger.warning(f"Proveedor '{LLM_PROVIDER}' no reconocido. Usando Ollama local por defecto.")
        from langchain_ollama import ChatOllama
        return ChatOllama(
            model=OLLAMA_MODEL,
            base_url=OLLAMA_BASE_URL,
            temperature=OLLAMA_TEMPERATURE,
        )


class RAGAgent:
    """
    Agente principal de RAG (Retrieval-Augmented Generation) para Amershop.
    Soporta LLM Local (Ollama) sin consumo de tokens ni costos de API,
    así como búsqueda híbrida (vectorial FAISS + palabras clave con sinónimos).
    """

    def __init__(self, vector_store_manager, llm=None):
        self.vector_store_manager = vector_store_manager
        self.llm = llm if llm is not None else create_llm_instance()

        system_message_content = f"""{SYSTEM_PROMPT}

Contexto de los documentos oficiales:
{{context}}"""

        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_message_content),
                MessagesPlaceholder(variable_name="chat_history", optional=True),
                ("human", "{question}")
            ]
        )

        self.chain = self.prompt | self.llm | StrOutputParser()

    def query(self, question: str, chat_history: Optional[list] = None) -> Dict[str, Any]:
        """
        Ejecuta el ciclo RAG: búsqueda híbrida sobre FAISS y generación de respuesta con LLM.
        """
        if chat_history is None:
            chat_history = []

        try:
            # 1. Búsqueda híbrida (vectorial MMR + palabras clave + sinónimos)
            relevant_docs = []
            if self.vector_store_manager is not None:
                relevant_docs = self.vector_store_manager.search(question, k=SEARCH_K)

            sources = list(dict.fromkeys(
                doc.metadata.get("source", "desconocido")
                for doc in relevant_docs
            ))

            if not relevant_docs:
                answer = (
                    f"¡Hola! Soy el asistente virtual de {STORE_NAME}. "
                    "¿En qué puedo ayudarte?"
                    if _is_greeting(question)
                    else NO_DOCUMENTS_ANSWER
                )
                return {
                    "answer": answer,
                    "sources": [],
                    "context_docs": [],
                }

            # Formatear el contexto
            context_text = "\n\n".join([
                f"Fuente: {doc.metadata.get('source', 'desconocido')}\nContenido: {doc.page_content}"
                for doc in relevant_docs
            ])

            # 2. Generación con el LLM (Ollama local o Gemini)
            answer = self.chain.invoke({
                "context": context_text,
                "question": question,
                "chat_history": chat_history
            })

            return {
                "answer": answer,
                "sources": sources,
                "context_docs": relevant_docs
            }

        except Exception as e:
            error_str = str(e)
            logger.error(f"Error procesando la consulta RAG: {error_str}")

            # Mensajes amigables según el tipo de error
            if "Connection refused" in error_str or "11434" in error_str:
                user_msg = (
                    "⚠️ No se pudo conectar con el servicio local de Ollama (puerto 11434). "
                    "Verifica que el contenedor o servicio 'ollama' esté corriendo y que el modelo "
                    f"'{OLLAMA_MODEL}' esté descargado con: `ollama pull {OLLAMA_MODEL}`."
                )
            elif "not found" in error_str.lower() and "model" in error_str.lower():
                user_msg = (
                    f"⚠️ El modelo local '{OLLAMA_MODEL}' no está descargado aún en Ollama. "
                    f"Ejecuta en tu servidor: `docker exec -it agente_ollama ollama pull {OLLAMA_MODEL}`."
                )
            else:
                user_msg = f"Ocurrió un error al procesar tu consulta: {error_str}"

            return {
                "answer": user_msg,
                "sources": [],
                "context_docs": []
            }
