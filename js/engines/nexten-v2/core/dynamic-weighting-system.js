/**
 * NEXTEN V2.0 - SYSTÈME DE PONDÉRATION DYNAMIQUE BASÉ SUR LES MOTIVATIONS
 * 
 * Ajuste automatiquement les poids des critères selon les priorités motivationnelles du candidat
 * Maintient la normalisation à 100% après ajustements
 */

class DynamicWeightingSystem {
    constructor() {
        // === PONDÉRATIONS DE BASE V2.0 (NORMALISÉES) ===
        this.baseWeights = {
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

        // === MAPPING MOTIVATIONS → CRITÈRES ===
        this.motivationToCriteria = {
            'remuneration': ['compensation'],
            'perspectives_evolution': ['semantic', 'companySize', 'industry'],
            'flexibilite': ['workEnvironment', 'contractType'],
            'localisation': ['location'],
            'autre': ['motivation'] // Fallback sur motivations générales
        };

        // === CONFIGURATION AJUSTEMENTS ===
        this.adjustmentConfig = {
            primary_boost: 0.08,       // +8% pour motivation #1
            secondary_boost: 0.05,     // +5% pour motivation #2
            tertiary_boost: 0.03,      // +3% pour motivation #3
            min_weight: 0.01,          // Poids minimum (1%)
            max_weight: 0.35           // Poids maximum (35%)
        };

        console.log('🎯 Système de pondération dynamique initialisé');
    }

    /**
     * CALCUL PONDÉRATION DYNAMIQUE PRINCIPALE
     * @param {Array} candidateMotivations - Motivations classées par ordre de priorité
     * @returns {Object} Pondérations ajustées et normalisées
     */
    calculateDynamicWeights(candidateMotivations) {
        console.log('⚡ Calcul pondération dynamique...', candidateMotivations);

        // Copie des poids de base
        const adjustedWeights = { ...this.baseWeights };
        
        // Validation des motivations
        if (!candidateMotivations || !Array.isArray(candidateMotivations) || candidateMotivations.length === 0) {
            console.warn('⚠️ Motivations invalides - utilisation poids de base');
            return {
                weights: adjustedWeights,
                adjustments: [],
                totalAdjustment: 0,
                isAdjusted: false
            };
        }

        const appliedAdjustments = [];
        let totalBoostApplied = 0;

        // === PHASE 1: APPLICATION DES BOOSTS ===
        candidateMotivations.slice(0, 3).forEach((motivation, index) => {
            const boost = this.getBoostForRank(index + 1);
            const affectedCriteria = this.motivationToCriteria[motivation] || [];

            if (affectedCriteria.length === 0) {
                console.warn(`⚠️ Motivation "${motivation}" non reconnue`);
                return;
            }

            // Distribution du boost entre les critères concernés
            const boostPerCriterion = boost / affectedCriteria.length;

            affectedCriteria.forEach(criterion => {
                if (adjustedWeights[criterion] !== undefined) {
                    const oldWeight = adjustedWeights[criterion];
                    adjustedWeights[criterion] += boostPerCriterion;
                    
                    // Respect des limites
                    adjustedWeights[criterion] = Math.min(
                        adjustedWeights[criterion], 
                        this.adjustmentConfig.max_weight
                    );

                    const actualBoost = adjustedWeights[criterion] - oldWeight;
                    totalBoostApplied += actualBoost;

                    appliedAdjustments.push({
                        motivation,
                        criterion,
                        rank: index + 1,
                        boost: actualBoost,
                        oldWeight: oldWeight,
                        newWeight: adjustedWeights[criterion],
                        percentage_change: Math.round((actualBoost / oldWeight) * 100)
                    });

                    console.log(`📈 ${criterion}: ${Math.round(oldWeight * 100)}% → ${Math.round(adjustedWeights[criterion] * 100)}% (+${Math.round(actualBoost * 100)}%)`);
                }
            });
        });

        // === PHASE 2: REDISTRIBUTION POUR NORMALISER À 100% ===
        const normalizedWeights = this.redistributeWeights(adjustedWeights, totalBoostApplied);

        // === PHASE 3: VALIDATION FINALE ===
        const validation = this.validateWeights(normalizedWeights);
        
        if (!validation.isValid) {
            console.error('❌ Erreur normalisation - retour aux poids de base');
            return {
                weights: this.baseWeights,
                adjustments: [],
                totalAdjustment: 0,
                isAdjusted: false,
                error: validation.error
            };
        }

        const result = {
            weights: normalizedWeights,
            adjustments: appliedAdjustments,
            totalAdjustment: totalBoostApplied,
            isAdjusted: appliedAdjustments.length > 0,
            summary: this.generateAdjustmentSummary(appliedAdjustments, normalizedWeights)
        };

        console.log('✅ Pondération dynamique calculée:', {
            adjustments: appliedAdjustments.length,
            totalBoost: Math.round(totalBoostApplied * 100) + '%'
        });

        return result;
    }

    /**
     * REDISTRIBUTION DES POIDS POUR NORMALISATION
     * Diminue proportionnellement les critères non boostés
     */
    redistributeWeights(adjustedWeights, totalBoostApplied) {
        console.log('🔄 Redistribution pour normalisation...');

        if (totalBoostApplied === 0) {
            return adjustedWeights;
        }

        // Calcul du facteur de réduction pour les critères non boostés
        const totalCurrentWeight = Object.values(adjustedWeights).reduce((sum, weight) => sum + weight, 0);
        const excessWeight = totalCurrentWeight - 1.0;

        if (Math.abs(excessWeight) < 0.001) {
            return adjustedWeights; // Déjà normalisé
        }

        // Identification des critères boostés (pour ne pas les diminuer)
        const boostedCriteria = new Set();
        Object.keys(this.motivationToCriteria).forEach(motivation => {
            this.motivationToCriteria[motivation].forEach(criterion => {
                boostedCriteria.add(criterion);
            });
        });

        // Calcul de la réduction nécessaire sur les critères non boostés
        const nonBoostedCriteria = Object.keys(adjustedWeights).filter(criterion => 
            !boostedCriteria.has(criterion)
        );

        if (nonBoostedCriteria.length === 0) {
            // Cas extrême : tous les critères sont boostés
            // Réduction proportionnelle sur tous
            const reductionFactor = 1.0 / totalCurrentWeight;
            Object.keys(adjustedWeights).forEach(criterion => {
                adjustedWeights[criterion] *= reductionFactor;
            });
        } else {
            // Réduction sur les critères non boostés uniquement
            const totalNonBoostedWeight = nonBoostedCriteria.reduce(
                (sum, criterion) => sum + adjustedWeights[criterion], 0
            );

            const targetReduction = excessWeight;
            const reductionFactor = Math.max(0, (totalNonBoostedWeight - targetReduction) / totalNonBoostedWeight);

            nonBoostedCriteria.forEach(criterion => {
                adjustedWeights[criterion] = Math.max(
                    adjustedWeights[criterion] * reductionFactor,
                    this.adjustmentConfig.min_weight
                );
            });
        }

        // Vérification finale et ajustement fin si nécessaire
        const finalTotal = Object.values(adjustedWeights).reduce((sum, weight) => sum + weight, 0);
        if (Math.abs(finalTotal - 1.0) > 0.001) {
            // Ajustement fin sur le critère avec le plus fort poids
            const maxWeightCriterion = Object.keys(adjustedWeights).reduce((max, criterion) => 
                adjustedWeights[criterion] > adjustedWeights[max] ? criterion : max
            );
            adjustedWeights[maxWeightCriterion] += (1.0 - finalTotal);
        }

        return adjustedWeights;
    }

    /**
     * OBTIENT LE BOOST SELON LE RANG DE LA MOTIVATION
     */
    getBoostForRank(rank) {
        switch (rank) {
            case 1: return this.adjustmentConfig.primary_boost;    // +8%
            case 2: return this.adjustmentConfig.secondary_boost;  // +5%
            case 3: return this.adjustmentConfig.tertiary_boost;   // +3%
            default: return 0;
        }
    }

    /**
     * VALIDATION DES POIDS FINAUX
     */
    validateWeights(weights) {
        const total = Object.values(weights).reduce((sum, weight) => sum + weight, 0);
        const tolerance = 0.01; // 1% de tolérance

        if (Math.abs(total - 1.0) > tolerance) {
            return {
                isValid: false,
                error: `Total des poids: ${Math.round(total * 100)}% (attendu: 100%)`
            };
        }

        // Vérification des limites individuelles
        for (const [criterion, weight] of Object.entries(weights)) {
            if (weight < 0 || weight > this.adjustmentConfig.max_weight) {
                return {
                    isValid: false,
                    error: `Poids invalide pour ${criterion}: ${Math.round(weight * 100)}%`
                };
            }
        }

        return { isValid: true };
    }

    /**
     * GÉNÈRE UN RÉSUMÉ DES AJUSTEMENTS
     */
    generateAdjustmentSummary(adjustments, finalWeights) {
        const summary = {
            totalAdjustments: adjustments.length,
            criteriaAffected: new Set(adjustments.map(adj => adj.criterion)).size,
            motivationsProcessed: new Set(adjustments.map(adj => adj.motivation)).size,
            majorChanges: adjustments.filter(adj => Math.abs(adj.percentage_change) >= 10),
            finalDistribution: {}
        };

        // Distribution finale par catégorie
        const categories = {
            'Core (Semantic + Location)': ['semantic', 'location'],
            'Questionnaires Enrichis': ['compensation', 'motivation', 'companySize', 'workEnvironment', 'industry', 'availability', 'contractType', 'listenReasons', 'processPosition']
        };

        Object.entries(categories).forEach(([categoryName, criteria]) => {
            const categoryWeight = criteria.reduce((sum, criterion) => 
                sum + (finalWeights[criterion] || 0), 0
            );
            summary.finalDistribution[categoryName] = Math.round(categoryWeight * 100) + '%';
        });

        return summary;
    }

    /**
     * INTÉGRATION AVEC LE SYSTÈME NEXTEN V2.0
     * Mise à jour des poids dans une instance NextenV2UnifiedSystem
     */
    integrateWithNextenV2(nextenV2Instance, candidateMotivations) {
        console.log('🔗 Intégration avec NEXTEN V2.0...');

        const dynamicResult = this.calculateDynamicWeights(candidateMotivations);
        
        if (dynamicResult.isAdjusted) {
            // Sauvegarde des poids originaux
            nextenV2Instance._originalWeights = { ...nextenV2Instance.v2CriteriaWeights };
            
            // Application des nouveaux poids
            nextenV2Instance.v2CriteriaWeights = dynamicResult.weights;
            
            // Ajout des métadonnées
            nextenV2Instance._dynamicWeightingApplied = {
                timestamp: new Date().toISOString(),
                candidateMotivations,
                adjustmentsSummary: dynamicResult.summary,
                adjustmentsDetail: dynamicResult.adjustments
            };

            console.log('✅ Pondération dynamique appliquée à NEXTEN V2.0');
        } else {
            console.log('ℹ️ Aucun ajustement nécessaire - poids de base conservés');
        }

        return dynamicResult;
    }

    /**
     * RESTAURATION DES POIDS ORIGINAUX
     */
    restoreOriginalWeights(nextenV2Instance) {
        if (nextenV2Instance._originalWeights) {
            nextenV2Instance.v2CriteriaWeights = nextenV2Instance._originalWeights;
            delete nextenV2Instance._originalWeights;
            delete nextenV2Instance._dynamicWeightingApplied;
            console.log('🔄 Poids originaux restaurés');
        }
    }
}

// Export pour intégration
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DynamicWeightingSystem;
}

if (typeof window !== 'undefined') {
    window.DynamicWeightingSystem = DynamicWeightingSystem;
    console.log('🎯 Système de pondération dynamique NEXTEN V2.0 disponible');
}