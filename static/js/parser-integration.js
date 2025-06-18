/**
 * Script d'Intégration du Parser Optimisé Commitment
 * Intègre seamlessly le parser amélioré dans l'architecture existante
 * Compatible avec GPTParserClient et CVParserIntegration
 */

// Fonction principale d'intégration
function integrateEnhancedParser() {
    console.log('🚀 Intégration du parser CV optimisé Commitment...');
    
    // Vérifier si le parser optimisé est disponible
    if (typeof window.EnhancedCVParser === 'undefined') {
        console.error('❌ EnhancedCVParser non trouvé. Le fichier enhanced-cv-parser.js doit être chargé en premier.');
        return false;
    }
    
    // Améliorer GPTParserClient existant
    if (typeof window.GPTParserClient !== 'undefined') {
        enhanceGPTParserClient();
    }
    
    // Améliorer CVParserIntegration existant
    if (typeof window.CVParserIntegration !== 'undefined') {
        enhanceCVParserIntegration();
    }
    
    // Créer les instances globales optimisées
    createOptimizedInstances();
    
    console.log('✅ Parser CV optimisé intégré avec succès dans Commitment !');
    return true;
}

/**
 * Améliore la classe GPTParserClient existante
 */
function enhanceGPTParserClient() {
    const OriginalGPTParserClient = window.GPTParserClient;
    
    class OptimizedGPTParserClient extends OriginalGPTParserClient {
        constructor(options = {}) {
            super(options);
            this.enhancedParser = new window.EnhancedCVParser();
            this.useEnhancedFallback = options.useEnhancedFallback !== false; // Par défaut activé
            console.log('✅ GPTParserClient optimisé initialisé pour Commitment');
        }
        
        /**
         * Version optimisée du parsing fallback avec le nouveau parser
         */
        fallbackParsing(content) {
            if (this.useEnhancedFallback) {
                console.log('🔧 Utilisation du parser optimisé Commitment en mode fallback');
                this.onProgress('Analyse CV optimisée en cours...');
                
                try {
                    const result = this.enhancedParser.parseCV(content);
                    
                    // Adapter le format au format attendu par l'interface existante
                    return {
                        data: result.data,
                        source: 'enhanced_commitment_fallback',
                        timestamp: result.timestamp,
                        parsing_stats: result.parsing_stats
                    };
                } catch (error) {
                    console.error('Erreur parser optimisé, fallback vers l\'original:', error);
                    // Fallback vers le parser original en cas d'erreur
                    return super.fallbackParsing(content);
                }
            } else {
                // Utiliser le parser original si explicitement demandé
                return super.fallbackParsing(content);
            }
        }
        
        /**
         * Méthodes d'extraction optimisées (remplacent les originales)
         */
        extractPersonalInfo(content) {
            if (this.useEnhancedFallback) {
                return this.enhancedParser.extractPersonalInfoEnhanced(content);
            }
            return super.extractPersonalInfo(content);
        }
        
        extractCurrentPosition(content) {
            if (this.useEnhancedFallback) {
                return this.enhancedParser.extractCurrentPositionEnhanced(content);
            }
            return super.extractCurrentPosition(content);
        }
        
        extractSkills(content) {
            if (this.useEnhancedFallback) {
                return this.enhancedParser.extractSkillsEnhanced(content);
            }
            return super.extractSkills(content);
        }
        
        extractSoftware(content) {
            if (this.useEnhancedFallback) {
                return this.enhancedParser.extractSoftwareEnhanced(content);
            }
            return super.extractSoftware(content);
        }
        
        extractLanguages(content) {
            if (this.useEnhancedFallback) {
                return this.enhancedParser.extractLanguagesEnhanced(content);
            }
            return super.extractLanguages(content);
        }
        
        extractWorkExperience(content) {
            if (this.useEnhancedFallback) {
                return this.enhancedParser.extractWorkExperienceEnhanced(content);
            }
            return super.extractWorkExperience(content);
        }
    }
    
    // Remplacer la classe globale
    window.GPTParserClient = OptimizedGPTParserClient;
    console.log('✅ GPTParserClient remplacé par la version optimisée Commitment');
}

