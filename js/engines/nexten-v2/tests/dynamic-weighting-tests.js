/**
 * TESTS UNITAIRES - SYSTÈME PONDÉRATION DYNAMIQUE NEXTEN V2.0
 * 
 * Suite de tests complète pour valider le système de pondération basé sur motivations
 * Tests de régression, performance et cas d'usage métier
 */

class DynamicWeightingTests {
    constructor() {
        this.testResults = [];
        this.performanceMetrics = {};
        console.log('🧪 Suite de tests pondération dynamique initialisée');
    }

    /**
     * EXÉCUTION DE TOUS LES TESTS
     */
    async runAllTests() {
        console.log('🚀 Lancement de la suite de tests complète...\n');
        
        const startTime = performance.now();
        
        try {
            // Tests unitaires système de base
            await this.testBasicWeightingSystem();
            await this.testWeightNormalization();
            await this.testMotivationMapping();
            
            // Tests d'intégration
            await this.testNextenV2Integration();
            await this.testCandidateMotivationExtraction();
            
            // Tests cas d'usage métier
            await this.testBusinessUseCases();
            
            // Tests de performance
            await this.testPerformance();
            
            // Tests de régression
            await this.testRegression();
            
            // Génération du rapport final
            const totalTime = performance.now() - startTime;
            this.generateTestReport(totalTime);
            
        } catch (error) {
            console.error('❌ Erreur dans les tests:', error);
            this.logTestResult('ERREUR_GLOBALE', false, error.message);
        }
    }

    /**
     * TESTS SYSTÈME DE BASE
     */
    async testBasicWeightingSystem() {
        console.log('📋 Tests système de pondération de base...');
        
        const dynamicSystem = new DynamicWeightingSystem();
        
        // Test 1: Initialisation système
        const test1 = dynamicSystem.baseWeights && 
                     Object.keys(dynamicSystem.baseWeights).length === 11 &&
                     dynamicSystem.motivationToCriteria;
        this.logTestResult('INIT_SYSTEM', test1, 'Système initialisé correctement');

        // Test 2: Poids de base totalisent 100%
        const totalBaseWeight = Object.values(dynamicSystem.baseWeights).reduce((sum, w) => sum + w, 0);
        const test2 = Math.abs(totalBaseWeight - 1.0) < 0.01;
        this.logTestResult('BASE_WEIGHTS_100', test2, `Total poids de base: ${Math.round(totalBaseWeight * 100)}%`);

        // Test 3: Mapping motivations complet
        const allCriteria = Object.keys(dynamicSystem.baseWeights);
        const mappedCriteria = new Set();
        Object.values(dynamicSystem.motivationToCriteria).forEach(criteria => 
            criteria.forEach(c => mappedCriteria.add(c))
        );
        const test3 = allCriteria.every(criterion => mappedCriteria.has(criterion));
        this.logTestResult('MOTIVATION_MAPPING', test3, `${mappedCriteria.size}/${allCriteria.length} critères mappés`);
    }

    /**
     * TESTS NORMALISATION DES POIDS
     */
    async testWeightNormalization() {
        console.log('⚖️ Tests normalisation des poids...');
        
        const dynamicSystem = new DynamicWeightingSystem();
        
        // Test cas motivation unique
        const result1 = dynamicSystem.calculateDynamicWeights(['remuneration']);
        const total1 = Object.values(result1.weights).reduce((sum, w) => sum + w, 0);
        const test1 = Math.abs(total1 - 1.0) < 0.001;
        this.logTestResult('NORMALIZATION_SINGLE', test1, `Total après ajustement: ${Math.round(total1 * 100)}%`);

        // Test cas motivations multiples
        const result2 = dynamicSystem.calculateDynamicWeights(['remuneration', 'flexibilite', 'localisation']);
        const total2 = Object.values(result2.weights).reduce((sum, w) => sum + w, 0);
        const test2 = Math.abs(total2 - 1.0) < 0.001;
        this.logTestResult('NORMALIZATION_MULTIPLE', test2, `Total avec 3 motivations: ${Math.round(total2 * 100)}%`);

        // Test cas motivation inconnue
        const result3 = dynamicSystem.calculateDynamicWeights(['motivation_inconnue']);
        const test3 = !result3.isAdjusted;
        this.logTestResult('UNKNOWN_MOTIVATION', test3, 'Motivation inconnue gérée correctement');

        // Test cas vide
        const result4 = dynamicSystem.calculateDynamicWeights([]);
        const test4 = !result4.isAdjusted;
        this.logTestResult('EMPTY_MOTIVATIONS', test4, 'Cas vide géré correctement');
    }

