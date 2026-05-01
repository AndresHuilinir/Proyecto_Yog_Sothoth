import os
from Orden_universal import ruta

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