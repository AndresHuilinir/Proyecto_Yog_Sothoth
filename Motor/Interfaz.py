import tkinter as tk
from PIL import Image, ImageTk
import os
import subprocess
import threading
from Conocimiento import generar_imagen, recargar_herejias
from Portales import resolver_plantilla
from Rezos import convertir_drive, descargar
from Orden_universal import ruta, CARPETA_CONFESIONES

UMBRAL_ARRASTRE = 80
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def _escala(root):
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    return min((sw * 0.88) / 720, (sh * 0.88) / 950)

def _tipo_media(ruta_archivo):
    ext = os.path.splitext(ruta_archivo)[1].lower()
    if ext in [".mp4", ".mov", ".webm", ".avi"]:
        return "VIDEO"
    if ext == ".gif":
        return "GIF"
    return None


class PantallaInicio:
    def __init__(self, df, callback):
        self.df       = df
        self.callback = callback

        self.root = tk.Tk()
        self.root.title("Confesiones — Inicio")
        self.root.configure(bg="#1a1a2e")
        self.root.resizable(False, False)

        sc       = _escala(self.root)
        self.sc  = sc
        self.root.geometry(f"{int(540*sc)}x{int(580*sc)}")

        f_titulo = ("Helvetica", max(10, int(18*sc)), "bold")
        f_normal = ("Helvetica", max(9,  int(12*sc)))
        f_sub    = ("Helvetica", max(8,  int(11*sc)))
        f_boton  = ("Helvetica", max(9,  int(12*sc)), "bold")
        f_result = ("Helvetica", max(8,  int(11*sc)))
        self.f_result = f_result

        frame_update = tk.Frame(self.root, bg="#1a1a2e")
        frame_update.pack(pady=(int(15*sc), 0), padx=int(20*sc), fill="x")

        tk.Button(
            frame_update, text="🔄 Buscar actualizaciones",
            bg="#16213e", fg="#aaaaaa", font=f_sub,
            relief="flat", padx=int(10*sc), pady=int(5*sc),
            cursor="hand2", command=self._actualizar
        ).pack(side="left")

        self.lbl_update = tk.Label(
            frame_update, text="", bg="#1a1a2e", fg="#aaaaaa", font=f_sub
        )
        self.lbl_update.pack(side="left", padx=(int(8*sc), 0))

        tk.Label(
            self.root, text="⚙️ Configuración de sesión",
            bg="#1a1a2e", fg="white", font=f_titulo
        ).pack(pady=(int(15*sc), int(10*sc)))

        tk.Label(
            self.root, text=f"Total de confesiones disponibles: {len(df)}",
            bg="#1a1a2e", fg="#aaaaaa", font=f_sub
        ).pack(pady=(0, int(12*sc)))

        tk.Label(self.root, text="Busca la confesión por un fragmento de texto:",
                 bg="#1a1a2e", fg="white", font=f_normal).pack()

        frame_busq = tk.Frame(self.root, bg="#1a1a2e")
        frame_busq.pack(pady=(int(5*sc), int(5*sc)))

        self.entry_busq = tk.Entry(frame_busq, font=("Helvetica", max(9, int(12*sc))), width=28)
        self.entry_busq.pack(side="left", padx=(0, int(6*sc)))

        tk.Button(
            frame_busq, text="Buscar", bg="#4d45e8", fg="white", font=f_boton,
            relief="flat", padx=int(10*sc), pady=int(4*sc),
            cursor="hand2", command=self._buscar
        ).pack(side="left")

        self.frame_resultados = tk.Frame(self.root, bg="#1a1a2e")
        self.frame_resultados.pack(pady=(int(5*sc), int(5*sc)), fill="x", padx=int(20*sc))

        self.lbl_error = tk.Label(self.root, text="", bg="#1a1a2e", fg="#ff4466", font=f_sub)
        self.lbl_error.pack()

        tk.Label(self.root, text="Número visual de inicio:",
                 bg="#1a1a2e", fg="white", font=f_normal).pack(pady=(int(10*sc), 0))

        self.entry_base = tk.Entry(
            self.root, font=("Helvetica", max(10, int(14*sc))),
            justify="center", width=10
        )
        self.entry_base.pack(pady=(int(4*sc), int(8*sc)))
        self.entry_base.insert(0, "1")

        self.root.mainloop()

    def _actualizar(self):
        self.lbl_update.config(text="Verificando...", fg="#ffcc00")
        self.root.update()

        REPO_URL = "https://github.com/TU_USUARIO/TU_REPO.git"

        env_sin_auth = os.environ.copy()
        env_sin_auth["GIT_TERMINAL_PROMPT"] = "0"
        env_sin_auth["GIT_ASKPASS"]         = "echo"
        env_sin_auth["GCM_INTERACTIVE"]     = "never"
        env_sin_auth["GIT_SSH_COMMAND"]     = "ssh -o BatchMode=yes"

        try:
            fetch = subprocess.run(
                [
                    "git",
                    "-c", "credential.helper=",
                    "-c", "http.extraHeader=",
                    "fetch", REPO_URL, "main"
                ],
                cwd=ROOT_DIR, capture_output=True, text=True,
                timeout=30, env=env_sin_auth
            )
            if fetch.returncode != 0:
                error_real = (fetch.stderr.strip() or fetch.stdout.strip())[:120]
                self.lbl_update.config(text=f"⚠️ {error_real}", fg="#ff4466")
                return

            diff = subprocess.run(
                ["git", "log", "HEAD..FETCH_HEAD", "--oneline"],
                cwd=ROOT_DIR, capture_output=True, text=True,
                env=env_sin_auth
            )
            cambios = diff.stdout.strip()

            if not cambios:
                self.lbl_update.config(text="✅ Ya tienes la versión más reciente.", fg="#00ff88")
                return

            ventana = tk.Toplevel(self.root)
            ventana.title("Cambios disponibles")
            ventana.configure(bg="#1a1a2e")
            ventana.geometry("500x300")

            tk.Label(
                ventana, text="Se encontraron estos cambios:",
                bg="#1a1a2e", fg="white",
                font=("Helvetica", 12, "bold")
            ).pack(pady=(20, 10))

            texto_widget = tk.Text(ventana, bg="#16213e", fg="white",
                                   font=("Helvetica", 10), wrap="word",
                                   padx=10, pady=10)
            texto_widget.pack(fill="both", expand=True, padx=20)
            texto_widget.insert("1.0", cambios)
            texto_widget.config(state="disabled")

            frame_btns = tk.Frame(ventana, bg="#1a1a2e")
            frame_btns.pack(pady=15)

            def confirmar():
                ventana.destroy()
                subprocess.run(
                    [
                        "git",
                        "-c", "credential.helper=",
                        "-c", "http.extraHeader=",
                        "pull", REPO_URL, "main"
                    ],
                    cwd=ROOT_DIR, capture_output=True, text=True,
                    env=env_sin_auth
                )
                self.lbl_update.config(
                    text="✅ Actualizado. Reinicia para aplicar.",
                    fg="#00ff88"
                )

            tk.Button(
                frame_btns, text="✅ Aplicar actualización",
                bg="#4d45e8", fg="white",
                font=("Helvetica", 11, "bold"),
                relief="flat", padx=15, pady=6,
                cursor="hand2", command=confirmar
            ).pack(side="left", padx=10)

            tk.Button(
                frame_btns, text="❌ Cancelar",
                bg="#16213e", fg="white",
                font=("Helvetica", 11),
                relief="flat", padx=15, pady=6,
                cursor="hand2", command=ventana.destroy
            ).pack(side="left", padx=10)

        except FileNotFoundError:
            self.lbl_update.config(text="⚠️ Git no está instalado.", fg="#ff4466")
        except subprocess.TimeoutExpired:
            self.lbl_update.config(text="⚠️ Tiempo agotado. Revisa tu conexión.", fg="#ff4466")
        except Exception as e:
            self.lbl_update.config(text=f"⚠️ Error: {str(e)[:60]}", fg="#ff4466")

    def _buscar(self):
        for w in self.frame_resultados.winfo_children():
            w.destroy()
        self.lbl_error.config(text="")

        fragmento = self.entry_busq.get().strip().lower()
        if not fragmento:
            self.lbl_error.config(text="Escribe algo para buscar.")
            return

        coincidencias = self.df[self.df["confesion"].str.lower().str.contains(fragmento, na=False)]

        if coincidencias.empty:
            self.lbl_error.config(text="No se encontraron coincidencias. Intenta con otro fragmento.")
            return

        ultimas = coincidencias.tail(3)

        if len(coincidencias) > 1:
            tk.Label(
                self.frame_resultados,
                text=f"Se encontraron {len(coincidencias)} coincidencias. Últimas 3:",
                bg="#1a1a2e", fg="#aaaaaa", font=self.f_result
            ).pack(anchor="w", pady=(0, int(4*self.sc)))

        for _, row in ultimas.iterrows():
            texto   = str(row["confesion"]).strip()
            resumen = (texto[:90] + "...") if len(texto) > 90 else texto
            idx     = int(row["id_csv"]) - 1

            btn = tk.Button(
                self.frame_resultados,
                text=f'[ID {row["id_csv"]}]  {resumen}',
                bg="#16213e", fg="white", font=self.f_result,
                relief="flat", wraplength=int(480*self.sc),
                justify="left", cursor="hand2",
                padx=int(8*self.sc), pady=int(6*self.sc),
                command=lambda i=idx: self._seleccionar(i)
            )
            btn.pack(fill="x", pady=int(2*self.sc))
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#2a2a5e"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#16213e"))

        if len(coincidencias) == 1:
            self._seleccionar(int(coincidencias.iloc[0]["id_csv"]) - 1)

    def _seleccionar(self, idx):
        try:
            numero_base = int(self.entry_base.get().strip())
        except ValueError:
            numero_base = 1
        self.root.destroy()
        self.callback(self.df, idx, numero_base)

