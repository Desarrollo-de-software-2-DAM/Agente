"""
Audita los documentos tal como los ve el agente (después del loader) y busca
términos que contradicen la configuración regional actual (Colombia, COP).

Colócalo en backend/scripts/ y ejecútalo dentro del contenedor:
    docker compose exec backend python scripts/auditar_datos.py
"""
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from loaders.multi_loader import load_all_documents  # noqa: E402

DOCS = Path(__file__).resolve().parent.parent / "documents"

PATRONES = {
    # (?-i:...) = distingue mayúsculas, para no confundir 'AmershOp' con 'Amershop'
    "Marca 'AmershOp' (unificar con 'Amershop')": r"(?-i:AmershOp)",
    "Notación científica en números (ej. 4e+06)": r"\d+e\+\d+",
    "IVA 16 % (Colombia: 19 %)": r"\b16\s?%",
    "Moneda USD / MXN (debe ser COP)": r"\b(USD|MXN)\b",
    "Teléfono +52 (debe ser +57)": r"\+52",
    "Pagos de México (SPEI / OXXO)": r"SPEI|OXXO",
    "Transportista mexicano (Estafeta)": r"Estafeta",
    "Referencias a México / es-MX": r"M[eé]xico|es-MX",
    "PayPal (revisar si aplica)": r"PayPal",
}


def main() -> int:
    hallazgos = defaultdict(lambda: defaultdict(int))
    docs = load_all_documents(str(DOCS))

    for d in docs:
        origen = d.metadata.get("source", "desconocido")
        for nombre, patron in PATRONES.items():
            n = len(re.findall(patron, d.page_content, flags=re.IGNORECASE))
            if n:
                hallazgos[origen][nombre] += n

    print(f"\nDocumentos analizados: {len({d.metadata.get('source') for d in docs})}")
    if not hallazgos:
        print("OK: no se encontraron términos conflictivos.")
        return 0

    print("Posibles inconsistencias encontradas:\n")
    for origen in sorted(hallazgos):
        print(f"  {origen}")
        for nombre, n in hallazgos[origen].items():
            print(f"      - {nombre}: {n}")
    print("\nRevisa cada caso: algunos pueden ser legítimos (por ejemplo, PayPal).")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())