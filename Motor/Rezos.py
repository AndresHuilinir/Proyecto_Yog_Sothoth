import requests
import os
from Orden_universal import ruta

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
            print(f"[WARN] Status {r.status_code}. Usando el que ya existe.")
    except Exception as e:
        print(f"[WARN] Error de red: {e}. Usando el que ya existe.")

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