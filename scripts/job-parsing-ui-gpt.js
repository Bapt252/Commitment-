// Job Parser UI Integration avec ChatGPT
// Remplace le système existant par une intégration ChatGPT

class JobParserUIIntegration {
    constructor() {
        this.gptParser = null;
        this.currentFile = null;
        
        // Éléments DOM existants
        this.fileInput = document.getElementById('job-file-input');
        this.dropZone = document.getElementById('job-drop-zone');
        this.textArea = document.getElementById('job-description-text');
        this.analyzeButton = document.getElementById('analyze-job-text');
        this.loader = document.getElementById('analysis-loader');
        this.resultsContainer = document.getElementById('job-info-container');
        this.fileBadge = document.getElementById('file-badge');
        this.fileName = document.getElementById('file-name');
        this.removeFileBtn = document.getElementById('remove-file');
        
        this.init();
    }
    
    init() {
        if (!this.dropZone) {
            console.error('❌ Éléments DOM du job parser non trouvés');
            return;
        }
        
        // Initialiser le parser GPT
        this.initGPTParser();
        
        // Créer l'interface de configuration API
        this.createApiConfigUI();
        
        // Configurer les événements existants
        this.setupFileUpload();
        this.setupTextAnalysis();
        this.setupFileRemoval();
        
        console.log('✅ Job Parser ChatGPT UI initialisé');
    }
    
    initGPTParser() {
        if (window.JobParserGPT) {
            this.gptParser = new window.JobParserGPT({ debug: true });
        } else {
            console.error('❌ JobParserGPT non disponible');
            return;
        }
    }
    
    // ===== INTERFACE CONFIGURATION API =====
    
    createApiConfigUI() {
        // Créer la section de configuration s'il n'existe pas
        let configSection = document.getElementById('gpt-config-section');
        
        if (!configSection) {
            configSection = document.createElement('div');
            configSection.id = 'gpt-config-section';
            configSection.className = 'api-config-section';
            
            const configHTML = `
                <div class="config-card">
                    <h4><i class="fas fa-key"></i> Configuration ChatGPT</h4>
                    <div class="config-content">
                        <div class="api-key-group">
                            <label for="openai-api-key">Clé API OpenAI :</label>
                            <div class="input-group">
                                <input type="password" id="openai-api-key" placeholder="sk-..." class="form-control">
                                <button type="button" id="save-api-key" class="btn btn-sm btn-primary">
                                    <i class="fas fa-save"></i> Sauvegarder
                                </button>
                                <button type="button" id="test-api-key" class="btn btn-sm btn-outline" style="display: none;">
                                    <i class="fas fa-check"></i> Tester
                                </button>
                            </div>
                            <small class="help-text">
                                Votre clé API OpenAI pour l'analyse intelligente. 
                                <a href="https://platform.openai.com/api-keys" target="_blank">Obtenir une clé API</a>
                            </small>
                        </div>
                        <div id="api-status" class="api-status"></div>
                    </div>
                </div>
            `;
            
            configSection.innerHTML = configHTML;
            
            // Insérer avant les instructions de parsing
            const instructions = document.querySelector('.parsing-instructions');
            if (instructions) {
                instructions.parentNode.insertBefore(configSection, instructions);
            }
        }
        
        // Ajouter les styles CSS
        this.addConfigStyles();
        
        // Configurer les événements
        this.setupApiConfigEvents();
        
        // Charger la clé API existante
        this.loadExistingApiKey();
    }
    
    addConfigStyles() {
        if (document.getElementById('job-parser-config-styles')) return;
        
        const styles = document.createElement('style');
        styles.id = 'job-parser-config-styles';
        styles.textContent = `
            .api-config-section {
                background: linear-gradient(135deg, #f8fafc, #e2e8f0);
                border: 2px solid #3b82f6;
                border-radius: 12px;
                padding: 20px;
                margin: 20px 0;
                box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
            }
            
            .config-card h4 {
                color: #1e40af;
                margin-bottom: 15px;
                display: flex;
                align-items: center;
                gap: 8px;
                font-size: 1.1rem;
            }
            
            .api-key-group {
                margin-bottom: 15px;
            }
            
            .api-key-group label {
                display: block;
                margin-bottom: 5px;
                font-weight: 500;
                color: #374151;
            }
            
            .input-group {
                display: flex;
                gap: 8px;
                align-items: center;
                margin-bottom: 5px;
            }
            
            .input-group input {
                flex: 1;
                min-width: 200px;
            }
            
            .btn-sm {
                padding: 6px 12px;
                font-size: 0.85rem;
            }
            
            .help-text {
                color: #6b7280;
                font-size: 0.85rem;
                line-height: 1.4;
            }
            
            .help-text a {
                color: #3b82f6;
                text-decoration: none;
            }
            
            .help-text a:hover {
                text-decoration: underline;
            }
            
            .api-status {
                padding: 10px;
                border-radius: 6px;
                font-size: 0.9rem;
                display: none;
            }
            
            .api-status.success {
                background-color: #d1fae5;
                color: #065f46;
                border: 1px solid #a7f3d0;
                display: block;
            }
            
            .api-status.error {
                background-color: #fee2e2;
                color: #991b1b;
                border: 1px solid #fca5a5;
                display: block;
            }
            
            .api-status.info {
                background-color: #dbeafe;
                color: #1e40af;
                border: 1px solid #93c5fd;
                display: block;
            }
        `;
        
        document.head.appendChild(styles);
    }
    
