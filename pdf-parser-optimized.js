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
