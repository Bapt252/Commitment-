/**
 * NEXTEN V2.0 Enhanced - Suite de tests automatisés Contract Type
 * Tests exhaustifs pour valider l'algorithme sophistiqué de type de contrat
 * 
 * @version 2.0-ENHANCED
 * @author NEXTEN Team
 * @created 2025-06-30
 */

class NextenContractTypeTestSuite {
    constructor() {
        this.testResults = [];
        this.totalTests = 0;
        this.passedTests = 0;
        this.failedTests = 0;
        this.startTime = null;
        this.endTime = null;
        
        // Initialisation du système à tester
        this.nextenSystem = new NextenV2EnhancedSystem();
        
        console.log('🧪 NEXTEN Contract Type Test Suite initialized');
    }
    
    /**
     * Lancement de tous les tests
     */
    async runAllTests() {
        this.startTime = performance.now();
        console.log('🚀 Starting comprehensive test suite...');
        
        try {
            // Tests de base
            await this.testExclusivePreference();
            await this.testPreferredPreference();
            await this.testAcceptablePreference();
            await this.testFlexiblePreference();
            
            // Tests de cas limites
            await this.testEdgeCases();
            
            // Tests de fallback
            await this.testFallbackMechanisms();
            
            // Tests de performance
            await this.testPerformance();
            
            // Tests d'intégration
            await this.testIntegration();
            
            // Tests de normalisation
            await this.testContractTypeNormalization();
            
            // Tests de compatibilité
            await this.testBackwardCompatibility();
            
        } catch (error) {
            console.error('❌ Test suite error:', error);
            this.addTestResult('GLOBAL', 'Test Suite Execution', false, error.message);
        }
        
        this.endTime = performance.now();
        this.generateTestReport();
    }
    
    /**
     * Tests pour le niveau EXCLUSIF
     */
    async testExclusivePreference() {
        console.log('🔒 Testing EXCLUSIVE preference level...');
        
        const testCases = [
            {
                name: 'CDI Exclusif - Match exact',
                candidate: this.createCandidate(['cdi'], 'exclusive', 'cdi'),
                job: this.createJob('cdi'),
                expected: 1.0
            },
            {
                name: 'CDI Exclusif - Refus CDD',
                candidate: this.createCandidate(['cdi'], 'exclusive', 'cdi'),
                job: this.createJob('cdd'),
                expected: 0.0
            },
            {
                name: 'Freelance Exclusif - Match exact',
                candidate: this.createCandidate(['freelance'], 'exclusive', 'freelance'),
                job: this.createJob('freelance'),
                expected: 1.0
            },
            {
                name: 'Freelance Exclusif - Refus CDI',
                candidate: this.createCandidate(['freelance'], 'exclusive', 'freelance'),
                job: this.createJob('cdi'),
                expected: 0.0
            }
        ];
        
        for (const testCase of testCases) {
            await this.executeTestCase('EXCLUSIVE', testCase);
        }
    }
    
    /**
     * Tests pour le niveau PRÉFÉRENTIEL
     */
    async testPreferredPreference() {
        console.log('❤️ Testing PREFERRED preference level...');
        
        const testCases = [
            {
                name: 'Préfère Freelance - Choix principal',
                candidate: this.createCandidate(['freelance', 'cdi'], 'preferred', 'freelance'),
                job: this.createJob('freelance'),
                expected: 0.9
            },
            {
                name: 'Préfère Freelance - Choix secondaire CDI',
                candidate: this.createCandidate(['freelance', 'cdi'], 'preferred', 'freelance'),
                job: this.createJob('cdi'),
                expected: 0.8
            },
            {
                name: 'Préfère CDI - Refus CDD',
                candidate: this.createCandidate(['cdi', 'freelance'], 'preferred', 'cdi'),
                job: this.createJob('cdd'),
                expected: 0.0
            },
            {
                name: 'Multi-contrats préférés',
                candidate: this.createCandidate(['cdi', 'cdd', 'interim'], 'preferred', 'cdi'),
                job: this.createJob('interim'),
                expected: 0.8
            }
        ];
        
        for (const testCase of testCases) {
            await this.executeTestCase('PREFERRED', testCase);
        }
    }
    
