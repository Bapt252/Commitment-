/**
 * NEXTEN SEMANTIC COMPATIBILITY ENGINE
 * Algorithme de Compatibilité Sémantique GPT - Critère #1 (25% du score total)
 * Architecture optimisée pour l'exploitation des parsers GPT symétriques
 */

class NextenCompatibilityEngine {
    constructor() {
        this.cache = new Map();
        this.performanceMetrics = {
            totalCalculations: 0,
            cacheHits: 0,
            averageTime: 0
        };
        
        // Configuration du moteur sémantique
        this.config = {
            temporal: {
                degradationRate: 0.07,  // -7% par année
                minimumWeight: 0.30,    // Plancher 30%
                currentBoost: 1.0       // 100% pour expérience actuelle
            },
            scoring: {
                titleWeight: 0.40,      // 40% - Titre/Poste
                skillsWeight: 0.35,     // 35% - Compétences
                responsibilitiesWeight: 0.25  // 25% - Responsabilités/Missions
            },
            similarity: {
                threshold: 0.15,        // Seuil minimum de similarité
                cacheSize: 1000        // Taille du cache de similarité
            }
        };

        this.initializeSectorDictionaries();
        this.initializeSkillHierarchies();
    }

    /**
     * DICTIONNAIRES SECTORIELS SPÉCIALISÉS
     * Gestion intelligente des synonymes par secteur d'activité
     */
    initializeSectorDictionaries() {
        this.sectorSynonyms = {
            luxe: {
                titles: [
                    ['assistant', 'assistante'],
                    ['manager', 'responsable', 'chef'],
                    ['coordinator', 'coordinateur', 'coordinatrice'],
                    ['office manager', 'gestionnaire', 'administrative'],
                    ['director', 'directeur', 'directrice'],
                    ['consultant', 'conseiller', 'conseillère']
                ],
                skills: [
                    ['sap', 'erp', 'système intégré'],
                    ['retail', 'vente', 'commerce'],
                    ['luxury', 'luxe', 'haut de gamme'],
                    ['fashion', 'mode', 'textile'],
                    ['cosmetics', 'cosmétique', 'beauté'],
                    ['customer service', 'service client', 'relation client']
                ],
                companies: [
                    ['hermès', 'hermes'],
                    ['dior', 'christian dior'],
                    ['by kilian', 'kilian'],
                    ['lvmh', 'louis vuitton']
                ]
            },
            tech: {
                titles: [
                    ['developer', 'développeur', 'dev'],
                    ['engineer', 'ingénieur', 'ing'],
                    ['analyst', 'analyste'],
                    ['architect', 'architecte']
                ],
                skills: [
                    ['javascript', 'js', 'node'],
                    ['python', 'py'],
                    ['database', 'bdd', 'sql'],
                    ['cloud', 'aws', 'azure']
                ]
            }
        };
    }

    /**
     * HIÉRARCHIES DE COMPÉTENCES
     * Gestion des relations parent-enfant (ERP ⊃ SAP ⊃ MyEasyOrder)
     */
    initializeSkillHierarchies() {
        this.skillHierarchies = {
            'erp': ['sap', 'oracle', 'microsoft dynamics', 'myeasyorder'],
            'sap': ['sap business one', 'sap s/4hana', 'myeasyorder'],
            'office': ['microsoft office', 'excel', 'word', 'powerpoint', 'outlook'],
            'microsoft office': ['excel', 'word', 'powerpoint', 'outlook'],
            'management': ['leadership', 'équipe', 'coordination', 'planning'],
            'retail': ['vente', 'commerce', 'point de vente', 'caisse']
        };
    }

