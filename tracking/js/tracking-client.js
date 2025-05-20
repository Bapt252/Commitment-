/**
 * Commitment Tracking Client
 * 
 * Client JavaScript pour l'intégration du système de tracking côté frontend.
 * Permet de collecter les données comportementales utilisateur et de les envoyer
 * au serveur de manière efficace, avec gestion de la confidentialité et du consentement.
 */

class TrackingClient {
    /**
     * Initialise le client de tracking
     * 
     * @param {string} apiBaseUrl - URL de base de l'API (ex: http://localhost:5050)
     * @param {Object} options - Options de configuration
     * @param {number} options.batchSize - Taille maximale du lot d'événements (défaut: 10)
     * @param {number} options.batchInterval - Intervalle entre les envois en ms (défaut: 2000)
     * @param {number} options.retryAttempts - Nombre de tentatives en cas d'échec (défaut: 3)
     * @param {boolean} options.useLocalStorage - Utiliser localStorage pour le cache (défaut: true)
     * @param {boolean} options.debug - Mode debug (défaut: false)
     */
    constructor(apiBaseUrl, options = {}) {
        this.apiBaseUrl = apiBaseUrl;
        this.options = {
            batchSize: options.batchSize || 10,
            batchInterval: options.batchInterval || 2000,
            retryAttempts: options.retryAttempts || 3,
            useLocalStorage: options.useLocalStorage !== false,
            debug: options.debug || false,
            ...options
        };
        
        this.eventQueue = [];
        this.processingQueue = false;
        this.userConsent = {};
        
        // Charger les consentements du localStorage si disponible
        if (this.options.useLocalStorage && window.localStorage) {
            try {
                const storedConsent = localStorage.getItem('tracking_consent');
                if (storedConsent) {
                    this.userConsent = JSON.parse(storedConsent);
                }
            } catch (e) {
                this.log('Error loading consent from localStorage', e);
            }
        }
        
        // Démarrer le processeur de queue
        this.startQueueProcessor();
        
        this.log('Tracking client initialized', this.options);
    }
    
    /**
     * Fonction de logging interne
     */
    log(...args) {
        if (this.options.debug) {
            console.log('[TrackingClient]', ...args);
        }
    }
    
    /**
     * Vérifie si l'utilisateur a donné son consentement pour un type spécifique
     * 
     * @param {string} consentType - Type de consentement (ex: 'analytics')
     * @returns {boolean} - True si le consentement est valide
     */
    hasConsent(consentType) {
        return this.userConsent[consentType] && 
               this.userConsent[consentType].granted && 
               new Date(this.userConsent[consentType].expiresAt) > new Date();
    }
    
