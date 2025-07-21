// Diagnostic ChatGPT Détaillé - Identifier pourquoi l'extraction ne fonctionne pas
// Ce script va diagnostiquer tous les aspects du système ChatGPT

class ChatGPTDiagnostic {
    constructor() {
        this.results = [];
        this.errors = [];
    }
    
    log(message, type = 'info') {
        const timestamp = new Date().toLocaleTimeString();
        const logEntry = `[${timestamp}] ${type.toUpperCase()}: ${message}`;
        
        if (type === 'error') {
            this.errors.push(logEntry);
            console.error(logEntry);
        } else {
            this.results.push(logEntry);
            console.log(logEntry);
        }
    }
    
    async runFullDiagnostic() {
        console.clear();
        console.log('🔍 DIAGNOSTIC CHATGPT DÉTAILLÉ - DÉMARRAGE');
        console.log('================================================');
        
        // 1. Vérifier l'existence des classes et instances
        this.checkClassesAndInstances();
        
        // 2. Vérifier la configuration API
        this.checkApiConfiguration();
        
        // 3. Vérifier les éléments DOM
        this.checkDOMElements();
        
        // 4. Vérifier les event listeners
        this.checkEventListeners();
        
        // 5. Test de connexion API
        await this.testApiConnection();
        
        // 6. Test d'analyse complète
        await this.testFullAnalysis();
        
        // 7. Afficher le rapport final
        this.displayFinalReport();
    }
    
    checkClassesAndInstances() {
        this.log('=== 1. VÉRIFICATION DES CLASSES ET INSTANCES ===');
        
        // Vérifier JobParserGPT
        if (window.JobParserGPT) {
            this.log('✅ JobParserGPT classe disponible');
        } else {
            this.log('❌ JobParserGPT classe MANQUANTE', 'error');
        }
        
        // Vérifier JobParserUIIntegration
        if (window.JobParserUIIntegration) {
            this.log('✅ JobParserUIIntegration classe disponible');
        } else {
            this.log('❌ JobParserUIIntegration classe MANQUANTE', 'error');
        }
        
        // Vérifier l'instance ChatGPT
        if (window.jobParsingUIGPT) {
            this.log('✅ Instance jobParsingUIGPT créée');
            
            if (window.jobParsingUIGPT.gptParser) {
                this.log('✅ Parser GPT initialisé');
            } else {
                this.log('❌ Parser GPT NON initialisé', 'error');
            }
        } else {
            this.log('❌ Instance jobParsingUIGPT MANQUANTE', 'error');
        }
        
        // Vérifier l'ancien système
        if (window.jobParsingUI) {
            this.log('⚠️ Ancien système jobParsingUI encore présent (conflit possible)', 'error');
        } else {
            this.log('✅ Ancien système correctement désactivé');
        }
    }
    
    checkApiConfiguration() {
        this.log('=== 2. VÉRIFICATION CONFIGURATION API ===');
        
        // Vérifier le champ de saisie de clé API
        const apiKeyInput = document.getElementById('openai-api-key');
        if (apiKeyInput) {
            this.log('✅ Champ clé API trouvé');
            
            if (apiKeyInput.value && apiKeyInput.value.trim().length > 0) {
                this.log('✅ Clé API saisie dans le champ');
                this.log(`📝 Longueur clé: ${apiKeyInput.value.length} caractères`);
                
                if (apiKeyInput.value.startsWith('sk-')) {
                    this.log('✅ Format clé API correct (commence par sk-)');
                } else {
                    this.log('❌ Format clé API incorrect (doit commencer par sk-)', 'error');
                }
            } else {
                this.log('❌ Aucune clé API saisie', 'error');
            }
        } else {
            this.log('❌ Champ clé API introuvable', 'error');
        }
        
        // Vérifier le stockage local
        try {
            const storedKey = localStorage.getItem('openai_api_key_jobparser');
            if (storedKey) {
                this.log('✅ Clé API trouvée dans localStorage');
                this.log(`📝 Longueur clé stockée: ${storedKey.length} caractères`);
            } else {
                this.log('❌ Aucune clé API en localStorage', 'error');
            }
        } catch (e) {
            this.log('❌ Erreur accès localStorage: ' + e.message, 'error');
        }
        
        // Vérifier la configuration du parser
        if (window.jobParsingUIGPT && window.jobParsingUIGPT.gptParser) {
            const hasApiKey = window.jobParsingUIGPT.gptParser.hasApiKey();
            if (hasApiKey) {
                this.log('✅ Parser confirme avoir une clé API');
            } else {
                this.log('❌ Parser n\'a pas de clé API', 'error');
            }
        }
    }
    
