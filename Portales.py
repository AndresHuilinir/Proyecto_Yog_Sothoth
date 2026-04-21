#Portales.py
import pandas as pd
import requests
import os
import glob

def Plegarias():
    SHEET_ID = "1Ep3ehmPODFXPms3gwp_JUHNF0YaSn7f7-sJcREWF1pM"
    GID      = "1504952135"
    URL      = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"
    
    destino  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hoja_nueva.csv")
    
    print("Descargando hoja de cálculo...")
    r = requests.get(URL, timeout=15)
    
    if r.status_code == 200:
        with open(destino, "wb") as f:
            f.write(r.content)
        print(f"[OK] CSV descargado → {destino}")
    else:
        print(f"[WARN] No se pudo descargar el CSV (status {r.status_code}). Usando el que ya existe.")


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

def cognitotrofia():
    csv_files = glob.glob(ruta("*.csv"))
    if not csv_files:
        raise Exception("No se encontró ningún archivo CSV.")

    maestra_path = ruta("La llave maestra.csv")
    COLUMNAS = ["marca_temporal", "confesion", "imagen", "sede"]

    def leer_csv(path):
        df = pd.read_csv(
            path,
            encoding="utf-8",
            engine="python",
            names=COLUMNAS,
            header=0,          # salta la primera fila (encabezado)
            on_bad_lines="warn",
            dtype=str,
        )
        # ⚠️ Asignar id_csv ANTES de cualquier limpieza,
        # basado en la línea real del archivo (fila 1 = encabezado → datos empiezan en 2)
        df.insert(0, "id_csv", range(3, len(df) + 3))
        return df

    if len(csv_files) == 1:
        archivo = csv_files[0]
        if archivo != maestra_path:
            os.rename(archivo, maestra_path)
        df = leer_csv(maestra_path)

    else:
        if maestra_path in csv_files:
            nuevo_csv = [f for f in csv_files if f != maestra_path][0]
            df_maestra = leer_csv(maestra_path)
            df_nuevo   = leer_csv(nuevo_csv)
            df = pd.concat([df_maestra, df_nuevo], ignore_index=True)
            df = df.drop_duplicates(subset=["marca_temporal", "confesion"], keep="first")
            # Reasignar IDs en orden tras fusión
            df["id_csv"] = range(1, len(df) + 1)
            df.to_csv(maestra_path, index=False, header=True, encoding="utf-8")
            os.remove(nuevo_csv)
        else:
            os.rename(csv_files[0], maestra_path)
            df = leer_csv(maestra_path)

    # Limpiar filas completamente vacías DESPUÉS de asignar IDs
    df = df.dropna(subset=["confesion", "sede"], how="all")
    df["confesion"] = df["confesion"].fillna("")
    df["sede"]      = df["sede"].fillna("")
    df["imagen"]    = df["imagen"].fillna("")

    return df.reset_index(drop=True)

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
    total = 0

    for carpeta in carpetas:
        if not os.path.exists(carpeta):
            continue
        for archivo in os.listdir(carpeta):
            ruta_archivo = os.path.join(carpeta, archivo)
            if os.path.isfile(ruta_archivo):
                os.remove(ruta_archivo)
                total += 1

    print(f"[OK] {total} archivos eliminados. Las carpetas siguen intactas.")