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

def _detectar_extension(content_type, url):
    MAPA = {
        "video/mp4":       "MP4",
        "video/quicktime": "MOV",
        "video/webm":      "WEBM",
        "video/avi":       "AVI",
        "audio/mpeg":      "MP3",
        "audio/wav":       "WAV",
        "audio/ogg":       "OGG",
        "application/pdf": "PDF",
        "image/webp":      "WEBP",
        "image/bmp":       "BMP",
    }
    for mime, nombre in MAPA.items():
        if mime in content_type:
            return nombre
    ext = os.path.splitext(url.split("?")[0])[-1].upper().replace(".", "")
    return ext if ext else "desconocido"

def descargar(url, base_path):
    try:
        r = requests.get(url, timeout=60, stream=True)
        if r.status_code == 200:
            content_type = r.headers.get("Content-Type", "")
            if   "jpeg" in content_type or "jpg" in content_type: ext = ".jpg"
            elif "png"  in content_type:                           ext = ".png"
            elif "gif"  in content_type:                           ext = ".gif"
            elif "video/mp4"    in content_type:                   ext = ".mp4"
            elif "quicktime"    in content_type:                   ext = ".mov"
            elif "webm"         in content_type:                   ext = ".webm"
            elif "avi"          in content_type:                   ext = ".avi"
            else:
                return f"FORMATO:{_detectar_extension(content_type, url)}"
            path = base_path + ext
            with open(path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            return path
    except Exception as e:
        print(f"Error descarga: {e}")
    return None