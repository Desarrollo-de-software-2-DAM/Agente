"""
Fixtures compartidas para la suite de pruebas automatizadas de Amershop.
Configura una base de datos SQLite en memoria para aislar los tests de PostgreSQL.
"""

import os
import sys
from pathlib import Path

# Añadir el directorio backend al PYTHONPATH
BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

# Configurar variables de entorno antes de importar módulos
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["LLM_PROVIDER"] = "ollama"
os.environ["OLLAMA_MODEL"] = "llama3.2"
os.environ["OLLAMA_BASE_URL"] = "http://localhost:11434"

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from langchain_core.documents import Document

from db import Base, get_db, User, Message, hash_password
from main import app
import main as main_module


@pytest.fixture(scope="session")
def test_engine():
    """Motor de base de datos SQLite en memoria."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture
def db_session(test_engine):
    """Sesión de base de datos aislada para cada test."""
    connection = test_engine.connect()
    transaction = connection.begin()
    TestingSessionLocal = sessionmaker(bind=connection, autoflush=False, expire_on_commit=False)
    session = TestingSessionLocal()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    """TestClient de FastAPI con dependencia get_db sobreescrita."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_documents():
    """Documentos de prueba para loaders y vector store."""
    return [
        Document(
            page_content="Amershop ofrece devoluciones gratuitas dentro de los primeros 30 días.",
            metadata={"source": "politica_reembolso.md", "page": 1}
        ),
        Document(
            page_content="El horario de atención es de lunes a viernes de 09:00 a 18:00 horas.",
            metadata={"source": "datos_oficiales.md", "page": 1}
        ),
        Document(
            page_content="Producto: Laptop Dell XPS 15 | Categoría: Laptops | Precio: $5.500.000",
            metadata={"source": "catalogo_productos.xlsx", "categoria": "Laptops"}
        )
    ]
