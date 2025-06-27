/**
 * NEXTEN CULTURAL FIT ANALYZER - CRITÈRE #4 (15% DU SCORE TOTAL)
 * Système d'analyse d'adéquation culturelle entreprise/candidat
 * Intelligence émotionnelle et correspondance valeurs organisationnelles
 */

class CulturalFitAnalyzer {
    constructor() {
        this.cache = new Map();
        
        this.performanceMetrics = {
            totalCalculations: 0,
            cacheHits: 0,
            averageTime: 0,
            culturalAccuracyRate: 0
        };

        this.config = {
            // Pondération des dimensions culturelles
            scoring: {
                valuesAlignmentWeight: 0.30,      // 30% - Alignement valeurs
                workStyleCompatibilityWeight: 0.25, // 25% - Style de travail
                teamDynamicsWeight: 0.20,         // 20% - Dynamique équipe
                communicationStyleWeight: 0.15,   // 15% - Style communication
                adaptabilityWeight: 0.10          // 10% - Capacité d'adaptation
            },
            
            // Cache management
            cache: {
                duration: 7 * 24 * 60 * 60 * 1000, // 7 jours
                maxSize: 3000
            }
        };

        this.initializeCulturalDimensions();
        this.initializeCompanyProfiles();
        this.initializePersonalityMapping();
    }

    /**
     * DIMENSIONS CULTURELLES ORGANISATIONNELLES
     * Framework basé sur Hofstede et modèles organisationnels
     */
    initializeCulturalDimensions() {
        this.culturalDimensions = {
            // Échelle hiérarchique
            hierarchy: {
                horizontal: {
                    keywords: ['horizontal', 'plat', 'collaboratif', 'équipe', 'autonomie'],
                    score: 0.9,
                    description: 'Structure plate, autonomie élevée'
                },
                vertical: {
                    keywords: ['hiérarchique', 'vertical', 'management', 'supervision', 'reporting'],
                    score: 0.7,
                    description: 'Structure hiérarchique traditionnelle'
                }
            },
            
            // Innovation vs Tradition
            innovation: {
                disruptive: {
                    keywords: ['innovation', 'disruption', 'créativité', 'startup', 'agile', 'expérimentation'],
                    score: 0.95,
                    description: 'Culture d\'innovation et d\'expérimentation'
                },
                traditional: {
                    keywords: ['tradition', 'établi', 'procédures', 'standards', 'conformité'],
                    score: 0.6,
                    description: 'Approche traditionnelle et structurée'
                }
            },
            
            // Individualisme vs Collectivisme
            teamwork: {
                individualistic: {
                    keywords: ['individuel', 'autonome', 'indépendant', 'responsabilité_personnelle'],
                    score: 0.7,
                    description: 'Valorisation de l\'autonomie individuelle'
                },
                collective: {
                    keywords: ['équipe', 'collectif', 'collaboration', 'consensus', 'partage'],
                    score: 0.9,
                    description: 'Forte culture collaborative'
                }
            },
            
            // Prise de risque
            riskTolerance: {
                riskTaking: {
                    keywords: ['risque', 'audace', 'entrepreneurial', 'initiative', 'challenge'],
                    score: 0.85,
                    description: 'Encouragement de la prise d\'initiative'
                },
                conservative: {
                    keywords: ['prudent', 'sécurisé', 'stable', 'prévisible', 'contrôlé'],
                    score: 0.65,
                    description: 'Approche prudente et sécurisée'
                }
            }
        };
    }

