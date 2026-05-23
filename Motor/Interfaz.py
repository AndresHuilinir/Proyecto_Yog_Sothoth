# Interfaz.py
import tkinter as tk
from PIL import Image, ImageTk
import os
from Conocimiento import generar_imagen
from Portales import resolver_plantilla
from Rezos import convertir_drive, descargar
from Orden_universal import ruta

UMBRAL_ARRASTRE = 150


def _escala(root):
    """Calcula factor de escala para ajustarse al 88% de la pantalla."""
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    return min((sw * 0.88) / 720, (sh * 0.88) / 950)


class PantallaInicio:
    def __init__(self, df, callback):
        self.df       = df
        self.callback = callback

        self.root = tk.Tk()
        self.root.title("Confesiones — Inicio")
        self.root.configure(bg="#1a1a2e")
        self.root.resizable(False, False)

        sc = _escala(self.root)
        w  = int(500 * sc)
        h  = int(420 * sc)
        self.root.geometry(f"{w}x{h}")

        f_titulo = ("Helvetica", max(10, int(18 * sc)), "bold")
        f_normal = ("Helvetica", max(9,  int(12 * sc)))
        f_sub    = ("Helvetica", max(8,  int(11 * sc)))
        f_boton  = ("Helvetica", max(9,  int(13 * sc)), "bold")

        tk.Label(
            self.root, text="⚙️ Configuración de sesión",
            bg="#1a1a2e", fg="white", font=f_titulo
        ).pack(pady=(int(30*sc), int(15*sc)))

        tk.Label(
            self.root,
            text=f"Total de confesiones disponibles: {len(df)}",
            bg="#1a1a2e", fg="#aaaaaa", font=f_sub
        ).pack(pady=(0, int(15*sc)))

        tk.Label(self.root, text="ID de inicio:",
                 bg="#1a1a2e", fg="white", font=f_normal).pack()
        self.entry_id = tk.Entry(
            self.root, font=("Helvetica", max(10, int(14*sc))),
            justify="center", width=10
        )
        self.entry_id.pack(pady=(int(4*sc), int(15*sc)))
        self.entry_id.insert(0, "1")

        tk.Label(self.root, text="Número visual de inicio:",
                 bg="#1a1a2e", fg="white", font=f_normal).pack()
        self.entry_base = tk.Entry(
            self.root, font=("Helvetica", max(10, int(14*sc))),
            justify="center", width=10
        )
        self.entry_base.pack(pady=(int(4*sc), int(20*sc)))
        self.entry_base.insert(0, "1")

        self.lbl_error = tk.Label(
            self.root, text="", bg="#1a1a2e", fg="#ff4466", font=f_sub
        )
        self.lbl_error.pack()

        tk.Button(
            self.root, text="Comenzar →",
            bg="#4d45e8", fg="white", font=f_boton,
            relief="flat", padx=int(18*sc), pady=int(7*sc),
            cursor="hand2", command=self._confirmar
        ).pack(pady=int(10*sc))

        self.root.mainloop()

    def _confirmar(self):
        try:
            id_inicio   = int(self.entry_id.get().strip())
            numero_base = int(self.entry_base.get().strip())
        except ValueError:
            self.lbl_error.config(text="Ingresa números válidos.")
            return

        desfase = 4
        idx = id_inicio - desfase

        if idx < 0 or idx >= len(self.df):
            self.lbl_error.config(
                text=f"ID fuera de rango (1 → {len(self.df) + desfase})."
            )
            return

        self.root.destroy()
        self.callback(self.df, idx, numero_base)


