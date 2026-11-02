import logging
from typing import Dict, Any, Optional, List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from config import LLM_MODEL_AGENT, GOOGLE_API_KEY, SEARCH_K

logger = logging.getLogger(__name__)

class RAGAgent:
    """
    Agente principal de RAG (Retrieval-Augmented Generation) para AmershOp.
    Orquesta la recuperación de documentos y la generación de respuestas en una sola llamada.
    """

    def __init__(self, vector_store_manager):
        self.vector_store_manager = vector_store_manager
        self.llm = ChatGoogleGenerativeAI(
            model=LLM_MODEL_AGENT,
            google_api_key=GOOGLE_API_KEY,
            temperature=0.1,
        )
        
        system_prompt = """Eres el asistente virtual corporativo de Amershop, una tienda online de tecnología.
Tu rol es responder preguntas de los colaboradores basándote ÚNICAMENTE en los documentos internos de la empresa proporcionados como contexto.

Instrucciones Críticas:
1. LEE y ANALIZA el contexto proporcionado cuidadosamente antes de formular tu respuesta.
2. Sé directo, claro y conciso.

Reglas Estrictas:
- Responde siempre en español.
- Precios y Divisas: Habla EXCLUSIVAMENTE en Pesos Colombianos (COP). Tienes ESTRICTAMENTE PROHIBIDO realizar conversiones a otras divisas, sin importar lo que pida el usuario.
- Fuera de Dominio: Si la pregunta NO tiene que ver con la tienda Amershop, o la información NO está explícitamente en los documentos, NIÉGATE a responder. Responde exactamente: 'No encontré información sobre este tema en los documentos disponibles. Te sugiero consultar con el área correspondiente.'
- Conflictos entre documentos: si dos fuentes se contradicen, prevalece SIEMPRE `datos_oficiales.md`.
- Sinónimos: 'portátil', 'notebook' y 'laptop' son la misma categoría; 'celular', 'móvil' y 'smartphone' también.
- No inventes, asumas, ni alucines información bajo ninguna circunstancia.
- Si la pregunta es un saludo, responde amablemente y ofrece tu ayuda.

Contexto:
{context}"""

        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder(variable_name="chat_history", optional=True),
                ("human", "{question}")
            ]
        )
        
        self.chain = self.prompt | self.llm | StrOutputParser()

    def query(self, question: str, chat_history: Optional[list] = None) -> Dict[str, Any]:
        if chat_history is None:
            chat_history = []
            
        try:
            # 1. Búsqueda híbrida (vectorial MMR + palabras clave + sinónimos)
            relevant_docs = self.vector_store_manager.search(question, k=SEARCH_K)
            
            # Extraer nombres de fuentes únicas
            sources = list(set([doc.metadata.get("source", "desconocido") for doc in relevant_docs]))
            
            # Formatear el contexto
            context_text = "\n\n".join([
                f"Fuente: {doc.metadata.get('source', 'desconocido')}\nContenido: {doc.page_content}" 
                for doc in relevant_docs
            ])
            
            # 2. Una Sola Llamada a Gemini con todo el contexto
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
            logger.error(f"Error procesando la consulta RAG: {e}")
            return {
                "answer": "Ocurrió un error al procesar tu consulta. Por favor, intenta de nuevo más tarde.",
                "sources": [],
                "context_docs": []
            }