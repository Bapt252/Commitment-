#!/bin/bash

# 🚀 Quick Fix PDF - SuperSmartMatch V2 PROMPT 2
# Résout immédiatement le problème d'extraction PDF

set -e

echo "🚀 SuperSmartMatch V2 - Quick Fix PDF"
echo "====================================="
echo ""

# Vérifier si nous sommes dans le bon répertoire
if [ ! -f "parse-real-documents.js" ]; then
    echo "❌ Veuillez exécuter ce script depuis le répertoire racine du projet SuperSmartMatch V2"
    echo "   (là où se trouve parse-real-documents.js)"
    exit 1
fi

echo "✅ Répertoire du projet détecté"
echo ""

# Sauvegarder l'ancien parser
if [ -f "parse-real-documents.js" ]; then
    cp parse-real-documents.js parse-real-documents.js.backup
    echo "💾 Ancien parser sauvegardé: parse-real-documents.js.backup"
fi

echo "📥 Installation du parser PDF optimisé..."

# Créer le parser PDF optimisé
cat > pdf-parser-optimized.js << 'EOF'
#!/usr/bin/env node

/**
 * 🚀 Parser PDF Ultra-Optimisé - SuperSmartMatch V2 PROMPT 2
 * Résout le problème d'extraction de texte PDF + OCR intégré
 */

const fs = require('fs');
const { execSync } = require('child_process');
const path = require('path');

class SuperSmartPDFParser {
    constructor() {
        this.checkTools();
    }

    checkTools() {
        console.log('🔍 Vérification des outils...');
        
        const tools = {
            pdftotext: this.hasCommand('pdftotext --version'),
            pdf2txt: this.hasCommand('pdf2txt.py --version'),
            tesseract: this.hasCommand('tesseract --version'),
            textutil: this.hasCommand('textutil --help')
        };

        const available = Object.values(tools).filter(Boolean).length;
        console.log(`📊 Outils disponibles: ${available}/4`);
        
        Object.entries(tools).forEach(([tool, avail]) => {
            console.log(`${avail ? '✅' : '❌'} ${tool}`);
        });
        
        if (available === 0) {
            console.log('⚠️ Aucun outil d\'extraction trouvé !');
            console.log('🔧 Lancez: ./install-pdf-tools.sh');
            return false;
        }
        
        return tools;
    }

    hasCommand(command) {
        try {
            execSync(command, { stdio: 'pipe' });
            return true;
        } catch (error) {
            return false;
        }
    }

    async extractBestText(pdfPath) {
        console.log(`\n📄 Extraction: ${path.basename(pdfPath)}`);
        console.log('================================');
        
        if (!fs.existsSync(pdfPath)) {
            throw new Error(`Fichier non trouvé: ${pdfPath}`);
        }

        const methods = [
            () => this.tryPdftotext(pdfPath),
            () => this.tryPdf2txt(pdfPath),
            () => this.tryTesseract(pdfPath),
            () => this.tryTextutil(pdfPath)
        ];

        let bestResult = null;
        let bestScore = 0;

        for (const method of methods) {
            try {
                const result = await method();
                if (result && result.text.length > 50) {
                    const score = this.scoreExtraction(result.text);
                    console.log(`   📊 ${result.method}: ${result.text.length} chars, score: ${score}`);
                    
                    if (score > bestScore) {
                        bestScore = score;
                        bestResult = result;
                    }
                }
            } catch (error) {
                console.log(`   ❌ Méthode échouée: ${error.message.split('\n')[0]}`);
            }
        }

        if (!bestResult) {
            throw new Error('Toutes les méthodes d\'extraction ont échoué');
        }

        console.log(`\n✅ Meilleure extraction: ${bestResult.method} (score: ${bestScore})`);
        
        // Sauvegarder
        const outputPath = pdfPath.replace('.pdf', '_extracted.txt');
        fs.writeFileSync(outputPath, bestResult.text);
        console.log(`💾 Texte sauvegardé: ${outputPath}`);
        
        return bestResult;
    }

    scoreExtraction(text) {
        let score = 0;
        
        // Longueur du texte
        score += Math.min(text.length / 1000, 50);
        
        // Présence d'email
        if (text.match(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/)) score += 20;
        
        // Présence de téléphone
        if (text.match(/\d{2}[\s.-]?\d{2}[\s.-]?\d{2}[\s.-]?\d{2}[\s.-]?\d{2}/)) score += 15;
        
        // Pas de charabia PDF
        if (!this.isGarbage(text)) score += 30;
        
        // Mots français/anglais courants
        const commonWords = ['le', 'de', 'et', 'à', 'un', 'il', 'être', 'et', 'à', 'avoir', 'ne', 'je', 'son', 'que', 'se', 'qui', 'ce', 'dans', 'en', 'du', 'elle', 'au', 'de', 'ce', 'le', 'pour', 'are', 'the', 'and', 'to', 'of', 'in', 'you', 'that', 'it', 'he', 'was', 'for', 'on', 'with', 'as', 'his', 'they'];
        const wordCount = commonWords.filter(word => text.toLowerCase().includes(word)).length;
        score += wordCount * 2;
        
        return Math.round(score);
    }

    tryPdftotext(pdfPath) {
        console.log('  🔄 Tentative pdftotext...');
        const outputPath = pdfPath.replace('.pdf', '_pdftotext.txt');
        execSync(`pdftotext -layout -enc UTF-8 "${pdfPath}" "${outputPath}"`, { stdio: 'pipe' });
        
        if (fs.existsSync(outputPath)) {
            const text = fs.readFileSync(outputPath, 'utf8');
            return { text, method: 'pdftotext' };
        }
        throw new Error('pdftotext failed');
    }