class WidgetFormato:
    def __init__(self, parent, formato, sc):
        self.frame = tk.Frame(parent, bg="#2a1a00",
                              highlightbackground="#ffcc00", highlightthickness=2)
        self.frame.pack(pady=int(4*sc), padx=int(10*sc), fill="x")

        tk.Label(self.frame,
                 text=f"⚠️  Confesión con archivo en formato {formato}",
                 bg="#2a1a00", fg="#ffcc00",
                 font=("Helvetica", max(9, int(11*sc)), "bold")
                 ).pack(side="left", padx=int(10*sc), pady=int(6*sc))

        tk.Button(self.frame, text="✕ Cerrar aviso",
                  bg="#ffcc00", fg="#1a1a00",
                  font=("Helvetica", max(8, int(10*sc)), "bold"),
                  relief="flat", cursor="hand2",
                  padx=int(8*sc), pady=int(4*sc),
                  command=self.frame.destroy
                  ).pack(side="right", padx=int(10*sc), pady=int(6*sc))


class InterfazTinder:
    def __init__(self, df, idx_inicio, numero_base):
        self.df                    = df
        self.numero_base           = numero_base
        self.idx_actual            = idx_inicio
        self.variantes             = []
        self.arrastrando           = False
        self.x_inicio              = 0
        self.offset_x              = 0
        self.aceptadas             = 0
        self.ignoradas             = 0
        self.numero_visual_actual  = numero_base
        self.tk_imgs               = []
        self._fila_actual          = None
        self._formato_aviso_actual = None

        self.root = tk.Tk()
        self.root.title("Confesiones")
        self.root.configure(bg="#1a1a2e")
        self.root.resizable(False, False)

        self.sc = _escala(self.root)
        sc = self.sc

        self.root.geometry(f"{int(720*sc)}x{int(950*sc)}")
        self.CANVAS_W = int(700 * sc)
        self.CANVAS_H = int(680 * sc)

        f_contador = ("Helvetica", max(9,  int(13*sc)), "bold")
        f_variante = ("Helvetica", max(8,  int(10*sc)))
        f_instruc  = ("Helvetica", max(8,  int(11*sc)))
        f_dir      = ("Helvetica", max(14, int(26*sc)), "bold")
        f_groseria = ("Helvetica", max(8,  int(10*sc)))

        self.lbl_contador = tk.Label(self.root, text="", bg="#1a1a2e", fg="white", font=f_contador)
        self.lbl_contador.pack(pady=(int(12*sc), int(2*sc)))

        self.lbl_variante = tk.Label(self.root, text="", bg="#1a1a2e", fg="#aaaaaa", font=f_variante)
        self.lbl_variante.pack(pady=(0, int(4*sc)))

        self.canvas = tk.Canvas(self.root, width=self.CANVAS_W, height=self.CANVAS_H,
                                bg="#16213e", highlightthickness=0)
        self.canvas.pack(pady=int(4*sc))

        self.frame_formato = tk.Frame(self.root, bg="#1a1a2e")
        self.frame_formato.pack(fill="x", padx=int(10*sc))

        tk.Label(self.root,
                 text="← Ignorar     Arrastra la imagen     Aceptar →",
                 bg="#1a1a2e", fg="#555577", font=f_instruc).pack(pady=int(4*sc))

        self.lbl_direccion = tk.Label(self.root, text="", bg="#1a1a2e", font=f_dir)
        self.lbl_direccion.pack(pady=int(2*sc))

        # ── Panel "Colocar grosería" ──────────────────────────────────────────
        frame_groseria = tk.Frame(self.root, bg="#1a1a2e")
        frame_groseria.pack(pady=(int(6*sc), int(4*sc)))

        tk.Label(frame_groseria, text="Colocar grosería:",
                 bg="#1a1a2e", fg="#aaaaaa", font=f_groseria
                 ).pack(side="left", padx=(0, int(6*sc)))

        self.entry_groseria = tk.Entry(frame_groseria,
                                       font=("Helvetica", max(9, int(11*sc))),
                                       width=18)
        self.entry_groseria.pack(side="left", padx=(0, int(6*sc)))
        self.entry_groseria.bind("<Return>", lambda e: self._agregar_hereje())

        tk.Button(
            frame_groseria, text="Agregar y regenerar",
            bg="#4d45e8", fg="white", font=f_groseria,
            relief="flat", cursor="hand2",
            padx=int(8*sc), pady=int(3*sc),
            command=self._agregar_hereje
        ).pack(side="left")

        self.lbl_groseria_aviso = tk.Label(self.root, text="", bg="#1a1a2e",
                                           fg="#00ff88", font=f_groseria)
        self.lbl_groseria_aviso.pack()
        # ─────────────────────────────────────────────────────────────────────

        self.canvas.bind("<ButtonPress-1>",  self._inicio_arrastre)
        self.canvas.bind("<B1-Motion>",       self._durante_arrastre)
        self.canvas.bind("<ButtonRelease-1>", self._fin_arrastre)

        self._cargar_confesion()
        self.root.mainloop()

    def _agregar_hereje(self):
        palabra = self.entry_groseria.get().strip().lower()
        if not palabra:
            return
        herejia_path = ruta("Herejia.txt")
        with open(herejia_path, "a", encoding="utf-8") as f:
            f.write(f"\n{palabra}")
        recargar_herejias()
        self.entry_groseria.delete(0, tk.END)
        self.lbl_groseria_aviso.config(text=f'"{palabra}" agregada — regenerando...')
        self.root.after(2500, lambda: self.lbl_groseria_aviso.config(text=""))
        for v in self.variantes:
            if os.path.exists(v):
                os.remove(v)
        self.variantes = []
        self._regenerar_actual()

    def _regenerar_actual(self):
        if self._fila_actual is None:
            return
        self.canvas.delete("all")
        self.canvas.create_text(
            self.CANVAS_W // 2, self.CANVAS_H // 2,
            text="⏳ Regenerando...", fill="white",
            font=("Helvetica", max(12, int(18 * self.sc)), "bold"),
            tags="cargando"
        )
        t = threading.Thread(
            target=self._procesar_en_hilo,
            args=(self._fila_actual, self.numero_visual_actual),
            daemon=True
        )
        t.start()

    def _cargar_confesion(self):
        self.variantes = []
        self.lbl_direccion.config(text="")

        for w in self.frame_formato.winfo_children():
            w.destroy()

        if self.idx_actual >= len(self.df):
            self._finalizar()
            return

        row               = self.df.iloc[self.idx_actual]
        self._fila_actual = row
        numero_visual     = self.numero_visual_actual

        self.canvas.delete("all")
        self.canvas.create_text(
            self.CANVAS_W // 2, self.CANVAS_H // 2,
            text="⏳ Generando...", fill="white",
            font=("Helvetica", max(12, int(18 * self.sc)), "bold"),
            tags="cargando"
        )
        self.lbl_contador.config(
            text=f"Confesión {self.idx_actual + 1} de {len(self.df)}"
                 f"  |  ✅ {self.aceptadas}  ❌ {self.ignoradas}"
        )
        self.lbl_variante.config(text="")

        t = threading.Thread(
            target=self._procesar_en_hilo,
            args=(row, numero_visual),
            daemon=True
        )
        t.start()

    def _procesar_en_hilo(self, row, numero_visual):
        plantilla, sede_custom = resolver_plantilla(str(row["sede"]))
        confesion  = str(row["confesion"])
        link_drive = str(row["imagen"]).strip()

        ruta_adjunto   = None
        requiere_canva = False
        formato_aviso  = None

        if "drive.google.com" in link_drive:
            url_directa = convertir_drive(link_drive)
            if url_directa:
                temp_path = ruta(f"archivos/temp_{numero_visual}")
                resultado = descargar(url_directa, temp_path)
                if resultado and resultado.startswith("FORMATO:"):
                    formato_aviso  = resultado.split("FORMATO:")[1]
                    requiere_canva = True
                elif resultado:
                    ruta_adjunto = resultado

        if ruta_adjunto and os.path.splitext(ruta_adjunto)[1].lower() in [".mp4", ".mov", ".webm", ".avi"]:
            self.root.after(0, lambda: self.canvas.create_text(
                self.CANVAS_W // 2, self.CANVAS_H // 2 + int(50 * self.sc),
                text="🎬 Procesando video, puede tardar unos minutos...",
                fill="#ffcc00",
                font=("Helvetica", max(8, int(11 * self.sc))),
                tags="cargando"
            ))

        try:
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
            self.root.after(0, self._mostrar_resultado, [], formato_aviso, confesion, True)
            return

        base = os.path.join(CARPETA_CONFESIONES, f"Confesion {numero_visual}")
        candidatos = [
            f"{base}.png",
            f"{base} (Formato no disponible, configurar en Canva).png",
            f"{base} V1.png",
            f"{base} V1.gif",
            f"{base} V1.mp4",
            f"{base} V2 (1).png",
            f"{base} V2 (2).png",
            f"{base} V2 (2).gif",
            f"{base} V2 (2).mp4",
        ]
        variantes = [c for c in candidatos if os.path.exists(c)]
        self.root.after(0, self._mostrar_resultado, variantes, formato_aviso, confesion, False)

    def _mostrar_resultado(self, variantes, formato_aviso, confesion_texto, hubo_error):
        self.variantes             = variantes
        self._formato_aviso_actual = formato_aviso

        self.lbl_contador.config(
            text=f"Confesión {self.idx_actual + 1} de {len(self.df)}"
                 f"  |  ✅ {self.aceptadas}  ❌ {self.ignoradas}"
        )

        if formato_aviso:
            WidgetFormato(self.frame_formato, formato_aviso, self.sc)

        if not self.variantes:
            self._mostrar_sin_imagen(confesion_texto, hubo_error)
            return

        self._mostrar_variantes()

    def _mostrar_sin_imagen(self, texto, hubo_error):
        cw = self.CANVAS_W
        ch = self.CANVAS_H
        sc = self.sc
        self.canvas.delete("all")
        self.tk_imgs = []

        self.canvas.create_rectangle(0, 0, cw, ch, fill="#1a1a2e", outline="")

        aviso       = "⚠️ Error al generar imagen — evalúa el texto" if hubo_error else "⚠️ Sin imagen generada — evalúa el texto"
        color_aviso = "#ff4466" if hubo_error else "#ffcc00"

        self.canvas.create_text(
            cw // 2, int(ch * 0.18),
            text=aviso, fill=color_aviso,
            font=("Helvetica", max(9, int(12*sc)), "bold"),
            tags="imagen"
        )
        self.canvas.create_text(
            cw // 2, int(ch * 0.52),
            text=texto, fill="white",
            font=("Helvetica", max(9, int(12*sc))),
            width=int(cw * 0.85), justify="center",
            tags="imagen"
        )
        self.lbl_variante.config(text="Sin archivos — evalúa igualmente con arrastre")

    def _thumb(self, ruta_img, max_w, max_h):
        ext = os.path.splitext(ruta_img)[1].lower()
        if ext in [".mp4", ".mov", ".webm", ".avi"]:
            try:
                from moviepy.editor import VideoFileClip
                clip  = VideoFileClip(ruta_img)
                frame = clip.get_frame(0)
                clip.close()
                img = Image.fromarray(frame).convert("RGBA")
            except Exception:
                img = Image.new("RGBA", (max_w, max_h), (30, 30, 60, 255))
        else:
            img = Image.open(ruta_img).convert("RGBA")
        img.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
        return img

    def _dibujar_indicador(self, x, y_top, ruta_archivo):
        tipo = _tipo_media(ruta_archivo)
        if not tipo:
            return
        sc        = self.sc
        texto     = f"▶ {tipo}"
        font_size = max(8, int(10*sc))
        pad       = int(5*sc)
        ancho_rec = int(65*sc)
        alto_rec  = font_size + pad * 2
        self.canvas.create_rectangle(
            x - ancho_rec//2, y_top,
            x + ancho_rec//2, y_top + alto_rec,
            fill="#1a1a1a", outline="#ffcc00", tags="imagen"
        )
        self.canvas.create_text(
            x, y_top + alto_rec//2,
            text=texto, fill="#ffcc00",
            font=("Helvetica", font_size, "bold"),
            tags="imagen"
        )

    def _mostrar_variantes(self, dx=0):
        sc = self.sc
        cw = self.CANVAS_W
        ch = self.CANVAS_H
        self.canvas.delete("all")
        self.tk_imgs = []
        n  = len(self.variantes)
        cx = cw // 2

        if n == 1:
            self.lbl_variante.config(text="")
            img    = self._thumb(self.variantes[0], int(cw*0.97), int(ch*0.97))
            tk_img = ImageTk.PhotoImage(img)
            self.tk_imgs.append(tk_img)
            self.canvas.create_image(cx+dx, ch//2, anchor="center", image=tk_img, tags="imagen")
            self._dibujar_indicador(cx+dx, ch//2 - img.height//2, self.variantes[0])

        elif n == 3:
            self.lbl_variante.config(text="V1 ↑   |   V2(1) ↙   V2(2) ↘")
            specs = [
                (self.variantes[0], cx,           int(ch*0.33), int(cw*0.64), int(cw*0.64)),
                (self.variantes[1], int(cw*0.24), int(ch*0.78), int(cw*0.44), int(cw*0.44)),
                (self.variantes[2], int(cw*0.76), int(ch*0.78), int(cw*0.44), int(cw*0.44)),
            ]
            for v, x, y, mw, mh in specs:
                img    = self._thumb(v, mw, mh)
                tk_img = ImageTk.PhotoImage(img)
                self.tk_imgs.append(tk_img)
                self.canvas.create_image(x+dx, y, anchor="center", image=tk_img, tags="imagen")
                self._dibujar_indicador(x+dx, y - img.height//2, v)

        else:
            self.lbl_variante.config(text="")
            w_cada = int(cw * 0.47)
            for i, v in enumerate(self.variantes):
                img    = self._thumb(v, w_cada, int(ch*0.97))
                tk_img = ImageTk.PhotoImage(img)
                self.tk_imgs.append(tk_img)
                x = int(cw*0.25) + i*int(cw*0.50)
                self.canvas.create_image(x+dx, ch//2, anchor="center", image=tk_img, tags="imagen")
                self._dibujar_indicador(x+dx, ch//2 - img.height//2, v)

    def _inicio_arrastre(self, event):
        self.arrastrando = True
        self.x_inicio    = event.x
        self.offset_x    = 0

    def _durante_arrastre(self, event):
        if not self.arrastrando:
            return
        self.offset_x = event.x - self.x_inicio
        if self.variantes:
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
            if self.variantes:
                self._mostrar_variantes()
            self.lbl_direccion.config(text="")

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

    def _finalizar(self):
        self.canvas.delete("all")
        self.lbl_contador.config(
            text=f"✅ Aceptadas: {self.aceptadas}  |  ❌ Ignoradas: {self.ignoradas}")
        self.lbl_variante.config(text="Proceso finalizado 🎉")
        self.lbl_direccion.config(text="")
        self.root.after(3000, self.root.destroy)


def lanzar_interfaz(df):
    def iniciar(df, idx_inicio, numero_base):
        df_procesar = df.iloc[idx_inicio:].reset_index(drop=True)
        InterfazTinder(df_procesar, 0, numero_base)
    PantallaInicio(df, iniciar)