/**
 * NEXTEN EXPERIENCE LEVEL MATCHER - CRITÈRE #3 (20% DU SCORE TOTAL)
 * Système de matching niveau d'expérience et progression carrière
 * Analyse comparative postes précédents vs exigences poste cible
 */

class ExperienceLevelMatcher {
    constructor() {
        this.cache = new Map();
        
        this.performanceMetrics = {
            totalCalculations: 0,
            cacheHits: 0,
            averageTime: 0,
            accuracyRate: 0
        };

        this.config = {
            // Pondération des critères d'expérience
            scoring: {
                yearsExperienceWeight: 0.35,    // 35% - Années d'expérience totales
                roleProgressionWeight: 0.25,    // 25% - Progression dans les rôles
                industryExperienceWeight: 0.20, // 20% - Expérience sectorielle
                managementExperienceWeight: 0.15, // 15% - Expérience management
                technicalSkillsWeight: 0.05     // 5% - Compétences techniques spécifiques
            },
            
            // Niveaux d'expérience
            experienceLevels: {
                junior: { minYears: 0, maxYears: 2, multiplier: 1.0 },
                intermediate: { minYears: 2, maxYears: 5, multiplier: 1.1 },
                senior: { minYears: 5, maxYears: 10, multiplier: 1.2 },
                expert: { minYears: 10, maxYears: 15, multiplier: 1.3 },
                executive: { minYears: 15, maxYears: 999, multiplier: 1.4 }
            },
            
            // Cache management
            cache: {
                duration: 30 * 24 * 60 * 60 * 1000, // 30 jours
                maxSize: 5000
            }
        };

        this.initializeIndustryMapping();
        this.initializeRoleHierarchy();
        this.initializeSkillsDatabase();
    }

    /**
     * MAPPING INDUSTRIES ET SECTEURS
     * Correspondances et transferabilité entre secteurs
     */
    initializeIndustryMapping() {
        this.industries = {
            luxe: {
                keywords: ['luxe', 'luxury', 'premium', 'haut_de_gamme', 'prestige'],
                transferableFrom: ['mode', 'cosmétique', 'bijouterie', 'automobile_premium'],
                transferabilityScore: 0.9,
                specificSkills: ['client_vip', 'savoir_vivre', 'codes_luxe']
            },
            mode: {
                keywords: ['mode', 'fashion', 'textile', 'vêtement', 'accessoire'],
                transferableFrom: ['luxe', 'cosmétique', 'retail'],
                transferabilityScore: 0.85,
                specificSkills: ['tendances', 'stylisme', 'merchandising']
            },
            cosmétique: {
                keywords: ['cosmétique', 'beauté', 'parfum', 'skincare', 'makeup'],
                transferableFrom: ['luxe', 'mode', 'pharmacie'],
                transferabilityScore: 0.8,
                specificSkills: ['formulation', 'dermatologie', 'marketing_beauté']
            },
            retail: {
                keywords: ['retail', 'vente', 'commerce', 'distribution'],
                transferableFrom: ['any'],
                transferabilityScore: 0.7,
                specificSkills: ['vente', 'merchandising', 'gestion_stock']
            },
            tech: {
                keywords: ['technologie', 'digital', 'informatique', 'software'],
                transferableFrom: ['digital', 'e-commerce'],
                transferabilityScore: 0.6,
                specificSkills: ['programmation', 'data', 'digital']
            }
        };
    }

    /**
     * HIÉRARCHIE DES RÔLES
     * Progression naturelle et scoring évolution
     */
    initializeRoleHierarchy() {
        this.roleHierarchy = {
            // Échelle hiérarchique (1-10)
            scales: {
                'stagiaire': 1,
                'assistant': 2,
                'junior': 3,
                'chargé': 4,
                'senior': 5,
                'responsable': 6,
                'manager': 7,
                'directeur': 8,
                'vp': 9,
                'c-level': 10
            },
            
            // Progression naturelle par fonction
            careerPaths: {
                commercial: [
                    'commercial_junior', 'commercial', 'senior_commercial', 
                    'responsable_commercial', 'manager_commercial', 'directeur_commercial'
                ],
                marketing: [
                    'assistant_marketing', 'chargé_marketing', 'senior_marketing',
                    'responsable_marketing', 'manager_marketing', 'directeur_marketing'
                ],
                management: [
                    'team_lead', 'superviseur', 'manager', 
                    'senior_manager', 'directeur', 'directeur_général'
                ]
            }
        };
    }

