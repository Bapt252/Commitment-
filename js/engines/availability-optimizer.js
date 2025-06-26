/**
 * NEXTEN AVAILABILITY OPTIMIZER - CRITÈRE #5 (10% DU SCORE TOTAL)
 * Système d'optimisation disponibilité et contraintes temporelles
 * Matching calendrier candidat/entreprise avec gestion télétravail
 */

class AvailabilityOptimizer {
    constructor() {
        this.cache = new Map();
        
        this.performanceMetrics = {
            totalCalculations: 0,
            cacheHits: 0,
            averageTime: 0,
            schedulingAccuracy: 0
        };

        this.config = {
            // Pondération des critères temporels
            scoring: {
                startDateCompatibilityWeight: 0.35,    // 35% - Date de début
                scheduleFlexibilityWeight: 0.25,       // 25% - Flexibilité horaires
                remoteWorkCompatibilityWeight: 0.20,   // 20% - Télétravail
                travelAvailabilityWeight: 0.15,        // 15% - Disponibilité déplacements
                overtimeToleranceWeight: 0.05          // 5% - Tolérance heures supplémentaires
            },
            
            // Gestion cache
            cache: {
                duration: 3 * 24 * 60 * 60 * 1000, // 3 jours (données temporelles volatiles)
                maxSize: 2000
            },
            
            // Paramètres temporels
            timing: {
                urgentStartDays: 14,      // < 14 jours = urgent
                normalStartDays: 30,      // 14-30 jours = normal
                flexibleStartDays: 90,    // > 30 jours = flexible
                maxAcceptableDelayDays: 60 // Délai max acceptable
            }
        };

        this.initializeWorkPatterns();
        this.initializeRemoteWorkPolicies();
        this.initializeTravelRequirements();
    }

    /**
     * PATTERNS DE TRAVAIL
     * Templates horaires et flexibilité
     */
    initializeWorkPatterns() {
        this.workPatterns = {
            // Horaires standards
            traditional: {
                schedule: '09:00-18:00',
                flexibilityScore: 0.3,
                coreHours: ['10:00-16:00'],
                description: 'Horaires fixes traditionnels'
            },
            
            flexible: {
                schedule: '08:00-20:00',
                flexibilityScore: 0.8,
                coreHours: ['10:00-15:00'],
                description: 'Horaires flexibles avec plages libres'
            },
            
            hybrid: {
                schedule: '09:00-17:30',
                flexibilityScore: 0.6,
                coreHours: ['10:00-16:00'],
                description: 'Mélange horaires fixes et flexibles'
            },
            
            compressed: {
                schedule: '08:00-18:00',
                flexibilityScore: 0.4,
                daysPerWeek: 4,
                description: 'Semaine de 4 jours, journées longues'
            },
            
            // Secteurs spécifiques
            retail: {
                schedule: '10:00-19:00',
                flexibilityScore: 0.2,
                weekendWork: true,
                description: 'Horaires commerce avec week-ends'
            },
            
            startup: {
                schedule: '10:00-19:00',
                flexibilityScore: 0.9,
                overtimeFrequency: 'high',
                description: 'Flexibilité élevée avec possibles heures sup'
            }
        };
    }

