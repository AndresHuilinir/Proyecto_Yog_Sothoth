import Conocimiento
import os

# =========================
# AJUSTE DEL CENSURADOR
# =========================
desfase_del_censurador = 0
Conocimiento.DESFASE_CENSURADOR = desfase_del_censurador

from Orden_universal import CARPETA_CONFESIONES
os.makedirs(CARPETA_CONFESIONES, exist_ok=True)

# =========================
# PARÁMETROS DE PRUEBA
# =========================
PLANTILLA   = "SJ"
SEDE_CUSTOM = None

PALABRAS_PRUEBA = [50, 100, 150, 200, 250, 275, 300, 350, 400, 450, 500]

RELLENO = (
    "este es un texto de prueba para ver cuántas palabras caben en una imagen "
)

for n in PALABRAS_PRUEBA:
    palabras_necesarias = n
    texto = ""
    while len(texto.split()) < palabras_necesarias:
        texto += RELLENO
    texto = " ".join(texto.split()[:palabras_necesarias])

    numero = 8000 + n

    Conocimiento.generar_imagen(
        nombre_plantilla = PLANTILLA,
        numero           = numero,
        confesion        = texto,
        sede_custom      = SEDE_CUSTOM,
    )
    print(f"[OK] {n} palabras → Confesion {numero}.png")

print("\nRevisa Confesiones/ y busca desde qué imagen el texto se vuelve muy pequeño o se corta.")
print("Ese número de palabras es tu límite por imagen.")