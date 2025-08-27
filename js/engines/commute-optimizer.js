/**
 * NEXTEN COMMUTE OPTIMIZER - CRITÈRE #2 (20% DU SCORE TOTAL)
 * Système de calcul temps de trajet intelligent avec cache multiniveau
 * Intégration Google Maps Distance Matrix API optimisée
 */

class CommuteOptimizer {
    constructor() {
        this.cache = {
            level1: new Map(), // Cache exact 24h (adresse A → adresse B)
            level2: new Map(), // Patterns géographiques récurrents (zones populaires)
            level3: new Map()  // Approximations intelligentes (rayon 500m)
        };
        
        this.performanceMetrics = {
            totalCalculations: 0,
            cacheHits: { level1: 0, level2: 0, level3: 0 },
            apiCalls: 0,
            averageTime: 0,
            costTracking: 0 // Suivi coûts API Google
        };

        this.config = {
            // Configuration API Google Maps
            api: {
                maxLocationsPerBatch: 25, // Limite API Distance Matrix
                maxApiCallsPerMinute: 100,
                baseUrl: 'https://maps.googleapis.com/maps/api/distancematrix/json'
            },
            // Scoring des trajets
            scoring: {
                durationWeight: 0.40,      // 40% - Durée trajet
                transportEaseWeight: 0.30, // 30% - Facilité transport
                costWeight: 0.20,          // 20% - Coût transport
                preferencesWeight: 0.10    // 10% - Préférences candidat
            },
            // Pondération durée
            duration: {
                excellent: 30,    // < 30min = score maximal (1.0)
                good: 45,         // 30-45min = score élevé (0.8-0.9)
                acceptable: 60,   // 45-60min = score acceptable (0.6-0.7)
                poor: 90          // > 90min = score minimal (0.1)
            },
            // Cache management
            cache: {
                level1Duration: 24 * 60 * 60 * 1000, // 24h en ms
                level2Duration: 7 * 24 * 60 * 60 * 1000, // 7 jours
                approximationRadius: 500, // 500m pour level3
                maxSize: 10000
            }
        };

        this.initializeTransportModes();
        this.initializeGeographicalZones();
    }

    /**
     * INITIALISATION DES MODES DE TRANSPORT
     * Bonification selon préférences candidat
     */
    initializeTransportModes() {
        this.transportModes = {
            driving: {
                name: 'Voiture',
                bonus: 1.15,
                keywords: ['voiture', 'vehicule', 'conduite', 'parking']
            },
            transit: {
                name: 'Transport Public',
                bonus: 1.25,
                keywords: ['metro', 'bus', 'tramway', 'transport_public', 'rer', 'transilien']
            },
            walking: {
                name: 'À pied',
                bonus: 1.05,
                keywords: ['marche', 'pied', 'walking']
            },
            bicycling: {
                name: 'Vélo',
                bonus: 1.10,
                keywords: ['velo', 'bicyclette', 'cyclisme', 'bike']
            }
        };
    }

    /**
     * ZONES GÉOGRAPHIQUES POPULAIRES PARIS
     * Pour optimisation cache niveau 2
     */
    initializeGeographicalZones() {
        this.popularZones = {
            'defense': {
                center: { lat: 48.8908, lng: 2.2383 },
                radius: 1000,
                transport: ['rer_a', 'metro_1', 'tramway_t2'],
                businessDistrict: true
            },
            'republique': {
                center: { lat: 48.8673, lng: 2.3629 },
                radius: 800,
                transport: ['metro_3', 'metro_5', 'metro_8', 'metro_9', 'metro_11'],
                businessDistrict: false
            },
            'chatelet': {
                center: { lat: 48.8566, lng: 2.3477 },
                radius: 500,
                transport: ['metro_1', 'metro_4', 'metro_7', 'metro_11', 'metro_14', 'rer_a', 'rer_b'],
                businessDistrict: true
            },
            'saint_denis': {
                center: { lat: 48.9362, lng: 2.3574 },
                radius: 1200,
                transport: ['rer_b', 'rer_d', 'metro_13'],
                businessDistrict: false
            }
        };
    }