    /**
     * POLITIQUES TÉLÉTRAVAIL
     * Configurations hybrides par secteur
     */
    initializeRemoteWorkPolicies() {
        this.remoteWorkPolicies = {
            // Modes de télétravail
            full_remote: {
                onSiteDays: 0,
                flexibilityScore: 1.0,
                requirement: 'Autonomie complète requise'
            },
            
            hybrid_4_1: {
                onSiteDays: 1,
                remoteWeekDays: 4,
                flexibilityScore: 0.9,
                requirement: 'Présence minimale 1 jour/semaine'
            },
            
            hybrid_3_2: {
                onSiteDays: 2,
                remoteWeekDays: 3,
                flexibilityScore: 0.7,
                requirement: 'Équilibre bureau/domicile'
            },
            
            hybrid_2_3: {
                onSiteDays: 3,
                remoteWeekDays: 2,
                flexibilityScore: 0.5,
                requirement: 'Présence majoritaire au bureau'
            },
            
            on_site_only: {
                onSiteDays: 5,
                remoteWeekDays: 0,
                flexibilityScore: 0.1,
                requirement: 'Présence physique obligatoire'
            },
            
            // Secteurs spécifiques
            luxe_retail: {
                onSiteDays: 4,
                remoteWeekDays: 1,
                flexibilityScore: 0.3,
                requirement: 'Présence client essentielle'
            },
            
            tech_startup: {
                onSiteDays: 1,
                remoteWeekDays: 4,
                flexibilityScore: 0.95,
                requirement: 'Collaboration ponctuelle en présentiel'
            }
        };
    }

    /**
     * EXIGENCES DÉPLACEMENTS
     * Fréquence et types de voyages professionnels
     */
    initializeTravelRequirements() {
        this.travelRequirements = {
            none: {
                frequency: 0,
                score: 1.0,
                description: 'Aucun déplacement requis'
            },
            
            occasional: {
                frequency: 2, // jours/mois
                score: 0.9,
                description: 'Déplacements occasionnels (2j/mois)'
            },
            
            regular: {
                frequency: 5, // jours/mois
                score: 0.7,
                description: 'Déplacements réguliers (1j/semaine)'
            },
            
            frequent: {
                frequency: 10, // jours/mois
                score: 0.4,
                description: 'Déplacements fréquents (50% du temps)'
            },
            
            intensive: {
                frequency: 15, // jours/mois
                score: 0.2,
                description: 'Déplacements intensifs (75% du temps)'
            }
        };
    }

