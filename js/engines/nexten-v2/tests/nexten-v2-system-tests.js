/**
 * NEXTEN V2.0 - TESTS SYSTÈME COMPLETS
 * Suite de tests exhaustive pour validation du système 11 critères
 * 
 * Usage:
 * - Ouvrir dans navigateur avec tous les modules V2.0 chargés
 * - Appeler runNextenV2Tests() dans la console
 * - Analyser le rapport généré
 */

class NextenV2SystemTests {
    constructor() {
        this.testResults = {
            total: 0,
            passed: 0,
            failed: 0,
            errors: []
        };
        
        this.testProfiles = this.initializeTestProfiles();
        this.nextenV2System = null;
        
        console.log('🧪 NEXTEN V2.0 System Tests initialisé');
    }

    /**
     * LANCEMENT COMPLET DES TESTS
     */
    async runAllTests() {
        console.log('🚀 === NEXTEN V2.0 - VALIDATION SYSTÈME COMPLÈTE ===');
        
        try {
            // Phase 1: Tests fondamentaux
            await this.testSystemBootstrap();
            
            // Phase 2: Tests profils de référence
            await this.testReferenceProfiles();
            
            // Phase 3: Tests de performance
            await this.testPerformanceValidation();
            
            // Phase 4: Tests edge cases
            await this.testEdgeCases();
            
            // Phase 5: Tests de régression
            await this.testRegression();
            
            // Génération du rapport final
            return this.generateFinalReport();
            
        } catch (error) {
            console.error('❌ Erreur critique lors des tests:', error);
            this.testResults.errors.push(`Erreur critique: ${error.message}`);
            return this.generateFinalReport();
        }
    }

