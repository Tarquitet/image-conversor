# Image Conversor — carpeta `image-conversor`

Descripción

- Conjunto de utilidades GUI para inspección, redimensionado, conversión y exportación de imágenes. La versión más reciente incluye un inspector visual con zoom/cortina, presets guardables (`presets.json`) y procesamiento por lotes.

Características (basadas en `9_escalas_presets_modos.py`)

- Inspector avanzado que muestra comparación lado a lado (original vs procesado) con control deslizante y zoom.
- Soporte para formatos modernos (`AVIF`, `HEIC`) y plugins (`pillow-avif-plugin`, `pillow-heif`).
- Presets guardables en `presets.json` y aplicación de presets a items seleccionados.
- Controles de calidad, escala, subsampling, convertir a B/N, rotación/flip, marca de agua y renombrado por prefijo.
- Batch processing con selección de carpeta de salida y guardado optimizado (calidad y conversión automática).

Requisitos

- Python 3.8+
- Paquetes: `ttkbootstrap`, `Pillow`, `pillow-avif-plugin`, `pillow-heif` (el script intenta instalarlos si faltan).

Uso

- Ejecutar la versión más reciente (ejemplo):

```bash
python dev/scripts/image-conversor/<latest_num>_<fixed_name>.py
```

Flujo típico

1. `➕ Agregar` — seleccionar archivos a procesar.
2. Ajustar formato, calidad y escala; usar `Guardar Preset` si quieres reutilizar.
3. `PROCESAR LOTE` — genera los archivos convertidos en la carpeta de salida.
4. `Inspector` — abrir vista comparativa para asegurar cambios antes de exportar.

Evolución (resumen)

- V1..V3: Soporte básico de formatos y UI mejorada.
- Versiones intermedias: soporte PSD/EPS, mejoras en UX para porcentaje vs pixeles, y modo inspector.
- V9: `9_escalas_presets_modos.py` — implementación de inspector, presets, soporte HEIF/AVIF y optimizaciones de lote.

Consejos

- Si trabajas con AVIF/HEIC asegúrate de tener los plugins `pillow-avif-plugin` y `pillow-heif` instalados.
- Para grandes lotes, prueba primero con 1-2 imágenes y revisa `presets.json`.