    /**
     * Tests pour le niveau ACCEPTABLE
     */
    async testAcceptablePreference() {
        console.log('✅ Testing ACCEPTABLE preference level...');
        
        const testCases = [
            {
                name: 'Premier choix CDI - Bonus',
                candidate: this.createCandidate(['cdi', 'cdd', 'interim'], 'acceptable', 'cdi'),
                job: this.createJob('cdi'),
                expected: 0.8 // 70% + 10% bonus
            },
            {
                name: 'Deuxième choix CDD - Sans bonus',
                candidate: this.createCandidate(['cdi', 'cdd', 'interim'], 'acceptable', 'cdi'),
                job: this.createJob('cdd'),
                expected: 0.7
            },
            {
                name: 'Troisième choix Interim - Sans bonus',
                candidate: this.createCandidate(['cdi', 'cdd', 'interim'], 'acceptable', 'cdi'),
                job: this.createJob('interim'),
                expected: 0.7
            },
            {
                name: 'Type non accepté - Refus',
                candidate: this.createCandidate(['cdi', 'cdd'], 'acceptable', 'cdi'),
                job: this.createJob('freelance'),
                expected: 0.0
            }
        ];
        
        for (const testCase of testCases) {
            await this.executeTestCase('ACCEPTABLE', testCase);
        }
    }
    
    /**
     * Tests pour le niveau FLEXIBLE
     */
    async testFlexiblePreference() {
        console.log('🔄 Testing FLEXIBLE preference level...');
        
        const testCases = [
            {
                name: 'Flexible CDI - Score uniforme',
                candidate: this.createCandidate(['cdi', 'cdd', 'freelance'], 'flexible', 'cdi'),
                job: this.createJob('cdi'),
                expected: 0.85
            },
            {
                name: 'Flexible CDD - Score uniforme',
                candidate: this.createCandidate(['cdi', 'cdd', 'freelance'], 'flexible', 'cdi'),
                job: this.createJob('cdd'),
                expected: 0.85
            },
            {
                name: 'Flexible Freelance - Score uniforme',
                candidate: this.createCandidate(['cdi', 'cdd', 'freelance'], 'flexible', 'cdi'),
                job: this.createJob('freelance'),
                expected: 0.85
            },
            {
                name: 'Flexible - Type non sélectionné',
                candidate: this.createCandidate(['cdi', 'cdd'], 'flexible', 'cdi'),
                job: this.createJob('interim'),
                expected: 0.0
            }
        ];
        
        for (const testCase of testCases) {
            await this.executeTestCase('FLEXIBLE', testCase);
        }
    }
    
    /**
     * Tests de cas limites
     */
    async testEdgeCases() {
        console.log('🎯 Testing edge cases...');
        
        const testCases = [
            {
                name: 'Données vides',
                candidate: { contractData: { selectedTypes: [], preferenceLevel: null, isValid: false } },
                job: this.createJob('cdi'),
                expectFallback: true
            },
            {
                name: 'Niveau inconnu',
                candidate: this.createCandidate(['cdi'], 'unknown_level', 'cdi'),
                job: this.createJob('cdi'),
                expectError: true
            },
            {
                name: 'Type de contrat inexistant',
                candidate: this.createCandidate(['cdi'], 'exclusive', 'cdi'),
                job: this.createJob('type_inexistant'),
                expected: 0.0
            },
            {
                name: 'Sélection multiples avec exclusif',
                candidate: this.createCandidate(['cdi', 'cdd'], 'exclusive', 'cdi'),
                job: this.createJob('cdd'),
                expected: 0.0 // Seul le premier type devrait être considéré
            }
        ];
        
        for (const testCase of testCases) {
            await this.executeEdgeCase(testCase);
        }
    }
    
    /**
     * Tests des mécanismes de fallback
     */
    async testFallbackMechanisms() {
        console.log('🛡️ Testing fallback mechanisms...');
        
        const testCases = [
            {
                name: 'Format legacy contractType',
                candidate: { contractType: 'cdi' },
                job: this.createJob('cdi'),
                expected: 0.95
            },
            {
                name: 'Format legacy type_contrat_souhaite',
                candidate: { type_contrat_souhaite: 'freelance' },
                job: this.createJob('freelance'),
                expected: 0.95
            },
            {
                name: 'Aucune donnée contrat',
                candidate: {},
                job: this.createJob('cdi'),
                expected: 0.6 // fallbackScore
            },
            {
                name: 'Compatibilité CDI vers CDD',
                candidate: { contractType: 'cdi' },
                job: this.createJob('cdd'),
                expected: 0.6
            }
        ];
        
        for (const testCase of testCases) {
            await this.executeTestCase('FALLBACK', testCase);
        }
    }
    
    /**
     * Tests de performance
     */
    async testPerformance() {
        console.log('⚡ Testing performance...');
        
        const iterations = 1000;
        const candidate = this.createCandidate(['cdi', 'cdd'], 'preferred', 'cdi');
        const job = this.createJob('cdi');
        
        const startTime = performance.now();
        
        for (let i = 0; i < iterations; i++) {
            await this.nextenSystem.calculateContractTypeCriterion(candidate, job, {});
        }
        
        const endTime = performance.now();
        const totalTime = endTime - startTime;
        const averageTime = totalTime / iterations;
        
        const success = averageTime < 5; // < 5ms par calcul
        
        this.addTestResult(
            'PERFORMANCE',
            `${iterations} calculs en ${Math.round(totalTime)}ms (moy: ${averageTime.toFixed(2)}ms)`,
            success,
            success ? null : `Performance insuffisante: ${averageTime.toFixed(2)}ms > 5ms`
        );
    }
    
