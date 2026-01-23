# 🚀 OMEGA Image Converter (v0.15)

> **Una suite profesional de escritorio para inspección, optimización multihilo, edición no destructiva y conversión masiva de imágenes.**

El **OMEGA Image Converter** es una herramienta GUI avanzada escrita en Python. Está diseñada para creadores de contenido, desarrolladores web y diseñadores que necesitan un control granular sobre la compresión de sus imágenes, soportando desde formatos estándar hasta formatos de última generación como AVIF y HEIC.

## ✨ Características Principales (Actualizado v15)

- **📏 Redimensionado Exacto por Píxeles:** Control total sobre el tamaño final. Cambia las dimensiones especificando el Ancho (Width) y Alto (Height) exactos en píxeles, abandonando el antiguo método por porcentajes.
- **🚀 Procesamiento Multihilo (Multi-core):** Aprovecha todos los núcleos de tu procesador para convertir lotes gigantes de imágenes a una velocidad optimizada.
- **🔍 Inspector Visual Avanzado (Modo Cortina):** Compara el original y el resultado píxel por píxel con un efecto cortina, zoom dinámico y analítica de datos completos al hacer clic.
- **🧹 Gestión de Lista Avanzada:** Elimina imágenes específicas de la cola de trabajo de forma individual con un solo clic.
- **💾 Sistema de Presets:** Guarda tus configuraciones favoritas en un archivo `presets.json` para reutilizarlas instantáneamente.
- **©️ Inserción de Logos y Marcas de Agua:** Agrega logos PNG o texto con opacidad personalizada a tus exportaciones.
- **📦 Optimización Extrema:** Soporte para Subsampling (Chroma 4:2:0) para reducir drásticamente el peso de la imagen y reportes visuales del porcentaje exacto de peso ahorrado.

## 🗂️ Formatos Soportados

| Formatos Web Modernos       | Formatos Clásicos       | Formatos de Diseño   |
| :-------------------------- | :---------------------- | :------------------- |
| **AVIF** (Ultra compresión) | **JPEG / JPG**          | **PSD** (Photoshop)  |
| **HEIC** (Apple/iOS)        | **PNG** (Transparencia) | **PDF** (Documento)  |
| **WEBP** (Google)           | **GIF** (Animado)       | **EPS** (PostScript) |
| **JPEG 2000**               | **BMP / ICO**           | **TIFF / TGA**       |

## ⚙️ Requisitos e Instalación

El script cuenta con un **Auto-Instalador**. Al ejecutarlo por primera vez, intentará descargar automáticamente las dependencias necesarias.

**Requisitos del sistema:**

- Python 3.8 o superior.

**Dependencias (instaladas automáticamente):**

- `ttkbootstrap` (Interfaz gráfica moderna)
- `Pillow` (Procesamiento de imagen base)
- `pillow-avif-plugin` (Soporte AVIF)
- `pillow-heif` (Soporte HEIC)

### Ejecución

```bash
python 15_better_ux_change_percent_2_px.py
```

## 📖 Guía de Uso Rápida

1. **Agregar y Limpiar:** Haz clic en `➕ Agregar` para seleccionar imágenes. Si te equivocas con alguna, usa la `❌` individual para quitarla de la lista.
2. **Configurar Dimensiones y Calidad:** Selecciona una imagen y ajusta su nuevo ancho/alto en píxeles. Si deseas aplicar esto a todo el lote, usa `⚡ APLICAR GLOBAL`.
3. **Inspeccionar Ahorro:** Revisa la barra de información para ver el porcentaje exacto de peso ahorrado. Haz clic en la "Vista Previa" para abrir el **Inspector Omega** a pantalla completa.
4. **Exportación Multihilo:** Elige tu carpeta de salida y presiona `🚀 PROCESAR LOTE`. El motor multihilo procesará las imágenes en paralelo.

## 📈 Evolución del Proyecto (Changelog)

- **v1-v5:** Soporte inicial de formatos (AVIF/HEIC), mejora de la GUI e inspector de imágenes grandes.
- **v6-v9:** Implementación del Inspector con Zoom, efecto cortina, presets JSON y edición no destructiva.
- **v10:** Soporte para colores web y superposición de logos PNG.
- **v11:** Mejora en la visualización de datos de compresión (porcentaje ahorrado).
- **v12:** Integración del motor de procesamiento Multicore (Multihilo) para optimización de velocidad.
- **v13-v14:** Mejoras de UX para permitir el cierre/eliminación de imágenes individuales de la lista.
- **v15 (Actual):** Refactorización de la escala: Transición del redimensionamiento porcentual al control exacto por dimensiones en Píxeles (Ancho x Alto).

### 💡 Consejos

- **Aprovecha el Multihilo:** Para carpetas con cientos de fotos (ej. galerías de eventos o e-commerce), la versión 15 reducirá tu tiempo de espera drásticamente en comparación con las versiones anteriores.
- **Web Core Vitals:** Si optimizas para web, exporta en **AVIF** con **Modo Ahorro (4:2:0)** para obtener las mejores puntuaciones en Google PageSpeed.
