# Portales.py
import pandas as pd
import requests
import os
import glob

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def ruta(path):
    return os.path.join(BASE_DIR, path)

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

def Plegarias():
    SHEET_ID = "1Ep3ehmPODFXPms3gwp_JUHNF0YaSn7f7-sJcREWF1pM"
    GID      = "1504952135"
    URL      = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"
    destino  = ruta("hoja_nueva.csv")

    print("Descargando hoja de cálculo...")
    try:
        r = requests.get(URL, timeout=15)
        if r.status_code == 200:
            with open(destino, "wb") as f:
                f.write(r.content)
            print(f"[OK] CSV descargado → {destino}")
        else:
            print(f"[WARN] No se pudo descargar el CSV (status {r.status_code}). Usando el que ya existe.")
    except Exception as e:
        print(f"[WARN] Error de red: {e}. Usando el que ya existe.")

def cognitotrofia():
    COLUMNAS     = ["marca_temporal", "confesion", "imagen", "sede"]
    maestra_path = ruta("La llave maestra.csv")
    csv_files    = glob.glob(ruta("*.csv"))

    if not csv_files:
        raise Exception("No se encontró ningún archivo CSV.")

    def leer_csv(path):
        return pd.read_csv(
            path,
            encoding="utf-8",
            engine="python",
            names=COLUMNAS,
            header=0,
            on_bad_lines="warn",
            dtype=str,
        )

    # Separar maestra de nuevos
    nuevos = [f for f in csv_files if f != maestra_path]

    if os.path.exists(maestra_path):
        df = leer_csv(maestra_path)
        # Fusionar con nuevos si los hay
        for nuevo in nuevos:
            df_nuevo = leer_csv(nuevo)
            df = pd.concat([df, df_nuevo], ignore_index=True)
            df = df.drop_duplicates(subset=["marca_temporal", "confesion"], keep="first")
            os.remove(nuevo)
        df.to_csv(maestra_path, index=False, header=True, encoding="utf-8")
    else:
        # No existe maestra — renombrar el primero y fusionar el resto
        os.rename(csv_files[0], maestra_path)
        df = leer_csv(maestra_path)
        for nuevo in nuevos[1:]:
            df_nuevo = leer_csv(nuevo)
            df = pd.concat([df, df_nuevo], ignore_index=True)
            df = df.drop_duplicates(subset=["marca_temporal", "confesion"], keep="first")
            os.remove(nuevo)
        df.to_csv(maestra_path, index=False, header=True, encoding="utf-8")

    # Limpiar
    df = df.dropna(subset=["confesion", "sede"], how="all")
    df[["confesion", "sede", "imagen"]] = df[["confesion", "sede", "imagen"]].fillna("")

    # ID limpio basado en posición real
    df = df.reset_index(drop=True)
    df.insert(0, "id_csv", range(1, len(df) + 1))

    return df

def convertir_drive(url):
    if "id=" in url:
        id_f = url.split("id=")[-1].split("&")[0]
    elif "/d/" in url:
        id_f = url.split("/d/")[1].split("/")[0]
    else:
        return None
    return f"https://drive.google.com/uc?export=download&id={id_f}"

def descargar(url, base_path):
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            content_type = r.headers.get("Content-Type", "")
            if   "jpeg" in content_type: ext = ".jpg"
            elif "png"  in content_type: ext = ".png"
            else: return "INVALIDO"
            path = base_path + ext
            with open(path, "wb") as f:
                f.write(r.content)
            return path
    except Exception as e:
        print(f"Error descarga: {e}")
    return None

def eterno_retorno():
    carpetas = [ruta("Confesiones"), ruta("archivos")]
    total    = 0
    for carpeta in carpetas:
        if not os.path.exists(carpeta):
            continue
        for archivo in os.listdir(carpeta):
            ruta_archivo = os.path.join(carpeta, archivo)
            if os.path.isfile(ruta_archivo):
                os.remove(ruta_archivo)
                total += 1
    print(f"[OK] {total} archivos eliminados.")
                os.remove(ruta_archivo)
                total += 1
    print(f"[OK] {total} archivos eliminados.")
