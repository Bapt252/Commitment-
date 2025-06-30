/**
 * NEXTEN V2.0 OPTIMIZED - Google Maps Location Matcher
 * Calcul de géolocalisation avec intégration Google Maps API
 * 4 modes de transport, fallbacks intelligents, cache optimisé
 * 
 * @version 2.0-OPTIMIZED
 * @author NEXTEN Team
 * @created 2025-06-30
 */

class GoogleMapsLocationMatcher {
    constructor(options = {}) {
        // Configuration Google Maps
        this.config = {
            apiKey: options.apiKey || process.env.GOOGLE_MAPS_API_KEY || null,
            enabled: options.enabled !== false,
            baseUrl: 'https://maps.googleapis.com/maps/api',
            services: {
                distanceMatrix: '/distancematrix/json',
                geocoding: '/geocode/json',
                directions: '/directions/json'
            },
            defaultParams: {
                units: 'metric',
                language: 'fr',
                region: 'fr'
            }
        };
        
        // Modes de transport supportés
        this.transportModes = {
            driving: {
                name: 'Voiture',
                averageSpeed: 30, // km/h en ville
                maxDistance: 100, // km raisonnable
                icon: '🚗'
            },
            transit: {
                name: 'Transport Public',
                averageSpeed: 20, // km/h transport public
                maxDistance: 50,
                icon: '🚇'
            },
            walking: {
                name: 'Marche',
                averageSpeed: 5, // km/h marche
                maxDistance: 10,
                icon: '🚶'
            },
            bicycling: {
                name: 'Vélo',
                averageSpeed: 15, // km/h vélo
                maxDistance: 25,
                icon: '🚴'
            }
        };
        
        // Configuration du cache
        this.cache = {
            geocoding: new Map(),
            distances: new Map(),
            ttl: 3600000, // 1 heure
            maxSize: 1000
        };
        
        // Métriques et statistiques
        this.metrics = {
            apiCalls: 0,
            cacheHits: 0,
            cacheMisses: 0,
            errors: 0,
            averageResponseTime: 0,
            geocodingCalls: 0,
            distanceMatrixCalls: 0
        };
        
        // Configuration fallback
        this.fallbackConfig = {
            enabled: true,
            useEuclideanDistance: true,
            cityMappings: this.initializeCityMappings(),
            defaultScores: {
                sameCity: 0.85,
                sameRegion: 0.65,
                differentRegion: 0.35,
                remote: 1.0
            }
        };
        
        console.log('🗺️ Google Maps Location Matcher initialized');
        console.log(`📡 API enabled: ${this.config.enabled}`);
        console.log(`🚗 Transport modes: ${Object.keys(this.transportModes).length}`);
    }
    
    /**
     * Calcul principal de matching géographique
     * @param {Object} candidateData - Données candidat avec localisation
     * @param {Object} jobData - Données job avec localisation
     * @param {Object} options - Options de calcul
     * @returns {Promise<Object>} Résultat de matching géographique
     */
    async calculateLocationMatch(candidateData, jobData, options = {}) {
        const startTime = performance.now();
        const transportMode = options.transportMode || 'driving';
        
        try {
            // Vérification des cas spéciaux
            const specialCase = this.checkSpecialCases(candidateData, jobData);
            if (specialCase) {
                return this.addPerformanceMetrics(specialCase, startTime);
            }
            
            // Calcul avec Google Maps si activé
            if (this.config.enabled && this.config.apiKey) {
                return await this.calculateWithGoogleMaps(candidateData, jobData, transportMode, options);
            } else {
                // Fallback intelligent
                return await this.calculateWithFallback(candidateData, jobData, transportMode, options);
            }
            
        } catch (error) {
            console.error('❌ Erreur calcul géolocalisation:', error);
            this.metrics.errors++;
            return this.generateErrorFallback(candidateData, jobData, error, startTime);
        }
    }
    
