import sys
import os
import stat
import subprocess

MOTOR_DIR  = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR   = os.path.dirname(MOTOR_DIR)
ritual     = os.path.join(MOTOR_DIR, "Ritual.py")
python     = sys.executable
REPO_URL   = "https://github.com/TU_USUARIO/TU_REPO.git"

# Forzar HTTPS y deshabilitar autenticación interactiva
subprocess.run(["git", "remote", "set-url", "origin", REPO_URL],
               cwd=ROOT_DIR, capture_output=True)
subprocess.run(["git", "config", "core.askPass", ""],
               cwd=ROOT_DIR, capture_output=True)
subprocess.run(["git", "config", "--global", "credential.helper", ""],
               cwd=ROOT_DIR, capture_output=True)
subprocess.run(["git", "config", "--global", "GIT_TERMINAL_PROMPT", "0"],
               cwd=ROOT_DIR, capture_output=True)
subprocess.run(["git", "config", "--global", "core.askPass", "echo"],
               cwd=ROOT_DIR, capture_output=True)

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