    /**
     * TESTS MAPPING MOTIVATIONS → CRITÈRES
     */
    async testMotivationMapping() {
        console.log('🗺️ Tests mapping motivations → critères...');
        
        const dynamicSystem = new DynamicWeightingSystem();
        
        // Test mapping rémunération
        const result1 = dynamicSystem.calculateDynamicWeights(['remuneration']);
        const compensationBoost = result1.weights.compensation > dynamicSystem.baseWeights.compensation;
        this.logTestResult('MAPPING_REMUNERATION', compensationBoost, 'Rémunération boost compensation');

        // Test mapping flexibilité
        const result2 = dynamicSystem.calculateDynamicWeights(['flexibilite']);
        const workEnvBoost = result2.weights.workEnvironment > dynamicSystem.baseWeights.workEnvironment;
        this.logTestResult('MAPPING_FLEXIBILITE', workEnvBoost, 'Flexibilité boost workEnvironment');

        // Test mapping localisation
        const result3 = dynamicSystem.calculateDynamicWeights(['localisation']);
        const locationBoost = result3.weights.location > dynamicSystem.baseWeights.location;
        this.logTestResult('MAPPING_LOCALISATION', locationBoost, 'Localisation boost location');

        // Test mapping perspectives évolution (multi-critères)
        const result4 = dynamicSystem.calculateDynamicWeights(['perspectives_evolution']);
        const evolutionBoosts = ['semantic', 'companySize', 'industry'].every(criterion => 
            result4.weights[criterion] > dynamicSystem.baseWeights[criterion]
        );
        this.logTestResult('MAPPING_EVOLUTION', evolutionBoosts, 'Perspectives évolution boost multi-critères');
    }

    /**
     * TESTS INTÉGRATION NEXTEN V2
     */
    async testNextenV2Integration() {
        console.log('🔗 Tests intégration NEXTEN V2...');
        
        try {
            // Test création instance
            const nextenV2 = new NextenV2WithDynamicWeighting();
            const test1 = nextenV2.dynamicWeightingSystem instanceof DynamicWeightingSystem;
            this.logTestResult('NEXTEN_V2_CREATION', test1, 'Instance créée avec système dynamique');

            // Test diagnostic système
            const diagnostic = nextenV2.diagnosticDynamicWeighting();
            const test2 = diagnostic.systemStatus === 'operational';
            this.logTestResult('NEXTEN_V2_DIAGNOSTIC', test2, `Statut: ${diagnostic.systemStatus}`);

            // Test simulation
            const simulation = nextenV2.simulateDynamicWeighting(['remuneration', 'flexibilite']);
            const test3 = simulation.wouldBeAdjusted === true;
            this.logTestResult('NEXTEN_V2_SIMULATION', test3, 'Simulation fonctionne');

        } catch (error) {
            this.logTestResult('NEXTEN_V2_INTEGRATION', false, `Erreur: ${error.message}`);
        }
    }

