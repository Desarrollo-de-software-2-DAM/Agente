import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config import LLM_MODEL_GRADER, GOOGLE_API_KEY

logger = logging.getLogger(__name__)

class DocumentGrader:
    """
    Evalúa si un documento recuperado es relevante para la pregunta del usuario.
    Utiliza un LLM (Gemini) para realizar la evaluación de manera rápida.
    """

    def __init__(self):
        """Inicializa el evaluador de documentos con Gemini."""
        self.llm = ChatGoogleGenerativeAI(
            model=LLM_MODEL_GRADER, 
            google_api_key=GOOGLE_API_KEY, 
            temperature=0)


        # Prompt para evaluar la relevancia del documento
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", """Eres un evaluador de relevancia de documentos.
Tu tarea es evaluar si el documento proporcionado contiene información útil para responder a la pregunta del usuario.
Responde ÚNICAMENTE con 'SI' si el documento es relevante, o 'NO' si no lo es."""),
                ("human", "Pregunta: {question}\n\nDocumento: {document}")
            ]
        )
        
        self.chain = self.prompt | self.llm | StrOutputParser()

    def grade(self, question: str, document: Document) -> bool:
        """
        Evalúa la relevancia de un documento frente a una pregunta.

        Args:
            question (str): La pregunta del usuario.
            document (Document): El documento a evaluar.

        Returns:
            bool: True si el documento es relevante, False en caso contrario.
        """
        try:
            result = self.chain.invoke({
                "question": question,
                "document": document.page_content
            })
            return result.strip().upper() == "SI"
        except Exception as e:
            logger.error(f"Error al evaluar el documento: {e}")
            # En caso de error, asumimos que es relevante para no perder información útil
            return True
