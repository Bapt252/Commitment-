/**
 * NEXTEN V2.0 - COMPENSATION MATCHER
 * Critère #3 (15% du score) - Rémunération fourchettes + négociation
 * Algorithme intelligent de matching salarial avec facteurs contextuels
 */

class CompensationMatcher {
    constructor() {
        this.weight = 0.15; // 15% du score total Nexten V2.0
        this.name = 'compensation';
        
        // Grilles salariales sectorielles (en k€ annuel)
        this.sectorSalaryGrids = {
            luxe: {
                junior: { min: 35, max: 55 },
                intermediate: { min: 50, max: 75 },
                senior: { min: 70, max: 120 },
                expert: { min: 100, max: 180 }
            },
            mode: {
                junior: { min: 30, max: 45 },
                intermediate: { min: 40, max: 65 },
                senior: { min: 60, max: 100 },
                expert: { min: 90, max: 150 }
            },
            tech: {
                junior: { min: 40, max: 60 },
                intermediate: { min: 55, max: 85 },
                senior: { min: 75, max: 130 },
                expert: { min: 110, max: 200 }
            },
            cosmetique: {
                junior: { min: 32, max: 50 },
                intermediate: { min: 45, max: 70 },
                senior: { min: 65, max: 110 },
                expert: { min: 95, max: 160 }
            },
            finance: {
                junior: { min: 45, max: 70 },
                intermediate: { min: 65, max: 95 },
                senior: { min: 85, max: 150 },
                expert: { min: 120, max: 250 }
            },
            default: {
                junior: { min: 30, max: 50 },
                intermediate: { min: 45, max: 70 },
                senior: { min: 65, max: 100 },
                expert: { min: 90, max: 150 }
            }
        };

        // Ajustements géographiques (multiplicateur)
        this.locationAdjustments = {
            'paris': 1.15,        // +15% Paris
            'ile_de_france': 1.08, // +8% IDF
            'lyon': 1.05,         // +5% Lyon
            'marseille': 1.02,    // +2% Marseille
            'toulouse': 1.02,     // +2% Toulouse
            'bordeaux': 1.00,     // Référence
            'lille': 0.98,        // -2% Lille
            'nantes': 0.98,       // -2% Nantes
            'strasbourg': 0.97,   // -3% Strasbourg
            'montpellier': 0.95,  // -5% Montpellier
            'default': 1.00       // Référence
        };

        // Multiplicateurs expérience
        this.experienceMultipliers = {
            '0-1': 0.85,          // -15% débutant
            '1-3': 1.00,          // Référence junior
            '3-5': 1.20,          // +20% intermédiaire
            '5-8': 1.45,          // +45% senior
            '8-12': 1.70,         // +70% expert
            '12+': 2.00           // +100% expert senior
        };

        // Cache des calculs
        this.calculationCache = new Map();
        
        // Métriques de performance
        this.metrics = {
            totalCalculations: 0,
            averageCalculationTime: 0,
            cacheHitRate: 0
        };

        console.log('💰 CompensationMatcher initialisé - Critère #3 (15%)');
    }

    /**
     * CALCUL PRINCIPAL DU SCORE DE COMPENSATION
     * Algorithme de matching intelligent avec facteurs contextuels
     */
    async calculateCompensationScore(candidateData, jobData, companyData = {}) {
        const startTime = performance.now();
        
        try {
            // Cache check
            const cacheKey = this.generateCacheKey(candidateData, jobData, companyData);
            const cached = this.calculationCache.get(cacheKey);
            if (cached && this.isCacheValid(cached)) {
                this.updateMetrics(performance.now() - startTime, true);
                return cached.result;
            }

            // Extraction des données salariales
            const salaryData = this.extractSalaryData(candidateData, jobData, companyData);
            
            if (!this.validateSalaryData(salaryData)) {
                return this.getFallbackScore('Données salariales insuffisantes');
            }

            // Calcul du score de chevauchement des fourchettes
            const overlapScore = this.calculateRangeOverlap(salaryData);
            
            // Ajustements contextuels
            const contextualAdjustments = this.calculateContextualAdjustments(salaryData);
            
            // Score de négociation potential
            const negotiationScore = this.calculateNegotiationPotential(salaryData);
            
            // Package global vs salaire fixe
            const packageScore = this.calculatePackageValue(salaryData);
            
            // Score composite final
            const finalScore = this.computeFinalCompensationScore({
                overlap: overlapScore,
                contextual: contextualAdjustments,
                negotiation: negotiationScore,
                package: packageScore
            });

            const result = {
                finalScore: Math.min(finalScore, 1.0),
                components: {
                    range_overlap: overlapScore,
                    contextual_adjustments: contextualAdjustments,
                    negotiation_potential: negotiationScore,
                    package_value: packageScore
                },
                details: {
                    candidate_range: salaryData.candidateRange,
                    job_range: salaryData.jobRange,
                    sector_context: salaryData.sector,
                    location_context: salaryData.location,
                    experience_level: salaryData.experienceLevel,
                    package_elements: salaryData.packageElements
                },
                insights: {
                    overlap_type: this.getOverlapType(salaryData),
                    negotiation_recommendation: this.getNegotiationRecommendation(salaryData),
                    package_advantages: this.getPackageAdvantages(salaryData)
                },
                performance: {
                    calculationTime: performance.now() - startTime,
                    dataQuality: this.assessDataQuality(salaryData),
                    confidence: this.calculateConfidence(salaryData)
                }
            };

            // Mise en cache
            this.calculationCache.set(cacheKey, {
                result: result,
                timestamp: Date.now()
            });

            this.updateMetrics(performance.now() - startTime, false);
            return result;

        } catch (error) {
            console.error('❌ Erreur CompensationMatcher:', error);
            return this.getFallbackScore(`Erreur calcul: ${error.message}`);
        }
    }