    /**
     * MOTEUR PRINCIPAL DE COMPATIBILITÉ
     * Calcul du score de compatibilité sémantique avec pondération temporelle
     */
    async calculateCompatibility(candidateData, jobData) {
        const startTime = performance.now();
        
        try {
            // Extraction des données depuis les parsers GPT
            const candidate = this.extractCandidateFeatures(candidateData);
            const job = this.extractJobFeatures(jobData);
            
            // Calculs de compatibilité par dimension
            const titleScore = await this.calculateTitleCompatibility(candidate, job);
            const skillsScore = await this.calculateSkillsCompatibility(candidate, job);
            const responsibilitiesScore = await this.calculateResponsibilitiesCompatibility(candidate, job);
            
            // Application de la pondération temporelle
            const temporalWeights = this.calculateTemporalWeights(candidate.experiences);
            
            // Score composite final
            const finalScore = this.calculateCompositeScore({
                title: titleScore,
                skills: skillsScore,
                responsibilities: responsibilitiesScore
            }, temporalWeights);
            
            // Métriques de performance
            const calculationTime = performance.now() - startTime;
            this.updatePerformanceMetrics(calculationTime);
            
            return {
                score: finalScore,
                breakdown: {
                    title: { score: titleScore.score, weight: this.config.scoring.titleWeight },
                    skills: { score: skillsScore.score, weight: this.config.scoring.skillsWeight },
                    responsibilities: { score: responsibilitiesScore.score, weight: this.config.scoring.responsibilitiesWeight }
                },
                temporal: temporalWeights,
                performance: {
                    calculationTime: calculationTime,
                    cacheHit: false
                },
                details: {
                    titleMatches: titleScore.matches,
                    skillMatches: skillsScore.matches,
                    responsibilityMatches: responsibilitiesScore.matches
                }
            };
            
        } catch (error) {
            console.error('Erreur dans le calcul de compatibilité:', error);
            return { score: 0, error: error.message };
        }
    }

    /**
     * EXTRACTION DES CARACTÉRISTIQUES CANDIDAT
     * Exploitation optimale des données CV Parser v6.2.0
     */
    extractCandidateFeatures(candidateData) {
        return {
            titles: this.extractTitles(candidateData.experiences_professionnelles || []),
            skills: [
                ...(candidateData.competences_detaillees || []),
                ...(candidateData.competences_techniques || []),
                ...(candidateData.certifications || [])
            ],
            experiences: candidateData.experiences_professionnelles || [],
            profileType: candidateData.analyse_cv?.profil_type || '',
            responsibilities: this.extractResponsibilities(candidateData.experiences_professionnelles || []),
            sector: this.detectSector(candidateData)
        };
    }

    /**
     * EXTRACTION DES CARACTÉRISTIQUES POSTE
     * Exploitation optimale des données Job Parser GPT
     */
    extractJobFeatures(jobData) {
        return {
            title: jobData.titre_poste || '',
            mainMission: jobData.mission_principale || '',
            skills: jobData.competences || [],
            requiredExperience: jobData.experience_requise || '',
            responsibilities: jobData.missions || jobData.responsabilites || [],
            sector: this.detectJobSector(jobData)
        };
    }

    /**
     * CALCUL DE COMPATIBILITÉ DES TITRES
     * Analyse sémantique avancée avec synonymes sectoriels
     */
    async calculateTitleCompatibility(candidate, job) {
        const cacheKey = `title_${this.hashString(candidate.titles.join(','))}_${this.hashString(job.title)}`;
        
        if (this.cache.has(cacheKey)) {
            this.performanceMetrics.cacheHits++;
            return this.cache.get(cacheKey);
        }
        
        let maxSimilarity = 0;
        const matches = [];
        
        for (const candidateTitle of candidate.titles) {
            const similarity = this.calculateSemanticSimilarity(
                candidateTitle.toLowerCase(),
                job.title.toLowerCase(),
                candidate.sector
            );
            
            if (similarity > maxSimilarity) {
                maxSimilarity = similarity;
            }
            
            if (similarity > this.config.similarity.threshold) {
                matches.push({
                    candidateTitle,
                    jobTitle: job.title,
                    similarity,
                    type: 'title'
                });
            }
        }
        
        const result = {
            score: Math.min(maxSimilarity, 1.0),
            matches
        };
        
        this.cache.set(cacheKey, result);
        return result;
    }