    /**
     * MOTEUR PRINCIPAL DE CALCUL TRAJET
     * Scoring composite avec cache intelligent
     */
    async calculateCommuteScore(candidateData, jobData) {
        const startTime = performance.now();
        
        try {
            // Extraction des données géographiques
            const candidateLocation = this.extractCandidateLocation(candidateData);
            const jobLocation = this.extractJobLocation(jobData);
            
            if (!candidateLocation || !jobLocation) {
                throw new Error('Données de géolocalisation manquantes');
            }

            // Tentative de récupération depuis le cache
            const cacheResult = await this.tryGetFromCache(candidateLocation, jobLocation);
            if (cacheResult) {
                this.updatePerformanceMetrics(performance.now() - startTime, true);
                return cacheResult;
            }

            // Calcul avec API Google Maps
            const commuteData = await this.calculateCommuteWithAPI(candidateLocation, jobLocation);
            
            // Scoring composite
            const score = await this.calculateCompositeCommuteScore(
                commuteData, 
                candidateData.preferences_transport || [],
                candidateData.mobilite_acceptee || ''
            );

            // Mise en cache
            await this.storeInCache(candidateLocation, jobLocation, score);

            // Métriques de performance
            this.updatePerformanceMetrics(performance.now() - startTime, false);

            return score;

        } catch (error) {
            console.error('Erreur calcul commute score:', error);
            return this.getFallbackScore(candidateData, jobData);
        }
    }

    /**
     * EXTRACTION LOCALISATION CANDIDAT
     * Depuis CV Parser v6.2.0 avec géolocalisation
     */
    extractCandidateLocation(candidateData) {
        return {
            address: candidateData.adresse,
            coordinates: candidateData.coordonnees,
            preferences: candidateData.preferences_transport || [],
            mobility: candidateData.mobilite || candidateData.mobilite_acceptee || 'paris_banlieue',
            maxCommuteDuration: candidateData.duree_trajet_max || '60min'
        };
    }

    /**
     * EXTRACTION LOCALISATION ENTREPRISE
     * Depuis Job Parser GPT avec Google Maps
     */
    extractJobLocation(jobData) {
        return {
            address: jobData.adresse,
            coordinates: jobData.coordonnees,
            accessibility: jobData.accessibilite || [],
            district: jobData.quartier || '',
            businessArea: this.isBusinessDistrict(jobData.coordonnees)
        };
    }

    /**
     * TENTATIVE RÉCUPÉRATION CACHE MULTINIVEAU
     * Level 1 → Level 2 → Level 3 → API
     */
    async tryGetFromCache(candidateLocation, jobLocation) {
        // Cache Level 1: Exact match
        const exactKey = this.generateCacheKey(candidateLocation, jobLocation, 'exact');
        if (this.cache.level1.has(exactKey)) {
            const cached = this.cache.level1.get(exactKey);
            if (this.isCacheValid(cached, this.config.cache.level1Duration)) {
                this.performanceMetrics.cacheHits.level1++;
                return { ...cached.data, performance: { cacheHit: true, level: 1 } };
            }
        }

        // Cache Level 2: Zone patterns
        const zoneKey = this.generateZoneKey(candidateLocation, jobLocation);
        if (this.cache.level2.has(zoneKey)) {
            const cached = this.cache.level2.get(zoneKey);
            if (this.isCacheValid(cached, this.config.cache.level2Duration)) {
                this.performanceMetrics.cacheHits.level2++;
                return { ...cached.data, performance: { cacheHit: true, level: 2 } };
            }
        }

        // Cache Level 3: Approximation géographique
        const approxKey = this.findApproximateMatch(candidateLocation, jobLocation);
        if (approxKey && this.cache.level3.has(approxKey)) {
            const cached = this.cache.level3.get(approxKey);
            this.performanceMetrics.cacheHits.level3++;
            return { ...cached.data, performance: { cacheHit: true, level: 3 } };
        }

        return null;
    }

    /**
     * CALCUL AVEC API GOOGLE MAPS
     * Distance Matrix optimisée avec gestion des heures
     */
    async calculateCommuteWithAPI(candidateLocation, jobLocation) {
        this.performanceMetrics.apiCalls++;
        
        // Simulation heures de pointe
        const peakHours = ['08:00', '09:00', '18:00', '19:00'];
        const offPeakHours = ['14:00', '16:00'];
        
        const results = {};
        
        // Calcul pour différents modes de transport
        for (const [mode, config] of Object.entries(this.transportModes)) {
            try {
                // Simulation appel API Google Maps Distance Matrix
                const apiResult = await this.callGoogleMapsAPI(
                    candidateLocation.coordinates,
                    jobLocation.coordinates,
                    mode,
                    peakHours[0] // Heure de pointe principale
                );
                
                results[mode] = apiResult;
                
                // Coût tracking (0.005€ par élément pour Distance Matrix API)
                this.performanceMetrics.costTracking += 0.005;
                
            } catch (error) {
                console.warn(`Erreur API pour mode ${mode}:`, error);
                results[mode] = this.getEstimatedCommute(candidateLocation, jobLocation, mode);
            }
        }

        return results;
    }

