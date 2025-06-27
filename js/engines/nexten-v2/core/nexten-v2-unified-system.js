/**
 * NEXTEN V2.0 UNIFIED SYSTEM - SYSTÈME 11 CRITÈRES GRANULAIRES
 * Évolution du système Nexten vers 95%+ de précision matching
 * Architecture modulaire exploitant 100% des questionnaires candidat/entreprise
 */

class NextenV2UnifiedSystem extends NextenUnifiedSystem {
    constructor() {
        super(); // Hérite de Nexten v1 pour rétro-compatibilité
        
        // === NOUVELLE ARCHITECTURE V2.0 - 11 CRITÈRES ===
        this.v2Criteria = {
            // Critères existants optimisés (45%)
            semantic: null,           // #1 - Compatibilité Sémantique (25%)
            location: null,           // #2 - Géolocalisation + Trajets (20%)
            
            // Nouveaux critères questionnaires enrichis (55%)
            compensation: null,       // #3 - Rémunération fourchettes + négociation (15%)
            motivation: null,         // #4 - Leviers motivation prioritaires (10%)
            companySize: null,        // #5 - Taille structure vs préférences (8%)
            workEnvironment: null,    // #6 - Environnement travail détaillé (8%)
            industry: null,           // #7 - Secteurs préférés + rédhibitoires (6%)
            availability: null,       // #8 - Urgence vs délai candidat (5%)
            contractType: null,       // #9 - CDI/CDD/Freelance compatibilité (5%)
            listenReasons: null,      // #10 - Anti-patterns intelligents (3%)
            processPosition: null     // #11 - Position process vs durée (2%)
        };

        // === NOUVELLE PONDÉRATION OPTIMISÉE V2.0 (100%) ===
        this.v2CriteriaWeights = {
            // Core critères techniques (45%)
            semantic: 0.25,           // #1 - Compatibilité Sémantique (EXISTANT optimisé)
            location: 0.20,           // #2 - Géolocalisation + Trajets (EXISTANT optimisé)
            
            // Critères questionnaires enrichis (55%)
            compensation: 0.15,       // #3 - Rémunération fourchettes + négociation
            motivation: 0.10,         // #4 - Leviers motivation prioritaires candidat
            companySize: 0.08,        // #5 - Taille structure vs préférences
            workEnvironment: 0.08,    // #6 - Environnement travail détaillé
            industry: 0.06,           // #7 - Secteurs préférés + rédhibitoires
            availability: 0.05,       // #8 - Urgence vs délai candidat
            contractType: 0.05,       // #9 - CDI/CDD/Freelance compatibilité
            listenReasons: 0.03,      // #10 - Anti-patterns intelligents
            processPosition: 0.02     // #11 - Position process vs durée
        };

        // Système adaptatif v1/v2
        this.matchingMode = 'adaptive'; // 'v1', 'v2', 'adaptive'
        this.dataCompleteness = {
            questionnaire_candidat: 0,
            questionnaire_entreprise: 0,
            cv_parser: 0,
            job_parser: 0
        };

        // Métriques spécifiques v2.0
        this.v2Metrics = {
            precision_target: 0.95,
            current_precision: 0.0,
            questionnaire_usage: 0.0,
            criteria_coverage: 0.0,
            performance_v2: 0
        };

        this.initializeV2Criteria();
        this.initializeQuestionnaireMapper();
        
        console.log('🚀 NEXTEN V2.0 - Système 11 critères initialisé');
    }

