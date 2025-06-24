// Job Parsing UI Script - VERSION FONCTIONNELLE CORRIGÉE
// Connecte l'interface utilisateur avec l'API de parsing réelle

class JobParsingUI {
    constructor() {
        this.fileInput = document.getElementById('job-file-input');
        this.dropZone = document.getElementById('job-drop-zone');
        this.textArea = document.getElementById('job-description-text');
        this.analyzeButton = document.getElementById('analyze-job-text');
        this.loader = document.getElementById('analysis-loader');
        this.resultsContainer = document.getElementById('job-info-container');
        this.fileBadge = document.getElementById('file-badge');
        this.fileName = document.getElementById('file-name');
        this.removeFileBtn = document.getElementById('remove-file');
        
        // Initialiser les parsers
        this.jobParserAPI = new JobParserAPI({ debug: true });
        this.pdfCleaner = new PDFCleaner();
        
        this.init();
    }
    
    init() {
        if (!this.dropZone) return;
        
        this.setupFileUpload();
        this.setupTextAnalysis();
        this.setupFileRemoval();
        
        console.log('✅ Job Parsing UI fonctionnel initialisé avec API réelle');
    }
    
    setupFileUpload() {
        // Gestion du drag & drop
        this.dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            this.dropZone.classList.add('drag-active');
        });
        
        this.dropZone.addEventListener('dragleave', (e) => {
            e.preventDefault();
            this.dropZone.classList.remove('drag-active');
        });
        
        this.dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            this.dropZone.classList.remove('drag-active');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.handleFileSelection(files[0]);
            }
        });
        
        // Clic sur la zone de drop
        this.dropZone.addEventListener('click', () => {
            this.fileInput.click();
        });
        
        // Sélection de fichier
        if (this.fileInput) {
            this.fileInput.addEventListener('change', (e) => {
                if (e.target.files.length > 0) {
                    this.handleFileSelection(e.target.files[0]);
                }
            });
        }
    }
    
    setupTextAnalysis() {
        if (this.analyzeButton) {
            this.analyzeButton.addEventListener('click', () => {
                const text = this.textArea.value.trim();
                if (text) {
                    this.analyzeJobText(text);
                } else {
                    this.showNotification('error', 'Texte requis', 'Veuillez saisir le texte de la fiche de poste.');
                }
            });
        }
    }
    
    setupFileRemoval() {
        if (this.removeFileBtn) {
            this.removeFileBtn.addEventListener('click', () => {
                this.clearFile();
            });
        }
    }
    
    async handleFileSelection(file) {
        // Vérifier le type de fichier
        const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
        
        if (!allowedTypes.includes(file.type)) {
            this.showNotification('error', 'Type de fichier non supporté', 'Veuillez sélectionner un fichier PDF, DOCX ou TXT.');
            return;
        }
        
        // Vérifier la taille (5MB max)
        if (file.size > 5 * 1024 * 1024) {
            this.showNotification('error', 'Fichier trop volumineux', 'La taille du fichier ne doit pas dépasser 5MB.');
            return;
        }
        
        // Afficher le fichier sélectionné
        this.showSelectedFile(file);
        
        // Analyser le fichier RÉELLEMENT
        await this.analyzeFile(file);
    }
    
    showSelectedFile(file) {
        if (this.fileName && this.fileBadge) {
            this.fileName.textContent = file.name;
            this.fileBadge.style.display = 'flex';
            
            // Cacher le texte de drop zone
            const dropText = this.dropZone.querySelector('.drop-zone-text');
            if (dropText) {
                dropText.style.display = 'none';
            }
        }
    }
    
    clearFile() {
        if (this.fileInput) {
            this.fileInput.value = '';
        }
        
        if (this.fileBadge) {
            this.fileBadge.style.display = 'none';
        }
        
        // Réafficher le texte de drop zone
        const dropText = this.dropZone.querySelector('.drop-zone-text');
        if (dropText) {
            dropText.style.display = 'block';
        }
        
        // Cacher les résultats
        this.hideResults();
    }
    
    async analyzeFile(file) {
        this.showLoader();
        
        try {
            console.log('🚀 Analyse RÉELLE du fichier:', file.name, 'Type:', file.type);
            
            let extractedText = '';
            
            // Extraction en fonction du type de fichier
            switch (file.type) {
                case 'application/pdf':
                    extractedText = await this.extractTextFromPDF(file);
                    break;
                
                case 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                    extractedText = await this.extractTextFromDOCX(file);
                    break;
                    
                case 'application/msword':
                    extractedText = await this.extractTextFromDOC(file);
                    break;
                    
                case 'text/plain':
                    extractedText = await this.extractTextFromTXT(file);
                    break;
                    
                default:
                    throw new Error('Type de fichier non supporté');
            }
            
            console.log('📄 Texte extrait (100 premiers caractères):', extractedText.substring(0, 100));
            
            // Analyser le texte avec l'API RÉELLE
            if (extractedText.trim()) {
                const results = await this.jobParserAPI.parseJobText(extractedText);
                this.displayResults(results);
                this.showNotification('success', 'Analyse terminée', 'Les informations ont été extraites avec succès du fichier.');
            } else {
                throw new Error('Aucun texte extractible trouvé dans le fichier');
            }
            
        } catch (error) {
            console.error('❌ Erreur lors de l\'analyse du fichier:', error);
            this.showNotification('error', 'Erreur d\'analyse', 'Impossible d\'analyser le fichier: ' + error.message);
        } finally {
            this.hideLoader();
        }
    }
    
    async analyzeJobText(text) {
        this.showLoader();
        
        try {
            console.log('🚀 Analyse RÉELLE du texte (longueur: ' + text.length + ' caractères)');
            
            // Utiliser l'API RÉELLE pour analyser le texte
            const results = await this.jobParserAPI.parseJobText(text);
            
            console.log('📊 Résultats d\'analyse:', results);
            
            this.displayResults(results);
            this.showNotification('success', 'Analyse terminée', 'Les informations ont été extraites avec succès.');
            
        } catch (error) {
            console.error('❌ Erreur lors de l\'analyse du texte:', error);
            this.showNotification('error', 'Erreur d\'analyse', 'Impossible d\'analyser le texte: ' + error.message);
        } finally {
            this.hideLoader();
        }
    }
    
    // === EXTRACTEURS DE TEXTE PAR TYPE DE FICHIER ===
    
    async extractTextFromPDF(file) {
        if (!window.pdfjsLib) {
            throw new Error('PDF.js non chargé. Veuillez recharger la page.');
        }
        
        try {
            return await this.pdfCleaner.extractTextFromPDF(file);
        } catch (error) {
            console.error('Erreur extraction PDF:', error);
            throw new Error('Impossible d\'extraire le texte du PDF: ' + error.message);
        }
    }
    
    async extractTextFromDOCX(file) {
        // Utiliser mammoth.js pour les fichiers DOCX
        if (window.mammoth) {
            try {
                const arrayBuffer = await this.readFileAsArrayBuffer(file);
                const result = await mammoth.extractRawText({ arrayBuffer });
                return result.value;
            } catch (error) {
                throw new Error('Erreur lors de la lecture du fichier DOCX: ' + error.message);
            }
        } else {
            // Fallback: essayer de le lire comme texte (peut marcher partiellement)
            console.warn('mammoth.js non disponible, tentative de lecture comme texte');
            return await this.readFileAsText(file);
        }
    }
    
    async extractTextFromDOC(file) {
        // Les fichiers .doc sont plus complexes, on essaie une lecture basique
        console.warn('Fichiers .doc non entièrement supportés, résultats partiels possibles');
        return await this.readFileAsText(file);
    }
    
    async extractTextFromTXT(file) {
        return await this.readFileAsText(file);
    }
    
    // === UTILITAIRES DE LECTURE DE FICHIERS ===
    
    readFileAsArrayBuffer(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => resolve(e.target.result);
            reader.onerror = (e) => reject(new Error('Erreur de lecture: ' + e.target.error));
            reader.readAsArrayBuffer(file);
        });
    }
    
    readFileAsText(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => resolve(e.target.result);
            reader.onerror = (e) => reject(new Error('Erreur de lecture: ' + e.target.error));
            reader.readAsText(file, 'UTF-8');
        });
    }
    
    // === AFFICHAGE DES RÉSULTATS ===
    
    displayResults(results) {
        if (!this.resultsContainer) return;
        
        console.log('📋 Affichage des résultats:', results);
        
        // Afficher le conteneur de résultats
        this.resultsContainer.style.display = 'block';
        
        // Remplir les champs avec les VRAIES données
        this.setFieldValue('job-title-value', results.title || 'Non spécifié');
        this.setFieldValue('job-contract-value', results.contract_type || 'Non spécifié');
        this.setFieldValue('job-location-value', results.location || 'Non spécifié');
        this.setFieldValue('job-experience-value', results.experience || 'Non spécifié');
        this.setFieldValue('job-education-value', results.education || 'Non spécifié');
        this.setFieldValue('job-salary-value', results.salary || 'Non spécifié');
        
        // Responsabilités (array ou string)
        if (results.responsibilities && Array.isArray(results.responsibilities) && results.responsibilities.length > 0) {
            this.setFieldValue('job-responsibilities-value', results.responsibilities.join('\n• '));
        } else if (results.responsibilities) {
            this.setFieldValue('job-responsibilities-value', results.responsibilities);
        } else {
            this.setFieldValue('job-responsibilities-value', 'Non spécifié');
        }
        
        // Avantages (array ou string)
        if (results.benefits && Array.isArray(results.benefits) && results.benefits.length > 0) {
            this.setFieldValue('job-benefits-value', results.benefits.join(', '));
        } else if (results.benefits) {
            this.setFieldValue('job-benefits-value', results.benefits);
        } else {
            this.setFieldValue('job-benefits-value', 'Non spécifié');
        }
        
        // Afficher les compétences
        this.displaySkills(results.skills || []);
        
        // Scroll vers les résultats
        this.resultsContainer.scrollIntoView({ behavior: 'smooth' });
    }
    
    setFieldValue(fieldId, value) {
        const field = document.getElementById(fieldId);
        if (field) {
            field.textContent = value || 'Non spécifié';
        }
    }
    
    displaySkills(skills) {
        const skillsContainer = document.getElementById('job-skills-value');
        if (!skillsContainer) return;
        
        if (skills && Array.isArray(skills) && skills.length > 0) {
            skillsContainer.innerHTML = '';
            skills.forEach(skill => {
                const tag = document.createElement('span');
                tag.className = 'tag';
                tag.textContent = skill;
                skillsContainer.appendChild(tag);
            });
        } else {
            skillsContainer.textContent = 'Non spécifié';
        }
    }
    
    // === UTILITAIRES UI ===
    
    showLoader() {
        if (this.loader) {
            this.loader.style.display = 'flex';
        }
    }
    
    hideLoader() {
        if (this.loader) {
            this.loader.style.display = 'none';
        }
    }
    
    hideResults() {
        if (this.resultsContainer) {
            this.resultsContainer.style.display = 'none';
        }
    }
    
    showNotification(type, title, message) {
        // Utilise la fonction de notification du script principal
        if (window.questionnaireNav) {
            window.questionnaireNav.showNotification(type, title, message);
        } else {
            console.log(`${type.toUpperCase()}: ${title} - ${message}`);
        }
    }
}