    /**
     * SIMULATION APPEL API GOOGLE MAPS
     * Remplacement par vraie API en production
     */
    async callGoogleMapsAPI(origin, destination, mode, departureTime) {
        // SIMULATION - En production, utiliser la vraie API
        const distance = this.calculateEuclideanDistance(origin, destination);
        
        // Facteurs de correction par mode
        const modeFactors = {
            driving: { time: 1.2, reliability: 0.9 },
            transit: { time: 1.8, reliability: 0.7 },
            walking: { time: 12, reliability: 1.0 },
            bicycling: { time: 4, reliability: 0.85 }
        };
        
        const factor = modeFactors[mode] || modeFactors.driving;
        const estimatedTime = Math.round(distance * factor.time); // minutes
        
        return {
            distance: `${distance.toFixed(1)} km`,
            duration: `${estimatedTime} min`,
            duration_value: estimatedTime * 60, // secondes
            status: 'OK',
            mode: mode,
            reliability: factor.reliability,
            traffic_factor: mode === 'driving' ? this.getTrafficFactor(departureTime) : 1.0
        };
    }

    /**
     * SCORING COMPOSITE INTELLIGENT
     * Pondération selon préférences et contexte
     */
    async calculateCompositeCommuteScore(commuteData, transportPreferences, mobility) {
        const scores = {};
        let bestScore = 0;
        let bestMode = '';
        
        for (const [mode, data] of Object.entries(commuteData)) {
            if (data.status !== 'OK') continue;
            
            const durationMinutes = data.duration_value / 60;
            
            // Score basé sur la durée
            const durationScore = this.calculateDurationScore(durationMinutes);
            
            // Score facilité transport
            const easeScore = this.calculateTransportEaseScore(mode, data);
            
            // Score coût
            const costScore = this.calculateCostScore(mode, durationMinutes);
            
            // Bonus préférences candidat
            const preferencesBonus = this.calculatePreferencesBonus(mode, transportPreferences);
            
            // Score composite pour ce mode
            const modeScore = (
                durationScore * this.config.scoring.durationWeight +
                easeScore * this.config.scoring.transportEaseWeight +
                costScore * this.config.scoring.costWeight +
                preferencesBonus * this.config.scoring.preferencesWeight
            ) * this.transportModes[mode].bonus;
            
            scores[mode] = {
                score: modeScore,
                duration: durationMinutes,
                ease: easeScore,
                cost: costScore,
                preferences: preferencesBonus,
                reliability: data.reliability
            };
            
            if (modeScore > bestScore) {
                bestScore = modeScore;
                bestMode = mode;
            }
        }
        
        return {
            finalScore: Math.min(bestScore, 1.0),
            bestMode: bestMode,
            breakdown: scores,
            details: {
                allModes: commuteData,
                recommendation: this.generateRecommendation(scores, bestMode),
                alternatives: this.findAlternatives(scores)
            }
        };
    }

    /**
     * SCORING DURÉE DE TRAJET
     * Fonction décroissante optimisée
     */
    calculateDurationScore(durationMinutes) {
        const { excellent, good, acceptable, poor } = this.config.duration;
        
        if (durationMinutes <= excellent) return 1.0;
        if (durationMinutes <= good) return 0.8 + (excellent - durationMinutes) / (excellent - good) * 0.2;
        if (durationMinutes <= acceptable) return 0.6 + (good - durationMinutes) / (good - acceptable) * 0.2;
        if (durationMinutes <= poor) return 0.2 + (acceptable - durationMinutes) / (acceptable - poor) * 0.4;
        
        return Math.max(0.1, 0.2 - (durationMinutes - poor) / 60 * 0.1);
    }