    /**
     * CALCUL DE COMPATIBILITÉ DES COMPÉTENCES
     * Matching intelligent avec hiérarchies de compétences
     */
    async calculateSkillsCompatibility(candidate, job) {
        const cacheKey = `skills_${this.hashString(candidate.skills.join(','))}_${this.hashString(job.skills.join(','))}`;
        
        if (this.cache.has(cacheKey)) {
            this.performanceMetrics.cacheHits++;
            return this.cache.get(cacheKey);
        }
        
        let totalSimilarity = 0;
        let matchCount = 0;
        const matches = [];
        
        for (const jobSkill of job.skills) {
            let bestMatch = 0;
            let bestCandidateSkill = '';
            
            for (const candidateSkill of candidate.skills) {
                const similarity = this.calculateSkillSimilarity(
                    candidateSkill.toLowerCase(),
                    jobSkill.toLowerCase(),
                    candidate.sector
                );
                
                if (similarity > bestMatch) {
                    bestMatch = similarity;
                    bestCandidateSkill = candidateSkill;
                }
            }
            
            if (bestMatch > this.config.similarity.threshold) {
                totalSimilarity += bestMatch;
                matchCount++;
                matches.push({
                    candidateSkill: bestCandidateSkill,
                    jobSkill,
                    similarity: bestMatch,
                    type: 'skill'
                });
            }
        }
        
        const result = {
            score: matchCount > 0 ? totalSimilarity / job.skills.length : 0,
            matches
        };
        
        this.cache.set(cacheKey, result);
        return result;
    }

    /**
     * CALCUL DE COMPATIBILITÉ DES RESPONSABILITÉS
     * Matching sémantique des missions et responsabilités
     */
    async calculateResponsibilitiesCompatibility(candidate, job) {
        if (!candidate.responsibilities.length || !job.responsibilities.length) {
            return { score: 0, matches: [] };
        }
        
        const cacheKey = `resp_${this.hashString(candidate.responsibilities.join(','))}_${this.hashString(job.responsibilities.join(','))}`;
        
        if (this.cache.has(cacheKey)) {
            this.performanceMetrics.cacheHits++;
            return this.cache.get(cacheKey);
        }
        
        let totalSimilarity = 0;
        const matches = [];
        
        for (const jobResp of job.responsibilities) {
            let bestMatch = 0;
            let bestCandidateResp = '';
            
            for (const candidateResp of candidate.responsibilities) {
                const similarity = this.calculateSemanticSimilarity(
                    candidateResp.toLowerCase(),
                    jobResp.toLowerCase(),
                    candidate.sector
                );
                
                if (similarity > bestMatch) {
                    bestMatch = similarity;
                    bestCandidateResp = candidateResp;
                }
            }
            
            if (bestMatch > this.config.similarity.threshold) {
                totalSimilarity += bestMatch;
                matches.push({
                    candidateResponsibility: bestCandidateResp,
                    jobResponsibility: jobResp,
                    similarity: bestMatch,
                    type: 'responsibility'
                });
            }
        }
        
        const result = {
            score: totalSimilarity / job.responsibilities.length,
            matches
        };
        
        this.cache.set(cacheKey, result);
        return result;
    }

    /**
     * PONDÉRATION TEMPORELLE INTELLIGENTE
     * Formule : max(0.30, 1.0 - (années_depuis * 0.07))
     */
    calculateTemporalWeights(experiences) {
        const currentYear = new Date().getFullYear();
        const weights = [];
        
        for (const exp of experiences) {
            const endYear = exp.date_fin ? 
                parseInt(exp.date_fin.toString().substr(0, 4)) : 
                currentYear;
            
            const yearsSince = currentYear - endYear;
            const weight = Math.max(
                this.config.temporal.minimumWeight,
                this.config.temporal.currentBoost - (yearsSince * this.config.temporal.degradationRate)
            );
            
            weights.push({
                experience: exp.poste || exp.titre,
                yearsSince,
                weight,
                company: exp.entreprise
            });
        }
        
        return weights;
    }

