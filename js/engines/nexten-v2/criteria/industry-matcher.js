/**
 * NEXTEN V2.0 - INDUSTRY MATCHER
 * Critère #7 (6% du score) - Secteurs préférés + rédhibitoires
 * Algorithme intelligent de matching sectoriel avec transferabilité
 */

class IndustryMatcher {
    constructor() {
        this.weight = 0.06; // 6% du score total Nexten V2.0
        this.name = 'industry';
        
        // Secteurs avec caractéristiques et sous-secteurs
        this.industryDatabase = {
            luxe: {
                label: 'Luxe',
                subcategories: ['maroquinerie', 'joaillerie', 'horlogerie', 'parfums', 'mode_luxe', 'vins_spiritueux'],
                characteristics: {
                    prestige_level: 'very_high',
                    innovation_pace: 'medium',
                    internationalization: 'very_high',
                    seasonality: 'high',
                    customer_exclusivity: 'very_high',
                    craftsmanship: 'very_high'
                },
                typical_roles: ['chef_produit', 'marketing', 'retail', 'communication', 'commercial'],
                growth_trend: 'stable_premium',
                salary_level: 'high',
                work_culture: 'excellence_oriented'
            },
            mode: {
                label: 'Mode',
                subcategories: ['pret_a_porter', 'accessoires', 'chaussures', 'lingerie', 'sportswear', 'streetwear'],
                characteristics: {
                    prestige_level: 'high',
                    innovation_pace: 'very_high',
                    internationalization: 'high',
                    seasonality: 'very_high',
                    creativity_focus: 'very_high',
                    trend_sensitivity: 'very_high'
                },
                typical_roles: ['styliste', 'chef_produit', 'acheteur', 'marketing', 'retail'],
                growth_trend: 'dynamic',
                salary_level: 'medium_high',
                work_culture: 'creative_fast_paced'
            },
            cosmetique: {
                label: 'Cosmétique',
                subcategories: ['parfums', 'soins_visage', 'maquillage', 'soins_corps', 'capillaire', 'bio_naturel'],
                characteristics: {
                    prestige_level: 'high',
                    innovation_pace: 'high',
                    internationalization: 'very_high',
                    regulation_level: 'high',
                    research_intensity: 'high',
                    brand_importance: 'very_high'
                },
                typical_roles: ['chef_produit', 'marketing', 'formulation', 'regulatory', 'commercial'],
                growth_trend: 'growing',
                salary_level: 'medium_high',
                work_culture: 'brand_focused'
            },
            tech: {
                label: 'Technologie',
                subcategories: ['software', 'hardware', 'fintech', 'e_commerce', 'saas', 'ai_ml', 'cybersecurity'],
                characteristics: {
                    prestige_level: 'high',
                    innovation_pace: 'very_high',
                    internationalization: 'very_high',
                    growth_speed: 'very_high',
                    disruption_potential: 'very_high',
                    skills_evolution: 'very_high'
                },
                typical_roles: ['developpeur', 'chef_produit', 'data_scientist', 'devops', 'product_manager'],
                growth_trend: 'exponential',
                salary_level: 'high',
                work_culture: 'innovation_agile'
            },
            finance: {
                label: 'Finance',
                subcategories: ['banque', 'assurance', 'asset_management', 'private_equity', 'trading', 'fintech'],
                characteristics: {
                    prestige_level: 'high',
                    innovation_pace: 'medium',
                    internationalization: 'high',
                    regulation_level: 'very_high',
                    stability: 'high',
                    performance_pressure: 'very_high'
                },
                typical_roles: ['analyste', 'gestionnaire', 'conseiller', 'trader', 'risk_manager'],
                growth_trend: 'stable',
                salary_level: 'very_high',
                work_culture: 'performance_driven'
            },
            sante: {
                label: 'Santé',
                subcategories: ['pharma', 'medical_devices', 'biotech', 'digital_health', 'diagnostics'],
                characteristics: {
                    prestige_level: 'high',
                    innovation_pace: 'high',
                    internationalization: 'high',
                    regulation_level: 'very_high',
                    social_impact: 'very_high',
                    research_cycles: 'very_long'
                },
                typical_roles: ['recherche', 'regulatory', 'medical_affairs', 'commercial', 'clinical_research'],
                growth_trend: 'growing',
                salary_level: 'high',
                work_culture: 'mission_driven'
            },
            energie: {
                label: 'Énergie',
                subcategories: ['petrole_gaz', 'renouvelables', 'nucleaire', 'utilities', 'green_tech'],
                characteristics: {
                    prestige_level: 'medium',
                    innovation_pace: 'medium',
                    internationalization: 'high',
                    regulation_level: 'high',
                    environmental_impact: 'very_high',
                    capital_intensity: 'very_high'
                },
                typical_roles: ['ingenieur', 'chef_projet', 'business_developer', 'regulatory', 'operations'],
                growth_trend: 'transformation',
                salary_level: 'high',
                work_culture: 'engineering_focused'
            }
        };

        // Matrice de transferabilité entre secteurs
        this.transferabilityMatrix = {
            luxe: {
                mode: 0.85,
                cosmetique: 0.80,
                tech: 0.45,
                finance: 0.40,
                sante: 0.35,
                energie: 0.20
            },
            mode: {
                luxe: 0.85,
                cosmetique: 0.75,
                tech: 0.50,
                finance: 0.35,
                sante: 0.30,
                energie: 0.20
            },
            cosmetique: {
                luxe: 0.80,
                mode: 0.75,
                sante: 0.65,
                tech: 0.45,
                finance: 0.35,
                energie: 0.25
            },
            tech: {
                finance: 0.70,
                sante: 0.60,
                cosmetique: 0.45,
                luxe: 0.45,
                mode: 0.50,
                energie: 0.55
            },
            finance: {
                tech: 0.70,
                sante: 0.50,
                luxe: 0.40,
                cosmetique: 0.35,
                mode: 0.35,
                energie: 0.45
            },
            sante: {
                cosmetique: 0.65,
                tech: 0.60,
                finance: 0.50,
                luxe: 0.35,
                mode: 0.30,
                energie: 0.40
            },
            energie: {
                tech: 0.55,
                finance: 0.45,
                sante: 0.40,
                luxe: 0.20,
                mode: 0.20,
                cosmetique: 0.25
            }
        };

        // Profils candidats selon préférences sectorielles
        this.candidateSectorProfiles = {
            sector_specialist: {
                preference_type: 'focused',
                sector_depth: 'deep',
                transferability_tolerance: 'low',
                experience_weight: 'high'
            },
            industry_versatile: {
                preference_type: 'broad',
                sector_depth: 'medium',
                transferability_tolerance: 'high',
                experience_weight: 'medium'
            },
            sector_explorer: {
                preference_type: 'discovery',
                sector_depth: 'emerging',
                transferability_tolerance: 'very_high',
                experience_weight: 'low'
            },
            prestige_seeker: {
                preference_type: 'prestige_focused',
                sector_depth: 'surface',
                transferability_tolerance: 'medium',
                experience_weight: 'medium'
            }
        };

        // Cache des analyses sectorielles
        this.industryCache = new Map();
        
        // Métriques de performance
        this.metrics = {
            totalAnalyses: 0,
            averageAnalysisTime: 0,
            cacheHitRate: 0
        };

        console.log('🏭 IndustryMatcher initialisé - Critère #7 (6%)');
    }