    setupApiConfigEvents() {
        const apiKeyInput = document.getElementById('openai-api-key');
        const saveBtn = document.getElementById('save-api-key');
        const testBtn = document.getElementById('test-api-key');
        
        if (saveBtn) {
            saveBtn.addEventListener('click', () => this.saveApiKey());
        }
        
        if (testBtn) {
            testBtn.addEventListener('click', () => this.testApiKey());
        }
        
        if (apiKeyInput) {
            apiKeyInput.addEventListener('input', () => {
                const hasKey = apiKeyInput.value.trim().length > 0;
                if (testBtn) {
                    testBtn.style.display = hasKey ? 'inline-block' : 'none';
                }
            });
        }
    }
    
    loadExistingApiKey() {
        if (this.gptParser && this.gptParser.hasApiKey()) {
            const apiKeyInput = document.getElementById('openai-api-key');
            if (apiKeyInput) {
                const storedKey = this.gptParser.getStoredApiKey();
                if (storedKey) {
                    apiKeyInput.value = storedKey;
                    this.showApiStatus('success', '✅ Clé API chargée');
                    
                    const testBtn = document.getElementById('test-api-key');
                    if (testBtn) {
                        testBtn.style.display = 'inline-block';
                    }
                }
            }
        }
    }
    
    async saveApiKey() {
        const apiKeyInput = document.getElementById('openai-api-key');
        if (!apiKeyInput) return;
        
        const apiKey = apiKeyInput.value.trim();
        
        if (!apiKey) {
            this.showApiStatus('error', '❌ Veuillez saisir une clé API');
            return;
        }
        
        if (!apiKey.startsWith('sk-')) {
            this.showApiStatus('error', '❌ Format de clé API invalide (doit commencer par sk-)');
            return;
        }
        
        try {
            this.gptParser.setApiKey(apiKey);
            this.showApiStatus('success', '✅ Clé API sauvegardée avec succès');
            
            const testBtn = document.getElementById('test-api-key');
            if (testBtn) {
                testBtn.style.display = 'inline-block';
            }
        } catch (error) {
            this.showApiStatus('error', '❌ Erreur lors de la sauvegarde: ' + error.message);
        }
    }
    
    async testApiKey() {
        if (!this.gptParser || !this.gptParser.hasApiKey()) {
            this.showApiStatus('error', '❌ Clé API non configurée');
            return;
        }
        
        this.showApiStatus('info', '🔄 Test de la connexion en cours...');
        
        try {
            await this.gptParser.testConnection();
            this.showApiStatus('success', '✅ Connexion ChatGPT réussie ! Parser prêt à utiliser.');
        } catch (error) {
            this.showApiStatus('error', '❌ Échec du test: ' + error.message);
        }
    }
    
    showApiStatus(type, message) {
        const statusDiv = document.getElementById('api-status');
        if (statusDiv) {
            statusDiv.className = `api-status ${type}`;
            statusDiv.textContent = message;
            
            // Auto-hide après 5 secondes pour les succès
            if (type === 'success') {
                setTimeout(() => {
                    statusDiv.style.display = 'none';
                }, 5000);
            }
        }
    }
    
    // ===== GESTION DES FICHIERS =====
    
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
    
