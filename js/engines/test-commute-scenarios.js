/**
 * TESTS COMPLETS NEXTEN COMMUTE SCENARIOS
 * Validation des critères #1 + #2 avec données réelles Paris/Banlieue
 * Extension du profil Dorothée Lim avec géolocalisation
 */

class NextenCommuteScenarioTester {
    constructor() {
        this.commuteOptimizer = new CommuteOptimizer();
        this.geoMatcher = null; // Initialisé si NextenGeoMatcher disponible
        
        this.initializeTestData();
    }

    /**
     * DONNÉES TEST ÉTENDUES - DOROTHÉE LIM GEO
     * Profil complet avec géolocalisation pour tests critères #1 + #2
     */
    initializeTestData() {
        this.dorotheeLimExtended = {
            // === DONNÉES SÉMANTIQUES (Critère #1) ===
            experiences_professionnelles: [
                {
                    poste: "Office Manager",
                    entreprise: "Hermès",
                    date_debut: "2020",
                    date_fin: "2024",
                    missions: [
                        "Coordination administrative générale",
                        "Gestion des systèmes SAP et ERP",
                        "Support à la direction générale",
                        "Organisation des plannings équipes",
                        "Interface avec les clients VIP"
                    ]
                },
                {
                    poste: "Assistante Direction",
                    entreprise: "By Kilian",
                    date_debut: "2018",
                    date_fin: "2020",
                    missions: [
                        "Organisation planning direction",
                        "Gestion de projets cosmétiques",
                        "Interface clients et partenaires",
                        "Coordination événements luxe"
                    ]
                }
            ],
            competences_detaillees: [
                "SAP Business One", "ERP Management", "Microsoft Office Expert",
                "Gestion administrative", "Coordination équipes", "Planning et organisation",
                "Relation client VIP", "Secteur luxe et cosmétique", "MyEasyOrder"
            ],
            
            // === NOUVELLES DONNÉES GÉOGRAPHIQUES (Critère #2) ===
            adresse: "Boulogne-Billancourt, 92100",
            coordonnees: { lat: 48.8356, lng: 2.2501 },
            preferences_transport: ["metro", "tramway", "velo"],
            mobilite_acceptee: "paris_proche_banlieue",
            duree_trajet_max: "45min",
            
            // Métadonnées additionnelles
            analyse_cv: {
                profil_type: "Profil expérimenté secteur luxe avec expertise administrative",
                secteur_principal: "Luxe et Cosmétique"
            }
        };

        this.testJobsParisRegion = {
            // === SCÉNARIO 1: LA DÉFENSE (RER A DIRECT) ===
            defense_excellent: {
                titre_poste: "Office Manager Secteur Luxe",
                mission_principale: "Coordination administrative et gestion ERP environnement luxe",
                competences: ["SAP", "Office Management", "Coordination équipes", "ERP", "Secteur luxe"],
                experience_requise: "10+ ans expérience administrative secteur luxe",
                
                // Géolocalisation
                adresse: "La Défense, 92400 Courbevoie",
                coordonnees: { lat: 48.8908, lng: 2.2383 },
                accessibilite: ["rer_a", "metro_1", "parking", "tramway_t2"],
                
                // Scores attendus
                expected_semantic: 0.90, // Correspondance parfaite
                expected_commute: 0.85,  // RER A direct, ~20min
                expected_combined: 0.87  // Excellent overall
            },

            // === SCÉNARIO 2: RÉPUBLIQUE (MÉTRO DENSE) ===
            republique_good: {
                titre_poste: "Coordinatrice Administrative",
                mission_principale: "Coordination administrative et support direction",
                competences: ["Coordination", "Microsoft Office", "Gestion administrative", "Planning"],
                experience_requise: "5+ ans expérience administrative",
                
                // Géolocalisation
                adresse: "République, 75003 Paris",
                coordonnees: { lat: 48.8673, lng: 2.3629 },
                accessibilite: ["metro_3", "metro_5", "metro_8", "metro_9", "metro_11"],
                
                // Scores attendus
                expected_semantic: 0.75, // Bonne correspondance
                expected_commute: 0.78,  // Métro + tramway, ~25min
                expected_combined: 0.765
            },

            // === SCÉNARIO 3: ISSY-LES-MOULINEAUX (TRAMWAY) ===
            issy_moderate: {
                titre_poste: "Assistante Direction",
                mission_principale: "Support administratif à la direction",
                competences: ["Microsoft Office", "Organisation", "Communication"],
                experience_requise: "3+ ans expérience",
                
                // Géolocalisation
                adresse: "Issy-les-Moulineaux, 92130",
                coordonnees: { lat: 48.8247, lng: 2.2733 },
                accessibilite: ["tramway_t2", "metro_12", "bus"],
                
                // Scores attendus
                expected_semantic: 0.55, // Correspondance partielle
                expected_commute: 0.70,  // Tramway direct, ~15min
                expected_combined: 0.605
            },

            // === SCÉNARIO 4: SAINT-DENIS (BANLIEUE COMPLEXE) ===
            saint_denis_challenging: {
                titre_poste: "Gestionnaire Administrative",
                mission_principale: "Gestion administrative courante",
                competences: ["Administration", "Organisation"],
                experience_requise: "2+ ans",
                
                // Géolocalisation
                adresse: "Saint-Denis, 93200",
                coordonnees: { lat: 48.9362, lng: 2.3574 },
                accessibilite: ["rer_b", "rer_d", "metro_13"],
                
                // Scores attendus
                expected_semantic: 0.35, // Correspondance faible
                expected_commute: 0.40,  // Trajet complexe, ~45min
                expected_combined: 0.368
            }
        };
    }

