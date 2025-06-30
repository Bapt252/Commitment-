/**
 * NEXTEN SYSTEM TESTS - Validation Complète du Système 100%
 * Tests fonctionnels et de performance pour tous les critères
 */

class NextenSystemTests {
    constructor() {
        this.testResults = [];
        this.performanceMetrics = {
            totalTests: 0,
            passedTests: 0,
            failedTests: 0,
            averageExecutionTime: 0
        };
    }

    /**
     * DONNÉES DE TEST - PROFIL DOROTHÉE LIM
     * Candidat de référence pour validation système
     */
    getTestCandidateProfile() {
        return {
            id: 'dorothee_lim_test',
            nom: 'Lim',
            prenom: 'Dorothée',
            
            // Données géographiques
            adresse: '15 Rue de la Pompe, 75016 Paris',
            coordonnees: { lat: 48.8738, lng: 2.2754 },
            mobilite_acceptee: 'paris_banlieue',
            duree_trajet_max: '45min',
            preferences_transport: ['metro', 'rer', 'bus'],
            
            // Expérience professionnelle
            experiences: [
                {
                    intitule: 'Responsable Marketing Luxe',
                    entreprise: 'Chanel',
                    secteur: 'luxe',
                    date_debut: '2020-01-01',
                    date_fin: '2024-12-31',
                    missions: [
                        'Gestion portfolio produits parfums haut de gamme',
                        'Stratégie marketing digital luxury brands',
                        'Management équipe 8 personnes',
                        'Lancement produits exclusifs'
                    ],
                    description: 'Direction marketing opérationnel pour division parfums'
                },
                {
                    intitule: 'Chef de Produit Senior',
                    entreprise: 'L\'Oréal Luxe',
                    secteur: 'cosmétique',
                    date_debut: '2017-06-01',
                    date_fin: '2019-12-31',
                    missions: [
                        'Développement gamme skincare premium',
                        'Analyse concurrentielle marché beauté',
                        'Coordination équipes R&D et marketing',
                        'Gestion budget 2M€'
                    ]
                }
            ],
            
            // Compétences
            competences: [
                'Marketing Luxe', 'Gestion de Produit', 'Management d\'Équipe',
                'Stratégie Digitale', 'Codes Luxe', 'Parfumerie',
                'Cosmétique', 'Leadership', 'Budget Management',
                'Innovation Produit', 'Relation Client VIP'
            ],
            
            // Formation et langues
            niveau_etudes: 'Master Marketing Luxe ESSEC',
            langues: ['Français (natif)', 'Anglais (courant)', 'Mandarin (notions)'],
            certifications: ['Google Analytics', 'Certification Parfumerie ISIPCA'],
            
            // Préférences et contraintes
            salaire_actuel: 75000,
            pretentions: 85000,
            teletravail: 'hybrid_3_2',
            disponibilite: '2025-02-01',
            preavis: '3 mois',
            mobilite: 'paris_idf',
            heures_sup: 'occasionnellement',
            
            // Motivations et valeurs
            motivations: 'Passion pour l\'univers du luxe et la beauté. Recherche poste à responsabilités avec équipe à manager dans environnement créatif et exigeant.',
            objectifs: 'Évoluer vers direction marketing dans maison de luxe prestigieuse',
            valeurs: ['excellence', 'créativité', 'authenticité', 'innovation'],
            
            // Situation actuelle
            situation: 'En poste, recherche active pour évolution'
        };
    }