// === BIBLIOTHÈQUE MAMMOTH.JS POUR DOCX (lightweight) ===
// Ajouter mammoth.js depuis CDN si pas déjà présent
if (!window.mammoth) {
    const script = document.createElement('script');
    script.src = 'https://cdnjs.cloudflare.com/ajax/libs/mammoth/1.6.0/mammoth.browser.min.js';
    script.onload = () => {
        console.log('📚 mammoth.js chargé pour les fichiers DOCX');
    };
    script.onerror = () => {
        console.warn('⚠️ mammoth.js non chargé, support DOCX limité');
    };
    document.head.appendChild(script);
}

// Initialiser l'UI de parsing FONCTIONNEL quand le DOM est prêt
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(() => {
        // S'assurer que JobParserAPI est disponible
        if (window.JobParserAPI && window.PDFCleaner) {
            window.jobParsingUI = new JobParsingUI();
            console.log('🎉 Job Parser FONCTIONNEL initialisé avec API réelle !');
        } else {
            console.error('❌ JobParserAPI ou PDFCleaner non disponibles');
            // Retry après un délai
            setTimeout(() => {
                if (window.JobParserAPI && window.PDFCleaner) {
                    window.jobParsingUI = new JobParsingUI();
                    console.log('🎉 Job Parser FONCTIONNEL initialisé (retry réussi) !');
                }
            }, 1000);
        }
    }, 500);
});

// Export pour utilisation dans d'autres scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = JobParsingUI;
}