    /**
     * CALCUL PRINCIPAL DU SCORE SECTORIEL
     * Analyse intelligente préférences sectorielles vs offre
     */
    async calculateIndustryScore(candidateData, jobData, companyData = {}) {
        const startTime = performance.now();
        
        try {
            // Cache check
            const cacheKey = this.generateIndustryCacheKey(candidateData, jobData, companyData);
            const cached = this.industryCache.get(cacheKey);
            if (cached && this.isCacheValid(cached)) {
                this.updateMetrics(performance.now() - startTime, true);
                return cached.result;
            }

            // Extraction des préférences sectorielles candidat
            const candidateSectorPreferences = this.extractCandidateSectorPreferences(candidateData);
            
            // Analyse du secteur de l'offre
            const jobSectorAnalysis = this.analyzeJobSector(jobData, companyData);
            
            if (!this.validateIndustryData(candidateSectorPreferences, jobSectorAnalysis)) {
                return this.getFallbackScore('Données sectorielles insuffisantes');
            }

            // Calcul du matching direct des secteurs
            const directSectorMatch = this.calculateDirectSectorMatch(candidateSectorPreferences, jobSectorAnalysis);
            
            // Analyse de la transferabilité
            const transferabilityScore = this.calculateTransferabilityScore(candidateSectorPreferences, jobSectorAnalysis);
            
            // Évaluation de l'expérience sectorielle
            const experienceRelevance = this.calculateSectorExperienceRelevance(candidateSectorPreferences, jobSectorAnalysis);
            
            // Détection des secteurs rédhibitoires
            const avoidanceAnalysis = this.analyzeAvoidanceSectors(candidateSectorPreferences, jobSectorAnalysis);
            
            // Score composite final
            const finalScore = this.computeFinalIndustryScore({
                directMatch: directSectorMatch,
                transferability: transferabilityScore,
                experience: experienceRelevance,
                avoidance: avoidanceAnalysis
            });

            const result = {
                finalScore: Math.min(finalScore, 1.0),
                industryAnalysis: {
                    candidate_preferences: candidateSectorPreferences,
                    job_sector: jobSectorAnalysis,
                    direct_match: directSectorMatch,
                    transferability: transferabilityScore,
                    experience_relevance: experienceRelevance
                },
                insights: {
                    sector_strengths: this.identifySectorStrengths(candidateSectorPreferences, jobSectorAnalysis),
                    transferability_opportunities: this.identifyTransferabilityOpportunities(candidateSectorPreferences, jobSectorAnalysis),
                    sector_recommendations: this.generateSectorRecommendations(candidateSectorPreferences, jobSectorAnalysis, finalScore)
                },
                performance: {
                    analysisTime: performance.now() - startTime,
                    dataQuality: this.assessIndustryDataQuality(candidateSectorPreferences, jobSectorAnalysis),
                    confidence: this.calculateIndustryConfidence(candidateSectorPreferences, jobSectorAnalysis)
                }
            };

            // Mise en cache
            this.industryCache.set(cacheKey, {
                result: result,
                timestamp: Date.now()
            });

            this.updateMetrics(performance.now() - startTime, false);
            return result;

        } catch (error) {
            console.error('❌ Erreur IndustryMatcher:', error);
            return this.getFallbackScore(`Erreur analyse: ${error.message}`);
        }
    }