    /**
     * PROFILS DE TEST DIVERSIFIÉS - PRODUCTION READY
     */
    initializeTestProfiles() {
        return {
            // Profil de référence: Dorothée Lim (validation 97%)
            reference_profile: {
                name: "Dorothée Lim - Référence",
                candidate: {
                    id: "ref_001",
                    nom: "Dorothée Lim",
                    pretentions_salariales: "85-95k€",
                    motivations: ["evolution_carriere", "innovation_creativite", "remuneration"],
                    taille_entreprise_preference: "groupe",
                    environnement_prefere: "hybrid_3_2",
                    secteurs_cibles: ["luxe", "mode", "cosmetique"],
                    disponibilite: "3_mois",
                    type_contrat_souhaite: "cdi",
                    competences: ["Marketing", "Brand Management", "Luxe", "Digital"],
                    experiences: [
                        { 
                            entreprise: "LVMH", 
                            poste: "Chef de Produit", 
                            secteur: "luxe",
                            duree: "3 ans"
                        },
                        { 
                            entreprise: "Chanel", 
                            poste: "Marketing Manager", 
                            secteur: "luxe",
                            duree: "2 ans"
                        }
                    ],
                    coordonnees: { ville: "Paris", code_postal: "75001" }
                },
                job: {
                    id: "job_001",
                    titre: "Directeur Marketing - Maison de Luxe",
                    fourchette_salariale: "90-110k€",
                    secteur: "luxe",
                    mode_travail: "hybrid_3_2",
                    type_contrat: "cdi",
                    urgence_recrutement: "normal",
                    competences_requises: ["Marketing", "Luxe", "Management", "Digital"],
                    missions: ["Stratégie marketing", "Management équipe", "Développement marque"],
                    coordonnees: { ville: "Paris", code_postal: "75008" }
                },
                company: {
                    nom: "Maison Lumière",
                    secteur: "luxe",
                    effectif: 850,
                    localisation: "Paris",
                    taille_equipe: 12,
                    avantages: ["mutuelle", "restaurant", "remote"]
                },
                expectedScore: 0.97,
                expectedLevel: "excellent",
                targetTime: 150
            },

            // Profil Tech/Startup
            tech_profile: {
                name: "Alexandre - Tech Startup",
                candidate: {
                    id: "tech_001",
                    nom: "Alexandre Martin",
                    pretentions_salariales: "70-85k€",
                    motivations: ["innovation_creativite", "autonomie_responsabilite", "apprentissage"],
                    taille_entreprise_preference: "startup",
                    environnement_prefere: "hybrid_4_1",
                    secteurs_cibles: ["tech", "fintech"],
                    disponibilite: "1_mois",
                    type_contrat_souhaite: "cdi",
                    competences: ["React", "Node.js", "Python", "Product Management"],
                    experiences: [
                        { entreprise: "Scale Up", poste: "Tech Lead", secteur: "tech", duree: "2 ans" }
                    ]
                },
                job: {
                    id: "tech_job_001",
                    titre: "Lead Developer - FinTech",
                    fourchette_salariale: "75-90k€",
                    secteur: "tech",
                    mode_travail: "hybrid_4_1",
                    type_contrat: "cdi",
                    urgence_recrutement: "urgent"
                },
                company: {
                    nom: "TechStart",
                    secteur: "fintech",
                    effectif: 45,
                    localisation: "Paris"
                },
                expectedScore: 0.88,
                expectedLevel: "excellent",
                targetTime: 160
            },

            // Profil Finance Corporate
            finance_profile: {
                name: "Sophie - Finance Corporate",
                candidate: {
                    id: "finance_001",
                    nom: "Sophie Dubois",
                    pretentions_salariales: "110-130k€",
                    motivations: ["carriere_internationale", "stabilite_securite", "prestige_entreprise"],
                    taille_entreprise_preference: "groupe",
                    environnement_prefere: "hybrid_2_3",
                    secteurs_cibles: ["finance", "consulting"],
                    disponibilite: "6_mois",
                    type_contrat_souhaite: "cdi",
                    competences: ["Finance", "M&A", "Strategy", "Leadership"],
                    experiences: [
                        { entreprise: "Goldman Sachs", poste: "VP", secteur: "finance", duree: "5 ans" }
                    ]
                },
                job: {
                    id: "finance_job_001",
                    titre: "Director M&A",
                    fourchette_salariale: "120-150k€",
                    secteur: "finance",
                    mode_travail: "hybrid_2_3",
                    type_contrat: "cdi"
                },
                company: {
                    nom: "BankCorp",
                    secteur: "finance",
                    effectif: 12000,
                    localisation: "Paris"
                },
                expectedScore: 0.91,
                expectedLevel: "excellent",
                targetTime: 140
            },

            // Profil avec mismatch volontaire
            mismatch_profile: {
                name: "Jean - Mismatch Test",
                candidate: {
                    id: "mismatch_001",
                    nom: "Jean Mismatch",
                    pretentions_salariales: "45-55k€",
                    motivations: ["equilibre_vie_pro", "teletravail_100"],
                    taille_entreprise_preference: "startup",
                    environnement_prefere: "remote_100",
                    secteurs_cibles: ["sante", "education"],
                    competences: ["RH", "Formation"]
                },
                job: {
                    id: "mismatch_job_001",
                    titre: "Directeur Marketing - Maison de Luxe",
                    fourchette_salariale: "90-110k€",
                    secteur: "luxe",
                    mode_travail: "on_site_100",
                    type_contrat: "cdi"
                },
                company: {
                    nom: "Luxury Corp",
                    secteur: "luxe",
                    effectif: 5000,
                    localisation: "Paris"
                },
                expectedScore: 0.35,
                expectedLevel: "poor",
                targetTime: 120
            }
        };
    }

    /**
     * PHASE 1: TESTS BOOTSTRAP SYSTÈME
     */
    async testSystemBootstrap() {
        console.log('\n🔧 PHASE 1: Bootstrap et initialisation système');
        
        try {
            // Test 1.1: Instanciation système
            console.log('Test 1.1: Instanciation NextenV2UnifiedSystem...');
            this.nextenV2System = new NextenV2UnifiedSystem();
            this.assertTest(
                this.nextenV2System !== null,
                "Instanciation système réussie"
            );

            // Test 1.2: Pondérations valides
            console.log('Test 1.2: Validation pondérations...');
            const weights = this.nextenV2System.v2CriteriaWeights;
            const totalWeight = Object.values(weights).reduce((sum, w) => sum + w, 0);
            this.assertTest(
                Math.abs(totalWeight - 1.0) < 0.01,
                `Pondérations totales = 100% (${Math.round(totalWeight * 100)}%)`
            );

            // Test 1.3: Critères initialisés
            console.log('Test 1.3: Initialisation critères...');
            const criteriaKeys = Object.keys(this.nextenV2System.v2Criteria);
            this.assertTest(
                criteriaKeys.length === 11,
                `11 critères définis (${criteriaKeys.length} trouvés)`
            );

            // Test 1.4: Architecture V2 prête
            console.log('Test 1.4: Architecture V2 prête...');
            this.assertTest(
                typeof this.nextenV2System.calculateV2MatchingScore === 'function',
                "Méthode principale calculateV2MatchingScore disponible"
            );

            console.log('✅ Phase 1: Bootstrap réussi');

        } catch (error) {
            this.failTest("Erreur phase bootstrap", error.message);
        }
    }

