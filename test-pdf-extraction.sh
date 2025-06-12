#!/bin/bash

echo "🧪 Test rapide de l'extraction PDF"
echo "================================="

# Vérifier les fichiers PDF
pdf_files=("cv_christine.pdf" "fdp.pdf" "DA SILVA christine manuelle_CV.pdf")
found_files=()

echo "🔍 Recherche des fichiers PDF..."
for file in "${pdf_files[@]}"; do
    if [ -f "$file" ]; then
        found_files+=("$file")
        echo "✅ Trouvé: $file"
    else
        echo "❌ Non trouvé: $file"
    fi
done

if [ ${#found_files[@]} -eq 0 ]; then
    echo ""
    echo "⚠️ Aucun fichier PDF trouvé"
    echo "📄 Créons un PDF de test..."
    
    # Créer un fichier texte de test
    cat > test_cv.txt << 'TESTCV'
CURRICULUM VITAE

DA SILVA Christine Manuelle
Email: dasilva_christine@yahoo.fr
Téléphone: 0471896956

COMPÉTENCES TECHNIQUES:
• JavaScript, TypeScript
• Python, Node.js
• HTML, CSS, React
• SQL, MongoDB
• Git, Docker

EXPÉRIENCE PROFESSIONNELLE:
Lead Developer - 5 ans d'expérience
Développement d'applications web modernes

FORMATION:
Master en Informatique
TESTCV
    
    if command -v textutil &> /dev/null; then
        textutil -convert pdf test_cv.txt -output test_cv.pdf 2>/dev/null
        if [ -f "test_cv.pdf" ]; then
            echo "📄 PDF de test créé: test_cv.pdf"
            found_files+=("test_cv.pdf")
        fi
    fi
    
    rm -f test_cv.txt
fi

if [ ${#found_files[@]} -gt 0 ]; then
    echo ""
    echo "🚀 Test de l'extraction avec ${#found_files[@]} fichier(s)..."
    echo ""
    
    node pdf-parser-optimized.js
    
    echo ""
    echo "📊 Résultats de l'extraction:"
    echo "=========================="
    
    for file in *_extracted.txt; do
        if [ -f "$file" ]; then
            size=$(wc -c < "$file")
            echo "✅ $file ($size caractères)"
            echo "   📄 Aperçu: $(head -2 "$file" | tr '\n' ' ' | cut -c1-80)..."
            echo ""
        fi
    done
    
    echo "🎯 Prochaine étape: node parse-real-documents.js"
    
else
    echo "❌ Aucun fichier PDF disponible pour le test"
    echo ""
    echo "💡 Pour tester:"
    echo "   1. Placez vos PDF dans ce répertoire"
    echo "   2. Relancez: ./test-pdf-extraction.sh"
fi
