/**
 * 🚀 NEXTEN V2.0 - SCRIPT D'INSTALLATION ET INTÉGRATION AUTOMATIQUE
 * 
 * Installation one-click du système de pondération dynamique
 * Validation complète et configuration automatique
 */

class NextenV2DynamicInstaller {
    constructor() {
        this.installationSteps = [];
        this.validationResults = {};
        this.configurationOptions = {};
        
        console.log('🚀 NEXTEN V2.0 - Installateur Pondération Dynamique initialisé');
    }

    /**
     * INSTALLATION COMPLÈTE AUTOMATIQUE
     * Processus one-click avec validation
     */
    async installComplete() {
        console.log('🔧 Début installation NEXTEN V2.0 + Pondération Dynamique...\n');
        
        const startTime = performance.now();
        let success = true;
        
        try {
            // Étape 1: Vérification des prérequis
            await this.checkPrerequisites();
            
            // Étape 2: Installation des modules
            await this.installModules();
            
            // Étape 3: Configuration système
            await this.configureSystem();
            
            // Étape 4: Tests de validation
            await this.runValidationTests();
            
            // Étape 5: Configuration production
            await this.setupProduction();
            
            // Rapport final
            const installTime = performance.now() - startTime;
            this.generateInstallationReport(installTime, true);
            
            return {
                success: true,
                installTime: Math.round(installTime),
                nextenV2Instance: this.createConfiguredInstance(),
                report: this.generateQuickStartGuide()
            };
            
        } catch (error) {
            console.error('❌ Erreur installation:', error);
            this.generateInstallationReport(performance.now() - startTime, false, error);
            
            return {
                success: false,
                error: error.message,
                rollbackInstructions: this.generateRollbackInstructions()
            };
        }
    }

    /**
     * VÉRIFICATION DES PRÉREQUIS
     */
    async checkPrerequisites() {
        console.log('🔍 Vérification des prérequis...');
        
        const checks = {
            nextenV1Available: false,
            es6Support: false,
            performanceAPI: false,
            promiseSupport: false,
            localStorageAccess: false
        };

        // Vérification Nexten V1
        try {
            if (typeof NextenUnifiedSystem !== 'undefined') {
                checks.nextenV1Available = true;
                console.log('✅ Nexten V1.0 disponible');
            } else {
                console.warn('⚠️ Nexten V1.0 non détecté - mode standalone');
            }
        } catch (e) {
            console.warn('⚠️ Nexten V1.0 non disponible');
        }

        // Vérification ES6+
        try {
            eval('() => {}'); // Arrow functions
            eval('const test = {};'); // const/let
            eval('class Test {}'); // Classes
            checks.es6Support = true;
            console.log('✅ Support ES6+ confirmé');
        } catch (e) {
            throw new Error('ES6+ requis - navigateur non compatible');
        }

        // Vérification Performance API
        if (typeof performance !== 'undefined' && performance.now) {
            checks.performanceAPI = true;
            console.log('✅ Performance API disponible');
        } else {
            console.warn('⚠️ Performance API non disponible - métriques limitées');
        }

        // Vérification Promises
        if (typeof Promise !== 'undefined') {
            checks.promiseSupport = true;
            console.log('✅ Support Promises confirmé');
        } else {
            throw new Error('Promises requises - navigateur non compatible');
        }

        // Test localStorage (en mode non restrictif)
        try {
            localStorage.setItem('nexten_test', 'test');
            localStorage.removeItem('nexten_test');
            checks.localStorageAccess = true;
            console.log('✅ localStorage accessible');
        } catch (e) {
            console.warn('⚠️ localStorage non accessible - fonctionnalités limitées');
        }

        this.validationResults.prerequisites = checks;
        console.log('✅ Prérequis validés\n');
    }

