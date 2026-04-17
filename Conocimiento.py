from PIL import Image, ImageDraw, ImageFont
import os

Y_NUMERO = 33
Y_CAMPUS = 93
Y_CONFESION = 210

X_NUMERO = 541
X_CAMPUS = 545

MARGEN_LATERAL = 70
ANCHO_IMAGEN = 1080

SIZE_FUENTE_NUMERO = 52 
SIZE_FUENTE_SEDE = 22
SIZE_FUENTE_CONFESION = 47

Y_LIMITE_INFERIOR_CONFESION = 1000

FUENTE_MONTSERRAT = "Caligrafía/Montserrat/static/Montserrat-Regular.ttf"
FUENTE_OPENSANS = "Caligrafía/Open_Sans/static/OpenSans-Regular.ttf"
FUENTE_OPENSANS_XB = "Caligrafía/Open_Sans/static/OpenSans-ExtraBold.ttf"

SEDES = {
    "CC": "Casa Central",
    "Conce": "Concepción",
    "SJ": "San Joaquín",
    "Viña": "Viña del Mar",
    "Vita": "Vitacura",
}

COLORES_CONFESION = {
    "CC": (77, 69, 232, 255),
    "Conce": (46, 113, 18, 255),
    "SJ": (2, 73, 159, 255),
    "Viña": (85, 85, 85, 255),
    "Vita": (37, 37, 37, 255),
    "Default": (0,0,0, 255), 
}

def dividir_texto_en_lineas(texto, fuente, ancho_max, draw):
    palabras = texto.split()
    lineas = []
    linea_actual = ""

    for palabra in palabras:
        prueba = linea_actual + (" " if linea_actual else "") + palabra
        bbox = draw.textbbox((0, 0), prueba, font=fuente)
        ancho = bbox[2] - bbox[0]

        if ancho <= ancho_max:
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
    dummy_img = Image.new("RGB", (1, 1))
    dummy_draw = ImageDraw.Draw(dummy_img)

    while size > 8:
        fuente = ImageFont.truetype(fuente_path, size)
        lineas = dividir_texto_en_lineas(texto, fuente, ancho_max, dummy_draw)

        alto_total = 0
        for linea in lineas:
            bbox = dummy_draw.textbbox((0, 0), linea, font=fuente)
            alto_total += (bbox[3] - bbox[1]) + 10

        if y_inicio + alto_total <= y_limite:
            return fuente, lineas

        size -= 1

    fuente = ImageFont.truetype(fuente_path, 8)
    lineas = dividir_texto_en_lineas(texto, fuente, ancho_max, dummy_draw)
    return fuente, lineas

def formatear_con_dos_puntos(s: str) -> str:
    grupos = []
    i = len(s)
    
    while i > 0:
        grupos.append(s[max(0, i-2):i])
        i -= 2
    
    grupos.reverse()
    return ":".join(grupos)

def generar_imagen(nombre_plantilla, numero, confesion, sede_custom=None):
    os.makedirs("Confesiones", exist_ok=True)
    ruta_salida = f"Confesiones/Confesion {numero}.png"

    ruta_plantilla = f"Plantillas/{nombre_plantilla}.png"
    if not os.path.exists(ruta_plantilla):
        ruta_plantilla = "Plantillas/Default.png"

    img = Image.open(ruta_plantilla).convert("RGBA")
    draw = ImageDraw.Draw(img)

    color_blanco = (255,255,255,255)
    color_confesion = COLORES_CONFESION.get(nombre_plantilla, COLORES_CONFESION["Default"])

    fuente_numero = ImageFont.truetype(FUENTE_MONTSERRAT, SIZE_FUENTE_NUMERO)
    fuente_campus = ImageFont.truetype(FUENTE_OPENSANS, SIZE_FUENTE_SEDE)

    ancho_max_confesion = ANCHO_IMAGEN - MARGEN_LATERAL * 2

    fuente_confesion, lineas = ajustar_fuente_confesion(
        confesion,
        FUENTE_OPENSANS_XB,
        ancho_max_confesion,
        Y_CONFESION,
        Y_LIMITE_INFERIOR_CONFESION,
        SIZE_FUENTE_CONFESION
    )

    texto_numero = formatear_con_dos_puntos(str(numero))
    bbox_n = draw.textbbox((0, 0), texto_numero, font=fuente_numero)
    ancho_n = bbox_n[2] - bbox_n[0]
    draw.text((X_NUMERO - ancho_n // 2, Y_NUMERO), texto_numero, font=fuente_numero, fill=color_blanco)

    if nombre_plantilla == "Default" and sede_custom:
        texto_campus = f"{sede_custom}"
        bbox_c = draw.textbbox((0, 0), texto_campus, font=fuente_campus)
        ancho_c = bbox_c[2] - bbox_c[0]
        draw.text((X_CAMPUS - ancho_c // 2, Y_CAMPUS), texto_campus, font=fuente_campus, fill=color_blanco)

    y_actual = Y_CONFESION

    for linea in lineas:
        bbox_l = draw.textbbox((0, 0), linea, font=fuente_confesion)
        ancho_l = bbox_l[2] - bbox_l[0]
        alto_l = bbox_l[3] - bbox_l[1]
        x_linea = (ANCHO_IMAGEN - ancho_l) // 2
        draw.text((x_linea, y_actual), linea, font=fuente_confesion, fill=color_confesion)
        y_actual += alto_l + 10

    img.save(ruta_salida)
    print(f"[OK] Imagen guardada en {ruta_salida}")