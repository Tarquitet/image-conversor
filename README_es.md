# 🚀 OMEGA Image Converter (v0.17)

> **Una suite profesional de escritorio para inspección, optimización multihilo, edición no destructiva y conversión masiva de imágenes.**

El **OMEGA Image Converter** es una herramienta GUI avanzada escrita en Python. Está diseñada para creadores de contenido, desarrolladores web y diseñadores que necesitan un control granular sobre la compresión de sus imágenes, soportando desde formatos estándar hasta formatos de última generación como AVIF y HEIC.

![1770839881735 a](images/README/1770839881735.png)

![1769207328325 b](images/README/1769207328325.avif)

![1769206967488 c](images/README/1769206967488.avif)

![1769206951282 d](images/README/1769206951282.avif)

## ✨ Características Principales (Actualizado v17)

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
python Latest_<NAME>_<VERSION>.py
```

## 📖 Guía de Uso Rápida

1. **Agregar y Limpiar:** Haz clic en `➕ Agregar` para seleccionar imágenes. Si te equivocas con alguna, usa la `❌` individual para quitarla de la lista.
2. **Configurar Dimensiones y Calidad:** Selecciona una imagen y ajusta su nuevo ancho/alto en píxeles. Si deseas aplicar esto a todo el lote, usa `⚡ APLICAR GLOBAL`.
3. **Inspeccionar Ahorro:** Revisa la barra de información para ver el porcentaje exacto de peso ahorrado. Haz clic en la "Vista Previa" para abrir el **Inspector Omega** a pantalla completa.
4. **Exportación Multihilo:** Elige tu carpeta de salida y presiona `🚀 PROCESAR LOTE`. El motor multihilo procesará las imágenes en paralelo.

## 📈 Evolución del Proyecto (Changelog)

- **v1–v5:** Soporte inicial de formatos, interfaz básica y capacidades de conversión.
- **v6–v9:** Implementación del Inspector con zoom y efecto cortina, presets en `presets.json` y edición no destructiva.
- **v10:** Soporte mejorado para colores web y capacidad de superponer logos PNG.
- **v11:** Visualización avanzada de métricas de compresión (porcentaje de ahorro) en la interfaz.
- **v12:** Integración del motor Multicore para procesamiento paralelo y mayor velocidad en lotes.
- **v13–v14:** Mejoras de UX para permitir cerrar y eliminar imágenes individuales de la cola de trabajo.
- **v15:** Cambio del sistema de escalado: paso del redimensionado por porcentaje a control exacto por píxeles (Ancho × Alto).
- **v16:** Correcciones y mejoras en soporte de PNG y SVG; mejoras en el manejo de transparencias y reducción de artefactos en exportaciones.
- **v17 (Actual):** Corrección de problemas de transparencia en WebP/AVIF, robustecimiento del pipeline de exportación y mejoras menores de estabilidad.

### 💡 Consejos

- **Aprovecha el Multihilo:** Para carpetas con cientos de fotos, la versión 15 reducirá tu tiempo de espera drásticamente.
- **Web Core Vitals:** Para web, exporta en **AVIF** con **Modo Ahorro (4:2:0)** para mejores puntuaciones en PageSpeed.

## ⚖️ Créditos y Licencias

Este proyecto usa librerías de código abierto como `Pillow`, `ttkbootstrap`, `pillow-heif` y `pillow-avif-plugin`.

[![Read in English](https://img.shields.io/badge/Read%20in%20English-EN-blue?style=flat-square&logo=github)](README.md)