    /**
     * Vérification des cas spéciaux (remote, même adresse, etc.)
     */
    checkSpecialCases(candidateData, jobData) {
        // Job en remote complet
        if (jobData.workMode === 'remote_100' || 
            jobData.location === 'Remote First' ||
            jobData.location?.toLowerCase().includes('remote')) {
            return {
                score: 1.0,
                details: {
                    type: 'remote_job',
                    reason: 'Job en télétravail complet',
                    travelTime: 0,
                    distance: 0,
                    transportMode: 'none'
                },
                confidence: 1.0,
                apiCalls: 0,
                fallback: false
            };
        }
        
        // Même adresse exacte
        if (candidateData.location === jobData.location) {
            return {
                score: 0.98,
                details: {
                    type: 'same_address',
                    reason: 'Adresse identique',
                    travelTime: 5,
                    distance: 0.5,
                    transportMode: 'walking'
                },
                confidence: 0.95,
                apiCalls: 0,
                fallback: false
            };
        }
        
        return null;
    }
    
    /**
     * Calcul avec Google Maps API
     */
    async calculateWithGoogleMaps(candidateData, jobData, transportMode, options) {
        const startTime = performance.now();
        
        try {
            // 1. Géocodage des adresses si nécessaire
            const candidateCoords = await this.geocodeAddress(candidateData);
            const jobCoords = await this.geocodeAddress(jobData);
            
            // 2. Calcul de distance et temps via Distance Matrix API
            const distanceData = await this.getDistanceMatrix(
                candidateCoords,
                jobCoords,
                transportMode,
                options
            );
            
            // 3. Scoring basé sur les résultats Google Maps
            const score = this.calculateLocationScore(distanceData, transportMode);
            
            return {
                score,
                details: {
                    type: 'google_maps_api',
                    distance: distanceData.distance,
                    travelTime: distanceData.duration,
                    transportMode,
                    route: `${candidateData.location} → ${jobData.location}`,
                    candidateCoords,
                    jobCoords,
                    googleMapsData: distanceData
                },
                confidence: 0.95,
                apiCalls: this.metrics.distanceMatrixCalls + this.metrics.geocodingCalls,
                fallback: false,
                calculationTime: performance.now() - startTime
            };
            
        } catch (error) {
            console.warn('⚠️ Google Maps API error, using fallback:', error.message);
            return await this.calculateWithFallback(candidateData, jobData, transportMode, options);
        }
    }
    
    /**
     * Géocodage d'une adresse
     */
    async geocodeAddress(locationData) {
        const address = locationData.location || locationData.adresse;
        
        // Vérification cache
        const cacheKey = `geocode_${address}`;
        if (this.cache.geocoding.has(cacheKey)) {
            this.metrics.cacheHits++;
            return this.cache.geocoding.get(cacheKey);
        }
        
        // Coordonnées déjà présentes
        if (locationData.coordinates || (locationData.latitude && locationData.longitude)) {
            const coords = locationData.coordinates || {
                lat: locationData.latitude,
                lng: locationData.longitude
            };
            this.cache.geocoding.set(cacheKey, coords);
            return coords;
        }
        
        // Appel API Geocoding
        try {
            const url = this.buildGeocodingUrl(address);
            const response = await this.makeApiCall(url);
            
            if (response.status === 'OK' && response.results.length > 0) {
                const location = response.results[0].geometry.location;
                const coords = { lat: location.lat, lng: location.lng };
                
                // Mise en cache
                this.cache.geocoding.set(cacheKey, coords);
                this.metrics.geocodingCalls++;
                
                return coords;
            } else {
                throw new Error(`Geocoding failed: ${response.status}`);
            }
            
        } catch (error) {
            console.warn('⚠️ Geocoding fallback for:', address);
            // Fallback avec coordonnées estimées
            return this.estimateCoordinatesFromAddress(address);
        }
    }
    