    /**
     * POSTE DE TEST - DIRECTEUR MARKETING LUXE
     */
    getTestJobOffer() {
        return {
            id: 'directeur_marketing_luxe_paris',
            intitule: 'Directeur Marketing - Division Parfums',
            entreprise: 'Maison de Luxe Parisienne',
            secteur: 'luxe',
            
            // Localisation
            adresse: '1 Place Vendôme, 75001 Paris',
            coordonnees: { lat: 48.8675, lng: 2.3292 },
            quartier: 'Place Vendôme',
            accessibilite: ['metro_1', 'metro_7', 'metro_14'],
            
            // Description poste
            description: `
                Nous recherchons un Directeur Marketing expérimenté pour diriger notre division parfums.
                Rattaché à la Direction Générale, vous piloterez la stratégie marketing globale de nos fragrances exclusives.
                Management d'une équipe de 12 personnes dans un environnement exigeant et créatif.
                Connaissance impérative des codes du luxe et expérience en parfumerie souhaitée.
                Déplacements réguliers (boutiques, événements, salons internationaux).
            `,
            
            // Exigences
            experience_requise: '8 ans minimum',
            niveau_poste: 'directeur',
            competences_requises: [
                'Marketing Luxe', 'Management', 'Parfumerie', 'Stratégie',
                'Codes Luxe', 'Leadership', 'Innovation', 'Budget'
            ],
            formation_requise: 'Master Marketing/Commerce',
            langues_requises: ['Français', 'Anglais'],
            
            // Conditions
            salaire: 95000,
            remuneration: 'Fixe + Variable + Avantages',
            teletravail: 'hybrid_2_3',
            horaires: 'flexible avec core hours 10h-16h',
            deplacement: 'régulier (5j/mois)',
            
            // Package
            avantages: [
                'Mutuelle premium',
                'Tickets restaurant',
                'Transport remboursé',
                'Formation continue',
                'Produits gratuits',
                'Participation événements'
            ],
            evolution_possible: 'excellent',
            
            // Urgence et timing
            date_prise_poste: '2025-03-01',
            urgence: 'normal',
            priorite: 'haute'
        };
    }

    /**
     * DONNÉES ENTREPRISE DE TEST
     */
    getTestCompanyData() {
        return {
            id: 'maison_luxe_paris',
            nom: 'Maison de Luxe Parisienne',
            secteur: 'luxe',
            taille: 'grande_entreprise',
            effectifs: 2500,
            
            // Culture entreprise
            valeurs: ['excellence', 'tradition', 'innovation', 'savoir_vivre'],
            culture: 'luxe_traditionnel',
            management_style: 'directif_bienveillant',
            
            // Politiques RH
            remote_policy: 'hybrid_2_3',
            horaires: 'flexible',
            formation: 'continue',
            
            // Avantages
            avantages: [
                'mutuelle', 'tickets_restaurant', 'transport',
                'formation', 'produits_gratuits', 'participation_evenements'
            ],
            
            // Localisation
            siege: 'Paris 1er',
            implantations: ['Paris', 'London', 'New York', 'Tokyo']
        };
    }

