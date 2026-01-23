import sys
import os
import subprocess
import io
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

# --- 1. AUTO-INSTALADOR COMPLETO ---
def setup_dependencies():
    """Verifica e instala dependencias gráficas y de imagen."""
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
        print("[SISTEMA] Reiniciando aplicación...")
        os.execv(sys.executable, ['python'] + sys.argv)

setup_dependencies()

# --- 2. IMPORTACIONES ---
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from PIL import Image, ImageTk
import pillow_avif
import pillow_heif

# Registrar HEIC para que Pillow lo entienda
pillow_heif.register_heif_opener()

class UniversalBatchConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Tarquitet - Batch Image Processor")
        self.root.geometry("1400x900")
        
        # Variables de Estado
        self.image_queue = []        # Lista de rutas de archivos
        self.current_img_path = None # Ruta seleccionada actualmente
        self.original_image = None   # Objeto PIL en memoria
        self.processed_buffer = None # Buffer de la previsualización
        self.original_size = 0       
        self.processed_size = 0
        
        # Configuración por defecto
        self.format_var = tk.StringVar(value="AVIF")
        self.quality_var = tk.IntVar(value=80)
        self.scale_var = tk.IntVar(value=100)
        self.bg_color_var = tk.StringVar(value="BLANCO")
        
        # Ruta de Salida (Por defecto: carpeta 'converted' donde esté el script)
        default_out = os.path.join(os.getcwd(), "converted")
        if not os.path.exists(default_out): 
            try: os.makedirs(default_out)
            except: default_out = os.getcwd()
        self.output_dir_var = tk.StringVar(value=default_out)

        self.build_ui()

    def build_ui(self):
        # --- HEADER ---
        header = ttk.Frame(self.root, padding=20)
        header.pack(fill="x")
        ttk.Label(header, text="BATCH IMAGE CONVERTER", font=("Helvetica", 18, "bold"), bootstyle="primary").pack(side="left")
        ttk.Label(header, text="Lista + Previsualización + Conversión Masiva", font=("Arial", 10), bootstyle="secondary").pack(side="left", padx=15, pady=5)

        # --- CONTENIDO PRINCIPAL (PANED WINDOW) ---
        paned = ttk.PanedWindow(self.root, orient="horizontal")
        paned.pack(fill="both", expand=True, padx=10, pady=5)

        # === IZQUIERDA: LISTA DE ARCHIVOS (COLA) ===
        left_panel = ttk.Frame(paned, padding=(0,0,10,0))
        paned.add(left_panel, weight=1)

        # Botones de Lista
        list_btns = ttk.Frame(left_panel)
        list_btns.pack(fill="x", pady=(0, 5))
        ttk.Button(list_btns, text="📂 Agregar Imágenes", command=self.add_images, bootstyle="outline-primary").pack(side="left", fill="x", expand=True, padx=2)
        ttk.Button(list_btns, text="❌ Limpiar Lista", command=self.clear_list, bootstyle="outline-danger").pack(side="left", padx=2)

        # Listbox con Scroll
        list_frame = ttk.Frame(left_panel)
        list_frame.pack(fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.listbox = tk.Listbox(list_frame, font=("Consolas", 10), selectmode="SINGLE", borderwidth=0, highlightthickness=0)
        self.listbox.pack(side="left", fill="both", expand=True)
        self.listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.listbox.yview)
        
        self.listbox.bind('<<ListboxSelect>>', self.on_select_file)

        # === DERECHA: EDITOR Y VISTA PREVIA ===
        right_panel = ttk.Frame(paned, padding=(10,0,0,0))
        paned.add(right_panel, weight=3)

        # 1. VISUALIZADOR (SPLIT: ORIG VS PREVIEW)
        preview_area = ttk.Frame(right_panel)
        preview_area.pack(fill="both", expand=True)

        # Frame Izq (Original)
        f_orig = ttk.Labelframe(preview_area, text=" Original ", padding=10, bootstyle="secondary")
        f_orig.pack(side="left", fill="both", expand=True, padx=5)
        self.lbl_orig_img = ttk.Label(f_orig, text="Selecciona una imagen de la lista", anchor="center")
        self.lbl_orig_img.pack(fill="both", expand=True)
        self.lbl_orig_info = ttk.Label(f_orig, text="-", font=("Consolas", 9), bootstyle="secondary")
        self.lbl_orig_info.pack(side="bottom", fill="x")

        # Frame Der (Resultado)
        f_proc = ttk.Labelframe(preview_area, text=" Resultado (Con Ajustes Actuales) ", padding=10, bootstyle="success")
        f_proc.pack(side="left", fill="both", expand=True, padx=5)
        self.lbl_proc_img = ttk.Label(f_proc, text="...", anchor="center")
        self.lbl_proc_img.pack(fill="both", expand=True)
        self.lbl_proc_info = ttk.Label(f_proc, text="-", font=("Consolas", 9, "bold"), bootstyle="success")
        self.lbl_proc_info.pack(side="bottom", fill="x")

        # 2. PANEL DE CONTROLES (ABAJO)
        controls = ttk.Labelframe(self.root, text="Configuración Global & Exportación", padding=20, bootstyle="info")
        controls.pack(fill="x", padx=10, pady=10)

        # Fila 1: Ajustes de Imagen
        row1 = ttk.Frame(controls)
        row1.pack(fill="x", pady=(0, 15))

        # Formato
        c1 = ttk.Frame(row1)
        c1.pack(side="left", fill="y", padx=(0, 20))
        ttk.Label(c1, text="Formato Salida").pack(anchor="w")
        formats = ["AVIF (Web)", "HEIC (iOS)", "WEBP", "JPEG", "PNG", "GIF", "PSD", "PDF", "EPS", "BMP", "TIFF", "ICO"]
        cb = ttk.Combobox(c1, textvariable=self.format_var, values=formats, state="readonly", width=15)
        cb.pack(pady=5)
        cb.bind("<<ComboboxSelected>>", self.schedule_update)

        # Calidad
        c2 = ttk.Frame(row1)
        c2.pack(side="left", fill="y", padx=20)
        self.lbl_qual = ttk.Label(c2, text=f"Calidad: {self.quality_var.get()}%")
        self.lbl_qual.pack(anchor="w")
        sc_q = ttk.Scale(c2, from_=1, to=100, variable=self.quality_var, length=200, command=lambda x: self.update_labels())
        sc_q.pack(pady=5)
        sc_q.bind("<ButtonRelease-1>", self.schedule_update)

        # Escala
        c3 = ttk.Frame(row1)
        c3.pack(side="left", fill="y", padx=20)
        self.lbl_scale = ttk.Label(c3, text=f"Escala: {self.scale_var.get()}%")
        self.lbl_scale.pack(anchor="w")
        sc_s = ttk.Scale(c3, from_=10, to=100, variable=self.scale_var, length=200, command=lambda x: self.update_labels())
        sc_s.pack(pady=5)
        sc_s.bind("<ButtonRelease-1>", self.schedule_update)

        # Fondo
        c4 = ttk.Frame(row1)
        c4.pack(side="left", fill="y", padx=20)
        ttk.Label(c4, text="Fondo Transparencia").pack(anchor="w")
        ttk.Radiobutton(c4, text="Blanco", variable=self.bg_color_var, value="BLANCO", command=self.schedule_update).pack(anchor="w")
        ttk.Radiobutton(c4, text="Negro", variable=self.bg_color_var, value="NEGRO", command=self.schedule_update).pack(anchor="w")

        # Fila 2: Ruta y Botones Finales
        row2 = ttk.Frame(controls)
        row2.pack(fill="x", pady=(10, 0))

        # Selector de Ruta
        path_frame = ttk.Frame(row2)
        path_frame.pack(side="left", fill="x", expand=True, padx=(0, 20))
        ttk.Label(path_frame, text="Carpeta de Salida:", font=("Arial", 9, "bold")).pack(anchor="w")
        
        p_inner = ttk.Frame(path_frame)
        p_inner.pack(fill="x", pady=5)
        ttk.Entry(p_inner, textvariable=self.output_dir_var).pack(side="left", fill="x", expand=True)
        ttk.Button(p_inner, text="📂 Cambiar", command=self.choose_output_dir, bootstyle="secondary").pack(side="left", padx=5)

        # Botones de Acción
        ttk.Button(row2, text="Guardar SOLO ESTA (Preview)", command=self.save_current_single, bootstyle="warning").pack(side="right", padx=5)
        ttk.Button(row2, text="🚀 CONVERTIR TODO LA LISTA", command=self.process_batch, bootstyle="success").pack(side="right", padx=5, ipady=5)

    # --- GESTIÓN DE LISTA ---
    def add_images(self):
        ftypes = [("Imágenes", "*.jpg *.jpeg *.png *.webp *.avif *.heic *.psd *.bmp *.tiff *.tga *.ico *.gif *.eps *.pdf")]
        files = filedialog.askopenfilenames(filetypes=ftypes)
        if files:
            for f in files:
                if f not in self.image_queue:
                    self.image_queue.append(f)
                    self.listbox.insert(tk.END, os.path.basename(f))
            
            # Seleccionar el primero automáticamente si no hay selección
            if not self.current_img_path and self.image_queue:
                self.listbox.select_set(0)
                self.on_select_file(None)

    def clear_list(self):
        self.image_queue = []
        self.listbox.delete(0, tk.END)
        self.current_img_path = None
        self.original_image = None
        self.lbl_orig_img.config(image='', text="Lista vacía")
        self.lbl_proc_img.config(image='', text="...")
        self.lbl_orig_info.config(text="-")
        self.lbl_proc_info.config(text="-")

    def on_select_file(self, event):
        sel = self.listbox.curselection()
        if not sel: return
        
        index = sel[0]
        path = self.image_queue[index]
        self.current_img_path = path
        self.load_image_preview(path)

    def choose_output_dir(self):
        d = filedialog.askdirectory()
        if d: self.output_dir_var.set(d)

    def update_labels(self):
        self.lbl_qual.config(text=f"Calidad: {int(self.quality_var.get())}%")
        self.lbl_scale.config(text=f"Escala: {int(self.scale_var.get())}%")

    def schedule_update(self, event=None):
        if self.original_image: self.process_preview()

    # --- LÓGICA DE PROCESAMIENTO (CORE) ---
    def load_image_preview(self, path):
        try:
            self.original_image = Image.open(path)
            self.original_size = os.path.getsize(path)
            
            # Mostrar Original
            self.show_thumbnail(self.original_image, self.lbl_orig_img)
            info = f"{os.path.basename(path)}\n{self.original_image.format} | {self.original_image.size[0]}x{self.original_image.size[1]} | {self.format_bytes(self.original_size)}"
            self.lbl_orig_info.config(text=info)

            # Generar Preview
            self.process_preview()
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar: {os.path.basename(path)}\n{e}")

    def process_image_logic(self, img_obj, return_buffer=True):
        """Lógica central de conversión, usada tanto para preview como para exportación."""
        target = img_obj.copy()
        
        # 1. Escala
        scale = self.scale_var.get()
        if scale < 100:
            w, h = target.size
            target = target.resize((int(w*(scale/100)), int(h*(scale/100))), Image.Resampling.LANCZOS)

        # 2. Configuración
        raw_fmt = self.format_var.get().split(" ")[0]
        quality = int(self.quality_var.get())

        fmt_map = {
            "AVIF": "AVIF", "HEIC": "HEIF", "WEBP": "WEBP", "JPEG": "JPEG", 
            "PNG": "PNG", "GIF": "GIF", "PSD": "PSD", "PDF": "PDF", 
            "EPS": "EPS", "BMP": "BMP", "ICO": "ICO", "TIFF": "TIFF"
        }
        pil_fmt = fmt_map.get(raw_fmt, "JPEG")

        # 3. Transparencia
        no_alpha = ["JPEG", "BMP", "EPS", "PDF"]
        if (pil_fmt in no_alpha) and target.mode in ("RGBA", "LA", "P"):
            bg_col = (255, 255, 255) if self.bg_color_var.get() == "BLANCO" else (0, 0, 0)
            bg = Image.new("RGB", target.size, bg_col)
            if target.mode == 'P': target = target.convert('RGBA')
            try: bg.paste(target, mask=target.split()[3])
            except: bg.paste(target)
            target = bg
        elif target.mode == "P" and pil_fmt not in ["GIF", "PNG"]:
             target = target.convert("RGB")

        # 4. Guardar (Simulado o Final)
        buffer = io.BytesIO()
        
        save_args = {}
        if pil_fmt == "AVIF": save_args = {"quality": quality, "speed": 6}
        elif pil_fmt == "JPEG": save_args = {"quality": quality, "optimize": True}
        elif pil_fmt == "WEBP": save_args = {"quality": quality, "method": 6}
        elif pil_fmt == "PNG": save_args = {"optimize": True, "compress_level": 6}
        elif pil_fmt == "PDF": save_args = {"resolution": 100.0, "save_all": True}
        elif pil_fmt == "ICO":
             if target.size[0] > 256: target = target.resize((256, 256), Image.Resampling.LANCZOS)

        target.save(buffer, format=pil_fmt, **save_args)
        
        if return_buffer:
            return buffer.getvalue()
        else:
            return None # (Caso raro, no usado aquí)

    def process_preview(self):
        if not self.original_image: return
        try:
            img_bytes = self.process_image_logic(self.original_image)
            self.processed_buffer = img_bytes # Guardar para "Guardar Solo Esta"
            
            # Mostrar
            try:
                preview_img = Image.open(io.BytesIO(img_bytes))
            except:
                # Si el formato no se puede re-leer (ej: EPS/PDF complejos), mostramos placeholder o la original procesada
                preview_img = self.original_image 
            
            self.show_thumbnail(preview_img, self.lbl_proc_img)
            
            # Stats
            size = len(img_bytes)
            diff = self.original_size - size
            diff_str = f"(-{self.format_bytes(diff)})" if diff > 0 else f"(+{self.format_bytes(abs(diff))})"
            col = "success" if diff > 0 else "danger"
            
            raw_fmt = self.format_var.get().split(" ")[0]
            self.lbl_proc_info.config(text=f"{raw_fmt} | {self.format_bytes(size)} {diff_str}", bootstyle=col)
            
        except Exception as e:
            self.lbl_proc_info.config(text=f"Error: {e}", bootstyle="danger")

    def show_thumbnail(self, pil_img, label):
        display_w, display_h = 450, 350
        img_copy = pil_img.copy()
        img_copy.thumbnail((display_w, display_h), Image.Resampling.LANCZOS)
        tk_img = ImageTk.PhotoImage(img_copy)
        label.config(image=tk_img)
        label.image = tk_img

    def format_bytes(self, size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024: return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} TB"

    # --- ACCIONES FINALES ---
    def save_current_single(self):
        if not self.processed_buffer: return
        raw_fmt = self.format_var.get().split(" ")[0].lower()
        ext_map = {"avif":"avif", "heic":"heic", "jpeg":"jpg", "tiff":"tif"}
        ext = ext_map.get(raw_fmt, raw_fmt)
        
        path = filedialog.asksaveasfilename(defaultextension=f".{ext}", filetypes=[(raw_fmt.upper(), f"*.{ext}")])
        if path:
            with open(path, "wb") as f: f.write(self.processed_buffer)
            messagebox.showinfo("Guardado", f"Imagen guardada:\n{path}")

    def process_batch(self):
        if not self.image_queue:
            messagebox.showwarning("Vacío", "No hay imágenes en la lista para convertir.")
            return

        out_dir = self.output_dir_var.get()
        if not os.path.exists(out_dir):
            try: os.makedirs(out_dir)
            except: 
                messagebox.showerror("Error", "No se pudo crear la carpeta de salida.")
                return

        raw_fmt = self.format_var.get().split(" ")[0].lower()
        ext_map = {"avif":"avif", "heic":"heic", "jpeg":"jpg", "tiff":"tif", "psd":"psd", "pdf":"pdf"}
        ext = ext_map.get(raw_fmt, raw_fmt)
        
        success_count = 0
        
        # Progreso Visual
        progress_win = tk.Toplevel(self.root)
        progress_win.title("Procesando...")
        progress_win.geometry("300x150")
        ttk.Label(progress_win, text="Convirtiendo Lote...", font=("Arial", 12, "bold")).pack(pady=10)
        p_bar = ttk.Progressbar(progress_win, maximum=len(self.image_queue), mode="determinate")
        p_bar.pack(fill="x", padx=20, pady=10)
        p_lbl = ttk.Label(progress_win, text="Iniciando...")
        p_lbl.pack()
        
        for i, img_path in enumerate(self.image_queue):
            try:
                fname = os.path.basename(img_path)
                p_lbl.config(text=f"Procesando: {fname}")
                progress_win.update()
                
                # Abrir y Procesar
                with Image.open(img_path) as img:
                    img_bytes = self.process_image_logic(img)
                    
                    # Nombre de salida
                    base_name = os.path.splitext(fname)[0]
                    out_path = os.path.join(out_dir, f"{base_name}.{ext}")
                    
                    with open(out_path, "wb") as f:
                        f.write(img_bytes)
                
                success_count += 1
            except Exception as e:
                print(f"Error en {img_path}: {e}")
            
            p_bar['value'] = i + 1
            progress_win.update()

        progress_win.destroy()
        messagebox.showinfo("Batch Finalizado", f"Se convirtieron {success_count} de {len(self.image_queue)} imágenes.\nCarpeta: {out_dir}")

if __name__ == "__main__":
    app_window = ttk.Window(themename="darkly") 
    app = UniversalBatchConverter(app_window)
    app_window.mainloop()