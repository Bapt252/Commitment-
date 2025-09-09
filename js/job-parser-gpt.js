// JobParserGPT - Version sécurisée pour analyse intelligente de fiches de poste
// Les clés API doivent être configurées côté serveur uniquement

class JobParserGPT {
    constructor(options = {}) {
        this.debug = options.debug || false;
        this.version = '1.0-SECURE-' + Date.now();
        this.serverEndpoint = options.serverEndpoint || '/api/job-parser-gpt';
        
        if (this.debug) {
            console.log('🤖 JobParserGPT v1.0 initialisé (Mode sécurisé)');
            console.log('🔒 Les clés API sont gérées côté serveur');
        }
    }
    
    // ===== EXTRACTION DES FICHIERS =====
    
    async extractTextFromFile(file) {
        const fileType = file.type;
        
        if (fileType === 'text/plain') {
            return await this.readTextFile(file);
        } else if (fileType === 'application/pdf') {
            return await this.extractTextFromPDF(file);
        } else if (fileType.includes('word') || fileType.includes('document')) {
            return await this.extractTextFromWord(file);
        } else {
            throw new Error('Type de fichier non supporté: ' + fileType);
        }
    }
    
    async readTextFile(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = e => resolve(e.target.result);
            reader.onerror = e => reject(new Error('Erreur lecture fichier texte'));
            reader.readAsText(file, 'utf-8');
        });
    }
    
    async extractTextFromPDF(file) {
        try {
            // Vérifier que PDF.js est chargé
            if (typeof pdfjsLib === 'undefined') {
                throw new Error('PDF.js non disponible');
            }
            
            const arrayBuffer = await this.fileToArrayBuffer(file);
            const pdf = await pdfjsLib.getDocument(arrayBuffer).promise;
            
            let fullText = '';
            
            for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
                const page = await pdf.getPage(pageNum);
                const textContent = await page.getTextContent();
                
                const pageText = textContent.items
                    .map(item => item.str)
                    .join(' ');
                
                fullText += pageText + '\n';
            }
            
            return this.cleanExtractedText(fullText);
            
        } catch (error) {
            console.error('Erreur extraction PDF:', error);
            throw new Error('Impossible d\'extraire le texte du PDF: ' + error.message);
        }
    }
    
    async extractTextFromWord(file) {
        // Pour les fichiers Word, on utilise une approche simplifiée
        // En production, vous pourriez utiliser une bibliothèque comme mammoth.js
        try {
            const text = await this.readTextFile(file);
            return this.cleanExtractedText(text);
        } catch (error) {
            throw new Error('Extraction de fichier Word non implémentée complètement');
        }
    }
    
    fileToArrayBuffer(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = e => resolve(e.target.result);
            reader.onerror = e => reject(new Error('Erreur lecture fichier'));
            reader.readAsArrayBuffer(file);
        });
    }
    
    cleanExtractedText(text) {
        return text
            .replace(/\s+/g, ' ')  // Normaliser les espaces
            .replace(/\n+/g, '\n') // Normaliser les retours à la ligne
            .trim();
    }
    
    // ===== ANALYSE VIA SERVEUR SÉCURISÉ =====
    
    async analyzeJobWithServer(text) {
        if (!text || text.trim().length < 50) {
            throw new Error('Texte trop court pour analyse');
        }
        
        try {
            const response = await fetch(this.serverEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({
                    text: text,
                    action: 'parse-job'
                })
            });
            
            if (!response.ok) {
                const errorData = await response.text();
                throw new Error(`Erreur serveur (${response.status}): ${errorData}`);
            }
            
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.error || 'Erreur inconnue du serveur');
            }
            
            return this.validateAndCleanResult(data.result);
            
        } catch (error) {
            console.error('Erreur analyse serveur:', error);
            throw error;
        }
    }
    
    validateAndCleanResult(result) {
        // Valider et nettoyer le résultat
        const validatedResult = {
            title: (result.title || '').substring(0, 100),
            company: (result.company || '').substring(0, 100),
            location: (result.location || '').substring(0, 100),
            contract_type: (result.contract_type || '').substring(0, 50),
            experience: (result.experience || '').substring(0, 200),
            education: (result.education || '').substring(0, 200),
            salary: (result.salary || '').substring(0, 100),
            skills: Array.isArray(result.skills) ? result.skills.slice(0, 8) : [],
            responsibilities: (result.responsibilities || '').substring(0, 1000),
            benefits: (result.benefits || '').substring(0, 500)
        };
        
        return validatedResult;
    }
    
    // ===== MÉTHODES PRINCIPALES =====
    
    async parseJobFile(file) {
        if (this.debug) {
            console.log('📄 Analyse fichier via serveur sécurisé:', file.name);
        }
        
        try {
            // Étape 1: Extraire le texte
            const text = await this.extractTextFromFile(file);
            
            if (this.debug) {
                console.log('✅ Texte extrait, longueur:', text.length);
                console.log('📝 Aperçu:', text.substring(0, 200) + '...');
            }
            
            // Étape 2: Analyser via serveur sécurisé
            return await this.analyzeJobWithServer(text);
            
        } catch (error) {
            console.error('Erreur parsing fichier:', error);
            throw error;
        }
    }
    
    async parseJobText(text) {
        if (this.debug) {
            console.log('📝 Analyse texte via serveur sécurisé, longueur:', text.length);
        }
        
        try {
            return await this.analyzeJobWithServer(text);
        } catch (error) {
            console.error('Erreur parsing texte:', error);
            throw error;
        }
    }
    
    // ===== ALTERNATIVE POUR FICHIERS =====
    
    async parseJobFileUpload(file) {
        if (this.debug) {
            console.log('📤 Upload fichier pour analyse:', file.name);
        }
        
        try {
            const formData = new FormData();
            formData.append('file', file);
            
            const response = await fetch(this.serverEndpoint + '/upload', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                const errorData = await response.text();
                throw new Error(`Erreur upload (${response.status}): ${errorData}`);
            }
            
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.error || 'Erreur upload inconnue');
            }
            
            return this.validateAndCleanResult(data.result);
            
        } catch (error) {
            console.error('Erreur upload fichier:', error);
            throw error;
        }
    }
    
    // ===== MÉTHODES UTILITAIRES =====
    
    async testConnection() {
        try {
            const response = await fetch(this.serverEndpoint + '/health', {
                method: 'GET',
                headers: {
                    'Accept': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error(`Serveur non disponible (${response.status})`);
            }
            
            const data = await response.json();
            
            if (this.debug) {
                console.log('✅ Test de connexion serveur réussi:', data);
            }
            
            return data;
            
        } catch (error) {
            console.error('❌ Test de connexion serveur échoué:', error);
            throw error;
        }
    }
    
    // ===== MÉTHODES DE STATUT =====
    
    getStatus() {
        return {
            version: this.version,
            mode: 'secure',
            serverEndpoint: this.serverEndpoint,
            debug: this.debug
        };
    }
}

// ===== INTÉGRATION GLOBALE =====

// Remplacer l'ancienne instance si elle existe
if (typeof window !== 'undefined') {
    window.JobParserGPT = JobParserGPT;
    
    // Créer une instance globale
    window.jobParserGPTInstance = new JobParserGPT({ debug: true });
    
    console.log('🤖 JobParserGPT chargé et prêt (Mode sécurisé) !');
    console.log('📋 Fonctionnalités:');
    console.log('  - Analyse fichiers PDF/DOCX/TXT');
    console.log('  - Extraction texte locale');
    console.log('  - Analyse IA via serveur sécurisé');
    console.log('  - 10 champs extraits automatiquement');
    console.log('  🔒 Sécurité: Aucune clé API exposée côté client');
}

// Export pour modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = JobParserGPT;
}