class InterfazTinder:
    def __init__(self, df, idx_inicio, numero_base):
        self.df                   = df
        self.numero_base          = numero_base
        self.idx_actual           = idx_inicio
        self.variantes            = []
        self.arrastrando          = False
        self.x_inicio             = 0
        self.offset_x             = 0
        self.aceptadas            = 0
        self.ignoradas            = 0
        self.numero_visual_actual = numero_base
        self.tk_imgs              = []

        self.root = tk.Tk()
        self.root.title("Confesiones")
        self.root.configure(bg="#1a1a2e")
        self.root.resizable(False, False)

        # Escala según pantalla — solo afecta la UI, NO las imágenes guardadas
        self.sc = _escala(self.root)
        sc = self.sc

        win_w = int(720 * sc)
        win_h = int(950 * sc)
        self.root.geometry(f"{win_w}x{win_h}")

        self.CANVAS_W = int(700 * sc)
        self.CANVAS_H = int(720 * sc)

        f_contador = ("Helvetica", max(9,  int(13 * sc)), "bold")
        f_variante = ("Helvetica", max(8,  int(10 * sc)))
        f_instruc  = ("Helvetica", max(8,  int(11 * sc)))
        f_dir      = ("Helvetica", max(14, int(26 * sc)), "bold")

        self.lbl_contador = tk.Label(
            self.root, text="", bg="#1a1a2e", fg="white", font=f_contador
        )
        self.lbl_contador.pack(pady=(int(12*sc), int(2*sc)))

        self.lbl_variante = tk.Label(
            self.root, text="", bg="#1a1a2e", fg="#aaaaaa", font=f_variante
        )
        self.lbl_variante.pack(pady=(0, int(4*sc)))

        self.canvas = tk.Canvas(
            self.root, width=self.CANVAS_W, height=self.CANVAS_H,
            bg="#16213e", highlightthickness=0
        )
        self.canvas.pack(pady=int(4*sc))

        self.lbl_aviso = tk.Label(
            self.root, text="", bg="#1a1a2e", fg="#ffcc00",
            font=f_variante, wraplength=int(680 * sc)
        )
        self.lbl_aviso.pack(pady=int(2*sc))

        tk.Label(
            self.root,
            text="← Ignorar     Arrastra la imagen     Aceptar →",
            bg="#1a1a2e", fg="#555577", font=f_instruc
        ).pack(pady=int(2*sc))

        self.lbl_direccion = tk.Label(
            self.root, text="", bg="#1a1a2e", font=f_dir
        )
        self.lbl_direccion.pack(pady=int(2*sc))

        self.canvas.bind("<ButtonPress-1>",  self._inicio_arrastre)
        self.canvas.bind("<B1-Motion>",       self._durante_arrastre)
        self.canvas.bind("<ButtonRelease-1>", self._fin_arrastre)

        self._cargar_confesion()
        self.root.mainloop()

    # =========================
    # GENERACIÓN
    # =========================
    def _cargar_confesion(self):
        if self.idx_actual >= len(self.df):
            self._finalizar()
            return

        self.variantes = []
        self.tk_imgs   = []
        self.lbl_aviso.config(text="")
        self.lbl_direccion.config(text="")

        row           = self.df.iloc[self.idx_actual]
        numero_visual = self.numero_visual_actual
        plantilla, sede_custom = resolver_plantilla(str(row["sede"]))
        confesion     = str(row["confesion"])
        link_drive    = str(row["imagen"]).strip()

        ruta_adjunto   = None
        requiere_canva = False

        if "drive.google.com" in link_drive:
            url_directa = convertir_drive(link_drive)
            if url_directa:
                temp_path = ruta(f"archivos/temp_{numero_visual}")
                resultado = descargar(url_directa, temp_path)
                if resultado == "INVALIDO":
                    requiere_canva = True
                    self.lbl_aviso.config(
                        text="⚠️ Adjunto no admitido (video u otro). Configurar en Canva."
                    )
                elif resultado:
                    ruta_adjunto = resultado

        try:
            # generar_imagen guarda siempre en 1080x1080 — sin cambios
            generar_imagen(
                nombre_plantilla = plantilla,
                numero           = numero_visual,
                confesion        = confesion,
                sede_custom      = sede_custom,
                ruta_adjunto     = ruta_adjunto,
                requiere_canva   = requiere_canva,
            )
        except Exception as e:
            print(f"[ERROR] Generando confesión {numero_visual}: {e}")
            self.idx_actual += 1
            self._cargar_confesion()
            return

        base       = f"Confesiones/Confesion {numero_visual}"
        candidatos = [
            f"{base}.png",
            f"{base} (Formato no disponible, configurar en Canva).png",
            f"{base} V1.png",
            f"{base} V2 (1).png",
            f"{base} V2 (2).png",
        ]
        for c in candidatos:
            if os.path.exists(c):
                self.variantes.append(c)

        if not self.variantes:
            self.idx_actual += 1
            self._cargar_confesion()
            return

        self.lbl_contador.config(
            text=f"Confesión {self.idx_actual + 1} de {len(self.df)}"
                 f"  |  ✅ {self.aceptadas}  ❌ {self.ignoradas}"
        )
        self._mostrar_variantes()

    def _thumb(self, ruta_img, max_w, max_h):
        """Carga imagen escalada para mostrar en pantalla. No toca el archivo."""
        img = Image.open(ruta_img).convert("RGBA")
        img.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
        return img

    def _mostrar_variantes(self, dx=0):
        sc = self.sc
        cw = self.CANVAS_W
        ch = self.CANVAS_H
        self.canvas.delete("all")
        self.tk_imgs = []
        n = len(self.variantes)

        cx = cw // 2  # centro horizontal del canvas

        if n == 1:
            self.lbl_variante.config(text="")
            img = self._thumb(self.variantes[0],
                              int(cw * 0.97), int(ch * 0.97))
            tk_img = ImageTk.PhotoImage(img)
            self.tk_imgs.append(tk_img)
            self.canvas.create_image(cx + dx, ch // 2, anchor="center",
                                     image=tk_img, tags="imagen")

        elif n == 3:
            # Pirámide: V1 arriba grande, V2(1) y V2(2) abajo lado a lado
            self.lbl_variante.config(text="V1 ↑   |   V2(1) ↙   V2(2) ↘")

            top_max = int(cw * 0.64)
            bot_max = int(cw * 0.44)
            top_y   = int(ch * 0.33)
            bot_y   = int(ch * 0.78)
            bot_x1  = int(cw * 0.24)
            bot_x2  = int(cw * 0.76)

            img_top = self._thumb(self.variantes[0], top_max, top_max)
            tk_top  = ImageTk.PhotoImage(img_top)
            self.tk_imgs.append(tk_top)
            self.canvas.create_image(cx + dx, top_y, anchor="center",
                                     image=tk_top, tags="imagen")

            img_bl = self._thumb(self.variantes[1], bot_max, bot_max)
            tk_bl  = ImageTk.PhotoImage(img_bl)
            self.tk_imgs.append(tk_bl)
            self.canvas.create_image(bot_x1 + dx, bot_y, anchor="center",
                                     image=tk_bl, tags="imagen")

            img_br = self._thumb(self.variantes[2], bot_max, bot_max)
            tk_br  = ImageTk.PhotoImage(img_br)
            self.tk_imgs.append(tk_br)
            self.canvas.create_image(bot_x2 + dx, bot_y, anchor="center",
                                     image=tk_br, tags="imagen")

        else:
            # 2 imágenes lado a lado
            self.lbl_variante.config(text="")
            w_cada = int(cw * 0.47)
            for i, v in enumerate(self.variantes):
                img    = self._thumb(v, w_cada, int(ch * 0.97))
                tk_img = ImageTk.PhotoImage(img)
                self.tk_imgs.append(tk_img)
                x = int(cw * 0.25) + i * int(cw * 0.50)
                self.canvas.create_image(x + dx, ch // 2, anchor="center",
                                         image=tk_img, tags="imagen")

    # =========================
    # ARRASTRE
    # =========================
    def _inicio_arrastre(self, event):
        self.arrastrando = True
        self.x_inicio    = event.x
        self.offset_x    = 0

    def _durante_arrastre(self, event):
        if not self.arrastrando:
            return
        self.offset_x = event.x - self.x_inicio
        self._mostrar_variantes(dx=self.offset_x)

        if self.offset_x > UMBRAL_ARRASTRE:
            self.lbl_direccion.config(text="✅", fg="#00ff88")
        elif self.offset_x < -UMBRAL_ARRASTRE:
            self.lbl_direccion.config(text="❌", fg="#ff4466")
        else:
            self.lbl_direccion.config(text="")

    def _fin_arrastre(self, event):
        if not self.arrastrando:
            return
        self.arrastrando = False

        if self.offset_x > UMBRAL_ARRASTRE:
            self._accion_derecha()
        elif self.offset_x < -UMBRAL_ARRASTRE:
            self._accion_izquierda()
        else:
            self._mostrar_variantes()
            self.lbl_direccion.config(text="")

    # =========================
    # ACCIONES
    # =========================
    def _accion_derecha(self):
        self.aceptadas            += 1
        self.numero_visual_actual += 1
        self.idx_actual           += 1
        self._cargar_confesion()

    def _accion_izquierda(self):
        for v in self.variantes:
            if os.path.exists(v):
                os.remove(v)
        self.ignoradas  += 1
        self.idx_actual += 1
        self._cargar_confesion()

    # =========================
    # FIN
    # =========================
    def _finalizar(self):
        self.canvas.delete("all")
        self.lbl_contador.config(
            text=f"✅ Aceptadas: {self.aceptadas}  |  ❌ Ignoradas: {self.ignoradas}"
        )
        self.lbl_variante.config(text="Proceso finalizado 🎉")
        self.lbl_direccion.config(text="")
        self.root.after(3000, self.root.destroy)


def lanzar_interfaz(df):
    def iniciar(df, idx_inicio, numero_base):
        df_procesar = df.iloc[idx_inicio:].reset_index(drop=True)
        InterfazTinder(df_procesar, 0, numero_base)

    PantallaInicio(df, iniciar)