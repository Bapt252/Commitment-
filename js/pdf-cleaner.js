/**
 * PDF Cleaner - Module pour nettoyer les données PDF et améliorer l'analyse des fiches de poste
 * Ce module détecte et nettoie les artefacts PDF qui peuvent perturber l'analyse des fiches de poste.
 */

// Classe principale pour le nettoyage des PDF
class PDFCleaner {
    /**
     * Initialise le nettoyeur de PDF
     * @param {Object} options - Options de configuration
     */
    constructor(options = {}) {
        this.options = Object.assign({
            debug: false
        }, options);
    }

    /**
     * Détecte si le texte contient des artefacts PDF
     * @param {string} text - Texte à analyser
     * @returns {boolean} - True si des artefacts PDF sont détectés
     */
    hasPDFArtifacts(text) {
        if (!text) return false;

        // Patterns d'artefacts PDF à détecter
        const pdfArtifactPatterns = [
            /\d+\s+\d+\s+obj/,                // Objets PDF (ex: "1 0 obj")
            /endobj/,                         // Fin d'objet
            /xref/,                           // Table de référence
            /trailer/,                        // Trailer
            /startxref/,                      // Début de xref
            /stream/,                         // Début de stream
            /endstream/,                      // Fin de stream
            /<</,                             // Début de dictionnaire
            />>/,                             // Fin de dictionnaire
            /%PDF-\d+\.\d+/,                  // En-tête PDF
            /\/Type\s*\/[A-Za-z]+/,           // Définition de type PDF
            /\/Length\s+\d+/,                 // Définition de longueur
            /\/Filter\s+\/[A-Za-z]+/,         // Définition de filtre
            /\/[A-Z][a-zA-Z]+\s+\d+\s+\d+\s+R/, // Référence à un objet
            /\/Contents\s+\[\s*\d+\s+\d+\s+R\s*\]/ // Référence à des contenus
        ];

        // Vérifier si le texte contient des artefacts PDF
        return pdfArtifactPatterns.some(pattern => pattern.test(text));
    }

    /**
     * Détermine le ratio d'artefacts PDF dans un texte
     * @param {string} text - Texte à analyser
     * @returns {number} - Ratio entre 0 et 1 (0 = aucun artefact, 1 = que des artefacts)
     */
    getPDFArtifactRatio(text) {
        if (!text) return 0;

        const lines = text.split('\n');
        let artifactLines = 0;

        // Patterns d'artefacts PDF à détecter
        const pdfArtifactPatterns = [
            /^\s*\d+\s+\d+\s+obj/,            // Objets PDF (ex: "1 0 obj")
            /^\s*endobj/,                     // Fin d'objet
            /^\s*xref/,                       // Table de référence
            /^\s*trailer/,                    // Trailer
            /^\s*startxref/,                  // Début de xref
            /^\s*stream/,                     // Début de stream
            /^\s*endstream/,                  // Fin de stream
            /^\s*<</,                         // Début de dictionnaire
            /^\s*>>/,                         // Fin de dictionnaire
            /^\s*%PDF-\d+\.\d+/,              // En-tête PDF
            /^\s*\/[A-Z][A-Za-z]*\s+/,        // Noms PDF
            /^\s*\[\s*\d+\s+\d+\s+\d+\s+\d+\s*\]/, // Rectangle de sélection
            /^\s*\d+\s+\d+$/,                 // Juste deux nombres sur une ligne
            /^\s*\/Length\s+\d+/,             // Définition de longueur
            /^\s*\/Filter/,                   // Définition de filtre
            /^\s*\/[A-Z][a-zA-Z]+\s+\d+\s+\d+\s+R/, // Référence à un objet
            /^\s*\/Contents\s+\[\s*\d+\s+\d+\s+R\s*\]/ // Référence à des contenus
        ];

        // Compter les lignes contenant des artefacts PDF
        for (const line of lines) {
            if (pdfArtifactPatterns.some(pattern => pattern.test(line))) {
                artifactLines++;
            }
        }

        // Calculer le ratio
        return artifactLines / lines.length;
    }