    /**
     * Calcul de distance via Distance Matrix API
     */
    async getDistanceMatrix(originCoords, destCoords, transportMode, options) {
        const cacheKey = `distance_${originCoords.lat}_${originCoords.lng}_${destCoords.lat}_${destCoords.lng}_${transportMode}`;
        
        // Vérification cache
        if (this.cache.distances.has(cacheKey)) {
            this.metrics.cacheHits++;
            return this.cache.distances.get(cacheKey);
        }
        
        try {
            const url = this.buildDistanceMatrixUrl(originCoords, destCoords, transportMode);
            const response = await this.makeApiCall(url);
            
            if (response.status === 'OK' && 
                response.rows[0].elements[0].status === 'OK') {
                
                const element = response.rows[0].elements[0];
                const distanceData = {
                    distance: element.distance.value / 1000, // en km
                    duration: element.duration.value / 60,   // en minutes
                    distanceText: element.distance.text,
                    durationText: element.duration.text,
                    transportMode
                };
                
                // Mise en cache
                this.cache.distances.set(cacheKey, distanceData);
                this.metrics.distanceMatrixCalls++;
                
                return distanceData;
                
            } else {
                throw new Error(`Distance Matrix failed: ${response.status}`);
            }
            
        } catch (error) {
            console.warn('⚠️ Distance Matrix fallback');
            // Fallback avec calcul euclidien
            return this.calculateEuclideanDistanceData(originCoords, destCoords, transportMode);
        }
    }
    
    /**
     * Calcul avec fallback intelligent
     */
    async calculateWithFallback(candidateData, jobData, transportMode, options) {
        const startTime = performance.now();
        
        try {
            // Analyse des villes/régions
            const candidateLocation = this.parseLocation(candidateData.location);
            const jobLocation = this.parseLocation(jobData.location);
            
            // Calcul basé sur la proximité géographique
            let score;
            let details;
            
            if (candidateLocation.city === jobLocation.city) {
                // Même ville
                score = this.fallbackConfig.defaultScores.sameCity;
                details = {
                    type: 'city_matching',
                    reason: 'Même ville',
                    estimatedDistance: 15,
                    estimatedTravelTime: 30,
                    transportMode
                };
                
            } else if (candidateLocation.region === jobLocation.region) {
                // Même région
                score = this.fallbackConfig.defaultScores.sameRegion;
                details = {
                    type: 'region_matching',
                    reason: 'Même région',
                    estimatedDistance: 50,
                    estimatedTravelTime: 60,
                    transportMode
                };
                
            } else {
                // Régions différentes
                score = this.fallbackConfig.defaultScores.differentRegion;
                details = {
                    type: 'cross_region',
                    reason: 'Régions différentes',
                    estimatedDistance: 200,
                    estimatedTravelTime: 180,
                    transportMode
                };
            }
            
            // Ajustement selon le mode de transport
            score = this.adjustScoreForTransportMode(score, transportMode, details.estimatedDistance);
            
            return {
                score,
                details: {
                    ...details,
                    candidateLocation: candidateLocation.display,
                    jobLocation: jobLocation.display,
                    fallbackMethod: 'geographic_analysis'
                },
                confidence: 0.70,
                apiCalls: 0,
                fallback: true,
                calculationTime: performance.now() - startTime
            };
            
        } catch (error) {
            console.error('❌ Fallback calculation error:', error);
            return this.generateErrorFallback(candidateData, jobData, error, startTime);
        }
    }
    
    /**
     * Scoring basé sur les données Google Maps
     */
    calculateLocationScore(distanceData, transportMode) {
        const { distance, duration } = distanceData;
        const modeConfig = this.transportModes[transportMode];
        
        let score = 1.0;
        
        // Scoring basé sur le temps de trajet
        if (duration <= 20) {
            score = 1.0;  // Excellent
        } else if (duration <= 30) {
            score = 0.9;  // Très bon
        } else if (duration <= 45) {
            score = 0.8;  // Bon
        } else if (duration <= 60) {
            score = 0.7;  // Acceptable
        } else if (duration <= 90) {
            score = 0.5;  // Moyen
        } else {
            score = 0.3;  // Difficile
        }
        
        // Pénalité pour distance excessive selon le mode
        if (distance > modeConfig.maxDistance) {
            score *= 0.7;
        }
        
        // Bonus pour transport public écologique
        if (transportMode === 'transit' && distance > 10) {
            score *= 1.1;
        }
        
        return Math.min(1.0, Math.max(0.1, score));
    }
    
