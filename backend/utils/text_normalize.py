"""
Normalización de texto y expansión de consultas (tarjeta #13).

Problema que resuelve: el usuario pregunta por "portátiles" pero los documentos
dicen "Laptops". Los embeddings por defecto (FastEmbed, modelo en inglés) no
relacionan ambos términos de forma fiable, así que normalizamos (tildes,
mayúsculas, plurales) y expandimos la consulta con sinónimos del dominio.
"""

import math
import re
import unicodedata
from collections import Counter
from typing import Dict, Iterable, List

from langchain_core.documents import Document

# Grupos de sinónimos del dominio (se escriben de forma natural; se normalizan al cargar).
SYNONYM_GROUPS: List[List[str]] = [
    ["laptop", "portátil", "notebook", "computadora portátil", "ordenador portátil", "computador portátil"],
    ["smartphone", "celular", "móvil", "teléfono", "teléfono inteligente"],
    ["tablet", "tableta"],
    ["audífonos", "auriculares", "headphones", "cascos", "earbuds"],
    ["bocina", "altavoz", "parlante", "speaker"],
    ["mouse", "ratón"],
    ["monitor", "pantalla"],
    ["envío", "entrega", "despacho", "paquetería"],
    ["devolución", "reembolso", "reintegro"],
    ["garantía", "cobertura de garantía"],
    ["factura", "comprobante fiscal"],
]

# Alias que se escriben en el texto indexado de cada categoría del catálogo.
CATEGORY_ALIASES: Dict[str, List[str]] = {
    "Laptops": ["portátiles", "notebooks", "computadoras portátiles", "ordenadores portátiles"],
    "Smartphones": ["celulares", "móviles", "teléfonos"],
    "Tablets": ["tabletas"],
    "Audio": ["audífonos", "bocinas", "sonido"],
    "Gaming": ["videojuegos", "gamer"],
    "Accesorios": ["periféricos", "complementos"],
}

STOPWORDS = {
    "de", "la", "el", "los", "las", "un", "una", "unos", "unas", "y", "o", "en", "a", "que",
    "es", "son", "con", "por", "para", "del", "al", "se", "su", "sus", "mi", "me", "tienen",
    "tiene", "hay", "cual", "cuales", "como", "cuanto", "cuantos", "qué", "que", "quiero",
}


def strip_accents(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn")


def normalize(text: str) -> str:
    """Minúsculas, sin tildes y con espacios colapsados."""
    return re.sub(r"\s+", " ", strip_accents(text).lower()).strip()


def stem(word: str) -> str:
    """Singularización ligera para español (portatiles→portatil, clientes→cliente)."""
    if len(word) > 4 and word.endswith("es") and word[-3] in "lrnzd":
        return word[:-2]
    if len(word) > 3 and word.endswith("s"):
        return word[:-1]
    return word


def tokenize(text: str) -> List[str]:
    """Tokens normalizados y singularizados, sin stopwords."""
    tokens = re.findall(r"[a-z0-9]+", normalize(text))
    return [stem(t) for t in tokens if t not in {normalize(s) for s in STOPWORDS} and len(t) > 1]


def _build_synonym_index() -> Dict[str, List[str]]:
    index: Dict[str, List[str]] = {}
    for group in SYNONYM_GROUPS:
        terms = [normalize(t) for t in group]
        for term in terms:
            for tok in term.split():
                if len(term.split()) == 1:  # solo términos de una palabra son clave de búsqueda
                    index[stem(tok)] = terms
    return index


_SYNONYM_INDEX = _build_synonym_index()


def expand_query(query: str) -> str:
    """Añade sinónimos del dominio a la consulta. 'portátiles' → '... laptop notebook ...'."""
    extras: List[str] = []
    for tok in tokenize(query):
        for term in _SYNONYM_INDEX.get(tok, []):
            if term not in extras and stem(term) != tok:
                extras.append(term)
    return f"{query} {' '.join(extras)}".strip() if extras else query


def keyword_search(query: str, documents: Iterable[Document], k: int = 5) -> List[Document]:
    """Búsqueda léxica (TF-IDF simple) sobre texto normalizado. Complementa a la vectorial."""
    docs = list(documents)
    if not docs:
        return []
    q_tokens = set(tokenize(expand_query(query)))
    if not q_tokens:
        return []

    doc_tokens = [Counter(tokenize(d.page_content)) for d in docs]
    n = len(docs)
    df = Counter(t for c in doc_tokens for t in c)

    scored = []
    for doc, counts in zip(docs, doc_tokens):
        score = sum(
            (1 + math.log(counts[t])) * math.log(1 + n / df[t])
            for t in q_tokens if counts.get(t)
        )
        if score > 0:
            scored.append((score, doc))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [d for _, d in scored[:k]]
