@echo off
chcp 65001 >nul
echo ============================================
echo   Instalador - Proyecto Yog Sothoth
echo ============================================
echo.

:: ---- PYTHON ----
python --version >nul 2>&1
if errorlevel 1 (
    echo [!] Python no encontrado. Descargando instalador...
    PowerShell -NoProfile -ExecutionPolicy Bypass -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.12.4/python-3.12.4-amd64.exe' -OutFile '%TEMP%\python_installer.exe'"
    if errorlevel 1 (
        echo.
        echo [ERROR] No se pudo descargar Python.
        echo Revisa tu conexion a internet e intenta de nuevo.
        echo O instalalo manualmente desde https://www.python.org/downloads/
        echo IMPORTANTE: marca "Add Python to PATH" durante la instalacion.
        echo.
        pause
        exit
    )
    echo [OK] Instalando Python...
    "%TEMP%\python_installer.exe" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
    if errorlevel 1 (
        echo.
        echo [ERROR] Fallo la instalacion de Python.
        echo Intenta ejecutar este archivo como Administrador.
        echo.
        pause
        exit
    )
    del "%TEMP%\python_installer.exe"
    echo [OK] Python instalado correctamente.
    echo.
    :: Recargar PATH para que Python sea visible en esta sesion
    set "PATH=%PATH%;C:\Program Files\Python312;C:\Program Files\Python312\Scripts"
    set "PATH=%PATH%;%LOCALAPPDATA%\Programs\Python\Python312;%LOCALAPPDATA%\Programs\Python\Python312\Scripts"
) else (
    echo [OK] Python ya estaba instalado.
)

:: Verificar que Python responde
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ERROR] Python se instalo pero no responde.
    echo Cierra este instalador, REINICIA el PC e intentalo de nuevo.
    echo.
    pause
    exit
)



:: ---- DEPENDENCIAS ----
echo.
echo Instalando dependencias de Python...
cd /d "%~dp0Motor"

python -m pip install --upgrade pip --quiet
if errorlevel 1 (
    echo [WARN] No se pudo actualizar pip, continuando igual...
)

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
if errorlevel 1 (
    echo [WARN] No se pudo crear el acceso directo automaticamente.
    echo Puedes ejecutar el programa con: python Motor\Ritual.py
)

echo.
echo ============================================
echo   Instalacion completada con exito.
echo.
echo   IMPORTANTE: Si es la primera vez que
echo   instalas Python o Git, REINICIA el PC
echo   antes de usar Yoguito.bat
echo ============================================
echo.
pause