    /**
     * Tests d'intégration
     */
    async testIntegration() {
        console.log('🔗 Testing integration...');
        
        // Test d'intégration avec le système complet
        const candidateData = {
            id: 'test_candidate',
            contractData: this.createCandidate(['cdi', 'freelance'], 'preferred', 'freelance').contractData,
            motivations: ['flexibility', 'remuneration'],
            location: 'Paris',
            coordinates: { lat: 48.8566, lng: 2.3522 }
        };
        
        const jobData = {
            id: 'test_job',
            contractType: 'freelance',
            title: 'Développeur Senior',
            location: 'Paris',
            coordinates: { lat: 48.8566, lng: 2.3522 },
            salary: '50000-60000'
        };
        
        try {
            const result = await this.nextenSystem.calculateOptimizedMatching(
                candidateData,
                jobData,
                {},
                { forceRefresh: true }
            );
            
            const contractScore = result.criteria.contractType.score;
            const success = contractScore === 0.9; // Préférence principale
            
            this.addTestResult(
                'INTEGRATION',
                'Calcul matching complet avec contract type enhanced',
                success,
                success ? null : `Score contractType inattendu: ${contractScore} (attendu: 0.9)`
            );
            
        } catch (error) {
            this.addTestResult(
                'INTEGRATION',
                'Calcul matching complet',
                false,
                error.message
            );
        }
    }
    
    /**
     * Tests de normalisation
     */
    async testContractTypeNormalization() {
        console.log('🔄 Testing contract type normalization...');
        
        const testCases = [
            { input: 'CDI', expected: 'cdi' },
            { input: 'contrat_cdi', expected: 'cdi' },
            { input: 'CDD', expected: 'cdd' },
            { input: 'freelance', expected: 'freelance' },
            { input: 'free_lance', expected: 'freelance' },
            { input: 'consulting', expected: 'freelance' },
            { input: 'interim', expected: 'interim' },
            { input: 'interimaire', expected: 'interim' },
            { input: 'type_inconnu', expected: 'type_inconnu' }
        ];
        
        for (const testCase of testCases) {
            const normalized = this.nextenSystem.normalizeContractType(testCase.input);
            const success = normalized === testCase.expected;
            
            this.addTestResult(
                'NORMALIZATION',
                `"${testCase.input}" → "${normalized}"`,
                success,
                success ? null : `Attendu: "${testCase.expected}", reçu: "${normalized}"`
            );
        }
    }
    
    /**
     * Tests de compatibilité descendante
     */
    async testBackwardCompatibility() {
        console.log('📋 Testing backward compatibility...');
        
        // Test avec l'ancien système NextenV2OptimizedSystem
        const oldSystem = new NextenV2OptimizedSystem();
        const newSystem = this.nextenSystem;
        
        const legacyCandidate = { contractType: 'cdi' };
        const job = this.createJob('cdi');
        
        try {
            const oldResult = await oldSystem.calculateContractTypeCriterion(legacyCandidate, job, {});
            const newResult = await newSystem.calculateContractTypeCriterion(legacyCandidate, job, {});
            
            const scoreDiff = Math.abs(oldResult.score - newResult.score);
            const success = scoreDiff < 0.01; // Tolérance de 1%
            
            this.addTestResult(
                'COMPATIBILITY',
                'Compatibilité avec format legacy',
                success,
                success ? null : `Différence de score: ${scoreDiff} (ancien: ${oldResult.score}, nouveau: ${newResult.score})`
            );
            
        } catch (error) {
            this.addTestResult(
                'COMPATIBILITY',
                'Test compatibilité legacy',
                false,
                error.message
            );
        }
    }
    
    /**
     * Utilitaires pour créer des données de test
     */
    createCandidate(selectedTypes, preferenceLevel, primaryChoice) {
        return {
            contractData: {
                selectedTypes,
                preferenceLevel,
                primaryChoice,
                isValid: true
            }
        };
    }
    
    createJob(contractType) {
        return {
            contractType,
            title: 'Test Job',
            company: 'Test Company'
        };
    }
    
