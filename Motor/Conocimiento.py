from PIL import Image, ImageDraw, ImageFont
from pilmoji import Pilmoji
from pilmoji.source import GoogleEmojiSource
import os
import re
import math
from Orden_universal import (
    Y_NUMERO, Y_CAMPUS, Y_CONFESION, Y_CENTRO_CONFESION, X_NUMERO, X_CAMPUS,
    X_CENTRO_CONFESION, MARGEN_LATERAL, ANCHO_IMAGEN, SIZE_FUENTE_NUMERO,
    SIZE_FUENTE_SEDE, SIZE_FUENTE_CONFESION, Y_LIMITE_INFERIOR_CONFESION, Y_MITAD,
    FUENTE_MONTSERRAT, FUENTE_OPENSANS, FUENTE_OPENSANS_XB,
    COLOR_BLANCO, COLORES_CONFESION, CARPETA_CONFESIONES
)

DESFASE_CENSURADOR = 0
LIMITE_PALABRAS    = 175  # ajustar según Erudito_a_prueba.py

_DUMMY_IMG  = Image.new("RGB", (1, 1))
_DUMMY_DRAW = ImageDraw.Draw(_DUMMY_IMG)

_PATRON_EMOJI = re.compile(
    "["
    "\U0001F600-\U0001FFFF"
    "\U00002702-\U000027B0"
    "\U000024C2-\U0001F251"
    "\u2640-\u2642"
    "\u2600-\u2B55"
    "\u200d\u23cf\u23e9\u231a\ufe0f\u3030"
    "]+",
    flags=re.UNICODE,
)

def _cargar_herejias():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Herejia.txt")
    if not os.path.exists(path):
        return set()
    with open(path, encoding="utf-8") as f:
        return {w.strip().lower() for w in f.readlines() if w.strip()}

_HEREJIAS = _cargar_herejias()

def recargar_herejias():
    global _HEREJIAS
    _HEREJIAS = _cargar_herejias()

def _es_video(ruta):
    return os.path.splitext(ruta)[1].lower() in [".mp4", ".mov", ".webm", ".avi"]

def _es_gif(ruta):
    return os.path.splitext(ruta)[1].lower() == ".gif"

def _pilmoji_text_seguro(pilmoji, draw, pos, texto, font, fill):
    try:
        pilmoji.text(pos, texto, font=font, fill=fill)
    except Exception:
        texto_limpio = _PATRON_EMOJI.sub("", texto).strip()
        draw.text(pos, texto_limpio, font=font, fill=fill)

def _aplicar_censura(draw, linea, fuente, x_inicio, y):
    if not _HEREJIAS:
        return
    palabras = linea.split(" ")
    x_cursor = x_inicio
    for palabra in palabras:
        if not palabra:
            bbox_esp = _DUMMY_DRAW.textbbox((0, 0), " ", font=fuente)
            x_cursor += bbox_esp[2] - bbox_esp[0]
            continue
        bbox_p  = _DUMMY_DRAW.textbbox((0, 0), palabra, font=fuente)
        ancho_p = bbox_p[2] - bbox_p[0]
        alto_p  = bbox_p[3] - bbox_p[1]
        limpia  = re.sub(r"[^\w]", "", palabra).lower()
        if limpia in _HEREJIAS:
            inicio_rect = x_cursor + int(ancho_p * DESFASE_CENSURADOR)
            draw.rectangle(
                [inicio_rect, y, x_cursor + ancho_p, y + alto_p + 2],
                fill=(0, 0, 0, 255)
            )
        bbox_esp = _DUMMY_DRAW.textbbox((0, 0), palabra + " ", font=fuente)
        x_cursor += bbox_esp[2] - bbox_esp[0]

def dividir_texto_en_lineas(texto, fuente, ancho_max):
    palabras = texto.split()
    lineas, linea_actual = [], ""
    for palabra in palabras:
        prueba = linea_actual + (" " if linea_actual else "") + palabra
        bbox   = _DUMMY_DRAW.textbbox((0, 0), prueba, font=fuente)
        if (bbox[2] - bbox[0]) <= ancho_max:
            linea_actual = prueba
        else:
            if linea_actual:
                lineas.append(linea_actual)
            linea_actual = palabra
    if linea_actual:
        lineas.append(linea_actual)
    return lineas

