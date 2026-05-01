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

# Imagen dummy global — se crea una sola vez para medir texto
_DUMMY_IMG  = Image.new("RGB", (1, 1))
_DUMMY_DRAW = ImageDraw.Draw(_DUMMY_IMG)

# =========================
# FUNCIONES AUXILIARES
# =========================
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
        grupos.append(s[max(0, i-2):i])
        i -= 2
    grupos.reverse()
    return ":".join(grupos)

def _componer_imagen(ruta_plantilla, nombre_plantilla, numero, sede_custom,
                     lineas, fuente, color_confesion, y_confesion_limite,
                     adjunto=None, y_adjunto_desde=None):
    """
    Función interna que compone una imagen completa y la retorna.
    Centraliza toda la lógica de renderizado evitando repetición.
    """
    img  = Image.open(ruta_plantilla).convert("RGBA")
    draw = ImageDraw.Draw(img)

    fuente_numero = ImageFont.truetype(FUENTE_MONTSERRAT, SIZE_FUENTE_NUMERO)
    fuente_campus = ImageFont.truetype(FUENTE_OPENSANS,   SIZE_FUENTE_SEDE)
    color_blanco  = (255, 255, 255, 255)
    ancho_max     = ANCHO_IMAGEN - MARGEN_LATERAL * 2

    texto_numero = formatear_con_dos_puntos(numero)
    bbox_n   = _DUMMY_DRAW.textbbox((0, 0), texto_numero, font=fuente_numero)
    x_numero = X_NUMERO - (bbox_n[2] - bbox_n[0]) // 2

    # Un solo contexto Pilmoji por imagen
    with Pilmoji(img, source=GoogleEmojiSource) as pilmoji:

        # Número
        pilmoji.text((x_numero, Y_NUMERO), texto_numero, font=fuente_numero, fill=color_blanco)

        # Campus (solo Default)
        if nombre_plantilla == "Default" and sede_custom:
            bbox_c   = _DUMMY_DRAW.textbbox((0, 0), sede_custom, font=fuente_campus)
            x_campus = X_CAMPUS - (bbox_c[2] - bbox_c[0]) // 2
            pilmoji.text((x_campus, Y_CAMPUS), sede_custom, font=fuente_campus, fill=color_blanco)

        # Confesión
        y_actual = Y_CONFESION
        for linea in lineas:
            bbox = _DUMMY_DRAW.textbbox((0, 0), linea, font=fuente)
            x    = (ANCHO_IMAGEN - (bbox[2] - bbox[0])) // 2
            pilmoji.text((x, y_actual), linea, font=fuente, fill=color_confesion)
            y_actual += (bbox[3] - bbox[1]) + 10

    # Adjunto (si aplica)
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

    # --- CASO 1: Sin adjunto válido ---
    if not ruta_adjunto:
        f, l = ajustar_fuente_confesion(
            confesion, FUENTE_OPENSANS_XB,
            ancho_max, Y_CONFESION, Y_LIMITE_INFERIOR_CONFESION, SIZE_FUENTE_CONFESION
        )
        img = _componer_imagen(ruta_plantilla, nombre_plantilla, numero,
                               sede_custom, l, f, color_confesion,
                               Y_LIMITE_INFERIOR_CONFESION)
        nombre_archivo = (
            f"Confesion {numero} (Formato no disponible, configurar en Canva).png"
            if requiere_canva else f"Confesion {numero}.png"
        )
        img.save(f"Confesiones/{nombre_archivo}")

    # --- CASO 2: Con adjunto válido → V1, V2(1), V2(2) ---
    else:
        adjunto = Image.open(ruta_adjunto).convert("RGBA")

        # Calcular fuentes UNA sola vez y reutilizar
        f_mitad, l_mitad = ajustar_fuente_confesion(
            confesion, FUENTE_OPENSANS_XB,
            ancho_max, Y_CONFESION, Y_MITAD - 20, SIZE_FUENTE_CONFESION
        )
        f_completo, l_completo = ajustar_fuente_confesion(
            confesion, FUENTE_OPENSANS_XB,
            ancho_max, Y_CONFESION, Y_LIMITE_INFERIOR_CONFESION, SIZE_FUENTE_CONFESION
        )

        # V1: texto arriba + imagen abajo
        img_v1 = _componer_imagen(ruta_plantilla, nombre_plantilla, numero,
                                  sede_custom, l_mitad, f_mitad, color_confesion,
                                  Y_MITAD - 20, adjunto=adjunto, y_adjunto_desde=Y_MITAD)
        img_v1.save(f"Confesiones/Confesion {numero} V1.png")

        # V2(1): solo confesión completa
        img_v2_1 = _componer_imagen(ruta_plantilla, nombre_plantilla, numero,
                                    sede_custom, l_completo, f_completo, color_confesion,
                                    Y_LIMITE_INFERIOR_CONFESION)
        img_v2_1.save(f"Confesiones/Confesion {numero} V2 (1).png")

        # V2(2): solo imagen centrada (sin texto de confesión)
        img_v2_2 = _componer_imagen(ruta_plantilla, nombre_plantilla, numero,
                                    sede_custom, [], f_completo, color_confesion,
                                    Y_LIMITE_INFERIOR_CONFESION,
                                    adjunto=adjunto, y_adjunto_desde=Y_CONFESION)
        img_v2_2.save(f"Confesiones/Confesion {numero} V2 (2).png")

# =========================
# CONFIGURACIÓN DE SESIÓN
# =========================
def indecision(df, id_target, accion_texto):
    fila = df[df["id_csv"] == id_target - 2]
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
    print(f"   Rango de IDs: {df['id_csv'].min() + 2} → {df['id_csv'].max() + 2}\n")

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

    return fila_inicio - 2, rango, ignorados, numero_base