    /**
     * Exécution d'un cas de test standard
     */
    async executeTestCase(category, testCase) {
        try {
            const result = await this.nextenSystem.calculateContractTypeCriterion(
                testCase.candidate,
                testCase.job,
                {}
            );
            
            const score = Math.round(result.score * 100) / 100;
            const expected = testCase.expected;
            const success = Math.abs(score - expected) < 0.01;
            
            this.addTestResult(
                category,
                testCase.name,
                success,
                success ? null : `Score: ${score}, attendu: ${expected}`
            );
            
        } catch (error) {
            this.addTestResult(
                category,
                testCase.name,
                false,
                error.message
            );
        }
    }
    
    /**
     * Exécution d'un cas limite
     */
    async executeEdgeCase(testCase) {
        try {
            const result = await this.nextenSystem.calculateContractTypeCriterion(
                testCase.candidate,
                testCase.job,
                {}
            );
            
            if (testCase.expectFallback) {
                const success = result.fallback === true;
                this.addTestResult(
                    'EDGE_CASE',
                    testCase.name,
                    success,
                    success ? null : 'Fallback attendu mais pas activé'
                );
            } else if (testCase.expectError) {
                this.addTestResult(
                    'EDGE_CASE',
                    testCase.name,
                    false,
                    'Erreur attendue mais calcul réussi'
                );
            } else {
                const score = Math.round(result.score * 100) / 100;
                const expected = testCase.expected;
                const success = Math.abs(score - expected) < 0.01;
                
                this.addTestResult(
                    'EDGE_CASE',
                    testCase.name,
                    success,
                    success ? null : `Score: ${score}, attendu: ${expected}`
                );
            }
            
        } catch (error) {
            if (testCase.expectError) {
                this.addTestResult(
                    'EDGE_CASE',
                    testCase.name,
                    true,
                    null
                );
            } else {
                this.addTestResult(
                    'EDGE_CASE',
                    testCase.name,
                    false,
                    error.message
                );
            }
        }
    }
    
    /**
     * Ajout d'un résultat de test
     */
    addTestResult(category, name, success, error = null) {
        this.totalTests++;
        if (success) {
            this.passedTests++;
        } else {
            this.failedTests++;
        }
        
        this.testResults.push({
            category,
            name,
            success,
            error,
            timestamp: new Date().toISOString()
        });
        
        const status = success ? '✅' : '❌';
        const errorMsg = error ? ` (${error})` : '';
        console.log(`  ${status} ${name}${errorMsg}`);
    }
    
    /**
     * Génération du rapport de test
     */
    generateTestReport() {
        const executionTime = this.endTime - this.startTime;
        
        console.log('\n📊 ========== RAPPORT DE TESTS ==========');
        console.log(`⏱️  Temps d'exécution: ${Math.round(executionTime)}ms`);
        console.log(`📋 Tests totaux: ${this.totalTests}`);
        console.log(`✅ Tests réussis: ${this.passedTests}`);
        console.log(`❌ Tests échoués: ${this.failedTests}`);
        console.log(`📈 Taux de réussite: ${Math.round((this.passedTests / this.totalTests) * 100)}%`);
        
        // Rapport par catégorie
        const categories = {};
        this.testResults.forEach(result => {
            if (!categories[result.category]) {
                categories[result.category] = { total: 0, passed: 0 };
            }
            categories[result.category].total++;
            if (result.success) {
                categories[result.category].passed++;
            }
        });
        
        console.log('\n📊 Résultats par catégorie:');
        Object.entries(categories).forEach(([category, stats]) => {
            const rate = Math.round((stats.passed / stats.total) * 100);
            console.log(`  ${category}: ${stats.passed}/${stats.total} (${rate}%)`);
        });
        
        // Tests échoués
        const failedTests = this.testResults.filter(r => !r.success);
        if (failedTests.length > 0) {
            console.log('\n❌ Tests échoués:');
            failedTests.forEach(test => {
                console.log(`  • [${test.category}] ${test.name}: ${test.error}`);
            });
        }
        
        console.log('\n🎉 Rapport de tests terminé');
        
        return {
            totalTests: this.totalTests,
            passedTests: this.passedTests,
            failedTests: this.failedTests,
            successRate: Math.round((this.passedTests / this.totalTests) * 100),
            executionTime: Math.round(executionTime),
            categories,
            failedTests
        };
    }
}

// Fonction globale pour lancer les tests
async function runContractTypeTests() {
    console.log('🚀 Launching NEXTEN Contract Type Test Suite...');
    
    const testSuite = new NextenContractTypeTestSuite();
    const report = await testSuite.runAllTests();
    
    return report;
}

// Export pour utilisation modulaire
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { NextenContractTypeTestSuite, runContractTypeTests };
} else if (typeof window !== 'undefined') {
    window.NextenContractTypeTestSuite = NextenContractTypeTestSuite;
    window.runContractTypeTests = runContractTypeTests;
}

console.log('🧪 NEXTEN Contract Type Test Suite loaded');