    /**
     * PHASE 2: TESTS PROFILS DE RÉFÉRENCE
     */
    async testReferenceProfiles() {
        console.log('\n🎯 PHASE 2: Validation profils de référence');

        for (const [profileKey, profile] of Object.entries(this.testProfiles)) {
            console.log(`\n--- Test profil: ${profile.name} ---`);
            
            try {
                const startTime = performance.now();
                const result = await this.nextenV2System.calculateV2MatchingScore(
                    profile.candidate,
                    profile.job,
                    profile.company
                );
                const calculationTime = performance.now() - startTime;

                // Test 2.1: Score dans la plage attendue
                const scoreVariance = Math.abs(result.finalScore - profile.expectedScore);
                this.assertTest(
                    scoreVariance <= 0.05,
                    `Score dans plage attendue: ${Math.round(result.finalScore * 100)}% (attendu: ${Math.round(profile.expectedScore * 100)}%, écart: ${Math.round(scoreVariance * 100)}%)`
                );

                // Test 2.2: Niveau qualité correct
                const levelCorrect = this.isLevelCompatible(result.qualityLevel, profile.expectedLevel);
                this.assertTest(
                    levelCorrect,
                    `Niveau qualité: ${result.qualityLevel} (attendu: ${profile.expectedLevel})`
                );

                // Test 2.3: Performance dans objectif
                this.assertTest(
                    calculationTime <= profile.targetTime,
                    `Performance: ${Math.round(calculationTime)}ms (objectif: ${profile.targetTime}ms)`
                );

                // Test 2.4: Structure résultat complète
                this.assertTest(
                    result.criteriaBreakdown && result.criteriaBreakdown.criteria,
                    "Breakdown critères présent"
                );

                this.assertTest(
                    result.insights && result.insights.recommendations,
                    "Insights et recommandations présents"
                );

                this.assertTest(
                    result.performance && typeof result.performance.precision_estimated === 'number',
                    "Métriques performance présentes"
                );

                // Test 2.5: Critères calculés
                const criteriaCount = Object.keys(result.criteriaBreakdown.criteria).length;
                this.assertTest(
                    criteriaCount >= 3, // Au minimum 3 critères calculés
                    `Critères calculés: ${criteriaCount}/11`
                );

                console.log(`   📊 Résultat: ${Math.round(result.finalScore * 100)}% (${result.qualityLevel}) en ${Math.round(calculationTime)}ms`);

            } catch (error) {
                this.failTest(`Erreur profil ${profile.name}`, error.message);
            }
        }

        console.log('✅ Phase 2: Profils de référence validés');
    }

    /**
     * PHASE 3: TESTS DE PERFORMANCE
     */
    async testPerformanceValidation() {
        console.log('\n⚡ PHASE 3: Validation performance');

        try {
            const profile = this.testProfiles.reference_profile;
            const iterations = 5;
            const times = [];

            console.log(`Test performance sur ${iterations} itérations...`);

            // Test de charge
            for (let i = 0; i < iterations; i++) {
                const startTime = performance.now();
                await this.nextenV2System.calculateV2MatchingScore(
                    profile.candidate,
                    profile.job,
                    profile.company
                );
                times.push(performance.now() - startTime);
            }

            const avgTime = times.reduce((sum, t) => sum + t, 0) / times.length;
            const maxTime = Math.max(...times);
            const minTime = Math.min(...times);

            // Test 3.1: Temps moyen
            this.assertTest(
                avgTime < 200,
                `Temps moyen < 200ms: ${Math.round(avgTime)}ms`
            );

            // Test 3.2: Temps maximum
            this.assertTest(
                maxTime < 300,
                `Temps max < 300ms: ${Math.round(maxTime)}ms`
            );

            // Test 3.3: Consistance performance
            const timeVariance = maxTime - minTime;
            this.assertTest(
                timeVariance < 100,
                `Variance temps < 100ms: ${Math.round(timeVariance)}ms`
            );

            console.log(`   📈 Performance: Moy ${Math.round(avgTime)}ms, Min ${Math.round(minTime)}ms, Max ${Math.round(maxTime)}ms`);
            console.log('✅ Phase 3: Performance validée');

        } catch (error) {
            this.failTest("Erreur tests performance", error.message);
        }
    }