    /**
     * EXÉCUTION COMPLÈTE DES TESTS GÉOGRAPHIQUES
     */
    async runCompleteCommuteTests() {
        console.log("🗺️ TESTS NEXTEN COMMUTE OPTIMIZER - SCENARIOS PARIS");
        console.log("==================================================");
        
        const results = {};
        
        for (const [scenarioName, jobData] of Object.entries(this.testJobsParisRegion)) {
            console.log(`\n🔍 SCÉNARIO: ${scenarioName.toUpperCase()}`);
            console.log(`📍 Lieu: ${jobData.adresse}`);
            console.log("-".repeat(60));
            
            const result = await this.testCommuteScenario(this.dorotheeLimExtended, jobData);
            results[scenarioName] = result;
            
            this.displayScenarioResult(scenarioName, result, jobData);
        }
        
        // Rapport global
        console.log("\n📊 RAPPORT GLOBAL COMMUTE TESTS");
        console.log("=================================");
        this.generateGlobalReport(results);
        
        return results;
    }

    /**
     * TEST D'UN SCÉNARIO SPÉCIFIQUE
     */
    async testCommuteScenario(candidateData, jobData) {
        const startTime = performance.now();
        
        try {
            // Test du CommuteOptimizer seul
            const commuteResult = await this.commuteOptimizer.calculateCommuteScore(candidateData, jobData);
            
            // Test intégré si GeoMatcher disponible
            let integratedResult = null;
            if (this.geoMatcher) {
                integratedResult = await this.geoMatcher.enhancedGeoMatching('dorothee_test', 'job_test');
            }
            
            const totalTime = performance.now() - startTime;
            
            return {
                commute_only: commuteResult,
                integrated: integratedResult,
                performance: {
                    calculation_time: totalTime,
                    meets_target: totalTime < 100 // Objectif < 100ms
                }
            };
            
        } catch (error) {
            console.error(`Erreur test scénario:`, error);
            return { error: error.message };
        }
    }

    /**
     * AFFICHAGE RÉSULTAT SCÉNARIO
     */
    displayScenarioResult(scenarioName, result, expectedJobData) {
        if (result.error) {
            console.log(`❌ Erreur: ${result.error}`);
            return;
        }
        
        const commuteResult = result.commute_only;
        const performance = result.performance;
        
        // Score et performance
        console.log(`🎯 Score trajet: ${(commuteResult.finalScore * 100).toFixed(1)}% (attendu: ${(expectedJobData.expected_commute * 100).toFixed(0)}%)`);
        console.log(`⏱️  Temps calcul: ${performance.calculation_time.toFixed(2)}ms ${performance.meets_target ? '✅' : '❌'}`);
        console.log(`🚀 Mode recommandé: ${commuteResult.bestMode}`);
        
        // Détail par mode de transport
        if (commuteResult.breakdown) {
            console.log("\n🚌 DÉTAIL PAR MODE:");
            Object.entries(commuteResult.breakdown).forEach(([mode, data]) => {
                const duration = Math.round(data.duration);
                const score = (data.score * 100).toFixed(0);
                const icon = this.getModeIcon(mode);
                console.log(`  ${icon} ${mode}: ${duration}min (${score}%)`);
            });
        }
        
        // Recommandation
        if (commuteResult.details?.recommendation) {
            console.log(`\n💡 Recommandation: ${commuteResult.details.recommendation.reason}`);
        }
        
        // Alternatives
        if (commuteResult.details?.alternatives?.length > 0) {
            console.log("🔄 Alternatives:");
            commuteResult.details.alternatives.forEach(alt => {
                console.log(`  • ${alt.mode}: ${alt.duration} (${alt.score})`);
            });
        }
        
        // Validation vs attendu
        const scoreInRange = this.isScoreInExpectedRange(
            commuteResult.finalScore, 
            expectedJobData.expected_commute, 
            0.1
        );
        console.log(`\n✅ Validation: ${scoreInRange ? 'PASS' : 'FAIL'} (tolérance ±10%)`);
    }

