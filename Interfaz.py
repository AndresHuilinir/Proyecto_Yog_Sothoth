# Interfaz.py
import tkinter as tk
from tkinter import font as tkfont
from PIL import Image, ImageTk
import os
from Conocimiento import generar_imagen
from Portales import resolver_plantilla
from Rezos import convertir_drive, descargar
from Orden_universal import ruta

UMBRAL_ARRASTRE = 100

class PantallaInicio:
    def __init__(self, df, callback):
        self.df       = df
        self.callback = callback

        self.root = tk.Tk()
        self.root.title("Confesiones — Inicio")
        self.root.configure(bg="#1a1a2e")
        self.root.geometry("500x400")
        self.root.resizable(False, False)

        tk.Label(
            self.root, text="⚙️ Configuración de sesión",
            bg="#1a1a2e", fg="white",
            font=("Helvetica", 18, "bold")
        ).pack(pady=(40, 20))

        tk.Label(
            self.root,
            text=f"Total de confesiones disponibles: {len(df)}",
            bg="#1a1a2e", fg="#aaaaaa",
            font=("Helvetica", 11)
        ).pack(pady=(0, 20))

        # ID de inicio
        tk.Label(
            self.root, text="ID de inicio:",
            bg="#1a1a2e", fg="white",
            font=("Helvetica", 12)
        ).pack()
        self.entry_id = tk.Entry(
            self.root, font=("Helvetica", 14),
            justify="center", width=10
        )
        self.entry_id.pack(pady=(5, 20))
        self.entry_id.insert(0, "1")

        # Número visual base
        tk.Label(
            self.root, text="Número visual de inicio:",
            bg="#1a1a2e", fg="white",
            font=("Helvetica", 12)
        ).pack()
        self.entry_base = tk.Entry(
            self.root, font=("Helvetica", 14),
            justify="center", width=10
        )
        self.entry_base.pack(pady=(5, 30))
        self.entry_base.insert(0, "1")

        self.lbl_error = tk.Label(
            self.root, text="", bg="#1a1a2e", fg="#ff4466",
            font=("Helvetica", 11)
        )
        self.lbl_error.pack()

        tk.Button(
            self.root, text="Comenzar →",
            bg="#4d45e8", fg="white",
            font=("Helvetica", 13, "bold"),
            relief="flat", padx=20, pady=8,
            cursor="hand2",
            command=self._confirmar
        ).pack(pady=10)

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
        self.tk_imgs              = []  # mantener referencias para evitar GC

        self.root = tk.Tk()
        self.root.title("Confesiones")
        self.root.configure(bg="#1a1a2e")
        self.root.geometry("720x950")
        self.root.resizable(False, False)

        # Header
        self.lbl_contador = tk.Label(
            self.root, text="", bg="#1a1a2e", fg="white",
            font=("Helvetica", 13, "bold")
        )
        self.lbl_contador.pack(pady=(15, 3))

        self.lbl_variante = tk.Label(
            self.root, text="", bg="#1a1a2e", fg="#aaaaaa",
            font=("Helvetica", 10)
        )
        self.lbl_variante.pack(pady=(0, 5))

        # Canvas
        self.canvas = tk.Canvas(
            self.root, width=700, height=720,
            bg="#16213e", highlightthickness=0
        )
        self.canvas.pack(pady=5)

        # Aviso
        self.lbl_aviso = tk.Label(
            self.root, text="", bg="#1a1a2e", fg="#ffcc00",
            font=("Helvetica", 10), wraplength=680
        )
        self.lbl_aviso.pack(pady=3)

        # Instrucciones
        tk.Label(
            self.root,
            text="← Ignorar     Arrastra la imagen     Aceptar →",
            bg="#1a1a2e", fg="#555577",
            font=("Helvetica", 11)
        ).pack(pady=3)

        # Indicador dirección
        self.lbl_direccion = tk.Label(
            self.root, text="", bg="#1a1a2e",
            font=("Helvetica", 26, "bold")
        )
        self.lbl_direccion.pack(pady=3)

        # Eventos
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
        self.lbl_aviso.config(text="")
        self.lbl_direccion.config(text="")
        self.tk_imgs = []

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
                        text="⚠️ Archivo adjunto en formato no admitido. Configurar en Canva."
                    )
                elif resultado:
                    ruta_adjunto = resultado

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

        total = len(self.df)
        self.lbl_contador.config(
            text=f"Confesión {self.idx_actual + 1} de {total}  |  ✅ {self.aceptadas}  ❌ {self.ignoradas}"
        )
        self._mostrar_variantes()

    def _mostrar_variantes(self):
        self.canvas.delete("all")
        self.tk_imgs = []
        n = len(self.variantes)

        if n == 1:
            # Una sola imagen centrada
            self.lbl_variante.config(text="")
            img = Image.open(self.variantes[0]).convert("RGBA")
            img.thumbnail((680, 680), Image.Resampling.LANCZOS)
            tk_img = ImageTk.PhotoImage(img)
            self.tk_imgs.append(tk_img)
            self.canvas.create_image(350, 360, anchor="center",
                                     image=tk_img, tags="imagen")

        elif n == 3:
            # Pirámide: V1 arriba centrada, V2(1) y V2(2) abajo lado a lado
            self.lbl_variante.config(text="V1 arriba  |  V2(1) y V2(2) abajo")

            # V1 arriba
            img_top = Image.open(self.variantes[0]).convert("RGBA")
            img_top.thumbnail((460, 460), Image.Resampling.LANCZOS)
            tk_top = ImageTk.PhotoImage(img_top)
            self.tk_imgs.append(tk_top)
            self.canvas.create_image(350, 240, anchor="center",
                                     image=tk_top, tags="imagen")

            # V2(1) abajo izquierda
            img_bl = Image.open(self.variantes[1]).convert("RGBA")
            img_bl.thumbnail((320, 320), Image.Resampling.LANCZOS)
            tk_bl = ImageTk.PhotoImage(img_bl)
            self.tk_imgs.append(tk_bl)
            self.canvas.create_image(175, 590, anchor="center",
                                     image=tk_bl, tags="imagen")

            # V2(2) abajo derecha
            img_br = Image.open(self.variantes[2]).convert("RGBA")
            img_br.thumbnail((320, 320), Image.Resampling.LANCZOS)
            tk_br = ImageTk.PhotoImage(img_br)
            self.tk_imgs.append(tk_br)
            self.canvas.create_image(525, 590, anchor="center",
                                     image=tk_br, tags="imagen")

        else:
            # 2 imágenes lado a lado
            self.lbl_variante.config(text="")
            for i, v in enumerate(self.variantes):
                img = Image.open(v).convert("RGBA")
                img.thumbnail((330, 680), Image.Resampling.LANCZOS)
                tk_img = ImageTk.PhotoImage(img)
                self.tk_imgs.append(tk_img)
                x = 175 + i * 350
                self.canvas.create_image(x, 360, anchor="center",
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
        self.canvas.move("imagen", self.offset_x - (
                self.offset_x - (event.x - self.x_inicio)
        ), 0)
        # Mover todo el grupo
        self.canvas.delete("all")
        self.tk_imgs_backup = self.tk_imgs[:]
        n = len(self.variantes)
        dx = self.offset_x

        if n == 1:
            self.canvas.create_image(350 + dx, 360, anchor="center",
                                     image=self.tk_imgs[0], tags="imagen")
        elif n == 3:
            self.canvas.create_image(350 + dx, 240, anchor="center",
                                     image=self.tk_imgs[0], tags="imagen")
            self.canvas.create_image(175 + dx, 590, anchor="center",
                                     image=self.tk_imgs[1], tags="imagen")
            self.canvas.create_image(525 + dx, 590, anchor="center",
                                     image=self.tk_imgs[2], tags="imagen")
        else:
            for i, tk_img in enumerate(self.tk_imgs):
                x = 175 + i * 350
                self.canvas.create_image(x + dx, 360, anchor="center",
                                         image=tk_img, tags="imagen")

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
    """Punto de entrada desde Ritual.py"""
    def iniciar(df, idx_inicio, numero_base):
        df_procesar = df.iloc[idx_inicio:].reset_index(drop=True)
        InterfazTinder(df_procesar, 0, numero_base)

    PantallaInicio(df, iniciar)