/**
 * NEXTEN V2.0 OPTIMIZED - ENHANCED CONTRACT TYPE MATCHING
 * Mise à jour du critère contractType pour intégrer la logique sophistiquée
 * du questionnaire candidat avec gestion des préférences avancées
 * 
 * @version 2.0-OPTIMIZED-ENHANCED
 * @author NEXTEN Team  
 * @date 2025-06-30
 * 
 * CHANGEMENTS MAJEURS:
 * - Intégration complète des données du questionnaire sophistiqué
 * - Scoring nuancé: Exact 100%, Préférentiel 80%, Acceptable 70%, Non-match 0%
 * - Gestion des niveaux: exclusive, preferred, acceptable, flexible
 * - Compatibilité totale avec l'existant maintenue
 * - Fallbacks intelligents pour les anciennes données
 */

(function() {
    'use strict';
    
    /**
     * AMÉLIORATION DU CRITÈRE CONTRACT TYPE POUR NEXTEN V2.0
     * Remplace la méthode existante par une version sophistiquée
     */
    function enhanceContractTypeCriterion() {
        
        // Vérifier que NEXTEN V2.0 est disponible
        if (typeof NextenV2OptimizedSystem === 'undefined') {
            console.warn('⚠️ NEXTEN V2.0 System non trouvé - mise à jour reportée');
            return;
        }
        
        console.log('🔄 Mise à jour du critère Contract Type pour NEXTEN V2.0...');
        
        // Configuration du scoring sophistiqué selon les exigences
        const scoringConfig = {
            exactMatch: 1.0,        // 100% - Correspondance exacte
            preferential: 0.8,      // 80% - Correspondance préférentielle  
            acceptable: 0.7,        // 70% - Correspondance acceptable
            nonMatch: 0.0          // 0% - Non-correspondance
        };
        
        // Mapping des types de contrats
        const contractTypes = {
            'cdi': 'CDI',
            'cdd': 'CDD', 
            'freelance': 'Freelance',
            'interim': 'Intérim'
        };
        
        /**
         * NOUVELLE MÉTHODE calculateContractTypeCriterion SOPHISTIQUÉE
         * Remplace complètement l'ancienne méthode (pondération maintenue à 4.5%)
         */
        NextenV2OptimizedSystem.prototype.calculateContractTypeCriterion = async function(candidateData, jobData, options = {}) {
            const startTime = performance.now();
            
            try {
                console.log('💼 Calcul critère Contract Type sophistiqué - NEXTEN V2.0 Enhanced');
                
                // Extraction des données candidat depuis le questionnaire
                const candidateContractData = extractCandidateContractData(candidateData);
                const jobContractType = extractJobContractType(jobData);
                
                // Validation des données
                if (!validateContractData(candidateContractData, jobContractType)) {
                    console.warn('⚠️ Données invalides - fallback activé');
                    return getContractFallbackResult(candidateData, jobData);
                }
                
                // Calcul du score sophistiqué
                const matchingResult = calculateContractMatchingScore(
                    candidateContractData, 
                    jobContractType
                );
                
                // Construction du résultat final
                const result = {
                    score: matchingResult.score,
                    details: {
                        candidatePreferences: candidateContractData,
                        jobContractType: jobContractType,
                        matchType: matchingResult.matchType,
                        reasoning: matchingResult.reasoning,
                        scoringBreakdown: matchingResult.breakdown,
                        algorithm: "enhanced_contract_matching_v2",
                        calculationTime: performance.now() - startTime,
                        nextenV2Enhanced: true,
                        questionnaireIntegrated: true
                    },
                    confidence: matchingResult.confidence,
                    fallback: false
                };
                
                console.log('✅ Contract Type Score:', result.score);
                console.log('🎯 Match Type:', result.details.matchType);
                
                return result;
                
            } catch (error) {
                console.error('❌ Erreur Contract Type sophistiqué:', error);
                return getContractFallbackResult(candidateData, jobData);
            }
        };
        
        /**
         * Extraction et parsing des données contractuelles du candidat
         */
        function extractCandidateContractData(candidateData) {
            // Données du questionnaire sophistiqué (priorité 1)
            const contractData = candidateData.contractData || {};
            
            // Données des champs cachés du questionnaire (priorité 2)
            const selectedTypesField = candidateData['contract-types-selected'];
            const preferenceLevelField = candidateData['contract-preference-level'];
            const primaryChoiceField = candidateData['contract-primary-choice'];
            
            // Données legacy (priorité 3)
            const legacyContractType = candidateData.contractType || 
                                      candidateData.type_contrat_souhaite;
            
            // Prioriser les nouvelles données du questionnaire sophistiqué
            if (contractData.selectedTypes && contractData.selectedTypes.length > 0) {
                return {
                    selectedTypes: Array.isArray(contractData.selectedTypes) 
                        ? contractData.selectedTypes 
                        : contractData.selectedTypes.split(','),
                    preferenceLevel: contractData.preferenceLevel,
                    primaryChoice: contractData.primaryChoice,
                    isValid: contractData.isValid !== false,
                    source: 'questionnaire_enhanced'
                };
            }
            
            // Utiliser les champs cachés du questionnaire
            if (selectedTypesField && preferenceLevelField) {
                return {
                    selectedTypes: selectedTypesField.split(',').filter(t => t.trim()),
                    preferenceLevel: preferenceLevelField,
                    primaryChoice: primaryChoiceField || selectedTypesField.split(',')[0],
                    isValid: true,
                    source: 'questionnaire_fields'
                };
            }
            
            // Fallback vers l'ancien système
            if (legacyContractType) {
                return {
                    selectedTypes: [legacyContractType],
                    preferenceLevel: 'flexible',
                    primaryChoice: legacyContractType,
                    isValid: true,
                    source: 'legacy_system'
                };
            }
            
            // Données par défaut (CDI flexible)
            return {
                selectedTypes: ['cdi'],
                preferenceLevel: 'flexible',
                primaryChoice: 'cdi',
                isValid: false,
                source: 'default'
            };
        }
        
        /**
         * Extraction du type de contrat du poste
         */
        function extractJobContractType(jobData) {
            return jobData.contractType || 
                   jobData.type_contrat || 
                   jobData.contract_type || 
                   'cdi'; // Défaut CDI
        }
        
        /**
         * Validation des données contractuelles
         */
        function validateContractData(candidateContractData, jobContractType) {
            const validTypes = Object.keys(contractTypes);
            
            const candidateTypesValid = candidateContractData.selectedTypes.every(
                type => validTypes.includes(type)
            );
            
            const jobTypeValid = validTypes.includes(jobContractType);
            
            return candidateTypesValid && jobTypeValid;
        }
        
        /**
         * CŒUR DE LA LOGIQUE : Calcul sophistiqué du score de matching
         * Implémente exactement les exigences spécifiées
         */
        function calculateContractMatchingScore(candidateContractData, jobContractType) {
            const { selectedTypes, preferenceLevel, primaryChoice } = candidateContractData;
            
            console.log('📊 Calcul scoring contractuel sophistiqué:');
            console.log('   Types acceptés:', selectedTypes);
            console.log('   Niveau préférence:', preferenceLevel);
            console.log('   Choix principal:', primaryChoice);
            console.log('   Type poste:', jobContractType);
            
            // ÉTAPE 1: Vérifier si le type est accepté
            const isTypeAccepted = selectedTypes.includes(jobContractType);
            
            if (!isTypeAccepted) {
                console.log('❌ Type de contrat NON accepté par le candidat');
                return {
                    score: scoringConfig.nonMatch, // 0%
                    matchType: 'non_match',
                    reasoning: `❌ INCOMPATIBLE: Le candidat n'accepte pas le type ${contractTypes[jobContractType]}. Types acceptés: ${selectedTypes.map(t => contractTypes[t]).join(', ')}`,
                    breakdown: {
                        typeAccepted: false,
                        preferenceLevel: preferenceLevel,
                        selectedTypes: selectedTypes,
                        jobType: jobContractType,
                        finalScore: scoringConfig.nonMatch
                    },
                    confidence: 0.95
                };
            }
            
            console.log('✅ Type de contrat accepté - calcul du score selon préférence');
            
            // ÉTAPE 2: Calcul selon le niveau de préférence (selon exigences)
            let score;
            let matchType;
            let reasoning;
            
            switch (preferenceLevel) {
                case 'exclusive':
                    // 🔒 MODE EXCLUSIF - Recherche UNIQUEMENT ce type
                    if (selectedTypes.length === 1 && selectedTypes[0] === jobContractType) {
                        score = scoringConfig.exactMatch; // 100%
                        matchType = 'exclusive_perfect_match';
                        reasoning = `🎯 PARFAIT: Correspondance exacte exclusive pour ${contractTypes[jobContractType]}`;
                    } else {
                        // Cas d'erreur du questionnaire - ne devrait pas arriver
                        score = scoringConfig.acceptable; // 70%
                        matchType = 'exclusive_partial';
                        reasoning = `⚠️ Mode exclusif incohérent - score ajusté pour ${contractTypes[jobContractType]}`;
                    }
                    break;
                    
                case 'preferred':
                    // ❤️ PRÉFÉRENCE FORTE - Aime particulièrement certains types
                    if (primaryChoice === jobContractType) {
                        score = scoringConfig.exactMatch; // 100%
                        matchType = 'primary_preference_match';
                        reasoning = `🌟 EXCELLENT: ${contractTypes[jobContractType]} est le type PRÉFÉRÉ du candidat`;
                    } else {
                        score = scoringConfig.preferential; // 80%
                        matchType = 'secondary_preference_match';
                        reasoning = `👍 BON: Le candidat accepte ${contractTypes[jobContractType]} mais préfère ${contractTypes[primaryChoice]}`;
                    }
                    break;
                    
                case 'acceptable':
                    // ✅ ACCEPTABLE - Trouve ces types corrects sans plus
                    if (primaryChoice === jobContractType) {
                        score = scoringConfig.preferential; // 80%
                        matchType = 'acceptable_primary';
                        reasoning = `👌 BON: ${contractTypes[jobContractType]} est acceptable et correspond au choix principal`;
                    } else {
                        score = scoringConfig.acceptable; // 70%
                        matchType = 'acceptable_secondary';
                        reasoning = `✅ CORRECT: Le candidat trouve les ${contractTypes[jobContractType]} acceptables`;
                    }
                    break;
                    
                case 'flexible':
                    // 🤝 FLEXIBLE - Ouvert à tous les types sélectionnés
                    score = scoringConfig.preferential; // 80%
                    matchType = 'flexible_match';
                    reasoning = `🤝 BON: Le candidat est flexible sur tous ses types sélectionnés, dont ${contractTypes[jobContractType]}`;
                    break;
                    
                default:
                    // Fallback pour niveau inconnu
                    score = scoringConfig.acceptable; // 70%
                    matchType = 'default_match';
                    reasoning = `⚙️ DÉFAUT: Correspondance par défaut pour ${contractTypes[jobContractType]}`;
            }
            
            console.log(`🎯 Score final: ${score} (${Math.round(score * 100)}%)`);
            
            return {
                score,
                matchType,
                reasoning,
                breakdown: {
                    typeAccepted: true,
                    preferenceLevel: preferenceLevel,
                    isPrimaryChoice: primaryChoice === jobContractType,
                    selectedTypesCount: selectedTypes.length,
                    jobType: jobContractType,
                    scoringRule: `${preferenceLevel} → ${Math.round(score * 100)}%`,
                    finalScore: score
                },
                confidence: 0.90
            };
        }
        
        /**
         * Résultat de fallback en cas d'erreur
         */
        function getContractFallbackResult(candidateData, jobData) {
            console.log('🔄 Activation du fallback Contract Type...');
            
            const candidateType = candidateData.contractType || 
                                candidateData.type_contrat_souhaite || 
                                'cdi';
            const jobType = jobData.contractType || 
                          jobData.type_contrat || 
                          'cdi';
            
            // Matrice de compatibilité simple pour fallback
            const simpleCompatibility = {
                cdi: { cdi: 0.95, cdd: 0.6, freelance: 0.3, interim: 0.3 },
                cdd: { cdi: 0.8, cdd: 0.95, freelance: 0.7, interim: 0.6 },
                freelance: { cdi: 0.4, cdd: 0.7, freelance: 0.95, interim: 0.4 },
                interim: { cdi: 0.4, cdd: 0.6, freelance: 0.4, interim: 0.95 }
            };
            
            const score = simpleCompatibility[candidateType]?.[jobType] || 0.7;
            
            return {
                score,
                details: {
                    candidateType,
                    jobType,
                    compatibilityMatrix: simpleCompatibility[candidateType],
                    fallback: true,
                    method: 'simple_compatibility_matrix',
                    reasoning: `Fallback: Compatibilité ${candidateType} ↔ ${jobType}`,
                    algorithm: "fallback_contract_matching",
                    calculationTime: performance.now() - startTime
                },
                confidence: 0.70,
                fallback: true
            };
        }
        
        console.log('✅ Critère Contract Type sophistiqué intégré dans NEXTEN V2.0');
        console.log('📊 Scoring configuré selon exigences:');
        console.log('   - Correspondance exacte (candidat cherche CDI + poste CDI): 100%');
        console.log('   - Correspondance préférentielle (candidat préfère CDI, accepte CDD + poste CDD): 80%');
        console.log('   - Correspondance acceptable (candidat accepte + poste propose type accepté): 70%');
        console.log('   - Non-correspondance (candidat refuse ce type): 0%');
        
        return true;
    }
    
    // AUTO-INTÉGRATION INTELLIGENTE
    if (typeof NextenV2OptimizedSystem !== 'undefined') {
        enhanceContractTypeCriterion();
    } else {
        // Attendre que NEXTEN V2.0 soit chargé
        if (typeof window !== 'undefined') {
            const checkInterval = setInterval(() => {
                if (typeof NextenV2OptimizedSystem !== 'undefined') {
                    enhanceContractTypeCriterion();
                    clearInterval(checkInterval);
                }
            }, 100);
            
            // Timeout après 5 secondes
            setTimeout(() => {
                clearInterval(checkInterval);
                console.warn('⏰ Timeout: NEXTEN V2.0 non trouvé après 5 secondes');
            }, 5000);
        }
    }
    
    // Export pour usage manuel si nécessaire
    if (typeof window !== 'undefined') {
        window.enhanceNextenContractCriterion = enhanceContractTypeCriterion;
    }
    
    console.log('💼 NEXTEN V2.0 Contract Type Enhancement loaded and ready');
    
})();

