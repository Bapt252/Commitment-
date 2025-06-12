#!/usr/bin/env node

/**
 * 🔧 Fix immédiat pour l'extraction PDF - SuperSmartMatch V2
 * Corrige la détection de garbage PDF et améliore le scoring
 */

const fs = require('fs');
const { execSync } = require('child_process');
const path = require('path');

class FixedPDFParser {
    constructor() {
        console.log('🔧 Parser PDF Corrigé - SuperSmartMatch V2');
        console.log('==========================================');
    }

    // Détection améliorée du garbage PDF
    isReallyGarbage(text) {
        if (!text || text.length < 10) return true;
        
        // Premiers 500 caractères pour la détection
        const sample = text.substring(0, 500);
        
        // Patterns de garbage PDF stricts
        const strictGarbagePatterns = [
            /^%PDF-/,                           // Commence par %PDF-
            /^[\x00-\x08\x0B\x0C\x0E-\x1F]+/,  // Caractères de contrôle au début
            /obj\s+\d+\s+\d+\s+R/,              // Références d'objets PDF
            /stream[\s\S]*?endstream/,           // Flux PDF
            /\/[A-Z][a-zA-Z]*\s+\d/,           // Commandes PDF avec nombres
            /BT[\s\S]*?ET/,                     // Blocs de texte PDF
            /<<[\s\S]*?>>/                      // Dictionnaires PDF
        ];
        
        // Si 2+ patterns matchent, c'est du garbage
        const garbageMatches = strictGarbagePatterns.filter(pattern => pattern.test(sample)).length;
        
        // Test additionnel: ratio de caractères imprimables
        const printableChars = sample.match(/[a-zA-Z0-9\s.,;:!?@-]/g) || [];
        const printableRatio = printableChars.length / sample.length;
        
        const isGarbage = garbageMatches >= 2 || printableRatio < 0.3;
        
        console.log(`   🔍 Garbage check: ${garbageMatches} patterns, ${Math.round(printableRatio*100)}% printable → ${isGarbage ? 'GARBAGE' : 'OK'}`);
        
        return isGarbage;
    }

    // Scoring révisé qui pénalise fortement le garbage
    scoreExtraction(text) {
        if (this.isReallyGarbage(text)) {
            return 0; // Score de 0 pour le garbage
        }
        
        let score = 0;
        
        // Longueur (mais limitée pour éviter de favoriser le garbage long)
        score += Math.min(text.length / 100, 25);
        
        // Présence d'informations utiles
        if (text.match(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/)) score += 30; // Email
        if (text.match(/\d{2}[\s.-]?\d{2}[\s.-]?\d{2}[\s.-]?\d{2}[\s.-]?\d{2}/)) score += 25; // Téléphone
        if (text.match(/\b(JavaScript|Python|HTML|CSS|React|Vue|Angular|Java|PHP|SQL)\b/i)) score += 20; // Compétences tech
        
        // Mots français/anglais courants
        const commonWords = ['experience', 'compétences', 'formation', 'projet', 'développeur', 'manager', 'the', 'and', 'to', 'of', 'in', 'you', 'that', 'it', 'for', 'on', 'with', 'as'];
        const wordMatches = commonWords.filter(word => text.toLowerCase().includes(word)).length;
        score += wordMatches * 3;
        
        // Ratio de caractères lisibles
        const readable = text.match(/[a-zA-ZÀ-ÿ0-9\s.,;:!?@-]/g) || [];
        const readableRatio = readable.length / text.length;
        score += readableRatio * 30;
        
        return Math.round(score);
    }

    async extractCleanText(pdfPath) {
        console.log(`\n📄 Extraction corrigée: ${path.basename(pdfPath)}`);
        console.log('=========================================');
        
        if (!fs.existsSync(pdfPath)) {
            throw new Error(`Fichier non trouvé: ${pdfPath}`);
        }

        const methods = [
            () => this.tryPdftotext(pdfPath),
            () => this.tryPdf2txt(pdfPath), 
            () => this.tryTesseract(pdfPath),
            () => this.tryTextutil(pdfPath)
        ];

        let validResults = [];

        for (const method of methods) {
            try {
                const result = await method();
                if (result && result.text.length > 50) {
                    const score = this.scoreExtraction(result.text);
                    const isClean = !this.isReallyGarbage(result.text);
                    
                    console.log(`   📊 ${result.method}: ${result.text.length} chars, score: ${score}, clean: ${isClean ? 'YES' : 'NO'}`);
                    
                    if (isClean && score > 0) {
                        validResults.push({ ...result, score });
                    }
                }
            } catch (error) {
                console.log(`   ❌ ${error.message.split('\n')[0]}`);
            }
        }

        if (validResults.length === 0) {
            throw new Error('Aucune extraction propre trouvée');
        }

        // Sélectionner le meilleur résultat PROPRE
        const bestResult = validResults.reduce((best, current) => 
            current.score > best.score ? current : best
        );

        console.log(`\n✅ Meilleure extraction PROPRE: ${bestResult.method} (score: ${bestResult.score})`);
        
        // Sauvegarder
        const outputPath = pdfPath.replace('.pdf', '_clean_extracted.txt');
        fs.writeFileSync(outputPath, bestResult.text);
        console.log(`💾 Texte propre sauvegardé: ${outputPath}`);
        
        // Prévisualisation
        const preview = bestResult.text.substring(0, 200).replace(/\s+/g, ' ');
        console.log(`📖 Aperçu: ${preview}...`);
        
        return bestResult;
    }