    /**
     * MOTEUR PRINCIPAL OPTIMISATION DISPONIBILITÉ
     * Scoring multi-critères avec intelligence temporelle
     */
    async calculateAvailabilityScore(candidateData, jobData, companyData) {
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

            // Extraction contraintes candidat
            const candidateConstraints = this.extractCandidateConstraints(candidateData);
            
            // Extraction exigences poste
            const jobRequirements = this.extractJobRequirements(jobData, companyData);
            
            // Calculs des sous-scores
            const startDateScore = await this.calculateStartDateCompatibility(
                candidateConstraints.availability, jobRequirements.startDate
            );
            
            const scheduleScore = await this.calculateScheduleFlexibility(
                candidateConstraints.schedule, jobRequirements.workPattern
            );
            
            const remoteWorkScore = await this.calculateRemoteWorkCompatibility(
                candidateConstraints.remotePreferences, jobRequirements.remotePolicy
            );
            
            const travelScore = await this.calculateTravelAvailability(
                candidateConstraints.travelWillingness, jobRequirements.travelRequirements
            );
            
            const overtimeScore = await this.calculateOvertimeTolerance(
                candidateConstraints.overtimeAcceptance, jobRequirements.overtimeExpectation
            );

            // Score composite final
            const finalScore = (
                startDateScore * this.config.scoring.startDateCompatibilityWeight +
                scheduleScore * this.config.scoring.scheduleFlexibilityWeight +
                remoteWorkScore * this.config.scoring.remoteWorkCompatibilityWeight +
                travelScore * this.config.scoring.travelAvailabilityWeight +
                overtimeScore * this.config.scoring.overtimeToleranceWeight
            );

            const result = {
                finalScore: Math.min(finalScore, 1.0),
                breakdown: {
                    startDateCompatibility: { score: startDateScore, weight: this.config.scoring.startDateCompatibilityWeight },
                    scheduleFlexibility: { score: scheduleScore, weight: this.config.scoring.scheduleFlexibilityWeight },
                    remoteWorkCompatibility: { score: remoteWorkScore, weight: this.config.scoring.remoteWorkCompatibilityWeight },
                    travelAvailability: { score: travelScore, weight: this.config.scoring.travelAvailabilityWeight },
                    overtimeTolerance: { score: overtimeScore, weight: this.config.scoring.overtimeToleranceWeight }
                },
                scheduling: {
                    candidateConstraints: candidateConstraints,
                    jobRequirements: jobRequirements,
                    recommendations: this.generateSchedulingRecommendations(candidateConstraints, jobRequirements, finalScore),
                    nextSteps: this.generateNextSteps(candidateConstraints, jobRequirements)
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
            console.error('Erreur calcul availability score:', error);
            return this.getFallbackScore();
        }
    }

    /**
     * EXTRACTION CONTRAINTES CANDIDAT
     * Parsing disponibilités et préférences temporelles
     */
    extractCandidateConstraints(candidateData) {
        return {
            availability: this.parseAvailability(candidateData.disponibilite || candidateData.date_disponibilite),
            schedule: this.parseSchedulePreferences(candidateData.horaires_preferes || ''),
            remotePreferences: this.parseRemotePreferences(candidateData.teletravail || candidateData.remote_work || ''),
            travelWillingness: this.parseTravelWillingness(candidateData.mobilite || candidateData.deplacement || ''),
            overtimeAcceptance: this.parseOvertimeAcceptance(candidateData.heures_sup || ''),
            currentCommitments: this.parseCurrentCommitments(candidateData.situation || ''),
            noticePeriod: this.parseNoticePeriod(candidateData.preavis || candidateData.disponibilite || '')
        };
    }

    /**
     * EXTRACTION EXIGENCES POSTE
     * Parsing contraintes temporelles entreprise
     */
    extractJobRequirements(jobData, companyData) {
        return {
            startDate: this.parseStartDate(jobData.date_prise_poste || jobData.urgence || ''),
            workPattern: this.identifyWorkPattern(jobData.horaires || companyData.horaires || ''),
            remotePolicy: this.identifyRemotePolicy(jobData.teletravail || companyData.remote_policy || ''),
            travelRequirements: this.identifyTravelRequirements(jobData.deplacement || ''),
            overtimeExpectation: this.parseOvertimeExpectation(jobData.description || ''),
            flexibility: this.assessFlexibilityFromDescription(jobData.description || ''),
            urgency: this.assessUrgency(jobData.urgence || jobData.priorite || '')
        };
    }

    /**
     * SCORING COMPATIBILITÉ DATE DÉBUT
     * Adéquation timing candidat vs besoin entreprise
     */
    async calculateStartDateCompatibility(candidateAvailability, jobStartDate) {
        const today = new Date();
        const candidateStartDate = this.parseDate(candidateAvailability);
        const requiredStartDate = this.parseDate(jobStartDate);
        
        if (!candidateStartDate || !requiredStartDate) {
            return 0.7; // Score neutre si dates imprécises
        }
        
        const candidateDelayDays = Math.ceil((candidateStartDate - today) / (1000 * 60 * 60 * 24));
        const requiredDelayDays = Math.ceil((requiredStartDate - today) / (1000 * 60 * 60 * 24));
        
        const difference = candidateDelayDays - requiredDelayDays;
        
        // Score basé sur l'écart
        if (difference <= 0) {
            // Candidat disponible avant/à la date requise = excellent
            return 1.0;
        } else if (difference <= 14) {
            // Retard acceptable (< 2 semaines)
            return 0.8 - (difference / 14) * 0.3;
        } else if (difference <= this.config.timing.maxAcceptableDelayDays) {
            // Retard significatif mais acceptable
            return 0.5 - (difference / 60) * 0.3;
        } else {
            // Retard inacceptable
            return 0.2;
        }
    }

    /**
     * SCORING FLEXIBILITÉ HORAIRES
     * Correspondance patterns de travail
     */
    async calculateScheduleFlexibility(candidateSchedule, jobWorkPattern) {
        const candidatePattern = this.identifyWorkPattern(candidateSchedule);
        const jobPattern = this.workPatterns[jobWorkPattern] || this.workPatterns.traditional;
        
        // Matrice de compatibilité horaires
        const compatibilityMatrix = {
            'traditional-traditional': 1.0,
            'traditional-flexible': 0.8,
            'flexible-flexible': 1.0,
            'flexible-traditional': 0.9, // Flexible s'adapte au rigide
            'hybrid-hybrid': 1.0,
            'startup-startup': 1.0,
            'retail-retail': 1.0,
            'compressed-compressed': 1.0,
            // Cross-patterns
            'flexible-startup': 0.95,
            'traditional-retail': 0.6,
            'hybrid-traditional': 0.8
        };
        
        const key = `${candidatePattern}-${jobWorkPattern}`;
        return compatibilityMatrix[key] || 0.7;
    }

    /**
     * SCORING COMPATIBILITÉ TÉLÉTRAVAIL
     * Adéquation préférences remote vs politique entreprise
     */
    async calculateRemoteWorkCompatibility(candidateRemotePrefs, jobRemotePolicy) {
        const candidateScore = this.getRemotePreferenceScore(candidateRemotePrefs);
        const jobPolicy = this.remoteWorkPolicies[jobRemotePolicy] || this.remoteWorkPolicies.hybrid_3_2;
        
        // Écart entre préférence candidat et offre entreprise
        const difference = Math.abs(candidateScore - jobPolicy.flexibilityScore);
        
        // Score inversement proportionnel à l'écart
        return Math.max(0.3, 1.0 - difference);
    }

    /**
     * SCORING DISPONIBILITÉ DÉPLACEMENTS
     * Willingness vs requirements
     */
    async calculateTravelAvailability(candidateTravelWillingness, jobTravelRequirements) {
        const candidateWillingness = this.getTravelWillingnessScore(candidateTravelWillingness);
        const jobRequirement = this.travelRequirements[jobTravelRequirements] || this.travelRequirements.occasional;
        
        if (candidateWillingness >= jobRequirement.score) {
            // Candidat accepte les déplacements requis
            return 1.0;
        } else {
            // Réticence aux déplacements
            return candidateWillingness / jobRequirement.score;
        }
    }

    /**
     * SCORING TOLÉRANCE HEURES SUP
     * Acceptation vs attentes
     */
    async calculateOvertimeTolerance(candidateOvertimeAcceptance, jobOvertimeExpectation) {
        const candidateAcceptance = this.getOvertimeAcceptanceScore(candidateOvertimeAcceptance);
        const jobExpectation = this.getOvertimeExpectationScore(jobOvertimeExpectation);
        
        if (candidateAcceptance >= jobExpectation) {
            return 1.0;
        } else {
            // Pénalité proportionnelle à l'écart
            return Math.max(0.4, candidateAcceptance / jobExpectation);
        }
    }

    /**
     * UTILITAIRES PARSING
     */
    parseAvailability(availabilityText) {
        if (!availabilityText) return 'immediate';
        
        const text = availabilityText.toLowerCase();
        
        if (text.includes('immédiat') || text.includes('immediate') || text.includes('asap')) {
            return 'immediate';
        }
        if (text.includes('1 mois') || text.includes('month')) {
            return '1_month';
        }
        if (text.includes('2 mois') || text.includes('two_month')) {
            return '2_months';
        }
        if (text.includes('3 mois') || text.includes('three_month')) {
            return '3_months';
        }
        
        // Tentative d'extraction de date
        const dateMatch = text.match(/(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})/);
        if (dateMatch) {
            return `${dateMatch[3]}-${dateMatch[2].padStart(2, '0')}-${dateMatch[1].padStart(2, '0')}`;
        }
        
        return 'flexible';
    }

