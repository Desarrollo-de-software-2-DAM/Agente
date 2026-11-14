"""
Pruebas del gestor vectorial (FAISS + FastEmbed) de Amershop.
Verifica la indexación en disco temporal, búsqueda híbrida y limpieza.
"""

from pathlib import Path
from vectorstore.faiss_store import VectorStoreManager
from langchain_core.documents import Document


def test_vector_store_initialization(tmp_path):
    """Verifica que el gestor vectorial se inicialice correctamente en un directorio temporal."""
    manager = VectorStoreManager(persist_directory=str(tmp_path), collection_name="test_col")
    assert manager.get_document_count() == 0
    assert manager.get_indexed_sources() == []


def test_index_and_count_documents(tmp_path, sample_documents):
    """Verifica que los documentos se indexen y se calcule el recuento de fragmentos."""
    manager = VectorStoreManager(persist_directory=str(tmp_path), collection_name="test_col")
    count = manager.index_documents(sample_documents)
    assert count >= 3
    assert manager.get_document_count() == count

    sources = manager.get_indexed_sources()
    assert "politica_reembolso.md" in sources
    assert "datos_oficiales.md" in sources


def test_clear_store(tmp_path, sample_documents):
    """Verifica que clear_store vacíe los documentos y elimine los archivos de persistencia."""
    manager = VectorStoreManager(persist_directory=str(tmp_path), collection_name="test_col")
    manager.index_documents(sample_documents)
    assert manager.get_document_count() > 0

    manager.clear_store()
    assert manager.get_document_count() == 0
    assert manager.get_indexed_sources() == []


def test_search_returns_relevant_document(tmp_path, sample_documents):
    """Verifica que la búsqueda híbrida recupere el documento relevante."""
    manager = VectorStoreManager(persist_directory=str(tmp_path), collection_name="test_col")
    manager.index_documents(sample_documents)

    results = manager.search("horario de atencion", k=1)
    assert len(results) > 0
    assert "horario" in results[0].page_content.lower()