    /**
     * SCORING FACILITÉ TRANSPORT
     * Basé sur la fiabilité et accessibilité
     */
    calculateTransportEaseScore(mode, data) {
        const baseReliability = data.reliability || 0.8;
        
        // Bonus selon le mode
        const modeBonus = {
            transit: 0.9,  // Transport public = facilité élevée
            driving: 0.85, // Voiture = besoin parking
            walking: 0.7,  // Marche = effort physique
            bicycling: 0.75 // Vélo = dépendant météo
        };
        
        return baseReliability * (modeBonus[mode] || 0.8);
    }

    /**
     * SCORING COÛT TRANSPORT
     * Estimation coûts selon mode et distance
     */
    calculateCostScore(mode, durationMinutes) {
        // Coûts estimés par mode (€/trajet)
        const baseCosts = {
            transit: 1.90,  // Ticket métro/bus
            driving: durationMinutes * 0.15, // Essence + usure
            walking: 0,     // Gratuit
            bicycling: 0.10 // Usure vélo
        };
        
        const cost = baseCosts[mode] || 2.0;
        
        // Score inversement proportionnel au coût
        // 0€ = 1.0, 5€ = 0.5, 10€+ = 0.1
        return Math.max(0.1, 1.0 - (cost / 10));
    }

    /**
     * BONUS PRÉFÉRENCES CANDIDAT
     * Correspondance avec préférences déclarées
     */
    calculatePreferencesBonus(mode, transportPreferences) {
        if (!transportPreferences || transportPreferences.length === 0) {
            return 0.5; // Neutre si pas de préférences
        }
        
        const modeKeywords = this.transportModes[mode].keywords;
        const hasPreference = transportPreferences.some(pref => 
            modeKeywords.some(keyword => 
                pref.toLowerCase().includes(keyword)
            )
        );
        
        return hasPreference ? 1.0 : 0.3;
    }

    /**
     * GESTION CACHE INTELLIGENT
     */
    async storeInCache(candidateLocation, jobLocation, result) {
        // Cache Level 1: Exact
        const exactKey = this.generateCacheKey(candidateLocation, jobLocation, 'exact');
        this.cache.level1.set(exactKey, {
            data: result,
            timestamp: Date.now()
        });

        // Cache Level 2: Zone patterns
        const zoneKey = this.generateZoneKey(candidateLocation, jobLocation);
        this.cache.level2.set(zoneKey, {
            data: result,
            timestamp: Date.now()
        });

        // Nettoyage cache si trop grand
        this.cleanupCache();
    }

    /**
     * UTILITAIRES GÉOGRAPHIQUES
     */
    calculateEuclideanDistance(point1, point2) {
        const R = 6371; // Rayon terre en km
        const dLat = this.deg2rad(point2.lat - point1.lat);
        const dLng = this.deg2rad(point2.lng - point1.lng);
        
        const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                  Math.cos(this.deg2rad(point1.lat)) * Math.cos(this.deg2rad(point2.lat)) *
                  Math.sin(dLng/2) * Math.sin(dLng/2);
        
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
        return R * c;
    }

    deg2rad(deg) {
        return deg * (Math.PI / 180);
    }

    /**
     * GÉNÉRATION DE CLÉS CACHE
     */
    generateCacheKey(candidateLocation, jobLocation, type) {
        const candidate = `${candidateLocation.coordinates.lat},${candidateLocation.coordinates.lng}`;
        const job = `${jobLocation.coordinates.lat},${jobLocation.coordinates.lng}`;
        return `${type}_${candidate}_${job}`;
    }

    generateZoneKey(candidateLocation, jobLocation) {
        const candidateZone = this.getZoneForLocation(candidateLocation.coordinates);
        const jobZone = this.getZoneForLocation(jobLocation.coordinates);
        return `zone_${candidateZone}_${jobZone}`;
    }

    getZoneForLocation(coordinates) {
        for (const [zoneName, zone] of Object.entries(this.popularZones)) {
            const distance = this.calculateEuclideanDistance(coordinates, zone.center);
            if (distance * 1000 <= zone.radius) {
                return zoneName;
            }
        }
        return 'other';
    }

    /**
     * FALLBACK INTELLIGENT
     * Estimation sans API si problème
     */
    getFallbackScore(candidateData, jobData) {
        const candidateCoords = candidateData.coordonnees;
        const jobCoords = jobData.coordonnees;
        
        if (!candidateCoords || !jobCoords) {
            return { finalScore: 0.1, error: 'Coordonnées manquantes' };
        }
        
        const distance = this.calculateEuclideanDistance(candidateCoords, jobCoords);
        const estimatedTime = distance * 1.5; // Estimation conservative
        
        const durationScore = this.calculateDurationScore(estimatedTime);
        
        return {
            finalScore: durationScore * 0.7, // Pénalité pour estimation
            bestMode: 'estimated',
            fallback: true,
            estimatedDistance: distance,
            estimatedTime: estimatedTime
        };
    }

