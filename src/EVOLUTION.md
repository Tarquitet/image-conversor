# Evolución detallada — `image-conversor` (carpeta)

Hitos principales

- Implementación de inspector visual (comparativa original vs procesado) con zoom y cortina para inspección fina.
- Añadido soporte para formatos modernos (`AVIF`, `HEIC`) mediante `pillow-avif-plugin` y `pillow-heif`.
- Presets: `presets.json` permite guardar y reusar configuraciones (formato, calidad, escala, watermark).
- Batch processing optimizado: operaciones no destructivas, generación por prefijo y opciones de renombrado.

Detalles técnicos

- `ImageItem` define metadatos por imagen (formato objetivo, calidad, escala, flags de transformación, metadatos e watermark).
- Inspector y procesamiento usan `Pillow` y plugins para formatos; se implementaron transformaciones como rotación, flip, grayscale y redimensionado con `Image.Resampling`.

Mejoras futuras

- Incorporar procesamiento multihilo/colamanejo para grandes lotes (hay intentos en archivos numerados `12_multicore-attemp-for-optispeed.py`).
- Extraer utilidades comunes a un módulo para mantener DRY entre versiones.
