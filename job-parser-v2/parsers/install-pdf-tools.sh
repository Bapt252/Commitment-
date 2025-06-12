#!/bin/bash

echo "🚀 Installation rapide des outils PDF"
echo "====================================="

if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "📦 Installation pour macOS..."
    
    if ! command -v brew &> /dev/null; then
        echo "📥 Installation de Homebrew..."
        echo "⚠️ Une interaction peut être nécessaire..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    
    echo "📄 Installation des outils PDF..."
    brew install poppler || echo "⚠️ poppler peut déjà être installé"
    brew install python3 || echo "⚠️ python3 peut déjà être installé"
    pip3 install pdfminer.six || echo "⚠️ pdfminer.six peut déjà être installé"
    
    echo "👁️ Installation Tesseract OCR..."
    brew install tesseract || echo "⚠️ tesseract peut déjà être installé"
    brew install imagemagick || echo "⚠️ imagemagick peut déjà être installé"
    brew install ghostscript || echo "⚠️ ghostscript peut déjà être installé"
    
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "📦 Installation pour Linux..."
    
    if command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y poppler-utils python3 python3-pip tesseract-ocr tesseract-ocr-fra imagemagick ghostscript
        pip3 install pdfminer.six
    else
        echo "⚠️ Gestionnaire de paquets non supporté. Installation manuelle requise."
    fi
fi

echo ""
echo "✅ Installation terminée !"
echo "🧪 Testez avec: node pdf-parser-optimized.js"
