import pandas as pd
import requests
import os
import glob

# Necesitamos definir esto aquí para que las rutas funcionen
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
        if clave in sede: return valor, None
    return "Default", sede.strip()

def cognitotrofia():
    """Gestiona, fusiona y nutre el CSV principal."""
    csv_files = glob.glob(ruta("*.csv"))
    if not csv_files:
        raise Exception("No se encontró ningún archivo CSV.")

    maestra_path = ruta("La llave maestra.csv")
    COLUMNAS = ["marca_temporal", "confesion", "imagen", "sede"]

    if len(csv_files) == 1:
        archivo = csv_files[0]
        if archivo != maestra_path:
            os.rename(archivo, maestra_path)
        df = pd.read_csv(maestra_path, encoding="utf-8", engine="python", names=COLUMNAS, header=0)
    else:
        if maestra_path in csv_files:
            nuevo_csv = [f for f in csv_files if f != maestra_path][0]
            df_maestra = pd.read_csv(maestra_path, encoding="utf-8", engine="python", names=COLUMNAS, header=0)
            df_nuevo = pd.read_csv(nuevo_csv, encoding="utf-8", engine="python", names=COLUMNAS, header=0)
            df = pd.concat([df_maestra, df_nuevo], ignore_index=True)
            df = df.drop_duplicates(subset=["marca_temporal", "confesion"], keep="first")
            df.to_csv(maestra_path, index=False, header=True, encoding="utf-8")
            os.remove(nuevo_csv)
        else:
            os.rename(csv_files[0], maestra_path)
            df = pd.read_csv(maestra_path, encoding="utf-8", engine="python", names=COLUMNAS, header=0)

    df = df.dropna(how="all").reset_index(drop=True)
    df["confesion"] = df["confesion"].fillna("")
    df["sede"]      = df["sede"].fillna("")
    df["imagen"]    = df["imagen"].fillna("")

    if "id_csv" in df.columns:
        df = df.drop(columns=["id_csv"])
    df.insert(0, "id_csv", range(1, len(df) + 1))
    
    return df

def convertir_drive(url):
    if "id=" in url: id_f = url.split("id=")[-1].split("&")[0]
    elif "/d/" in url: id_f = url.split("/d/")[1].split("/")[0]
    else: return None
    return f"https://drive.google.com/uc?export=download&id={id_f}"

def descargar(url, base_path):
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            content_type = r.headers.get("Content-Type", "")
            if "jpeg" in content_type: ext = ".jpg"
            elif "png" in content_type: ext = ".png"
            else: return "INVALIDO"
                
            path = base_path + ext
            with open(path, "wb") as f: f.write(r.content)
            return path
    except: pass
    return None