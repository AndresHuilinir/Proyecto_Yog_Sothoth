# Conocimiento.py
from PIL import Image, ImageDraw, ImageFont
from pilmoji import Pilmoji
from pilmoji.source import GoogleEmojiSource
import os

# =========================
# CONSTANTES DE DISEÑO
# =========================
Y_NUMERO    = 33
Y_CAMPUS    = 93
Y_CONFESION = 210
X_NUMERO    = 541
X_CAMPUS    = 545
MARGEN_LATERAL  = 70
ANCHO_IMAGEN    = 1080
ALTO_IMAGEN     = 1080
SIZE_FUENTE_NUMERO    = 52
SIZE_FUENTE_SEDE      = 22
SIZE_FUENTE_CONFESION = 47
Y_LIMITE_INFERIOR_CONFESION = 1000
Y_MITAD = 540

FUENTE_MONTSERRAT  = "Caligrafía/Montserrat/static/Montserrat-Regular.ttf"
FUENTE_OPENSANS    = "Caligrafía/Open_Sans/static/OpenSans-Regular.ttf"
FUENTE_OPENSANS_XB = "Caligrafía/Open_Sans/static/OpenSans-ExtraBold.ttf"

COLORES_CONFESION = {
    "CC":      (77,  69,  232, 255),
    "Conce":   (46,  113, 18,  255),
    "SJ":      (2,   73,  159, 255),
    "Viña":    (85,  85,  85,  255),
    "Vita":    (37,  37,  37,  255),
    "Default": (0,   0,   0,   255),
}

# =========================
# FUNCIONES AUXILIARES
# =========================
def dividir_texto_en_lineas(texto, fuente, ancho_max, draw):
    palabras = texto.split()
    lineas, linea_actual = [], ""
    for palabra in palabras:
        prueba = linea_actual + (" " if linea_actual else "") + palabra
        bbox   = draw.textbbox((0, 0), prueba, font=fuente)
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
    size = size_default
    dummy_img  = Image.new("RGB", (1, 1))
    dummy_draw = ImageDraw.Draw(dummy_img)
    while size > 8:
        fuente = ImageFont.truetype(fuente_path, size)
        lineas = dividir_texto_en_lineas(texto, fuente, ancho_max, dummy_draw)
        alto_total = sum(
            (dummy_draw.textbbox((0, 0), l, font=fuente)[3]
             - dummy_draw.textbbox((0, 0), l, font=fuente)[1] + 10)
            for l in lineas
        )
        if y_inicio + alto_total <= y_limite:
            return fuente, lineas
        size -= 1
    fuente = ImageFont.truetype(fuente_path, 8)
    return fuente, dividir_texto_en_lineas(texto, fuente, ancho_max, dummy_draw)

def formatear_con_dos_puntos(s: str) -> str:
    s      = str(s).zfill(2)
    grupos = [s[max(0, i - 2):i] for i in range(len(s), 0, -2)]
    grupos.reverse()
    return ":".join(grupos)

def dibujar_base(img, draw, nombre_plantilla, numero, sede_custom):
    color_blanco  = (255, 255, 255, 255)
    fuente_numero = ImageFont.truetype(FUENTE_MONTSERRAT, SIZE_FUENTE_NUMERO)
    fuente_campus = ImageFont.truetype(FUENTE_OPENSANS,   SIZE_FUENTE_SEDE)

    texto_numero = formatear_con_dos_puntos(numero)
    bbox_n   = draw.textbbox((0, 0), texto_numero, font=fuente_numero)
    x_numero = X_NUMERO - (bbox_n[2] - bbox_n[0]) // 2

    with Pilmoji(img, source=GoogleEmojiSource) as pilmoji:
        pilmoji.text((x_numero, Y_NUMERO), texto_numero, font=fuente_numero, fill=color_blanco)

        if nombre_plantilla == "Default" and sede_custom:
            bbox_c   = draw.textbbox((0, 0), sede_custom, font=fuente_campus)
            x_campus = X_CAMPUS - (bbox_c[2] - bbox_c[0]) // 2
            pilmoji.text((x_campus, Y_CAMPUS), sede_custom, font=fuente_campus, fill=color_blanco)