    /**
     * TEST COMPLET DU SYSTÈME
     */
    async runCompleteSystemTest() {
        console.log('🧪 NEXTEN COMPLETE SYSTEM TEST - Démarrage...\n');
        
        const testCandidate = this.getTestCandidateProfile();
        const testJob = this.getTestJobOffer();
        const testCompany = this.getTestCompanyData();
        
        // Initialisation du système
        const system = new NextenUnifiedSystem();
        
        try {
            // Test principal
            const startTime = performance.now();
            const result = await system.calculateCompleteMatchingScore(testCandidate, testJob, testCompany);
            const endTime = performance.now();
            
            const executionTime = endTime - startTime;
            
            // Validation des résultats
            const validationResults = this.validateSystemResults(result, executionTime);
            
            // Affichage des résultats
            this.displayTestResults(result, validationResults, executionTime);
            
            // Test de performance
            const performanceTests = await this.runPerformanceTests(system, testCandidate, testJob, testCompany);
            
            return {
                success: validationResults.overall,
                result: result,
                validation: validationResults,
                performance: performanceTests,
                executionTime: executionTime
            };
            
        } catch (error) {
            console.error('❌ Erreur lors du test système:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * VALIDATION DES RÉSULTATS
     */
    validateSystemResults(result, executionTime) {
        const validations = {
            structure: this.validateResultStructure(result),
            performance: this.validatePerformance(result, executionTime),
            scoring: this.validateScoring(result),
            consistency: this.validateConsistency(result),
            overall: false
        };
        
        validations.overall = Object.values(validations).every(v => v === true);
        return validations;
    }

    validateResultStructure(result) {
        const requiredFields = [
            'finalScore', 'qualityLevel', 'criteriaBreakdown',
            'insights', 'performance', 'metadata'
        ];
        
        const hasAllFields = requiredFields.every(field => result.hasOwnProperty(field));
        
        if (!hasAllFields) {
            console.log('❌ Structure incomplète');
            return false;
        }
        
        const requiredCriteria = ['semantic', 'commute', 'experience', 'cultural', 'availability', 'bonus'];
        const hasAllCriteria = requiredCriteria.every(criterion => 
            result.criteriaBreakdown.hasOwnProperty(criterion)
        );
        
        if (!hasAllCriteria) {
            console.log('❌ Critères manquants');
            return false;
        }
        
        console.log('✅ Structure des résultats valide');
        return true;
    }

    validatePerformance(result, executionTime) {
        const maxTime = 150; // 150ms max
        
        if (executionTime > maxTime) {
            console.log(`❌ Performance: ${executionTime.toFixed(1)}ms > ${maxTime}ms`);
            return false;
        }
        
        console.log(`✅ Performance: ${executionTime.toFixed(1)}ms < ${maxTime}ms`);
        return true;
    }

    validateScoring(result) {
        const score = result.finalScore;
        
        if (score < 0 || score > 1) {
            console.log(`❌ Score invalide: ${score}`);
            return false;
        }
        
        // Validation cohérence pondération
        const breakdown = result.criteriaBreakdown;
        const calculatedScore = (
            breakdown.semantic.score * breakdown.semantic.weight +
            breakdown.commute.score * breakdown.commute.weight +
            breakdown.experience.score * breakdown.experience.weight +
            breakdown.cultural.score * breakdown.cultural.weight +
            breakdown.availability.score * breakdown.availability.weight +
            breakdown.bonus.score * breakdown.bonus.weight
        );
        
        const scoreDifference = Math.abs(score - calculatedScore);
        if (scoreDifference > 0.05) {
            console.log(`❌ Incohérence scoring: ${score} vs ${calculatedScore}`);
            return false;
        }
        
        console.log(`✅ Scoring cohérent: ${(score * 100).toFixed(1)}%`);
        return true;
    }

    validateConsistency(result) {
        // Vérification que le profil test donne un bon score
        const expectedMinScore = 0.75; // Dorothée devrait avoir un bon score
        
        if (result.finalScore < expectedMinScore) {
            console.log(`⚠️  Score plus faible qu'attendu: ${(result.finalScore * 100).toFixed(1)}% < ${(expectedMinScore * 100)}%`);
            return false;
        }
        
        console.log('✅ Consistance des résultats validée');
        return true;
    }

    /**
     * TESTS DE PERFORMANCE
     */
    async runPerformanceTests(system, candidate, job, company) {
        console.log('\n🏃‍♂️ Tests de performance...');
        
        const iterations = 5;
        const times = [];
        
        for (let i = 0; i < iterations; i++) {
            const start = performance.now();
            await system.calculateCompleteMatchingScore(candidate, job, company);
            const end = performance.now();
            times.push(end - start);
        }
        
        const avgTime = times.reduce((a, b) => a + b, 0) / times.length;
        const minTime = Math.min(...times);
        const maxTime = Math.max(...times);
        
        console.log(`📊 Performance moyenne: ${avgTime.toFixed(1)}ms`);
        console.log(`⚡ Plus rapide: ${minTime.toFixed(1)}ms`);
        console.log(`🐌 Plus lent: ${maxTime.toFixed(1)}ms`);
        
        return {
            averageTime: avgTime,
            minTime: minTime,
            maxTime: maxTime,
            iterations: iterations
        };
    }

    /**
     * AFFICHAGE RÉSULTATS DÉTAILLÉS
     */
    displayTestResults(result, validations, executionTime) {
        console.log('\n📊 RÉSULTATS DU TEST SYSTÈME NEXTEN');
        console.log('=====================================');
        
        // Score global
        console.log(`🎯 Score Final: ${(result.finalScore * 100).toFixed(1)}%`);
        console.log(`🏆 Niveau Qualité: ${result.qualityLevel}`);
        console.log(`⏱️  Temps d'exécution: ${executionTime.toFixed(1)}ms`);
        
        // Breakdown par critère
        console.log('\n📋 Détail par Critère:');
        Object.entries(result.criteriaBreakdown).forEach(([criterion, data]) => {
            const score = (data.score * 100).toFixed(1);
            const weight = (data.weight * 100).toFixed(0);
            console.log(`  ${criterion}: ${score}% (poids: ${weight}%)`);
        });
        
        // Insights
        console.log('\n💡 Insights:');
        if (result.insights.strengths.length > 0) {
            console.log('  Forces:');
            result.insights.strengths.forEach(strength => {
                console.log(`    - ${strength.criterion}: ${(strength.score * 100).toFixed(0)}%`);
            });
        }
        
        if (result.insights.weaknesses.length > 0) {
            console.log('  Faiblesses:');
            result.insights.weaknesses.forEach(weakness => {
                console.log(`    - ${weakness.criterion}: ${(weakness.score * 100).toFixed(0)}%`);
            });
        }
        
        // Recommandations
        console.log('\n📝 Recommandations:');
        result.insights.recommendations.forEach(rec => {
            console.log(`  ${rec.priority}: ${rec.message}`);
        });
        
        // Validation
        console.log('\n✅ Validation:');
        Object.entries(validations).forEach(([test, passed]) => {
            const status = passed ? '✅' : '❌';
            console.log(`  ${status} ${test}`);
        });
        
        console.log('\n=====================================');
    }

    /**
     * TEST STRESS SYSTÈME
     */
    async runStressTest(iterations = 100) {
        console.log(`\n🔥 STRESS TEST - ${iterations} itérations...`);
        
        const system = new NextenUnifiedSystem();
        const candidate = this.getTestCandidateProfile();
        const job = this.getTestJobOffer();
        const company = this.getTestCompanyData();
        
        const results = [];
        const errors = [];
        
        for (let i = 0; i < iterations; i++) {
            try {
                const start = performance.now();
                const result = await system.calculateCompleteMatchingScore(candidate, job, company);
                const end = performance.now();
                
                results.push({
                    iteration: i,
                    score: result.finalScore,
                    time: end - start,
                    cacheHit: result.performance.cacheHit
                });
                
                if (i % 10 === 0) {
                    console.log(`  Progression: ${i}/${iterations}`);
                }
                
            } catch (error) {
                errors.push({ iteration: i, error: error.message });
            }
        }
        
        // Analyse des résultats
        const avgScore = results.reduce((sum, r) => sum + r.score, 0) / results.length;
        const avgTime = results.reduce((sum, r) => sum + r.time, 0) / results.length;
        const cacheHitRate = results.filter(r => r.cacheHit).length / results.length;
        
        console.log(`\n📊 Résultats Stress Test:`);
        console.log(`  ✅ Succès: ${results.length}/${iterations}`);
        console.log(`  ❌ Erreurs: ${errors.length}/${iterations}`);
        console.log(`  📊 Score moyen: ${(avgScore * 100).toFixed(1)}%`);
        console.log(`  ⏱️  Temps moyen: ${avgTime.toFixed(1)}ms`);
        console.log(`  🎯 Cache hit rate: ${(cacheHitRate * 100).toFixed(1)}%`);
        
        return {
            success: errors.length === 0,
            results: results,
            errors: errors,
            avgScore: avgScore,
            avgTime: avgTime,
            cacheHitRate: cacheHitRate
        };
    }
}

// Export pour utilisation
if (typeof module !== 'undefined' && module.exports) {
    module.exports = NextenSystemTests;
}

if (typeof window !== 'undefined') {
    window.NextenSystemTests = NextenSystemTests;
    
    // Auto-exécution du test si en mode debug
    if (window.location.search.includes('test=nexten')) {
        window.addEventListener('load', async () => {
            console.log('🚀 Auto-exécution des tests Nexten...');
            const tests = new NextenSystemTests();
            await tests.runCompleteSystemTest();
        });
    }
}
