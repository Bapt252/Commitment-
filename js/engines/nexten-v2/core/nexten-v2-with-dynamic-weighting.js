/**
 * NEXTEN V2.0 - EXTENSION PONDÉRATION DYNAMIQUE
 * 
 * Extension de NextenV2UnifiedSystem avec système de pondération basé sur motivations
 * Intègre le DynamicWeightingSystem de manière transparente
 */

class NextenV2WithDynamicWeighting extends NextenV2UnifiedSystem {
    constructor() {
        super();
        
        // Chargement du système de pondération dynamique
        this.dynamicWeightingSystem = new DynamicWeightingSystem();
        
        // Correction des pondérations de base pour correspondre aux valeurs normalisées
        this.v2CriteriaWeights = {
            semantic: 0.205,           // 20.5% - Compatibilité Sémantique
            compensation: 0.196,       // 19.6% - Rémunération (PRIORITAIRE)
            location: 0.161,           // 16.1% - Géolocalisation
            motivation: 0.107,         // 10.7% - Motivations
            companySize: 0.071,        // 7.1% - Taille Entreprise
            workEnvironment: 0.071,    // 7.1% - Environnement Travail
            industry: 0.054,           // 5.4% - Secteur d'Activité
            availability: 0.045,       // 4.5% - Disponibilité
            contractType: 0.045,       // 4.5% - Type de Contrat
            listenReasons: 0.027,      // 2.7% - Anti-patterns
            processPosition: 0.018     // 1.8% - Position Processus
        };
        
        console.log('🎯 NEXTEN V2.0 avec pondération dynamique initialisé');
    }

    /**
     * CALCUL MATCHING AVEC PONDÉRATION DYNAMIQUE AUTOMATIQUE
     * Version principale - détecte automatiquement les motivations
     */
    async calculateV2MatchingScoreWithDynamicWeights(candidateData, jobData, companyData = {}) {
        const startTime = performance.now();
        console.log('🎯 Calcul matching avec pondération dynamique...');

        try {
            // === PHASE 1: EXTRACTION DES MOTIVATIONS ===
            const candidateMotivations = this.extractCandidateMotivations(candidateData);
            
            if (candidateMotivations.length > 0) {
                console.log('📋 Motivations détectées:', candidateMotivations);
            } else {
                console.log('ℹ️ Aucune motivation détectée - utilisation pondération standard');
            }

            // === PHASE 2: APPLICATION PONDÉRATION DYNAMIQUE ===
            let weightingResult = null;
            if (candidateMotivations.length > 0) {
                weightingResult = this.dynamicWeightingSystem.integrateWithNextenV2(this, candidateMotivations);
            }

            // === PHASE 3: CALCUL MATCHING AVEC PONDÉRATION AJUSTÉE ===
            const matchingResult = await this.calculateV2MatchingScore(candidateData, jobData, companyData);

            // === PHASE 4: ENRICHISSEMENT DU RÉSULTAT ===
            if (weightingResult && weightingResult.isAdjusted) {
                matchingResult.dynamicWeighting = {
                    applied: true,
                    candidateMotivations,
                    adjustmentsSummary: weightingResult.summary,
                    adjustmentsDetail: weightingResult.adjustments,
                    impactAnalysis: this.analyzeWeightingImpact(weightingResult),
                    weightComparison: this.compareWeights(this.dynamicWeightingSystem.baseWeights, weightingResult.weights)
                };
                
                console.log('✅ Pondération dynamique appliquée:', {
                    adjustments: weightingResult.adjustments.length,
                    majorChanges: weightingResult.summary.majorChanges.length
                });
            } else {
                matchingResult.dynamicWeighting = {
                    applied: false,
                    reason: candidateMotivations.length === 0 ? 'no_motivations' : 'no_adjustment_needed',
                    candidateMotivations
                };
            }

            // === PHASE 5: MÉTRIQUES PERFORMANCE ===
            matchingResult.performance.dynamicWeightingTime = performance.now() - startTime - matchingResult.performance.calculationTime;
            
            return matchingResult;

        } catch (error) {
            console.error('❌ Erreur pondération dynamique:', error);
            // Fallback vers calcul standard
            const standardResult = await this.calculateV2MatchingScore(candidateData, jobData, companyData);
            standardResult.dynamicWeighting = {
                applied: false,
                error: error.message,
                fallback: true
            };
            return standardResult;
            
        } finally {
            // === RESTAURATION DES POIDS ORIGINAUX ===
            this.dynamicWeightingSystem.restoreOriginalWeights(this);
        }
    }

