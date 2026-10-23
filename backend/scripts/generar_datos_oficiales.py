"""
Genera documents/datos_oficiales.md a partir de las fuentes únicas de verdad:
  - documents/config_tienda.json   -> contacto, horarios, umbral de envío gratis, políticas
  - documents/precios_envio.csv    -> tarifas y tiempos de envío por zona y peso

Uso:  python scripts/generar_datos_oficiales.py
Ejecútalo cada vez que cambies alguno de esos dos archivos y reindexa (borra chroma_db/).
"""
import json
from pathlib import Path

import pandas as pd

DOCS = Path(__file__).resolve().parent.parent / "documents"


def generar() -> str:
    cfg = json.loads((DOCS / "config_tienda.json").read_text(encoding="utf-8"))
    envios = pd.read_csv(DOCS / "precios_envio.csv")
    t, reg, env, pol = cfg["tienda"], cfg["configuracion_regional"], cfg["configuracion_envios"], cfg["politicas"]
    m = reg["moneda"]

    zonas = []
    for zona, g in envios.groupby("Zona", sort=False):
        zonas.append(f"### Zona {zona.replace('_', ' ')}\n")
        zonas.append("| Peso (kg) | Estándar (USD) | Express (USD) | Días estándar | Días express |")
        zonas.append("|---|---|---|---|---|")
        for _, r in g.iterrows():
            zonas.append(
                f"| {r.Peso_Min_kg:g} - {r.Peso_Max_kg:g} | ${r.Costo_Estandar:g} | ${r.Costo_Express:g} "
                f"| {r.Tiempo_Estandar_Dias} | {r.Tiempo_Express_Dias} |"
            )
        zonas.append("")

    return f"""# Datos oficiales de {t['nombre']} (fuente de verdad)

> Si otro documento contradice estos valores, **prevalecen los de este documento**.

## Contacto y horarios
- Sitio web: {t['url']}
- Correo de contacto: {t['email_contacto']}
- Teléfono: {t['telefono']}
- Horario de atención: {t['horario_atencion']}

## Moneda e impuestos
- Moneda: {m}. IVA: {reg['impuesto_iva_porcentaje']}%.

## Pagos aceptados
{chr(10).join('- ' + p for p in cfg['pagos_aceptados'])}

## Envíos
- Envío estándar GRATIS en compras superiores a ${env['umbral_envio_gratis']:g} {m}.
- Transportistas: {', '.join(env['transportistas_activos'])}.
- Los tiempos de entrega están en días hábiles y dependen de la zona y del peso del paquete.

{chr(10).join(zonas)}
## Devoluciones y garantía
- Plazo de devolución: {pol['dias_limite_devolucion']} días naturales desde la recepción.
- Garantía base: {pol['dias_garantia_base']} días (1 año) contra defectos de fabricación.
- Tarifa por devolución por cambio de opinión: ${pol['costo_reestocaje_devolucion']:g} {m}.
"""


if __name__ == "__main__":
    out = DOCS / "datos_oficiales.md"
    out.write_text(generar(), encoding="utf-8")
    print(f"Generado {out}")