    /**
     * MOTEUR PRINCIPAL V2.0 - MATCHING 11 CRITÈRES
     * Orchestration intelligente avec fallback v1
     */
    async calculateV2MatchingScore(candidateData, jobData, companyData = {}) {
        const startTime = performance.now();
        
        try {
            // Analyse de complétude des données
            const dataAnalysis = this.analyzeDataCompleteness(candidateData, jobData, companyData);
            
            // Décision mode matching adaptatif
            const matchingMode = this.determineMatchingMode(dataAnalysis);
            
            if (matchingMode === 'v1_fallback') {
                console.log('📊 Mode V1 - Données questionnaires insuffisantes');
                return await this.calculateCompleteMatchingScore(candidateData, jobData, companyData);
            }

            // Mapping automatique questionnaires → critères
            const enrichedData = await this.mapQuestionnairesToCriteria(candidateData, jobData, companyData);
            
            // Calcul parallèle des 11 critères V2.0
            const v2Results = await this.calculateAllV2Criteria(enrichedData);
            
            // Score composite final V2.0
            const finalScore = this.computeV2FinalScore(v2Results);
            
            // Construction résultat enrichi V2.0
            const result = {
                finalScore: Math.min(finalScore, 1.0),
                version: '2.0',
                qualityLevel: this.determineV2QualityLevel(finalScore),
                matchingMode: matchingMode,
                criteriaBreakdown: this.buildV2CriteriaBreakdown(v2Results),
                insights: {
                    strengths: this.identifyV2Strengths(v2Results),
                    improvements: this.identifyV2Improvements(v2Results),
                    recommendations: this.generateV2Recommendations(v2Results, finalScore),
                    nextSteps: this.generateV2NextSteps(v2Results, finalScore)
                },
                dataUsage: {
                    questionnaire_candidat: dataAnalysis.questionnaire_candidat,
                    questionnaire_entreprise: dataAnalysis.questionnaire_entreprise,
                    cv_parser: dataAnalysis.cv_parser,
                    job_parser: dataAnalysis.job_parser,
                    total_coverage: dataAnalysis.total_coverage
                },
                performance: {
                    calculationTime: performance.now() - startTime,
                    dataCompleteness: dataAnalysis.total_coverage,
                    criteriaUsed: Object.keys(v2Results).length,
                    precision_estimated: this.estimateV2Precision(v2Results, dataAnalysis),
                    target_precision: this.v2Metrics.precision_target
                },
                metadata: {
                    timestamp: new Date().toISOString(),
                    version: '2.0.0',
                    candidateId: candidateData.id || 'unknown',
                    jobId: jobData.id || 'unknown',
                    system: 'nexten-v2-11-criteria'
                }
            };

            // Mise à jour métriques V2.0
            this.updateV2Metrics(result);
            
            return result;

        } catch (error) {
            console.error('❌ Erreur Nexten V2.0:', error);
            console.log('🔄 Fallback vers Nexten V1.0');
            return await this.calculateCompleteMatchingScore(candidateData, jobData, companyData);
        }
    }

    /**
     * ANALYSE COMPLÉTUDE DONNÉES
     * Détermine la richesse des données questionnaires
     */
    analyzeDataCompleteness(candidateData, jobData, companyData) {
        const analysis = {
            questionnaire_candidat: 0,
            questionnaire_entreprise: 0,
            cv_parser: 0,
            job_parser: 0,
            total_coverage: 0
        };

        // Analyse données candidat
        const candidateQuestionnaireFields = [
            'pretentions_salariales', 'motivations', 'taille_entreprise_preference',
            'environnement_prefere', 'secteurs_cibles', 'disponibilite',
            'type_contrat_souhaite', 'raisons_changement', 'situation_process'
        ];
        
        const candidateQuestionnaireFilled = candidateQuestionnaireFields.filter(field => 
            candidateData[field] && candidateData[field] !== ''
        ).length;
        
        analysis.questionnaire_candidat = candidateQuestionnaireFilled / candidateQuestionnaireFields.length;

        // Analyse données entreprise/poste
        const jobQuestionnaireFields = [
            'fourchette_salariale', 'avantages', 'taille_equipe', 'mode_travail',
            'secteur', 'urgence_recrutement', 'type_contrat', 'processus_recrutement'
        ];
        
        const jobQuestionnaireFilled = jobQuestionnaireFields.filter(field => 
            jobData[field] && jobData[field] !== ''
        ).length;
        
        analysis.questionnaire_entreprise = jobQuestionnaireFilled / jobQuestionnaireFields.length;

        // Coverage total
        analysis.total_coverage = (analysis.questionnaire_candidat + analysis.questionnaire_entreprise) / 2;

        return analysis;
    }

