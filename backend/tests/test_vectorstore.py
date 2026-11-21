"""
Pruebas del gestor vectorial (FAISS + FastEmbed) de Amershop.
Verifica la indexación en disco temporal, búsqueda híbrida y limpieza.
"""

from pathlib import Path
from types import SimpleNamespace
from vectorstore.faiss_store import VectorStoreManager
from langchain_core.documents import Document
from config import CHUNK_OVERLAP, CHUNK_SIZE, EMBEDDING_MODEL


def test_vector_store_initialization(tmp_path):
    """Verifica que el gestor vectorial se inicialice correctamente en un directorio temporal."""
    manager = VectorStoreManager(persist_directory=str(tmp_path), collection_name="test_col")
    assert manager.get_document_count() == 0
    assert manager.get_indexed_sources() == []


def test_vector_store_uses_configured_embedding_and_chunking(tmp_path, monkeypatch):
    """Comprueba que se apliquen las opciones de embedding y fragmentación."""
    monkeypatch.setattr(
        "vectorstore.faiss_store.FastEmbedEmbeddings",
        lambda **kwargs: SimpleNamespace(**kwargs),
    )

    manager = VectorStoreManager(persist_directory=str(tmp_path), collection_name="test_col")

    assert manager.embeddings.model_name == EMBEDDING_MODEL
    assert manager.text_splitter._chunk_size == CHUNK_SIZE
    assert manager.text_splitter._chunk_overlap == CHUNK_OVERLAP


def test_incompatible_persisted_index_is_discarded(tmp_path, monkeypatch):
    """Evita reutilizar vectores creados con otro modelo o configuración."""
    monkeypatch.setattr(
        "vectorstore.faiss_store.FastEmbedEmbeddings",
        lambda **kwargs: SimpleNamespace(**kwargs),
    )
    (tmp_path / "index.faiss").write_bytes(b"old index")
    (tmp_path / "index.pkl").write_bytes(b"old docstore")
    (tmp_path / "test_col_docs.pkl").write_bytes(b"old documents")
    (tmp_path / "test_col_config.json").write_text(
        '{"embedding_model": "modelo-antiguo"}',
        encoding="utf-8",
    )

    manager = VectorStoreManager(persist_directory=str(tmp_path), collection_name="test_col")

    assert manager.get_document_count() == 0
    assert not (tmp_path / "index.faiss").exists()
    assert not (tmp_path / "index.pkl").exists()
    assert not (tmp_path / "test_col_docs.pkl").exists()


def test_source_fingerprint_detects_document_changes(tmp_path, monkeypatch):
    """Detecta ediciones a los documentos para que el backend regenere FAISS."""
    monkeypatch.setattr(
        "vectorstore.faiss_store.FastEmbedEmbeddings",
        lambda **kwargs: SimpleNamespace(**kwargs),
    )
    manager = VectorStoreManager(persist_directory=str(tmp_path), collection_name="test_col")
    document = tmp_path / "faq.md"
    document.write_text("Contenido inicial", encoding="utf-8")
    manager._source_fingerprint = manager._fingerprint_directory(str(tmp_path))

    assert manager.has_current_sources(str(tmp_path))

    document.write_text("Contenido actualizado", encoding="utf-8")
    assert not manager.has_current_sources(str(tmp_path))


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