    checkDOMElements() {
        this.log('=== 3. VÉRIFICATION ÉLÉMENTS DOM ===');
        
        const elementsToCheck = [
            'job-drop-zone',
            'job-file-input', 
            'job-description-text',
            'analyze-job-text',
            'analysis-loader',
            'job-info-container',
            'gpt-config-section'
        ];
        
        elementsToCheck.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                this.log(`✅ ${id} trouvé`);
            } else {
                this.log(`❌ ${id} MANQUANT`, 'error');
            }
        });
        
        // Vérifier les champs de résultats
        const resultFields = [
            'job-title-value',
            'job-contract-value', 
            'job-location-value',
            'job-skills-value'
        ];
        
        resultFields.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                this.log(`✅ Champ résultat ${id}: "${element.textContent}"`);
            } else {
                this.log(`❌ Champ résultat ${id} MANQUANT`, 'error');
            }
        });
    }
    
    checkEventListeners() {
        this.log('=== 4. VÉRIFICATION EVENT LISTENERS ===');
        
        const analyzeBtn = document.getElementById('analyze-job-text');
        if (analyzeBtn) {
            // Tester si le bouton répond au clic
            this.log('🧪 Test du bouton d\'analyse...');
            
            // Simuler un clic (sans déclencher l'analyse)
            const originalHandler = analyzeBtn.onclick;
            let hasHandler = false;
            
            // Vérifier s'il y a des event listeners
            const listeners = getEventListeners ? getEventListeners(analyzeBtn) : null;
            if (listeners && listeners.click && listeners.click.length > 0) {
                hasHandler = true;
                this.log(`✅ ${listeners.click.length} event listener(s) sur le bouton`);
            }
            
            if (originalHandler) {
                hasHandler = true;
                this.log('✅ Handler onclick détecté');
            }
            
            if (!hasHandler) {
                this.log('❌ Aucun event listener sur le bouton d\'analyse', 'error');
            }
        }
    }
    
    async testApiConnection() {
        this.log('=== 5. TEST CONNEXION API ===');
        
        if (!window.jobParsingUIGPT || !window.jobParsingUIGPT.gptParser) {
            this.log('❌ Impossible de tester - Parser non disponible', 'error');
            return;
        }
        
        const parser = window.jobParsingUIGPT.gptParser;
        
        if (!parser.hasApiKey()) {
            this.log('❌ Impossible de tester - Clé API manquante', 'error');
            return;
        }
        
        try {
            this.log('🔄 Test de connexion en cours...');
            const result = await parser.testConnection();
            this.log('✅ Test de connexion RÉUSSI');
            this.log(`📋 Résultat test: ${JSON.stringify(result, null, 2)}`);
        } catch (error) {
            this.log(`❌ Test de connexion ÉCHOUÉ: ${error.message}`, 'error');
            
            if (error.message.includes('401')) {
                this.log('💡 Erreur 401 = Clé API invalide', 'error');
            } else if (error.message.includes('429')) {
                this.log('💡 Erreur 429 = Quota dépassé', 'error');
            } else if (error.message.includes('network')) {
                this.log('💡 Erreur réseau - Vérifiez votre connexion', 'error');
            }
        }
    }
    
    async testFullAnalysis() {
        this.log('=== 6. TEST ANALYSE COMPLÈTE ===');
        
        if (!window.jobParsingUIGPT || !window.jobParsingUIGPT.gptParser) {
            this.log('❌ Impossible de tester - Parser non disponible', 'error');
            return;
        }
        
        const parser = window.jobParsingUIGPT.gptParser;
        
        if (!parser.hasApiKey()) {
            this.log('❌ Impossible de tester - Clé API manquante', 'error');
            return;
        }
        
        const testText = `Poste: Développeur Full Stack
Entreprise: TechCorp
Localisation: Paris, France  
Type de contrat: CDI
Expérience: 3-5 ans d'expérience
Formation: Master en informatique ou équivalent
Compétences techniques: JavaScript, React, Node.js, MongoDB, Git
Missions: 
- Développement d'applications web modernes
- Collaboration avec l'équipe design
- Maintenance et optimisation du code existant
- Participation aux réunions techniques
Rémunération: 50-60k€ selon profil
Avantages: 
- Télétravail hybride 2j/semaine
- Mutuelle prise en charge à 100%
- Tickets restaurant
- Formation continue`;
        
        try {
            this.log('🔄 Test d\'analyse en cours...');
            this.log(`📝 Texte test: ${testText.substring(0, 100)}...`);
            
            const result = await parser.parseJobText(testText);
            this.log('✅ Analyse RÉUSSIE');
            this.log(`📋 Résultat: ${JSON.stringify(result, null, 2)}`);
            
            // Vérifier que les données ne sont pas vides
            const filledFields = Object.keys(result).filter(key => 
                result[key] && result[key].toString().trim() !== '' && result[key] !== 'Non spécifié'
            );
            
            this.log(`📊 Champs extraits: ${filledFields.length}/10`);
            filledFields.forEach(field => {
                this.log(`  ✅ ${field}: ${result[field]}`);
            });
            
        } catch (error) {
            this.log(`❌ Analyse ÉCHOUÉE: ${error.message}`, 'error');
        }
    }
    
    displayFinalReport() {
        console.log('\n');
        console.log('================================================');
        console.log('📊 RAPPORT FINAL DU DIAGNOSTIC');
        console.log('================================================');
        
        if (this.errors.length === 0) {
            console.log('🎉 AUCUNE ERREUR DÉTECTÉE - Le système devrait fonctionner !');
        } else {
            console.log(`❌ ${this.errors.length} ERREUR(S) DÉTECTÉE(S):`);
            this.errors.forEach((error, index) => {
                console.log(`${index + 1}. ${error}`);
            });
        }
        
        console.log('\n💡 ACTIONS RECOMMANDÉES:');
        
        if (this.errors.some(e => e.includes('clé API'))) {
            console.log('1. 🔑 Configurer une clé API OpenAI valide');
            console.log('   - Aller sur https://platform.openai.com/api-keys');
            console.log('   - Créer une nouvelle clé (sk-...)');
            console.log('   - La saisir dans la section bleue de configuration');
        }
        
        if (this.errors.some(e => e.includes('MANQUANT'))) {
            console.log('2. 🔄 Recharger la page pour réinitialiser les scripts');
        }
        
        if (this.errors.some(e => e.includes('conflit'))) {
            console.log('3. 🧹 Nettoyer le cache du navigateur');
        }
        
        console.log('\n🛠️ FONCTIONS UTILES:');
        console.log('- diagnoseChatGPTParser() : Diagnostic rapide');
        console.log('- testChatGPTParser() : Test d\'analyse');
        console.log('- window.chatgptDiag.runFullDiagnostic() : Ce diagnostic complet');
    }
}

// Créer l'instance globale
window.chatgptDiag = new ChatGPTDiagnostic();

// Fonction de diagnostic rapide
window.diagnoseChatGPTParser = function() {
    window.chatgptDiag.runFullDiagnostic();
};

console.log('🔍 Diagnostic ChatGPT Détaillé chargé !');
console.log('💡 Utilisez diagnoseChatGPTParser() pour lancer le diagnostic complet');