def escribir_texto(img, draw, lineas, fuente, color, y_inicial):
    y_actual = y_inicial
    with Pilmoji(img, source=GoogleEmojiSource) as pilmoji:
        for linea in lineas:
            bbox = draw.textbbox((0, 0), linea, font=fuente)
            x    = (ANCHO_IMAGEN - (bbox[2] - bbox[0])) // 2
            pilmoji.text((x, y_actual), linea, font=fuente, fill=color)
            y_actual += (bbox[3] - bbox[1]) + 10

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

    # --- CASO 1: Sin adjunto válido ---
    if not ruta_adjunto:
        img  = Image.open(ruta_plantilla).convert("RGBA")
        draw = ImageDraw.Draw(img)
        dibujar_base(img, draw, nombre_plantilla, numero, sede_custom)
        f, l = ajustar_fuente_confesion(
            confesion, FUENTE_OPENSANS_XB,
            ancho_max, Y_CONFESION, Y_LIMITE_INFERIOR_CONFESION, SIZE_FUENTE_CONFESION
        )
        escribir_texto(img, draw, l, f, color_confesion, Y_CONFESION)
        nombre_archivo = (
            f"Confesion {numero} (Formato no disponible, configurar en Canva).png"
            if requiere_canva else
            f"Confesion {numero}.png"
        )
        img.save(f"Confesiones/{nombre_archivo}")

    # --- CASO 2: Con adjunto válido → V1, V2(1), V2(2) ---
    else:
        # V1: texto arriba, imagen abajo
        img_v1  = Image.open(ruta_plantilla).convert("RGBA")
        draw_v1 = ImageDraw.Draw(img_v1)
        dibujar_base(img_v1, draw_v1, nombre_plantilla, numero, sede_custom)
        f_v1, l_v1 = ajustar_fuente_confesion(
            confesion, FUENTE_OPENSANS_XB,
            ancho_max, Y_CONFESION, Y_MITAD - 20, SIZE_FUENTE_CONFESION
        )
        escribir_texto(img_v1, draw_v1, l_v1, f_v1, color_confesion, Y_CONFESION)
        adjunto = Image.open(ruta_adjunto).convert("RGBA")
        espacio_h = ancho_max
        espacio_v = Y_LIMITE_INFERIOR_CONFESION - Y_MITAD
        adjunto.thumbnail((espacio_h, espacio_v), Image.Resampling.LANCZOS)
        pos_x = (ANCHO_IMAGEN - adjunto.width)  // 2
        pos_y = Y_MITAD + (espacio_v - adjunto.height) // 2
        img_v1.alpha_composite(adjunto, (pos_x, pos_y))
        img_v1.save(f"Confesiones/Confesion {numero} V1.png")

        # V2(1): solo confesión
        img_v2_1  = Image.open(ruta_plantilla).convert("RGBA")
        draw_v2_1 = ImageDraw.Draw(img_v2_1)
        dibujar_base(img_v2_1, draw_v2_1, nombre_plantilla, numero, sede_custom)
        f_v2, l_v2 = ajustar_fuente_confesion(
            confesion, FUENTE_OPENSANS_XB,
            ancho_max, Y_CONFESION, Y_LIMITE_INFERIOR_CONFESION, SIZE_FUENTE_CONFESION
        )
        escribir_texto(img_v2_1, draw_v2_1, l_v2, f_v2, color_confesion, Y_CONFESION)
        img_v2_1.save(f"Confesiones/Confesion {numero} V2 (1).png")

        # V2(2): solo imagen centrada
        img_v2_2  = Image.open(ruta_plantilla).convert("RGBA")
        draw_v2_2 = ImageDraw.Draw(img_v2_2)
        dibujar_base(img_v2_2, draw_v2_2, nombre_plantilla, numero, sede_custom)
        adjunto_v2 = Image.open(ruta_adjunto).convert("RGBA")
        adjunto_v2.thumbnail(
            (ancho_max, Y_LIMITE_INFERIOR_CONFESION - Y_CONFESION),
            Image.Resampling.LANCZOS
        )
        pos_x2 = (ANCHO_IMAGEN - adjunto_v2.width) // 2
        pos_y2 = Y_CONFESION + ((Y_LIMITE_INFERIOR_CONFESION - Y_CONFESION) - adjunto_v2.height) // 2
        img_v2_2.alpha_composite(adjunto_v2, (pos_x2, pos_y2))
        img_v2_2.save(f"Confesiones/Confesion {numero} V2 (2).png")

# =========================
# CONFIGURACIÓN DE SESIÓN
# =========================
def indecision(df, id_target, accion_texto):
    fila = df[df["id_csv"] == id_target-2]
    if not fila.empty:
        texto   = str(fila.iloc[0]["confesion"]).strip()
        resumen = (texto[:70] + "...") if len(texto) > 70 else texto
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

    # 1. Fila de inicio
    while True:
        try:
            fila_inicio = int(input("¿Desde qué ID deseas comenzar?: "))
            if indecision(df, fila_inicio, "comenzar desde"):
                break
        except ValueError:
            print("Ingresa un número válido.")

    # 2. Rango
    while True:
        try:
            rango = int(input("\n¿Cuántas confesiones procesar?: "))
            if rango >= 1:
                break
            print("Debe ser 1 o mayor.")
        except ValueError:
            print("Ingresa un número válido.")

    # 3. IDs a ignorar
    ignorados = set()
    print("\n--- Modo Ignorar ---")
    while True:
        entrada = input("ID a ignorar (X para terminar): ").strip().upper()
        if entrada == "X":
            break
        try:
            id_ignorar = int(entrada)
            if indecision(df, id_ignorar, "ignorar"):
                ignorados.add(id_ignorar - 2)
                print(f"-> ID {id_ignorar} agregado a ignorados.\n")
            else:
                print("-> Cancelado.\n")
        except ValueError:
            print("Ingresa un número válido o X para terminar.")

    # 4. Número base visual
    while True:
        try:
            numero_base = int(input("\n¿Con qué número visual quieres empezar?: "))
            break
        except ValueError:
            numero_base = 1
            break

    return fila_inicio, rango, ignorados, numero_base