    /**
     * EXTRACTION DES PRÉFÉRENCES SECTORIELLES CANDIDAT
     * Analyse des secteurs cibles, acceptables et à éviter
     */
    extractCandidateSectorPreferences(candidateData) {
        const preferences = {
            target_sectors: [],      // Secteurs souhaités
            acceptable_sectors: [],  // Secteurs acceptables
            exclusion_sectors: [],   // Secteurs rédhibitoires
            experience_sectors: [],  // Secteurs d'expérience
            profile_type: null       // Type de profil sectoriel
        };

        // Secteurs cibles explicites
        if (candidateData.secteurs_cibles || candidateData.target_industries) {
            preferences.target_sectors = this.parseSectorList(
                candidateData.secteurs_cibles || candidateData.target_industries
            );
        }

        // Secteurs acceptables
        if (candidateData.secteurs_acceptables || candidateData.acceptable_industries) {
            preferences.acceptable_sectors = this.parseSectorList(
                candidateData.secteurs_acceptables || candidateData.acceptable_industries
            );
        }

        // Secteurs à éviter
        if (candidateData.secteurs_redhibitoires || candidateData.avoid_industries) {
            preferences.exclusion_sectors = this.parseSectorList(
                candidateData.secteurs_redhibitoires || candidateData.avoid_industries
            );
        }

        // Extraction des secteurs d'expérience
        preferences.experience_sectors = this.extractExperienceSectors(candidateData);
        
        // Inférence du profil candidat
        preferences.profile_type = this.inferCandidateSectorProfile(candidateData);

        return preferences;
    }

