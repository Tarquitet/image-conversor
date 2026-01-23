import sys
import os
import subprocess
import io
import tkinter as tk
from tkinter import filedialog, messagebox

# --- 1. AUTO-INSTALADOR COMPLETO ---
def setup_dependencies():
    required_libs = {
        'ttkbootstrap': 'ttkbootstrap',
        'Pillow': 'PIL',
        'pillow-avif-plugin': 'pillow_avif',
        'pillow-heif': 'pillow_heif'
    }
    
    installed = False
    for package, import_name in required_libs.items():
        try:
            if package == 'pillow-avif-plugin': import pillow_avif
            elif package == 'pillow-heif': import pillow_heif
            else: __import__(import_name)
        except ImportError:
            print(f"[SISTEMA] Instalando {package}...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                installed = True
            except Exception as e:
                print(f"[ERROR] {package}: {e}")

    if installed:
        print("[SISTEMA] Reiniciando...")
        os.execv(sys.executable, ['python'] + sys.argv)

setup_dependencies()

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from PIL import Image, ImageTk, PdfImagePlugin
import pillow_avif
import pillow_heif

pillow_heif.register_heif_opener()

class UniversalConverterUltimate:
    def __init__(self, root):
        self.root = root
        self.root.title("Tarquitet - The Ultimate Converter")
        self.root.geometry("1350x920")
        
        self.original_image = None
        self.processed_buffer = None 
        self.original_size = 0       
        self.processed_size = 0      

        # Valores por defecto
        self.format_var = tk.StringVar(value="AVIF")
        self.quality_var = tk.IntVar(value=80)
        self.scale_var = tk.IntVar(value=100)
        self.bg_color_var = tk.StringVar(value="BLANCO")

        self.build_ui()

    def build_ui(self):
        # HEADER
        header = ttk.Frame(self.root, padding=20)
        header.pack(fill="x")
        ttk.Label(header, text="IMAGEN LAB: EDICIÓN OMNIVERSAL", font=("Helvetica", 18, "bold"), bootstyle="primary").pack(side="left")
        ttk.Button(header, text="📂 Cargar Archivo", command=self.open_image, bootstyle="outline-light").pack(side="right")

        # CONTENIDO
        main_content = ttk.Frame(self.root, padding=10)
        main_content.pack(fill="both", expand=True)

        # IZQUIERDA
        self.frame_left = ttk.Labelframe(main_content, text=" Entrada ", padding=10, bootstyle="secondary")
        self.frame_left.pack(side="left", fill="both", expand=True, padx=5)
        self.lbl_orig_img = ttk.Label(self.frame_left, text="Arrastra tu imagen aquí...", anchor="center")
        self.lbl_orig_img.pack(fill="both", expand=True)
        self.lbl_orig_info = ttk.Label(self.frame_left, text="-", font=("Consolas", 10))
        self.lbl_orig_info.pack(side="bottom", fill="x")

        # DERECHA
        self.frame_right = ttk.Labelframe(main_content, text=" Salida (Preview) ", padding=10, bootstyle="success")
        self.frame_right.pack(side="left", fill="both", expand=True, padx=5)
        self.lbl_proc_img = ttk.Label(self.frame_right, text="...", anchor="center")
        self.lbl_proc_img.pack(fill="both", expand=True)
        self.lbl_proc_info = ttk.Label(self.frame_right, text="-", font=("Consolas", 10, "bold"), bootstyle="success")
        self.lbl_proc_info.pack(side="bottom", fill="x")

        # CONTROLES
        controls = ttk.Labelframe(self.root, text="Centro de Mando", padding=20, bootstyle="info")
        controls.pack(fill="x", padx=20, pady=20)

        # 1. FORMATOS (LISTA EXTENDIDA)
        c1 = ttk.Frame(controls)
        c1.pack(side="left", fill="y", padx=20)
        ttk.Label(c1, text="Formato Destino").pack(anchor="w")
        
        # --- AQUÍ ESTÁ LA LISTA COMPLETA ---
        formats = [
            "AVIF (Web Ultra)", "HEIC (iPhone)", "WEBP (Web Std)", 
            "JPEG (Foto)", "PNG (Transparente)", "GIF (Web)",
            "PSD (Adobe Photoshop)", "PDF (Documento)", "EPS (PostScript)",
            "BMP (Windows)", "ICO (Icono)", "TIFF (Imprenta)", 
            "TGA (Juegos)", "PCX (Retro)", "SGI (VFX)", "PPM (Unix)"
        ]
        
        cb = ttk.Combobox(c1, textvariable=self.format_var, values=formats, state="readonly", width=25)
        cb.pack(pady=5)
        cb.bind("<<ComboboxSelected>>", self.schedule_update)

        # 2. CALIDAD
        c2 = ttk.Frame(controls)
        c2.pack(side="left", fill="y", padx=20)
        self.lbl_qual = ttk.Label(c2, text=f"Calidad: {self.quality_var.get()}%")
        self.lbl_qual.pack(anchor="w")
        sc_q = ttk.Scale(c2, from_=1, to=100, variable=self.quality_var, length=200, command=lambda x: self.update_labels())
        sc_q.pack(pady=5)
        sc_q.bind("<ButtonRelease-1>", self.schedule_update) 

        # 3. ESCALA
        c3 = ttk.Frame(controls)
        c3.pack(side="left", fill="y", padx=20)
        self.lbl_scale = ttk.Label(c3, text=f"Escala: {self.scale_var.get()}%")
        self.lbl_scale.pack(anchor="w")
        sc_s = ttk.Scale(c3, from_=10, to=100, variable=self.scale_var, length=200, command=lambda x: self.update_labels())
        sc_s.pack(pady=5)
        sc_s.bind("<ButtonRelease-1>", self.schedule_update)

        # 4. FONDO
        c4 = ttk.Frame(controls)
        c4.pack(side="left", fill="y", padx=20)
        ttk.Label(c4, text="Fondo (Relleno)").pack(anchor="w")
        ttk.Radiobutton(c4, text="Blanco", variable=self.bg_color_var, value="BLANCO", command=self.schedule_update).pack(anchor="w")
        ttk.Radiobutton(c4, text="Negro", variable=self.bg_color_var, value="NEGRO", command=self.schedule_update).pack(anchor="w")

        # BOTÓN
        self.btn_save = ttk.Button(controls, text="💾 GUARDAR", command=self.save_image, state="disabled", bootstyle="success")
        self.btn_save.pack(side="right", fill="y", padx=10, ipady=10)

    def update_labels(self):
        self.lbl_qual.config(text=f"Calidad: {int(self.quality_var.get())}%")
        self.lbl_scale.config(text=f"Escala: {int(self.scale_var.get())}%")

    def schedule_update(self, event=None):
        if self.original_image: self.process_preview()

    def open_image(self):
        # Filtros de archivo masivos
        ftypes = [
            ("Todas", "*.jpg *.png *.webp *.avif *.heic *.psd *.bmp *.tiff *.tga *.ico *.gif *.eps *.pdf *.pcx"),
            ("Adobe", "*.psd *.eps *.pdf"),
            ("Modernos", "*.avif *.heic *.webp"),
            ("Clásicos", "*.jpg *.png *.bmp")
        ]
        path = filedialog.askopenfilename(filetypes=ftypes)
        if not path: return

        try:
            self.original_image = Image.open(path)
            self.original_size = os.path.getsize(path)
            
            self.show_thumbnail(self.original_image, self.lbl_orig_img)
            info = f"{self.original_image.format} | {self.original_image.size[0]}x{self.original_image.size[1]} | {self.format_bytes(self.original_size)}"
            self.lbl_orig_info.config(text=info)

            self.btn_save.config(state="normal")
            self.process_preview()

        except Exception as e:
            messagebox.showerror("Error", f"Archivo no soportado o dañado:\n{e}")

    def process_preview(self):
        if not self.original_image: return
        target = self.original_image.copy()
        
        # ESCALADO
        scale = self.scale_var.get()
        if scale < 100:
            w, h = target.size
            target = target.resize((int(w*(scale/100)), int(h*(scale/100))), Image.Resampling.LANCZOS)

        # CONFIG DE FORMATO
        raw_fmt = self.format_var.get().split(" ")[0] # "AVIF"
        quality = int(self.quality_var.get())

        # Mapeo Completo
        fmt_map = {
            "AVIF": "AVIF", "HEIC": "HEIF", "WEBP": "WEBP", "JPEG": "JPEG", 
            "PNG": "PNG", "GIF": "GIF", "PSD": "PSD", "PDF": "PDF", 
            "EPS": "EPS", "BMP": "BMP", "ICO": "ICO", "TIFF": "TIFF", 
            "TGA": "TGA", "PCX": "PCX", "SGI": "SGI", "PPM": "PPM"
        }
        pil_fmt = fmt_map.get(raw_fmt, "JPEG")

        # GESTIÓN DE TRANSPARENCIA
        # Formatos que NO soportan transparencia
        no_alpha = ["JPEG", "BMP", "PCX", "EPS", "PDF"] 
        
        if (pil_fmt in no_alpha) and target.mode in ("RGBA", "LA", "P"):
            bg_col = (255, 255, 255) if self.bg_color_var.get() == "BLANCO" else (0, 0, 0)
            bg = Image.new("RGB", target.size, bg_col)
            if target.mode == 'P': target = target.convert('RGBA')
            # Usar canal alpha como máscara
            try: bg.paste(target, mask=target.split()[3])
            except: bg.paste(target) # Fallback si no hay máscara limpia
            target = bg
        elif target.mode == "P" and pil_fmt not in ["GIF", "PNG"]:
             target = target.convert("RGB")

        # GUARDADO SIMULADO
        buffer = io.BytesIO()
        try:
            save_args = {}
            if pil_fmt == "AVIF": save_args = {"quality": quality, "speed": 6}
            elif pil_fmt == "JPEG": save_args = {"quality": quality, "optimize": True}
            elif pil_fmt == "WEBP": save_args = {"quality": quality, "method": 6}
            elif pil_fmt == "PNG": save_args = {"optimize": True, "compress_level": 6}
            elif pil_fmt == "GIF": save_args = {"optimize": True} 
            elif pil_fmt == "PDF": save_args = {"resolution": 100.0, "save_all": True}
            
            target.save(buffer, format=pil_fmt, **save_args)
            
            # MOSTRAR
            self.processed_size = buffer.getbuffer().nbytes
            self.processed_buffer = buffer.getvalue()
            
            # Renderizado de Vista Previa
            # Nota: PDF y EPS no se pueden "abrir" fácilmente con Pillow estándar para preview
            # Así que si es formato complejo, mostramos la imagen procesada antes de codificar
            if pil_fmt in ["PDF", "EPS", "PSD"]:
                preview_img = target # Mostramos el raster
            else:
                try:
                    preview_img = Image.open(io.BytesIO(self.processed_buffer))
                except:
                    preview_img = target # Fallback

            self.show_thumbnail(preview_img, self.lbl_proc_img)
            
            diff = self.original_size - self.processed_size
            diff_str = f"(-{self.format_bytes(diff)})" if diff > 0 else f"(+{self.format_bytes(abs(diff))})"
            col = "success" if diff > 0 else "danger"
            self.lbl_proc_info.config(text=f"{pil_fmt} | {self.format_bytes(self.processed_size)} {diff_str}", bootstyle=col)

        except Exception as e:
            self.lbl_proc_info.config(text=f"Error: {e}", bootstyle="danger")
            print(e)

    def show_thumbnail(self, pil_img, label):
        display_w, display_h = 550, 450
        img_copy = pil_img.copy()
        img_copy.thumbnail((display_w, display_h), Image.Resampling.LANCZOS)
        tk_img = ImageTk.PhotoImage(img_copy)
        label.config(image=tk_img)
        label.image = tk_img

    def save_image(self):
        if not self.processed_buffer: return
        raw_fmt = self.format_var.get().split(" ")[0].lower()
        
        # Mapa de extensiones correctas
        ext_map = {
            "avif": "avif", "heic": "heic", "jpeg": "jpg", "psd": "psd",
            "pdf": "pdf", "eps": "eps", "gif": "gif", "tiff": "tif", "pcx": "pcx"
        }
        ext = ext_map.get(raw_fmt, raw_fmt)

        path = filedialog.asksaveasfilename(defaultextension=f".{ext}", filetypes=[(f"{raw_fmt.upper()}", f"*.{ext}")])
        if path:
            with open(path, "wb") as f: f.write(self.processed_buffer)
            messagebox.showinfo("Exportado", f"Archivo guardado:\n{path}")

    def format_bytes(self, size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024: return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} TB"

if __name__ == "__main__":
    app_window = ttk.Window(themename="darkly") 
    app = UniversalConverterUltimate(app_window)
    app_window.mainloop()