    tryPdf2txt(pdfPath) {
        console.log('  🔄 Tentative pdf2txt.py...');
        const outputPath = pdfPath.replace('.pdf', '_pdf2txt.txt');
        execSync(`pdf2txt.py -o "${outputPath}" "${pdfPath}"`, { stdio: 'pipe' });
        
        if (fs.existsSync(outputPath)) {
            const text = fs.readFileSync(outputPath, 'utf8');
            return { text, method: 'pdf2txt' };
        }
        throw new Error('pdf2txt failed');
    }

    tryTesseract(pdfPath) {
        console.log('  🔄 Tentative OCR Tesseract...');
        const outputPath = pdfPath.replace('.pdf', '_tesseract.txt');
        
        try {
            const imagePath = pdfPath.replace('.pdf', '_temp.png');
            execSync(`convert -density 300 "${pdfPath}[0]" "${imagePath}"`, { stdio: 'pipe' });
            execSync(`tesseract "${imagePath}" "${outputPath.replace('.txt', '')}" -l fra+eng`, { stdio: 'pipe' });
            
            if (fs.existsSync(outputPath)) {
                const text = fs.readFileSync(outputPath, 'utf8');
                // Nettoyage
                if (fs.existsSync(imagePath)) fs.unlinkSync(imagePath);
                return { text, method: 'tesseract' };
            }
        } catch (error) {
            throw new Error('tesseract OCR failed');
        }
        throw new Error('tesseract failed');
    }

    tryTextutil(pdfPath) {
        console.log('  🔄 Tentative textutil...');
        const outputPath = pdfPath.replace('.pdf', '_textutil.txt');
        execSync(`textutil -convert txt "${pdfPath}" -output "${outputPath}"`, { stdio: 'pipe' });
        
        if (fs.existsSync(outputPath)) {
            const text = fs.readFileSync(outputPath, 'utf8');
            return { text, method: 'textutil' };
        }
        throw new Error('textutil failed');
    }

    isGarbage(text) {
        // Détecter le charabia PDF
        const garbagePatterns = [
            /obj\s+\d+\s+\d+\s+R/,
            /\/[A-Z][a-zA-Z]*\s+/,
            /stream[\s\S]*?endstream/,
            /%PDF-\d\.\d/,
            /^[\x00-\x1F\x7F-\x9F]*$/m
        ];
        
        const garbageCount = garbagePatterns.filter(pattern => pattern.test(text.substring(0, 1000))).length;
        return garbageCount >= 2;
    }
}

// Fonction principale
async function main() {
    console.log('🚀 SuperSmartMatch V2 - Parser PDF Ultra-Optimisé');
    console.log('================================================');
    
    const parser = new SuperSmartPDFParser();
    
    const testFiles = [
        'cv_christine.pdf',
        'fdp.pdf', 
        'DA SILVA christine manuelle_CV.pdf'
    ];
    
    console.log('\n🎯 Recherche des fichiers PDF...');
    
    const foundFiles = testFiles.filter(file => {
        const exists = fs.existsSync(file);
        console.log(`${exists ? '✅' : '❌'} ${file}`);
        return exists;
    });
    
    if (foundFiles.length === 0) {
        console.log('\n⚠️ Aucun fichier PDF trouvé dans le répertoire');
        console.log('📄 Placez vos PDF dans le répertoire et relancez le script');
        return;
    }
    
    console.log(`\n🚀 Traitement de ${foundFiles.length} fichier(s)...\n`);
    
    for (const file of foundFiles) {
        try {
            await parser.extractBestText(file);
            console.log(`✅ ${file} traité avec succès\n`);
        } catch (error) {
            console.log(`❌ Erreur avec ${file}: ${error.message}\n`);
        }
    }
    
    console.log('🎉 Extraction terminée !');
    console.log('📁 Fichiers texte générés: *_extracted.txt');
    console.log('🚀 Lancez maintenant: node parse-real-documents.js');
}

if (require.main === module) {
    main().catch(console.error);
}

module.exports = SuperSmartPDFParser;
EOF

chmod +x pdf-parser-optimized.js

# Créer le script d'installation
cat > install-pdf-tools.sh << 'EOF'
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
EOF

chmod +x install-pdf-tools.sh

# Créer un script de test rapide
cat > test-pdf-extraction.sh << 'EOF'
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
EOF

chmod +x test-pdf-extraction.sh

echo ""
echo "🎉 Quick Fix PDF installé avec succès !"
echo ""
echo "📁 Nouveaux fichiers créés:"
echo "   ✅ pdf-parser-optimized.js    - Parser PDF ultra-robuste"
echo "   ✅ install-pdf-tools.sh       - Installation des dépendances"
echo "   ✅ test-pdf-extraction.sh     - Test rapide"
echo ""
echo "🚀 Utilisation immédiate:"
echo ""
echo "1️⃣ Installer les outils PDF (si nécessaire):"
echo "   ./install-pdf-tools.sh"
echo ""
echo "2️⃣ Tester l'extraction:"
echo "   ./test-pdf-extraction.sh"
echo ""
echo "3️⃣ Utiliser avec vos PDF:"
echo "   node pdf-parser-optimized.js"
echo ""
echo "4️⃣ Continuer avec votre parser existant:"
echo "   node parse-real-documents.js"
echo ""
echo "🔧 Le problème d'extraction PDF sera résolu !"
echo "   Le parser testera automatiquement plusieurs méthodes"
echo "   et choisira la meilleure extraction disponible."
