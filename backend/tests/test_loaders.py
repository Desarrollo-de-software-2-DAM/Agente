"""
Pruebas de los cargadores de documentos (multi_loader) en Amershop.
Verifica que se procesen correctamente los diferentes formatos y se normalice la marca.
"""

import json
from pathlib import Path
from loaders.multi_loader import (
    load_single_document,
    load_all_documents,
    _load_markdown,
    _load_csv,
    _load_json,
    _load_html,
    _normalizar_marca
)
from langchain_core.documents import Document


def test_load_markdown(tmp_path):
    """Verifica la carga de archivos Markdown."""
    md_file = tmp_path / "test_doc.md"
    md_file.write_text("# Título de Prueba\n\nEste es un contenido de prueba.", encoding="utf-8")

    docs = _load_markdown(str(md_file))
    assert len(docs) == 1
    assert "Título de Prueba" in docs[0].page_content
    assert docs[0].metadata["source"] == "test_doc.md"


def test_load_csv(tmp_path):
    """Verifica la conversión de CSV a tabla Markdown estructurada."""
    csv_file = tmp_path / "precios.csv"
    csv_file.write_text("Zona,Costo\nLocal,15000\nNacional,30000", encoding="utf-8")

    docs = _load_csv(str(csv_file))
    assert len(docs) == 1
    assert "Local" in docs[0].page_content
    assert "15000" in docs[0].page_content


def test_load_json(tmp_path):
    """Verifica la carga y serialización legible de archivos JSON."""
    json_file = tmp_path / "tienda.json"
    data = {"tienda": "Amershop", "moneda": "COP", "iva": 0.19}
    json_file.write_text(json.dumps(data), encoding="utf-8")

    docs = _load_json(str(json_file))
    assert len(docs) == 1
    assert "Amershop" in docs[0].page_content
    assert "COP" in docs[0].page_content


def test_load_html(tmp_path):
    """Verifica la extracción de texto limpio desde archivos HTML."""
    html_file = tmp_path / "guia.html"
    html_content = "<html><body><h1>Guía de Envíos</h1><p>Envíos gratis sobre $4.000.000 COP</p></body></html>"
    html_file.write_text(html_content, encoding="utf-8")

    docs = _load_html(str(html_file))
    assert len(docs) == 1
    assert "Guía de Envíos" in docs[0].page_content
    assert "4.000.000 COP" in docs[0].page_content


def test_normalizar_marca():
    """Verifica que cualquier aparición errónea de 'AmershOp' se unifique a 'Amershop'."""
    raw_docs = [
        Document(page_content="Bienvenido a la tienda oficial de AmershOp Colombia.", metadata={}),
        Document(page_content="Políticas internas de Amershop vigentes.", metadata={})
    ]
    normalized = _normalizar_marca(raw_docs)
    assert all("AmershOp" not in d.page_content for d in normalized)
    assert normalized[0].page_content.startswith("Bienvenido a la tienda oficial de Amershop")


def test_nonexistent_or_unsupported_file(tmp_path):
    """Verifica que archivos inexistentes o no soportados devuelvan lista vacía sin romper el flujo."""
    assert load_single_document(str(tmp_path / "no_existe.pdf")) == []

    unsupported = tmp_path / "archivo.exe"
    unsupported.write_text("binario", encoding="utf-8")
    assert load_single_document(str(unsupported)) == []