    /**
     * EXTRACTION DES MOTIVATIONS DU CANDIDAT
     * Supporte plusieurs formats de données questionnaire
     */
    extractCandidateMotivations(candidateData) {
        console.log('🔍 Extraction des motivations candidat...');
        
        // Format 1: Array direct des motivations ordonnées
        if (candidateData.motivations && Array.isArray(candidateData.motivations)) {
            const validMotivations = candidateData.motivations.filter(motivation => 
                motivation && typeof motivation === 'string' && motivation.trim() !== ''
            );
            console.log('📋 Format array détecté:', validMotivations);
            return validMotivations;
        }

        // Format 2: Champs séparés motivation_1, motivation_2, motivation_3
        const motivations = [];
        for (let i = 1; i <= 5; i++) {
            const motivationField = candidateData[`motivation_${i}`] || candidateData[`motiv_${i}`];
            if (motivationField && typeof motivationField === 'string' && motivationField.trim() !== '') {
                motivations.push(motivationField.trim().toLowerCase());
            }
        }
        
        if (motivations.length > 0) {
            console.log('📋 Format champs séparés détecté:', motivations);
            return motivations;
        }

        // Format 3: Objet avec ranking
        if (candidateData.motivations_ranking) {
            const ranked = Object.entries(candidateData.motivations_ranking)
                .sort(([,a], [,b]) => a - b) // Tri par ordre de priorité
                .map(([motivation, rank]) => motivation);
            console.log('📋 Format ranking détecté:', ranked);
            return ranked;
        }

        // Format 4: Analyse des préférences questionnaire
        const inferredMotivations = this.inferMotivationsFromQuestionnaire(candidateData);
        if (inferredMotivations.length > 0) {
            console.log('🔍 Motivations inférées du questionnaire:', inferredMotivations);
            return inferredMotivations;
        }

        console.log('⚠️ Aucune motivation détectée');
        return [];
    }

    /**
     * INFÉRENCE DES MOTIVATIONS À PARTIR DU QUESTIONNAIRE
     * Analyse les réponses pour déduire les priorités
     */
    inferMotivationsFromQuestionnaire(candidateData) {
        const inferredMotivations = [];
        
        // Analyse rémunération
        if (candidateData.pretentions_salariales && 
            (candidateData.negociation_salariale === 'importante' || 
             candidateData.priorite_salaire === 'elevee')) {
            inferredMotivations.push('remuneration');
        }

        // Analyse localisation
        if (candidateData.ville && candidateData.zone_geographique_fixe === 'oui') {
            inferredMotivations.push('localisation');
        }

        // Analyse flexibilité
        if (candidateData.mode_travail_prefere === 'remote' || 
            candidateData.mode_travail_prefere === 'hybride' ||
            candidateData.flexibilite_horaires === 'importante') {
            inferredMotivations.push('flexibilite');
        }

        // Analyse évolution
        if (candidateData.perspectives_evolution === 'importante' ||
            candidateData.ambitions_carriere === 'elevees') {
            inferredMotivations.push('perspectives_evolution');
        }

        return inferredMotivations;
    }

    /**
     * ANALYSE DE L'IMPACT DE LA PONDÉRATION
     * Évalue l'effet des ajustements sur le score final
     */
    analyzeWeightingImpact(weightingResult) {
        const impact = {
            significantChanges: [],
            potentialScoreImprovement: 0,
            riskAreas: [],
            recommendations: []
        };

        // Analyse des changements significatifs
        weightingResult.adjustments.forEach(adjustment => {
            if (Math.abs(adjustment.percentage_change) >= 15) {
                impact.significantChanges.push({
                    criterion: adjustment.criterion,
                    change: adjustment.percentage_change,
                    motivation: adjustment.motivation,
                    newWeight: Math.round(adjustment.newWeight * 100) + '%'
                });
            }
        });

        // Estimation de l'amélioration potentielle du score
        const totalWeightIncrease = weightingResult.adjustments
            .filter(adj => adj.boost > 0)
            .reduce((sum, adj) => sum + adj.boost, 0);
        
        impact.potentialScoreImprovement = Math.round(totalWeightIncrease * 0.3 * 100); // Estimation conservative

        // Identification des zones de risque
        Object.entries(weightingResult.weights).forEach(([criterion, weight]) => {
            if (weight < 0.02) { // Poids très faible
                impact.riskAreas.push({
                    criterion,
                    issue: 'poids_tres_faible',
                    weight: Math.round(weight * 100) + '%'
                });
            }
            if (weight > 0.30) { // Poids très élevé
                impact.riskAreas.push({
                    criterion,
                    issue: 'poids_tres_eleve',
                    weight: Math.round(weight * 100) + '%'
                });
            }
        });

        // Recommandations
        if (impact.significantChanges.length > 0) {
            impact.recommendations.push('Mettre l\'accent sur les critères ajustés lors de l\'entretien');
        }
        
        if (impact.potentialScoreImprovement > 5) {
            impact.recommendations.push('Pondération favorable - candidat aligné avec ses motivations');
        }

        return impact;
    }

