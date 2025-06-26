/**
 * TEST COMPLET AVEC PROFIL DOROTHÉE LIM
 * Validation de l'algorithme avec données réelles CV Parser v6.2.0
 */

class NextenCompatibilityTester {
    constructor() {
        this.engine = new NextenCompatibilityEngine();
    }

    /**
     * DONNÉES RÉELLES DOROTHÉE LIM
     * Profil extrait du CV Parser v6.2.0 (17+ ans expérience secteur luxe)
     */
    getDorotheeProfileData() {
        return {
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
                        "Coordination événements luxe",
                        "Suivi administratif complet"
                    ]
                },
                {
                    poste: "Coordinatrice Administrative",
                    entreprise: "Dior",
                    date_debut: "2015",
                    date_fin: "2018",
                    missions: [
                        "Coordination équipes administratives",
                        "Gestion ERP et systèmes intégrés",
                        "Support opérationnel direction",
                        "Organisation événements mode",
                        "Relation client haut de gamme"
                    ]
                },
                {
                    poste: "Assistante Manager",
                    entreprise: "LVMH",
                    date_debut: "2012",
                    date_fin: "2015",
                    missions: [
                        "Support management équipes",
                        "Gestion administrative courante",
                        "Coordination inter-services",
                        "Suivi projets transversaux"
                    ]
                }
            ],
            competences_detaillees: [
                "SAP Business One",
                "ERP Management",
                "Microsoft Office Expert",
                "Gestion administrative",
                "Coordination équipes",
                "Planning et organisation",
                "Relation client VIP",
                "Secteur luxe et cosmétique",
                "MyEasyOrder",
                "Gestion de projets"
            ],
            competences_techniques: [
                "SAP",
                "ERP",
                "Excel avancé",
                "PowerPoint",
                "Outlook",
                "MyEasyOrder",
                "Systèmes intégrés"
            ],
            certifications: [
                "Certification SAP Business One",
                "Formation Microsoft Office Expert",
                "Certification Gestion de Projet"
            ],
            analyse_cv: {
                profil_type: "Profil expérimenté secteur luxe avec expertise administrative et systèmes ERP",
                niveau_experience: "Senior (17+ ans)",
                secteur_principal: "Luxe et Cosmétique",
                competences_cles: ["SAP", "ERP", "Office Management", "Coordination", "Secteur Luxe"]
            }
        };
    }

    /**
     * POSTES TYPES POUR TESTS
     * Différents niveaux de correspondance
     */
    getJobTestCases() {
        return {
            // CAS 1: Correspondance parfaite (score attendu 85-95%)
            perfect_match: {
                titre_poste: "Office Manager Secteur Luxe",
                mission_principale: "Coordination administrative et gestion ERP dans environnement luxe",
                competences: ["SAP", "Office Management", "Coordination équipes", "ERP", "Secteur luxe"],
                experience_requise: "10+ ans expérience administrative secteur luxe",
                missions: [
                    "Gestion administrative générale",
                    "Coordination des systèmes SAP",
                    "Support direction",
                    "Interface clients VIP"
                ]
            },

            // CAS 2: Bonne correspondance (score attendu 70-80%)
            good_match: {
                titre_poste: "Coordinatrice Administrative",
                mission_principale: "Coordination administrative et support direction",
                competences: ["Coordination", "Microsoft Office", "Gestion administrative", "Planning"],
                experience_requise: "5+ ans expérience administrative",
                missions: [
                    "Coordination équipes",
                    "Gestion planning",
                    "Support opérationnel",
                    "Organisation événements"
                ]
            },

            // CAS 3: Correspondance partielle (score attendu 40-60%)
            partial_match: {
                titre_poste: "Assistante Direction",
                mission_principale: "Support administratif à la direction",
                competences: ["Microsoft Office", "Organisation", "Communication"],
                experience_requise: "3+ ans expérience",
                missions: [
                    "Support direction",
                    "Gestion agenda",
                    "Communication interne"
                ]
            },

            // CAS 4: Correspondance faible (score attendu 10-30%)
            weak_match: {
                titre_poste: "Développeur Web",
                mission_principale: "Développement applications web",
                competences: ["JavaScript", "HTML", "CSS", "React"],
                experience_requise: "3+ ans développement",
                missions: [
                    "Développement frontend",
                    "Intégration API",
                    "Tests unitaires"
                ]
            }
        };
    }

    /**
     * EXÉCUTION DES TESTS COMPLETS
     */
    async runCompleteTests() {
        console.log("🧪 TESTS NEXTEN COMPATIBILITY ENGINE");
        console.log("======================================");
        
        const dorotheeProfil = this.getDorotheeProfileData();
        const testCases = this.getJobTestCases();
        
        const results = {};
        
        for (const [caseName, jobData] of Object.entries(testCases)) {
            console.log(`\n🔍 TEST: ${caseName.toUpperCase()}`);
            console.log("-".repeat(40));
            
            const result = await this.engine.calculateCompatibility(dorotheeProfil, jobData);
            results[caseName] = result;
            
            this.displayTestResult(caseName, result, jobData);
        }
        
        // Rapport de performance global
        console.log("\n📊 RAPPORT DE PERFORMANCE GLOBAL");
        console.log("=================================");
        const performanceReport = this.engine.getPerformanceReport();
        console.log(`Calculs totaux: ${performanceReport.totalCalculations}`);
        console.log(`Temps moyen: ${performanceReport.averageTime.toFixed(2)}ms`);
        console.log(`Taux cache hit: ${performanceReport.cacheHitRate}`);
        console.log(`Taille cache: ${performanceReport.cacheSize}`);
        
        return results;
    }

    /**
     * AFFICHAGE DÉTAILLÉ DES RÉSULTATS
     */
    displayTestResult(caseName, result, jobData) {
        const scorePercent = (result.score * 100).toFixed(1);
        const expectedRanges = {
            perfect_match: [85, 95],
            good_match: [70, 80],
            partial_match: [40, 60],
            weak_match: [10, 30]
        };
        
        const [minExpected, maxExpected] = expectedRanges[caseName] || [0, 100];
        const scoreInRange = result.score * 100 >= minExpected && result.score * 100 <= maxExpected;
        
        console.log(`📋 Poste: ${jobData.titre_poste}`);
        console.log(`🎯 Score final: ${scorePercent}% ${scoreInRange ? '✅' : '❌'} (attendu: ${minExpected}-${maxExpected}%)`);
        console.log(`⏱️  Temps calcul: ${result.performance.calculationTime.toFixed(2)}ms`);
        
        console.log("\n📈 BREAKDOWN DÉTAILLÉ:");
        console.log(`  • Titres: ${(result.breakdown.title.score * 100).toFixed(1)}% (poids: ${(result.breakdown.title.weight * 100).toFixed(0)}%)`);
        console.log(`  • Compétences: ${(result.breakdown.skills.score * 100).toFixed(1)}% (poids: ${(result.breakdown.skills.weight * 100).toFixed(0)}%)`);
        console.log(`  • Responsabilités: ${(result.breakdown.responsibilities.score * 100).toFixed(1)}% (poids: ${(result.breakdown.responsibilities.weight * 100).toFixed(0)}%)`);
        
        // Affichage des correspondances principales
        if (result.details.titleMatches.length > 0) {
            console.log(`\n🏷️  CORRESPONDANCES TITRES (${result.details.titleMatches.length}):`);
            result.details.titleMatches.slice(0, 3).forEach(match => {
                console.log(`  • "${match.candidateTitle}" ↔ "${match.jobTitle}" (${(match.similarity * 100).toFixed(1)}%)`);
            });
        }
        
        if (result.details.skillMatches.length > 0) {
            console.log(`\n🛠️  CORRESPONDANCES COMPÉTENCES (${result.details.skillMatches.length}):`);
            result.details.skillMatches.slice(0, 5).forEach(match => {
                console.log(`  • "${match.candidateSkill}" ↔ "${match.jobSkill}" (${(match.similarity * 100).toFixed(1)}%)`);
            });
        }
        
        // Pondération temporelle
        if (result.temporal.length > 0) {
            console.log(`\n⏰ PONDÉRATION TEMPORELLE:`);
            result.temporal.slice(0, 3).forEach(tw => {
                console.log(`  • ${tw.experience} chez ${tw.company}: ${(tw.weight * 100).toFixed(0)}% (${tw.yearsSince} ans)`);
            });
        }
    }

    /**
     * TEST DE PERFORMANCE SPÉCIFIQUE
     */
    async performanceStressTest() {
        console.log("\n⚡ TEST DE PERFORMANCE - STRESS TEST");
        console.log("====================================");
        
        const dorotheeProfil = this.getDorotheeProfileData();
        const perfectMatch = this.getJobTestCases().perfect_match;
        
        const iterations = 100;
        const startTime = performance.now();
        
        for (let i = 0; i < iterations; i++) {
            await this.engine.calculateCompatibility(dorotheeProfil, perfectMatch);
        }
        
        const totalTime = performance.now() - startTime;
        const avgTime = totalTime / iterations;
        
        console.log(`✅ ${iterations} calculs effectués`);
        console.log(`⏱️  Temps total: ${totalTime.toFixed(2)}ms`);
        console.log(`📊 Temps moyen: ${avgTime.toFixed(2)}ms`);
        console.log(`🚀 Performance: ${avgTime < 100 ? '✅ < 100ms (Objectif atteint)' : '❌ > 100ms (Optimisation requise)'}`);
        
        const finalReport = this.engine.getPerformanceReport();
        console.log(`💾 Efficacité cache: ${finalReport.cacheHitRate}`);
        
        return {
            iterations,
            totalTime,
            avgTime,
            performanceGoalMet: avgTime < 100,
            cacheEfficiency: finalReport.cacheHitRate
        };
    }

    /**
     * VALIDATION SECTEUR LUXE SPÉCIFIQUE
     */
    async validateLuxurySectorSpecialization() {
        console.log("\n💎 VALIDATION SPÉCIALISATION SECTEUR LUXE");
        console.log("==========================================");
        
        const dorotheeProfil = this.getDorotheeProfileData();
        
        // Test avec différentes entreprises luxe
        const luxuryJobs = [
            {
                titre_poste: "Office Manager",
                mission_principale: "Gestion administrative Hermès",
                competences: ["SAP", "Luxe", "ERP"],
                context: "Hermès (même entreprise)"
            },
            {
                titre_poste: "Coordinatrice", 
                mission_principale: "Coordination Chanel",
                competences: ["Coordination", "Luxury", "Management"],
                context: "Chanel (concurrent luxe)"
            },
            {
                titre_poste: "Assistante",
                mission_principale: "Support Louis Vuitton",
                competences: ["Office", "LVMH", "Support"],
                context: "Louis Vuitton (même groupe)"
            }
        ];
        
        for (const job of luxuryJobs) {
            const result = await this.engine.calculateCompatibility(dorotheeProfil, job);
            console.log(`\n${job.context}:`);
            console.log(`  Score: ${(result.score * 100).toFixed(1)}%`);
            console.log(`  Secteur détecté candidat: ${this.engine.detectSector(dorotheeProfil)}`);
            console.log(`  Secteur détecté poste: ${this.engine.detectJobSector(job)}`);
        }
    }
}

// Auto-exécution des tests si chargé directement
if (typeof window !== 'undefined') {
    const tester = new NextenCompatibilityTester();
    
    // Tests automatiques au chargement
    document.addEventListener('DOMContentLoaded', async () => {
        await tester.runCompleteTests();
        await tester.performanceStressTest();
        await tester.validateLuxurySectorSpecialization();
    });
    
    // Export global pour usage manuel
    window.NextenCompatibilityTester = NextenCompatibilityTester;
}

// Export pour Node.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = NextenCompatibilityTester;
}