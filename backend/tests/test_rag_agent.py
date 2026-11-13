"""
Pruebas del agente RAG (Retrieval-Augmented Generation) de Amershop.
Verifica la orquestación del agente con LLM simulado para pruebas deterministas y sin red.
"""

from unittest.mock import MagicMock
from langchain_core.documents import Document
from agents.rag_agent import RAGAgent



class FakeLLM:
    """LLM falso para pruebas deterministas sin conexión a Ollama/Gemini."""

    def __init__(self, response_text: str = "Respuesta simulada"):
        self.response_text = response_text

    def __call__(self, prompt_value):
        """Permite que LangChain utilice esta clase como Runnable."""
        return self.response_text

    def invoke(self, *args, **kwargs):
        return self.response_text



def test_rag_agent_query_success():
    """Verifica el flujo RAG: búsqueda y generación de respuesta."""
    fake_docs = [
        Document(
            page_content="El plazo de garantía legal es de 1 año para equipos nuevos.",
            metadata={"source": "terminos_condiciones.pdf"}
        )
    ]
    mock_vectorstore = MagicMock()
    mock_vectorstore.search.return_value = fake_docs

    fake_llm = FakeLLM("La garantía legal es de 1 año.")
    agent = RAGAgent(vector_store_manager=mock_vectorstore, llm=fake_llm)

    result = agent.query("¿Cuánto tiempo de garantía tienen los productos?")
    assert "garantía" in result["answer"].lower()
    assert "terminos_condiciones.pdf" in result["sources"]
    assert len(result["context_docs"]) == 1


def test_rag_agent_query_no_documents():
    """Verifica que el agente maneje búsquedas sin documentos relevantes sin lanzar excepciones."""
    mock_vectorstore = MagicMock()
    mock_vectorstore.search.return_value = []

    fake_llm = FakeLLM("No encontré información sobre este tema en los documentos disponibles.")
    agent = RAGAgent(vector_store_manager=mock_vectorstore, llm=fake_llm)

    result = agent.query("¿Venden cohetes espaciales?")
    assert "no encontré información" in result["answer"].lower()
    assert result["sources"] == []