    /**
     * EXTRACTION DES DONNÉES SALARIALES
     * Normalisation des données candidat/entreprise
     */
    extractSalaryData(candidateData, jobData, companyData) {
        return {
            // Données candidat
            candidateRange: this.parseSalaryRange(
                candidateData.pretentions_salariales || 
                candidateData.salaire_souhaite ||
                candidateData.salary_expectation
            ),
            currentSalary: this.parseSalary(candidateData.salaire_actuel || candidateData.current_salary),
            
            // Données poste
            jobRange: this.parseSalaryRange(
                jobData.fourchette_salariale || 
                jobData.salary_range ||
                jobData.remuneration
            ),
            
            // Contexte
            sector: this.extractSector(jobData, companyData),
            location: this.extractLocation(jobData, candidateData),
            experienceLevel: this.extractExperienceLevel(candidateData),
            
            // Package global
            packageElements: {
                benefits: this.extractBenefits(jobData, companyData),
                bonuses: this.extractBonuses(jobData, companyData),
                stock_options: this.extractStockOptions(jobData, companyData),
                remote_work: this.extractRemoteWork(jobData, candidateData)
            }
        };
    }

    /**
     * CALCUL CHEVAUCHEMENT DES FOURCHETTES
     * Algorithme intelligent de matching des plages salariales
     */
    calculateRangeOverlap(salaryData) {
        const { candidateRange, jobRange } = salaryData;
        
        if (!candidateRange || !jobRange) {
            return 0.5; // Score neutre si données manquantes
        }

        // Calcul de l'intersection des plages
        const overlapMin = Math.max(candidateRange.min, jobRange.min);
        const overlapMax = Math.min(candidateRange.max, jobRange.max);
        
        if (overlapMax < overlapMin) {
            // Aucun chevauchement - calcul de la distance
            const gap = overlapMin - overlapMax;
            const averageRange = (candidateRange.max - candidateRange.min + jobRange.max - jobRange.min) / 2;
            const gapRatio = gap / averageRange;
            
            // Score dégradé selon l'écart
            if (gapRatio <= 0.1) return 0.7;      // Écart < 10% = acceptable
            if (gapRatio <= 0.2) return 0.5;      // Écart < 20% = moyen
            if (gapRatio <= 0.3) return 0.3;      // Écart < 30% = faible
            return 0.1;                            // Écart > 30% = très faible
        }

        // Chevauchement existant - calcul du ratio
        const overlapSize = overlapMax - overlapMin;
        const candidateRangeSize = candidateRange.max - candidateRange.min;
        const jobRangeSize = jobRange.max - jobRange.min;
        const averageRangeSize = (candidateRangeSize + jobRangeSize) / 2;
        
        const overlapRatio = overlapSize / averageRangeSize;
        
        // Score basé sur la taille du chevauchement
        if (overlapRatio >= 0.8) return 1.0;      // Chevauchement > 80% = parfait
        if (overlapRatio >= 0.6) return 0.9;      // Chevauchement > 60% = excellent
        if (overlapRatio >= 0.4) return 0.8;      // Chevauchement > 40% = très bon
        if (overlapRatio >= 0.2) return 0.7;      // Chevauchement > 20% = bon
        return 0.6;                                // Chevauchement < 20% = acceptable
    }

