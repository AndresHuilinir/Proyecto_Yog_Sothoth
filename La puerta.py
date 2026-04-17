# La puerta.py
import pandas as pd
import requests
import os
import glob
from Conocimiento import generar_imagen

# =========================
# RUTA BASE DEL PROYECTO
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def ruta(path):
    return os.path.join(BASE_DIR, path)

# =========================
# MAPEO SEDE → PLANTILLA
# =========================
MAPA_SEDES = {
    "🏛️ San Joaquín": "SJ",
    "🚢 Casa Central": "CC",
    "🏫 Vitacura":     "Vita",
    "🌳 Concepción":   "Conce",
    "🏖️ Viña del Mar": "Viña",
}

def resolver_plantilla(sede):
    for clave, valor in MAPA_SEDES.items():
        if clave in sede:
            return valor, None
    return "Default", sede.strip()

# =========================
# CONFIG
# =========================
os.makedirs(ruta("archivos"),    exist_ok=True)
os.makedirs(ruta("Confesiones"), exist_ok=True)

csv_files = glob.glob(ruta("*.csv"))
if not csv_files:
    raise Exception("No se encontró ningún archivo CSV en la carpeta")
CSV_FILE = csv_files[0]
destino_csv = ruta("La llave.csv")
if CSV_FILE != destino_csv:
    os.rename(CSV_FILE, destino_csv)
    CSV_FILE = destino_csv

# =========================
# PEDIR FILA DE INICIO Y RANGO
# =========================
while True:
    try:
        fila_inicio = int(input("¿Desde qué fila deseas comenzar? (1 = primera fila de datos): "))
        if fila_inicio < 1:
            print("El número debe ser 1 o mayor.")
            continue
        break
    except ValueError:
        print("Por favor ingresa un número válido.")

while True:
    try:
        rango = int(input("¿Cuántas confesiones deseas procesar?: "))
        if rango < 1:
            print("El rango debe ser 1 o mayor.")
            continue
        break
    except ValueError:
        print("Por favor ingresa un número válido.")

# =========================
# LEER CSV
# =========================
COLUMNAS = ["marca_temporal", "confesion", "imagen", "sede"]

df = pd.read_csv(
    CSV_FILE,
    encoding="utf-8",
    quotechar='"',
    skipinitialspace=True,
    engine="python",
    on_bad_lines="warn",
    names=COLUMNAS,
    header=0,
)

# Limpiar filas completamente vacías
df = df.dropna(how="all")

# Rellenar NaN con string vacío en columnas clave
df["confesion"] = df["confesion"].fillna("")
df["sede"]      = df["sede"].fillna("")
df["imagen"]    = df["imagen"].fillna("")

print(f"Total de filas leídas: {len(df)}")

df["fila_real"] = range(1, len(df) + 1)
total_filas = len(df)

df = df[df["fila_real"] >= fila_inicio].reset_index(drop=True)

if df.empty:
    print(f"No hay filas desde la posición {fila_inicio}. El CSV tiene {total_filas} filas en total.")
    exit()

# Aplicar rango — si hay menos filas disponibles, procesa las que haya
disponibles = len(df)
df = df.head(rango)
print(f"Procesando {len(df)} de {rango} pedidas ({disponibles} disponibles desde fila {fila_inicio})")

# Columnas fijas
col_confesion = "confesion"
col_sede      = "sede"
col_link      = "imagen"

# =========================
# FUNCIONES DESCARGA
# =========================
def convertir_drive(url):
    if "id=" in url:
        file_id = url.split("id=")[-1].split("&")[0].strip()
    elif "/d/" in url:
        file_id = url.split("/d/")[1].split("/")[0].strip()
    else:
        return None
    if not file_id:
        return None
    return f"https://drive.google.com/uc?export=download&id={file_id}"

def obtener_extension(response):
    content_type = response.headers.get("Content-Type", "")
    if   "image/jpeg"         in content_type: return ".jpg"
    elif "image/png"          in content_type: return ".png"
    elif "image/webp"         in content_type: return ".webp"
    elif "image/gif"          in content_type: return ".gif"
    elif "application/pdf"    in content_type: return ".pdf"
    elif "video/mp4"          in content_type: return ".mp4"
    elif "video/quicktime"    in content_type: return ".mov"
    elif "video/webm"         in content_type: return ".webm"
    elif "audio/mpeg"         in content_type: return ".mp3"
    elif "audio/wav"          in content_type: return ".wav"
    elif "audio/ogg"          in content_type: return ".ogg"
    else:
        disposition = response.headers.get("Content-Disposition", "")
        if "filename=" in disposition:
            filename = disposition.split("filename=")[-1].strip().strip('"')
            _, ext = os.path.splitext(filename)
            if ext:
                return ext
        return ""

def descargar(url, base_path):
    try:
        r = requests.get(url)
        if r.status_code == 200:
            ext  = obtener_extension(r)
            path = base_path + ext
            with open(path, "wb") as f:
                f.write(r.content)
            return path
    except Exception as e:
        print("Error descarga:", e)
    return None

# =========================
# LOOP PRINCIPAL
# =========================
generadas   = 0
descargadas = 0

for _, row in df.iterrows():
    fila_csv  = row["fila_real"]
    confesion = str(row[col_confesion]).strip()
    sede      = str(row[col_sede]).strip()

    if not confesion or confesion.lower() == "nan":
        print(f"[SKIP] fila {fila_csv} — sin confesión")
        continue

    # --- Generar imagen de confesión ---
    plantilla, sede_custom = resolver_plantilla(sede)
    try:
        generar_imagen(
            nombre_plantilla = plantilla,
            numero           = fila_csv,
            confesion        = confesion,
            sede_custom      = sede_custom
        )
        generadas += 1
    except Exception as e:
        print(f"[FAIL imagen] fila {fila_csv}: {e}")

    # --- Descargar archivo adjunto de Drive (si existe) ---
    valor = str(row[col_link]).strip()
    if "drive.google.com" in valor:
        url = convertir_drive(valor)
        if url:
            base_nombre = ruta(f"archivos/versiculo_{fila_csv}")
            resultado   = descargar(url, base_nombre)
            if resultado:
                print(f"[OK adjunto] {resultado}")
                descargadas += 1
            else:
                print(f"[FAIL adjunto] fila {fila_csv}")

print(f"\nImágenes generadas  : {generadas}")
print(f"Adjuntos descargados: {descargadas}")