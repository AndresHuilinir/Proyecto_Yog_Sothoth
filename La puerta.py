import pandas as pd
import requests
import os
import glob
from Conocimiento import generar_imagen

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
def ruta(path): return os.path.join(BASE_DIR, path)

MAPA_SEDES = {
    "🏛️ San Joaquín": "SJ",
    "🚢 Casa Central": "CC",
    "🏫 Vitacura":     "Vita",
    "🌳 Concepción":   "Conce",
    "🏖️ Viña del Mar": "Viña",
}

def resolver_plantilla(sede):
    for clave, valor in MAPA_SEDES.items():
        if clave in sede: return valor, None
    return "Default", sede.strip()

# Preparación carpetas
os.makedirs(ruta("archivos"), exist_ok=True)
os.makedirs(ruta("Confesiones"), exist_ok=True)

# Manejo CSV
csv_files = glob.glob(ruta("*.csv"))
if not csv_files: raise Exception("No hay CSV")
CSV_FILE = csv_files[0]
destino_csv = ruta("La llave.csv")
if CSV_FILE != destino_csv:
    os.rename(CSV_FILE, destino_csv)
    CSV_FILE = destino_csv

# =========================
# LECTURA DE CSV (Se mueve arriba para poder mostrar las confesiones a ignorar)
# =========================
COLUMNAS = ["marca_temporal", "confesion", "imagen", "sede"]
df = pd.read_csv(CSV_FILE, encoding="utf-8", engine="python", names=COLUMNAS, header=0)
df = df.dropna(how="all")

# Crear ID incremental
df.insert(0, "id_csv", range(1, len(df) + 1))

df["confesion"] = df["confesion"].fillna("")
df["sede"]      = df["sede"].fillna("")
df["imagen"]    = df["imagen"].fillna("")

# =========================
# FLUJO DE ENTRADA
# =========================
while True:
    try:
        fila_inicio = int(input("¿Desde qué fila deseas comenzar? (1 = primera): "))
        rango = int(input("¿Cuántas confesiones procesar?: "))
        break
    except ValueError: print("Ingresa números válidos.")

# Loop de ignorados CON CONFIRMACIÓN
ignorados = set()
print("\n--- Modo Ignorar ---")
print("Ingresa el número de fila (id) que quieres saltar. Escribe 'X' para terminar.")
while True:
    entrada = input("ID a ignorar: ").strip().upper()
    if entrada == "X": break
    try:
        id_ignorar = int(entrada)
        # Buscar en el DataFrame
        fila = df[df["id_csv"] == id_ignorar]
        
        if not fila.empty:
            texto_conf = str(fila.iloc[0]["confesion"]).strip()
            # Mostramos un fragmento si la confesión es absurdamente larga
            texto_mostrar = (texto_conf[:70] + '...') if len(texto_conf) > 70 else texto_conf
            
            confirma = input(f'\nQuieres eliminar la confesion "{texto_mostrar}" Numero "{id_ignorar}"? (S/N): ').strip().upper()
            if confirma == 'S':
                ignorados.add(id_ignorar)
                print(f"-> ID {id_ignorar} ignorado exitosamente.\n")
            else:
                print("-> Acción cancelada.\n")
        else:
            print(f"-> No se encontró el ID {id_ignorar} en el CSV.\n")
            
    except ValueError:
        continue

# Número base para el diseño
try:
    numero_base = int(input("\n¿Con qué número quieres que EMPIECE el diseño de la imagen?: "))
except ValueError:
    numero_base = 1

# Filtrar el DataFrame
df_procesar = df[df["id_csv"] >= fila_inicio].copy()
df_procesar = df_procesar[~df_procesar["id_csv"].isin(ignorados)]
df_procesar = df_procesar.head(rango)

# =========================
# FUNCIONES DE RED
# =========================
def convertir_drive(url):
    if "id=" in url: id_f = url.split("id=")[-1].split("&")[0]
    elif "/d/" in url: id_f = url.split("/d/")[1].split("/")[0]
    else: return None
    return f"https://drive.google.com/uc?export=download&id={id_f}"

def descargar(url, base_path):
    """Descarga el archivo y verifica si es imagen. Retorna ruta, 'INVALIDO' o None."""
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            content_type = r.headers.get("Content-Type", "")
            if "jpeg" in content_type:
                ext = ".jpg"
            elif "png" in content_type:
                ext = ".png"
            else:
                return "INVALIDO" # Es un PDF, Video, Doc, etc.
                
            path = base_path + ext
            with open(path, "wb") as f: f.write(r.content)
            return path
    except: pass
    return None

# =========================
# LOOP DE GENERACIÓN
# =========================
print(f"\nIniciando... Numeración visual empezará en: {numero_base}\n")

for i, (_, row) in enumerate(df_procesar.iterrows()):
    numero_visual = numero_base + i
    
    confesion = str(row["confesion"]).strip()
    sede = str(row["sede"]).strip()
    link_drive = str(row["imagen"]).strip()
    
    plantilla, sede_custom = resolver_plantilla(sede)
    
    ruta_adjunto = None
    requiere_canva = False
    
    # Procesar enlace de Drive
    if "drive.google.com" in link_drive:
        url_directa = convertir_drive(link_drive)
        if url_directa:
            resultado = descargar(url_directa, ruta(f"archivos/adjunto_{numero_visual}"))
            if resultado == "INVALIDO":
                requiere_canva = True # Activamos flag para nombre especial
            elif resultado:
                ruta_adjunto = resultado

    try:
        generar_imagen(
            nombre_plantilla = plantilla,
            numero = numero_visual,
            confesion = confesion,
            sede_custom = sede_custom,
            ruta_adjunto = ruta_adjunto,
            requiere_canva = requiere_canva
        )
        msg = f"[OK] ID CSV {row['id_csv']} -> Imagen {numero_visual}"
        if requiere_canva: msg += " (Formato incompatible -> Etiqueta Canva añadida)"
        elif ruta_adjunto: msg += " (Con Adjunto V1/V2)"
        print(msg)
    except Exception as e:
        print(f"[ERROR] En ID {row['id_csv']}: {e}")

print("\nProceso finalizado.")