    /**
     * CALCUL DE SIMILARITÉ SÉMANTIQUE AVANCÉE
     * Intégration des dictionnaires sectoriels et synonymes
     */
    calculateSemanticSimilarity(text1, text2, sector = null) {
        // Similarité directe
        if (text1 === text2) return 1.0;
        
        // Vérification des synonymes sectoriels
        if (sector && this.sectorSynonyms[sector]) {
            const synonyms = this.sectorSynonyms[sector];
            
            for (const synonymGroup of [...synonyms.titles, ...synonyms.skills]) {
                if (synonymGroup.includes(text1) && synonymGroup.includes(text2)) {
                    return 0.95; // Très haute similarité pour synonymes
                }
            }
        }
        
        // Calcul de similarité textuelle (Jaccard + Levenshtein)
        const similarity = this.calculateTextSimilarity(text1, text2);
        
        return similarity;
    }

    /**
     * CALCUL DE SIMILARITÉ DES COMPÉTENCES
     * Avec gestion des hiérarchies de compétences
     */
    calculateSkillSimilarity(skill1, skill2, sector = null) {
        // Similarité directe
        if (skill1 === skill2) return 1.0;
        
        // Vérification hiérarchies de compétences
        for (const [parent, children] of Object.entries(this.skillHierarchies)) {
            if (parent === skill1 && children.includes(skill2)) {
                return 0.85; // Compétence parent-enfant
            }
            if (parent === skill2 && children.includes(skill1)) {
                return 0.90; // Compétence enfant-parent (plus valorisée)
            }
            if (children.includes(skill1) && children.includes(skill2)) {
                return 0.80; // Compétences sœurs
            }
        }
        
        // Calcul sémantique standard
        return this.calculateSemanticSimilarity(skill1, skill2, sector);
    }

    /**
     * CALCUL DE SIMILARITÉ TEXTUELLE
     * Combinaison Jaccard + Levenshtein optimisée
     */
    calculateTextSimilarity(text1, text2) {
        const words1 = new Set(text1.split(/\s+/));
        const words2 = new Set(text2.split(/\s+/));
        
        // Similarité Jaccard
        const intersection = new Set([...words1].filter(x => words2.has(x)));
        const union = new Set([...words1, ...words2]);
        const jaccardSim = intersection.size / union.size;
        
        // Distance de Levenshtein normalisée
        const levenshteinDist = this.levenshteinDistance(text1, text2);
        const maxLength = Math.max(text1.length, text2.length);
        const levenshteinSim = maxLength > 0 ? 1 - (levenshteinDist / maxLength) : 1;
        
        // Combinaison pondérée
        return (jaccardSim * 0.6) + (levenshteinSim * 0.4);
    }

    /**
     * CALCUL DU SCORE COMPOSITE FINAL
     * Pondération intelligente avec poids temporels
     */
    calculateCompositeScore(scores, temporalWeights) {
        const weights = this.config.scoring;
        
        // Score de base pondéré
        const baseScore = (
            scores.title.score * weights.titleWeight +
            scores.skills.score * weights.skillsWeight +
            scores.responsibilities.score * weights.responsibilitiesWeight
        );
        
        // Application de la pondération temporelle moyenne
        const avgTemporalWeight = temporalWeights.length > 0 ?
            temporalWeights.reduce((sum, tw) => sum + tw.weight, 0) / temporalWeights.length :
            1.0;
        
        return Math.min(baseScore * avgTemporalWeight, 1.0);
    }

    /**
     * UTILITAIRES ET MÉTHODES D'EXTRACTION
     */
    extractTitles(experiences) {
        return experiences.map(exp => exp.poste || exp.titre).filter(Boolean);
    }

    extractResponsibilities(experiences) {
        const responsibilities = [];
        for (const exp of experiences) {
            if (exp.missions) responsibilities.push(...exp.missions);
            if (exp.responsabilites) responsibilities.push(...exp.responsabilites);
            if (exp.description) responsibilities.push(exp.description);
        }
        return responsibilities.filter(Boolean);
    }