    /**
     * ANALYSE DU SECTEUR DE L'OFFRE
     * Identification et caractérisation du secteur du poste
     */
    analyzeJobSector(jobData, companyData) {
        const analysis = {
            primary_sector: null,
            secondary_sectors: [],
            sector_characteristics: null,
            company_positioning: null,
            explicit_sector: null,
            inferred_sector: null
        };

        // Secteur explicite
        analysis.explicit_sector = this.extractExplicitSector(jobData, companyData);
        
        // Inférence du secteur
        analysis.inferred_sector = this.inferSectorFromContext(jobData, companyData);
        
        // Détermination du secteur principal
        analysis.primary_sector = analysis.explicit_sector || analysis.inferred_sector || 'general';
        
        // Caractéristiques du secteur
        if (this.industryDatabase[analysis.primary_sector]) {
            analysis.sector_characteristics = this.industryDatabase[analysis.primary_sector].characteristics;
        }
        
        // Positionnement de l'entreprise dans le secteur
        analysis.company_positioning = this.analyzeCompanyPositioning(analysis.primary_sector, companyData);

        return analysis;
    }

    /**
     * CALCUL DU MATCHING DIRECT DES SECTEURS
     * Score basé sur la correspondance exacte des préférences
     */
    calculateDirectSectorMatch(candidatePreferences, jobSectorAnalysis) {
        const jobSector = jobSectorAnalysis.primary_sector;
        
        // Match parfait avec secteurs cibles
        if (candidatePreferences.target_sectors.includes(jobSector)) {
            return 1.0;
        }
        
        // Match avec secteurs acceptables
        if (candidatePreferences.acceptable_sectors.includes(jobSector)) {
            return 0.8;
        }
        
        // Match avec secteurs d'expérience
        if (candidatePreferences.experience_sectors.includes(jobSector)) {
            return 0.7;
        }
        
        // Exclusion rédhibitoire
        if (candidatePreferences.exclusion_sectors.includes(jobSector)) {
            return 0.1;
        }
        
        // Aucune préférence explicite
        return 0.5;
    }

    /**
     * CALCUL DU SCORE DE TRANSFERABILITÉ
     * Évaluation de la transférabilité des compétences entre secteurs
     */
    calculateTransferabilityScore(candidatePreferences, jobSectorAnalysis) {
        const jobSector = jobSectorAnalysis.primary_sector;
        let maxTransferability = 0;
        
        // Recherche de la meilleure transferabilité possible
        candidatePreferences.experience_sectors.forEach(expSector => {
            const transferability = this.getTransferabilityScore(expSector, jobSector);
            maxTransferability = Math.max(maxTransferability, transferability);
        });
        
        candidatePreferences.target_sectors.forEach(targetSector => {
            const transferability = this.getTransferabilityScore(targetSector, jobSector);
            maxTransferability = Math.max(maxTransferability, transferability);
        });
        
        return maxTransferability;
    }

    /**
     * ÉVALUATION DE LA PERTINENCE D'EXPÉRIENCE SECTORIELLE
     * Score basé sur la profondeur et récence de l'expérience
     */
    calculateSectorExperienceRelevance(candidatePreferences, jobSectorAnalysis) {
        const jobSector = jobSectorAnalysis.primary_sector;
        let experienceScore = 0.3; // Score de base
        
        // Bonus pour expérience directe dans le secteur
        if (candidatePreferences.experience_sectors.includes(jobSector)) {
            experienceScore += 0.4; // +40% pour expérience directe
        }
        
        // Bonus pour expérience dans secteurs similaires
        candidatePreferences.experience_sectors.forEach(expSector => {
            const similarity = this.getSectorSimilarity(expSector, jobSector);
            if (similarity > 0.7) {
                experienceScore += 0.2; // +20% pour secteurs très similaires
            } else if (similarity > 0.5) {
                experienceScore += 0.1; // +10% pour secteurs similaires
            }
        });
        
        return Math.min(experienceScore, 1.0);
    }