    /**
     * Ajustement du score selon le mode de transport
     */
    adjustScoreForTransportMode(baseScore, transportMode, estimatedDistance) {
        const modeConfig = this.transportModes[transportMode];
        
        // Pénalité si distance excessive pour le mode
        if (estimatedDistance > modeConfig.maxDistance) {
            baseScore *= 0.6;
        }
        
        // Ajustements spécifiques par mode
        switch (transportMode) {
            case 'walking':
                if (estimatedDistance > 5) baseScore *= 0.5;
                break;
            case 'bicycling':
                if (estimatedDistance > 15) baseScore *= 0.7;
                break;
            case 'transit':
                if (estimatedDistance < 5) baseScore *= 0.9; // Moins efficace pour courtes distances
                break;
            case 'driving':
                // Pas d'ajustement particulier
                break;
        }
        
        return Math.min(1.0, Math.max(0.1, baseScore));
    }
    
    /**
     * Construction des URLs d'API
     */
    buildGeocodingUrl(address) {
        const params = new URLSearchParams({
            address: encodeURIComponent(address),
            key: this.config.apiKey,
            language: this.config.defaultParams.language,
            region: this.config.defaultParams.region
        });
        
        return `${this.config.baseUrl}${this.config.services.geocoding}?${params}`;
    }
    
    buildDistanceMatrixUrl(origin, destination, transportMode) {
        const params = new URLSearchParams({
            origins: `${origin.lat},${origin.lng}`,
            destinations: `${destination.lat},${destination.lng}`,
            mode: transportMode,
            units: this.config.defaultParams.units,
            language: this.config.defaultParams.language,
            key: this.config.apiKey
        });
        
        return `${this.config.baseUrl}${this.config.services.distanceMatrix}?${params}`;
    }
    
    /**
     * Appel API avec gestion d'erreurs
     */
    async makeApiCall(url) {
        const startTime = performance.now();
        
        try {
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            // Mise à jour des métriques
            this.metrics.apiCalls++;
            const responseTime = performance.now() - startTime;
            this.metrics.averageResponseTime = 
                (this.metrics.averageResponseTime + responseTime) / 2;
            
            return data;
            
        } catch (error) {
            this.metrics.errors++;
            throw error;
        }
    }
    
    /**
     * Parsing et analyse des localisations
     */
    parseLocation(locationString) {
        if (!locationString) {
            return { city: 'Unknown', region: 'Unknown', display: 'Non spécifié' };
        }
        
        const cleanLocation = locationString.trim();
        const parts = cleanLocation.split(',').map(part => part.trim());
        
        // Extraction ville et région
        let city = 'Unknown';
        let region = 'Unknown';
        
        if (parts.length >= 2) {
            city = parts[0].toLowerCase();
            
            // Détection de la région à partir du code postal ou nom
            const lastPart = parts[parts.length - 1].toLowerCase();
            if (lastPart.includes('paris') || lastPart.match(/75\d{3}/)) {
                region = 'ile-de-france';
            } else if (lastPart.includes('lyon') || lastPart.match(/69\d{3}/)) {
                region = 'auvergne-rhone-alpes';
            } else if (lastPart.includes('marseille') || lastPart.match(/13\d{3}/)) {
                region = 'provence-alpes-cote-dazur';
            } else {
                region = this.mapCityToRegion(city);
            }
        } else {
            city = cleanLocation.toLowerCase();
            region = this.mapCityToRegion(city);
        }
        
        return {
            city: this.normalizeCityName(city),
            region,
            display: cleanLocation
        };
    }
    