    /**
     * TESTS EXTRACTION MOTIVATIONS CANDIDAT
     */
    async testCandidateMotivationExtraction() {
        console.log('👤 Tests extraction motivations candidat...');
        
        try {
            const nextenV2 = new NextenV2WithDynamicWeighting();
            
            // Test format array
            const candidate1 = { motivations: ['remuneration', 'localisation'] };
            const motivations1 = nextenV2.extractCandidateMotivations(candidate1);
            const test1 = motivations1.length === 2 && motivations1[0] === 'remuneration';
            this.logTestResult('EXTRACTION_ARRAY', test1, `Motivations extraites: ${motivations1.length}`);

            // Test format champs séparés
            const candidate2 = { 
                motivation_1: 'flexibilite', 
                motivation_2: 'perspectives_evolution',
                motivation_3: ''
            };
            const motivations2 = nextenV2.extractCandidateMotivations(candidate2);
            const test2 = motivations2.length === 2;
            this.logTestResult('EXTRACTION_FIELDS', test2, `Champs séparés: ${motivations2.length} motivations`);

            // Test inférence depuis questionnaire
            const candidate3 = {
                pretentions_salariales: '45000-55000',
                negociation_salariale: 'importante',
                mode_travail_prefere: 'hybride'
            };
            const motivations3 = nextenV2.extractCandidateMotivations(candidate3);
            const test3 = motivations3.includes('remuneration') && motivations3.includes('flexibilite');
            this.logTestResult('EXTRACTION_INFERENCE', test3, `Inférence: ${motivations3.join(', ')}`);

        } catch (error) {
            this.logTestResult('CANDIDATE_EXTRACTION', false, `Erreur: ${error.message}`);
        }
    }