    /**
     * PROFILS TYPES D'ENTREPRISES
     * Secteurs et tailles avec caractéristiques culturelles
     */
    initializeCompanyProfiles() {
        this.companyProfiles = {
            // Secteur Luxe
            luxe: {
                values: ['excellence', 'prestige', 'savoir_vivre', 'esthétique', 'tradition'],
                workStyle: 'formal',
                communication: 'diplomatic',
                hierarchy: 'vertical',
                innovation: 'controlled',
                clientOrientation: 'premium',
                cultureScore: 0.9
            },
            
            // Secteur Mode
            mode: {
                values: ['créativité', 'tendances', 'esthétique', 'dynamisme', 'expression'],
                workStyle: 'creative',
                communication: 'expressive',
                hierarchy: 'flexible',
                innovation: 'trendsetting',
                clientOrientation: 'mass_premium',
                cultureScore: 0.85
            },
            
            // Secteur Cosmétique
            cosmétique: {
                values: ['beauté', 'bien_être', 'science', 'innovation', 'inclusive'],
                workStyle: 'analytical',
                communication: 'persuasive',
                hierarchy: 'matrix',
                innovation: 'scientific',
                clientOrientation: 'consumer_centric',
                cultureScore: 0.8
            },
            
            // Secteur Tech
            tech: {
                values: ['innovation', 'disruption', 'efficacité', 'données', 'impact'],
                workStyle: 'agile',
                communication: 'direct',
                hierarchy: 'horizontal',
                innovation: 'disruptive',
                clientOrientation: 'user_centric',
                cultureScore: 0.95
            },
            
            // Taille entreprise
            startup: {
                flexibility: 'high',
                pace: 'fast',
                structure: 'minimal',
                autonomy: 'high',
                culturalStrength: 0.9
            },
            pme: {
                flexibility: 'medium',
                pace: 'medium',
                structure: 'moderate',
                autonomy: 'medium',
                culturalStrength: 0.7
            },
            grande_entreprise: {
                flexibility: 'low',
                pace: 'structured',
                structure: 'formal',
                autonomy: 'defined',
                culturalStrength: 0.8
            }
        };
    }

    /**
     * MAPPING PERSONNALITÉ CANDIDAT
     * Analyse CV et entretiens pour profil psychologique
     */
    initializePersonalityMapping() {
        this.personalityTraits = {
            // Big Five adapté au contexte professionnel
            openness: {
                high: {
                    keywords: ['créatif', 'innovant', 'curieux', 'expérimentation', 'apprentissage'],
                    culturalFit: ['innovation', 'créativité', 'startup', 'mode']
                },
                low: {
                    keywords: ['procédures', 'méthodes', 'structure', 'routine', 'stabilité'],
                    culturalFit: ['tradition', 'luxe', 'grande_entreprise']
                }
            },
            
            conscientiousness: {
                high: {
                    keywords: ['rigoureux', 'organisé', 'fiable', 'méthodique', 'ponctuel'],
                    culturalFit: ['luxe', 'cosmétique', 'grande_entreprise']
                },
                low: {
                    keywords: ['flexible', 'spontané', 'adaptable', 'libre'],
                    culturalFit: ['startup', 'créatif', 'mode']
                }
            },
            
            extraversion: {
                high: {
                    keywords: ['social', 'énergique', 'leadership', 'communication', 'équipe'],
                    culturalFit: ['commercial', 'management', 'collaboration']
                },
                low: {
                    keywords: ['analytique', 'réflexion', 'concentration', 'autonome'],
                    culturalFit: ['technique', 'recherche', 'individuel']
                }
            },
            
            agreeableness: {
                high: {
                    keywords: ['collaboratif', 'empathie', 'harmonie', 'consensus', 'bienveillant'],
                    culturalFit: ['équipe', 'service_client', 'rh']
                },
                low: {
                    keywords: ['assertif', 'négociation', 'décision', 'leadership', 'challenge'],
                    culturalFit: ['commercial', 'management', 'stratégique']
                }
            }
        };
    }