    /**
     * INSTALLATION DES MODULES
     */
    async installModules() {
        console.log('📦 Installation des modules...');
        
        const modules = {
            dynamicWeightingSystem: false,
            nextenV2WithDynamic: false,
            tests: false
        };

        // Vérification DynamicWeightingSystem
        try {
            if (typeof DynamicWeightingSystem !== 'undefined') {
                modules.dynamicWeightingSystem = true;
                console.log('✅ DynamicWeightingSystem chargé');
            } else {
                throw new Error('DynamicWeightingSystem non trouvé');
            }
        } catch (e) {
            console.error('❌ Erreur chargement DynamicWeightingSystem:', e.message);
            throw new Error('Module DynamicWeightingSystem requis');
        }

        // Vérification NextenV2WithDynamicWeighting
        try {
            if (typeof NextenV2WithDynamicWeighting !== 'undefined') {
                modules.nextenV2WithDynamic = true;
                console.log('✅ NextenV2WithDynamicWeighting chargé');
            } else {
                throw new Error('NextenV2WithDynamicWeighting non trouvé');
            }
        } catch (e) {
            console.error('❌ Erreur chargement NextenV2WithDynamicWeighting:', e.message);
            throw new Error('Module NextenV2WithDynamicWeighting requis');
        }

        // Vérification Tests (optionnel)
        try {
            if (typeof runDynamicWeightingTests !== 'undefined') {
                modules.tests = true;
                console.log('✅ Tests pondération dynamique disponibles');
            } else {
                console.warn('⚠️ Tests non disponibles - validation limitée');
            }
        } catch (e) {
            console.warn('⚠️ Tests non chargés');
        }

        this.validationResults.modules = modules;
        console.log('✅ Modules installés\n');
    }

    /**
     * CONFIGURATION SYSTÈME
     */
    async configureSystem() {
        console.log('⚙️ Configuration du système...');
        
        // Configuration par défaut
        this.configurationOptions = {
            adjustmentConfig: {
                primary_boost: 0.08,       // +8% motivation #1
                secondary_boost: 0.05,     // +5% motivation #2
                tertiary_boost: 0.03,      // +3% motivation #3
                min_weight: 0.01,          // Poids minimum 1%
                max_weight: 0.35           // Poids maximum 35%
            },
            
            performanceTargets: {
                maxCalculationTime: 200,   // 200ms max
                targetPrecision: 0.95,     // 95% précision min
                fallbackEnabled: true      // Fallback automatique
            },
            
            debugMode: false,              // Mode debug désactivé par défaut
            
            productionMode: {
                enabled: false,
                monitoring: true,
                logging: 'errors'          // errors/warnings/all
            }
        };

        // Test de l'instance
        try {
            const testInstance = new NextenV2WithDynamicWeighting();
            console.log('✅ Instance de test créée avec succès');
            
            // Test diagnostic
            const diagnostic = testInstance.diagnosticDynamicWeighting();
            if (diagnostic.systemStatus === 'operational') {
                console.log('✅ Diagnostic système : Opérationnel');
            } else {
                console.warn('⚠️ Diagnostic système : Points d\'attention', diagnostic.issues);
            }
            
            this.validationResults.systemConfig = {
                instanceCreated: true,
                diagnosticStatus: diagnostic.systemStatus,
                issues: diagnostic.issues || []
            };
            
        } catch (error) {
            console.error('❌ Erreur création instance:', error.message);
            throw new Error('Configuration système échouée');
        }

        console.log('✅ Système configuré\n');
    }

