/**
 * Fix PDF Extraction - Module pour corriger l'extraction PDF
 * Compatible avec le CV Parser V2
 */

const fs = require('fs');
const pdf = require('pdf-parse');

/**
 * Extrait le texte d'un PDF de manière robuste
 * @param {string} pdfPath - Chemin vers le fichier PDF
 * @returns {Promise<Object>} - Résultat avec texte extrait
 */
async function extractPdfText(pdfPath) {
    try {
        console.log(`[fix-pdf-extraction] Extraction du fichier: ${pdfPath}`);
        
        // Vérifier que le fichier existe
        if (!fs.existsSync(pdfPath)) {
            throw new Error(`Fichier non trouvé: ${pdfPath}`);
        }
        
        // Lire le fichier PDF
        const dataBuffer = fs.readFileSync(pdfPath);
        
        // Extraire le texte avec pdf-parse
        const data = await pdf(dataBuffer);
        
        console.log(`[fix-pdf-extraction] Extraction réussie: ${data.text.length} caractères`);
        
        return {
            success: true,
            text: data.text,
            numpages: data.numpages,
            info: data.info,
            metadata: data.metadata,
            version: data.version
        };
        
    } catch (error) {
        console.error(`[fix-pdf-extraction] Erreur: ${error.message}`);
        
        // Fallback: extraction basique
        try {
            const dataBuffer = fs.readFileSync(pdfPath);
            // Tentative d'extraction simple (recherche de patterns texte)
            const basicText = dataBuffer.toString('utf8').replace(/[^\x20-\x7E]/g, ' ').trim();
            
            if (basicText.length > 50) {
                console.log(`[fix-pdf-extraction] Fallback réussi: ${basicText.length} caractères`);
                return {
                    success: true,
                    text: basicText,
                    numpages: 1,
                    fallback: true
                };
            }
        } catch (fallbackError) {
            console.error(`[fix-pdf-extraction] Fallback échoué: ${fallbackError.message}`);
        }
        
        return {
            success: false,
            error: error.message,
            text: '',
            numpages: 0
        };
    }
}

/**
 * Fonction principale d'extraction
 */
async function main() {
    const pdfPath = process.argv[2];
    
    if (!pdfPath) {
        console.error('[fix-pdf-extraction] Usage: node fix-pdf-extraction.js <chemin-pdf>');
        process.exit(1);
    }
    
    try {
        const result = await extractPdfText(pdfPath);
        console.log(JSON.stringify(result));
    } catch (error) {
        console.error('[fix-pdf-extraction] Erreur fatale:', error.message);
        console.log(JSON.stringify({
            success: false,
            error: error.message,
            text: '',
            numpages: 0
        }));
    }
}

// Exporter les fonctions
module.exports = {
    extractPdfText
};

// Exécuter si appelé directement
if (require.main === module) {
    main();
}
