import logging
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config import (
    LLM_PROVIDER, OLLAMA_BASE_URL, OLLAMA_MODEL,
    LLM_MODEL_GRADER, GOOGLE_API_KEY
)

logger = logging.getLogger(__name__)


def create_grader_llm():
    """Crea la instancia LLM para el evaluador de documentos."""
    if LLM_PROVIDER == "ollama":
        try:
            from langchain_ollama import ChatOllama
            return ChatOllama(
                model=OLLAMA_MODEL,
                base_url=OLLAMA_BASE_URL,
                temperature=0.0,
            )
        except Exception:
            from langchain_community.chat_models import ChatOllama
            return ChatOllama(
                model=OLLAMA_MODEL,
                base_url=OLLAMA_BASE_URL,
                temperature=0.0,
            )
    else:
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=LLM_MODEL_GRADER,
            google_api_key=GOOGLE_API_KEY,
            temperature=0.0,
        )


class DocumentGrader:
    """
    Evalúa si un documento recuperado es relevante para la pregunta del usuario.
    Funciona localmente con Ollama o con Gemini.
    """

    def __init__(self, llm=None):
        self.llm = llm if llm is not None else create_grader_llm()

        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", """Eres un evaluador de relevancia de documentos para la tienda Amershop.
Tu tarea es evaluar si el documento proporcionado contiene información útil para responder a la pregunta del usuario.
Responde ÚNICAMENTE con 'SI' si el documento es relevante, o 'NO' si no lo es."""),
                ("human", "Pregunta: {question}\n\nDocumento: {document}")
            ]
        )

        self.chain = self.prompt | self.llm | StrOutputParser()

    def grade(self, question: str, document: Document) -> bool:
        """
        Evalúa la relevancia de un documento frente a una pregunta.
        """
        try:
            result = self.chain.invoke({
                "question": question,
                "document": document.page_content
            })
            return result.strip().upper().startswith("SI")
        except Exception as e:
            logger.error(f"Error al evaluar el documento: {e}")
            # En caso de error, asumimos relevante para no perder información
            return True
