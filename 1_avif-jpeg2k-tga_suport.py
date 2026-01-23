import sys
import os
import subprocess
import io
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

# --- 1. AUTO-INSTALADOR DE DEPENDENCIAS EXTENDIDO ---
def setup_dependencies():
    """Verifica e instala soporte para formatos modernos (AVIF, HEIC)."""
    required_libs = {
        'ttkbootstrap': 'ttkbootstrap',
        'Pillow': 'PIL',
        'pillow-avif-plugin': 'pillow_avif', # Plugin para AVIF
        'pillow-heif': 'pillow_heif'         # Plugin para HEIC (iPhone)
    }
    
    installed = False
    for package, import_name in required_libs.items():
        try:
            # Truco: Algunos plugins se registran solos al importar PIL, 
            # pero verificamos si podemos importarlos para estar seguros.
            if package == 'pillow-avif-plugin': 
                import pillow_avif
            elif package == 'pillow-heif':
                import pillow_heif
            else:
                __import__(import_name)
        except ImportError:
            print(f"[SISTEMA] Instalando soporte para {package}...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                installed = True
            except Exception as e:
                print(f"[ERROR] No se pudo instalar {package}: {e}")

    if installed:
        print("[SISTEMA] Reiniciando aplicación con nuevos formatos...")
        os.execv(sys.executable, ['python'] + sys.argv)

setup_dependencies()

# --- 2. IMPORTACIONES ---
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from PIL import Image, ImageTk
import pillow_avif # Habilita AVIF automáticamente
import pillow_heif # Habilita HEIC

# Registrar HEIC para que Pillow lo entienda
pillow_heif.register_heif_opener()

class UniversalConverterPro:
    def __init__(self, root):
        self.root = root
        self.root.title("Tarquitet - Ultimate Image Converter (AVIF/HEIC/WebP)")
        self.root.geometry("1350x900")
        
        # Variables de Estado
        self.original_image = None
        self.processed_buffer = None 
        self.original_size = 0       
        self.processed_size = 0      
        self.preview_cache = {}      

        # Configuración por defecto
        self.format_var = tk.StringVar(value="AVIF") # Sugerimos AVIF por defecto
        self.quality_var = tk.IntVar(value=80)
        self.scale_var = tk.IntVar(value=100)
        self.bg_color_var = tk.StringVar(value="BLANCO")

        self.build_ui()

    def build_ui(self):
        # --- HEADER ---
        header = ttk.Frame(self.root, padding=20)
        header.pack(fill="x")
        
        ttk.Label(header, text="CONVERTIDOR MULTIFORMATO PRO", font=("Helvetica", 18, "bold"), bootstyle="primary").pack(side="left")
        ttk.Label(header, text="Soporte: AVIF • HEIC • WebP • TGA • JPEG 2000", font=("Arial", 9), bootstyle="secondary").pack(side="left", padx=10, pady=5)
        ttk.Button(header, text="📂 Cargar Imagen", command=self.open_image, bootstyle="outline-light").pack(side="right")

        # --- CONTENIDO PRINCIPAL (SPLIT VIEW) ---
        main_content = ttk.Frame(self.root, padding=10)
        main_content.pack(fill="both", expand=True)

        # IZQUIERDA: ORIGINAL
        self.frame_left = ttk.Labelframe(main_content, text=" Original ", padding=10, bootstyle="secondary")
        self.frame_left.pack(side="left", fill="both", expand=True, padx=5)
        
        self.lbl_orig_img = ttk.Label(self.frame_left, text="Arrastra o carga una imagen...", anchor="center")
        self.lbl_orig_img.pack(fill="both", expand=True)
        self.lbl_orig_info = ttk.Label(self.frame_left, text="-", font=("Consolas", 10), bootstyle="secondary")
        self.lbl_orig_info.pack(side="bottom", fill="x")

        # DERECHA: PROCESADA
        self.frame_right = ttk.Labelframe(main_content, text=" Resultado (Vista Previa) ", padding=10, bootstyle="success")
        self.frame_right.pack(side="left", fill="both", expand=True, padx=5)
        
        self.lbl_proc_img = ttk.Label(self.frame_right, text="...", anchor="center")
        self.lbl_proc_img.pack(fill="both", expand=True)
        self.lbl_proc_info = ttk.Label(self.frame_right, text="-", font=("Consolas", 10, "bold"), bootstyle="success")
        self.lbl_proc_info.pack(side="bottom", fill="x")

        # --- PANEL DE CONTROL (ABAJO) ---
        controls = ttk.Labelframe(self.root, text="Panel de Control Avanzado", padding=20, bootstyle="info")
        controls.pack(fill="x", padx=20, pady=20)

        # Columna 1: Formatos Extendidos
        c1 = ttk.Frame(controls)
        c1.pack(side="left", fill="y", padx=20)
        ttk.Label(c1, text="Formato Salida").pack(anchor="w")
        
        # LISTA EXTENDIDA DE FORMATOS
        formats = [
            "AVIF (Ultra Compresión)", 
            "HEIC (Apple)", 
            "WEBP (Web Standard)", 
            "JPEG (Universal)", 
            "PNG (Sin Pérdida)", 
            "JPEG 2000 (.jp2)", 
            "TGA (Texturas)", 
            "TIFF (Impresión)", 
            "BMP (Raw)", 
            "ICO (Favicon)", 
            "PPM (Portable)"
        ]
        
        cb = ttk.Combobox(c1, textvariable=self.format_var, values=formats, state="readonly", width=25)
        cb.pack(pady=5)
        cb.bind("<<ComboboxSelected>>", self.schedule_update)

        # Columna 2: Calidad / Compresión
        c2 = ttk.Frame(controls)
        c2.pack(side="left", fill="y", padx=20)
        self.lbl_qual = ttk.Label(c2, text=f"Calidad / Compresión: {self.quality_var.get()}%")
        self.lbl_qual.pack(anchor="w")
        sc_q = ttk.Scale(c2, from_=1, to=100, variable=self.quality_var, length=220, command=lambda x: self.update_label_quality())
        sc_q.pack(pady=5)
        sc_q.bind("<ButtonRelease-1>", self.schedule_update) 

        # Columna 3: Escala
        c3 = ttk.Frame(controls)
        c3.pack(side="left", fill="y", padx=20)
        self.lbl_scale = ttk.Label(c3, text=f"Escala: {self.scale_var.get()}%")
        self.lbl_scale.pack(anchor="w")
        sc_s = ttk.Scale(c3, from_=10, to=100, variable=self.scale_var, length=220, command=lambda x: self.update_label_scale())
        sc_s.pack(pady=5)
        sc_s.bind("<ButtonRelease-1>", self.schedule_update)

        # Columna 4: Fondo
        c4 = ttk.Frame(controls)
        c4.pack(side="left", fill="y", padx=20)
        ttk.Label(c4, text="Fondo Transparencia").pack(anchor="w")
        ttk.Radiobutton(c4, text="Blanco", variable=self.bg_color_var, value="BLANCO", command=self.schedule_update).pack(anchor="w")
        ttk.Radiobutton(c4, text="Negro", variable=self.bg_color_var, value="NEGRO", command=self.schedule_update).pack(anchor="w")

        # Botón Guardar
        self.btn_save = ttk.Button(controls, text="💾 EXPORTAR", command=self.save_image, state="disabled", bootstyle="success")
        self.btn_save.pack(side="right", fill="y", padx=10, ipady=10)

    # --- LÓGICA UI ---
    def update_label_quality(self):
        self.lbl_qual.config(text=f"Calidad / Compresión: {int(self.quality_var.get())}%")
    
    def update_label_scale(self):
        self.lbl_scale.config(text=f"Escala: {int(self.scale_var.get())}%")

    def schedule_update(self, event=None):
        if self.original_image: self.process_preview()

    # --- LÓGICA DE IMAGEN ---
    def open_image(self):
        # Permitimos abrir casi cualquier cosa, incluyendo HEIC y AVIF
        ftypes = [
            ("Todas las imágenes", "*.jpg *.jpeg *.png *.webp *.avif *.heic *.bmp *.tiff *.tga *.ico *.jp2 *.ppm"),
            ("Modernos", "*.avif *.heic *.webp"),
            ("Clásicos", "*.jpg *.png")
        ]
        path = filedialog.askopenfilename(filetypes=ftypes)
        if not path: return

        try:
            self.original_image = Image.open(path)
            self.original_size = os.path.getsize(path)
            
            # Mostrar Original
            self.show_thumbnail(self.original_image, self.lbl_orig_img)
            info = f"{self.original_image.format} | {self.original_image.size[0]}x{self.original_image.size[1]} | {self.format_bytes(self.original_size)}"
            self.lbl_orig_info.config(text=info)

            self.btn_save.config(state="normal")
            self.process_preview()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo leer la imagen:\n{e}")

    def process_preview(self):
        if not self.original_image: return

        # 1. Copia y Resize
        target_img = self.original_image.copy()
        scale = self.scale_var.get()
        if scale < 100:
            w, h = target_img.size
            new_w, new_h = int(w * (scale/100)), int(h * (scale/100))
            target_img = target_img.resize((new_w, new_h), Image.Resampling.LANCZOS)

        # 2. Configuración de Formato
        raw_fmt = self.format_var.get().split(" ")[0] # Extraer "AVIF" de "AVIF (Ultra...)"
        quality = int(self.quality_var.get())

        # Mapeo de nombres UI a nombres PIL internos
        fmt_map = {
            "AVIF": "AVIF", "HEIC": "HEIF", "WEBP": "WEBP", 
            "JPEG": "JPEG", "PNG": "PNG", "JPEG 2000": "JPEG2000",
            "TGA": "TGA", "TIFF": "TIFF", "BMP": "BMP", 
            "ICO": "ICO", "PPM": "PPM"
        }
        pil_fmt = fmt_map.get(raw_fmt, "JPEG")

        # 3. Manejo de Transparencia
        # Formatos que NO soportan transparencia
        no_alpha_formats = ["JPEG", "BMP", "JPEG2000", "PPM"] 
        
        if pil_fmt in no_alpha_formats and target_img.mode in ("RGBA", "LA", "P"):
            bg_col = (255, 255, 255) if self.bg_color_var.get() == "BLANCO" else (0, 0, 0)
            background = Image.new("RGB", target_img.size, bg_col)
            if target_img.mode == 'P': target_img = target_img.convert('RGBA')
            background.paste(target_img, mask=target_img.split()[3])
            target_img = background
        elif target_img.mode == "P" and pil_fmt not in ["GIF", "PNG"]:
             target_img = target_img.convert("RGB")

        # 4. Guardado en Memoria (Simulación)
        buffer = io.BytesIO()
        try:
            save_args = {}
            
            # --- AJUSTES ESPECÍFICOS POR FORMATO ---
            if pil_fmt == "AVIF":
                save_args = {"quality": quality, "speed": 6} # Speed 6 es balanceado
            elif pil_fmt == "HEIF":
                save_args = {"quality": quality}
            elif pil_fmt == "WEBP":
                save_args = {"quality": quality, "method": 6}
            elif pil_fmt == "JPEG":
                save_args = {"quality": quality, "optimize": True}
            elif pil_fmt == "PNG":
                # PNG usa compress_level (0-9)
                save_args = {"optimize": True, "compress_level": 6} 
            elif pil_fmt == "ICO":
                if target_img.size[0] > 256: 
                    target_img = target_img.resize((256, 256), Image.Resampling.LANCZOS)
            
            target_img.save(buffer, format=pil_fmt, **save_args)
            
            # 5. Visualizar Resultado
            self.processed_size = buffer.getbuffer().nbytes
            self.processed_buffer = buffer.getvalue()
            
            # Re-leer para mostrar artefactos de compresión reales
            preview_img = Image.open(io.BytesIO(self.processed_buffer))
            self.show_thumbnail(preview_img, self.lbl_proc_img)

            # Info
            diff = self.original_size - self.processed_size
            diff_str = f"(-{self.format_bytes(diff)})" if diff > 0 else f"(+{self.format_bytes(abs(diff))})"
            color = "success" if diff > 0 else "danger"
            self.lbl_proc_info.config(text=f"{pil_fmt} | {self.format_bytes(self.processed_size)} {diff_str}", bootstyle=color)

        except Exception as e:
            self.lbl_proc_info.config(text=f"Error: {e}", bootstyle="danger")
            print(f"Error saving {pil_fmt}: {e}")

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
        
        # Corrección de extensiones
        ext_map = {"avif": "avif", "heic": "heic", "jpeg": "jpg", "jpeg 2000": "jp2", "tiff": "tif"}
        ext = ext_map.get(raw_fmt, raw_fmt)

        path = filedialog.asksaveasfilename(defaultextension=f".{ext}", filetypes=[(f"{raw_fmt.upper()}", f"*.{ext}")])
        if path:
            with open(path, "wb") as f: f.write(self.processed_buffer)
            messagebox.showinfo("Guardado", f"Imagen exportada exitosamente:\n{path}")

    def format_bytes(self, size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024: return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} TB"

if __name__ == "__main__":
    app_window = ttk.Window(themename="darkly") 
    app = UniversalConverterPro(app_window)
    app_window.mainloop()