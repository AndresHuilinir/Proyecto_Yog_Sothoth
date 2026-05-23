#!/bin/bash

echo "============================================"
echo "  Instalador - Proyecto Yog Sothoth"
echo "============================================"
echo ""

if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python no está instalado."
    echo ""
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo " Ve a https://www.python.org/downloads/ y descarga la versión para Mac."
    else
        echo "   sudo apt install python3 python3-pip   (Ubuntu/Debian)"
        echo "   sudo dnf install python3               (Fedora)"
    fi
    echo ""
    read -p "Presiona Enter para cerrar..."
    exit 1
fi

echo "[OK] Python encontrado."
echo ""
echo "Instalando dependencias..."
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/Motor"

python3 -m pip install --upgrade pip --quiet
python3 -m pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo ""
    echo "[ERROR] Algo salió mal. Intenta:"
    echo "  pip3 install -r Motor/requirements.txt"
    echo ""
    read -p "Presiona Enter para cerrar..."
    exit 1
fi

echo ""
echo "[OK] Dependencias instaladas."
echo ""
echo "Creando acceso directo..."
python3 crear_acceso.py

if [ -f "../Lanzar.sh" ]; then
    chmod +x "../Lanzar.sh"
fi

echo ""
echo "============================================"
echo "  Instalacion completada"
echo "  Ahora puedes usar: Lanzar.sh"
echo "============================================"
echo ""
read -p "Presiona Enter para cerrar..."