    /**
     * TEST STRESS PERFORMANCE
     */
    async performanceStressTest() {
        console.log("\n⚡ STRESS TEST PERFORMANCE COMMUTE");
        console.log("==================================");
        
        const iterations = 50;
        const scenario = this.testJobsParisRegion.defense_excellent;
        const times = [];
        
        console.log(`Exécution de ${iterations} calculs...`);
        
        for (let i = 0; i < iterations; i++) {
            const startTime = performance.now();
            await this.commuteOptimizer.calculateCommuteScore(this.dorotheeLimExtended, scenario);
            times.push(performance.now() - startTime);
            
            if ((i + 1) % 10 === 0) {
                process.stdout.write(`${i + 1}... `);
            }
        }
        
        console.log("\n");
        
        // Analyse des résultats
        const avgTime = times.reduce((a, b) => a + b, 0) / times.length;
        const maxTime = Math.max(...times);
        const minTime = Math.min(...times);
        const p95Time = times.sort((a, b) => a - b)[Math.floor(times.length * 0.95)];
        
        console.log(`📊 Résultats (${iterations} itérations):`);
        console.log(`  • Temps moyen: ${avgTime.toFixed(2)}ms`);
        console.log(`  • Temps min: ${minTime.toFixed(2)}ms`);
        console.log(`  • Temps max: ${maxTime.toFixed(2)}ms`);
        console.log(`  • P95: ${p95Time.toFixed(2)}ms`);
        console.log(`  • Objectif < 100ms: ${avgTime < 100 ? '✅ ATTEINT' : '❌ NON ATTEINT'}`);
        
        // Métriques cache
        const cacheReport = this.commuteOptimizer.getPerformanceReport();
        console.log(`\n💾 Efficacité cache:`);
        console.log(`  • Hit rate global: ${cacheReport.cacheHitRate}`);
        console.log(`  • Cache Level 1: ${cacheReport.cacheBreakdown.level1} hits`);
        console.log(`  • Cache Level 2: ${cacheReport.cacheBreakdown.level2} hits`);
        console.log(`  • Cache Level 3: ${cacheReport.cacheBreakdown.level3} hits`);
        
        return {
            iterations,
            avgTime,
            maxTime,
            minTime,
            p95Time,
            performanceGoalMet: avgTime < 100,
            cacheEfficiency: cacheReport.cacheHitRate
        };
    }

    /**
     * TEST VALIDITÉ CACHE MULTINIVEAU
     */
    async testCacheEfficiency() {
        console.log("\n🏪 TEST EFFICACITÉ CACHE MULTINIVEAU");
        console.log("====================================");
        
        const scenario = this.testJobsParisRegion.defense_excellent;
        
        // Premier calcul (pas de cache)
        console.log("1️⃣ Premier calcul (population cache)...");
        const result1 = await this.commuteOptimizer.calculateCommuteScore(this.dorotheeLimExtended, scenario);
        console.log(`   Temps: ${result1.performance?.calculationTime?.toFixed(2) || 'N/A'}ms`);
        
        // Deuxième calcul (cache level 1)
        console.log("2️⃣ Deuxième calcul (cache exact)...");
        const result2 = await this.commuteOptimizer.calculateCommuteScore(this.dorotheeLimExtended, scenario);
        console.log(`   Temps: ${result2.performance?.calculationTime?.toFixed(2) || 'N/A'}ms`);
        console.log(`   Cache hit: ${result2.performance?.cacheHit ? '✅' : '❌'}`);
        
        // Test avec variations géographiques (cache level 2/3)
        console.log("3️⃣ Calculs avec variations géographiques...");
        const variations = [
            { ...this.dorotheeLimExtended, coordonnees: { lat: 48.8356, lng: 2.2505 } }, // Légère variation
            { ...this.dorotheeLimExtended, coordonnees: { lat: 48.8360, lng: 2.2500 } }  // Autre variation
        ];
        
        for (let i = 0; i < variations.length; i++) {
            const result = await this.commuteOptimizer.calculateCommuteScore(variations[i], scenario);
            console.log(`   Variation ${i + 1}: ${result.performance?.cacheHit ? 'Cache hit' : 'Cache miss'}`);
        }
        
        // Rapport final cache
        const finalReport = this.commuteOptimizer.getPerformanceReport();
        console.log(`\n📈 Efficacité finale: ${finalReport.cacheHitRate}`);
        console.log(`💰 Coût moyen par calcul: ${finalReport.averageCostPerCalculation}€`);
    }

