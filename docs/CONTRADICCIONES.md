# Registro de contradicciones de la base documental

Este documento registra inconsistencias encontradas entre los documentos de la base de conocimiento de Amershop y las decisiones indicadas por el equipo. Su objetivo es evitar que el agente utilice información contradictoria.

## Fuentes de referencia

- `backend/documents/config_tienda.json`: datos de configuración de la tienda, como contacto, horarios, políticas, moneda, medios de pago y umbral de envío gratuito.
- `backend/documents/precios_envio.csv`: tarifas y tiempos de entrega por zona y peso.
- `backend/documents/datos_oficiales.md`: resumen generado a partir de las fuentes anteriores mediante `backend/scripts/generar_datos_oficiales.py`. No debe editarse manualmente; debe regenerarse cuando cambien las fuentes.

El prompt del agente indica que `datos_oficiales.md` prevalece frente a otros documentos cuando existe una contradicción. La calidad de esta regla depende de que las fuentes originales estén actualizadas y de que el resumen se regenere después de los cambios.

## Hallazgos y decisiones registradas

| Dato | Inconsistencia identificada | Resolución registrada en el documento del proyecto |
|---|---|---|
| Envío gratuito | `config_tienda.json` contiene el valor `999`, mientras que un HTML menciona `$50 USD`. | Se toma como referencia el valor del JSON y se indica que el HTML fue corregido. |
| Costos y tiempos de envío | El HTML contenía tiempos/costos distintos a los valores por zona y peso del CSV. | Se toma el CSV como referencia y se indica que el HTML fue corregido. |
| Horario de soporte | La presentación y el FAQ contenían horarios distintos al JSON. | Se toma el JSON como referencia; el documento registra que FAQ y presentación fueron corregidos. |
| Teléfono | Se encontraron variantes con prefijos distintos. | Se registra `+57-800-AMERSHOP` como valor de referencia y se indica que FAQ y presentación fueron corregidos. |
| Texto repetido en PDF | Algunos párrafos se repetían durante la extracción. | El loader incorpora un filtro para eliminar párrafos redundantes. |

## Decisiones que requieren confirmación del equipo

Los siguientes puntos aparecen como pendientes en el registro del proyecto y no deben darse por resueltos sin confirmación:

1. **Moneda:** el registro identifica una discrepancia entre el valor de moneda de `config_tienda.json` y otros datos colombianos de la tienda. Confirmar el valor definitivo en el JSON y en los documentos de apoyo.
2. **Garantía:** se registraron diferencias entre el FAQ, la configuración y los términos y condiciones. Confirmar el alcance legal/comercial y actualizar los documentos afectados.
3. **Umbral de envío gratuito:** confirmar que el valor `999` corresponde al monto vigente y a la moneda correcta.
4. **Nombre de marca:** unificar la escritura de `Amershop` en todos los documentos.

## Procedimiento cuando cambien los datos

1. Modificar la fuente de datos correspondiente, no el archivo generado.
2. Revisar que FAQ, HTML, PDF, DOCX, PPTX y catálogo no contradigan los datos oficiales.
3. Ejecutar el generador de datos oficiales:

   ```bash
   docker compose exec backend python scripts/generar_datos_oficiales.py
   ```

4. Asegurarse de que el archivo generado actualizado se incluya en el proyecto y que el índice vectorial se regenere conforme a la configuración efectiva del `VectorStoreManager`.
5. Ejecutar las pruebas automatizadas y el script de auditoría:

   ```bash
   docker compose exec backend pytest -q
   docker compose exec backend python scripts/auditar_datos.py
   ```

> Antes de reindexar en Docker, revisar la nota sobre la discrepancia entre `FAISS_PERSIST_DIR`, la ruta predeterminada `./faiss_db/` y el volumen `faiss_data` en el README principal. No asumir que el volumen persistente contiene el índice hasta alinear esas rutas.
