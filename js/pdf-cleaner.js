/**
 * Classe pour nettoyer et extraire le texte des PDFs
 */
class PDFCleaner {
    constructor() {
        // On pourrait ajouter des options ici si nécessaire
    }
    
    /**
     * Extrait le texte d'un fichier PDF
     * @param {File} pdfFile - Le fichier PDF
     * @returns {Promise<string>} - Le texte extrait
     */
    async extractTextFromPDF(pdfFile) {
        // Vérifier si pdfjsLib est disponible
        if (!window.pdfjsLib) {
            console.error('PDF.js library not found!');
            throw new Error('PDF.js library not loaded. Please include it in your project.');
        }
        
        try {
            // Lire le fichier en tant qu'ArrayBuffer
            const arrayBuffer = await this.readFileAsArrayBuffer(pdfFile);
            
            // Charger le document PDF
            const loadingTask = pdfjsLib.getDocument({ data: arrayBuffer });
            const pdf = await loadingTask.promise;
            
            // Extraire le texte de toutes les pages
            let extractedText = '';
            for (let i = 1; i <= pdf.numPages; i++) {
                const page = await pdf.getPage(i);
                const content = await page.getTextContent();
                
                // Fusionner les éléments textuels avec des espaces
                const pageText = content.items
                    .map(item => item.str)
                    .join(' ');
                
                extractedText += pageText + '\n\n';
            }
            
            // Nettoyer le texte extrait
            return this.cleanPDFText(extractedText);
        } catch (error) {
            console.error('Error extracting text from PDF:', error);
            throw error;
        }
    }
    
    /**
     * Lit un fichier en tant qu'ArrayBuffer
     * @param {File} file - Le fichier à lire
     * @returns {Promise<ArrayBuffer>} - Le contenu du fichier
     */
    readFileAsArrayBuffer(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            
            reader.onload = function(e) {
                resolve(e.target.result);
            };
            
            reader.onerror = function(e) {
                reject(new Error('Error reading file: ' + e.target.error));
            };
            
            reader.readAsArrayBuffer(file);
        });
    }
    
    /**
     * Nettoie le texte extrait d'un PDF
     * @param {string} text - Le texte brut
     * @returns {string} - Le texte nettoyé
     */
    cleanPDFText(text) {
        if (!text) return '';
        
        // Supprimer les caractères spéciaux inutiles
        let cleanedText = text
            .replace(/\s+/g, ' ')  // Remplacer les séquences d'espaces par un seul espace
            .replace(/[^\x20-\x7E\xA0-\xFF\u0100-\u017F\u0180-\u024F\n]/g, '') // Garder uniquement les caractères latins courants
            .replace(/(\n\s*){3,}/g, '\n\n');  // Limiter les sauts de ligne consécutifs
        
        // Supprimer les en-têtes et pieds de page récurrents (motifs typiques)
        cleanedText = this.removeHeadersAndFooters(cleanedText);
        
        // Normaliser les sauts de ligne pour les listes
        cleanedText = this.normalizeListItems(cleanedText);
        
        return cleanedText.trim();
    }
    
    /**
     * Supprime les en-têtes et pieds de page récurrents
     * @param {string} text - Le texte à nettoyer
     * @returns {string} - Le texte sans en-têtes/pieds de page
     */
    removeHeadersAndFooters(text) {
        // Supprimer les numéros de page isolés
        const pageNumberRegex = /^[0-9]+$|^Page [0-9]+ \/ [0-9]+$|^Page [0-9]+$/gm;
        let cleanedText = text.replace(pageNumberRegex, '');
        
        // Supprimer les dates isolées
        const dateRegex = /^\d{1,2}\/\d{1,2}\/\d{2,4}$/gm;
        cleanedText = cleanedText.replace(dateRegex, '');
        
        // Supprimer les lignes qui contiennent uniquement le nom du fichier ou des informations de copyright
        const copyrightRegex = /^.*(?:confidential|tous droits réservés|copyright|©|confidentiel).*$/gim;
        cleanedText = cleanedText.replace(copyrightRegex, '');
        
        return cleanedText;
    }
    
    /**
     * Normalise les éléments de liste
     * @param {string} text - Le texte à normaliser
     * @returns {string} - Le texte avec listes normalisées
     */
    normalizeListItems(text) {
        // Détecter et normaliser les éléments de liste avec chiffres
        const numberedListRegex = /(\n\s*)(\d+[\.\)]\s+)([A-Z])/g;
        let normalizedText = text.replace(numberedListRegex, '$1$2$3');
        
        // Détecter et normaliser les éléments de liste avec puces
        const bulletListRegex = /(\n\s*)([\-\•\*]\s+)([A-Z])/g;
        normalizedText = normalizedText.replace(bulletListRegex, '$1$2$3');
        
        return normalizedText;
    }
}

// Exposer globalement
window.PDFCleaner = PDFCleaner;