    /**
     * ANALYSE DES SECTEURS RÉDHIBITOIRES
     * Détection et impact des secteurs à éviter
     */
    analyzeAvoidanceSectors(candidatePreferences, jobSectorAnalysis) {
        const jobSector = jobSectorAnalysis.primary_sector;
        const analysis = {
            is_avoided: false,
            avoidance_reason: null,
            severity: 'none',
            impact: 0
        };
        
        if (candidatePreferences.exclusion_sectors.includes(jobSector)) {
            analysis.is_avoided = true;
            analysis.avoidance_reason = `Secteur "${jobSector}" dans la liste des secteurs à éviter`;
            analysis.severity = 'high';
            analysis.impact = 0.8; // Malus de 80%
        }
        
        return analysis;
    }

    /**
     * SCORE COMPOSITE FINAL INDUSTRIE
     * Combinaison pondérée des différents éléments
     */
    computeFinalIndustryScore(components) {
        // Base score selon matching direct
        let finalScore = components.directMatch * 0.50; // 50% - Matching direct
        
        // Si pas de match direct, utiliser transferabilité
        if (components.directMatch < 0.6) {
            finalScore += components.transferability * 0.30; // 30% - Transferabilité
        } else {
            finalScore += 0.30; // Bonus si déjà bon match direct
        }
        
        // Expérience sectorielle
        finalScore += components.experience * 0.20; // 20% - Expérience
        
        // Pénalité secteurs rédhibitoires
        if (components.avoidance.is_avoided) {
            finalScore *= (1 - components.avoidance.impact);
        }
        
        return Math.max(Math.min(finalScore, 1.0), 0.05);
    }

    /**
     * UTILITAIRES DE PARSING ET ANALYSE
     */
    parseSectorList(sectorInput) {
        if (!sectorInput) return [];
        
        if (Array.isArray(sectorInput)) {
            return sectorInput.map(s => this.normalizeSectorName(s)).filter(s => s);
        }
        
        if (typeof sectorInput === 'string') {
            return sectorInput.split(/[,;]/)
                               .map(s => this.normalizeSectorName(s.trim()))
                               .filter(s => s);
        }
        
        return [];
    }

    normalizeSectorName(sectorName) {
        if (!sectorName) return null;
        
        const normalized = sectorName.toLowerCase().replace(/[^a-z]/g, '');
        
        // Mapping des variantes vers secteurs standardisés
        const mappings = {
            'luxe': ['luxe', 'luxury', 'haut'],
            'mode': ['mode', 'fashion', 'textile', 'pret'],
            'cosmetique': ['cosmetique', 'cosmetic', 'beaute', 'parfum'],
            'tech': ['tech', 'technologie', 'informatique', 'digital', 'software'],
            'finance': ['finance', 'banque', 'assurance', 'trading'],
            'sante': ['sante', 'health', 'pharma', 'medical', 'biotech'],
            'energie': ['energie', 'energy', 'petrole', 'renouvelable']
        };
        
        for (const [sector, variants] of Object.entries(mappings)) {
            if (variants.some(variant => normalized.includes(variant))) {
                return sector;
            }
        }
        
        return null;
    }

    extractExperienceSectors(candidateData) {
        const sectors = [];
        
        if (candidateData.experiences && Array.isArray(candidateData.experiences)) {
            candidateData.experiences.forEach(exp => {
                if (exp.secteur || exp.industry) {
                    const sector = this.normalizeSectorName(exp.secteur || exp.industry);
                    if (sector && !sectors.includes(sector)) {
                        sectors.push(sector);
                    }
                }
            });
        }
        
        return sectors;
    }