    parseDate(dateString) {
        if (!dateString) return null;
        
        // Format ISO
        if (dateString.match(/^\d{4}-\d{2}-\d{2}$/)) {
            return new Date(dateString);
        }
        
        // Formats relatifs
        const today = new Date();
        switch (dateString) {
            case 'immediate':
                return today;
            case '1_month':
                return new Date(today.getTime() + 30 * 24 * 60 * 60 * 1000);
            case '2_months':
                return new Date(today.getTime() + 60 * 24 * 60 * 60 * 1000);
            case '3_months':
                return new Date(today.getTime() + 90 * 24 * 60 * 60 * 1000);
            default:
                return today;
        }
    }

    identifyWorkPattern(scheduleDescription) {
        if (!scheduleDescription) return 'traditional';
        
        const text = scheduleDescription.toLowerCase();
        
        if (text.includes('flexible') || text.includes('modulable')) return 'flexible';
        if (text.includes('startup') || text.includes('scale-up')) return 'startup';
        if (text.includes('retail') || text.includes('magasin') || text.includes('weekend')) return 'retail';
        if (text.includes('4 jours') || text.includes('4j')) return 'compressed';
        if (text.includes('hybride') || text.includes('mixte')) return 'hybrid';
        
        return 'traditional';
    }

    /**
     * GÉNÉRATION RECOMMANDATIONS SCHEDULING
     */
    generateSchedulingRecommendations(candidateConstraints, jobRequirements, score) {
        const recommendations = [];
        
        if (score < 0.6) {
            recommendations.push({
                priority: 'high',
                type: 'timing_conflict',
                message: 'Conflits temporels significatifs à résoudre'
            });
        }
        
        if (candidateConstraints.noticePeriod > 30) {
            recommendations.push({
                priority: 'medium',
                type: 'notice_period',
                message: `Préavis de ${candidateConstraints.noticePeriod} jours à négocier`
            });
        }
        
        return recommendations;
    }