    /**
     * MOTEUR PRINCIPAL ANALYSE CULTURELLE
     * Scoring multi-dimensionnel avec IA comportementale
     */
    async calculateCulturalFitScore(candidateData, jobData, companyData) {
        const startTime = performance.now();
        
        try {
            // Vérification cache
            const cacheKey = this.generateCacheKey(candidateData, jobData, companyData);
            const cached = this.cache.get(cacheKey);
            if (cached && this.isCacheValid(cached)) {
                this.performanceMetrics.cacheHits++;
                this.updatePerformanceMetrics(performance.now() - startTime, true);
                return cached.data;
            }

            // Extraction profil candidat
            const candidateProfile = this.extractCandidatePersonality(candidateData);
            
            // Extraction culture entreprise
            const companyCulture = this.extractCompanyCulture(jobData, companyData);
            
            // Calculs des sous-scores
            const valuesScore = await this.calculateValuesAlignment(
                candidateProfile.values, companyCulture.values
            );
            
            const workStyleScore = await this.calculateWorkStyleCompatibility(
                candidateProfile.workStyle, companyData.workStyle
            );
            
            const teamScore = await this.calculateTeamDynamicsScore(
                candidateProfile.teamOrientation, companyData.teamDynamics
            );
            
            const communicationScore = await this.calculateCommunicationStyleScore(
                candidateProfile.communicationStyle, companyData.communicationStyle
            );
            
            const adaptabilityScore = await this.calculateAdaptabilityScore(
                candidateProfile.adaptability, companyData.changeFrequency
            );

            // Score composite final
            const finalScore = (
                valuesScore * this.config.scoring.valuesAlignmentWeight +
                workStyleScore * this.config.scoring.workStyleCompatibilityWeight +
                teamScore * this.config.scoring.teamDynamicsWeight +
                communicationScore * this.config.scoring.communicationStyleWeight +
                adaptabilityScore * this.config.scoring.adaptabilityWeight
            );

            const result = {
                finalScore: Math.min(finalScore, 1.0),
                breakdown: {
                    valuesAlignment: { score: valuesScore, weight: this.config.scoring.valuesAlignmentWeight },
                    workStyleCompatibility: { score: workStyleScore, weight: this.config.scoring.workStyleCompatibilityWeight },
                    teamDynamics: { score: teamScore, weight: this.config.scoring.teamDynamicsWeight },
                    communicationStyle: { score: communicationScore, weight: this.config.scoring.communicationStyleWeight },
                    adaptability: { score: adaptabilityScore, weight: this.config.scoring.adaptabilityWeight }
                },
                culturalInsights: {
                    candidateProfile: candidateProfile,
                    companyProfile: companyCulture,
                    compatibility: this.generateCompatibilityInsights(candidateProfile, companyProfile, finalScore),
                    recommendations: this.generateCulturalRecommendations(candidateProfile, companyProfile, finalScore)
                }
            };

            // Mise en cache
            this.cache.set(cacheKey, {
                data: result,
                timestamp: Date.now()
            });

            this.updatePerformanceMetrics(performance.now() - startTime, false);
            return result;

        } catch (error) {
            console.error('Erreur calcul cultural fit score:', error);
            return this.getFallbackScore();
        }
    }

    /**
     * EXTRACTION PROFIL PERSONNALITÉ CANDIDAT
     * Analyse CV, expériences et préférences
     */
    extractCandidatePersonality(candidateData) {
        return {
            values: this.extractPersonalValues(candidateData),
            workStyle: this.analyzeWorkStyle(candidateData.experiences || []),
            teamOrientation: this.analyzeTeamOrientation(candidateData),
            communicationStyle: this.analyzeCommunicationStyle(candidateData),
            adaptability: this.analyzeAdaptability(candidateData.experiences || []),
            motivations: this.extractMotivations(candidateData.motivations || candidateData.objectifs || ''),
            personality: this.analyzePersonalityTraits(candidateData)
        };
    }

    /**
     * EXTRACTION CULTURE ENTREPRISE
     * Analyse secteur, taille, valeurs déclarées
     */
    extractCompanyCulture(jobData, companyData) {
        const sector = this.identifySector(jobData.secteur || companyData.secteur || '');
        const size = this.identifyCompanySize(companyData.taille || companyData.effectifs || '');
        
        const baseProfile = this.companyProfiles[sector] || this.companyProfiles.tech;
        const sizeProfile = this.companyProfiles[size] || this.companyProfiles.pme;
        
        return {
            sector: sector,
            size: size,
            values: baseProfile.values,
            workStyle: baseProfile.workStyle,
            hierarchy: baseProfile.hierarchy,
            innovation: baseProfile.innovation,
            teamDynamics: this.analyzeTeamDynamicsFromDescription(jobData.description || ''),
            communicationStyle: baseProfile.communication,
            changeFrequency: sizeProfile.pace,
            culturalStrength: baseProfile.cultureScore
        };
    }

    /**
     * SCORING ALIGNEMENT VALEURS
     * Correspondance valeurs personnelles vs organisationnelles
     */
    async calculateValuesAlignment(candidateValues, companyValues) {
        if (!candidateValues || candidateValues.length === 0) return 0.5;
        if (!companyValues || companyValues.length === 0) return 0.5;
        
        let alignmentScore = 0;
        let matchedValues = 0;
        
        for (const candidateValue of candidateValues) {
            for (const companyValue of companyValues) {
                const similarity = this.calculateValuesSimilarity(candidateValue, companyValue);
                if (similarity > 0.6) {
                    alignmentScore += similarity;
                    matchedValues++;
                    break; // Une seule correspondance par valeur candidat
                }
            }
        }
        
        if (matchedValues === 0) return 0.3;
        
        // Score = moyenne des correspondances avec bonus coverage
        const averageAlignment = alignmentScore / matchedValues;
        const coverageBonus = Math.min(matchedValues / companyValues.length, 1.0) * 0.2;
        
        return Math.min(averageAlignment + coverageBonus, 1.0);
    }