    /**
     * Normalisation des noms de villes
     */
    normalizeCityName(cityName) {
        const cityMappings = {
            'paris': 'paris',
            'lyon': 'lyon',
            'marseille': 'marseille',
            'toulouse': 'toulouse',
            'nice': 'nice',
            'nantes': 'nantes',
            'strasbourg': 'strasbourg',
            'montpellier': 'montpellier',
            'bordeaux': 'bordeaux',
            'lille': 'lille',
            'neuilly-sur-seine': 'paris',
            'boulogne-billancourt': 'paris',
            'courbevoie': 'paris',
            'la-defense': 'paris'
        };
        
        return cityMappings[cityName.toLowerCase()] || cityName.toLowerCase();
    }
    
    /**
     * Mapping ville -> région
     */
    mapCityToRegion(cityName) {
        const regionMappings = {
            'paris': 'ile-de-france',
            'lyon': 'auvergne-rhone-alpes',
            'marseille': 'provence-alpes-cote-dazur',
            'toulouse': 'occitanie',
            'nice': 'provence-alpes-cote-dazur',
            'nantes': 'pays-de-la-loire',
            'strasbourg': 'grand-est',
            'montpellier': 'occitanie',
            'bordeaux': 'nouvelle-aquitaine',
            'lille': 'hauts-de-france'
        };
        
        return regionMappings[cityName.toLowerCase()] || 'unknown';
    }
    
    /**
     * Estimation de coordonnées depuis une adresse
     */
    estimateCoordinatesFromAddress(address) {
        const cityCoordinates = {
            'paris': { lat: 48.8566, lng: 2.3522 },
            'lyon': { lat: 45.7640, lng: 4.8357 },
            'marseille': { lat: 43.2965, lng: 5.3698 },
            'toulouse': { lat: 43.6047, lng: 1.4442 },
            'nice': { lat: 43.7102, lng: 7.2620 },
            'nantes': { lat: 47.2184, lng: -1.5536 },
            'strasbourg': { lat: 48.5734, lng: 7.7521 },
            'montpellier': { lat: 43.6110, lng: 3.8767 },
            'bordeaux': { lat: 44.8378, lng: -0.5792 },
            'lille': { lat: 50.6292, lng: 3.0573 }
        };
        
        // Recherche par ville dans l'adresse
        for (const [city, coords] of Object.entries(cityCoordinates)) {
            if (address.toLowerCase().includes(city)) {
                return coords;
            }
        }
        
        // Fallback Paris par défaut
        return cityCoordinates.paris;
    }
    
    /**
     * Calcul euclidien de secours
     */
    calculateEuclideanDistanceData(coord1, coord2, transportMode) {
        const distance = this.calculateEuclideanDistance(coord1, coord2);
        const modeConfig = this.transportModes[transportMode];
        const estimatedTime = (distance / modeConfig.averageSpeed) * 60;
        
        return {
            distance,
            duration: estimatedTime,
            distanceText: `${Math.round(distance)} km`,
            durationText: `${Math.round(estimatedTime)} min`,
            transportMode,
            fallback: true
        };
    }
    