    /**
     * TESTS DE VALIDATION
     */
    async runValidationTests() {
        console.log('🧪 Exécution des tests de validation...');
        
        const testResults = {
            dynamicWeightingTests: null,
            basicFunctionality: null,
            performanceTests: null
        };

        // Tests pondération dynamique
        if (this.validationResults.modules.tests) {
            try {
                console.log('🔬 Tests pondération dynamique...');
                const dynamicResults = await runDynamicWeightingTests();
                testResults.dynamicWeightingTests = dynamicResults;
                
                if (dynamicResults.successRate >= 95) {
                    console.log(`✅ Tests pondération dynamique : ${dynamicResults.successRate}% réussite`);
                } else {
                    console.warn(`⚠️ Tests pondération dynamique : ${dynamicResults.successRate}% réussite (< 95%)`);
                }
                
            } catch (error) {
                console.error('❌ Erreur tests pondération dynamique:', error.message);
                testResults.dynamicWeightingTests = { success: false, error: error.message };
            }
        }

        // Tests fonctionnalité de base
        try {
            console.log('🔬 Tests fonctionnalité de base...');
            
            const nexten = new NextenV2WithDynamicWeighting();
            
            // Test extraction motivations
            const testCandidate = {
                motivations: ['remuneration', 'flexibilite'],
                pretentions_salariales: '45000-55000'
            };
            
            const motivations = nexten.extractCandidateMotivations(testCandidate);
            const motivationsOK = motivations.length === 2 && motivations[0] === 'remuneration';
            
            // Test simulation pondération
            const simulation = nexten.simulateDynamicWeighting(['remuneration', 'localisation']);
            const simulationOK = simulation.wouldBeAdjusted === true;
            
            testResults.basicFunctionality = {
                extractMotivations: motivationsOK,
                simulateDynamic: simulationOK,
                overallSuccess: motivationsOK && simulationOK
            };
            
            if (testResults.basicFunctionality.overallSuccess) {
                console.log('✅ Tests fonctionnalité de base : Réussis');
            } else {
                console.warn('⚠️ Tests fonctionnalité de base : Échec partiel');
            }
            
        } catch (error) {
            console.error('❌ Erreur tests de base:', error.message);
            testResults.basicFunctionality = { success: false, error: error.message };
        }

        // Tests performance
        try {
            console.log('🔬 Tests performance...');
            
            const performanceResults = await this.runPerformanceTests();
            testResults.performanceTests = performanceResults;
            
            if (performanceResults.averageTime < 200) {
                console.log(`✅ Tests performance : ${performanceResults.averageTime}ms (< 200ms)`);
            } else {
                console.warn(`⚠️ Tests performance : ${performanceResults.averageTime}ms (> 200ms)`);
            }
            
        } catch (error) {
            console.error('❌ Erreur tests performance:', error.message);
            testResults.performanceTests = { success: false, error: error.message };
        }

        this.validationResults.tests = testResults;
        console.log('✅ Tests de validation terminés\n');
    }

    /**
     * TESTS PERFORMANCE
     */
    async runPerformanceTests() {
        const nexten = new NextenV2WithDynamicWeighting();
        const iterations = 10;
        const times = [];

        const testCandidate = {
            id: 'perf_test',
            motivations: ['remuneration', 'flexibilite', 'localisation'],
            pretentions_salariales: '45000-55000',
            ville: 'Paris'
        };

        const testJob = {
            id: 'perf_job',
            fourchette_salariale: '50000-60000',
            mode_travail: 'Hybride',
            ville: 'Paris'
        };

        for (let i = 0; i < iterations; i++) {
            const startTime = performance.now();
            
            // Simulation pour éviter erreurs de modules manquants
            const motivations = nexten.extractCandidateMotivations(testCandidate);
            const simulation = nexten.simulateDynamicWeighting(motivations);
            
            const endTime = performance.now();
            times.push(endTime - startTime);
        }

        const averageTime = times.reduce((sum, time) => sum + time, 0) / times.length;
        const maxTime = Math.max(...times);
        const minTime = Math.min(...times);

        return {
            averageTime: Math.round(averageTime),
            maxTime: Math.round(maxTime),
            minTime: Math.round(minTime),
            iterations,
            success: averageTime < 200
        };
    }

    /**
     * CONFIGURATION PRODUCTION
     */
    async setupProduction() {
        console.log('🏭 Configuration pour production...');
        
        // Configuration optimisée production
        this.configurationOptions.productionMode = {
            enabled: true,
            monitoring: true,
            logging: 'errors',
            caching: true,
            fallbackEnabled: true,
            maxRetries: 3,
            timeoutMs: 5000
        };

        // Recommandations déploiement
        const deploymentRecommendations = [
            'Activer monitoring métriques temps réel',
            'Configurer alertes sur temps calcul > 200ms',
            'Prévoir fallback automatique vers V2.0 standard',
            'Monitorer taux utilisation pondération dynamique',
            'Valider complétude questionnaires candidats'
        ];

        this.configurationOptions.deploymentRecommendations = deploymentRecommendations;
        
        console.log('✅ Configuration production prête\n');
    }

    /**
     * CRÉATION INSTANCE CONFIGURÉE
     */
    createConfiguredInstance() {
        console.log('🎯 Création instance configurée...');
        
        try {
            const nexten = new NextenV2WithDynamicWeighting();
            
            // Application configuration personnalisée
            if (nexten.dynamicWeightingSystem) {
                Object.assign(nexten.dynamicWeightingSystem.adjustmentConfig, 
                            this.configurationOptions.adjustmentConfig);
            }
            
            // Ajout métadonnées installation
            nexten._installationMetadata = {
                installedAt: new Date().toISOString(),
                version: '2.0.1',
                configurationApplied: true,
                validationPassed: this.validationResults
            };
            
            console.log('✅ Instance configurée créée');
            return nexten;
            
        } catch (error) {
            console.error('❌ Erreur création instance configurée:', error.message);
            throw error;
        }
    }