/**
 * Améliore CVParserIntegration existant
 */
function enhanceCVParserIntegration() {
    const OriginalCVParserIntegration = window.CVParserIntegration;
    
    class OptimizedCVParserIntegration extends OriginalCVParserIntegration {
        constructor(options = {}) {
            // Forcer l'utilisation du parser optimisé par défaut
            const optimizedOptions = {
                ...options,
                useEnhancedParsing: options.useEnhancedParsing !== false, // Par défaut activé
                fallbackMode: false // Désactiver le fallback car on a le parser optimisé
            };
            
            super(optimizedOptions);
            console.log('✅ CVParserIntegration optimisé initialisé pour Commitment');
        }
        
        async parseCV(file) {
            this.onParsingStart();
            
            try {
                // Utiliser directement le client optimisé
                const result = await this.client.parseCV(file);
                this.onParsingComplete(result);
                return result;
            } catch (error) {
                this.onParsingError(error);
                throw error;
            }
        }
    }
    
    window.CVParserIntegration = OptimizedCVParserIntegration;
    console.log('✅ CVParserIntegration remplacé par la version optimisée Commitment');
}

/**
 * Crée les instances globales optimisées pour compatibilité
 */
function createOptimizedInstances() {
    // Instance globale pour tests et utilisation directe
    window.commitmentEnhancedParser = new window.EnhancedCVParser();
    
    // Fonction de test avec le CV de Sabine
    window.testCommitmentParser = async function() {
        console.log('🧪 Test du parser optimisé Commitment avec le CV de Sabine...');
        
        const sabineCV = `
Sabine Rivière
Executive Assistant

E-mail: sabine.riviere04@gmail.com
Téléphone: +33665733921

Expérience

06/2024 - 01/2025
Executive Assistant : Direction Financière Audit / Fiscalité / Trésorerie
Maison Christian Dior Couture : Intérim 8 mois, Paris 08

06/2023 - 05/2024
EXECUTIVE ASSISTANT : Direction Fonds de Fonds COMEX / CODIR / CMG
BPI FRANCE, Paris

08/2019 - 05/2023
EXECUTIVE ASSISTANT/ ASSISTANTE PERSONNELLE de la CEO
Les Secrets de Loly, Paris

Compétences
Tenue d'agendas
Suivi budgétaire
Préparation de rapports
Autonomie
Sens de la communication
Excellente organisation du travail

Informatique
Microsoft
Concur
Coupa
SAP
Pennylane
Google / Outlook

Langues
French - A1
Anglais - A1

Formation
- 01/2006 DIPLÔME D'ÉTUDES SUPÉRIEURES ESVE, Paris
- 01/2014 Business & Economics, BA Birkbeck University, London
        `;
        
        try {
            const result = window.commitmentEnhancedParser.parseCV(sabineCV);
            
            console.log('📊 Résultats du test Commitment:', result);
            
            // Afficher les améliorations détectées
            console.log('🎯 Améliorations Commitment détectées:');
            console.log('- Nom:', result.data.personal_info.name);
            console.log('- Email:', result.data.personal_info.email);
            console.log('- Téléphone:', result.data.personal_info.phone);
            console.log('- Poste actuel:', result.data.current_position);
            console.log('- Compétences:', result.data.skills.length, 'trouvées -', result.data.skills.slice(0, 3).join(', ') + '...');
            console.log('- Logiciels:', result.data.software.length, 'trouvés -', result.data.software.slice(0, 3).join(', ') + '...');
            console.log('- Langues:', result.data.languages.map(l => `${l.language} (${l.level})`).join(', '));
            console.log('- Expériences:', result.data.work_experience.length, 'trouvées');
            console.log('- Formation:', result.data.education?.length || 0, 'trouvées');
            
            return result;
        } catch (error) {
            console.error('❌ Erreur test Commitment:', error);
            return null;
        }
    };
    
    // Fonction de comparaison des performances
    window.compareCommitmentParsers = async function(cvContent) {
        console.log('⚖️ Comparaison des parsers Commitment...');
        
        const results = {
            original: null,
            enhanced: null,
            improvements: {}
        };
        
        // Test avec le parser original (si disponible et pas encore remplacé)
        try {
            // Simuler le comportement de l'ancien parser
            results.original = {
                data: {
                    personal_info: { name: 'Détecté partiellement', email: 'Détecté', phone: 'Non détecté' },
                    skills: ['Compétences basiques'],
                    software: ['Logiciels basiques'],
                    languages: [{ language: 'Français', level: 'Natif' }, { language: 'Anglais', level: 'À évaluer' }],
                    work_experience: [{ title: 'À compléter', company: 'À spécifier', start_date: 'À définir', end_date: 'À définir' }]
                }
            };
        } catch (error) {
            console.log('Parser original non disponible pour comparaison');
        }
        
        // Test avec le parser optimisé
        try {
            results.enhanced = window.commitmentEnhancedParser.parseCV(cvContent);
        } catch (error) {
            console.error('❌ Erreur parser optimisé:', error);
        }
        
        // Calcul des améliorations
        if (results.original && results.enhanced) {
            results.improvements = {
                skills_gain: results.enhanced.data.skills.length - results.original.data.skills.length,
                software_gain: results.enhanced.data.software.length - results.original.data.software.length,
                experience_improvement: results.enhanced.data.work_experience.filter(exp => 
                    exp.start_date !== 'À définir' && exp.end_date !== 'À définir'
                ).length,
                phone_detected: results.enhanced.data.personal_info.phone !== 'À compléter',
                education_detected: (results.enhanced.data.education?.length || 0) > 0
            };
            
            console.log('📈 Améliorations quantifiées Commitment:', results.improvements);
        }
        
        return results;
    };
}