    /**
     * PHASE 4: TESTS EDGE CASES
     */
    async testEdgeCases() {
        console.log('\n🛡️ PHASE 4: Tests de robustesse (edge cases)');

        const edgeCases = [
            {
                name: "Données nulles",
                candidate: null,
                job: { titre: "Test" },
                company: {},
                shouldSurvive: true
            },
            {
                name: "Données vides",
                candidate: {},
                job: {},
                company: {},
                shouldSurvive: true
            },
            {
                name: "Salaires corrompus",
                candidate: { pretentions_salariales: "invalid_salary" },
                job: { fourchette_salariale: "corrupted" },
                company: {},
                shouldSurvive: true
            },
            {
                name: "Effectif invalide",
                candidate: { nom: "Test" },
                job: { titre: "Test" },
                company: { effectif: "not_a_number" },
                shouldSurvive: true
            },
            {
                name: "Secteurs manquants",
                candidate: { secteurs_cibles: null },
                job: { secteur: undefined },
                company: { secteur: "" },
                shouldSurvive: true
            }
        ];

        for (const testCase of edgeCases) {
            console.log(`   Test: ${testCase.name}...`);
            
            try {
                const result = await this.nextenV2System.calculateV2MatchingScore(
                    testCase.candidate,
                    testCase.job,
                    testCase.company
                );

                if (testCase.shouldSurvive) {
                    this.assertTest(
                        result && typeof result.finalScore === 'number',
                        `${testCase.name}: Système survit et retourne score valide`
                    );

                    this.assertTest(
                        result.finalScore >= 0 && result.finalScore <= 1,
                        `${testCase.name}: Score dans plage [0,1]`
                    );
                }

            } catch (error) {
                if (testCase.shouldSurvive) {
                    this.failTest(`${testCase.name}: Erreur inattendue`, error.message);
                } else {
                    this.assertTest(true, `${testCase.name}: Erreur attendue capturée`);
                }
            }
        }

        console.log('✅ Phase 4: Robustesse validée');
    }

    /**
     * PHASE 5: TESTS DE RÉGRESSION
     */
    async testRegression() {
        console.log('\n📊 PHASE 5: Tests de régression vs V1.0');

        try {
            // Test avec profil complet (doit utiliser V2)
            const completeProfile = this.testProfiles.reference_profile;
            console.log('Test mode V2 avec données complètes...');
            
            const v2Result = await this.nextenV2System.calculateV2MatchingScore(
                completeProfile.candidate,
                completeProfile.job,
                completeProfile.company
            );

            this.assertTest(
                v2Result.version === '2.0' || v2Result.matchingMode !== 'v1_fallback',
                "Mode V2 utilisé avec données complètes"
            );

            this.assertTest(
                v2Result.performance.precision_estimated > 0.91,
                `Précision estimée > V1.0: ${Math.round(v2Result.performance.precision_estimated * 100)}%`
            );

            // Test amélioration par rapport à V1.0
            const expectedImprovement = (v2Result.performance.precision_estimated - 0.912) * 100;
            this.assertTest(
                expectedImprovement > 0,
                `Amélioration vs V1.0: +${expectedImprovement.toFixed(1)}%`
            );

            console.log('✅ Phase 5: Régression validée');

        } catch (error) {
            this.failTest("Erreur tests régression", error.message);
        }
    }

