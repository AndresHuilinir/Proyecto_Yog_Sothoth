# crear_acceso.py
import sys
import os
import stat

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ritual   = os.path.join(BASE_DIR, "Ritual.py")
python   = sys.executable

if sys.platform == "win32":
    ruta_acceso = os.path.join(BASE_DIR, "Lanzar.bat")
    with open(ruta_acceso, "w") as f:
        f.write(f'@echo off\n"{python}" "{ritual}"\npause\n')
    print(f"[OK] Creado: {ruta_acceso}")
    print("Haz doble clic en Lanzar.bat para iniciar el programa.")

else:
    ruta_acceso = os.path.join(BASE_DIR, "Lanzar.sh")
    with open(ruta_acceso, "w") as f:
        f.write(f'#!/bin/bash\ncd "{BASE_DIR}"\n"{python}" "{ritual}"\n')
    os.chmod(ruta_acceso, os.stat(ruta_acceso).st_mode | stat.S_IEXEC)
    print(f"[OK] Creado: {ruta_acceso}")
    print("Haz doble clic en Lanzar.sh para iniciar el programa.")