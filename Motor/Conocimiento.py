# Conocimiento.py
from PIL import Image, ImageDraw, ImageFont
from pilmoji import Pilmoji
from pilmoji.source import GoogleEmojiSource
import os
import re
from Orden_universal import (
    Y_NUMERO, Y_CAMPUS, Y_CONFESION, X_NUMERO, X_CAMPUS,
    MARGEN_LATERAL, ANCHO_IMAGEN, SIZE_FUENTE_NUMERO, SIZE_FUENTE_SEDE,
    SIZE_FUENTE_CONFESION, Y_LIMITE_INFERIOR_CONFESION, Y_MITAD,
    FUENTE_MONTSERRAT, FUENTE_OPENSANS, FUENTE_OPENSANS_XB,
    COLOR_BLANCO, COLORES_CONFESION
)

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

# =========================
# FUNCIONES AUXILIARES
# =========================
def _pilmoji_text_seguro(pilmoji, draw, pos, texto, font, fill):
    try:
        pilmoji.text(pos, texto, font=font, fill=fill)
    except Exception:
        texto_limpio = _PATRON_EMOJI.sub("", texto).strip()
        draw.text(pos, texto_limpio, font=font, fill=fill)

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

    with Pilmoji(img, source=GoogleEmojiSource) as pilmoji:
        _pilmoji_text_seguro(pilmoji, draw,
                             (x_numero, Y_NUMERO), texto_numero, fuente_numero, COLOR_BLANCO)

        if nombre_plantilla == "Default" and sede_custom:
            bbox_c   = _DUMMY_DRAW.textbbox((0, 0), sede_custom, font=fuente_campus)
            x_campus = X_CAMPUS - (bbox_c[2] - bbox_c[0]) // 2
            _pilmoji_text_seguro(pilmoji, draw,
                                 (x_campus, Y_CAMPUS), sede_custom, fuente_campus, COLOR_BLANCO)

        y_actual = Y_CONFESION
        for linea in lineas:
            bbox = _DUMMY_DRAW.textbbox((0, 0), linea, font=fuente)
            x    = (ANCHO_IMAGEN - (bbox[2] - bbox[0])) // 2
            _pilmoji_text_seguro(pilmoji, draw,
                                 (x, y_actual), linea, fuente, color_confesion)
            y_actual += (bbox[3] - bbox[1]) + 10

    if adjunto and y_adjunto_desde:
        espacio_h = ancho_max
        espacio_v = Y_LIMITE_INFERIOR_CONFESION - y_adjunto_desde
        copia = adjunto.copy()
        copia.thumbnail((espacio_h, espacio_v), Image.Resampling.LANCZOS)
        pos_x = (ANCHO_IMAGEN - copia.width)  // 2
        pos_y = y_adjunto_desde + (espacio_v  - copia.height) // 2
        img.alpha_composite(copia, (pos_x, pos_y))

    return img

# =========================
# FUNCIÓN PRINCIPAL
# =========================
def generar_imagen(nombre_plantilla, numero, confesion,
                   sede_custom=None, ruta_adjunto=None, requiere_canva=False):
    os.makedirs("Confesiones", exist_ok=True)

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
        nombre_archivo = (
            f"Confesion {numero} (Formato no disponible, configurar en Canva).png"
            if requiere_canva else f"Confesion {numero}.png"
        )
        img.save(f"Confesiones/{nombre_archivo}")

    else:
        adjunto = Image.open(ruta_adjunto).convert("RGBA")

        f_mitad,    l_mitad    = ajustar_fuente_confesion(
            confesion, FUENTE_OPENSANS_XB,
            ancho_max, Y_CONFESION, Y_MITAD - 20, SIZE_FUENTE_CONFESION
        )
        f_completo, l_completo = ajustar_fuente_confesion(
            confesion, FUENTE_OPENSANS_XB,
            ancho_max, Y_CONFESION, Y_LIMITE_INFERIOR_CONFESION, SIZE_FUENTE_CONFESION
        )

        _componer_imagen(ruta_plantilla, nombre_plantilla, numero, sede_custom,
                         l_mitad, f_mitad, color_confesion,
                         adjunto=adjunto, y_adjunto_desde=Y_MITAD
                         ).save(f"Confesiones/Confesion {numero} V1.png")

        _componer_imagen(ruta_plantilla, nombre_plantilla, numero, sede_custom,
                         l_completo, f_completo, color_confesion
                         ).save(f"Confesiones/Confesion {numero} V2 (1).png")

        _componer_imagen(ruta_plantilla, nombre_plantilla, numero, sede_custom,
                         [], f_completo, color_confesion,
                         adjunto=adjunto, y_adjunto_desde=Y_CONFESION
                         ).save(f"Confesiones/Confesion {numero} V2 (2).png")

# =========================
# CONFIGURACIÓN DE SESIÓN
# =========================
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

def las_pruebas(df):
    print("\n--- [LAS PRUEBAS: Configuración de Sesión] ---")
    print(f"   Total de filas disponibles: {len(df)}")
    print(f"   Rango de IDs: {df['id_csv'].min()} → {df['id_csv'].max()}\n")

    while True:
        try:
            fila_inicio = int(input("¿Desde qué ID deseas comenzar?: "))
            if indecision(df, fila_inicio, "comenzar desde"):
                break
        except ValueError:
            print("Ingresa un número válido.")

    while True:
        try:
            rango = int(input("\n¿Cuántas confesiones procesar?: "))
            if rango >= 1:
                break
            print("Debe ser 1 o mayor.")
        except ValueError:
            print("Ingresa un número válido.")

    ignorados = set()
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