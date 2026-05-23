@echo off
chcp 65001 >nul
echo ============================================
echo   Instalador - Proyecto Yog Sothoth
echo ============================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no está instalado en tu PC.
    echo.
    echo  Para instalarlo:
    echo  1. Abre tu navegador
    echo  2. Ve a https://www.python.org/downloads/
    echo  3. Descarga la version mas reciente
    echo  4. Al instalar, MARCA la casilla "Add Python to PATH"
    echo  5. Una vez instalado, vuelve a ejecutar este archivo
    echo.
    pause
    exit
)

echo [OK] Python encontrado.
echo.
echo Instalando dependencias necesarias...
echo Esto puede tardar unos minutos la primera vez.
echo.

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

echo.
echo [OK] Dependencias instaladas correctamente.
echo.
echo Creando acceso directo...
python crear_acceso.py

echo.
echo ============================================
echo   Instalacion completada con exito
echo   Ahora puedes usar: Lanzar.bat
echo ============================================
echo.
pause