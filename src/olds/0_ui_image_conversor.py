import sys
import os
import subprocess
import io
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

# --- 1. AUTO-INSTALADOR DE DEPENDENCIAS ---
def setup_dependencies():
    """Verifica e instala librerías gráficas y de imagen."""
    required_libs = {
        'ttkbootstrap': 'ttkbootstrap',
        'Pillow': 'PIL'
    }
    
    installed = False
    for package, import_name in required_libs.items():
        try:
            __import__(import_name)
        except ImportError:
            print(f"[SISTEMA] Instalando {package}...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                installed = True
            except Exception as e:
                print(f"[ERROR] No se pudo instalar {package}: {e}")

    if installed:
        print("[SISTEMA] Reiniciando aplicación...")
        os.execv(sys.executable, ['python'] + sys.argv)

setup_dependencies()

# --- 2. IMPORTACIONES ---
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from PIL import Image, ImageTk

class UniversalConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Tarquitet - Universal Image Lab")
        self.root.geometry("1300x850")
        
        # Variables de Estado
        self.original_image = None   # Objeto PIL original
        self.processed_buffer = None # Bytes de la imagen procesada (para guardar)
        self.original_size = 0       # Bytes
        self.processed_size = 0      # Bytes
        self.preview_cache = {}      # Para evitar garbage collection de Tkinter

        # Configuración por defecto
        self.format_var = tk.StringVar(value="JPEG")
        self.quality_var = tk.IntVar(value=85)
        self.scale_var = tk.IntVar(value=100)
        self.bg_color_var = tk.StringVar(value="BLANCO") # Para transparencias

        self.build_ui()

    def build_ui(self):
        # --- HEADER ---
        header = ttk.Frame(self.root, padding=20)
        header.pack(fill="x")
        
        ttk.Label(header, text="CONVERTIDOR & COMPRESOR", font=("Helvetica", 18, "bold"), bootstyle="primary").pack(side="left")
        ttk.Button(header, text="📂 Abrir Imagen", command=self.open_image, bootstyle="outline-light").pack(side="right")

        # --- CONTENIDO PRINCIPAL (SPLIT VIEW) ---
        main_content = ttk.Frame(self.root, padding=10)
        main_content.pack(fill="both", expand=True)

        # IZQUIERDA: ORIGINAL
        self.frame_left = ttk.Labelframe(main_content, text=" Original ", padding=10, bootstyle="secondary")
        self.frame_left.pack(side="left", fill="both", expand=True, padx=5)
        
        self.lbl_orig_img = ttk.Label(self.frame_left, text="Carga una imagen...", anchor="center")
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
        controls = ttk.Labelframe(self.root, text="Panel de Ajustes", padding=20, bootstyle="info")
        controls.pack(fill="x", padx=20, pady=20)

        # Columna 1: Formato
        c1 = ttk.Frame(controls)
        c1.pack(side="left", fill="y", padx=20)
        ttk.Label(c1, text="Formato Salida").pack(anchor="w")
        formats = ["JPEG", "PNG", "WEBP", "BMP", "ICO", "TIFF"]
        cb = ttk.Combobox(c1, textvariable=self.format_var, values=formats, state="readonly", width=10)
        cb.pack(pady=5)
        cb.bind("<<ComboboxSelected>>", self.schedule_update)

        # Columna 2: Calidad
        c2 = ttk.Frame(controls)
        c2.pack(side="left", fill="y", padx=20)
        self.lbl_qual = ttk.Label(c2, text=f"Calidad: {self.quality_var.get()}%")
        self.lbl_qual.pack(anchor="w")
        sc_q = ttk.Scale(c2, from_=1, to=100, variable=self.quality_var, length=200, command=lambda x: self.update_label_quality())
        sc_q.pack(pady=5)
        sc_q.bind("<ButtonRelease-1>", self.schedule_update) # Actualizar al soltar

        # Columna 3: Escala (Resize)
        c3 = ttk.Frame(controls)
        c3.pack(side="left", fill="y", padx=20)
        self.lbl_scale = ttk.Label(c3, text=f"Escala: {self.scale_var.get()}%")
        self.lbl_scale.pack(anchor="w")
        sc_s = ttk.Scale(c3, from_=10, to=100, variable=self.scale_var, length=200, command=lambda x: self.update_label_scale())
        sc_s.pack(pady=5)
        sc_s.bind("<ButtonRelease-1>", self.schedule_update)

        # Columna 4: Fondo (Para transparencias)
        c4 = ttk.Frame(controls)
        c4.pack(side="left", fill="y", padx=20)
        ttk.Label(c4, text="Fondo (Si Transparente)").pack(anchor="w")
        ttk.Radiobutton(c4, text="Blanco", variable=self.bg_color_var, value="BLANCO", command=self.schedule_update).pack(anchor="w")
        ttk.Radiobutton(c4, text="Negro", variable=self.bg_color_var, value="NEGRO", command=self.schedule_update).pack(anchor="w")

        # Botón Guardar Gigante
        self.btn_save = ttk.Button(controls, text="💾 GUARDAR IMAGEN", command=self.save_image, state="disabled", bootstyle="success")
        self.btn_save.pack(side="right", fill="y", padx=10)

    # --- LÓGICA DE UI ---
    def update_label_quality(self):
        self.lbl_qual.config(text=f"Calidad: {int(self.quality_var.get())}%")
    
    def update_label_scale(self):
        self.lbl_scale.config(text=f"Escala: {int(self.scale_var.get())}%")

    def schedule_update(self, event=None):
        """Pequeño delay para no saturar al mover sliders"""
        if self.original_image:
            self.process_preview()

    # --- LÓGICA DE IMAGEN ---
    def open_image(self):
        path = filedialog.askopenfilename(filetypes=[("Imágenes", "*.jpg *.jpeg *.png *.webp *.bmp *.tiff *.ico")])
        if not path: return

        try:
            self.original_image = Image.open(path)
            self.original_size = os.path.getsize(path)
            
            # Mostrar Original
            self.show_thumbnail(self.original_image, self.lbl_orig_img)
            
            info = f"{self.original_image.format} | {self.original_image.size[0]}x{self.original_image.size[1]} px | {self.format_bytes(self.original_size)}"
            self.lbl_orig_info.config(text=info)

            # Preparar UI
            self.btn_save.config(state="normal")
            self.process_preview() # Generar primera conversión

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir la imagen:\n{e}")

    def process_preview(self):
        """EL CEREBRO: Convierte la imagen en memoria sin guardar en disco."""
        if not self.original_image: return

        # 1. Crear Copia para trabajar
        target_img = self.original_image.copy()
        
        # 2. Redimensionar
        scale = self.scale_var.get()
        if scale < 100:
            w, h = target_img.size
            new_w = int(w * (scale/100))
            new_h = int(h * (scale/100))
            target_img = target_img.resize((new_w, new_h), Image.Resampling.LANCZOS)

        # 3. Datos de conversión
        fmt = self.format_var.get()
        quality = int(self.quality_var.get())

        # 4. Manejo de Transparencia (Alpha Channel)
        # Formatos que NO soportan transparencia: JPEG, BMP
        if fmt in ["JPEG", "BMP"] and target_img.mode in ("RGBA", "LA", "P"):
            background = Image.new("RGB", target_img.size, (255, 255, 255) if self.bg_color_var.get() == "BLANCO" else (0, 0, 0))
            if target_img.mode == 'P':
                target_img = target_img.convert('RGBA')
            background.paste(target_img, mask=target_img.split()[3]) # Usar canal alpha como máscara
            target_img = background
        elif fmt != "JPEG" and target_img.mode != "RGBA" and fmt != "BMP":
            # Si es PNG/WEBP asegurar que sea RGB o RGBA
            pass # Pillow maneja esto bien generalmente

        # 5. Simular Guardado (En Memoria RAM)
        buffer = io.BytesIO()
        
        try:
            save_args = {}
            if fmt == "JPEG":
                save_args = {"quality": quality, "optimize": True}
            elif fmt == "WEBP":
                save_args = {"quality": quality, "method": 6} # Metodo 6 = mejor compresión
            elif fmt == "PNG":
                # PNG no usa "quality" igual que JPG, usa compress_level (1-9)
                # Mapeamos 1-100 a 0-9 (inverso, 9 es max compresion)
                save_args = {"optimize": True, "compress_level": 9}
            elif fmt == "ICO":
                # ICO necesita tamaños específicos, ajustamos si es necesario
                if target_img.size[0] > 256: 
                    target_img = target_img.resize((256, 256), Image.Resampling.LANCZOS)
            
            # Guardar en buffer
            if target_img.mode == "P" and fmt == "JPEG": target_img = target_img.convert("RGB")
            
            target_img.save(buffer, format=fmt, **save_args)
            
            # 6. Actualizar UI
            self.processed_size = buffer.getbuffer().nbytes
            self.processed_buffer = buffer.getvalue() # Guardamos los bytes finales
            
            # Mostrar resultado visual
            # Recargamos desde el buffer para mostrar EXACTAMENTE cómo se ve comprimida (artifacts y todo)
            preview_img_obj = Image.open(io.BytesIO(self.processed_buffer))
            self.show_thumbnail(preview_img_obj, self.lbl_proc_img)

            # Info comparativa
            diff = self.original_size - self.processed_size
            diff_str = f"(-{self.format_bytes(diff)})" if diff > 0 else f"(+{self.format_bytes(abs(diff))})"
            color = "success" if diff > 0 else "danger"
            
            info_text = f"{fmt} | {target_img.size[0]}x{target_img.size[1]} px | {self.format_bytes(self.processed_size)} {diff_str}"
            self.lbl_proc_info.config(text=info_text, bootstyle=color)

        except Exception as e:
            self.lbl_proc_info.config(text=f"Error conversion: {e}", bootstyle="danger")
            print(e)

    def show_thumbnail(self, pil_img, label_widget):
        """Ajusta la imagen al tamaño del label sin deformar"""
        # Tamaño fijo del área de visualización
        display_w, display_h = 500, 400 
        
        img_copy = pil_img.copy()
        img_copy.thumbnail((display_w, display_h), Image.Resampling.LANCZOS)
        
        tk_img = ImageTk.PhotoImage(img_copy)
        
        # Guardar en cache o se borra
        label_widget.config(image=tk_img)
        label_widget.image = tk_img 

    def save_image(self):
        if not self.processed_buffer: return
        
        fmt = self.format_var.get().lower()
        if fmt == "jpeg": fmt = "jpg"
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=f".{fmt}",
            filetypes=[(f"{fmt.upper()} Image", f"*.{fmt}")]
        )
        
        if file_path:
            with open(file_path, "wb") as f:
                f.write(self.processed_buffer)
            messagebox.showinfo("Éxito", f"Imagen guardada en:\n{file_path}")

    def format_bytes(self, size):
        power = 2**10
        n = 0
        power_labels = {0 : '', 1: 'KB', 2: 'MB', 3: 'GB'}
        while size > power:
            size /= power
            n += 1
        return f"{size:.2f} {power_labels[n]}"

if __name__ == "__main__":
    # Tema moderno Darkly
    app_window = ttk.Window(themename="darkly") 
    app = UniversalConverter(app_window)
    app_window.mainloop()