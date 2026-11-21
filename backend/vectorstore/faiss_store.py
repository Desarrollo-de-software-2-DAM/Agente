"""
Gestor de la base de datos vectorial FAISS para el proyecto AmershOp.
Maneja la indexación, búsqueda y administración de documentos.
"""

import os
import logging
import pickle
import json
import hashlib
from typing import List, Optional
from pathlib import Path

from langchain_core.documents import Document
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    COLLECTION_NAME,
    EMBEDDING_MODEL,
    FAISS_PERSIST_DIR,
    SUPPORTED_EXTENSIONS,
)
from utils.text_normalize import expand_query, keyword_search, normalize, tokenize

# Configuración del registro de eventos (logging)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def _is_store_contact_phone_query(query: str) -> bool:
    tokens = set(tokenize(query))
    device_terms = {
        "celular", "smartphone", "movil", "modelo", "producto", "comprar",
        "precio", "disponible", "venden", "catalogo",
    }
    return "telefono" in tokens and not tokens.intersection(device_terms)


class VectorStoreManager:
    """
    Gestor de la base de datos vectorial para el proyecto AmershOp.
    Usa FAISS para almacenamiento y búsqueda vectorial con persistencia en disco.
    """

    def __init__(
        self,
        persist_directory: str = FAISS_PERSIST_DIR,
        collection_name: str = COLLECTION_NAME,
    ):
        """
        Inicializa el gestor de la base de datos vectorial.

        Args:
            persist_directory (str): Directorio donde se persistirá la base de datos.
            collection_name (str): Nombre de la colección (usado para el archivo).
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.index_path = os.path.join(persist_directory, "index.faiss")
        self.docs_path = os.path.join(persist_directory, f"{collection_name}_docs.pkl")
        self.store_config_path = os.path.join(
            persist_directory, f"{collection_name}_config.json"
        )
        self._store_config = {
            "schema_version": 1,
            "embedding_model": EMBEDDING_MODEL,
            "chunk_size": CHUNK_SIZE,
            "chunk_overlap": CHUNK_OVERLAP,
        }
        self._source_fingerprint: Optional[str] = None

        try:
            self.embeddings = FastEmbedEmbeddings(model_name=EMBEDDING_MODEL)

            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=CHUNK_SIZE,
                chunk_overlap=CHUNK_OVERLAP,
            )

            # Crear directorio de persistencia si no existe
            os.makedirs(persist_directory, exist_ok=True)

            # Intentar cargar un índice existente
            self.vector_store = None
            self._all_documents: List[Document] = []
            self._load_existing()

            logger.info(f"VectorStoreManager inicializado correctamente en {self.persist_directory}")

        except Exception as e:
            logger.error(f"Error al inicializar VectorStoreManager: {e}")
            raise

    def _load_existing(self):
        """Intenta cargar un índice FAISS existente desde disco."""
        try:
            index_file = Path(self.index_path)
            faiss_docstore_path = Path(self.persist_directory) / "index.pkl"
            has_persisted_files = any(
                path.exists()
                for path in (
                    index_file,
                    faiss_docstore_path,
                    Path(self.docs_path),
                    Path(self.store_config_path),
                )
            )
            if not has_persisted_files:
                return

            try:
                with open(self.store_config_path, "r", encoding="utf-8") as file:
                    manifest = json.load(file)
            except (OSError, json.JSONDecodeError):
                manifest = None

            if not isinstance(manifest, dict) or manifest.get("settings") != self._store_config:
                self._discard_persisted_store(
                    "El índice no tiene metadatos compatibles o cambió su configuración."
                )
                return

            self._source_fingerprint = manifest.get("source_fingerprint")

            if not index_file.exists() and not faiss_docstore_path.exists():
                if os.path.exists(self.docs_path):
                    with open(self.docs_path, "rb") as file:
                        self._all_documents = pickle.load(file)
                    if not self._all_documents and self._source_fingerprint is not None:
                        return
                self._discard_persisted_store("El índice FAISS está incompleto.")
                return

            if not index_file.exists() or not faiss_docstore_path.exists():
                self._discard_persisted_store("El índice FAISS está incompleto.")
                return

            from langchain_community.vectorstores import FAISS
            self.vector_store = FAISS.load_local(
                self.persist_directory,
                self.embeddings,
                allow_dangerous_deserialization=True
            )
            logger.info("Índice FAISS cargado desde disco.")

            # Cargar documentos guardados
            if os.path.exists(self.docs_path):
                with open(self.docs_path, 'rb') as f:
                    self._all_documents = pickle.load(f)
                logger.info(f"Se cargaron {len(self._all_documents)} documentos desde disco.")
            else:
                self._discard_persisted_store(
                    "Falta la copia de documentos usada por la búsqueda léxica."
                )

        except Exception as e:
            logger.warning(f"No se pudo cargar índice existente: {e}")
            self.vector_store = None
            self._all_documents = []
            self._source_fingerprint = None

    def _discard_persisted_store(self, reason: str) -> None:
        """Descarta solo los archivos de este índice para permitir reconstruirlo."""
        logger.info("%s Se reconstruirá desde los documentos fuente.", reason)
        for path in (
            Path(self.index_path),
            Path(self.persist_directory) / "index.pkl",
            Path(self.docs_path),
            Path(self.store_config_path),
        ):
            try:
                path.unlink(missing_ok=True)
            except OSError as exc:
                logger.error("No se pudo eliminar %s: %s", path, exc)
                raise
        self.vector_store = None
        self._all_documents = []
        self._source_fingerprint = None

    def _save(self):
        """Guarda el índice FAISS y documentos a disco."""
        try:
            if self.vector_store is not None:
                self.vector_store.save_local(self.persist_directory)
                logger.info("Índice FAISS guardado en disco.")

            with open(self.docs_path, 'wb') as f:
                pickle.dump(self._all_documents, f)

            with open(self.store_config_path, "w", encoding="utf-8") as file:
                json.dump(
                    {
                        "settings": self._store_config,
                        "source_fingerprint": self._source_fingerprint,
                    },
                    file,
                    ensure_ascii=False,
                    indent=2,
                )

        except Exception as e:
            logger.error(f"Error al guardar la base de datos: {e}")

    def index_documents(self, documents: List[Document]) -> int:
        """
        Divide e indexa una lista de documentos en la base de datos vectorial.

        Args:
            documents (List[Document]): Lista de documentos a indexar.

        Returns:
            int: Número de fragmentos (chunks) indexados.
        """
        try:
            from langchain_community.vectorstores import FAISS

            if not documents:
                logger.warning("No se proporcionaron documentos para indexar.")
                return 0

            logger.info(f"Dividiendo {len(documents)} documentos...")
            chunks = self.text_splitter.split_documents(documents)

            if not chunks:
                return 0

            logger.info(f"Indexando {len(chunks)} fragmentos en FAISS...")

            if self.vector_store is None:
                # Crear nuevo índice
                self.vector_store = FAISS.from_documents(chunks, self.embeddings)
            else:
                # Agregar al índice existente
                self.vector_store.add_documents(chunks)

            self._all_documents.extend(chunks)
            self._save()

            logger.info("Documentos indexados y guardados correctamente.")
            return len(chunks)

        except Exception as e:
            logger.error(f"Error al indexar documentos: {e}")
            return 0

    def search(self, query: str, k: int = 5) -> List[Document]:
        """
        Búsqueda híbrida: vectorial (MMR) + léxica (palabras clave normalizadas),
        con la consulta expandida con sinónimos ('portátiles' → laptop, notebook...).
        Los resultados se fusionan con Reciprocal Rank Fusion.
        """
        try:
            if self.vector_store is None:
                logger.warning("No hay documentos indexados para buscar.")
                return []

            expanded = expand_query(query)
            logger.info(f"Búsqueda híbrida: '{query}' -> '{expanded}'")

            vector_hits = self.vector_store.max_marginal_relevance_search(
                expanded, k=k, fetch_k=max(20, k * 4)
            )
            keyword_hits = keyword_search(query, self._all_documents, k=k)

            fused: dict = {}
            for hits in (vector_hits, keyword_hits):
                for rank, doc in enumerate(hits):
                    key = (doc.metadata.get("source"), doc.metadata.get("page"), doc.page_content)
                    entry = fused.setdefault(key, [0.0, doc])
                    entry[0] += 1.0 / (60 + rank)
            ranked = sorted(fused.values(), key=lambda e: e[0], reverse=True)
            results = [doc for _, doc in ranked]

            if _is_store_contact_phone_query(query):
                official_contact = next(
                    (
                        doc for doc in self._all_documents
                        if doc.metadata.get("source") == "datos_oficiales.md"
                        and "telefono:" in normalize(doc.page_content)
                    ),
                    None,
                )
                if official_contact is not None:
                    results = [official_contact] + [
                        doc for doc in results if doc is not official_contact
                    ]

            return results[:k]
        except Exception as e:
            logger.error(f"Error al realizar la búsqueda: {e}")
            return []

    def get_document_count(self) -> int:
        """
        Obtiene el número total de fragmentos (chunks) indexados.

        Returns:
            int: Número total de fragmentos.
        """
        return len(self._all_documents)

    def get_indexed_sources(self) -> List[str]:
        """
        Obtiene una lista de las fuentes (nombres de archivo) únicas indexadas.

        Returns:
            List[str]: Lista de fuentes únicas.
        """
        sources = set()
        for doc in self._all_documents:
            if doc.metadata and "source" in doc.metadata:
                sources.add(doc.metadata["source"])
        return list(sources)

    def clear_store(self):
        """Elimina todos los documentos indexados."""
        try:
            logger.info("Limpiando la base de datos vectorial...")
            self.vector_store = None
            self._all_documents = []
            self._source_fingerprint = None

            for path in (
                Path(self.index_path),
                Path(self.persist_directory) / "index.pkl",
                Path(self.docs_path),
                Path(self.store_config_path),
            ):
                path.unlink(missing_ok=True)

            logger.info("Base de datos vectorial limpiada correctamente.")
        except Exception as e:
            logger.error(f"Error al limpiar la base de datos vectorial: {e}")

    @staticmethod
    def _fingerprint_directory(directory: str) -> str:
        """Calcula una huella estable del contenido de los documentos indexables."""
        root = Path(directory)
        digest = hashlib.sha256()
        files = sorted(
            (
                path for path in root.rglob("*")
                if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
            ),
            key=lambda path: path.relative_to(root).as_posix(),
        )
        for path in files:
            digest.update(path.relative_to(root).as_posix().encode("utf-8"))
            with path.open("rb") as file:
                for block in iter(lambda: file.read(65536), b""):
                    digest.update(block)
        return digest.hexdigest()

    def has_current_sources(self, directory: str) -> bool:
        """Indica si el índice corresponde al contenido actual de los documentos."""
        if self._source_fingerprint is None or not os.path.isdir(directory):
            return False
        return self._source_fingerprint == self._fingerprint_directory(directory)

    def reindex_from_directory(self, directory: str) -> int:
        """
        Limpia la base de datos actual y reindexa todos los documentos de un directorio.

        Args:
            directory (str): Ruta del directorio a indexar.

        Returns:
            int: Número de fragmentos indexados.
        """
        try:
            from loaders.multi_loader import load_all_documents

            if not os.path.isdir(directory):
                logger.error(f"El directorio proporcionado no existe: {directory}")
                return 0

            # Limpiar la base de datos
            self.clear_store()

            logger.info(f"Cargando documentos desde el directorio: {directory}")
            documents = load_all_documents(directory)

            if not documents:
                logger.warning("No se encontraron documentos en el directorio especificado.")
                self._source_fingerprint = self._fingerprint_directory(directory)
                self._save()
                return 0

            self._source_fingerprint = self._fingerprint_directory(directory)
            return self.index_documents(documents)

        except Exception as e:
            logger.error(f"Error al reindexar desde el directorio: {e}")
            return 0