    generateNextSteps(candidateConstraints, jobRequirements) {
        const steps = [];
        
        steps.push({
            step: 1,
            action: 'Confirmer date de début réaliste',
            responsible: 'RH'
        });
        
        if (jobRequirements.remotePolicy !== 'on_site_only') {
            steps.push({
                step: 2,
                action: 'Négocier modalités télétravail',
                responsible: 'Manager'
            });
        }
        
        if (jobRequirements.travelRequirements !== 'none') {
            steps.push({
                step: 3,
                action: 'Clarifier fréquence et destinations déplacements',
                responsible: 'RH'
            });
        }
        
        return steps;
    }

    /**
     * UTILITAIRES SCORING
     */
    getRemotePreferenceScore(remotePrefs) {
        if (!remotePrefs) return 0.5;
        
        const text = remotePrefs.toLowerCase();
        
        if (text.includes('full') || text.includes('100%') || text.includes('complet')) return 1.0;
        if (text.includes('4j') || text.includes('majoritaire')) return 0.8;
        if (text.includes('hybride') || text.includes('mix')) return 0.6;
        if (text.includes('occasionnel') || text.includes('ponctuel')) return 0.4;
        if (text.includes('bureau') || text.includes('présentiel')) return 0.2;
        
        return 0.5;
    }

    getTravelWillingnessScore(travelWillingness) {
        if (!travelWillingness) return 0.5;
        
        const text = travelWillingness.toLowerCase();
        
        if (text.includes('aucun') || text.includes('pas')) return 0.1;
        if (text.includes('occasionnel') || text.includes('rare')) return 0.6;
        if (text.includes('régulier') || text.includes('hebdo')) return 0.8;
        if (text.includes('fréquent') || text.includes('souvent')) return 0.9;
        if (text.includes('international') || text.includes('monde')) return 1.0;
        
        return 0.5;
    }

    /**
     * CACHE ET PERFORMANCE
     */
    generateCacheKey(candidateData, jobData, companyData) {
        const candidateId = candidateData.id || 'candidate';
        const jobId = jobData.id || 'job';
        const companyId = companyData.id || 'company';
        return `availability_${candidateId}_${jobId}_${companyId}`;
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
            error: 'Contraintes temporelles insuffisantes',
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
    module.exports = AvailabilityOptimizer;
}

if (typeof window !== 'undefined') {
    window.AvailabilityOptimizer = AvailabilityOptimizer;
}
