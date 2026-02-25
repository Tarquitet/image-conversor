# 🚀 OMEGA Image Converter (v0.15)

> **A professional suite for inspection, multithreaded optimization, non-destructive edits and bulk image conversion.**

OMEGA Image Converter is an advanced desktop tool written in Python for creators who need fine-grained control over image compression and conversion (including modern formats like AVIF and HEIC).

![1770839881735 a](images/README/1770839881735.png)

## ✨ Main Features (v15)

- **Exact Pixel Resizing:** Control final dimensions by exact pixels (width × height).
- **Multithreaded Processing:** Uses all CPU cores for fast batch conversion.
- **Advanced Visual Inspector:** Side-by-side comparison with curtain effect and pixel-level zoom.
- **Presets System:** Save export settings in `presets.json`.
- **Watermark/Logo Insertion:** Add PNG logos or text with opacity control.
- **Extreme Optimization:** Supports chroma subsampling (4:2:0) to reduce weight for web.

## Supported Formats

- AVIF, HEIC, WEBP, JPEG/JPG, PNG, GIF, PSD, PDF, EPS, TIFF, BMP, ICO, JPEG2000

---

## ⚙️ Requirements & Installation

- Python 3.8 or newer.

The tool includes an auto-installer that will fetch required packages on first run.

**Dependencies:** `ttkbootstrap`, `Pillow`, `pillow-avif-plugin`, `pillow-heif`.

Run:

```bash
python Latest_<NAME>_<VERSION>.py
```

[![Leer en Español](https://img.shields.io/badge/Leer%20en%20Espa%C3%B1ol-ES-blue?style=flat-square&logo=github)](README_es.md)

## Quick Usage

- Add images with ➕. Remove wrong entries with ❌.
- Configure dimensions or apply global presets.
- Preview savings and run batch export.

## Changelog

- v1–v5: Initial formats & GUI.
- v6–v9: Inspector, presets, non-destructive edits.
- v10–v15: Multithreading, pixel-precise resizing, UX improvements.