    /**
     * BASE DE DONNÉES COMPÉTENCES
     * Mapping compétences et scoring transferabilité
     */
    initializeSkillsDatabase() {
        this.skillsDatabase = {
            // Compétences transversales (valeur élevée)
            transversal: {
                'management': { value: 0.9, transferability: 0.95 },
                'leadership': { value: 0.9, transferability: 0.95 },
                'négociation': { value: 0.8, transferability: 0.9 },
                'communication': { value: 0.8, transferability: 0.9 },
                'analyse': { value: 0.8, transferability: 0.85 },
                'gestion_projet': { value: 0.85, transferability: 0.9 }
            },
            
            // Compétences sectorielles
            sectoriel: {
                'codes_luxe': { value: 0.95, transferability: 0.7 },
                'client_vip': { value: 0.9, transferability: 0.75 },
                'merchandising': { value: 0.8, transferability: 0.8 },
                'formulation_cosmétique': { value: 0.9, transferability: 0.5 }
            },
            
            // Compétences techniques
            technique: {
                'excel_avancé': { value: 0.7, transferability: 0.95 },
                'crm': { value: 0.75, transferability: 0.9 },
                'sap': { value: 0.8, transferability: 0.85 },
                'photoshop': { value: 0.6, transferability: 0.7 }
            }
        };
    }

