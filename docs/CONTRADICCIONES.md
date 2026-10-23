# Tarjeta #12 — Datos contradictorios: hallazgos y decisión

Fuentes únicas de verdad: `config_tienda.json` (contacto, horarios, políticas, envío gratis)
y `precios_envio.csv` (tarifas y tiempos). `documents/datos_oficiales.md` se **genera** de ambas
con `python scripts/generar_datos_oficiales.py` y prevalece ante cualquier conflicto.

| Dato | Conflicto | Resolución |
|---|---|---|
| Envío gratis | JSON `999` vs HTML `$50 USD` | **$999** (JSON). HTML corregido |
| Tiempos/costos de envío | HTML (1-2, 3-5 días, "mismo día") vs CSV (2-8 días por zona/peso) | CSV. HTML corregido (zonas Local / Nacional cercano / lejano) |
| Soporte | PPTX "24/7" vs FAQ L-V 9-18 vs JSON L-V + Sáb 10-14 | JSON. PPTX y FAQ corregidos |
| Teléfono | `800-AMERSHOP` vs `+52-800-AMERSHOP` | `+52-800-AMERSHOP`. FAQ y PPTX corregidos |
| Texto duplicado en PDFs | Párrafos "Adicionalmente, ..." repiten cada sección | Filtrados en el loader (`_strip_redundant_paragraphs`) |

## Pendientes que requieren decisión del negocio
1. **Moneda**: el JSON dice USD, pero precios del catálogo (laptop $25,999), IVA 16%, SPEI y OXXO apuntan a pesos mexicanos. El agente tiene prohibido convertir divisas.
2. **Garantía**: FAQ dice "todos los productos" y JSON 365 días; los Términos (PDF) dicen "la mayoría". Hay que regenerar el PDF.
3. **Umbral $999**: confirmar que es el valor vigente (el HTML decía $50).
4. **Nombre de marca**: "AmershOp" (documentos) vs "Amershop" (prompt, README).