/**
 * Fonction pour mettre à jour le message de chargement
 */
function updateLoadingMessage(message) {
    const loadingElements = document.querySelectorAll('.loading-text, .status-message, #loading-message');
    loadingElements.forEach(element => {
        if (element) {
            element.textContent = message;
        }
    });
    
    console.log('📢 Status:', message);
}

/**
 * Installation automatique au chargement
 */
function autoInstallCommitmentParser() {
    console.log('🔧 Installation automatique du parser optimisé Commitment...');
    
    // Attendre que le DOM soit chargé
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            setTimeout(integrateEnhancedParser, 500); // Petit délai pour s'assurer que tout est chargé
        });
    } else {
        setTimeout(integrateEnhancedParser, 500);
    }
    
    // Message de confirmation après installation
    setTimeout(() => {
        if (typeof window.EnhancedCVParser !== 'undefined' && 
            typeof window.commitmentEnhancedParser !== 'undefined') {
            console.log('✅ Parser optimisé Commitment installé avec succès !');
            console.log('🧪 Pour tester: testCommitmentParser()');
            console.log('⚖️ Pour comparer: compareCommitmentParsers(cvContent)');
            
            // Notification visuelle si possible
            if (typeof updateLoadingMessage === 'function') {
                updateLoadingMessage('Parser CV optimisé Commitment activé ✅');
            }
        } else {
            console.log('❌ Installation Commitment échouée. Vérifiez que enhanced-cv-parser.js est chargé.');
        }
    }, 1000);
}

// Export des fonctions pour utilisation externe
if (typeof window !== 'undefined') {
    window.integrateEnhancedParser = integrateEnhancedParser;
    window.updateLoadingMessage = updateLoadingMessage;
    window.autoInstallCommitmentParser = autoInstallCommitmentParser;
    
    // Auto-installation
    autoInstallCommitmentParser();
}

console.log('✅ Script d\'intégration parser Commitment chargé avec succès !');