    tryPdftotext(pdfPath) {
        if (!this.hasCommand('pdftotext --version')) throw new Error('pdftotext non disponible');
        
        const outputPath = pdfPath.replace('.pdf', '_pdftotext.txt');
        execSync(`pdftotext -layout -enc UTF-8 "${pdfPath}" "${outputPath}"`, { stdio: 'pipe' });
        
        if (fs.existsSync(outputPath)) {
            const text = fs.readFileSync(outputPath, 'utf8');
            return { text, method: 'pdftotext' };
        }
        throw new Error('pdftotext failed');
    }

    tryPdf2txt(pdfPath) {
        if (!this.hasCommand('pdf2txt.py --version')) throw new Error('pdf2txt non disponible');
        
        const outputPath = pdfPath.replace('.pdf', '_pdf2txt.txt');
        execSync(`pdf2txt.py -o "${outputPath}" "${pdfPath}"`, { stdio: 'pipe' });
        
        if (fs.existsSync(outputPath)) {
            const text = fs.readFileSync(outputPath, 'utf8');
            return { text, method: 'pdf2txt' };
        }
        throw new Error('pdf2txt failed');
    }

    tryTesseract(pdfPath) {
        if (!this.hasCommand('tesseract --version')) throw new Error('tesseract non disponible');
        
        const outputPath = pdfPath.replace('.pdf', '_tesseract.txt');
        
        try {
            const imagePath = pdfPath.replace('.pdf', '_temp.png');
            execSync(`convert -density 300 "${pdfPath}[0]" "${imagePath}"`, { stdio: 'pipe' });
            execSync(`tesseract "${imagePath}" "${outputPath.replace('.txt', '')}" -l fra+eng`, { stdio: 'pipe' });
            
            if (fs.existsSync(outputPath)) {
                const text = fs.readFileSync(outputPath, 'utf8');
                if (fs.existsSync(imagePath)) fs.unlinkSync(imagePath);
                return { text, method: 'tesseract' };
            }
        } catch (error) {
            throw new Error('tesseract OCR failed');
        }
        throw new Error('tesseract failed');
    }

    tryTextutil(pdfPath) {
        if (!this.hasCommand('textutil --help')) throw new Error('textutil non disponible');
        
        const outputPath = pdfPath.replace('.pdf', '_textutil.txt');
        execSync(`textutil -convert txt "${pdfPath}" -output "${outputPath}"`, { stdio: 'pipe' });
        
        if (fs.existsSync(outputPath)) {
            const text = fs.readFileSync(outputPath, 'utf8');
            return { text, method: 'textutil' };
        }
        throw new Error('textutil failed');
    }

    hasCommand(command) {
        try {
            execSync(command, { stdio: 'pipe' });
            return true;
        } catch (error) {
            return false;
        }
    }
}

// Installation rapide de pdftotext
function installPdftotext() {
    console.log('\n🔧 Installation pdftotext (recommandé)...');
    
    try {
        if (process.platform === 'darwin') {
            console.log('📦 Installation via Homebrew...');
            execSync('brew install poppler', { stdio: 'inherit' });
            console.log('✅ pdftotext installé !');
        } else {
            console.log('⚠️ Installez manuellement: sudo apt-get install poppler-utils');
        }
    } catch (error) {
        console.log('❌ Installation échouée:', error.message);
    }
}

// Fonction principale
async function main() {
    const parser = new FixedPDFParser();
    
    // Vérifier si pdftotext est disponible
    if (!parser.hasCommand('pdftotext --version')) {
        console.log('\n⚠️ pdftotext non trouvé - c\'est souvent la meilleure méthode');
        console.log('🔧 Voulez-vous l\'installer ? (Recommandé)');
        installPdftotext();
    }
    
    const testFiles = ['cv_christine.pdf', 'fdp.pdf'];
    
    console.log('\n🚀 Extraction avec détection garbage améliorée...\n');
    
    for (const file of testFiles) {
        if (fs.existsSync(file)) {
            try {
                await parser.extractCleanText(file);
                console.log(`✅ ${file} - Extraction propre réussie\n`);
            } catch (error) {
                console.log(`❌ ${file} - ${error.message}\n`);
            }
        }
    }
    
    console.log('🎉 Extraction corrigée terminée !');
    console.log('📁 Fichiers propres: *_clean_extracted.txt');
}

if (require.main === module) {
    main().catch(console.error);
}

module.exports = FixedPDFParser;