    /**
     * MÉTRIQUES ET MONITORING
     */
    updatePerformanceMetrics(calculationTime, wasCacheHit) {
        this.performanceMetrics.totalCalculations++;
        this.performanceMetrics.averageTime = 
            (this.performanceMetrics.averageTime * (this.performanceMetrics.totalCalculations - 1) + calculationTime) 
            / this.performanceMetrics.totalCalculations;
    }

    getPerformanceReport() {
        const totalCacheHits = Object.values(this.performanceMetrics.cacheHits).reduce((a, b) => a + b, 0);
        const cacheHitRate = this.performanceMetrics.totalCalculations > 0 ? 
            (totalCacheHits / this.performanceMetrics.totalCalculations * 100).toFixed(1) : '0';

        return {
            ...this.performanceMetrics,
            cacheHitRate: `${cacheHitRate}%`,
            cacheBreakdown: this.performanceMetrics.cacheHits,
            averageCostPerCalculation: this.performanceMetrics.totalCalculations > 0 ?
                (this.performanceMetrics.costTracking / this.performanceMetrics.totalCalculations).toFixed(4) : '0',
            cacheSizes: {
                level1: this.cache.level1.size,
                level2: this.cache.level2.size,
                level3: this.cache.level3.size
            }
        };
    }

    /**
     * UTILITAIRES SUPPLÉMENTAIRES
     */
    isCacheValid(cachedItem, maxAge) {
        return (Date.now() - cachedItem.timestamp) < maxAge;
    }

    cleanupCache() {
        // Nettoyage si trop d'entrées
        if (this.cache.level1.size > this.config.cache.maxSize) {
            const entries = Array.from(this.cache.level1.entries());
            entries.sort((a, b) => a[1].timestamp - b[1].timestamp);
            
            // Supprimer les 20% plus anciens
            const toDelete = Math.floor(entries.length * 0.2);
            for (let i = 0; i < toDelete; i++) {
                this.cache.level1.delete(entries[i][0]);
            }
        }
    }

    getTrafficFactor(departureTime) {
        const hour = parseInt(departureTime.split(':')[0]);
        
        // Facteurs d'embouteillage par heure
        if ((hour >= 7 && hour <= 9) || (hour >= 17 && hour <= 19)) {
            return 1.5; // Heures de pointe
        }
        if (hour >= 11 && hour <= 14) {
            return 0.9; // Heures creuses
        }
        return 1.1; // Normal
    }

    isBusinessDistrict(coordinates) {
        return Object.values(this.popularZones).some(zone => {
            if (!zone.businessDistrict) return false;
            const distance = this.calculateEuclideanDistance(coordinates, zone.center);
            return distance * 1000 <= zone.radius;
        });
    }

    generateRecommendation(scores, bestMode) {
        const best = scores[bestMode];
        const duration = Math.round(best.duration);
        
        return {
            mode: this.transportModes[bestMode].name,
            duration: `${duration} minutes`,
            score: `${(best.score * 100).toFixed(0)}%`,
            reason: this.getRecommendationReason(bestMode, best)
        };
    }

    getRecommendationReason(mode, scoreData) {
        if (scoreData.duration <= 30) return "Trajet très court et pratique";
        if (scoreData.preferences > 0.8) return "Correspond parfaitement à vos préférences";
        if (scoreData.cost > 0.8) return "Option la plus économique";
        if (scoreData.reliability > 0.9) return "Mode de transport très fiable";
        return "Meilleur compromis durée/facilité";
    }

    findAlternatives(scores) {
        return Object.entries(scores)
            .sort((a, b) => b[1].score - a[1].score)
            .slice(1, 3) // Top 2 alternatives
            .map(([mode, data]) => ({
                mode: this.transportModes[mode].name,
                duration: `${Math.round(data.duration)} min`,
                score: `${(data.score * 100).toFixed(0)}%`
            }));
    }
}

// Export pour intégration
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CommuteOptimizer;
}

if (typeof window !== 'undefined') {
    window.CommuteOptimizer = CommuteOptimizer;
}