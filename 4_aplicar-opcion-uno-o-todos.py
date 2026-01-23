import sys
import os
import subprocess
import io
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

# --- 1. AUTO-INSTALADOR ---
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
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                installed = True
            except: pass
    if installed: os.execv(sys.executable, ['python'] + sys.argv)

setup_dependencies()

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from PIL import Image, ImageTk
import pillow_avif
import pillow_heif

pillow_heif.register_heif_opener()

class ImageItem:
    """Clase para guardar la configuración individual de cada imagen"""
    def __init__(self, path):
        self.path = path
        self.name = os.path.basename(path)
        # Valores por defecto (se pueden sobrescribir)
        self.fmt = "AVIF"
        self.quality = 80
        self.scale = 100
        self.bg = "BLANCO"

class UniversalGranularConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Tarquitet - Granular Converter")
        self.root.geometry("1450x950")
        
        # Datos
        self.items = []              # Lista de objetos ImageItem
        self.current_item = None     # Objeto ImageItem seleccionado
        self.original_image = None   # PIL Image en memoria (cache)
        self.processed_buffer = None
        
        # Variables de UI (Vinculadas a los controles)
        self.var_fmt = tk.StringVar(value="AVIF")
        self.var_qual = tk.IntVar(value=80)
        self.var_scale = tk.IntVar(value=100)
        self.var_bg = tk.StringVar(value="BLANCO")
        
        # Ruta Salida (Default = Carpeta Actual)
        self.var_out_dir = tk.StringVar(value=os.getcwd())

        # Flags para evitar bucles de eventos
        self.ignore_ui_events = False 

        self.build_ui()

    def build_ui(self):
        # HEADER
        header = ttk.Frame(self.root, padding=20)
        header.pack(fill="x")
        ttk.Label(header, text="CONVERTIDOR GRANULAR", font=("Helvetica", 18, "bold"), bootstyle="primary").pack(side="left")
        ttk.Label(header, text="Configura cada imagen por separado o en lote", font=("Arial", 10)).pack(side="left", padx=15, pady=5)

        # MAIN
        paned = ttk.PanedWindow(self.root, orient="horizontal")
        paned.pack(fill="both", expand=True, padx=10, pady=5)

        # === IZQUIERDA: LISTA ===
        left = ttk.Frame(paned, padding=(0,0,10,0))
        paned.add(left, weight=1)

        # Botones Lista
        btns = ttk.Frame(left)
        btns.pack(fill="x", pady=5)
        ttk.Button(btns, text="➕ Agregar", command=self.add_images, bootstyle="outline-primary").pack(side="left", fill="x", expand=True, padx=2)
        ttk.Button(btns, text="❌ Limpiar", command=self.clear_list, bootstyle="outline-danger").pack(side="left", padx=2)

        # Listbox
        list_scroll = ttk.Frame(left)
        list_scroll.pack(fill="both", expand=True)
        scroll = ttk.Scrollbar(list_scroll)
        scroll.pack(side="right", fill="y")
        self.listbox = tk.Listbox(list_scroll, font=("Consolas", 10), selectmode="SINGLE", borderwidth=0)
        self.listbox.pack(side="left", fill="both", expand=True)
        self.listbox.config(yscrollcommand=scroll.set)
        scroll.config(command=self.listbox.yview)
        self.listbox.bind('<<ListboxSelect>>', self.on_select_list)

        # === DERECHA: EDITOR ===
        right = ttk.Frame(paned, padding=(10,0,0,0))
        paned.add(right, weight=3)

        # PREVIEW AREA
        preview = ttk.Frame(right)
        preview.pack(fill="both", expand=True)

        # Frame Original
        f_orig = ttk.Labelframe(preview, text=" Original ", padding=10, bootstyle="secondary")
        f_orig.pack(side="left", fill="both", expand=True, padx=5)
        self.lbl_orig = ttk.Label(f_orig, text="Selecciona una imagen", anchor="center")
        self.lbl_orig.pack(fill="both", expand=True)
        self.lbl_orig_info = ttk.Label(f_orig, text="-", font=("Consolas", 9))
        self.lbl_orig_info.pack(side="bottom", fill="x")

        # Frame Resultado
        f_proc = ttk.Labelframe(preview, text=" Resultado (Vista Previa) ", padding=10, bootstyle="success")
        f_proc.pack(side="left", fill="both", expand=True, padx=5)
        self.lbl_proc = ttk.Label(f_proc, text="...", anchor="center")
        self.lbl_proc.pack(fill="both", expand=True)
        self.lbl_proc_info = ttk.Label(f_proc, text="-", font=("Consolas", 9, "bold"), bootstyle="success")
        self.lbl_proc_info.pack(side="bottom", fill="x")

        # CONTROLES (SECCIÓN CLAVE)
        ctrl_frame = ttk.Labelframe(self.root, text="Panel de Configuración (Afecta a la imagen seleccionada)", padding=20, bootstyle="info")
        ctrl_frame.pack(fill="x", padx=10, pady=10)

        # Fila 1: Widgets
        row1 = ttk.Frame(ctrl_frame)
        row1.pack(fill="x")

        # Formato
        c1 = ttk.Frame(row1)
        c1.pack(side="left", padx=15)
        ttk.Label(c1, text="Formato").pack(anchor="w")
        formats = ["AVIF", "HEIC", "WEBP", "JPEG", "PNG", "GIF", "PSD", "PDF", "BMP", "TIFF", "ICO"]
        cb = ttk.Combobox(c1, textvariable=self.var_fmt, values=formats, state="readonly", width=10)
        cb.pack(pady=5)
        cb.bind("<<ComboboxSelected>>", self.on_ui_change)

        # Calidad
        c2 = ttk.Frame(row1)
        c2.pack(side="left", fill="x", expand=True, padx=15)
        self.lbl_qual_txt = ttk.Label(c2, text=f"Calidad: {self.var_qual.get()}%")
        self.lbl_qual_txt.pack(anchor="w")
        sc_q = ttk.Scale(c2, from_=1, to=100, variable=self.var_qual, command=lambda x: self.update_txt_labels())
        sc_q.pack(fill="x", pady=5)
        sc_q.bind("<ButtonRelease-1>", self.on_ui_change) # Solo actualiza al soltar

        # Escala
        c3 = ttk.Frame(row1)
        c3.pack(side="left", fill="x", expand=True, padx=15)
        self.lbl_scale_txt = ttk.Label(c3, text=f"Escala: {self.var_scale.get()}%")
        self.lbl_scale_txt.pack(anchor="w")
        sc_s = ttk.Scale(c3, from_=10, to=100, variable=self.var_scale, command=lambda x: self.update_txt_labels())
        sc_s.pack(fill="x", pady=5)
        sc_s.bind("<ButtonRelease-1>", self.on_ui_change)

        # Fondo
        c4 = ttk.Frame(row1)
        c4.pack(side="left", padx=15)
        ttk.Label(c4, text="Fondo").pack(anchor="w")
        ttk.Radiobutton(c4, text="Blanco", variable=self.var_bg, value="BLANCO", command=self.on_ui_change).pack(anchor="w")
        ttk.Radiobutton(c4, text="Negro", variable=self.var_bg, value="NEGRO", command=self.on_ui_change).pack(anchor="w")

        # BOTÓN PODEROSO: APLICAR A TODOS
        c5 = ttk.Frame(row1)
        c5.pack(side="left", padx=15)
        ttk.Button(c5, text="⚡ APLICAR A TODOS", command=self.apply_settings_to_all, bootstyle="warning-outline").pack(fill="x", ipady=5)
        ttk.Label(c5, text="(Copia esto a la lista)", font=("Arial", 7)).pack()

        # Fila 2: Ruta y Exportar
        row2 = ttk.Frame(ctrl_frame)
        row2.pack(fill="x", pady=(15, 0))

        # Ruta
        p_frame = ttk.Frame(row2)
        p_frame.pack(side="left", fill="x", expand=True)
        ttk.Label(p_frame, text="Guardar en:", font=("Arial", 9, "bold")).pack(side="left")
        ttk.Entry(p_frame, textvariable=self.var_out_dir).pack(side="left", fill="x", expand=True, padx=5)
        ttk.Button(p_frame, text="📂", width=3, command=self.choose_dir).pack(side="left")

        # Botones Acción
        ttk.Button(row2, text="Guardar ESTA Imagen", command=self.save_single, bootstyle="info").pack(side="right", padx=5)
        ttk.Button(row2, text="🚀 PROCESAR LOTE COMPLETO", command=self.process_batch, bootstyle="success").pack(side="right", padx=5, ipady=5)

    # --- LOGICA UI ---
    def update_txt_labels(self):
        self.lbl_qual_txt.config(text=f"Calidad: {int(self.var_qual.get())}%")
        self.lbl_scale_txt.config(text=f"Escala: {int(self.var_scale.get())}%")

    def add_images(self):
        files = filedialog.askopenfilenames(filetypes=[("Imágenes", "*.*")])
        if files:
            for f in files:
                # Verificar duplicados
                if not any(item.path == f for item in self.items):
                    new_item = ImageItem(f)
                    self.items.append(new_item)
                    self.listbox.insert(tk.END, new_item.name)
            
            # Autoseleccionar si es el primero
            if len(self.items) > 0 and not self.current_item:
                self.listbox.select_set(0)
                self.on_select_list(None)

    def clear_list(self):
        self.items = []
        self.listbox.delete(0, tk.END)
        self.current_item = None
        self.lbl_orig.config(image='', text="")
        self.lbl_proc.config(image='', text="")

    def on_select_list(self, event):
        sel = self.listbox.curselection()
        if not sel: return
        
        idx = sel[0]
        self.current_item = self.items[idx]
        
        # 1. CARGAR DATOS DEL ITEM EN LA UI
        # Usamos el flag ignore para que al setear los valores no dispare "on_ui_change"
        self.ignore_ui_events = True
        self.var_fmt.set(self.current_item.fmt)
        self.var_qual.set(self.current_item.quality)
        self.var_scale.set(self.current_item.scale)
        self.var_bg.set(self.current_item.bg)
        self.update_txt_labels()
        self.ignore_ui_events = False
        
        # 2. CARGAR IMAGEN Y PREVIEW
        self.load_image_preview()

    def on_ui_change(self, event=None):
        """Cuando el usuario mueve un slider o cambia formato"""
        if self.ignore_ui_events or not self.current_item: return
        
        # Actualizamos el OBJETO en memoria con lo que dice la UI
        self.current_item.fmt = self.var_fmt.get()
        self.current_item.quality = int(self.var_qual.get())
        self.current_item.scale = int(self.var_scale.get())
        self.current_item.bg = self.var_bg.get()
        
        # Regeneramos preview
        self.generate_preview()

    def apply_settings_to_all(self):
        """Toma la config actual y la pega en TODOS los items"""
        if not self.current_item: return
        
        fmt = self.var_fmt.get()
        q = self.var_qual.get()
        s = self.var_scale.get()
        bg = self.var_bg.get()
        
        for item in self.items:
            item.fmt = fmt
            item.quality = q
            item.scale = s
            item.bg = bg
            
        messagebox.showinfo("Aplicado", f"Configuración aplicada a {len(self.items)} imágenes.\nAhora todas se exportarán como {fmt}.")

    def choose_dir(self):
        d = filedialog.askdirectory()
        if d: self.var_out_dir.set(d)

    # --- CORE DE IMAGEN ---
    def load_image_preview(self):
        try:
            path = self.current_item.path
            self.original_image = Image.open(path)
            size = os.path.getsize(path)
            
            # Mostrar Original
            self.show_thumb(self.original_image, self.lbl_orig)
            self.lbl_orig_info.config(text=f"{self.current_item.name}\n{self.format_bytes(size)}")
            
            # Generar Preview
            self.generate_preview()
            
        except Exception as e:
            print(e)

    def generate_preview(self):
        if not self.original_image: return
        try:
            # Usamos los datos guardados en el objeto item
            img_bytes = self.process_image(self.original_image, self.current_item)
            self.processed_buffer = img_bytes
            
            # Mostrar Resultado
            try:
                prev = Image.open(io.BytesIO(img_bytes))
            except:
                prev = self.original_image # Fallback
            
            self.show_thumb(prev, self.lbl_proc)
            
            # Stats
            orig_size = os.path.getsize(self.current_item.path)
            new_size = len(img_bytes)
            diff = orig_size - new_size
            diff_str = f"-{self.format_bytes(diff)}" if diff > 0 else f"+{self.format_bytes(abs(diff))}"
            col = "success" if diff > 0 else "danger"
            self.lbl_proc_info.config(text=f"{self.current_item.fmt} | {self.format_bytes(new_size)} ({diff_str})", bootstyle=col)
            
        except Exception as e:
            self.lbl_proc_info.config(text=f"Error: {e}", bootstyle="danger")

    def process_image(self, pil_img, item_config):
        """Convierte una imagen según su configuración individual"""
        target = pil_img.copy()
        
        # 1. Escala
        if item_config.scale < 100:
            w, h = target.size
            target = target.resize((int(w*(item_config.scale/100)), int(h*(item_config.scale/100))), Image.Resampling.LANCZOS)
            
        # 2. Formato y Transparencia
        fmt = item_config.fmt
        
        # Mapeo a PIL
        pil_fmt = fmt
        if fmt == "HEIC": pil_fmt = "HEIF"
        
        no_alpha = ["JPEG", "BMP", "EPS", "PDF"]
        if (pil_fmt in no_alpha) and target.mode in ("RGBA", "LA", "P"):
            bg_col = (255, 255, 255) if item_config.bg == "BLANCO" else (0, 0, 0)
            bg = Image.new("RGB", target.size, bg_col)
            if target.mode == 'P': target = target.convert('RGBA')
            try: bg.paste(target, mask=target.split()[3])
            except: bg.paste(target)
            target = bg
        elif target.mode == "P" and pil_fmt not in ["GIF", "PNG"]:
            target = target.convert("RGB")
            
        # 3. Guardar
        buffer = io.BytesIO()
        save_args = {}
        
        q = int(item_config.quality)
        if pil_fmt == "AVIF": save_args = {"quality": q, "speed": 6}
        elif pil_fmt == "JPEG": save_args = {"quality": q, "optimize": True}
        elif pil_fmt == "WEBP": save_args = {"quality": q, "method": 6}
        elif pil_fmt == "PNG": save_args = {"optimize": True, "compress_level": 6}
        elif pil_fmt == "ICO":
             if target.size[0] > 256: target = target.resize((256, 256), Image.Resampling.LANCZOS)
             
        target.save(buffer, format=pil_fmt, **save_args)
        return buffer.getvalue()

    def show_thumb(self, img, lbl):
        w, h = 480, 350
        cp = img.copy()
        cp.thumbnail((w, h), Image.Resampling.LANCZOS)
        tk_img = ImageTk.PhotoImage(cp)
        lbl.config(image=tk_img)
        lbl.image = tk_img

    def format_bytes(self, size):
        for unit in ['B', 'KB', 'MB']:
            if size < 1024: return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} GB"

    # --- EXPORTAR ---
    def save_single(self):
        if not self.processed_buffer or not self.current_item: return
        ext = self.current_item.fmt.lower().replace("jpeg", "jpg").replace("heic", "heic")
        path = filedialog.asksaveasfilename(defaultextension=f".{ext}", initialfile=f"processed_{self.current_item.name}")
        if path:
            with open(path, "wb") as f: f.write(self.processed_buffer)
            messagebox.showinfo("Guardado", f"Archivo guardado.")

    def process_batch(self):
        if not self.items: return
        out_dir = self.var_out_dir.get()
        if not os.path.exists(out_dir): os.makedirs(out_dir)
        
        count = 0
        
        # Ventana Progreso
        prog = tk.Toplevel(self.root)
        prog.title("Procesando...")
        prog.geometry("300x150")
        ttk.Label(prog, text="Trabajando...", font=("Arial", 12, "bold")).pack(pady=10)
        p_bar = ttk.Progressbar(prog, maximum=len(self.items))
        p_bar.pack(fill="x", padx=20)
        
        for i, item in enumerate(self.items):
            try:
                with Image.open(item.path) as img:
                    img_bytes = self.process_image(img, item)
                    
                    # Nombre Salida
                    base = os.path.splitext(item.name)[0]
                    ext = item.fmt.lower().replace("jpeg", "jpg")
                    out_path = os.path.join(out_dir, f"{base}.{ext}")
                    
                    with open(out_path, "wb") as f: f.write(img_bytes)
                count += 1
            except Exception as e: print(e)
            
            p_bar['value'] = i+1
            prog.update()
            
        prog.destroy()
        messagebox.showinfo("Finalizado", f"Se procesaron {count} imágenes en:\n{out_dir}")

if __name__ == "__main__":
    app_window = ttk.Window(themename="darkly") 
    app = UniversalGranularConverter(app_window)
    app_window.mainloop()