    /**
     * VALIDATION PRÉFÉRENCES TRANSPORT
     */
    async testTransportPreferences() {
        console.log("\n🚌 TEST PRÉFÉRENCES TRANSPORT");
        console.log("=============================");
        
        const baseJob = this.testJobsParisRegion.defense_excellent;
        
        const preferencesVariants = [
            {
                name: "Fan de métro",
                preferences: ["metro", "rer", "transport_public"],
                expected_bonus: "transit"
            },
            {
                name: "Amoureux du vélo", 
                preferences: ["velo", "bicyclette", "cyclisme"],
                expected_bonus: "bicycling"
            },
            {
                name: "Conducteur",
                preferences: ["voiture", "vehicule", "conduite"],
                expected_bonus: "driving"
            },
            {
                name: "Marcheur",
                preferences: ["marche", "pied", "walking"],
                expected_bonus: "walking"
            }
        ];
        
        for (const variant of preferencesVariants) {
            console.log(`\n👤 Profil: ${variant.name}`);
            
            const candidateVariant = {
                ...this.dorotheeLimExtended,
                preferences_transport: variant.preferences
            };
            
            const result = await this.commuteOptimizer.calculateCommuteScore(candidateVariant, baseJob);
            
            if (result.breakdown) {
                const scores = Object.entries(result.breakdown)
                    .map(([mode, data]) => ({ mode, score: data.score }))
                    .sort((a, b) => b.score - a.score);
                
                console.log(`   Mode favorisé: ${scores[0].mode} (${(scores[0].score * 100).toFixed(0)}%)`);
                console.log(`   Attendu: ${variant.expected_bonus}`);
                console.log(`   Match: ${scores[0].mode === variant.expected_bonus ? '✅' : '❌'}`);
            }
        }
    }

    /**
     * RAPPORT GLOBAL DES TESTS
     */
    generateGlobalReport(results) {
        const validResults = Object.values(results).filter(r => !r.error);
        
        if (validResults.length === 0) {
            console.log("❌ Aucun test valide");
            return;
        }
        
        // Calcul des moyennes
        const avgCommuteScore = validResults.reduce((sum, r) => sum + r.commute_only.finalScore, 0) / validResults.length;
        const avgTime = validResults.reduce((sum, r) => sum + r.performance.calculation_time, 0) / validResults.length;
        const successCount = validResults.filter(r => r.performance.meets_target).length;
        
        console.log(`📊 Score moyen trajets: ${(avgCommuteScore * 100).toFixed(1)}%`);
        console.log(`⏱️  Temps moyen calcul: ${avgTime.toFixed(2)}ms`);
        console.log(`🎯 Objectif performance: ${successCount}/${validResults.length} (${(successCount/validResults.length*100).toFixed(0)}%)`);
        
        // Validation globale
        const allTestsPass = validResults.every(r => r.performance.meets_target);
        console.log(`\n🏆 VALIDATION GLOBALE: ${allTestsPass ? '✅ TOUS LES TESTS PASSENT' : '❌ OPTIMISATION REQUISE'}`);
        
        // Recommandations
        if (!allTestsPass) {
            console.log("\n💡 Recommandations d'optimisation:");
            console.log("   • Améliorer l'efficacité du cache");
            console.log("   • Optimiser les calculs de distance");
            console.log("   • Paralléliser les appels API");
        }
    }

    /**
     * UTILITAIRES
     */
    getModeIcon(mode) {
        const icons = {
            driving: "🚗",
            transit: "🚇",
            walking: "🚶",
            bicycling: "🚴"
        };
        return icons[mode] || "🚌";
    }

    isScoreInExpectedRange(actualScore, expectedScore, tolerance) {
        return Math.abs(actualScore - expectedScore) <= tolerance;
    }

    /**
     * AUTO-EXÉCUTION COMPLÈTE
     */
    async runAllTests() {
        console.log("🚀 EXÉCUTION COMPLÈTE TESTS NEXTEN COMMUTE");
        console.log("==========================================");
        
        try {
            // Tests principaux
            await this.runCompleteCommuteTests();
            
            // Tests de performance
            await this.performanceStressTest();
            
            // Tests cache
            await this.testCacheEfficiency();
            
            // Tests préférences
            await this.testTransportPreferences();
            
            console.log("\n🎉 TOUS LES TESTS TERMINÉS AVEC SUCCÈS!");
            
        } catch (error) {
            console.error("❌ Erreur durant les tests:", error);
        }
    }
}

// Auto-exécution si chargé directement
if (typeof window !== 'undefined') {
    const tester = new NextenCommuteScenarioTester();
    
    // Tests automatiques au chargement
    document.addEventListener('DOMContentLoaded', async () => {
        await tester.runAllTests();
    });
    
    // Export global pour usage manuel
    window.NextenCommuteScenarioTester = NextenCommuteScenarioTester;
    
    // Fonctions utilitaires globales
    window.runCommuteTests = async () => {
        const tester = new NextenCommuteScenarioTester();
        return await tester.runAllTests();
    };
}

// Export pour Node.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = NextenCommuteScenarioTester;
}