    /**
     * AJUSTEMENTS CONTEXTUELS
     * Prise en compte secteur, géographie, expérience
     */
    calculateContextualAdjustments(salaryData) {
        let adjustmentScore = 0.5; // Score de base
        
        // Ajustement sectoriel
        const sectorGrid = this.sectorSalaryGrids[salaryData.sector] || this.sectorSalaryGrids.default;
        const experienceGrid = sectorGrid[salaryData.experienceLevel] || sectorGrid.intermediate;
        
        // Vérification cohérence avec grille sectorielle
        if (salaryData.jobRange) {
            const jobMidpoint = (salaryData.jobRange.min + salaryData.jobRange.max) / 2;
            const gridMidpoint = (experienceGrid.min + experienceGrid.max) / 2;
            const sectorAlignment = 1 - Math.abs(jobMidpoint - gridMidpoint) / gridMidpoint;
            adjustmentScore += sectorAlignment * 0.2; // Bonus jusqu'à +20%
        }
        
        // Ajustement géographique
        const locationMultiplier = this.locationAdjustments[salaryData.location] || this.locationAdjustments.default;
        if (locationMultiplier > 1.05) {
            adjustmentScore += 0.1; // Bonus marchés chers
        } else if (locationMultiplier < 0.98) {
            adjustmentScore += 0.05; // Léger bonus marchés moins chers
        }
        
        // Ajustement expérience
        const experienceMultiplier = this.experienceMultipliers[salaryData.experienceLevel] || 1.0;
        if (experienceMultiplier > 1.3) {
            adjustmentScore += 0.15; // Bonus profils seniors
        }
        
        return Math.min(adjustmentScore, 1.0);
    }

    /**
     * POTENTIEL DE NÉGOCIATION
     * Évaluation des marges de manœuvre
     */
    calculateNegotiationPotential(salaryData) {
        if (!salaryData.candidateRange || !salaryData.jobRange) {
            return 0.5;
        }
        
        // Flexibilité côté candidat
        const candidateFlexibility = this.assessCandidateFlexibility(salaryData);
        
        // Marge côté entreprise
        const companyMargin = this.assessCompanyMargin(salaryData);
        
        // Zone de négociation
        const negotiationZone = this.calculateNegotiationZone(salaryData);
        
        // Score composite
        return (candidateFlexibility + companyMargin + negotiationZone) / 3;
    }

    /**
     * VALEUR DU PACKAGE GLOBAL
     * Évaluation avantages, bonus, stock-options
     */
    calculatePackageValue(salaryData) {
        const packageElements = salaryData.packageElements;
        let packageScore = 0.5; // Score de base
        
        // Avantages sociaux
        if (packageElements.benefits && packageElements.benefits.length > 0) {
            packageScore += 0.1 * Math.min(packageElements.benefits.length / 5, 1); // Max +10%
        }
        
        // Bonus et variables
        if (packageElements.bonuses && packageElements.bonuses.amount > 0) {
            const bonusRatio = packageElements.bonuses.amount / 100; // Base 100k€
            packageScore += 0.15 * Math.min(bonusRatio, 1); // Max +15%
        }
        
        // Stock-options / participation
        if (packageElements.stock_options) {
            packageScore += 0.1; // +10% si présence equity
        }
        
        // Télétravail
        if (packageElements.remote_work && packageElements.remote_work.enabled) {
            packageScore += 0.05; // +5% si télétravail
        }
        
        return Math.min(packageScore, 1.0);
    }

    /**
     * SCORE COMPOSITE FINAL
     * Pondération des différents composants
     */
    computeFinalCompensationScore(components) {
        return (
            components.overlap * 0.40 +           // 40% - Chevauchement fourchettes
            components.contextual * 0.25 +        // 25% - Ajustements contextuels
            components.negotiation * 0.20 +       // 20% - Potentiel négociation
            components.package * 0.15             // 15% - Valeur package global
        );
    }

    /**
     * UTILITAIRES DE PARSING
     */
    parseSalaryRange(salaryInput) {
        if (!salaryInput) return null;
        
        if (typeof salaryInput === 'object' && salaryInput.min && salaryInput.max) {
            return { min: salaryInput.min, max: salaryInput.max };
        }
        
        if (typeof salaryInput === 'string') {
            // Formats: "45-55k", "45-55", "45k-55k", "45000-55000"
            const match = salaryInput.match(/(\d+)k?\s*[-–]\s*(\d+)k?/);
            if (match) {
                return { 
                    min: parseInt(match[1]), 
                    max: parseInt(match[2]) 
                };
            }
            
            // Format unique: "50k", "50000"
            const singleMatch = salaryInput.match(/(\d+)k?/);
            if (singleMatch) {
                const value = parseInt(singleMatch[1]);
                return { 
                    min: value * 0.9, 
                    max: value * 1.1 
                }; // ±10% si valeur unique
            }
        }
        
        if (typeof salaryInput === 'number') {
            return { 
                min: salaryInput * 0.9, 
                max: salaryInput * 1.1 
            };
        }
        
        return null;
    }