    /**
     * Définit le consentement utilisateur
     * 
     * @param {string} userId - Identifiant de l'utilisateur
     * @param {string} consentType - Type de consentement (ex: 'analytics')
     * @param {boolean} isGranted - Si le consentement est accordé
     * @returns {Promise<boolean>} - True si l'opération a réussi
     */
    async setConsent(userId, consentType, isGranted) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/consent/set`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    user_id: userId,
                    consent_type: consentType,
                    is_granted: isGranted
                })
            });
            
            if (response.ok) {
                // Mettre à jour le cache local
                this.userConsent[consentType] = {
                    granted: isGranted,
                    expiresAt: isGranted ? new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString() : null
                };
                
                // Sauvegarder dans localStorage
                if (this.options.useLocalStorage && window.localStorage) {
                    localStorage.setItem('tracking_consent', JSON.stringify(this.userConsent));
                }
                
                this.log(`Consent ${isGranted ? 'granted' : 'revoked'} for ${consentType}`);
                return true;
            }
            
            this.log('Error setting consent', response.status);
            return false;
        } catch (error) {
            this.log('Error setting consent', error);
            return false;
        }
    }
    
    /**
     * Tracker un événement
     * 
     * @param {Object} eventData - Données de l'événement
     * @returns {boolean} - True si l'événement a été ajouté à la queue
     */
    trackEvent(eventData) {
        // Vérifier le consentement
        if (!this.hasConsent('analytics')) {
            this.log('Cannot track event - no analytics consent');
            return false;
        }
        
        // Enrichir avec métadonnées du navigateur
        const enrichedEvent = {
            ...eventData,
            client_timestamp: new Date().toISOString(),
            session_id: this.getSessionId()
        };
        
        // Ajouter des métadonnées du navigateur si disponibles
        if (window.navigator) {
            enrichedEvent.device_type = this.getDeviceType();
            
            if (!enrichedEvent.metadata) {
                enrichedEvent.metadata = {};
            }
            
            enrichedEvent.metadata.browser = {
                name: this.getBrowserName(),
                language: navigator.language,
                platform: navigator.platform,
                viewport: {
                    width: window.innerWidth,
                    height: window.innerHeight
                }
            };
            
            // Référer si disponible
            if (document.referrer) {
                enrichedEvent.referrer_url = document.referrer;
            }
        }
        
        // Ajouter à la queue
        this.eventQueue.push(enrichedEvent);
        this.log('Event added to queue', enrichedEvent);
        
        // Si la queue dépasse la taille maximale, traiter immédiatement
        if (this.eventQueue.length >= this.options.batchSize) {
            this.processQueue();
        }
        
        return true;
    }
    
    /**
     * Obtient le type d'appareil
     */
    getDeviceType() {
        const ua = navigator.userAgent;
        if (/(tablet|ipad|playbook|silk)|(android(?!.*mobi))/i.test(ua)) {
            return 'tablet';
        }
        if (/Mobile|Android|iP(hone|od)|IEMobile|BlackBerry|Kindle|Silk-Accelerated|(hpw|web)OS|Opera M(obi|ini)/.test(ua)) {
            return 'mobile';
        }
        return 'desktop';
    }
    
    /**
     * Obtient le nom du navigateur
     */
    getBrowserName() {
        const ua = navigator.userAgent;
        let browserName = "Unknown";
        
        if (ua.indexOf("Firefox") > -1) {
            browserName = "Firefox";
        } else if (ua.indexOf("Opera") > -1 || ua.indexOf("OPR") > -1) {
            browserName = "Opera";
        } else if (ua.indexOf("Edge") > -1) {
            browserName = "Edge";
        } else if (ua.indexOf("Chrome") > -1) {
            browserName = "Chrome";
        } else if (ua.indexOf("Safari") > -1) {
            browserName = "Safari";
        } else if (ua.indexOf("MSIE") > -1 || ua.indexOf("Trident/") > -1) {
            browserName = "Internet Explorer";
        }
        
        return browserName;
    }
    
    /**
     * Obtient un ID de session
     */
    getSessionId() {
        if (!this._sessionId) {
            // Générer un nouvel ID de session ou récupérer du sessionStorage
            if (window.sessionStorage && sessionStorage.getItem('tracking_session_id')) {
                this._sessionId = sessionStorage.getItem('tracking_session_id');
            } else {
                this._sessionId = 'session_' + Math.random().toString(36).substring(2, 15);
                if (window.sessionStorage) {
                    sessionStorage.setItem('tracking_session_id', this._sessionId);
                }
            }
        }
        return this._sessionId;
    }
    
    /**
     * Démarrer le processeur de queue
     */
    startQueueProcessor() {
        setInterval(() => {
            if (this.eventQueue.length > 0 && !this.processingQueue) {
                this.processQueue();
            }
        }, this.options.batchInterval);
    }
    
    /**
     * Traiter la queue d'événements
     */
    async processQueue() {
        if (this.processingQueue || this.eventQueue.length === 0) {
            return;
        }
        
        this.processingQueue = true;
        
        try {
            // Extraire un lot d'événements
            const batch = this.eventQueue.splice(0, this.options.batchSize);
            
            this.log(`Processing queue: ${batch.length} events`);
            
            // Envoyer les événements
            const results = await Promise.all(batch.map(event => this.sendEvent(event)));
            
            // Remettre en queue les événements qui ont échoué
            const failedEvents = batch.filter((_, i) => !results[i]);
            if (failedEvents.length > 0) {
                this.log(`Failed to send ${failedEvents.length} events, adding back to queue`);
                this.eventQueue.push(...failedEvents);
            }
        } catch (error) {
            this.log('Error processing event queue', error);
        } finally {
            this.processingQueue = false;
        }
    }
    
    /**
     * Envoyer un événement au serveur
     * 
     * @param {Object} event - Événement à envoyer
     * @returns {Promise<boolean>} - True si l'envoi a réussi
     */
    async sendEvent(event) {
        const endpoint = `/api/events/${event.event_type.replace('_', '/')}`;
        let retries = 0;
        
        while (retries < this.options.retryAttempts) {
            try {
                const response = await fetch(`${this.apiBaseUrl}${endpoint}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(event)
                });
                
                if (response.ok) {
                    this.log(`Event sent successfully: ${event.event_type}`);
                    return true;
                }
                
                // Si le consentement est requis mais manquant
                if (response.status === 403) {
                    this.log('Consent required for tracking');
                    return false;
                }
                
                // Autres erreurs
                throw new Error(`HTTP error ${response.status}`);
            } catch (error) {
                retries++;
                if (retries >= this.options.retryAttempts) {
                    this.log('Failed to send event after retries', error);
                    return false;
                }
                
                // Attendre avant de réessayer (backoff exponentiel)
                const waitTime = Math.pow(2, retries) * 1000;
                this.log(`Retry ${retries}/${this.options.retryAttempts} after ${waitTime}ms`);
                await new Promise(resolve => setTimeout(resolve, waitTime));
            }
        }
    }
    
    /**
     * Helper pour tracker les matchs proposés
     */
    trackMatchProposed(userId, matchId, matchScore, parameters, constraintSatisfaction, alternativesCount) {
        return this.trackEvent({
            event_type: 'match_proposed',
            user_id: userId,
            match_id: matchId,
            match_score: matchScore,
            match_parameters: parameters || {},
            alternatives_count: alternativesCount || 0,
            constraint_satisfaction: constraintSatisfaction || {}
        });
    }
    
    /**
     * Helper pour tracker les matchs visualisés
     */
    trackMatchViewed(userId, matchId, viewDurationSeconds, viewComplete = true) {
        return this.trackEvent({
            event_type: 'match_viewed',
            user_id: userId,
            match_id: matchId,
            view_duration_seconds: viewDurationSeconds,
            view_complete: viewComplete
        });
    }
    
    /**
     * Helper pour tracker les acceptations de match
     */
    trackMatchAccepted(userId, matchId, decisionTimeSeconds) {
        return this.trackEvent({
            event_type: 'match_accepted',
            user_id: userId,
            match_id: matchId,
            decision_time_seconds: decisionTimeSeconds
        });
    }
    
    /**
     * Helper pour tracker les rejets de match
     */
    trackMatchRejected(userId, matchId, decisionTimeSeconds, reasons = []) {
        return this.trackEvent({
            event_type: 'match_rejected',
            user_id: userId,
            match_id: matchId,
            decision_time_seconds: decisionTimeSeconds,
            reasons: reasons
        });
    }
    
    /**
     * Helper pour tracker les feedbacks
     */
    trackMatchFeedback(userId, matchId, rating, feedbackText = '', specificAspects = {}) {
        return this.trackEvent({
            event_type: 'match_feedback',
            user_id: userId,
            match_id: matchId,
            rating: rating,
            feedback_text: feedbackText,
            specific_aspects: specificAspects
        });
    }
    
    /**
     * Helper pour tracker les interactions après matching
     */
    trackMatchInteraction(userId, matchId, interactionType, interactionCount = 1, details = {}) {
        return this.trackEvent({
            event_type: 'match_interaction',
            user_id: userId,
            match_id: matchId,
            interaction_type: interactionType,
            interaction_count: interactionCount,
            details: details
        });
    }
    
    /**
     * Helper pour tracker les complétions d'engagement
     */
    trackMatchCompletion(userId, matchId, durationDays, completionRate, successIndicators = {}) {
        return this.trackEvent({
            event_type: 'match_completed',
            user_id: userId,
            match_id: matchId,
            duration_days: durationDays,
            completion_rate: completionRate,
            success_indicators: successIndicators
        });
    }
    
    /**
     * Helper pour tracker les abandons d'engagement
     */
    trackMatchAbandoned(userId, matchId, durationDays, completionRate, successIndicators = {}) {
        return this.trackEvent({
            event_type: 'match_abandoned',
            user_id: userId,
            match_id: matchId,
            duration_days: durationDays,
            completion_rate: completionRate,
            success_indicators: successIndicators
        });
    }
}

// Exporter le client
window.TrackingClient = TrackingClient;
