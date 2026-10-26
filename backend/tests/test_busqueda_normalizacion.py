"""Tarjeta #13: 'portátiles' debe encontrar los Laptops del catálogo."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from loaders.multi_loader import load_all_documents
from utils.text_normalize import expand_query, keyword_search, normalize, tokenize

DOCS_DIR = Path(__file__).resolve().parent.parent / "documents"


@pytest.fixture(scope="module")
def docs():
    return load_all_documents(str(DOCS_DIR))


def test_normalize_quita_tildes_y_mayusculas():
    assert normalize("  PORTÁTILES  ") == "portatiles"


def test_plural_y_singular_coinciden():
    assert tokenize("portátiles") == tokenize("portátil")
    assert tokenize("clientes") == tokenize("cliente")


@pytest.mark.parametrize("consulta", ["portátiles", "portatiles", "PORTÁTILES", "notebooks", "computadoras portátiles"])
def test_expand_query_agrega_laptop(consulta):
    assert "laptop" in expand_query(consulta).lower()


@pytest.mark.parametrize("consulta", ["¿Qué portátiles tienen?", "portatiles", "notebooks disponibles"])
def test_portatiles_encuentra_laptops(docs, consulta):
    resultados = keyword_search(consulta, docs, k=8)
    categorias = {d.metadata.get("categoria") for d in resultados}
    assert "Laptops" in categorias


def test_catalogo_genera_ficha_por_producto(docs):
    fichas = [d for d in docs if d.page_content.startswith("Producto:")]
    assert len(fichas) == 30


def test_pdfs_sin_parrafos_redundantes(docs):
    pdfs = [d for d in docs if d.metadata.get("format") == "pdf"]
    assert pdfs and all("adicionalmente" not in d.page_content.lower() for d in pdfs)