    parseSalary(salaryInput) {
        if (!salaryInput) return null;
        
        if (typeof salaryInput === 'number') return salaryInput;
        
        if (typeof salaryInput === 'string') {
            const match = salaryInput.match(/(\d+)k?/);
            return match ? parseInt(match[1]) : null;
        }
        
        return null;
    }

    /**
     * MÉTHODES D'EXTRACTION CONTEXTUELLES
     */
    extractSector(jobData, companyData) {
        return jobData.secteur || 
               jobData.sector || 
               companyData.secteur || 
               companyData.sector || 
               'default';
    }

    extractLocation(jobData, candidateData) {
        const jobLocation = jobData.localisation || jobData.location || jobData.ville;
        const candidateLocation = candidateData.localisation || candidateData.location || candidateData.ville;
        
        return this.normalizeLocation(jobLocation || candidateLocation || 'default');
    }

    extractExperienceLevel(candidateData) {
        const experience = candidateData.experience_years || candidateData.annees_experience;
        
        if (!experience) return 'intermediate';
        
        if (experience <= 1) return 'junior';
        if (experience <= 3) return 'intermediate';
        if (experience <= 8) return 'senior';
        return 'expert';
    }

    normalizeLocation(location) {
        if (!location) return 'default';
        
        const normalized = location.toLowerCase().replace(/[^a-z]/g, '');
        
        if (normalized.includes('paris')) return 'paris';
        if (normalized.includes('lyon')) return 'lyon';
        if (normalized.includes('marseille')) return 'marseille';
        if (normalized.includes('toulouse')) return 'toulouse';
        if (normalized.includes('bordeaux')) return 'bordeaux';
        if (normalized.includes('lille')) return 'lille';
        if (normalized.includes('nantes')) return 'nantes';
        
        return 'default';
    }

    /**
     * MÉTHODES UTILITAIRES
     */
    generateCacheKey(candidateData, jobData, companyData) {
        const key = JSON.stringify({
            candidate_salary: candidateData.pretentions_salariales,
            job_salary: jobData.fourchette_salariale,
            sector: jobData.secteur,
            location: jobData.localisation
        });
        return btoa(key).substring(0, 20);
    }

    isCacheValid(cached) {
        return (Date.now() - cached.timestamp) < 300000; // 5 minutes
    }

    validateSalaryData(salaryData) {
        return salaryData.candidateRange || salaryData.jobRange || salaryData.currentSalary;
    }

    getFallbackScore(reason) {
        return {
            finalScore: 0.5,
            error: reason,
            fallback: true,
            timestamp: new Date().toISOString()
        };
    }

    updateMetrics(calculationTime, wasCacheHit) {
        this.metrics.totalCalculations++;
        this.metrics.averageCalculationTime = 
            (this.metrics.averageCalculationTime * (this.metrics.totalCalculations - 1) + calculationTime) 
            / this.metrics.totalCalculations;
            
        if (wasCacheHit) {
            this.metrics.cacheHitRate = 
                (this.metrics.cacheHitRate * (this.metrics.totalCalculations - 1) + 1) 
                / this.metrics.totalCalculations;
        }
    }

    // Méthodes placeholder pour développement futur
    assessCandidateFlexibility(salaryData) { return 0.7; }
    assessCompanyMargin(salaryData) { return 0.6; }
    calculateNegotiationZone(salaryData) { return 0.8; }
    extractBenefits(jobData, companyData) { return []; }
    extractBonuses(jobData, companyData) { return { amount: 0 }; }
    extractStockOptions(jobData, companyData) { return false; }
    extractRemoteWork(jobData, candidateData) { return { enabled: false }; }
    getOverlapType(salaryData) { return 'standard'; }
    getNegotiationRecommendation(salaryData) { return 'proceed'; }
    getPackageAdvantages(salaryData) { return []; }
    assessDataQuality(salaryData) { return 0.8; }
    calculateConfidence(salaryData) { return 0.85; }
}

// Export pour intégration
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CompensationMatcher;
}

if (typeof window !== 'undefined') {
    window.CompensationMatcher = CompensationMatcher;
    console.log('💰 CompensationMatcher disponible - Critère #3 (15%)');
}