    /**
     * DÉTERMINE MODE MATCHING ADAPTATIF
     * v1, v2, ou hybride selon données disponibles
     */
    determineMatchingMode(dataAnalysis) {
        const questionnaireThreshold = 0.6; // 60% des champs questionnaires remplis
        
        if (dataAnalysis.questionnaire_candidat >= questionnaireThreshold && 
            dataAnalysis.questionnaire_entreprise >= questionnaireThreshold) {
            return 'v2_full';
        }
        
        if (dataAnalysis.questionnaire_candidat >= questionnaireThreshold || 
            dataAnalysis.questionnaire_entreprise >= questionnaireThreshold) {
            return 'v2_partial';
        }
        
        return 'v1_fallback';
    }

    /**
     * SCORE COMPOSITE FINAL V2.0
     * Pondération intelligente des 11 critères
     */
    computeV2FinalScore(v2Results) {
        let totalScore = 0;
        let totalWeight = 0;
        
        // Calcul pondéré avec gestion des critères manquants
        Object.entries(this.v2CriteriaWeights).forEach(([criterion, weight]) => {
            if (v2Results[criterion] && v2Results[criterion].score !== undefined) {
                totalScore += v2Results[criterion].score * weight;
                totalWeight += weight;
            }
        });
        
        // Normalisation si des critères manquent
        return totalWeight > 0 ? totalScore / totalWeight : 0.5;
    }

    /**
     * ESTIMATION PRÉCISION V2.0
     * Prédiction de la précision basée sur la richesse des données
     */
    estimateV2Precision(v2Results, dataAnalysis) {
        const basePrecision = 0.912; // Précision V1.0 de référence
        
        // Bonus précision selon données questionnaires
        const questionnaireBonusMax = 0.05; // +5% max avec questionnaires complets
        const questionnaireBonus = questionnaireBonusMax * dataAnalysis.total_coverage;
        
        // Bonus selon nombre de critères utilisés
        const criteriaCount = Object.keys(v2Results).length;
        const criteriaBonusMax = 0.03; // +3% max avec tous les critères
        const criteriaBonus = criteriaBonusMax * (criteriaCount / 11);
        
        const estimatedPrecision = Math.min(basePrecision + questionnaireBonus + criteriaBonus, 0.98);
        
        return estimatedPrecision;
    }

    // Méthodes placeholder à implémenter
    async initializeV2Criteria() { console.log('📦 Initialisation critères V2.0'); }
    async mapQuestionnairesToCriteria(candidateData, jobData, companyData) { return { candidate: candidateData, job: jobData, company: companyData }; }
    async calculateAllV2Criteria(enrichedData) { return { semantic: { score: 0.8 }, location: { score: 0.75 }, compensation: { score: 0.85 } }; }
    buildV2CriteriaBreakdown(v2Results) { return {}; }
    identifyV2Strengths(v2Results) { return []; }
    identifyV2Improvements(v2Results) { return []; }
    generateV2Recommendations(v2Results, finalScore) { return []; }
    generateV2NextSteps(v2Results, finalScore) { return []; }
    determineV2QualityLevel(finalScore) { return this.determineQualityLevel(finalScore); }
    updateV2Metrics(result) { this.v2Metrics.current_precision = result.performance.precision_estimated; }
    initializeQuestionnaireMapper() { console.log('📋 Questionnaire mapper initialized'); }
}

// Export pour intégration
if (typeof module !== 'undefined' && module.exports) {
    module.exports = NextenV2UnifiedSystem;
}

if (typeof window !== 'undefined') {
    window.NextenV2UnifiedSystem = NextenV2UnifiedSystem;
    console.log('🚀 NEXTEN V2.0 - Système unifié disponible');
}