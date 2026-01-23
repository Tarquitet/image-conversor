# 🚀 OMEGA Image Converter (v0.15)

> **Una suite profesional de escritorio para inspección, optimización, edición no destructiva y conversión masiva de imágenes.**

El **OMEGA Image Converter** es una herramienta GUI avanzada escrita en Python. Está diseñada para creadores de contenido, desarrolladores web y diseñadores que necesitan un control granular sobre la compresión de sus imágenes, soportando desde formatos estándar hasta formatos de última generación como AVIF y HEIC.

## ✨ Características Principales

- **🔍 Inspector Visual Avanzado (Modo Cortina):** Compara el original y el resultado píxel por píxel con un efecto cortina, zoom dinámico (rueda del mouse) y desplazamiento (clic y arrastrar).
- **💾 Sistema de Presets:** Guarda tus configuraciones favoritas (formato, escala, calidad, marca de agua) en un archivo `presets.json` para reutilizarlas con un solo clic.
- **⚡ Procesamiento por Lotes:** Aplica configuraciones globalmente a cientos de imágenes o de forma granular (una por una) y expórtalas en segundos.
- **🛠️ Edición Rápida No Destructiva:** Rota, voltea y convierte a Blanco/Negro con un solo clic antes de exportar.
- **©️ Marca de Agua y Renombrado:** Agrega texto con opacidad personalizada y prefijos a los nombres de los archivos exportados.
- **📦 Optimización Extrema:** Soporte para Subsampling (Chroma 4:2:0) para reducir drásticamente el peso de la imagen y opción para mantener o eliminar metadatos EXIF.

## 🗂️ Formatos Soportados

| Formatos Web Modernos       | Formatos Clásicos       | Formatos de Diseño   |
| :-------------------------- | :---------------------- | :------------------- |
| **AVIF** (Ultra compresión) | **JPEG / JPG**          | **PSD** (Photoshop)  |
| **HEIC** (Apple/iOS)        | **PNG** (Transparencia) | **PDF** (Documento)  |
| **WEBP** (Google)           | **GIF** (Animado)       | **EPS** (PostScript) |
| **JPEG 2000**               | **BMP / ICO**           | **TIFF / TGA**       |

---

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
python 9_escalas_presets_modos.py
```

## 📖 Guía de Uso Rápida

1. **Agregar:** Haz clic en `➕ Agregar` y selecciona las imágenes.
2. **Configurar:** Selecciona una imagen de la lista y ajusta su formato, calidad y escala. Si deseas aplicar esto a todo el lote, usa el botón `⚡ APLICAR GLOBAL`.
3. **Inspeccionar:** Haz clic sobre la imagen de "Vista Previa" para abrir el **Inspector Omega**. Desliza el mouse para ver la diferencia de calidad y peso antes de guardar.
4. **Marca de Agua (Opcional):** Ve a la pestaña "Marca & Salida" para configurar tu marca de agua y prefijo de renombrado.
5. **Exportar:** Elige tu carpeta de salida y presiona `🚀 PROCESAR LOTE`.

---

## 📈 Evolución del Proyecto (Changelog)

- **v1-v3:** Soporte inicial de formatos (AVIF/HEIC) y mejora de la interfaz gráfica con colas de archivos.
- **v4-v5:** Introducción de configuraciones granulares (individual vs global) e inspector de imágenes grandes con scroll sincronizado.
- **v6-v8:** Implementación del Inspector con Zoom y efecto cortina, subsampling 4:2:0, prefijos y marcas de agua.
- **v9 (Actual):** Consolidación final "OMEGA". Edición no destructiva (rotación/espejo/BN), integración del sistema de Presets JSON y optimización del flujo de trabajo por lotes.

---

### 💡 Consejos

- Si notas que el archivo pesa demasiado para web, activa el **Modo Ahorro (4:2:0)** en la pestaña de edición.
- Para grandes lotes de imágenes, prueba primero con 1 o 2 imágenes usando el Inspector para asegurar que la compresión no degrade detalles importantes.