    /**
     * TESTS CAS D'USAGE MÉTIER
     */
    async testBusinessUseCases() {
        console.log('💼 Tests cas d'usage métier...');
        
        // Cas 1: Candidat motivé par rémunération
        const candidateRemu = {
            id: 'test_candidate_1',
            motivations: ['remuneration', 'localisation'],
            pretentions_salariales: '50000-60000'
        };
        
        const jobRemu = {
            id: 'test_job_1',
            fourchette_salariale: '55000-65000',
            ville: 'Paris'
        };

        const simulationRemu = await this.simulateMatchingWithDynamicWeights(candidateRemu, jobRemu);
        const test1 = simulationRemu.dynamicWeighting.applied === true;
        this.logTestResult('BUSINESS_CASE_REMU', test1, 'Candidat rémunération traité');

        // Cas 2: Candidat motivé par flexibilité
        const candidateFlex = {
            id: 'test_candidate_2',
            motivations: ['flexibilite', 'perspectives_evolution'],
            mode_travail_prefere: 'remote'
        };
        
        const jobFlex = {
            id: 'test_job_2',
            mode_travail: 'Hybride possible',
            type_entreprise: 'Scale-up'
        };

        const simulationFlex = await this.simulateMatchingWithDynamicWeights(candidateFlex, jobFlex);
        const test2 = simulationFlex.dynamicWeighting.applied === true;
        this.logTestResult('BUSINESS_CASE_FLEX', test2, 'Candidat flexibilité traité');

        // Cas 3: Candidat sans motivations
        const candidateEmpty = {
            id: 'test_candidate_3',
            // Pas de motivations
        };
        
        const simulationEmpty = await this.simulateMatchingWithDynamicWeights(candidateEmpty, jobRemu);
        const test3 = simulationEmpty.dynamicWeighting.applied === false;
        this.logTestResult('BUSINESS_CASE_EMPTY', test3, 'Candidat sans motivations géré');
    }

    /**
     * TESTS PERFORMANCE
     */
    async testPerformance() {
        console.log('⚡ Tests performance...');
        
        const iterations = 100;
        const dynamicSystem = new DynamicWeightingSystem();
        
        // Test performance calcul pondération
        const startTime1 = performance.now();
        for (let i = 0; i < iterations; i++) {
            dynamicSystem.calculateDynamicWeights(['remuneration', 'flexibilite', 'localisation']);
        }
        const avgTime1 = (performance.now() - startTime1) / iterations;
        
        const test1 = avgTime1 < 10; // Moins de 10ms par calcul
        this.logTestResult('PERFORMANCE_CALCULATION', test1, `Temps moyen: ${avgTime1.toFixed(2)}ms`);
        this.performanceMetrics.calculationTime = avgTime1;

        // Test performance extraction motivations
        const testCandidate = {
            motivations: ['remuneration', 'localisation', 'flexibilite'],
            motivation_1: 'remuneration',
            motivation_2: 'localisation'
        };
        
        try {
            const nextenV2 = new NextenV2WithDynamicWeighting();
            
            const startTime2 = performance.now();
            for (let i = 0; i < iterations; i++) {
                nextenV2.extractCandidateMotivations(testCandidate);
            }
            const avgTime2 = (performance.now() - startTime2) / iterations;
            
            const test2 = avgTime2 < 5; // Moins de 5ms par extraction
            this.logTestResult('PERFORMANCE_EXTRACTION', test2, `Temps moyen: ${avgTime2.toFixed(2)}ms`);
            this.performanceMetrics.extractionTime = avgTime2;
            
        } catch (error) {
            this.logTestResult('PERFORMANCE_EXTRACTION', false, `Erreur: ${error.message}`);
        }
    }

    /**
     * TESTS RÉGRESSION
     */
    async testRegression() {
        console.log('🔄 Tests régression...');
        
        // Test: Les scores doivent rester cohérents
        const testCases = [
            { motivations: ['remuneration'], expectedBoostCriterion: 'compensation' },
            { motivations: ['flexibilite'], expectedBoostCriterion: 'workEnvironment' },
            { motivations: ['localisation'], expectedBoostCriterion: 'location' },
            { motivations: ['perspectives_evolution'], expectedBoostCriterion: 'semantic' }
        ];

        const dynamicSystem = new DynamicWeightingSystem();
        
        testCases.forEach((testCase, index) => {
            const result = dynamicSystem.calculateDynamicWeights(testCase.motivations);
            const isBoostCorrect = result.weights[testCase.expectedBoostCriterion] > 
                                 dynamicSystem.baseWeights[testCase.expectedBoostCriterion];
            
            this.logTestResult(`REGRESSION_${index + 1}`, isBoostCorrect, 
                             `Motivation ${testCase.motivations[0]} boost ${testCase.expectedBoostCriterion}`);
        });

        // Test cohérence des ajustements
        const multiMotivResult = dynamicSystem.calculateDynamicWeights(['remuneration', 'flexibilite']);
        const hasMultipleBoosts = multiMotivResult.adjustments.length >= 2;
        this.logTestResult('REGRESSION_MULTI', hasMultipleBoosts, 'Ajustements multiples cohérents');
    }

    /**
     * SIMULATION MATCHING AVEC PONDÉRATION DYNAMIQUE
     */
    async simulateMatchingWithDynamicWeights(candidateData, jobData) {
        try {
            const nextenV2 = new NextenV2WithDynamicWeighting();
            
            // Simulation plutôt que calcul réel pour les tests
            const motivations = nextenV2.extractCandidateMotivations(candidateData);
            const simulation = nextenV2.simulateDynamicWeighting(motivations);
            
            return {
                dynamicWeighting: {
                    applied: simulation.wouldBeAdjusted,
                    adjustments: simulation.adjustments,
                    weightComparison: simulation.weightComparison
                },
                candidateMotivations: motivations
            };
            
        } catch (error) {
            return {
                dynamicWeighting: { applied: false, error: error.message },
                candidateMotivations: []
            };
        }
    }

    /**
     * LOGGING RÉSULTAT TEST
     */
    logTestResult(testName, passed, details = '') {
        const result = {
            test: testName,
            passed,
            details,
            timestamp: new Date().toISOString()
        };
        
        this.testResults.push(result);
        
        const status = passed ? '✅' : '❌';
        console.log(`${status} ${testName}: ${details}`);
    }

    /**
     * GÉNÉRATION RAPPORT FINAL
     */
    generateTestReport(totalTime) {
        console.log('\n📊 RAPPORT DE TESTS - PONDÉRATION DYNAMIQUE NEXTEN V2.0');
        console.log('═'.repeat(60));
        
        const totalTests = this.testResults.length;
        const passedTests = this.testResults.filter(r => r.passed).length;
        const failedTests = totalTests - passedTests;
        const successRate = Math.round((passedTests / totalTests) * 100);
        
        console.log(`📋 Tests exécutés: ${totalTests}`);
        console.log(`✅ Tests réussis: ${passedTests}`);
        console.log(`❌ Tests échoués: ${failedTests}`);
        console.log(`📈 Taux de réussite: ${successRate}%`);
        console.log(`⏱️ Temps total: ${Math.round(totalTime)}ms`);
        
        if (Object.keys(this.performanceMetrics).length > 0) {
            console.log('\n⚡ MÉTRIQUES PERFORMANCE:');
            Object.entries(this.performanceMetrics).forEach(([metric, value]) => {
                console.log(`- ${metric}: ${value.toFixed(2)}ms`);
            });
        }
        
        if (failedTests > 0) {
            console.log('\n❌ TESTS ÉCHOUÉS:');
            this.testResults.filter(r => !r.passed).forEach(result => {
                console.log(`- ${result.test}: ${result.details}`);
            });
        }
        
        console.log('\n' + '═'.repeat(60));
        
        if (successRate >= 95) {
            console.log('🎉 SYSTÈME PRÊT POUR PRODUCTION');
        } else if (successRate >= 80) {
            console.log('⚠️ SYSTÈME FONCTIONNEL AVEC POINTS D\'ATTENTION');
        } else {
            console.log('🚨 SYSTÈME NON PRÊT - CORRECTIONS NÉCESSAIRES');
        }
        
        return {
            totalTests,
            passedTests,
            failedTests,
            successRate,
            totalTime: Math.round(totalTime),
            performanceMetrics: this.performanceMetrics,
            status: successRate >= 95 ? 'READY' : (successRate >= 80 ? 'WARNING' : 'FAILED')
        };
    }
}

// === EXÉCUTION AUTOMATIQUE DES TESTS ===

/**
 * FONCTION D'EXÉCUTION RAPIDE
 */
async function runDynamicWeightingTests() {
    const testSuite = new DynamicWeightingTests();
    return await testSuite.runAllTests();
}

/**
 * TESTS SPÉCIFIQUES POUR DEBUG
 */
async function runSpecificTests(testCategories = ['basic', 'integration', 'business']) {
    console.log('🎯 Exécution tests spécifiques:', testCategories.join(', '));
    
    const testSuite = new DynamicWeightingTests();
    
    if (testCategories.includes('basic')) {
        await testSuite.testBasicWeightingSystem();
        await testSuite.testWeightNormalization();
        await testSuite.testMotivationMapping();
    }
    
    if (testCategories.includes('integration')) {
        await testSuite.testNextenV2Integration();
        await testSuite.testCandidateMotivationExtraction();
    }
    
    if (testCategories.includes('business')) {
        await testSuite.testBusinessUseCases();
    }
    
    if (testCategories.includes('performance')) {
        await testSuite.testPerformance();
    }
    
    return testSuite.generateTestReport(0);
}

// Export pour utilisation
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { DynamicWeightingTests, runDynamicWeightingTests, runSpecificTests };
}

if (typeof window !== 'undefined') {
    window.DynamicWeightingTests = DynamicWeightingTests;
    window.runDynamicWeightingTests = runDynamicWeightingTests;
    window.runSpecificTests = runSpecificTests;
    console.log('🧪 Tests pondération dynamique disponibles');
}