    /**
     * COMPARAISON DES POIDS AVANT/APRÈS
     * Génère un rapport détaillé des changements
     */
    compareWeights(originalWeights, adjustedWeights) {
        const comparison = {
            changes: {},
            summary: {
                increased: 0,
                decreased: 0,
                unchanged: 0,
                totalVariation: 0
            }
        };

        Object.keys(originalWeights).forEach(criterion => {
            const originalWeight = originalWeights[criterion];
            const adjustedWeight = adjustedWeights[criterion];
            const change = adjustedWeight - originalWeight;
            const percentageChange = Math.round((change / originalWeight) * 100);

            comparison.changes[criterion] = {
                original: Math.round(originalWeight * 100) + '%',
                adjusted: Math.round(adjustedWeight * 100) + '%',
                change: (change >= 0 ? '+' : '') + Math.round(change * 100) + '%',
                percentageChange,
                direction: change > 0.005 ? 'increased' : (change < -0.005 ? 'decreased' : 'unchanged')
            };

            // Mise à jour du résumé
            if (change > 0.005) {
                comparison.summary.increased++;
            } else if (change < -0.005) {
                comparison.summary.decreased++;
            } else {
                comparison.summary.unchanged++;
            }

            comparison.summary.totalVariation += Math.abs(change);
        });

        comparison.summary.totalVariation = Math.round(comparison.summary.totalVariation * 100) + '%';

        return comparison;
    }

    /**
     * MODE TEST - SIMULATION PONDÉRATION SANS APPLICATION
     * Permet d'analyser l'impact avant application réelle
     */
    simulateDynamicWeighting(candidateMotivations) {
        console.log('🧪 Simulation pondération dynamique...');
        
        const simulation = this.dynamicWeightingSystem.calculateDynamicWeights(candidateMotivations);
        
        return {
            wouldBeAdjusted: simulation.isAdjusted,
            adjustments: simulation.adjustments,
            weightComparison: this.compareWeights(this.v2CriteriaWeights, simulation.weights),
            impactPreview: simulation.isAdjusted ? this.analyzeWeightingImpact(simulation) : null,
            recommendations: this.generateSimulationRecommendations(simulation)
        };
    }

    /**
     * RECOMMANDATIONS BASÉES SUR LA SIMULATION
     */
    generateSimulationRecommendations(simulation) {
        const recommendations = [];

        if (!simulation.isAdjusted) {
            recommendations.push({
                type: 'info',
                message: 'Aucun ajustement de pondération avec ces motivations'
            });
            return recommendations;
        }

        // Recommandations selon les ajustements
        simulation.adjustments.forEach(adjustment => {
            if (adjustment.percentage_change >= 20) {
                recommendations.push({
                    type: 'attention',
                    criterion: adjustment.criterion,
                    message: `Fort ajustement prévu (+${adjustment.percentage_change}%) - s'assurer de la qualité des données`
                });
            }
        });

        if (simulation.summary.majorChanges.length > 3) {
            recommendations.push({
                type: 'optimization',
                message: 'Nombreux ajustements prévus - profil candidat avec motivations claires'
            });
        }

        return recommendations;
    }

    /**
     * MÉTHODE DE DIAGNOSTIC
     * Vérifie la configuration et les poids
     */
    diagnosticDynamicWeighting() {
        console.log('🔧 Diagnostic du système de pondération dynamique...');
        
        const diagnostic = {
            systemStatus: 'operational',
            baseWeightsValid: false,
            mappingComplete: false,
            issues: [],
            recommendations: []
        };

        // Vérification des poids de base
        const totalBaseWeight = Object.values(this.v2CriteriaWeights).reduce((sum, weight) => sum + weight, 0);
        if (Math.abs(totalBaseWeight - 1.0) < 0.01) {
            diagnostic.baseWeightsValid = true;
        } else {
            diagnostic.issues.push(`Poids de base non normalisés: ${Math.round(totalBaseWeight * 100)}%`);
        }

        // Vérification du mapping motivations → critères
        const availableCriteria = Object.keys(this.v2CriteriaWeights);
        const mappedCriteria = new Set();
        
        Object.values(this.dynamicWeightingSystem.motivationToCriteria).forEach(criteria => {
            criteria.forEach(criterion => mappedCriteria.add(criterion));
        });

        const unmappedCriteria = availableCriteria.filter(criterion => !mappedCriteria.has(criterion));
        
        if (unmappedCriteria.length === 0) {
            diagnostic.mappingComplete = true;
        } else {
            diagnostic.issues.push(`Critères non mappés: ${unmappedCriteria.join(', ')}`);
        }

        // Génération des recommandations
        if (diagnostic.issues.length === 0) {
            diagnostic.recommendations.push('Système prêt pour utilisation en production');
        } else {
            diagnostic.recommendations.push('Corriger les problèmes identifiés avant utilisation');
        }

        console.log('🔧 Diagnostic terminé:', diagnostic);
        return diagnostic;
    }
}

// Export pour intégration
if (typeof module !== 'undefined' && module.exports) {
    module.exports = NextenV2WithDynamicWeighting;
}

if (typeof window !== 'undefined') {
    window.NextenV2WithDynamicWeighting = NextenV2WithDynamicWeighting;
    console.log('🎯 NEXTEN V2.0 avec pondération dynamique disponible');
}