    /**
     * GÉNÉRATION DU RAPPORT FINAL
     */
    generateFinalReport() {
        console.log('\n📋 === RAPPORT FINAL NEXTEN V2.0 ===');

        const successRate = this.testResults.total > 0 ? 
            (this.testResults.passed / this.testResults.total * 100) : 0;

        const report = {
            timestamp: new Date().toISOString(),
            summary: {
                total: this.testResults.total,
                passed: this.testResults.passed,
                failed: this.testResults.failed,
                successRate: successRate.toFixed(1)
            },
            details: {
                errors: this.testResults.errors,
                verdict: this.getVerdict(successRate)
            }
        };

        // Affichage console
        console.log(`📊 RÉSULTATS:`);
        console.log(`   Total: ${report.summary.total}`);
        console.log(`   ✅ Réussis: ${report.summary.passed}`);
        console.log(`   ❌ Échoués: ${report.summary.failed}`);
        console.log(`   📈 Taux de réussite: ${report.summary.successRate}%`);

        if (this.testResults.errors.length > 0) {
            console.log(`\n❌ ERREURS (${this.testResults.errors.length}):`);
            this.testResults.errors.forEach((error, index) => {
                console.log(`   ${index + 1}. ${error}`);
            });
        }

        console.log(`\n${report.details.verdict.emoji} VERDICT: ${report.details.verdict.message}`);
        console.log(`📝 RECOMMANDATION: ${report.details.verdict.recommendation}`);

        return report;
    }

    getVerdict(successRate) {
        if (successRate >= 95) {
            return {
                status: 'ready_production',
                emoji: '🏆',
                message: 'NEXTEN V2.0 PRÊT POUR PRODUCTION',
                recommendation: 'Déploiement autorisé. Système validé.'
            };
        } else if (successRate >= 85) {
            return {
                status: 'ready_staging',
                emoji: '✅',
                message: 'NEXTEN V2.0 PRÊT AVEC ATTENTION',
                recommendation: 'Tests supplémentaires recommandés avant production.'
            };
        } else if (successRate >= 70) {
            return {
                status: 'needs_fixes',
                emoji: '⚠️',
                message: 'NEXTEN V2.0 NÉCESSITE CORRECTIONS',
                recommendation: 'Corriger les erreurs identifiées avant nouveau test.'
            };
        } else {
            return {
                status: 'critical_issues',
                emoji: '❌',
                message: 'NEXTEN V2.0 PROBLÈMES CRITIQUES',
                recommendation: 'Révision complète nécessaire.'
            };
        }
    }

    // === UTILITAIRES ===

    assertTest(condition, testName) {
        this.testResults.total++;
        if (condition) {
            this.testResults.passed++;
            console.log(`   ✅ ${testName}`);
        } else {
            this.testResults.failed++;
            console.log(`   ❌ ${testName}`);
            this.testResults.errors.push(`Test échoué: ${testName}`);
        }
    }

    failTest(testName, error) {
        this.testResults.total++;
        this.testResults.failed++;
        console.log(`   ❌ ${testName}: ${error}`);
        this.testResults.errors.push(`${testName}: ${error}`);
    }

    isLevelCompatible(actual, expected) {
        const levels = {
            'poor': 1,
            'acceptable': 2,
            'good': 3,
            'excellent': 4
        };

        // Tolérance ±1 niveau
        return Math.abs((levels[actual] || 2) - (levels[expected] || 2)) <= 1;
    }
}

// === FONCTION PRINCIPALE ===

/**
 * Lancement des tests système NEXTEN V2.0
 */
async function runNextenV2SystemTests() {
    console.log('🚀 DÉMARRAGE TESTS SYSTÈME NEXTEN V2.0');
    console.log('⏰ Début:', new Date().toLocaleString());

    const testSuite = new NextenV2SystemTests();
    const report = await testSuite.runAllTests();

    console.log('⏰ Fin:', new Date().toLocaleString());
    console.log('📋 Tests terminés. Rapport disponible.');

    return report;
}

// Export pour utilisation
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { NextenV2SystemTests, runNextenV2SystemTests };
}

if (typeof window !== 'undefined') {
    window.NextenV2SystemTests = NextenV2SystemTests;
    window.runNextenV2SystemTests = runNextenV2SystemTests;
    console.log('🧪 NEXTEN V2.0 System Tests chargé et prêt');
}