def ajustar_fuente_confesion(texto, fuente_path, ancho_max, y_inicio, y_limite, size_default):
    for size in range(size_default, 7, -1):
        fuente = ImageFont.truetype(fuente_path, size)
        lineas = dividir_texto_en_lineas(texto, fuente, ancho_max)
        alto_total = sum(
            (_DUMMY_DRAW.textbbox((0, 0), l, font=fuente)[3]
             - _DUMMY_DRAW.textbbox((0, 0), l, font=fuente)[1] + 10)
            for l in lineas
        )
        if y_inicio + alto_total <= y_limite:
            return fuente, lineas
    fuente = ImageFont.truetype(fuente_path, 8)
    return fuente, dividir_texto_en_lineas(texto, fuente, ancho_max)

def formatear_con_dos_puntos(s: str) -> str:
    s = str(s)
    grupos = []
    i = len(s)
    while i > 0:
        grupos.append(s[max(0, i - 2):i])
        i -= 2
    grupos.reverse()
    return ":".join(grupos)

def _componer_imagen(ruta_plantilla, nombre_plantilla, numero, sede_custom,
                     lineas, fuente, color_confesion,
                     adjunto=None, y_adjunto_desde=None):
    img  = Image.open(ruta_plantilla).convert("RGBA")
    draw = ImageDraw.Draw(img)

    fuente_numero = ImageFont.truetype(FUENTE_MONTSERRAT, SIZE_FUENTE_NUMERO)
    fuente_campus = ImageFont.truetype(FUENTE_OPENSANS,   SIZE_FUENTE_SEDE)
    ancho_max     = ANCHO_IMAGEN - MARGEN_LATERAL * 2

    texto_numero = formatear_con_dos_puntos(numero)
    bbox_n   = _DUMMY_DRAW.textbbox((0, 0), texto_numero, font=fuente_numero)
    x_numero = X_NUMERO - (bbox_n[2] - bbox_n[0]) // 2

    lineas_con_pos = []

    alto_total = sum(
        (_DUMMY_DRAW.textbbox((0, 0), l, font=fuente)[3]
         - _DUMMY_DRAW.textbbox((0, 0), l, font=fuente)[1] + 10)
        for l in lineas
    ) if lineas else 0

    y_actual = max(Y_CONFESION, Y_CENTRO_CONFESION - alto_total // 2)

    with Pilmoji(img, source=GoogleEmojiSource) as pilmoji:
        _pilmoji_text_seguro(pilmoji, draw,
                             (x_numero, Y_NUMERO), texto_numero, fuente_numero, COLOR_BLANCO)

        if nombre_plantilla == "Default" and sede_custom:
            bbox_c   = _DUMMY_DRAW.textbbox((0, 0), sede_custom, font=fuente_campus)
            x_campus = X_CAMPUS - (bbox_c[2] - bbox_c[0]) // 2
            _pilmoji_text_seguro(pilmoji, draw,
                                 (x_campus, Y_CAMPUS), sede_custom, fuente_campus, COLOR_BLANCO)

        for linea in lineas:
            bbox = _DUMMY_DRAW.textbbox((0, 0), linea, font=fuente)
            x    = X_CENTRO_CONFESION - (bbox[2] - bbox[0]) // 2
            _pilmoji_text_seguro(pilmoji, draw,
                                 (x, y_actual), linea, fuente, color_confesion)
            lineas_con_pos.append((linea, x, y_actual))
            y_actual += (bbox[3] - bbox[1]) + 10

    for linea, x, y in lineas_con_pos:
        _aplicar_censura(draw, linea, fuente, x, y)

    if adjunto and y_adjunto_desde:
        espacio_h = ancho_max
        espacio_v = Y_LIMITE_INFERIOR_CONFESION - y_adjunto_desde
        copia = adjunto.copy()
        copia.thumbnail((espacio_h, espacio_v), Image.Resampling.LANCZOS)
        pos_x = (ANCHO_IMAGEN - copia.width)  // 2
        pos_y = y_adjunto_desde + (espacio_v  - copia.height) // 2
        img.alpha_composite(copia, (pos_x, pos_y))

    return img

def _componer_gif_frames(base_pil, ruta_gif, y_desde, ancho_max):
    espacio_v = Y_LIMITE_INFERIOR_CONFESION - y_desde
    gif = Image.open(ruta_gif)
    frames_out, duraciones = [], []
    try:
        while True:
            frame  = gif.copy().convert("RGBA")
            scale  = min(ancho_max / max(frame.width, 1), espacio_v / max(frame.height, 1))
            new_w  = max(1, int(frame.width  * scale))
            new_h  = max(1, int(frame.height * scale))
            frame  = frame.resize((new_w, new_h), Image.Resampling.LANCZOS)
            comp   = base_pil.copy()
            pos_x  = max(0, (ANCHO_IMAGEN - new_w) // 2)
            pos_y  = max(0, y_desde + (espacio_v - new_h) // 2)
            comp.alpha_composite(frame, (pos_x, pos_y))
            frames_out.append(comp)
            duraciones.append(gif.info.get("duration", 100))
            gif.seek(gif.tell() + 1)
    except EOFError:
        pass
    return frames_out, duraciones

def _guardar_gif(frames, duraciones, path):
    if not frames:
        return
    frames[0].save(
        path, save_all=True, append_images=frames[1:],
        loop=0, duration=duraciones, disposal=2, format="GIF"
    )

def _componer_video_clip(base_pil, ruta_video, y_desde, ancho_max):
    try:
        from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
        import numpy as np
    except ImportError:
        print("[WARN] moviepy no instalado.")
        return None

    espacio_v  = Y_LIMITE_INFERIOR_CONFESION - y_desde
    video_clip = VideoFileClip(ruta_video)
    scale      = min(ancho_max / max(video_clip.w, 1), espacio_v / max(video_clip.h, 1))
    new_w      = max(1, int(video_clip.w * scale))
    new_h      = max(1, int(video_clip.h * scale))
    video_res  = video_clip.resize((new_w, new_h))
    pos_x      = (ANCHO_IMAGEN - new_w) // 2
    pos_y      = y_desde + (espacio_v - new_h) // 2
    video_pos  = video_res.set_position((pos_x, pos_y))
    bg_array   = np.array(base_pil.convert("RGB"))
    bg_clip    = ImageClip(bg_array, duration=video_clip.duration)
    return CompositeVideoClip([bg_clip, video_pos], size=(ANCHO_IMAGEN, ANCHO_IMAGEN))

def _conf_path(nombre):
    return os.path.join(CARPETA_CONFESIONES, nombre)

def _generar_versiones_gif(ruta_plantilla, nombre_plantilla, numero, sede_custom,
                            confesion, color_confesion, ruta_gif, ancho_max, sufijo=""):
    f_m, l_m = ajustar_fuente_confesion(
        confesion, FUENTE_OPENSANS_XB, ancho_max, Y_CONFESION, Y_MITAD - 20, SIZE_FUENTE_CONFESION)
    base_v1  = _componer_imagen(ruta_plantilla, nombre_plantilla, numero, sede_custom, l_m, f_m, color_confesion)
    fr_v1, dur_v1 = _componer_gif_frames(base_v1, ruta_gif, Y_MITAD, ancho_max)
    _guardar_gif(fr_v1, dur_v1, _conf_path(f"Confesion {numero}{sufijo} V1.gif"))

    f_c, l_c = ajustar_fuente_confesion(
        confesion, FUENTE_OPENSANS_XB, ancho_max, Y_CONFESION, Y_LIMITE_INFERIOR_CONFESION, SIZE_FUENTE_CONFESION)
    _componer_imagen(ruta_plantilla, nombre_plantilla, numero, sede_custom, l_c, f_c, color_confesion
                     ).save(_conf_path(f"Confesion {numero}{sufijo} V2 (1).png"))

    base_v2 = _componer_imagen(ruta_plantilla, nombre_plantilla, numero, sede_custom, [], f_c, color_confesion)
    fr_v2, dur_v2 = _componer_gif_frames(base_v2, ruta_gif, Y_CONFESION, ancho_max)
    _guardar_gif(fr_v2, dur_v2, _conf_path(f"Confesion {numero}{sufijo} V2 (2).gif"))

def _generar_versiones_video(ruta_plantilla, nombre_plantilla, numero, sede_custom,
                              confesion, color_confesion, ruta_video, ancho_max, sufijo=""):
    f_m, l_m = ajustar_fuente_confesion(
        confesion, FUENTE_OPENSANS_XB, ancho_max, Y_CONFESION, Y_MITAD - 20, SIZE_FUENTE_CONFESION)
    base_v1  = _componer_imagen(ruta_plantilla, nombre_plantilla, numero, sede_custom, l_m, f_m, color_confesion)
    clip_v1  = _componer_video_clip(base_v1, ruta_video, Y_MITAD, ancho_max)
    if clip_v1:
        try:
            clip_v1.write_videofile(
                _conf_path(f"Confesion {numero}{sufijo} V1.mp4"), logger=None, verbose=False)
        finally:
            clip_v1.close()

    f_c, l_c = ajustar_fuente_confesion(
        confesion, FUENTE_OPENSANS_XB, ancho_max, Y_CONFESION, Y_LIMITE_INFERIOR_CONFESION, SIZE_FUENTE_CONFESION)
    _componer_imagen(ruta_plantilla, nombre_plantilla, numero, sede_custom, l_c, f_c, color_confesion
                     ).save(_conf_path(f"Confesion {numero}{sufijo} V2 (1).png"))

    base_v2  = _componer_imagen(ruta_plantilla, nombre_plantilla, numero, sede_custom, [], f_c, color_confesion)
    clip_v2  = _componer_video_clip(base_v2, ruta_video, Y_CONFESION, ancho_max)
    if clip_v2:
        try:
            clip_v2.write_videofile(
                _conf_path(f"Confesion {numero}{sufijo} V2 (2).mp4"), logger=None, verbose=False)
        finally:
            clip_v2.close()

def _generar_imagen_simple(nombre_plantilla, numero, confesion,
                            sede_custom=None, ruta_adjunto=None,
                            requiere_canva=False, sufijo=""):
    color_confesion = COLORES_CONFESION.get(nombre_plantilla, COLORES_CONFESION["Default"])
    ruta_plantilla  = (
        f"Plantillas/{nombre_plantilla}.png"
        if os.path.exists(f"Plantillas/{nombre_plantilla}.png")
        else "Plantillas/Default.png"
    )
    ancho_max = ANCHO_IMAGEN - MARGEN_LATERAL * 2

    if not ruta_adjunto:
        f, l = ajustar_fuente_confesion(
            confesion, FUENTE_OPENSANS_XB,
            ancho_max, Y_CONFESION, Y_LIMITE_INFERIOR_CONFESION, SIZE_FUENTE_CONFESION
        )
        img = _componer_imagen(ruta_plantilla, nombre_plantilla, numero,
                               sede_custom, l, f, color_confesion)
        if requiere_canva:
            nombre_archivo = f"Confesion {numero}{sufijo} (Formato no disponible, configurar en Canva).png"
        else:
            nombre_archivo = f"Confesion {numero}{sufijo}.png"
        img.save(_conf_path(nombre_archivo))

    elif _es_gif(ruta_adjunto):
        _generar_versiones_gif(ruta_plantilla, nombre_plantilla, numero, sede_custom,
                               confesion, color_confesion, ruta_adjunto, ancho_max, sufijo)

    elif _es_video(ruta_adjunto):
        _generar_versiones_video(ruta_plantilla, nombre_plantilla, numero, sede_custom,
                                 confesion, color_confesion, ruta_adjunto, ancho_max, sufijo)

    else:
        adjunto  = Image.open(ruta_adjunto).convert("RGBA")
        f_m, l_m = ajustar_fuente_confesion(
            confesion, FUENTE_OPENSANS_XB, ancho_max, Y_CONFESION, Y_MITAD - 20, SIZE_FUENTE_CONFESION)
        f_c, l_c = ajustar_fuente_confesion(
            confesion, FUENTE_OPENSANS_XB, ancho_max, Y_CONFESION, Y_LIMITE_INFERIOR_CONFESION, SIZE_FUENTE_CONFESION)

        _componer_imagen(ruta_plantilla, nombre_plantilla, numero, sede_custom,
                         l_m, f_m, color_confesion,
                         adjunto=adjunto, y_adjunto_desde=Y_MITAD
                         ).save(_conf_path(f"Confesion {numero}{sufijo} V1.png"))

        _componer_imagen(ruta_plantilla, nombre_plantilla, numero, sede_custom,
                         l_c, f_c, color_confesion
                         ).save(_conf_path(f"Confesion {numero}{sufijo} V2 (1).png"))

        _componer_imagen(ruta_plantilla, nombre_plantilla, numero, sede_custom,
                         [], f_c, color_confesion,
                         adjunto=adjunto, y_adjunto_desde=Y_CONFESION
                         ).save(_conf_path(f"Confesion {numero}{sufijo} V2 (2).png"))

def generar_imagen(nombre_plantilla, numero, confesion,
                   sede_custom=None, ruta_adjunto=None, requiere_canva=False):
    os.makedirs(CARPETA_CONFESIONES, exist_ok=True)

    palabras = confesion.split()

    if len(palabras) > LIMITE_PALABRAS and not ruta_adjunto:
        total_partes = math.ceil(len(palabras) / LIMITE_PALABRAS)
        for idx in range(total_partes):
            parte = " ".join(palabras[idx * LIMITE_PALABRAS:(idx + 1) * LIMITE_PALABRAS])
            _generar_imagen_simple(
                nombre_plantilla = nombre_plantilla,
                numero           = numero,
                confesion        = parte,
                sede_custom      = sede_custom,
                requiere_canva   = requiere_canva,
                sufijo           = f" parte_{idx + 1}",
            )
        return

    _generar_imagen_simple(
        nombre_plantilla = nombre_plantilla,
        numero           = numero,
        confesion        = confesion,
        sede_custom      = sede_custom,
        ruta_adjunto     = ruta_adjunto,
        requiere_canva   = requiere_canva,
        sufijo           = "",
    )

def indecision(df, id_target, accion_texto):
    fila = df[df["id_csv"] == id_target]
    if not fila.empty:
        texto    = str(fila.iloc[0]["confesion"]).strip()
        resumen  = (texto[:70] + "...") if len(texto) > 70 else texto
        confirma = input(
            f'\n¿Quieres {accion_texto} la confesión "{resumen}" (ID {id_target})? (S/N): '
        ).strip().upper()
        return confirma == "S"
    else:
        print(f"-> Error: No se encontró el ID {id_target}.")
        return False

def las_pruebas(df, modo="consola"):
    print("\n--- [LAS PRUEBAS: Configuración de Sesión] ---")
    print(f"   Total de confesiones: {len(df)}")
    print(f"   Rango de IDs: {df['id_csv'].min()} → {df['id_csv'].max()}\n")

    while True:
        try:
            fila_inicio = int(input("¿Desde qué ID deseas comenzar?: "))
            if indecision(df, fila_inicio, "comenzar desde"):
                break
        except ValueError:
            print("Ingresa un número válido.")

    if modo == "consola":
        while True:
            try:
                rango = int(input("\n¿Cuántas confesiones procesar?: "))
                if rango >= 1:
                    break
                print("Debe ser 1 o mayor.")
            except ValueError:
                print("Ingresa un número válido.")
    else:
        rango = len(df)

    ignorados = set()
    if modo == "consola":
        print("\n--- Modo Ignorar ---")
        while True:
            entrada = input("ID a ignorar (X para terminar): ").strip().upper()
            if entrada == "X":
                break
            try:
                id_ignorar = int(entrada)
                if indecision(df, id_ignorar, "ignorar"):
                    ignorados.add(id_ignorar)
                    print(f"-> ID {id_ignorar} agregado a ignorados.\n")
                else:
                    print("-> Cancelado.\n")
            except ValueError:
                print("Ingresa un número válido o X para terminar.")

    while True:
        try:
            numero_base = int(input("\n¿Con qué número visual quieres empezar?: "))
            break
        except ValueError:
            numero_base = 1
            break

    return fila_inicio, rango, ignorados, numero_base