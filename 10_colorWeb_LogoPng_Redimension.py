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
from PIL import Image, ImageTk, ImageDraw, ImageFont, ImageOps, ImageCms
import pillow_avif
import pillow_heif

pillow_heif.register_heif_opener()

# --- CLASE INSPECTOR ---
class GodInspector(tk.Toplevel):
    def __init__(self, master, img_orig, img_proc, info_orig, info_proc):
        super().__init__(master)
        self.title("Inspector God Mode")
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

# --- DATA MODEL ---
class ImageItem:
    def __init__(self, path):
        self.path = path
        self.name = os.path.basename(path)
        self.fmt = "AVIF"
        self.quality = 80
        # NUEVO: Modos de Escala
        self.resize_mode = "Scale %" # Scale %, Width Px, Height Px, Longest Px
        self.resize_val = 100
        self.bg = "BLANCO"
        self.subsample = False
        self.grayscale = False
        self.rotate = 0
        self.flip_h = False
        # Metadatos y Color
        self.keep_exif = False
        self.force_srgb = True # Nuevo
        # Watermark
        self.wm_type = "Text" # Text, Image
        self.wm_content = "" # Texto o Ruta
        self.wm_opacity = 50
        self.wm_scale = 15 # % del tamaño de imagen (para logo)
        self.prefix = ""

class UniversalGodConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Tarquitet - GOD MODE Converter")
        self.root.geometry("1600x980")
        
        self.items = []; self.current_item = None
        self.original_image = None; self.processed_buffer = None
        
        # Variables Globales UI
        self.var_fmt = tk.StringVar(value="AVIF")
        self.var_qual = tk.IntVar(value=80)
        self.var_resize_mode = tk.StringVar(value="Scale %")
        self.var_resize_val = tk.IntVar(value=100)
        
        self.var_bg = tk.StringVar(value="BLANCO")
        self.var_subsample = tk.BooleanVar(value=False)
        self.var_grayscale = tk.BooleanVar(value=False)
        self.var_exif = tk.BooleanVar(value=False)
        self.var_srgb = tk.BooleanVar(value=True) # sRGB
        
        # Watermark
        self.var_wm_type = tk.StringVar(value="Text")
        self.var_wm_content = tk.StringVar(value="")
        self.var_wm_opacity = tk.IntVar(value=50)
        self.var_wm_scale = tk.IntVar(value=15) # Para logo
        
        self.var_prefix = tk.StringVar(value="")
        self.var_out_dir = tk.StringVar(value=os.getcwd())
        
        self.presets_file = "god_presets.json"
        self.ignore_ui_events = False 
        self.build_ui()

    def build_ui(self):
        # HEADER
        header = ttk.Frame(self.root, padding=20)
        header.pack(fill="x")
        ttk.Label(header, text="GOD MODE CONVERTER", font=("Helvetica", 18, "bold"), bootstyle="primary").pack(side="left")
        
        p_area = ttk.Frame(header); p_area.pack(side="right")
        ttk.Label(p_area, text="Presets:").pack(side="left", padx=5)
        self.cb_presets = ttk.Combobox(p_area, values=self.load_preset_names(), state="readonly", width=15)
        self.cb_presets.pack(side="left")
        ttk.Button(p_area, text="💾", command=self.save_preset, bootstyle="secondary-outline").pack(side="left", padx=2)
        ttk.Button(p_area, text="📂", command=self.apply_preset, bootstyle="info-outline").pack(side="left", padx=2)

        paned = ttk.PanedWindow(self.root, orient="horizontal")
        paned.pack(fill="both", expand=True, padx=10, pady=5)

        # LEFT
        left = ttk.Frame(paned, padding=(0,0,10,0)); paned.add(left, weight=1)
        btns = ttk.Frame(left); btns.pack(fill="x", pady=5)
        ttk.Button(btns, text="➕ Fotos", command=self.add_images, bootstyle="outline-primary").pack(side="left", fill="x", expand=True)
        ttk.Button(btns, text="Limpiar", command=self.clear_list, bootstyle="outline-danger").pack(side="left", padx=2)
        
        list_scroll = ttk.Frame(left); list_scroll.pack(fill="both", expand=True)
        scroll = ttk.Scrollbar(list_scroll); scroll.pack(side="right", fill="y")
        self.listbox = tk.Listbox(list_scroll, font=("Consolas", 10), selectmode="SINGLE", borderwidth=0)
        self.listbox.pack(side="left", fill="both", expand=True)
        self.listbox.config(yscrollcommand=scroll.set); scroll.config(command=self.listbox.yview)
        self.listbox.bind('<<ListboxSelect>>', self.on_select_list)

        # RIGHT
        right = ttk.Frame(paned, padding=(10,0,0,0)); paned.add(right, weight=3)
        
        # PREVIEW
        f_prev = ttk.Labelframe(right, text=" Vista Previa (Click para Inspector) ", padding=10, bootstyle="secondary")
        f_prev.pack(fill="both", expand=True)
        self.lbl_preview = ttk.Label(f_prev, text="Arrastra imágenes...", anchor="center", cursor="crosshair")
        self.lbl_preview.pack(fill="both", expand=True)
        self.lbl_info = ttk.Label(f_prev, text="-", font=("Consolas", 10), bootstyle="inverse-secondary", anchor="center")
        self.lbl_info.pack(side="bottom", fill="x")
        self.lbl_preview.bind("<Button-1>", self.open_inspector)

        # CONTROLS
        nb = ttk.Notebook(right, bootstyle="info"); nb.pack(fill="x", pady=10)
        
        # TAB 1: IMAGEN
        t1 = ttk.Frame(nb, padding=15); nb.add(t1, text="Imagen & Color")
        
        # Edición
        r0 = ttk.Frame(t1); r0.pack(fill="x", pady=(0,10))
        ttk.Button(r0, text="⟲", command=lambda: self.rotate_img(90), bootstyle="secondary-outline").pack(side="left", padx=2)
        ttk.Button(r0, text="⟳", command=lambda: self.rotate_img(-90), bootstyle="secondary-outline").pack(side="left", padx=2)
        ttk.Button(r0, text="⇄", command=self.flip_img, bootstyle="secondary-outline").pack(side="left", padx=2)
        ttk.Checkbutton(r0, text="B/N", variable=self.var_grayscale, command=self.on_ui_change, bootstyle="round-toggle").pack(side="left", padx=10)
        ttk.Checkbutton(r0, text="Forzar sRGB (Web Safe)", variable=self.var_srgb, command=self.on_ui_change, bootstyle="success-round-toggle").pack(side="left", padx=10)

        # Params
        r1 = ttk.Frame(t1); r1.pack(fill="x", pady=5)
        
        # Fmt
        f1 = ttk.Frame(r1); f1.pack(side="left", padx=(0,10))
        ttk.Label(f1, text="Fmt").pack(anchor="w")
        cb_f = ttk.Combobox(f1, textvariable=self.var_fmt, values=["AVIF", "HEIC", "WEBP", "JPEG", "PNG", "GIF", "PSD"], state="readonly", width=6)
        cb_f.pack(); cb_f.bind("<<ComboboxSelected>>", self.on_ui_change)

        # Qual
        f2 = ttk.Frame(r1); f2.pack(side="left", fill="x", expand=True, padx=5)
        hf2 = ttk.Frame(f2); hf2.pack(fill="x")
        ttk.Label(hf2, text="Calidad").pack(side="left")
        sp_q = ttk.Spinbox(hf2, from_=1, to=100, textvariable=self.var_qual, width=4); sp_q.pack(side="right")
        sp_q.bind("<Return>", self.on_ui_change)
        ttk.Scale(f2, from_=1, to=100, variable=self.var_qual, command=lambda x: self.on_ui_change()).pack(fill="x")

        # RESIZE AVANZADO
        f3 = ttk.Frame(r1); f3.pack(side="left", fill="x", expand=True, padx=5)
        hf3 = ttk.Frame(f3); hf3.pack(fill="x")
        ttk.Label(hf3, text="Redimensión").pack(side="left")
        
        # Selector de Modo
        cb_rm = ttk.Combobox(hf3, textvariable=self.var_resize_mode, values=["Scale %", "Width Px", "Height Px", "Longest Px"], state="readonly", width=10)
        cb_rm.pack(side="left", padx=5)
        cb_rm.bind("<<ComboboxSelected>>", self.on_ui_change)
        
        sp_s = ttk.Spinbox(hf3, from_=1, to=10000, textvariable=self.var_resize_val, width=5)
        sp_s.pack(side="right"); sp_s.bind("<Return>", self.on_ui_change)
        
        # TAB 2: MARCA & SALIDA
        t2 = ttk.Frame(nb, padding=15); nb.add(t2, text="Marca de Agua (Logo)")
        
        # Tipo WM
        wm_top = ttk.Frame(t2); wm_top.pack(fill="x", pady=5)
        ttk.Label(wm_top, text="Tipo:").pack(side="left")
        ttk.Radiobutton(wm_top, text="Texto", variable=self.var_wm_type, value="Text", command=self.on_ui_change).pack(side="left", padx=5)
        ttk.Radiobutton(wm_top, text="Imagen (Logo)", variable=self.var_wm_type, value="Image", command=self.on_ui_change).pack(side="left", padx=5)
        
        # Content
        wm_cont = ttk.Frame(t2); wm_cont.pack(fill="x", pady=5)
        ttk.Label(wm_cont, text="Contenido:").pack(side="left")
        self.ent_wm = ttk.Entry(wm_cont, textvariable=self.var_wm_content)
        self.ent_wm.pack(side="left", fill="x", expand=True, padx=5)
        self.ent_wm.bind("<FocusOut>", self.on_ui_change)
        ttk.Button(wm_cont, text="📂", width=3, command=self.browse_logo).pack(side="left")

        # Sliders WM
        wm_sld = ttk.Frame(t2); wm_sld.pack(fill="x", pady=5)
        
        s1 = ttk.Frame(wm_sld); s1.pack(side="left", fill="x", expand=True, padx=5)
        ttk.Label(s1, text="Opacidad %").pack(anchor="w")
        ttk.Scale(s1, from_=0, to=100, variable=self.var_wm_opacity, command=lambda x: self.on_ui_change()).pack(fill="x")

        s2 = ttk.Frame(wm_sld); s2.pack(side="left", fill="x", expand=True, padx=5)
        ttk.Label(s2, text="Tamaño Relativo %").pack(anchor="w")
        ttk.Scale(s2, from_=1, to=100, variable=self.var_wm_scale, command=lambda x: self.on_ui_change()).pack(fill="x")

        # Renombrado
        rn_frame = ttk.Frame(t2); rn_frame.pack(fill="x", pady=10)
        ttk.Label(rn_frame, text="Prefijo:").pack(side="left")
        rn_e = ttk.Entry(rn_frame, textvariable=self.var_prefix); rn_e.pack(side="left", fill="x", expand=True, padx=5)
        rn_e.bind("<FocusOut>", self.on_ui_change)

        # BOTONES
        fr = ttk.Frame(right); fr.pack(fill="x", pady=10)
        ttk.Button(fr, text="⚡ APLICAR GLOBAL", command=self.apply_all, bootstyle="warning-outline").pack(side="left")
        
        pf = ttk.Frame(fr); pf.pack(side="left", fill="x", expand=True, padx=20)
        ttk.Entry(pf, textvariable=self.var_out_dir).pack(side="left", fill="x", expand=True)
        ttk.Button(pf, text="📂", width=3, command=self.choose_dir).pack(side="left")
        
        ttk.Button(fr, text="🚀 PROCESAR", command=self.process_batch, bootstyle="success").pack(side="right", ipady=5)

    # --- LOGICA ---
    def browse_logo(self):
        f = filedialog.askopenfilename(filetypes=[("PNG Logo", "*.png"), ("All", "*.*")])
        if f: 
            self.var_wm_content.set(f)
            self.var_wm_type.set("Image")
            self.on_ui_change()

    def rotate_img(self, deg):
        if self.current_item: self.current_item.rotate = (self.current_item.rotate + deg) % 360; self.generate_preview()
    def flip_img(self):
        if self.current_item: self.current_item.flip_h = not self.current_item.flip_h; self.generate_preview()

    def process_image(self, pil_img, item):
        target = pil_img.copy()
        
        # 0. Edición Base
        if item.rotate != 0: target = target.rotate(item.rotate, expand=True)
        if item.flip_h: target = ImageOps.mirror(target)
        
        # 1. Color Management (sRGB)
        if item.force_srgb and target.mode != "P": # No convertir palettes indexados
             try:
                # Si no tiene perfil, asumir sRGB (estándar), si tiene, convertir
                if "icc_profile" in target.info:
                    srgb_profile = ImageCms.createProfile("sRGB")
                    # Intentar leer perfil incrustado, si falla, convertir a RGB plano
                    input_profile = ImageCms.getOpenProfile(io.BytesIO(target.info["icc_profile"]))
                    target = ImageCms.profileToProfile(target, input_profile, srgb_profile)
             except: pass # Fallback silencioso
             
        if item.grayscale: target = ImageOps.grayscale(target)

        # 2. Redimensión Inteligente
        w, h = target.size
        new_w, new_h = w, h
        
        mode = item.resize_mode
        val = item.resize_val
        
        if mode == "Scale %":
            new_w = int(w * (val / 100))
            new_h = int(h * (val / 100))
        elif mode == "Width Px":
            new_w = val
            new_h = int(h * (val / w))
        elif mode == "Height Px":
            new_h = val
            new_w = int(w * (val / h))
        elif mode == "Longest Px":
            if w > h:
                new_w = val
                new_h = int(h * (val / w))
            else:
                new_h = val
                new_w = int(w * (val / h))
                
        if new_w != w or new_h != h:
            target = target.resize((new_w, new_h), Image.Resampling.LANCZOS)
            
        # 3. Watermark (Text OR Image)
        if item.wm_content.strip():
            if target.mode != "RGBA": target = target.convert("RGBA")
            wm_layer = Image.new("RGBA", target.size, (0,0,0,0))
            
            if item.wm_type == "Text":
                draw = ImageDraw.Draw(wm_layer)
                font_size = max(10, int(target.height * (item.wm_scale/100)*0.5)) # Scale afecta tamaño texto aprox
                try: font = ImageFont.truetype("arial.ttf", font_size)
                except: font = ImageFont.load_default()
                text = item.wm_content
                bbox = draw.textbbox((0,0), text, font=font)
                tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
                x = target.width - tw - int(target.width*0.02)
                y = target.height - th - int(target.height*0.02)
                alpha = int((item.wm_opacity/100)*255)
                draw.text((x,y), text, font=font, fill=(255,255,255,alpha))
                
            elif item.wm_type == "Image" and os.path.exists(item.wm_content):
                try:
                    logo = Image.open(item.wm_content).convert("RGBA")
                    # Escalar logo relativo a la imagen base
                    target_logo_w = int(target.width * (item.wm_scale / 100))
                    aspect = logo.height / logo.width
                    target_logo_h = int(target_logo_w * aspect)
                    logo = logo.resize((target_logo_w, target_logo_h), Image.Resampling.LANCZOS)
                    
                    # Ajustar opacidad logo
                    # Pillow no tiene "set opacity" directo, hay que operar sobre el canal alpha
                    r, g, b, a = logo.split()
                    alpha = a.point(lambda p: p * (item.wm_opacity/100))
                    logo.putalpha(alpha)
                    
                    # Posición (Esquina inferior derecha)
                    x = target.width - logo.width - int(target.width*0.02)
                    y = target.height - logo.height - int(target.height*0.02)
                    
                    wm_layer.paste(logo, (x, y))
                except: pass
                
            target = Image.alpha_composite(target, wm_layer)

        # 4. Save
        fmt = item.fmt; pil_fmt = "HEIF" if fmt == "HEIC" else fmt
        no_alpha = ["JPEG", "BMP", "EPS", "PDF"]
        if (pil_fmt in no_alpha) and target.mode in ("RGBA", "LA", "P"):
            bg_col = (255,255,255) if item.bg=="BLANCO" else (0,0,0)
            bg = Image.new("RGB", target.size, bg_col)
            try: bg.paste(target, mask=target.split()[3])
            except: bg.paste(target)
            target = bg
        elif target.mode == "P" and pil_fmt not in ["GIF", "PNG"]: target = target.convert("RGB")
        
        buf = io.BytesIO(); args = {}
        q = int(item.quality)
        if item.keep_exif and pil_img.info.get("exif"): args["exif"] = pil_img.info.get("exif")
        
        sub = 2 if item.subsample else 0
        if pil_fmt=="AVIF": args.update({"quality":q, "speed":6})
        elif pil_fmt=="JPEG": args.update({"quality":q, "optimize":True, "subsampling":sub})
        elif pil_fmt=="WEBP": args.update({"quality":q, "method":6})
        elif pil_fmt=="PNG": args.update({"optimize":True})
        
        target.save(buf, format=pil_fmt, **args)
        return buf.getvalue()

    # --- UI HELPERS ---
    def add_images(self):
        files = filedialog.askopenfilenames()
        if files:
            for f in files:
                if not any(i.path==f for i in self.items): 
                    self.items.append(ImageItem(f)); self.listbox.insert(tk.END, os.path.basename(f))
            if len(self.items)>0 and not self.current_item: self.listbox.select_set(0); self.on_select_list(None)

    def clear_list(self): 
        self.items=[]; self.listbox.delete(0,tk.END); self.current_item=None; self.lbl_preview.config(image='',text='')

    def on_select_list(self, e):
        sel = self.listbox.curselection()
        if not sel: return
        self.current_item = self.items[sel[0]]
        self.ignore_ui_events = True
        
        ci = self.current_item
        self.var_fmt.set(ci.fmt); self.var_qual.set(ci.quality)
        self.var_resize_mode.set(ci.resize_mode); self.var_resize_val.set(ci.resize_val)
        self.var_bg.set(ci.bg); self.var_subsample.set(ci.subsample)
        self.var_grayscale.set(ci.grayscale); self.var_exif.set(ci.keep_exif)
        self.var_srgb.set(ci.force_srgb)
        self.var_wm_type.set(ci.wm_type); self.var_wm_content.set(ci.wm_content)
        self.var_wm_opacity.set(ci.wm_opacity); self.var_wm_scale.set(ci.wm_scale)
        self.var_prefix.set(ci.prefix)
        
        self.ignore_ui_events = False
        self.load_image_preview()

    def on_ui_change(self, e=None):
        if self.ignore_ui_events or not self.current_item: return
        try: q=int(self.var_qual.get()); v=int(self.var_resize_val.get())
        except: return
        ci = self.current_item
        ci.fmt=self.var_fmt.get(); ci.quality=q
        ci.resize_mode=self.var_resize_mode.get(); ci.resize_val=v
        ci.bg=self.var_bg.get(); ci.subsample=self.var_subsample.get()
        ci.grayscale=self.var_grayscale.get(); ci.force_srgb=self.var_srgb.get()
        ci.keep_exif=self.var_exif.get()
        ci.wm_type=self.var_wm_type.get(); ci.wm_content=self.var_wm_content.get()
        ci.wm_opacity=self.var_wm_opacity.get(); ci.wm_scale=self.var_wm_scale.get()
        ci.prefix=self.var_prefix.get()
        self.generate_preview()

    def load_image_preview(self):
        try: self.original_image=Image.open(self.current_item.path); self.generate_preview()
        except Exception as e: print(e)

    def generate_preview(self):
        if not self.original_image: return
        try:
            b = self.process_image(self.original_image, self.current_item)
            self.processed_buffer = b
            try: prev=Image.open(io.BytesIO(b))
            except: prev=self.original_image
            
            cp=prev.copy(); cp.thumbnail((800,500), Image.Resampling.LANCZOS)
            tk_img=ImageTk.PhotoImage(cp)
            self.lbl_preview.config(image=tk_img); self.lbl_preview.image=tk_img
            
            orig=os.path.getsize(self.current_item.path); new=len(b)
            col="success" if new<orig else "danger"
            self.lbl_info.config(text=f"ORIG: {self.format_bytes(orig)} -> {self.format_bytes(new)}", bootstyle=col)
        except Exception as e: self.lbl_info.config(text=str(e), bootstyle="danger")

    def apply_all(self):
        if not self.current_item: return
        # Serializar actual
        ci = self.current_item
        for i in self.items:
            i.fmt=ci.fmt; i.quality=ci.quality
            i.resize_mode=ci.resize_mode; i.resize_val=ci.resize_val
            i.bg=ci.bg; i.subsample=ci.subsample; i.grayscale=ci.grayscale
            i.force_srgb=ci.force_srgb; i.keep_exif=ci.keep_exif
            i.wm_type=ci.wm_type; i.wm_content=ci.wm_content
            i.wm_opacity=ci.wm_opacity; i.wm_scale=ci.wm_scale
            i.prefix=ci.prefix
        messagebox.showinfo("God Mode", "Configuración clonada a todo el lote.")

    def process_batch(self):
        if not self.items: return
        d=self.var_out_dir.get()
        if not os.path.exists(d): os.makedirs(d)
        prog=tk.Toplevel(self.root); ttk.Label(prog,text="Procesando...").pack(pady=20)
        bar=ttk.Progressbar(prog,maximum=len(self.items)); bar.pack(fill="x",padx=20)
        for i, item in enumerate(self.items):
            try:
                with Image.open(item.path) as img:
                    b=self.process_image(img, item)
                    base=os.path.splitext(item.name)[0]
                    ext=item.fmt.lower().replace("jpeg","jpg")
                    with open(os.path.join(d, f"{item.prefix}{base}.{ext}"),"wb") as f: f.write(b)
            except: pass
            bar['value']=i+1; prog.update()
        prog.destroy(); messagebox.showinfo("Listo", "Proceso terminado.")
        
    def load_preset_names(self):
        if not os.path.exists(self.presets_file): return []
        try: 
            with open(self.presets_file,'r') as f: return list(json.load(f).keys())
        except: return []

    def save_preset(self):
        name = simpledialog.askstring("Preset", "Nombre:")
        if not name: return
        ci = self.current_item
        # Crear dict con todos los atributos
        p = vars(ci).copy()
        if 'path' in p: del p['path'] 
        if 'name' in p: del p['name'] # No guardar datos de archivo
        
        data = {}
        if os.path.exists(self.presets_file):
            with open(self.presets_file,'r') as f: data = json.load(f)
        data[name] = p
        with open(self.presets_file,'w') as f: json.dump(data, f)
        self.cb_presets['values'] = list(data.keys())
        
    def apply_preset(self):
        name = self.cb_presets.get()
        if not name or not os.path.exists(self.presets_file): return
        with open(self.presets_file,'r') as f: data = json.load(f)
        if name in data:
            p = data[name]
            ci = self.current_item
            # Restaurar atributos
            for k,v in p.items(): 
                if hasattr(ci, k): setattr(ci, k, v)
            self.on_select_list(None) # Refrescar UI

    # --- FUNCIONES DE SOPORTE QUE FALTABAN ---
    def open_inspector(self, event=None): 
        if self.original_image and self.processed_buffer:
            GodInspector(self.root, self.original_image, Image.open(io.BytesIO(self.processed_buffer)), "ORIG", "PROC")

    def choose_dir(self): 
        d = filedialog.askdirectory()
        if d: self.var_out_dir.set(d)

    def format_bytes(self, s):
        for u in ['B','KB','MB']: 
            if s < 1024: return f"{s:.2f} {u}"
            s /= 1024
        return f"{s:.2f} GB"

if __name__ == "__main__":
    app_window = ttk.Window(themename="darkly") 
    app = UniversalGodConverter(app_window)
    app_window.mainloop()