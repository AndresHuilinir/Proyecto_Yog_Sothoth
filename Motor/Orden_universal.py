import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OFFSET_ID = 2

def ruta(path):
    return os.path.join(BASE_DIR, path)

CARPETA_CONFESIONES = os.path.join(os.path.dirname(BASE_DIR), "Confesiones")

Y_NUMERO    = 33
Y_CAMPUS    = 93
Y_CONFESION = 210
X_NUMERO    = 541
X_CAMPUS    = 545
MARGEN_LATERAL              = 70
ANCHO_IMAGEN                = 1080
ALTO_IMAGEN                 = 1080
SIZE_FUENTE_NUMERO          = 52
SIZE_FUENTE_SEDE            = 22
SIZE_FUENTE_CONFESION       = 47
Y_LIMITE_INFERIOR_CONFESION = 1000
Y_MITAD                     = 540

FUENTE_MONTSERRAT  = "Caligrafía/Montserrat/static/Montserrat-Regular.ttf"
FUENTE_OPENSANS    = "Caligrafía/Open_Sans/static/OpenSans-Regular.ttf"
FUENTE_OPENSANS_XB = "Caligrafía/Open_Sans/static/OpenSans-ExtraBold.ttf"

COLOR_BLANCO = (255, 255, 255, 255)

COLORES_CONFESION = {
    "CC":      (77,  69,  232, 255),
    "Conce":   (46,  113, 18,  255),
    "SJ":      (2,   73,  159, 255),
    "Viña":    (85,  85,  85,  255),
    "Vita":    (37,  37,  37,  255),
    "Default": (0,   0,   0,   255),
}

MAPA_SEDES = {
    "🏛️ San Joaquín": "SJ",
    "🚢 Casa Central": "CC",
    "🏫 Vitacura":     "Vita",
    "🌳 Concepción":   "Conce",
    "🏖️ Viña del Mar": "Viña",
}