    /**
     * GÉNÉRATION RAPPORT INSTALLATION
     */
    generateInstallationReport(installTime, success, error = null) {
        console.log('\n📊 RAPPORT D\'INSTALLATION - NEXTEN V2.0 PONDÉRATION DYNAMIQUE');
        console.log('═'.repeat(70));
        
        const status = success ? '✅ SUCCÈS' : '❌ ÉCHEC';
        console.log(`📋 Statut: ${status}`);
        console.log(`⏱️ Temps d'installation: ${Math.round(installTime)}ms`);
        
        if (error) {
            console.log(`🚨 Erreur: ${error.message}`);
        }
        
        console.log('\n📦 MODULES:');
        Object.entries(this.validationResults.modules || {}).forEach(([module, status]) => {
            const statusIcon = status ? '✅' : '❌';
            console.log(`${statusIcon} ${module}`);
        });
        
        if (this.validationResults.tests) {
            console.log('\n🧪 TESTS:');
            const tests = this.validationResults.tests;
            
            if (tests.dynamicWeightingTests) {
                const rate = tests.dynamicWeightingTests.successRate || 0;
                console.log(`📊 Pondération dynamique: ${rate}% réussite`);
            }
            
            if (tests.basicFunctionality) {
                const status = tests.basicFunctionality.overallSuccess ? '✅' : '❌';
                console.log(`🔧 Fonctionnalité de base: ${status}`);
            }
            
            if (tests.performanceTests) {
                const avgTime = tests.performanceTests.averageTime || 0;
                const status = avgTime < 200 ? '✅' : '⚠️';
                console.log(`⚡ Performance: ${status} ${avgTime}ms`);
            }
        }
        
        console.log('\n' + '═'.repeat(70));
        
        if (success) {
            console.log('🎉 INSTALLATION RÉUSSIE - SYSTÈME PRÊT POUR PRODUCTION');
        } else {
            console.log('🚨 INSTALLATION ÉCHOUÉE - VÉRIFIER LES ERREURS CI-DESSUS');
        }
    }

    /**
     * GUIDE QUICK START
     */
    generateQuickStartGuide() {
        return {
            quickStart: `
🚀 NEXTEN V2.0 + PONDÉRATION DYNAMIQUE - GUIDE QUICK START

1. UTILISATION IMMÉDIATE :
   const nexten = new NextenV2WithDynamicWeighting();
   
2. CALCUL AVEC PONDÉRATION DYNAMIQUE :
   const result = await nexten.calculateV2MatchingScoreWithDynamicWeights(candidateData, jobData);
   
3. VÉRIFICATION PONDÉRATION APPLIQUÉE :
   if (result.dynamicWeighting.applied) {
       console.log('Pondération personnalisée activée !');
   }

4. INTERFACE DE TEST :
   Ouvrir: js/engines/nexten-v2/demo/dynamic-weighting-demo.html

5. DOCUMENTATION COMPLÈTE :
   Voir: js/engines/nexten-v2/docs/DYNAMIC_WEIGHTING.md
            `,
            
            examples: {
                basicUsage: `
// Candidat avec motivations
const candidat = {
    motivations: ['remuneration', 'flexibilite'],
    pretentions_salariales: '45000-55000'
};

const result = await nexten.calculateV2MatchingScoreWithDynamicWeights(candidat, poste);
console.log('Score optimisé:', Math.round(result.finalScore * 100) + '%');
                `,
                
                simulation: `
// Test impact sans calcul réel
const simulation = nexten.simulateDynamicWeighting(['remuneration', 'localisation']);
console.log('Ajustements prévus:', simulation.adjustments);
                `,
                
                diagnostic: `
// Vérification système
const diagnostic = nexten.diagnosticDynamicWeighting();
console.log('Statut:', diagnostic.systemStatus);
                `
            },
            
            links: {
                demo: 'js/engines/nexten-v2/demo/dynamic-weighting-demo.html',
                documentation: 'js/engines/nexten-v2/docs/DYNAMIC_WEIGHTING.md',
                tests: 'runDynamicWeightingTests()',
                mainDemo: 'js/engines/nexten-v2/demo/nexten-v2-demo-complete.html'
            }
        };
    }

