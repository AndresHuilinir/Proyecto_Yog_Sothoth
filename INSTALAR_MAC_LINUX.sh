#!/bin/bash

echo "============================================"
echo "  Instalador - Proyecto Yog Sothoth"
echo "============================================"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ---- HOMEBREW (solo Mac) ----
if [[ "$OSTYPE" == "darwin"* ]]; then
    if ! command -v brew &> /dev/null; then
        echo "[!] Homebrew no encontrado. Instalando..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        if [ $? -ne 0 ]; then
            echo "[ERROR] No se pudo instalar Homebrew."
            echo "Instálalo manualmente desde https://brew.sh"
            read -p "Presiona Enter para cerrar..."
            exit 1
        fi
        eval "$(/opt/homebrew/bin/brew shellenv)" 2>/dev/null || eval "$(/usr/local/bin/brew shellenv)" 2>/dev/null
        echo "[OK] Homebrew instalado."
    else
        echo "[OK] Homebrew ya estaba instalado."
    fi
fi

# ---- PYTHON ----
if ! command -v python3 &> /dev/null; then
    echo "[!] Python no encontrado. Instalando..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install python
    elif command -v apt &> /dev/null; then
        sudo apt update -y && sudo apt install -y python3 python3-pip
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y python3 python3-pip
    elif command -v pacman &> /dev/null; then
        sudo pacman -Sy --noconfirm python python-pip
    else
        echo "[ERROR] No se pudo instalar Python automaticamente."
        echo "Instálalo desde https://www.python.org/downloads/"
        read -p "Presiona Enter para cerrar..."
        exit 1
    fi
    echo "[OK] Python instalado."
else
    echo "[OK] Python ya estaba instalado."
fi

# ---- GIT ----
if ! command -v git &> /dev/null; then
    echo "[!] Git no encontrado. Instalando..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install git
    elif command -v apt &> /dev/null; then
        sudo apt install -y git
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y git
    elif command -v pacman &> /dev/null; then
        sudo pacman -Sy --noconfirm git
    else
        echo "[ERROR] No se pudo instalar Git automaticamente."
        echo "Instálalo desde https://git-scm.com/downloads"
        read -p "Presiona Enter para cerrar..."
        exit 1
    fi
    echo "[OK] Git instalado."
else
    echo "[OK] Git ya estaba instalado."
fi

# ---- DEPENDENCIAS ----
echo ""
echo "Instalando dependencias de Python..."
cd "$SCRIPT_DIR/Motor"

python3 -m pip install --upgrade pip --quiet
python3 -m pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo ""
    echo "[ERROR] Algo salió mal instalando las dependencias."
    echo "Intenta ejecutar el instalador con sudo."
    read -p "Presiona Enter para cerrar..."
    exit 1
fi

# ---- ACCESO DIRECTO ----
echo ""
echo "[OK] Dependencias instaladas."
echo ""
echo "Creando acceso directo..."
python3 crear_acceso.py

if [ -f "$SCRIPT_DIR/Lanzar.sh" ]; then
    chmod +x "$SCRIPT_DIR/Lanzar.sh"
fi

echo ""
echo "============================================"
echo "  Instalacion completada."
echo "  Usa Lanzar.sh para iniciar el programa."
echo "============================================"
echo ""
read -p "Presiona Enter para cerrar..."