    handleFileSelection(file) {
        // Vérifier le type de fichier
        const allowedTypes = [
            'application/pdf', 
            'application/msword', 
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 
            'text/plain'
        ];
        
        if (!allowedTypes.includes(file.type)) {
            this.showNotification('error', 'Type de fichier non supporté', 
                'Veuillez sélectionner un fichier PDF, DOCX ou TXT.');
            return;
        }
        
        // Vérifier la taille (5MB max)
        if (file.size > 5 * 1024 * 1024) {
            this.showNotification('error', 'Fichier trop volumineux', 
                'La taille du fichier ne doit pas dépasser 5MB.');
            return;
        }
        
        // Sauvegarder le fichier et afficher
        this.currentFile = file;
        this.showSelectedFile(file);
        
        // Analyser le fichier avec ChatGPT
        this.analyzeFile(file);
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
        this.currentFile = null;
        
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
    
    // ===== ANALYSE AVEC CHATGPT =====
    
    async analyzeFile(file) {
        if (!this.checkGPTReady()) return;
        
        this.showLoader('Extraction du contenu et analyse ChatGPT...');
        
        try {
            const result = await this.gptParser.parseJobFile(file);
            this.displayResults(result);
            this.hideLoader();
            
            this.showNotification('success', 'Analyse réussie', 
                'Les informations ont été extraites avec ChatGPT.');
        } catch (error) {
            this.hideLoader();
            console.error('Erreur analyse fichier:', error);
            this.showNotification('error', 'Erreur d\'analyse', 
                'Impossible d\'analyser le fichier: ' + error.message);
        }
    }
    
    async analyzeJobText(text) {
        if (!this.checkGPTReady()) return;
        
        this.showLoader('Analyse ChatGPT en cours...');
        
        try {
            const result = await this.gptParser.parseJobText(text);
            this.displayResults(result);
            this.hideLoader();
            
            this.showNotification('success', 'Analyse réussie', 
                'Les informations ont été extraites avec ChatGPT.');
        } catch (error) {
            this.hideLoader();
            console.error('Erreur analyse texte:', error);
            this.showNotification('error', 'Erreur d\'analyse', 
                'Impossible d\'analyser le texte: ' + error.message);
        }
    }
    
    checkGPTReady() {
        if (!this.gptParser) {
            this.showNotification('error', 'Parser non initialisé', 
                'Le parser ChatGPT n\'est pas disponible.');
            return false;
        }
        
        if (!this.gptParser.hasApiKey()) {
            this.showNotification('error', 'Clé API requise', 
                'Veuillez configurer votre clé API OpenAI.');
            return false;
        }
        
        return true;
    }
    
    // ===== AFFICHAGE DES RÉSULTATS =====
    
    displayResults(results) {
        if (!this.resultsContainer) return;
        
        // Afficher le conteneur de résultats
        this.resultsContainer.style.display = 'block';
        
        // Remplir les champs avec les résultats ChatGPT
        this.setFieldValue('job-title-value', results.title);
        this.setFieldValue('job-contract-value', results.contract_type);
        this.setFieldValue('job-location-value', results.location);
        this.setFieldValue('job-experience-value', results.experience);
        this.setFieldValue('job-education-value', results.education);
        this.setFieldValue('job-salary-value', results.salary);
        this.setFieldValue('job-responsibilities-value', results.responsibilities);
        this.setFieldValue('job-benefits-value', results.benefits);
        
        // Afficher les compétences avec tags
        this.displaySkills(results.skills);
        
        // Ajouter info sur la source
        this.addGPTAttribution();
        
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
        
        if (skills && skills.length > 0) {
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
    
    addGPTAttribution() {
        // Ajouter une petite indication que l'analyse a été faite par ChatGPT
        const existingAttribution = this.resultsContainer.querySelector('.gpt-attribution');
        if (existingAttribution) return;
        
        const attribution = document.createElement('div');
        attribution.className = 'gpt-attribution';
        attribution.style.cssText = `
            margin-top: 15px;
            padding: 8px 12px;
            background-color: #f0f9ff;
            border: 1px solid #0ea5e9;
            border-radius: 6px;
            font-size: 0.85rem;
            color: #0c4a6e;
            text-align: center;
        `;
        attribution.innerHTML = '<i class="fas fa-robot"></i> Analyse réalisée par ChatGPT';
        
        this.resultsContainer.appendChild(attribution);
    }
    
    // ===== UTILITAIRES =====
    
    showLoader(text = 'Analyse ChatGPT en cours...') {
        if (this.loader) {
            this.loader.style.display = 'flex';
            const loaderText = this.loader.querySelector('.loader-text');
            if (loaderText) {
                loaderText.textContent = text;
            }
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
        if (window.questionnaireNav && window.questionnaireNav.showNotification) {
            window.questionnaireNav.showNotification(type, title, message);
        } else {
            console.log(`${type.toUpperCase()}: ${title} - ${message}`);
        }
    }
}

// ===== INITIALISATION =====

// Attendre que le DOM soit prêt et que JobParserGPT soit chargé
document.addEventListener('DOMContentLoaded', function() {
    // Petit délai pour s'assurer que tous les scripts sont chargés
    setTimeout(() => {
        // Remplacer l'ancienne instance
        if (window.jobParsingUI) {
            console.log('🔄 Remplacement de l\'ancien Job Parsing UI...');
        }
        
        // Créer la nouvelle instance avec ChatGPT
        window.jobParsingUIGPT = new JobParserUIIntegration();
        
        console.log('🤖 Job Parser ChatGPT UI initialisé et prêt !');
    }, 500);
});

// Export pour utilisation dans d'autres scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = JobParserUIIntegration;
}