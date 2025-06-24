// job-parser-integration.js
// Script d'intégration pour connecter tous les composants du Job Parser

class JobParserIntegration {
    constructor() {
        this.isInitialized = false;
        this.debugMode = true;
        this.init();
    }
    
    async init() {
        console.log('🔧 Initialisation de l\'intégration Job Parser...');
        
        // Attendre que tous les scripts soient chargés
        await this.waitForDependencies();
        
        // Configurer les instances globales
        this.setupGlobalInstances();
        
        // Connecter les événements
        this.connectEvents();
        
        // Afficher les fonctions de diagnostic
        this.setupDiagnostics();
        
        this.isInitialized = true;
        console.log('✅ Intégration Job Parser complète !');
    }
    
    async waitForDependencies() {
        const maxAttempts = 50;
        let attempts = 0;
        
        while (attempts < maxAttempts) {
            const hasJobParserAPI = typeof window.JobParserAPI === 'function';
            const hasPDFCleaner = typeof window.PDFCleaner === 'function';
            const hasPDFJS = typeof window.pdfjsLib === 'object';
            
            if (hasJobParserAPI && hasPDFCleaner && hasPDFJS) {
                console.log('📚 Toutes les dépendances sont chargées');
                return true;
            }
            
            if (this.debugMode) {
                console.log(`⏳ Attente des dépendances... (${attempts + 1}/${maxAttempts})`);
                console.log('  - JobParserAPI:', hasJobParserAPI);
                console.log('  - PDFCleaner:', hasPDFCleaner);
                console.log('  - PDF.js:', hasPDFJS);
            }
            
            await this.sleep(100);
            attempts++;
        }
        
        throw new Error('Timeout: Dépendances non chargées après ' + maxAttempts + ' tentatives');
    }
    
    setupGlobalInstances() {
        // Configuration PDF.js
        if (window.pdfjsLib) {
            window.pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
            console.log('🔧 PDF.js worker configuré');
        }
        
        // Instance globale du parser avec debug
        window.globalJobParser = new JobParserAPI({ 
            debug: this.debugMode,
            enablePDFCleaning: true 
        });
        
        // Instance globale du PDF cleaner
        window.globalPDFCleaner = new PDFCleaner();
        
        console.log('🌐 Instances globales créées');
    }
    
    connectEvents() {
        // Connecter les boutons si pas déjà fait
        this.connectAnalyzeButtons();
        
        // Event pour le changement de texte
        const textArea = document.getElementById('job-description-text');
        if (textArea) {
            textArea.addEventListener('input', this.onTextChange.bind(this));
        }
        
        // Event pour changement de fichier
        const fileInput = document.getElementById('job-file-input');
        if (fileInput) {
            fileInput.addEventListener('change', this.onFileChange.bind(this));
        }
    }
    
    connectAnalyzeButtons() {
        // Bouton d'analyse principal (rond à côté du textarea)
        const analyzeBtn = document.getElementById('analyze-job-text');
        if (analyzeBtn) {
            // Supprimer les anciens listeners pour éviter les doublons
            analyzeBtn.replaceWith(analyzeBtn.cloneNode(true));
            const newAnalyzeBtn = document.getElementById('analyze-job-text');
            
            newAnalyzeBtn.addEventListener('click', async () => {
                await this.performRealAnalysis();
            });
            
            console.log('🔗 Bouton d\'analyse principal connecté');
        }
        
        // Bouton GPT (si présent)
        const gptBtn = document.getElementById('analyze-with-gpt');
        if (gptBtn) {
            gptBtn.addEventListener('click', async () => {
                await this.performRealAnalysis(); // Même analyse pour l'instant
            });
        }
    }
    
    async performRealAnalysis() {
        const textArea = document.getElementById('job-description-text');
        const fileInput = document.getElementById('job-file-input');
        const loader = document.getElementById('analysis-loader');
        
        // Vérifier qu'on a quelque chose à analyser
        const hasText = textArea && textArea.value.trim();
        const hasFile = fileInput && fileInput.files.length > 0;
        
        if (!hasText && !hasFile) {
            this.showNotification('error', 'Aucun contenu', 'Veuillez saisir du texte ou sélectionner un fichier');
            return;
        }
        
        // Afficher le loader
        if (loader) loader.style.display = 'flex';
        
        try {
            let results;
            
            if (hasFile) {
                // Analyser le fichier
                const file = fileInput.files[0];
                console.log('📄 Analyse du fichier:', file.name);
                
                let extractedText = '';
                
                switch (file.type) {
                    case 'application/pdf':
                        extractedText = await this.extractPDFText(file);
                        break;
                    case 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                        extractedText = await this.extractDOCXText(file);
                        break;
                    case 'text/plain':
                        extractedText = await this.extractTextFile(file);
                        break;
                    default:
                        throw new Error('Type de fichier non supporté: ' + file.type);
                }
                
                if (extractedText.trim()) {
                    results = await window.globalJobParser.parseJobText(extractedText);
                } else {
                    throw new Error('Aucun texte extractible du fichier');
                }
                
            } else {
                // Analyser le texte
                console.log('📝 Analyse du texte saisi');
                results = await window.globalJobParser.parseJobText(textArea.value);
            }
            
            // Afficher les résultats
            this.displayJobResults(results);
            this.showNotification('success', 'Analyse réussie', 'Informations extraites avec succès !');
            
        } catch (error) {
            console.error('❌ Erreur d\'analyse:', error);
            this.showNotification('error', 'Erreur d\'analyse', error.message);
        } finally {
            // Cacher le loader
            if (loader) loader.style.display = 'none';
        }
    }
    