    /**
     * SCORING COMPATIBILITÉ STYLE DE TRAVAIL
     * Adéquation méthodes de travail préférées
     */
    async calculateWorkStyleCompatibility(candidateStyle, companyStyle) {
        const styleCompatibility = {
            // Matrice de compatibilité
            'structured-formal': 0.9,
            'structured-agile': 0.6,
            'flexible-agile': 0.9,
            'flexible-formal': 0.5,
            'creative-creative': 1.0,
            'creative-analytical': 0.7,
            'analytical-analytical': 1.0,
            'analytical-creative': 0.7
        };
        
        const key = `${candidateStyle}-${companyStyle}`;
        return styleCompatibility[key] || 0.6; // Score par défaut
    }

    /**
     * SCORING DYNAMIQUE ÉQUIPE
     * Préférence collaboration vs autonomie
     */
    async calculateTeamDynamicsScore(candidateTeamOrientation, companyTeamDynamics) {
        // Échelle de 1-10 pour orientation équipe
        const orientationDiff = Math.abs(candidateTeamOrientation - companyTeamDynamics);
        
        // Score inversement proportionnel à la différence
        return Math.max(0.2, 1.0 - (orientationDiff / 10));
    }

    /**
     * SCORING STYLE COMMUNICATION
     * Adéquation modes de communication préférés
     */
    async calculateCommunicationStyleScore(candidateStyle, companyStyle) {
        const communicationMatrix = {
            'direct-direct': 1.0,
            'direct-diplomatic': 0.7,
            'diplomatic-diplomatic': 1.0,
            'diplomatic-direct': 0.8,
            'expressive-expressive': 1.0,
            'expressive-reserved': 0.6,
            'analytical-analytical': 1.0,
            'analytical-expressive': 0.7
        };
        
        const key = `${candidateStyle}-${companyStyle}`;
        return communicationMatrix[key] || 0.65;
    }

    /**
     * SCORING ADAPTABILITÉ
     * Capacité d'adaptation aux changements
     */
    async calculateAdaptabilityScore(candidateAdaptability, companyChangeFrequency) {
        const adaptabilityRequirements = {
            'fast': 0.8,     // Startup, changements fréquents
            'medium': 0.6,   // PME, changements modérés
            'slow': 0.4,     // Grande entreprise, changements rares
            'structured': 0.3 // Très structuré, peu de changements
        };
        
        const requiredAdaptability = adaptabilityRequirements[companyChangeFrequency] || 0.5;
        
        if (candidateAdaptability >= requiredAdaptability) {
            // Bonus léger pour sur-adaptabilité
            return Math.min(1.0, candidateAdaptability + 0.1);
        } else {
            // Pénalité pour sous-adaptabilité
            return candidateAdaptability / requiredAdaptability;
        }
    }

    /**
     * ANALYSE TRAITS PERSONNALITÉ
     * Détection Big Five à partir du CV
     */
    analyzePersonalityTraits(candidateData) {
        const traits = {};
        const text = this.concatenateTextData(candidateData);
        
        for (const [trait, levels] of Object.entries(this.personalityTraits)) {
            let score = 0.5; // Score neutre par défaut
            
            for (const [level, config] of Object.entries(levels)) {
                for (const keyword of config.keywords) {
                    if (text.toLowerCase().includes(keyword)) {
                        score = level === 'high' ? 0.7 : 0.3;
                        break;
                    }
                }
            }
            
            traits[trait] = score;
        }
        
        return traits;
    }

    /**
     * ANALYSE STYLE DE TRAVAIL
     * Déduction à partir des expériences
     */
    analyzeWorkStyle(experiences) {
        let structuredScore = 0;
        let creativeScore = 0;
        let analyticalScore = 0;
        
        for (const exp of experiences) {
            const description = (exp.missions || []).join(' ') + ' ' + (exp.description || '');
            
            if (this.containsKeywords(description, ['procédure', 'méthode', 'process', 'structure'])) {
                structuredScore++;
            }
            if (this.containsKeywords(description, ['créatif', 'innovation', 'design', 'concept'])) {
                creativeScore++;
            }
            if (this.containsKeywords(description, ['analyse', 'données', 'étude', 'recherche'])) {
                analyticalScore++;
            }
        }
        
        // Retourne le style dominant
        const maxScore = Math.max(structuredScore, creativeScore, analyticalScore);
        if (maxScore === structuredScore) return 'structured';
        if (maxScore === creativeScore) return 'creative';
        return 'analytical';
    }

