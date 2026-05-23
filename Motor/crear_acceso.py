import sys
import os
import stat

MOTOR_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR  = os.path.dirname(MOTOR_DIR)
ritual    = os.path.join(MOTOR_DIR, "Ritual.py")
python    = sys.executable

if sys.platform == "win32":
    ruta_acceso = os.path.join(ROOT_DIR, "Lanzar.bat")
    with open(ruta_acceso, "w") as f:
        f.write(
            f'@echo off\n'
            f'cd /d "{MOTOR_DIR}"\n'
            f'"{python}" "{ritual}"\n'
            f'pause\n'
        )
    print(f"[OK] Creado: {ruta_acceso}")
    print("Haz doble clic en Lanzar.bat para iniciar.")

else:
    ruta_acceso = os.path.join(ROOT_DIR, "Lanzar.sh")
    with open(ruta_acceso, "w") as f:
        f.write(
            f'#!/bin/bash\n'
            f'cd "{MOTOR_DIR}"\n'
            f'"{python}" "{ritual}"\n'
        )
    os.chmod(ruta_acceso, os.stat(ruta_acceso).st_mode | stat.S_IEXEC)
    print(f"[OK] Creado: {ruta_acceso}")
    print("Haz doble clic en Lanzar.sh para iniciar.")