    getTransferabilityScore(fromSector, toSector) {
        if (fromSector === toSector) return 1.0;
        
        return this.transferabilityMatrix[fromSector]?.[toSector] || 0.3;
    }

    getSectorSimilarity(sector1, sector2) {
        if (sector1 === sector2) return 1.0;
        
        // Utiliser la matrice de transferabilité comme proxy de similarité
        const score1 = this.transferabilityMatrix[sector1]?.[sector2] || 0;
        const score2 = this.transferabilityMatrix[sector2]?.[sector1] || 0;
        
        return Math.max(score1, score2);
    }

    // Méthodes placeholder
    extractExplicitSector(jobData, companyData) {
        return this.normalizeSectorName(
            jobData.secteur || 
            jobData.industry || 
            companyData.secteur || 
            companyData.industry
        );
    }

    inferSectorFromContext(jobData, companyData) {
        // Inférence basée sur mots-clés dans description
        const text = (
            (jobData.description || '') + ' ' +
            (jobData.titre || '') + ' ' +
            (companyData.description || '') + ' ' +
            (companyData.nom || '')
        ).toLowerCase();
        
        for (const [sector, data] of Object.entries(this.industryDatabase)) {
            if (text.includes(sector) || 
                data.subcategories.some(sub => text.includes(sub))) {
                return sector;
            }
        }
        
        return null;
    }

    analyzeCompanyPositioning(sector, companyData) {
        return {
            market_position: 'established',
            size_in_sector: 'medium',
            innovation_level: 'standard'
        };
    }

    inferCandidateSectorProfile(candidateData) {
        const experienceSectors = this.extractExperienceSectors(candidateData);
        
        if (experienceSectors.length === 1) {
            return 'sector_specialist';
        } else if (experienceSectors.length > 2) {
            return 'industry_versatile';
        } else {
            return 'sector_explorer';
        }
    }

    identifySectorStrengths(candidatePreferences, jobSectorAnalysis) { return []; }
    identifyTransferabilityOpportunities(candidatePreferences, jobSectorAnalysis) { return []; }
    generateSectorRecommendations(candidatePreferences, jobSectorAnalysis, finalScore) { return []; }
    assessIndustryDataQuality(candidatePreferences, jobSectorAnalysis) { return 0.8; }
    calculateIndustryConfidence(candidatePreferences, jobSectorAnalysis) { return 0.85; }

    generateIndustryCacheKey(candidateData, jobData, companyData) {
        const key = JSON.stringify({
            target_sectors: candidateData.secteurs_cibles,
            job_sector: jobData.secteur,
            company_sector: companyData.secteur
        });
        return btoa(key).substring(0, 20);
    }

    isCacheValid(cached) {
        return (Date.now() - cached.timestamp) < 1800000; // 30 minutes
    }

    validateIndustryData(candidatePreferences, jobSectorAnalysis) {
        return candidatePreferences.target_sectors.length > 0 || 
               candidatePreferences.experience_sectors.length > 0 || 
               jobSectorAnalysis.primary_sector;
    }

    getFallbackScore(reason) {
        return {
            finalScore: 0.5,
            error: reason,
            fallback: true,
            timestamp: new Date().toISOString()
        };
    }

    updateMetrics(analysisTime, wasCacheHit) {
        this.metrics.totalAnalyses++;
        this.metrics.averageAnalysisTime = 
            (this.metrics.averageAnalysisTime * (this.metrics.totalAnalyses - 1) + analysisTime) 
            / this.metrics.totalAnalyses;
            
        if (wasCacheHit) {
            this.metrics.cacheHitRate = 
                (this.metrics.cacheHitRate * (this.metrics.totalAnalyses - 1) + 1) 
                / this.metrics.totalAnalyses;
        }
    }
}

// Export pour intégration
if (typeof module !== 'undefined' && module.exports) {
    module.exports = IndustryMatcher;
}

if (typeof window !== 'undefined') {
    window.IndustryMatcher = IndustryMatcher;
    console.log('🏭 IndustryMatcher disponible - Critère #7 (6%)');
}