    detectSector(candidateData) {
        const experiences = candidateData.experiences_professionnelles || [];
        const companies = experiences.map(exp => exp.entreprise?.toLowerCase()).filter(Boolean);
        
        // Détection secteur luxe
        const luxuryKeywords = ['hermès', 'dior', 'chanel', 'louis vuitton', 'lvmh', 'kilian', 'luxe', 'luxury'];
        if (companies.some(company => luxuryKeywords.some(keyword => company.includes(keyword)))) {
            return 'luxe';
        }
        
        return 'general';
    }

    detectJobSector(jobData) {
        const title = (jobData.titre_poste || '').toLowerCase();
        const description = (jobData.mission_principale || '').toLowerCase();
        
        if (title.includes('luxe') || description.includes('luxury') || description.includes('luxe')) {
            return 'luxe';
        }
        
        return 'general';
    }

    levenshteinDistance(str1, str2) {
        const matrix = Array(str2.length + 1).fill().map(() => Array(str1.length + 1).fill(0));
        
        for (let i = 0; i <= str1.length; i++) matrix[0][i] = i;
        for (let j = 0; j <= str2.length; j++) matrix[j][0] = j;
        
        for (let j = 1; j <= str2.length; j++) {
            for (let i = 1; i <= str1.length; i++) {
                const cost = str1[i - 1] === str2[j - 1] ? 0 : 1;
                matrix[j][i] = Math.min(
                    matrix[j - 1][i] + 1,
                    matrix[j][i - 1] + 1,
                    matrix[j - 1][i - 1] + cost
                );
            }
        }
        
        return matrix[str2.length][str1.length];
    }

    hashString(str) {
        let hash = 0;
        for (let i = 0; i < str.length; i++) {
            const char = str.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash;
        }
        return hash.toString();
    }

    updatePerformanceMetrics(calculationTime) {
        this.performanceMetrics.totalCalculations++;
        this.performanceMetrics.averageTime = 
            (this.performanceMetrics.averageTime * (this.performanceMetrics.totalCalculations - 1) + calculationTime) 
            / this.performanceMetrics.totalCalculations;
    }

    /**
     * MÉTRIQUES DE PERFORMANCE SYSTÈME
     */
    getPerformanceReport() {
        return {
            ...this.performanceMetrics,
            cacheHitRate: this.performanceMetrics.totalCalculations > 0 ? 
                (this.performanceMetrics.cacheHits / this.performanceMetrics.totalCalculations * 100).toFixed(1) + '%' : '0%',
            cacheSize: this.cache.size
        };
    }
}

/**
 * INTÉGRATION AVEC NEXTEN SYSTEM
 * Extension seamless du NextenOptimizedSystem (Prompt 1)
 */
class NextenSemanticMatcherV2 extends NextenCompatibilityEngine {
    constructor(nextenSystem) {
        super();
        this.nextenSystem = nextenSystem;
        this.unifiedSchema = nextenSystem?.unifiedSchema;
    }

    /**
     * PONT AVEC L'ARCHITECTURE EXISTANTE
     * Hook seamless avec le système unifié
     */
    async enhancedMatching(candidateId, jobId) {
        if (!this.nextenSystem) {
            throw new Error("NextenOptimizedSystem requis pour enhanced matching");
        }

        // Récupération des données via le système unifié
        const candidateData = await this.nextenSystem.getCandidateData(candidateId);
        const jobData = await this.nextenSystem.getJobData(jobId);

        // Calcul de compatibilité avec l'algorithme avancé
        const compatibilityResult = await this.calculateCompatibility(candidateData, jobData);

        // Intégration dans le scoring global Nexten
        return {
            criterium1_score: compatibilityResult.score * 0.25, // 25% du score total
            detailed_analysis: compatibilityResult,
            nexten_integration: {
                candidateId,
                jobId,
                calculatedAt: new Date().toISOString(),
                algorithm_version: "v2.0_semantic_enhanced"
            }
        };
    }
}

// Export pour utilisation dans l'architecture Nexten
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { NextenCompatibilityEngine, NextenSemanticMatcherV2 };
}

// Global pour usage navigateur
if (typeof window !== 'undefined') {
    window.NextenCompatibilityEngine = NextenCompatibilityEngine;
    window.NextenSemanticMatcherV2 = NextenSemanticMatcherV2;
}