    async extractPDFText(file) {
        console.log('📑 Extraction PDF...');
        return await window.globalPDFCleaner.extractTextFromPDF(file);
    }
    
    async extractDOCXText(file) {
        console.log('📄 Extraction DOCX...');
        
        if (window.mammoth) {
            const arrayBuffer = await this.readFileAsArrayBuffer(file);
            const result = await mammoth.extractRawText({ arrayBuffer });
            return result.value;
        } else {
            // Fallback
            console.warn('mammoth.js non disponible');
            return await this.readFileAsText(file);
        }
    }
    
    async extractTextFile(file) {
        console.log('📋 Extraction TXT...');
        return await this.readFileAsText(file);
    }
    
    readFileAsArrayBuffer(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = e => resolve(e.target.result);
            reader.onerror = e => reject(new Error('Erreur de lecture: ' + e.target.error));
            reader.readAsArrayBuffer(file);
        });
    }
    
    readFileAsText(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = e => resolve(e.target.result);
            reader.onerror = e => reject(new Error('Erreur de lecture: ' + e.target.error));
            reader.readAsText(file, 'UTF-8');
        });
    }
    
    displayJobResults(results) {
        console.log('📊 Affichage des résultats:', results);
        
        const container = document.getElementById('job-info-container');
        if (!container) {
            console.error('Container de résultats non trouvé');
            return;
        }
        
        // Afficher le container
        container.style.display = 'block';
        
        // Mapper les champs
        const fieldMappings = {
            'job-title-value': results.title,
            'job-contract-value': results.contract_type,
            'job-location-value': results.location,
            'job-experience-value': results.experience,
            'job-education-value': results.education,
            'job-salary-value': results.salary,
        };
        
        // Remplir les champs simples
        Object.entries(fieldMappings).forEach(([fieldId, value]) => {
            const field = document.getElementById(fieldId);
            if (field) {
                field.textContent = value || 'Non spécifié';
            }
        });
        
        // Responsabilités (array ou string)
        const responsibilitiesField = document.getElementById('job-responsibilities-value');
        if (responsibilitiesField) {
            if (Array.isArray(results.responsibilities) && results.responsibilities.length > 0) {
                responsibilitiesField.textContent = '• ' + results.responsibilities.join('\n• ');
            } else {
                responsibilitiesField.textContent = results.responsibilities || 'Non spécifié';
            }
        }
        
        // Avantages (array ou string)
        const benefitsField = document.getElementById('job-benefits-value');
        if (benefitsField) {
            if (Array.isArray(results.benefits) && results.benefits.length > 0) {
                benefitsField.textContent = results.benefits.join(', ');
            } else {
                benefitsField.textContent = results.benefits || 'Non spécifié';
            }
        }
        
        // Compétences avec tags
        this.displaySkillTags(results.skills || []);
        
        // Scroll vers les résultats
        container.scrollIntoView({ behavior: 'smooth' });
    }
    
    displaySkillTags(skills) {
        const skillsContainer = document.getElementById('job-skills-value');
        if (!skillsContainer) return;
        
        skillsContainer.innerHTML = '';
        
        if (Array.isArray(skills) && skills.length > 0) {
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
    
    onTextChange(event) {
        const text = event.target.value.trim();
        const analyzeBtn = document.getElementById('analyze-job-text');
        
        // Mettre à jour l'état du bouton
        if (analyzeBtn) {
            analyzeBtn.style.opacity = text ? '1' : '0.5';
        }
    }
    
    onFileChange(event) {
        const file = event.target.files[0];
        console.log('📁 Fichier sélectionné:', file ? file.name : 'aucun');
    }
    
    showNotification(type, title, message) {
        if (window.questionnaireNav && window.questionnaireNav.showNotification) {
            window.questionnaireNav.showNotification(type, title, message);
        } else {
            // Fallback simple
            const logType = type === 'error' ? 'error' : 'log';
            console[logType](`${title}: ${message}`);
            
            // Fallback UI simple
            alert(`${title}: ${message}`);
        }
    }
    
    setupDiagnostics() {
        // Fonctions de diagnostic globales
        window.testJobParser = () => {
            console.log('🧪 Test du Job Parser...');
            
            const testText = `
            Intitulé du poste : Développeur Full Stack
            
            Nous recherchons un développeur expérimenté pour rejoindre notre équipe.
            
            Compétences requises :
            - JavaScript, React, Node.js
            - 3-5 ans d'expérience
            - Niveau Master en informatique
            
            Localisation : Paris
            Type de contrat : CDI
            Rémunération : 45k€ - 55k€
            `;
            
            return window.globalJobParser.parseJobText(testText);
        };
        
        window.debugJobParser = () => {
            console.log('🔍 Debug Job Parser:');
            console.log('- JobParserAPI disponible:', !!window.JobParserAPI);
            console.log('- PDFCleaner disponible:', !!window.PDFCleaner);
            console.log('- PDF.js disponible:', !!window.pdfjsLib);
            console.log('- Mammoth.js disponible:', !!window.mammoth);
            console.log('- Integration initialisée:', this.isInitialized);
            console.log('- Instance globale parser:', !!window.globalJobParser);
        };
        
        console.log('🛠️ Fonctions de diagnostic ajoutées:');
        console.log('  - testJobParser() : tester l\'analyse');
        console.log('  - debugJobParser() : vérifier les dépendances');
    }
    
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Initialiser l'intégration
document.addEventListener('DOMContentLoaded', () => {
    // Attendre un peu que tous les scripts se chargent
    setTimeout(() => {
        window.jobParserIntegration = new JobParserIntegration();
    }, 800);
});

// Export
if (typeof module !== 'undefined' && module.exports) {
    module.exports = JobParserIntegration;
}