    /**
     * GÉNÉRATION INSIGHTS COMPATIBILITÉ
     */
    generateCompatibilityInsights(candidateProfile, companyProfile, score) {
        const insights = [];
        
        if (score > 0.8) {
            insights.push({
                type: 'excellent_fit',
                message: 'Très forte compatibilité culturelle',
                details: 'Alignement remarquable des valeurs et du style de travail'
            });
        } else if (score > 0.6) {
            insights.push({
                type: 'good_fit',
                message: 'Bonne compatibilité culturelle',
                details: 'Quelques ajustements possibles mais profil adapté'
            });
        } else {
            insights.push({
                type: 'cultural_gap',
                message: 'Écart culturel significatif',
                details: 'Nécessite accompagnement pour intégration'
            });
        }
        
        return insights;
    }

    /**
     * GÉNÉRATION RECOMMANDATIONS CULTURELLES
     */
    generateCulturalRecommendations(candidateProfile, companyProfile, score) {
        const recommendations = [];
        
        if (score < 0.5) {
            recommendations.push({
                priority: 'high',
                type: 'onboarding',
                message: 'Programme d\'intégration culturelle renforcé recommandé'
            });
        }
        
        if (candidateProfile.workStyle !== companyProfile.workStyle) {
            recommendations.push({
                priority: 'medium',
                type: 'adaptation',
                message: `Accompagnement transition style ${candidateProfile.workStyle} vers ${companyProfile.workStyle}`
            });
        }
        
        return recommendations;
    }

    /**
     * UTILITAIRES
     */
    calculateValuesSimilarity(value1, value2) {
        // Mapping synonymes et concepts proches
        const valuesSynonyms = {
            'excellence': ['qualité', 'perfection', 'standard_élevé'],
            'innovation': ['créativité', 'nouveauté', 'disruption'],
            'collaboration': ['équipe', 'collectif', 'partenariat'],
            'efficacité': ['performance', 'résultats', 'productivité']
        };
        
        if (value1 === value2) return 1.0;
        
        // Vérifier synonymes
        for (const [mainValue, synonyms] of Object.entries(valuesSynonyms)) {
            if ((value1 === mainValue && synonyms.includes(value2)) ||
                (value2 === mainValue && synonyms.includes(value1))) {
                return 0.8;
            }
        }
        
        return 0.0;
    }

    containsKeywords(text, keywords) {
        const lowerText = text.toLowerCase();
        return keywords.some(keyword => lowerText.includes(keyword));
    }

    concatenateTextData(candidateData) {
        return [
            candidateData.motivations || '',
            candidateData.objectifs || '',
            (candidateData.experiences || []).map(exp => exp.description || '').join(' '),
            (candidateData.competences || []).join(' ')
        ].join(' ');
    }

    /**
     * CACHE ET PERFORMANCE
     */
    generateCacheKey(candidateData, jobData, companyData) {
        const candidateId = candidateData.id || 'candidate';
        const jobId = jobData.id || 'job';
        const companyId = companyData.id || 'company';
        return `cultural_${candidateId}_${jobId}_${companyId}`;
    }

    isCacheValid(cached) {
        return (Date.now() - cached.timestamp) < this.config.cache.duration;
    }

    updatePerformanceMetrics(calculationTime, wasCacheHit) {
        this.performanceMetrics.totalCalculations++;
        this.performanceMetrics.averageTime = 
            (this.performanceMetrics.averageTime * (this.performanceMetrics.totalCalculations - 1) + calculationTime) 
            / this.performanceMetrics.totalCalculations;
    }

    getFallbackScore() {
        return {
            finalScore: 0.6,
            error: 'Données culturelles insuffisantes',
            fallback: true
        };
    }

    getPerformanceReport() {
        const cacheHitRate = this.performanceMetrics.totalCalculations > 0 ? 
            (this.performanceMetrics.cacheHits / this.performanceMetrics.totalCalculations * 100).toFixed(1) : '0';

        return {
            ...this.performanceMetrics,
            cacheHitRate: `${cacheHitRate}%`,
            cacheSize: this.cache.size
        };
    }
}

// Export pour intégration
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CulturalFitAnalyzer;
}

if (typeof window !== 'undefined') {
    window.CulturalFitAnalyzer = CulturalFitAnalyzer;
}
