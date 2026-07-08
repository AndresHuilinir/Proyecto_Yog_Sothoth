@echo off
chcp 65001 >nul
echo ============================================
echo   Instalador - Proyecto Yog Sothoth
echo ============================================
echo.

:: ---- PYTHON ----
python --version >nul 2>&1
if errorlevel 1 (
    echo [!] Python no encontrado. Instalando automaticamente...
    winget install --id Python.Python.3 --source winget --accept-package-agreements --accept-source-agreements --silent
    if errorlevel 1 (
        echo.
        echo [ERROR] No se pudo instalar Python automaticamente.
        echo Por favor instalalo manualmente desde:
        echo https://www.python.org/downloads/
        echo IMPORTANTE: marca "Add Python to PATH" durante la instalacion.
        echo.
        pause
        exit
    )
    echo [OK] Python instalado.
    echo.
    echo Reiniciando variables de entorno...
    call refreshenv >nul 2>&1
) else (
    echo [OK] Python ya estaba instalado.
)

:: ---- GIT ----
git --version >nul 2>&1
if errorlevel 1 (
    echo [!] Git no encontrado. Instalando automaticamente...
    winget install --id Git.Git --source winget --accept-package-agreements --accept-source-agreements --silent
    if errorlevel 1 (
        echo.
        echo [ERROR] No se pudo instalar Git automaticamente.
        echo Por favor instalalo manualmente desde:
        echo https://git-scm.com/downloads
        echo.
        pause
        exit
    )
    echo [OK] Git instalado.
    echo.
    echo Actualizando PATH con Git...
    set "PATH=%PATH%;C:\Program Files\Git\cmd"
) else (
    echo [OK] Git ya estaba instalado.
)

:: ---- DEPENDENCIAS ----
echo.
echo Instalando dependencias de Python...
cd /d "%~dp0Motor"

python -m pip install --upgrade pip --quiet
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo [ERROR] Algo salio mal instalando las dependencias.
    echo Intenta ejecutar este archivo como Administrador:
    echo  - Click derecho en INSTALAR_WINDOWS.bat
    echo  - "Ejecutar como administrador"
    echo.
    pause
    exit
)

:: ---- ACCESO DIRECTO ----
echo.
echo [OK] Dependencias instaladas.
echo.
echo Creando acceso directo...
python crear_acceso.py

echo.
echo ============================================
echo   Instalacion completada con exito.
echo   Usa Lanzar.bat para iniciar el programa.
echo ============================================
echo.
pause