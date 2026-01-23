import sys
import os
import subprocess
import io
import tkinter as tk
from tkinter import filedialog, messagebox

# --- AUTO-INSTALADOR ---
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
from PIL import Image, ImageTk, ImageDraw, ImageFont
import pillow_avif
import pillow_heif

pillow_heif.register_heif_opener()

# --- CLASE INSPECTOR (Misma que antes) ---
class AdvancedInspector(tk.Toplevel):
    def __init__(self, master, img_orig, img_proc, info_orig, info_proc):
        super().__init__(master)
        self.title("Inspector de Precisión")
        self.geometry("1200x800")
        self.pil_orig = img_orig.convert("RGBA")
        self.pil_proc = img_proc.convert("RGBA")
        if self.pil_orig.size != self.pil_proc.size:
            self.pil_proc = self.pil_proc.resize(self.pil_orig.size, Image.Resampling.NEAREST)
        self.base_w, self.base_h = self.pil_orig.size
        self.txt_orig = info_orig
        self.txt_proc = info_proc
        self.zoom = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self.slider_x = 0.5 
        self.create_ui()
        self.bind_events()
        self.render_view()
        
    def create_ui(self):
        self.canvas = tk.Canvas(self, bg="#1a1a1a", highlightthickness=0, cursor="crosshair")
        self.canvas.pack(fill="both", expand=True)
        self.lbl_help = tk.Label(self, text="Rueda: Zoom | Click+Arrastrar: Mover | Mover Mouse: Cortina", bg="black", fg="white", font=("Arial", 8))
        self.lbl_help.place(relx=0.5, rely=0.98, anchor="s")

    def bind_events(self):
        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.canvas.bind("<MouseWheel>", self.on_zoom)
        self.canvas.bind("<Button-4>", self.on_zoom)
        self.canvas.bind("<Button-5>", self.on_zoom)
        self.canvas.bind("<ButtonPress-1>", self.start_pan)
        self.canvas.bind("<B1-Motion>", self.do_pan)
        self.bind("<Configure>", self.on_resize)

    def on_resize(self, event):
        if event.widget == self: self.render_view()
    def start_pan(self, event):
        self.drag_start_x = event.x
        self.drag_start_y = event.y
    def do_pan(self, event):
        dx = event.x - self.drag_start_x
        dy = event.y - self.drag_start_y
        self.pan_x += dx
        self.pan_y += dy
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        self.render_view()
    def on_mouse_move(self, event):
        w = self.canvas.winfo_width()
        if w > 0:
            self.slider_x = event.x / w
            self.render_view()
    def on_zoom(self, event):
        factor = 1.1 if (event.delta > 0 or event.num == 4) else 0.9
        new_zoom = self.zoom * factor
        if new_zoom < 0.1: new_zoom = 0.1
        if new_zoom > 20.0: new_zoom = 20.0
        self.zoom = new_zoom
        self.render_view()
    def render_view(self):
        cv_w = self.canvas.winfo_width()
        cv_h = self.canvas.winfo_height()
        if cv_w < 10: return
        zw = int(self.base_w * self.zoom)
        zh = int(self.base_h * self.zoom)
        final_img = Image.new("RGBA", (cv_w, cv_h), (30, 30, 30, 255))
        center_x = self.pan_x + (cv_w // 2)
        center_y = self.pan_y + (cv_h // 2)
        paste_x = center_x - (zw // 2)
        paste_y = center_y - (zh // 2)
        left_in_img = -paste_x / self.zoom
        top_in_img = -paste_y / self.zoom
        right_in_img = (cv_w - paste_x) / self.zoom
        bottom_in_img = (cv_h - paste_y) / self.zoom
        crop_box = (max(0, int(left_in_img)), max(0, int(top_in_img)), min(self.base_w, int(right_in_img)), min(self.base_h, int(bottom_in_img)))
        
        if crop_box[2] > crop_box[0] and crop_box[3] > crop_box[1]:
            part_orig = self.pil_orig.crop(crop_box)
            part_proc = self.pil_proc.crop(crop_box)
            target_size = (int((crop_box[2]-crop_box[0])*self.zoom), int((crop_box[3]-crop_box[1])*self.zoom))
            part_orig = part_orig.resize(target_size, Image.Resampling.NEAREST)
            part_proc = part_proc.resize(target_size, Image.Resampling.NEAREST)
            split_x = int(self.slider_x * cv_w)
            rel_split = split_x - max(0, int(paste_x + crop_box[0]*self.zoom))
            if paste_x > 0: rel_split = split_x - paste_x
            combined = part_proc.copy()
            if rel_split > 0:
                crop_w = min(rel_split, combined.width)
                section = part_orig.crop((0, 0, crop_w, combined.height))
                combined.paste(section, (0, 0))
            dest_x = max(0, paste_x + int(crop_box[0]*self.zoom))
            dest_y = max(0, paste_y + int(crop_box[1]*self.zoom))
            final_img.paste(combined, (dest_x, dest_y))
            
        draw = ImageDraw.Draw(final_img)
        split_line_x = int(self.slider_x * cv_w)
        draw.line([(split_line_x, 0), (split_line_x, cv_h)], fill="#00ff00", width=2)
        self.draw_hud(draw, 20, 20, "ORIGINAL", self.txt_orig, align="left", color=(200, 200, 200))
        self.draw_hud(draw, cv_w - 20, 20, "RESULTADO", self.txt_proc, align="right", color=(100, 255, 100))
        self.tk_image = ImageTk.PhotoImage(final_img)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, image=self.tk_image, anchor="nw")
    def draw_hud(self, draw, x, y, title, details, align="left", color="white"):
        lines = details.split('\n')
        font_title = ImageFont.load_default()
        line_h = 15
        box_w = 200
        box_h = (len(lines)+1) * line_h + 10
        box_x = x if align == "left" else x - box_w
        draw.rectangle([box_x, y, box_x + box_w, y + box_h], fill=(0, 0, 0, 180), outline=None)
        cur_y = y + 5
        draw.text((box_x + 10, cur_y), title, fill=color, font=font_title)
        cur_y += 20
        for line in lines:
            draw.text((box_x + 10, cur_y), line, fill="white", font=font_title)
            cur_y += line_h

# --- GESTOR DE ESTADO DE IMAGEN ---
class ImageItem:
    def __init__(self, path):
        self.path = path
        self.name = os.path.basename(path)
        self.fmt = "AVIF"
        self.quality = 80
        self.scale = 100
        self.bg = "BLANCO"
        self.subsample = False # Nuevo: Chroma Subsampling

class UniversalGranularConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Tarquitet - Laboratorio de Imagen Pro +")
        self.root.geometry("1450x950")
        
        self.items = []              
        self.current_item = None     
        self.original_image = None   
        self.processed_buffer = None
        
        # Variables Vinculadas
        self.var_fmt = tk.StringVar(value="AVIF")
        self.var_qual = tk.IntVar(value=80)
        self.var_scale = tk.IntVar(value=100)
        self.var_bg = tk.StringVar(value="BLANCO")
        self.var_subsample = tk.BooleanVar(value=False) # Variable para Checkbox
        self.var_out_dir = tk.StringVar(value=os.getcwd())
        
        self.ignore_ui_events = False 
        self.build_ui()

    def build_ui(self):
        # HEADER
        header = ttk.Frame(self.root, padding=20)
        header.pack(fill="x")
        ttk.Label(header, text="LABORATORIO DE IMAGEN PRO +", font=("Helvetica", 18, "bold"), bootstyle="primary").pack(side="left")

        # MAIN
        paned = ttk.PanedWindow(self.root, orient="horizontal")
        paned.pack(fill="both", expand=True, padx=10, pady=5)

        # IZQUIERDA
        left = ttk.Frame(paned, padding=(0,0,10,0))
        paned.add(left, weight=1)
        
        btns = ttk.Frame(left)
        btns.pack(fill="x", pady=5)
        ttk.Button(btns, text="➕ Agregar", command=self.add_images, bootstyle="outline-primary").pack(side="left", fill="x", expand=True, padx=2)
        ttk.Button(btns, text="❌ Limpiar", command=self.clear_list, bootstyle="outline-danger").pack(side="left")

        list_scroll = ttk.Frame(left)
        list_scroll.pack(fill="both", expand=True)
        scroll = ttk.Scrollbar(list_scroll)
        scroll.pack(side="right", fill="y")
        self.listbox = tk.Listbox(list_scroll, font=("Consolas", 10), selectmode="SINGLE", borderwidth=0)
        self.listbox.pack(side="left", fill="both", expand=True)
        self.listbox.config(yscrollcommand=scroll.set)
        scroll.config(command=self.listbox.yview)
        self.listbox.bind('<<ListboxSelect>>', self.on_select_list)

        # DERECHA
        right = ttk.Frame(paned, padding=(10,0,0,0))
        paned.add(right, weight=3)

        # PREVIEW
        preview = ttk.Frame(right)
        preview.pack(fill="both", expand=True)
        f_prev = ttk.Labelframe(preview, text=" Vista Previa (Click para Inspector) ", padding=10, bootstyle="secondary")
        f_prev.pack(fill="both", expand=True)
        self.lbl_preview = ttk.Label(f_prev, text="Selecciona una imagen...", anchor="center", cursor="crosshair")
        self.lbl_preview.pack(fill="both", expand=True)
        self.lbl_info_bar = ttk.Label(f_prev, text="-", font=("Consolas", 10), bootstyle="inverse-secondary", anchor="center")
        self.lbl_info_bar.pack(side="bottom", fill="x")
        self.lbl_preview.bind("<Button-1>", self.open_inspector)

        # PANEL DE CONTROLES REVISADO
        ctrl_frame = ttk.Labelframe(self.root, text="Ajustes de Compresión", padding=20, bootstyle="info")
        ctrl_frame.pack(fill="x", padx=10, pady=10)

        # Layout Flexible
        row1 = ttk.Frame(ctrl_frame)
        row1.pack(fill="x")

        # 1. FORMATO
        c1 = ttk.Frame(row1)
        c1.pack(side="left", padx=10, anchor="n")
        ttk.Label(c1, text="Formato").pack(anchor="w")
        formats = ["AVIF", "HEIC", "WEBP", "JPEG", "PNG", "GIF", "PSD", "PDF", "BMP", "ICO"]
        cb = ttk.Combobox(c1, textvariable=self.var_fmt, values=formats, state="readonly", width=8)
        cb.pack(pady=5)
        cb.bind("<<ComboboxSelected>>", self.on_ui_change)

        # 2. CALIDAD (SLIDER + SPINBOX)
        c2 = ttk.Frame(row1)
        c2.pack(side="left", fill="x", expand=True, padx=10, anchor="n")
        
        h2 = ttk.Frame(c2) # Header interno
        h2.pack(fill="x")
        ttk.Label(h2, text="Calidad %").pack(side="left")
        # Spinbox Manual
        sp_q = ttk.Spinbox(h2, from_=1, to=100, textvariable=self.var_qual, width=5, bootstyle="info")
        sp_q.pack(side="right")
        sp_q.bind("<Return>", self.on_ui_change)
        sp_q.bind("<FocusOut>", self.on_ui_change)

        sc_q = ttk.Scale(c2, from_=1, to=100, variable=self.var_qual) # Sin label texto aqui, usamos el spinbox
        sc_q.pack(fill="x", pady=5)
        sc_q.bind("<ButtonRelease-1>", self.on_ui_change)

        # 3. ESCALA (SLIDER + SPINBOX)
        c3 = ttk.Frame(row1)
        c3.pack(side="left", fill="x", expand=True, padx=10, anchor="n")
        
        h3 = ttk.Frame(c3)
        h3.pack(fill="x")
        ttk.Label(h3, text="Escala %").pack(side="left")
        sp_s = ttk.Spinbox(h3, from_=1, to=100, textvariable=self.var_scale, width=5, bootstyle="info")
        sp_s.pack(side="right")
        sp_s.bind("<Return>", self.on_ui_change)
        sp_s.bind("<FocusOut>", self.on_ui_change)

        sc_s = ttk.Scale(c3, from_=10, to=100, variable=self.var_scale)
        sc_s.pack(fill="x", pady=5)
        sc_s.bind("<ButtonRelease-1>", self.on_ui_change)

        # 4. EXTRAS (FONDO + SUBSAMPLING)
        c4 = ttk.Frame(row1)
        c4.pack(side="left", padx=10, anchor="n")
        ttk.Label(c4, text="Opciones Extra").pack(anchor="w")
        
        # Opciones de Fondo
        fr_bg = ttk.Frame(c4)
        fr_bg.pack(anchor="w", pady=2)
        ttk.Label(fr_bg, text="Fondo:", font=("Arial", 8)).pack(side="left")
        ttk.Radiobutton(fr_bg, text="B", variable=self.var_bg, value="BLANCO", command=self.on_ui_change).pack(side="left")
        ttk.Radiobutton(fr_bg, text="N", variable=self.var_bg, value="NEGRO", command=self.on_ui_change).pack(side="left")

        # Checkbox Subsampling
        chk_sub = ttk.Checkbutton(c4, text="Modo Ahorro (4:2:0)", variable=self.var_subsample, command=self.on_ui_change, bootstyle="round-toggle")
        chk_sub.pack(anchor="w", pady=5)
        
        # Tooltip casero
        ttk.Label(c4, text="(Menos color, menos peso)", font=("Arial", 7), foreground="gray").pack(anchor="w")

        # Botón Aplicar Todos
        ttk.Button(row1, text="⚡ APLICAR\nA TODOS", command=self.apply_settings_to_all, bootstyle="warning-outline").pack(side="left", padx=10, ipady=10)

        # FILA 2: RUTA Y BOTONES FINALES
        row2 = ttk.Frame(ctrl_frame)
        row2.pack(fill="x", pady=(15, 0))
        ttk.Label(row2, text="Guardar en:", font=("Arial", 9, "bold")).pack(side="left")
        ttk.Entry(row2, textvariable=self.var_out_dir).pack(side="left", fill="x", expand=True, padx=5)
        ttk.Button(row2, text="📂", width=3, command=self.choose_dir).pack(side="left")
        
        ttk.Button(row2, text="Guardar ESTA Imagen", command=self.save_single, bootstyle="info").pack(side="right", padx=5)
        ttk.Button(row2, text="🚀 PROCESAR LOTE", command=self.process_batch, bootstyle="success").pack(side="right", padx=5, ipady=5)

    # --- LÓGICA CORE ACTUALIZADA ---
    def add_images(self):
        files = filedialog.askopenfilenames(filetypes=[("Imágenes", "*.*")])
        if files:
            for f in files:
                if not any(item.path == f for item in self.items):
                    self.items.append(ImageItem(f))
                    self.listbox.insert(tk.END, os.path.basename(f))
            if len(self.items) > 0 and not self.current_item:
                self.listbox.select_set(0)
                self.on_select_list(None)

    def clear_list(self):
        self.items = []
        self.listbox.delete(0, tk.END)
        self.current_item = None
        self.lbl_preview.config(image='', text="Lista Vacía")

    def on_select_list(self, event):
        sel = self.listbox.curselection()
        if not sel: return
        self.current_item = self.items[sel[0]]
        self.ignore_ui_events = True
        self.var_fmt.set(self.current_item.fmt)
        self.var_qual.set(self.current_item.quality)
        self.var_scale.set(self.current_item.scale)
        self.var_bg.set(self.current_item.bg)
        self.var_subsample.set(self.current_item.subsample)
        self.ignore_ui_events = False
        self.load_image_preview()

    def on_ui_change(self, event=None):
        if self.ignore_ui_events or not self.current_item: return
        # Validar rangos manuales
        try:
            q = int(self.var_qual.get())
            s = int(self.var_scale.get())
            if q < 1: q=1; self.var_qual.set(1)
            if q > 100: q=100; self.var_qual.set(100)
            if s < 1: s=1; self.var_scale.set(1)
            if s > 100: s=100; self.var_scale.set(100)
        except: return

        self.current_item.fmt = self.var_fmt.get()
        self.current_item.quality = q
        self.current_item.scale = s
        self.current_item.bg = self.var_bg.get()
        self.current_item.subsample = self.var_subsample.get()
        self.generate_preview()

    def apply_settings_to_all(self):
        if not self.current_item: return
        f, q, s, b, sub = self.var_fmt.get(), self.var_qual.get(), self.var_scale.get(), self.var_bg.get(), self.var_subsample.get()
        for item in self.items:
            item.fmt, item.quality, item.scale, item.bg, item.subsample = f, q, s, b, sub
        messagebox.showinfo("Hecho", "Configuración clonada.")

    def load_image_preview(self):
        try:
            self.original_image = Image.open(self.current_item.path)
            self.generate_preview()
        except Exception as e: print(e)

    def generate_preview(self):
        if not self.original_image: return
        try:
            img_bytes = self.process_image(self.original_image, self.current_item)
            self.processed_buffer = img_bytes
            try: prev = Image.open(io.BytesIO(img_bytes))
            except: prev = self.original_image
            
            # Miniatura
            w, h = 900, 500
            cp = prev.copy()
            cp.thumbnail((w, h), Image.Resampling.LANCZOS)
            tk_img = ImageTk.PhotoImage(cp)
            self.lbl_preview.config(image=tk_img)
            self.lbl_preview.image = tk_img
            
            orig_s = os.path.getsize(self.current_item.path)
            new_s = len(img_bytes)
            diff = orig_s - new_s
            diff_str = f"-{self.format_bytes(diff)}" if diff > 0 else f"+{self.format_bytes(abs(diff))}"
            col = "success" if diff > 0 else "danger"
            extra = " [4:2:0]" if self.current_item.subsample else ""
            self.lbl_info_bar.config(text=f"ORIGINAL: {self.format_bytes(orig_s)}  -->  {self.current_item.fmt}{extra}: {self.format_bytes(new_s)} ({diff_str})", bootstyle=col)
        except Exception as e: self.lbl_info_bar.config(text=f"Error: {e}", bootstyle="danger")

    def process_image(self, pil_img, item):
        target = pil_img.copy()
        if item.scale < 100:
            w, h = target.size
            target = target.resize((int(w*(item.scale/100)), int(h*(item.scale/100))), Image.Resampling.LANCZOS)
        
        fmt = item.fmt
        pil_fmt = "HEIF" if fmt == "HEIC" else fmt
        no_alpha = ["JPEG", "BMP", "EPS", "PDF"]
        if (pil_fmt in no_alpha) and target.mode in ("RGBA", "LA", "P"):
            bg_col = (255, 255, 255) if item.bg == "BLANCO" else (0, 0, 0)
            bg = Image.new("RGB", target.size, bg_col)
            if target.mode == 'P': target = target.convert('RGBA')
            try: bg.paste(target, mask=target.split()[3])
            except: bg.paste(target)
            target = bg
        elif target.mode == "P" and pil_fmt not in ["GIF", "PNG"]: target = target.convert("RGB")
            
        buffer = io.BytesIO()
        save_args = {}
        q = int(item.quality)
        
        # --- LÓGICA DE SUBSAMPLING (NUEVO) ---
        subsampling_val = 2 if item.subsample else 0 # 2 = 4:2:0 (Ahorro), 0 = 4:4:4 (Calidad)

        if pil_fmt == "AVIF": 
            # Pillow-AVIF no expone subsampling directo fácil, pero speed ayuda
            save_args = {"quality": q, "speed": 6}
        elif pil_fmt == "JPEG": 
            save_args = {"quality": q, "optimize": True, "subsampling": subsampling_val}
        elif pil_fmt == "WEBP": 
            save_args = {"quality": q, "method": 6} 
            # WebP elige subsampling basado en calidad automáticamente, 
            # pero podemos forzarlo a lossy si el usuario quiere ahorro extremo
        elif pil_fmt == "PNG": 
            save_args = {"optimize": True, "compress_level": 6}

        target.save(buffer, format=pil_fmt, **save_args)
        return buffer.getvalue()

    # --- RESTO DE FUNCIONES ---
    def open_inspector(self, event=None):
        if not self.original_image or not self.processed_buffer: return
        try:
            proc_img = Image.open(io.BytesIO(self.processed_buffer))
            orig_size = os.path.getsize(self.current_item.path)
            proc_size = len(self.processed_buffer)
            txt_orig = f"Dim: {self.original_image.size}\nPeso: {self.format_bytes(orig_size)}"
            txt_proc = f"Fmt: {self.current_item.fmt}\nCalidad: {self.current_item.quality}\nPeso: {self.format_bytes(proc_size)}"
            AdvancedInspector(self.root, self.original_image, proc_img, txt_orig, txt_proc)
        except Exception as e: messagebox.showerror("Error", str(e))

    def choose_dir(self):
        d = filedialog.askdirectory()
        if d: self.var_out_dir.set(d)
    def format_bytes(self, size):
        for unit in ['B', 'KB', 'MB']:
            if size < 1024: return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} GB"
    def save_single(self):
        if not self.processed_buffer: return
        path = filedialog.asksaveasfilename(defaultextension=f".{self.current_item.fmt.lower()}")
        if path:
            with open(path, "wb") as f: f.write(self.processed_buffer)
            messagebox.showinfo("Guardado", "Archivo guardado.")
    def process_batch(self):
        if not self.items: return
        out_dir = self.var_out_dir.get()
        if not os.path.exists(out_dir): os.makedirs(out_dir)
        prog = tk.Toplevel(self.root)
        prog.title("Procesando...")
        p_bar = ttk.Progressbar(prog, maximum=len(self.items)); p_bar.pack(fill="x", padx=20, pady=20)
        for i, item in enumerate(self.items):
            try:
                with Image.open(item.path) as img:
                    img_bytes = self.process_image(img, item)
                    base = os.path.splitext(item.name)[0]
                    ext = item.fmt.lower().replace("jpeg", "jpg")
                    with open(os.path.join(out_dir, f"{base}.{ext}"), "wb") as f: f.write(img_bytes)
            except: pass
            p_bar['value'] = i+1
            prog.update()
        prog.destroy()
        messagebox.showinfo("Fin", f"Procesados {len(self.items)} archivos.")

if __name__ == "__main__":
    app_window = ttk.Window(themename="darkly") 
    app = UniversalGranularConverter(app_window)
    app_window.mainloop()