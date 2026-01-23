import sys
import os
import subprocess
import io
import json
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

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
from PIL import Image, ImageTk, ImageDraw, ImageFont, ImageOps
import pillow_avif
import pillow_heif

pillow_heif.register_heif_opener()

# --- CLASE INSPECTOR (Visor con Zoom/Cortina) ---
class AdvancedInspector(tk.Toplevel):
    def __init__(self, master, img_orig, img_proc, info_orig, info_proc):
        super().__init__(master)
        self.title("Inspector Omega")
        self.geometry("1200x800")
        self.pil_orig = img_orig.convert("RGBA")
        self.pil_proc = img_proc.convert("RGBA")
        if self.pil_orig.size != self.pil_proc.size:
            self.pil_proc = self.pil_proc.resize(self.pil_orig.size, Image.Resampling.NEAREST)
        self.base_w, self.base_h = self.pil_orig.size
        self.txt_orig = info_orig; self.txt_proc = info_proc
        self.zoom = 1.0; self.pan_x = 0; self.pan_y = 0; self.slider_x = 0.5 
        self.create_ui(); self.bind_events(); self.render_view()
        
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
        self.drag_start_x = event.x; self.drag_start_y = event.y
    def do_pan(self, event):
        dx = event.x - self.drag_start_x; dy = event.y - self.drag_start_y
        self.pan_x += dx; self.pan_y += dy
        self.drag_start_x = event.x; self.drag_start_y = event.y
        self.render_view()
    def on_mouse_move(self, event):
        w = self.canvas.winfo_width()
        if w > 0: self.slider_x = event.x / w; self.render_view()
    def on_zoom(self, event):
        factor = 1.1 if (event.delta > 0 or event.num == 4) else 0.9
        new_zoom = self.zoom * factor
        if new_zoom < 0.1: new_zoom = 0.1
        if new_zoom > 20.0: new_zoom = 20.0
        self.zoom = new_zoom; self.render_view()
        
    def render_view(self):
        cv_w = self.canvas.winfo_width(); cv_h = self.canvas.winfo_height()
        if cv_w < 10: return
        zw = int(self.base_w * self.zoom); zh = int(self.base_h * self.zoom)
        final_img = Image.new("RGBA", (cv_w, cv_h), (30, 30, 30, 255))
        center_x = self.pan_x + (cv_w // 2); center_y = self.pan_y + (cv_h // 2)
        paste_x = center_x - (zw // 2); paste_y = center_y - (zh // 2)
        left_in_img = -paste_x / self.zoom; top_in_img = -paste_y / self.zoom
        right_in_img = (cv_w - paste_x) / self.zoom; bottom_in_img = (cv_h - paste_y) / self.zoom
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
        lines = details.split('\n'); font_title = ImageFont.load_default()
        line_h = 15; box_w = 200; box_h = (len(lines)+1) * line_h + 10
        box_x = x if align == "left" else x - box_w
        draw.rectangle([box_x, y, box_x + box_w, y + box_h], fill=(0, 0, 0, 180), outline=None)
        cur_y = y + 5
        draw.text((box_x + 10, cur_y), title, fill=color, font=font_title); cur_y += 20
        for line in lines:
            draw.text((box_x + 10, cur_y), line, fill="white", font=font_title); cur_y += line_h

# --- GESTOR DE DATOS ---
class ImageItem:
    def __init__(self, path):
        self.path = path
        self.name = os.path.basename(path)
        # Config Imagen
        self.fmt = "AVIF"
        self.quality = 80
        self.scale = 100
        self.bg = "BLANCO"
        self.subsample = False
        self.grayscale = False # Nuevo
        self.rotate = 0        # Nuevo (0, 90, 180, 270)
        self.flip_h = False    # Nuevo
        # Metadatos
        self.keep_exif = False
        self.wm_text = ""
        self.wm_opacity = 50
        self.prefix = ""

class UniversalOmegaConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Tarquitet - OMEGA Converter")
        self.root.geometry("1600x950")
        
        self.items = []              
        self.current_item = None     
        self.original_image = None   
        self.processed_buffer = None
        
        # Variables Vinculadas
        self.var_fmt = tk.StringVar(value="AVIF")
        self.var_qual = tk.IntVar(value=80)
        self.var_scale = tk.IntVar(value=100)
        self.var_bg = tk.StringVar(value="BLANCO")
        self.var_subsample = tk.BooleanVar(value=False)
        self.var_grayscale = tk.BooleanVar(value=False) # BW
        self.var_exif = tk.BooleanVar(value=False)
        
        self.var_wm_text = tk.StringVar(value="")
        self.var_wm_opacity = tk.IntVar(value=50)
        self.var_prefix = tk.StringVar(value="")
        self.var_out_dir = tk.StringVar(value=os.getcwd())
        
        self.presets_file = "presets.json"
        self.ignore_ui_events = False 
        self.build_ui()

    def build_ui(self):
        # HEADER
        header = ttk.Frame(self.root, padding=20)
        header.pack(fill="x")
        ttk.Label(header, text="OMEGA CONVERTER", font=("Helvetica", 18, "bold"), bootstyle="primary").pack(side="left")
        
        # Presets Area
        p_area = ttk.Frame(header)
        p_area.pack(side="right")
        ttk.Label(p_area, text="Presets:").pack(side="left", padx=5)
        self.cb_presets = ttk.Combobox(p_area, values=self.load_preset_names(), state="readonly", width=15)
        self.cb_presets.pack(side="left")
        ttk.Button(p_area, text="💾 Guardar", command=self.save_preset, bootstyle="secondary-outline").pack(side="left", padx=2)
        ttk.Button(p_area, text="📂 Cargar", command=self.apply_preset, bootstyle="info-outline").pack(side="left", padx=2)

        paned = ttk.PanedWindow(self.root, orient="horizontal")
        paned.pack(fill="both", expand=True, padx=10, pady=5)

        # IZQUIERDA: LISTA
        left = ttk.Frame(paned, padding=(0,0,10,0))
        paned.add(left, weight=1)
        
        btns = ttk.Frame(left)
        btns.pack(fill="x", pady=5)
        ttk.Button(btns, text="➕ Agregar", command=self.add_images, bootstyle="outline-primary").pack(side="left", fill="x", expand=True)
        ttk.Button(btns, text="Limpiar", command=self.clear_list, bootstyle="outline-danger").pack(side="left", padx=2)

        list_scroll = ttk.Frame(left)
        list_scroll.pack(fill="both", expand=True)
        scroll = ttk.Scrollbar(list_scroll)
        scroll.pack(side="right", fill="y")
        self.listbox = tk.Listbox(list_scroll, font=("Consolas", 10), selectmode="SINGLE", borderwidth=0)
        self.listbox.pack(side="left", fill="both", expand=True)
        self.listbox.config(yscrollcommand=scroll.set)
        scroll.config(command=self.listbox.yview)
        self.listbox.bind('<<ListboxSelect>>', self.on_select_list)

        # DERECHA: PREVIEW + CONTROLES
        right = ttk.Frame(paned, padding=(10,0,0,0))
        paned.add(right, weight=3)

        preview = ttk.Frame(right)
        preview.pack(fill="both", expand=True)
        f_prev = ttk.Labelframe(preview, text=" Vista Previa (Click para Inspector) ", padding=10, bootstyle="secondary")
        f_prev.pack(fill="both", expand=True)
        self.lbl_preview = ttk.Label(f_prev, text="Arrastra imágenes...", anchor="center", cursor="crosshair")
        self.lbl_preview.pack(fill="both", expand=True)
        self.lbl_info = ttk.Label(f_prev, text="-", font=("Consolas", 10), bootstyle="inverse-secondary", anchor="center")
        self.lbl_info.pack(side="bottom", fill="x")
        self.lbl_preview.bind("<Button-1>", self.open_inspector)

        # --- PANEL DE CONTROL (TABS) ---
        notebook = ttk.Notebook(right, bootstyle="info")
        notebook.pack(fill="x", pady=10)

        # TAB 1: BÁSICO + EDICIÓN
        tab1 = ttk.Frame(notebook, padding=15)
        notebook.add(tab1, text="Imagen & Edición")
        
        r0 = ttk.Frame(tab1); r0.pack(fill="x", pady=(0,10))
        
        # Edición Rápida
        ef = ttk.Labelframe(r0, text="Edición Rápida", padding=5)
        ef.pack(side="left", fill="y", padx=5)
        ttk.Button(ef, text="⟲", command=lambda: self.rotate_img(90), bootstyle="secondary-outline").pack(side="left", padx=2)
        ttk.Button(ef, text="⟳", command=lambda: self.rotate_img(-90), bootstyle="secondary-outline").pack(side="left", padx=2)
        ttk.Button(ef, text="⇄", command=self.flip_img, bootstyle="secondary-outline").pack(side="left", padx=2)
        ttk.Checkbutton(ef, text="B/N", variable=self.var_grayscale, command=self.on_ui_change, bootstyle="round-toggle").pack(side="left", padx=10)

        r1 = ttk.Frame(tab1); r1.pack(fill="x", pady=5)
        f1 = ttk.Frame(r1); f1.pack(side="left", padx=(0,15))
        ttk.Label(f1, text="Formato").pack(anchor="w")
        cb = ttk.Combobox(f1, textvariable=self.var_fmt, values=["AVIF", "HEIC", "WEBP", "JPEG", "PNG", "GIF", "PSD", "PDF"], state="readonly", width=8)
        cb.pack(); cb.bind("<<ComboboxSelected>>", self.on_ui_change)

        f2 = ttk.Frame(r1); f2.pack(side="left", fill="x", expand=True, padx=10)
        hf2 = ttk.Frame(f2); hf2.pack(fill="x")
        ttk.Label(hf2, text="Calidad").pack(side="left")
        sp_q = ttk.Spinbox(hf2, from_=1, to=100, textvariable=self.var_qual, width=5)
        sp_q.pack(side="right"); sp_q.bind("<Return>", self.on_ui_change)
        ttk.Scale(f2, from_=1, to=100, variable=self.var_qual, command=lambda x: self.on_ui_change()).pack(fill="x")

        f3 = ttk.Frame(r1); f3.pack(side="left", fill="x", expand=True, padx=10)
        hf3 = ttk.Frame(f3); hf3.pack(fill="x")
        ttk.Label(hf3, text="Escala").pack(side="left")
        sp_s = ttk.Spinbox(hf3, from_=1, to=100, textvariable=self.var_scale, width=5)
        sp_s.pack(side="right"); sp_s.bind("<Return>", self.on_ui_change)
        ttk.Scale(f3, from_=10, to=100, variable=self.var_scale, command=lambda x: self.on_ui_change()).pack(fill="x")

        r2 = ttk.Frame(tab1); r2.pack(fill="x", pady=10)
        ttk.Checkbutton(r2, text="Modo Ahorro (4:2:0)", variable=self.var_subsample, command=self.on_ui_change, bootstyle="round-toggle").pack(side="left", padx=10)
        ttk.Checkbutton(r2, text="Mantener Metadatos", variable=self.var_exif, command=self.on_ui_change, bootstyle="round-toggle").pack(side="left", padx=10)

        # TAB 2: MARCA & RENOMBRADO
        tab2 = ttk.Frame(notebook, padding=15)
        notebook.add(tab2, text="Marca & Salida")
        
        wm_frame = ttk.LabelFrame(tab2, text="Marca de Agua", padding=10)
        wm_frame.pack(fill="x", pady=5)
        wr1 = ttk.Frame(wm_frame); wr1.pack(fill="x")
        ttk.Label(wr1, text="Texto:").pack(side="left")
        wm_e = ttk.Entry(wr1, textvariable=self.var_wm_text); wm_e.pack(side="left", fill="x", expand=True, padx=10)
        wm_e.bind("<FocusOut>", self.on_ui_change)
        
        wr2 = ttk.Frame(wm_frame); wr2.pack(fill="x", pady=5)
        ttk.Label(wr2, text="Opacidad:").pack(side="left")
        ttk.Scale(wr2, from_=10, to=100, variable=self.var_wm_opacity, command=lambda x: self.on_ui_change()).pack(side="left", fill="x", expand=True, padx=10)
        
        rn_frame = ttk.LabelFrame(tab2, text="Renombrado", padding=10)
        rn_frame.pack(fill="x", pady=5)
        ttk.Label(rn_frame, text="Prefijo:").pack(side="left")
        rn_e = ttk.Entry(rn_frame, textvariable=self.var_prefix); rn_e.pack(side="left", fill="x", expand=True, padx=10)
        rn_e.bind("<FocusOut>", self.on_ui_change)

        # --- BOTONES FINALES ---
        final_row = ttk.Frame(right)
        final_row.pack(fill="x", pady=10)
        ttk.Button(final_row, text="⚡ APLICAR GLOBAL", command=self.apply_all, bootstyle="warning-outline").pack(side="left", padx=5)
        
        p_frame = ttk.Frame(final_row); p_frame.pack(side="left", fill="x", expand=True, padx=20)
        ttk.Entry(p_frame, textvariable=self.var_out_dir).pack(side="left", fill="x", expand=True)
        ttk.Button(p_frame, text="📂", width=3, command=self.choose_dir).pack(side="left", padx=2)
        ttk.Button(final_row, text="🚀 PROCESAR LOTE", command=self.process_batch, bootstyle="success").pack(side="right", ipady=5, padx=5)

    # --- LOGICA PRESETS ---
    def load_preset_names(self):
        if not os.path.exists(self.presets_file): return []
        try:
            with open(self.presets_file, 'r') as f:
                data = json.load(f)
                return list(data.keys())
        except: return []

    def save_preset(self):
        name = simpledialog.askstring("Nuevo Preset", "Nombre del preset (ej: Web):")
        if not name: return
        
        preset = {
            "fmt": self.var_fmt.get(), "qual": self.var_qual.get(),
            "scale": self.var_scale.get(), "bg": self.var_bg.get(),
            "sub": self.var_subsample.get(), "bw": self.var_grayscale.get(),
            "exif": self.var_exif.get(), "wm": self.var_wm_text.get(),
            "op": self.var_wm_opacity.get()
        }
        
        data = {}
        if os.path.exists(self.presets_file):
            with open(self.presets_file, 'r') as f: data = json.load(f)
        
        data[name] = preset
        with open(self.presets_file, 'w') as f: json.dump(data, f)
        self.cb_presets['values'] = list(data.keys())
        messagebox.showinfo("Preset", f"Guardado: {name}")

    def apply_preset(self):
        name = self.cb_presets.get()
        if not name or not os.path.exists(self.presets_file): return
        
        with open(self.presets_file, 'r') as f: data = json.load(f)
        if name in data:
            p = data[name]
            self.ignore_ui_events = True
            self.var_fmt.set(p.get("fmt", "AVIF"))
            self.var_qual.set(p.get("qual", 80))
            self.var_scale.set(p.get("scale", 100))
            self.var_bg.set(p.get("bg", "BLANCO"))
            self.var_subsample.set(p.get("sub", False))
            self.var_grayscale.set(p.get("bw", False))
            self.var_exif.set(p.get("exif", False))
            self.var_wm_text.set(p.get("wm", ""))
            self.var_wm_opacity.set(p.get("op", 50))
            self.ignore_ui_events = False
            self.on_ui_change() # Aplicar al item actual

    # --- EDICION NO DESTRUCTIVA ---
    def rotate_img(self, deg):
        if not self.current_item: return
        self.current_item.rotate = (self.current_item.rotate + deg) % 360
        self.generate_preview()

    def flip_img(self):
        if not self.current_item: return
        self.current_item.flip_h = not self.current_item.flip_h
        self.generate_preview()

    # --- LOGICA GENERAL (ADAPTADA) ---
    def add_images(self):
        files = filedialog.askopenfilenames()
        if files:
            for f in files:
                if not any(item.path == f for item in self.items):
                    self.items.append(ImageItem(f))
                    self.listbox.insert(tk.END, os.path.basename(f))
            if len(self.items) > 0 and not self.current_item:
                self.listbox.select_set(0); self.on_select_list(None)

    def clear_list(self):
        self.items = []; self.listbox.delete(0, tk.END); self.current_item = None
        self.lbl_preview.config(image='', text="")

    def on_select_list(self, event):
        sel = self.listbox.curselection()
        if not sel: return
        self.current_item = self.items[sel[0]]
        self.ignore_ui_events = True
        
        # Cargar todo
        self.var_fmt.set(self.current_item.fmt); self.var_qual.set(self.current_item.quality)
        self.var_scale.set(self.current_item.scale); self.var_bg.set(self.current_item.bg)
        self.var_subsample.set(self.current_item.subsample); self.var_grayscale.set(self.current_item.grayscale)
        self.var_exif.set(self.current_item.keep_exif); self.var_wm_text.set(self.current_item.wm_text)
        self.var_wm_opacity.set(self.current_item.wm_opacity); self.var_prefix.set(self.current_item.prefix)
        
        self.ignore_ui_events = False
        self.load_image_preview()

    def on_ui_change(self, event=None):
        if self.ignore_ui_events or not self.current_item: return
        try:
            q = int(self.var_qual.get()); s = int(self.var_scale.get())
            if q<1: q=1; self.var_qual.set(1)
            if s<1: s=1; self.var_scale.set(1)
        except: return

        ci = self.current_item
        ci.fmt = self.var_fmt.get(); ci.quality = q; ci.scale = s
        ci.bg = self.var_bg.get(); ci.subsample = self.var_subsample.get()
        ci.grayscale = self.var_grayscale.get(); ci.keep_exif = self.var_exif.get()
        ci.wm_text = self.var_wm_text.get(); ci.wm_opacity = self.var_wm_opacity.get()
        ci.prefix = self.var_prefix.get()
        self.generate_preview()

    def apply_all(self):
        if not self.current_item: return
        for item in self.items:
            item.fmt = self.var_fmt.get(); item.quality = self.var_qual.get()
            item.scale = self.var_scale.get(); item.bg = self.var_bg.get()
            item.subsample = self.var_subsample.get(); item.grayscale = self.var_grayscale.get()
            item.keep_exif = self.var_exif.get(); item.wm_text = self.var_wm_text.get()
            item.wm_opacity = self.var_wm_opacity.get(); item.prefix = self.var_prefix.get()
        messagebox.showinfo("Hecho", "Ajustes replicados.")

    def load_image_preview(self):
        try: self.original_image = Image.open(self.current_item.path); self.generate_preview()
        except Exception as e: print(e)

    def generate_preview(self):
        if not self.original_image: return
        try:
            img_bytes = self.process_image(self.original_image, self.current_item)
            self.processed_buffer = img_bytes
            try: prev = Image.open(io.BytesIO(img_bytes))
            except: prev = self.original_image
            
            w, h = 800, 500
            cp = prev.copy(); cp.thumbnail((w, h), Image.Resampling.LANCZOS)
            tk_img = ImageTk.PhotoImage(cp)
            self.lbl_preview.config(image=tk_img); self.lbl_preview.image = tk_img
            
            orig_s = os.path.getsize(self.current_item.path); new_s = len(img_bytes)
            diff = orig_s - new_s
            col = "success" if diff > 0 else "danger"
            
            # Alerta de Tamaño Visual (TARGET SIZE WARNING)
            size_note = ""
            if new_s > 1024*1024: size_note = " ⚠️ PESADO"
            elif new_s < 200*1024: size_note = " ✅ WEB OK"
            
            self.lbl_info.config(text=f"ORIG: {self.format_bytes(orig_s)} -> {self.current_item.fmt}: {self.format_bytes(new_s)}{size_note}", bootstyle=col)
        except Exception as e: self.lbl_info.config(text=str(e), bootstyle="danger")

    def process_image(self, pil_img, item):
        target = pil_img.copy()
        
        # 0. EDICION BASICA
        if item.rotate != 0: target = target.rotate(item.rotate, expand=True)
        if item.flip_h: target = ImageOps.mirror(target)
        if item.grayscale: target = ImageOps.grayscale(target)

        # 1. EXIF
        exif_data = target.info.get("exif") if item.keep_exif else None
        
        # 2. Escala
        if item.scale < 100:
            w, h = target.size
            target = target.resize((int(w*(item.scale/100)), int(h*(item.scale/100))), Image.Resampling.LANCZOS)
            
        # 3. WATERMARK
        if item.wm_text.strip():
            if target.mode != "RGBA": target = target.convert("RGBA")
            txt_layer = Image.new("RGBA", target.size, (255, 255, 255, 0))
            draw = ImageDraw.Draw(txt_layer)
            font_size = max(10, int(target.height * 0.03))
            try: font = ImageFont.truetype("arial.ttf", font_size)
            except: font = ImageFont.load_default()
            text = item.wm_text
            bbox = draw.textbbox((0, 0), text, font=font)
            x = target.width - (bbox[2]-bbox[0]) - int(target.width*0.02)
            y = target.height - (bbox[3]-bbox[1]) - int(target.width*0.02)
            alpha = int((item.wm_opacity/100)*255)
            draw.text((x, y), text, font=font, fill=(255, 255, 255, alpha))
            target = Image.alpha_composite(target, txt_layer)

        # 4. Formato
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
        
        # 5. Guardar
        buffer = io.BytesIO()
        save_args = {}
        q = int(item.quality)
        if exif_data: save_args["exif"] = exif_data
        sub = 2 if item.subsample else 0
        if pil_fmt == "AVIF": save_args.update({"quality": q, "speed": 6})
        elif pil_fmt == "JPEG": save_args.update({"quality": q, "optimize": True, "subsampling": sub})
        elif pil_fmt == "WEBP": save_args.update({"quality": q, "method": 6})
        elif pil_fmt == "PNG": save_args.update({"optimize": True})
        
        target.save(buffer, format=pil_fmt, **save_args)
        return buffer.getvalue()

    def choose_dir(self):
        d = filedialog.askdirectory()
        if d: self.var_out_dir.set(d)
    def format_bytes(self, size):
        for unit in ['B', 'KB', 'MB']:
            if size < 1024: return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} GB"
    def open_inspector(self, event=None):
        if self.original_image and self.processed_buffer:
            proc = Image.open(io.BytesIO(self.processed_buffer))
            AdvancedInspector(self.root, self.original_image, proc, "ORIG", "PROC")
    def process_batch(self):
        if not self.items: return
        out_dir = self.var_out_dir.get()
        if not os.path.exists(out_dir): os.makedirs(out_dir)
        prog = tk.Toplevel(self.root); ttk.Label(prog, text="Procesando...").pack(pady=20)
        p_bar = ttk.Progressbar(prog, maximum=len(self.items)); p_bar.pack(fill="x", padx=20)
        for i, item in enumerate(self.items):
            try:
                with Image.open(item.path) as img:
                    img_bytes = self.process_image(img, item)
                    base = os.path.splitext(item.name)[0]
                    final_name = f"{item.prefix}{base}.{item.fmt.lower().replace('jpeg','jpg')}"
                    with open(os.path.join(out_dir, final_name), "wb") as f: f.write(img_bytes)
            except Exception as e: print(e)
            p_bar['value'] = i+1; prog.update()
        prog.destroy()
        messagebox.showinfo("Fin", "Proceso completado.")

if __name__ == "__main__":
    app_window = ttk.Window(themename="darkly") 
    app = UniversalOmegaConverter(app_window)
    app_window.mainloop()