    /**
     * Calcul distance euclidienne
     */
    calculateEuclideanDistance(coord1, coord2) {
        const R = 6371; // Rayon de la Terre en km
        const dLat = (coord2.lat - coord1.lat) * Math.PI / 180;
        const dLng = (coord2.lng - coord1.lng) * Math.PI / 180;
        const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                 Math.cos(coord1.lat * Math.PI / 180) * Math.cos(coord2.lat * Math.PI / 180) *
                 Math.sin(dLng/2) * Math.sin(dLng/2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
        return R * c;
    }
    
    /**
     * Initialisation des mappings de villes
     */
    initializeCityMappings() {
        return {
            'paris': {
                region: 'ile-de-france',
                suburbs: ['neuilly-sur-seine', 'boulogne-billancourt', 'courbevoie', 'la-defense'],
                coordinates: { lat: 48.8566, lng: 2.3522 }
            },
            'lyon': {
                region: 'auvergne-rhone-alpes',
                suburbs: ['villeurbanne', 'caluire-et-cuire'],
                coordinates: { lat: 45.7640, lng: 4.8357 }
            }
            // Autres villes...
        };
    }
    
    /**
     * Génération de fallback en cas d'erreur
     */
    generateErrorFallback(candidateData, jobData, error, startTime) {
        return {
            score: 0.5,
            details: {
                type: 'error_fallback',
                reason: 'Erreur de calcul géographique',
                error: error.message,
                candidateLocation: candidateData.location || 'Non spécifié',
                jobLocation: jobData.location || 'Non spécifié'
            },
            confidence: 0.3,
            apiCalls: 0,
            fallback: true,
            calculationTime: performance.now() - startTime
        };
    }
    
    /**
     * Ajout des métriques de performance
     */
    addPerformanceMetrics(result, startTime) {
        result.calculationTime = performance.now() - startTime;
        return result;
    }
    
    /**
     * Nettoyage du cache
     */
    cleanCache() {
        const now = Date.now();
        
        // Nettoyage cache géocodage
        for (const [key, value] of this.cache.geocoding.entries()) {
            if (now - value.timestamp > this.cache.ttl) {
                this.cache.geocoding.delete(key);
            }
        }
        
        // Nettoyage cache distances
        for (const [key, value] of this.cache.distances.entries()) {
            if (now - value.timestamp > this.cache.ttl) {
                this.cache.distances.delete(key);
            }
        }
        
        console.log('🧹 Cache cleaned');
    }
    
    /**
     * Statistiques du matcher
     */
    getStatistics() {
        return {
            version: '2.0-OPTIMIZED',
            config: {
                apiEnabled: this.config.enabled,
                hasApiKey: !!this.config.apiKey,
                transportModes: Object.keys(this.transportModes),
                fallbackEnabled: this.fallbackConfig.enabled
            },
            metrics: { ...this.metrics },
            cache: {
                geocodingSize: this.cache.geocoding.size,
                distancesSize: this.cache.distances.size,
                hitRate: this.metrics.cacheHits / (this.metrics.cacheHits + this.metrics.cacheMisses) || 0
            }
        };
    }
    
    /**
     * Test de connectivité Google Maps
     */
    async testConnectivity() {
        if (!this.config.enabled || !this.config.apiKey) {
            return {
                status: 'disabled',
                message: 'Google Maps API désactivé ou clé manquante'
            };
        }
        
        try {
            // Test simple de géocodage
            const testUrl = this.buildGeocodingUrl('Paris, France');
            const response = await this.makeApiCall(testUrl);
            
            if (response.status === 'OK') {
                return {
                    status: 'connected',
                    message: 'Google Maps API opérationnel',
                    quota: response.error_message ? 'limited' : 'ok'
                };
            } else {
                return {
                    status: 'error',
                    message: `API Error: ${response.status}`,
                    error: response.error_message
                };
            }
            
        } catch (error) {
            return {
                status: 'error',
                message: 'Erreur de connectivité',
                error: error.message
            };
        }
    }
    
    /**
     * Configuration dynamique
     */
    updateConfig(newConfig) {
        if (newConfig.apiKey !== undefined) {
            this.config.apiKey = newConfig.apiKey;
        }
        if (newConfig.enabled !== undefined) {
            this.config.enabled = newConfig.enabled;
        }
        if (newConfig.defaultTransportMode !== undefined) {
            this.config.defaultTransportMode = newConfig.defaultTransportMode;
        }
        
        console.log('⚙️ Google Maps config updated');
    }
    
    /**
     * Réinitialisation des métriques
     */
    resetMetrics() {
        this.metrics = {
            apiCalls: 0,
            cacheHits: 0,
            cacheMisses: 0,
            errors: 0,
            averageResponseTime: 0,
            geocodingCalls: 0,
            distanceMatrixCalls: 0
        };
        
        console.log('📊 Métriques réinitialisées');
    }
}

// Export pour utilisation modulaire
if (typeof module !== 'undefined' && module.exports) {
    module.exports = GoogleMapsLocationMatcher;
} else if (typeof window !== 'undefined') {
    window.GoogleMapsLocationMatcher = GoogleMapsLocationMatcher;
}

console.log('🗺️ Google Maps Location Matcher loaded successfully');