/**
 * TESTS DE VALIDATION
 */
function testEnhancedContractMatching() {
    console.log('🧪 Test du matching contractuel sophistiqué intégré');
    
    if (typeof NextenV2OptimizedSystem === 'undefined') {
        console.error('❌ NEXTEN V2.0 non disponible pour les tests');
        return;
    }
    
    const nextenSystem = new NextenV2OptimizedSystem();
    
    const testCases = [
        {
            name: "Candidat exclusif CDI vs Poste CDI → 100%",
            candidate: {
                'contract-types-selected': 'cdi',
                'contract-preference-level': 'exclusive',
                'contract-primary-choice': 'cdi'
            },
            job: { contractType: 'cdi' },
            expected: 1.0
        },
        {
            name: "Candidat préfère CDI, accepte CDD vs Poste CDD → 80%",
            candidate: {
                'contract-types-selected': 'cdi,cdd',
                'contract-preference-level': 'preferred',
                'contract-primary-choice': 'cdi'
            },
            job: { contractType: 'cdd' },
            expected: 0.8
        },
        {
            name: "Candidat exclusif CDI vs Poste Freelance → 0%",
            candidate: {
                'contract-types-selected': 'cdi',
                'contract-preference-level': 'exclusive',
                'contract-primary-choice': 'cdi'
            },
            job: { contractType: 'freelance' },
            expected: 0.0
        },
        {
            name: "Candidat flexible vs Poste Interim → 80%",
            candidate: {
                'contract-types-selected': 'cdi,cdd,interim',
                'contract-preference-level': 'flexible',
                'contract-primary-choice': 'cdi'
            },
            job: { contractType: 'interim' },
            expected: 0.8
        }
    ];
    
    testCases.forEach(async (testCase, index) => {
        console.log(`\n📋 Test ${index + 1}: ${testCase.name}`);
        
        try {
            const result = await nextenSystem.calculateContractTypeCriterion(
                testCase.candidate, 
                testCase.job
            );
            
            console.log(`   Score: ${result.score} (attendu: ${testCase.expected})`);
            console.log(`   Match: ${result.details?.matchType || 'N/A'}`);
            console.log(`   Reasoning: ${result.details?.reasoning || 'N/A'}`);
            
            const success = Math.abs(result.score - testCase.expected) < 0.1;
            console.log(`   ${success ? '✅ RÉUSSI' : '❌ ÉCHOUÉ'}`);
            
        } catch (error) {
            console.error(`   ❌ ERREUR: ${error.message}`);
        }
    });
}

// Export de la fonction de test
if (typeof window !== 'undefined') {
    window.testEnhancedContractMatching = testEnhancedContractMatching;
}

console.log('🚀 Enhanced Contract Matching pour NEXTEN V2.0 chargé avec succès');
console.log('🧪 Pour tester: testEnhancedContractMatching()');