    /**
     * Nettoie le texte extrait d'un PDF en supprimant les artefacts
     * @param {string} text - Texte à nettoyer
     * @returns {string} - Texte nettoyé
     */
    cleanPDFText(text) {
        if (!text) return "";

        // Si le texte ne contient pas d'artefacts PDF, le retourner tel quel
        if (!this.hasPDFArtifacts(text) || this.getPDFArtifactRatio(text) < 0.1) {
            this._log("Le texte ne contient pas d'artefacts PDF ou très peu, aucun nettoyage nécessaire");
            return text;
        }

        this._log("Nettoyage des artefacts PDF...");

        const lines = text.split('\n');
        const cleanedLines = [];
        let inContentSection = false;
        let contentStarted = false;
        let artifactCount = 0;
        let textualContentCount = 0;

        // Patterns pour détecter les artefacts PDF
        const pdfArtifactPatterns = [
            /^\s*\d+\s+\d+\s+obj/,            // Objets PDF (ex: "1 0 obj")
            /^\s*endobj/,                     // Fin d'objet
            /^\s*xref/,                       // Table de référence
            /^\s*trailer/,                    // Trailer
            /^\s*startxref/,                  // Début de xref
            /^\s*stream/,                     // Début de stream
            /^\s*endstream/,                  // Fin de stream
            /^\s*<</,                         // Début de dictionnaire
            /^\s*>>/,                         // Fin de dictionnaire
            /^\s*%PDF-\d+\.\d+/,              // En-tête PDF
            /^\s*\/[A-Z][A-Za-z]*\s+/,        // Noms PDF
            /^\s*\[\s*\d+\s+\d+\s+\d+\s+\d+\s*\]/, // Rectangle de sélection
            /^\s*\d+\s+\d+$/,                 // Juste deux nombres sur une ligne
            /^\s*\/Length\s+\d+/,             // Définition de longueur
            /^\s*\/Filter/                    // Définition de filtre
        ];

        // Pattern pour détecter les sections de contenu texte probable
        const textualContentPattern = /^[A-Z][a-z].*[a-z]$/;

        // Première passe: filtrer les lignes d'artefacts évidents
        for (const line of lines) {
            const isArtifact = pdfArtifactPatterns.some(pattern => pattern.test(line));
            const hasTextualContent = textualContentPattern.test(line.trim());

            if (isArtifact) {
                artifactCount++;
                continue;
            }

            if (hasTextualContent) {
                textualContentCount++;
                inContentSection = true;
            } else if (line.trim() === "" && inContentSection) {
                // Garder les lignes vides entre les sections de contenu
                cleanedLines.push(line);
                continue;
            } else if (!inContentSection && !contentStarted && line.trim() === "") {
                // Ignorer les lignes vides avant le début du contenu
                continue;
            }

            // Si la ligne n'est pas reconnue comme un artefact ni comme du contenu textuel
            if (line.trim().length > 0 || inContentSection) {
                cleanedLines.push(line);
                if (!contentStarted) contentStarted = true;
            }
        }

        this._log(`Artefacts détectés: ${artifactCount}, Lignes de contenu textuel: ${textualContentCount}`);

        let cleanedText = cleanedLines.join('\n');

        // Seconde passe: supprimer les motifs d'artefacts résiduels
        const residualPatterns = [
            /\d+\s+\d+\s+obj/g,               // Objets PDF
            /endobj/g,                        // Fin d'objet
            /xref/g,                          // Table de référence
            /trailer/g,                       // Trailer
            /startxref/g,                     // Début de xref
            /stream/g,                        // Début de stream
            /endstream/g,                     // Fin de stream
            /<</g,                            // Début de dictionnaire
            />>/g,                            // Fin de dictionnaire
            /%PDF-\d+\.\d+/g,                 // En-tête PDF
            /\/[A-Z][A-Za-z]*\s+\d+\s+\d+\s+R/g, // Référence à un objet
            /\/Contents\s+\[\s*\d+\s+\d+\s+R\s*\]/g // Référence à des contenus
        ];

        for (const pattern of residualPatterns) {
            cleanedText = cleanedText.replace(pattern, '');
        }

        // Normaliser les espaces
        cleanedText = cleanedText.replace(/\s+/g, ' ').trim();

        // Convertir les paragraphes (séparés par des lignes vides) en sauts de ligne
        cleanedText = cleanedText.replace(/\n\n+/g, '\n\n');

        this._log(`Texte nettoyé: ${cleanedText.length} caractères`);
        return cleanedText;
    }

    /**
     * Normalise le texte pour l'analyse (supprime les doublons, normalise les caractères, etc.)
     * @param {string} text - Texte à normaliser
     * @returns {string} - Texte normalisé
     */
    normalizeText(text) {
        if (!text) return "";

        // Nettoyer d'abord les artefacts PDF
        let normalizedText = this.cleanPDFText(text);

        // Remplacer les tirets et autres caractères de séparation par des espaces
        normalizedText = normalizedText.replace(/[–—−-]/g, ' ');

        // Normaliser les espaces
        normalizedText = normalizedText.replace(/\s+/g, ' ');

        // Normaliser les retours à la ligne
        normalizedText = normalizedText.replace(/\n+/g, '\n');

        // Supprimer les lignes vides consécutives
        normalizedText = normalizedText.split('\n')
            .filter((line, index, array) => line.trim() !== '' || (index > 0 && array[index - 1].trim() !== ''))
            .join('\n');

        return normalizedText.trim();
    }

    /**
     * Prétraite le texte d'une fiche de poste pour améliorer l'analyse
     * @param {string} text - Texte de la fiche de poste
     * @returns {string} - Texte prétraité
     */
    preprocessJobDescription(text) {
        if (!text) return "";

        // Détecter s'il s'agit d'un texte extrait d'un PDF
        const isPDFText = this.hasPDFArtifacts(text);
        let processedText = text;

        // Si c'est un PDF, nettoyer les artefacts
        if (isPDFText) {
            this._log("Le texte semble être extrait d'un PDF, nettoyage des artefacts...");
            processedText = this.cleanPDFText(text);
        }

        // Normaliser le texte
        processedText = this.normalizeText(processedText);

        return processedText;
    }

    /**
     * Affiche un message de log si le mode debug est activé
     * @param {string} message - Message à afficher
     * @private
     */
    _log(message) {
        if (this.options.debug) {
            console.log(`[PDFCleaner] ${message}`);
        }
    }
}

// Exporter la classe PDFCleaner pour l'utiliser dans d'autres fichiers
window.PDFCleaner = PDFCleaner;
