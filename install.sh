#!/bin/bash

# Script de instalação para Sistema de Leitura

set -e

echo "📚 Instalando Sistema de Leitura..."
echo ""

# Verificar se está no Ubuntu/Debian
if ! command -v apt-get &> /dev/null; then
    echo "❌ Este script requer apt-get (Ubuntu/Debian)"
    exit 1
fi

echo "1️⃣  Atualizando pacotes do sistema..."
sudo apt-get update

echo "2️⃣  Instalando dependências do sistema..."
sudo apt-get install -y \
    python3-pip \
    tesseract-ocr \
    tesseract-ocr-por \
    tesseract-ocr-eng \
    libtesseract-dev \
    ghostscript \
    imagemagick \
    libopencv-dev \
    python3-opencv

echo "3️⃣  Criando ambiente virtual Python..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Ambiente virtual criado"
else
    echo "✓ Ambiente virtual já existe"
fi

echo "4️⃣  Ativando ambiente virtual e instalando dependências Python..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✅ Instalação concluída com sucesso!"
echo ""
echo "📖 Para começar:"
echo "   1. source venv/bin/activate"
echo "   2. python book_scanner.py -i /caminho/imagens -o saida.pdf -l por"
echo ""