    /**
     * MOTEUR PRINCIPAL DE MATCHING EXPÉRIENCE
     * Scoring composite multi-dimensionnel
     */
    async calculateExperienceScore(candidateData, jobData) {
        const startTime = performance.now();
        
        try {
            // Vérification cache
            const cacheKey = this.generateCacheKey(candidateData, jobData);
            const cached = this.cache.get(cacheKey);
            if (cached && this.isCacheValid(cached)) {
                this.performanceMetrics.cacheHits++;
                this.updatePerformanceMetrics(performance.now() - startTime, true);
                return cached.data;
            }

            // Extraction données expérience candidat
            const candidateExperience = this.extractCandidateExperience(candidateData);
            
            // Extraction exigences poste
            const jobRequirements = this.extractJobRequirements(jobData);
            
            // Calculs des sous-scores
            const yearsScore = await this.calculateYearsExperienceScore(
                candidateExperience, jobRequirements
            );
            
            const progressionScore = await this.calculateRoleProgressionScore(
                candidateExperience.positions, jobRequirements.targetLevel
            );
            
            const industryScore = await this.calculateIndustryExperienceScore(
                candidateExperience.industries, jobRequirements.industry
            );
            
            const managementScore = await this.calculateManagementExperienceScore(
                candidateExperience.managementExperience, jobRequirements.managementRequired
            );
            
            const skillsScore = await this.calculateSkillsMatchScore(
                candidateExperience.skills, jobRequirements.requiredSkills
            );

            // Score composite final
            const finalScore = (
                yearsScore * this.config.scoring.yearsExperienceWeight +
                progressionScore * this.config.scoring.roleProgressionWeight +
                industryScore * this.config.scoring.industryExperienceWeight +
                managementScore * this.config.scoring.managementExperienceWeight +
                skillsScore * this.config.scoring.technicalSkillsWeight
            );

            const result = {
                finalScore: Math.min(finalScore, 1.0),
                breakdown: {
                    yearsExperience: { score: yearsScore, weight: this.config.scoring.yearsExperienceWeight },
                    roleProgression: { score: progressionScore, weight: this.config.scoring.roleProgressionWeight },
                    industryExperience: { score: industryScore, weight: this.config.scoring.industryExperienceWeight },
                    managementExperience: { score: managementScore, weight: this.config.scoring.managementExperienceWeight },
                    technicalSkills: { score: skillsScore, weight: this.config.scoring.technicalSkillsWeight }
                },
                details: {
                    candidateProfile: candidateExperience,
                    jobRequirements: jobRequirements,
                    recommendations: this.generateRecommendations(candidateExperience, jobRequirements, finalScore)
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
            console.error('Erreur calcul experience score:', error);
            return this.getFallbackScore();
        }
    }

    /**
     * EXTRACTION EXPÉRIENCE CANDIDAT
     * Parsing CV avec analyse carrière
     */
    extractCandidateExperience(candidateData) {
        return {
            totalYears: this.calculateTotalExperience(candidateData.experiences || []),
            positions: this.parsePositions(candidateData.experiences || []),
            industries: this.extractIndustries(candidateData.experiences || []),
            skills: this.extractSkills(candidateData.competences || []),
            managementExperience: this.extractManagementExperience(candidateData.experiences || []),
            educationLevel: candidateData.niveau_etudes || '',
            certifications: candidateData.certifications || [],
            languages: candidateData.langues || []
        };
    }

    /**
     * EXTRACTION EXIGENCES POSTE
     * Parsing offre avec analyse requirements
     */
    extractJobRequirements(jobData) {
        return {
            requiredYears: this.parseRequiredYears(jobData.experience_requise || ''),
            targetLevel: this.parseTargetLevel(jobData.niveau_poste || jobData.intitule || ''),
            industry: this.parseIndustry(jobData.secteur || jobData.description || ''),
            requiredSkills: this.parseRequiredSkills(jobData.competences_requises || []),
            managementRequired: this.parseManagementRequirement(jobData.description || ''),
            educationRequired: jobData.formation_requise || '',
            languagesRequired: jobData.langues_requises || []
        };
    }

    /**
     * SCORING ANNÉES D'EXPÉRIENCE
     * Comparaison avec exigences + bonus surqualification modérée
     */
    async calculateYearsExperienceScore(candidateExperience, jobRequirements) {
        const candidateYears = candidateExperience.totalYears;
        const requiredYears = jobRequirements.requiredYears;
        
        if (candidateYears >= requiredYears) {
            // Bonus modéré pour surqualification (max +20%)
            const overQualification = Math.min((candidateYears - requiredYears) / requiredYears, 0.2);
            return Math.min(1.0 + overQualification, 1.2);
        } else {
            // Pénalité linéaire pour sous-qualification
            const underQualification = candidateYears / requiredYears;
            return Math.max(underQualification, 0.1);
        }
    }

    /**
     * SCORING PROGRESSION CARRIÈRE
     * Analyse évolution hiérarchique et cohérence
     */
    async calculateRoleProgressionScore(positions, targetLevel) {
        if (!positions || positions.length === 0) return 0.1;
        
        // Calcul progression hiérarchique
        const progressionScore = this.analyzeHierarchicalProgression(positions);
        
        // Adéquation niveau actuel vs niveau cible
        const currentLevel = this.getRoleLevel(positions[0]); // Plus récent
        const targetLevelScore = this.calculateLevelMatch(currentLevel, targetLevel);
        
        // Stabilité dans les postes
        const stabilityScore = this.analyzeJobStability(positions);
        
        return (progressionScore * 0.4 + targetLevelScore * 0.4 + stabilityScore * 0.2);
    }

    /**
     * SCORING EXPÉRIENCE SECTORIELLE
     * Transferabilité et spécialisation industrie
     */
    async calculateIndustryExperienceScore(candidateIndustries, targetIndustry) {
        if (!candidateIndustries || candidateIndustries.length === 0) return 0.1;
        
        let bestScore = 0;
        
        for (const candidateIndustry of candidateIndustries) {
            let score = 0;
            
            // Match exact
            if (candidateIndustry.name === targetIndustry) {
                score = 1.0;
            } else {
                // Score de transferabilité
                score = this.calculateTransferabilityScore(candidateIndustry.name, targetIndustry);
            }
            
            // Bonus pour durée dans le secteur
            const durationBonus = Math.min(candidateIndustry.years / 5, 0.2);
            score += durationBonus;
            
            bestScore = Math.max(bestScore, score);
        }
        
        return Math.min(bestScore, 1.0);
    }

    /**
     * SCORING EXPÉRIENCE MANAGEMENT
     * Équipes managées et responsabilités
     */
    async calculateManagementExperienceScore(managementExp, managementRequired) {
        if (!managementRequired) return 0.8; // Si pas requis, score neutre
        
        if (!managementExp || managementExp.totalYears === 0) {
            return 0.2; // Pénalité si management requis mais absent
        }
        
        // Score basé sur années management
        const yearsScore = Math.min(managementExp.totalYears / 5, 1.0);
        
        // Score basé sur taille équipes
        const teamSizeScore = Math.min(managementExp.maxTeamSize / 10, 1.0);
        
        // Score basé sur niveaux managés
        const levelScore = managementExp.hasManageManagers ? 1.0 : 0.7;
        
        return (yearsScore * 0.4 + teamSizeScore * 0.3 + levelScore * 0.3);
    }

    /**
     * SCORING COMPÉTENCES
     * Matching skills requis vs acquis
     */
    async calculateSkillsMatchScore(candidateSkills, requiredSkills) {
        if (!requiredSkills || requiredSkills.length === 0) return 0.8;
        if (!candidateSkills || candidateSkills.length === 0) return 0.2;
        
        let totalScore = 0;
        let matchedSkills = 0;
        
        for (const requiredSkill of requiredSkills) {
            const skillMatch = this.findBestSkillMatch(requiredSkill, candidateSkills);
            if (skillMatch.score > 0.5) { // Seuil de match
                totalScore += skillMatch.score;
                matchedSkills++;
            }
        }
        
        // Score = moyenne des matches + bonus coverage
        const averageScore = matchedSkills > 0 ? totalScore / matchedSkills : 0;
        const coverageBonus = (matchedSkills / requiredSkills.length) * 0.2;
        
        return Math.min(averageScore + coverageBonus, 1.0);
    }

    /**
     * UTILITAIRES PARSING
     */
    calculateTotalExperience(experiences) {
        let totalMonths = 0;
        for (const exp of experiences) {
            const months = this.calculateDurationInMonths(exp.date_debut, exp.date_fin);
            totalMonths += months;
        }
        return Math.round(totalMonths / 12 * 10) / 10; // Années avec 1 décimale
    }

    parsePositions(experiences) {
        return experiences
            .map(exp => ({
                title: exp.intitule || exp.poste,
                company: exp.entreprise,
                duration: this.calculateDurationInMonths(exp.date_debut, exp.date_fin),
                level: this.getRoleLevel(exp.intitule || exp.poste),
                responsibilities: exp.missions || []
            }))
            .sort((a, b) => b.duration - a.duration); // Plus récent en premier
    }

    extractIndustries(experiences) {
        const industries = {};
        
        for (const exp of experiences) {
            const industry = this.identifyIndustry(exp.entreprise, exp.secteur, exp.description);
            const duration = this.calculateDurationInMonths(exp.date_debut, exp.date_fin) / 12;
            
            if (industries[industry]) {
                industries[industry] += duration;
            } else {
                industries[industry] = duration;
            }
        }
        
        return Object.entries(industries)
            .map(([name, years]) => ({ name, years }))
            .sort((a, b) => b.years - a.years);
    }

    /**
     * ANALYSE PROGRESSION HIÉRARCHIQUE
     */
    analyzeHierarchicalProgression(positions) {
        if (positions.length < 2) return 0.6; // Score neutre si pas assez d'historique
        
        let progressionPoints = 0;
        let comparisons = 0;
        
        for (let i = 0; i < positions.length - 1; i++) {
            const currentLevel = this.roleHierarchy.scales[positions[i].level] || 3;
            const previousLevel = this.roleHierarchy.scales[positions[i + 1].level] || 3;
            
            if (currentLevel > previousLevel) {
                progressionPoints += (currentLevel - previousLevel) / 3; // Progression positive
            } else if (currentLevel < previousLevel) {
                progressionPoints -= 0.2; // Légère pénalité régression
            }
            
            comparisons++;
        }
        
        const averageProgression = comparisons > 0 ? progressionPoints / comparisons : 0;
        return Math.max(Math.min(0.6 + averageProgression, 1.0), 0.1);
    }

    /**
     * UTILITAIRES SCORING
     */
    getRoleLevel(title) {
        const titleLower = (title || '').toLowerCase();
        
        for (const [level, scale] of Object.entries(this.roleHierarchy.scales)) {
            if (titleLower.includes(level)) return level;
        }
        
        // Détection par mots-clés
        if (titleLower.includes('directeur') || titleLower.includes('director')) return 'directeur';
        if (titleLower.includes('manager') || titleLower.includes('responsable')) return 'manager';
        if (titleLower.includes('senior')) return 'senior';
        if (titleLower.includes('junior') || titleLower.includes('assistant')) return 'junior';
        
        return 'chargé'; // Par défaut
    }

    calculateTransferabilityScore(fromIndustry, toIndustry) {
        const toIndustryData = this.industries[toIndustry];
        if (!toIndustryData) return 0.5;
        
        if (toIndustryData.transferableFrom.includes(fromIndustry) || 
            toIndustryData.transferableFrom.includes('any')) {
            return toIndustryData.transferabilityScore;
        }
        
        return 0.3; // Score faible si pas de transferabilité
    }

    /**
     * GÉNÉRATION RECOMMANDATIONS
     */
    generateRecommendations(candidateExperience, jobRequirements, finalScore) {
        const recommendations = [];
        
        if (finalScore < 0.6) {
            recommendations.push({
                type: 'improvement',
                message: 'Candidat nécessite un développement dans certains domaines'
            });
        }
        
        if (candidateExperience.totalYears < jobRequirements.requiredYears) {
            recommendations.push({
                type: 'experience',
                message: `Manque ${jobRequirements.requiredYears - candidateExperience.totalYears} années d'expérience`
            });
        }
        
        if (finalScore > 0.8) {
            recommendations.push({
                type: 'excellent',
                message: 'Profil très adapté au poste'
            });
        }
        
        return recommendations;
    }

    /**
     * UTILITAIRES CACHE ET PERFORMANCE
     */
    generateCacheKey(candidateData, jobData) {
        const candidateId = candidateData.id || JSON.stringify(candidateData).substring(0, 50);
        const jobId = jobData.id || JSON.stringify(jobData).substring(0, 50);
        return `exp_${candidateId}_${jobId}`;
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
            finalScore: 0.5,
            error: 'Données insuffisantes pour évaluation complète',
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
    module.exports = ExperienceLevelMatcher;
}

if (typeof window !== 'undefined') {
    window.ExperienceLevelMatcher = ExperienceLevelMatcher;
}