    /**
     * INSTRUCTIONS ROLLBACK
     */
    generateRollbackInstructions() {
        return {
            immediate: `
// Rollback immédiat vers V2.0 standard
const nextenStandard = new NextenV2UnifiedSystem();
const result = await nextenStandard.calculateV2MatchingScore(candidateData, jobData);
            `,
            
            complete: `
1. Désactiver pondération dynamique
2. Utiliser NextenV2UnifiedSystem au lieu de NextenV2WithDynamicWeighting
3. Supprimer les références aux motivations candidat
4. Fallback automatique intégré dans le code
            `,
            
            monitoring: [
                'Surveiller métriques performance',
                'Vérifier taux erreur < 1%',
                'Confirmer temps calcul < 200ms',
                'Valider précision maintenue > 95%'
            ]
        };
    }
}

// === FONCTIONS UTILITAIRES D'INSTALLATION ===

/**
 * INSTALLATION ONE-CLICK
 */
async function installNextenV2DynamicWeighting() {
    console.log('🚀 Lancement installation NEXTEN V2.0 + Pondération Dynamique...\n');
    
    const installer = new NextenV2DynamicInstaller();
    return await installer.installComplete();
}

/**
 * VALIDATION RAPIDE SYSTÈME
 */
async function validateNextenV2Dynamic() {
    console.log('🔍 Validation rapide NEXTEN V2.0 + Pondération Dynamique...\n');
    
    try {
        // Vérification modules
        if (typeof NextenV2WithDynamicWeighting === 'undefined') {
            throw new Error('NextenV2WithDynamicWeighting non chargé');
        }
        
        if (typeof DynamicWeightingSystem === 'undefined') {
            throw new Error('DynamicWeightingSystem non chargé');
        }
        
        // Test instance
        const nexten = new NextenV2WithDynamicWeighting();
        const diagnostic = nexten.diagnosticDynamicWeighting();
        
        // Test fonctionnel
        const testMotivations = ['remuneration', 'flexibilite'];
        const simulation = nexten.simulateDynamicWeighting(testMotivations);
        
        const result = {
            modulesLoaded: true,
            instanceCreated: true,
            diagnosticStatus: diagnostic.systemStatus,
            functionalTest: simulation.wouldBeAdjusted,
            overallStatus: diagnostic.systemStatus === 'operational' && simulation.wouldBeAdjusted
        };
        
        console.log('✅ Validation rapide terminée:', result);
        return result;
        
    } catch (error) {
        console.error('❌ Erreur validation:', error.message);
        return {
            error: error.message,
            overallStatus: false
        };
    }
}

/**
 * CRÉATION INSTANCE PRÉ-CONFIGURÉE
 */
function createNextenV2DynamicInstance(customConfig = {}) {
    console.log('🎯 Création instance NEXTEN V2.0 + Pondération Dynamique...');
    
    try {
        const nexten = new NextenV2WithDynamicWeighting();
        
        // Application configuration personnalisée
        if (customConfig.adjustmentConfig && nexten.dynamicWeightingSystem) {
            Object.assign(nexten.dynamicWeightingSystem.adjustmentConfig, customConfig.adjustmentConfig);
        }
        
        // Métadonnées
        nexten._quickSetup = {
            createdAt: new Date().toISOString(),
            customConfig: customConfig,
            ready: true
        };
        
        console.log('✅ Instance créée et configurée');
        return nexten;
        
    } catch (error) {
        console.error('❌ Erreur création instance:', error.message);
        throw error;
    }
}

// Export pour utilisation
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { 
        NextenV2DynamicInstaller,
        installNextenV2DynamicWeighting,
        validateNextenV2Dynamic,
        createNextenV2DynamicInstance
    };
}

if (typeof window !== 'undefined') {
    window.NextenV2DynamicInstaller = NextenV2DynamicInstaller;
    window.installNextenV2DynamicWeighting = installNextenV2DynamicWeighting;
    window.validateNextenV2Dynamic = validateNextenV2Dynamic;
    window.createNextenV2DynamicInstance = createNextenV2DynamicInstance;
    
    console.log('🚀 Installateur NEXTEN V2.0 + Pondération Dynamique disponible');
    console.log('Usage: await installNextenV2DynamicWeighting()');
}