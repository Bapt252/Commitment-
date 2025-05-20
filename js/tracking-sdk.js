/**
 * Commitment Tracking SDK
 * 
 * SDK JavaScript pour l'intégration du système de tracking avec le frontend.
 * Permet de collecter des événements utilisateur et de gérer les consentements.
 * 
 * @version 1.0.0
 */

/**
 * Configuration par défaut du SDK
 */
const DEFAULT_CONFIG = {
  apiUrl: '/api/events',
  consentUrl: '/api/consent',
  batchSize: 10,
  flushInterval: 5000, // 5 secondes
  useBeacon: true,
  debug: false,
  storageKey: 'commitment_tracking',
  anonymizeIp: true,
  sessionTimeout: 30 * 60 * 1000, // 30 minutes
};

/**
 * Types d'événements supportés
 */
const EventTypes = {
  MATCH_PROPOSED: 'match_proposed',
  MATCH_VIEWED: 'match_viewed',
  MATCH_ACCEPTED: 'match_accepted',
  MATCH_REJECTED: 'match_rejected',
  MATCH_FEEDBACK: 'match_feedback',
  MATCH_INTERACTION: 'match_interaction',
  MATCH_COMPLETED: 'match_completed',
  MATCH_ABANDONED: 'match_abandoned',
};

/**
 * Classe principale du SDK de tracking
 */
class CommitmentTracking {
  /**
   * Crée une nouvelle instance du SDK
   * 
   * @param {Object} config - Configuration personnalisée
   * @param {string} config.apiUrl - URL de base de l'API de tracking
   * @param {string} config.consentUrl - URL de l'API de consentement
   * @param {number} config.batchSize - Taille du lot pour l'envoi groupé d'événements
   * @param {number} config.flushInterval - Intervalle d'envoi automatique en ms
   * @param {boolean} config.useBeacon - Utiliser l'API Navigator.sendBeacon si disponible
   * @param {boolean} config.debug - Activer le mode debug
   * @param {string} config.storageKey - Clé pour le stockage local
   * @param {boolean} config.anonymizeIp - Anonymiser l'adresse IP
   * @param {number} config.sessionTimeout - Délai d'expiration de session en ms
   */
  constructor(config = {}) {
    // Fusionner la configuration personnalisée avec les valeurs par défaut
    this.config = { ...DEFAULT_CONFIG, ...config };
    
    // File d'attente pour les événements
    this.eventQueue = [];
    
    // ID de session unique pour cet utilisateur
    this.sessionId = this._getOrCreateSessionId();
    
    // État de consentement
    this.consents = this._loadConsents();
    
    // État d'initialisation
    this.initialized = false;
    
    // Timers
    this.flushTimer = null;
    this.sessionTimer = null;
    
    // Écouteurs d'événements
    this.listeners = {};
    
    // Méta-information sur le navigateur et l'appareil
    this.deviceInfo = this._getDeviceInfo();
    
    this._debug('SDK initialized with config:', this.config);
  }
  
  /**
   * Initialise le SDK et active la collecte d'événements
   * 
   * @param {string} userId - Identifiant utilisateur
   * @returns {Promise<boolean>} - True si l'initialisation a réussi
   */
  async init(userId) {
    if (this.initialized) {
      this._debug('SDK already initialized');
      return true;
    }
    
    if (!userId) {
      this._error('User ID is required for initialization');
      return false;
    }
    
    this.userId = userId;
    
    // Vérifier les consentements
    const hasConsent = this._hasRequiredConsents(['analytics']);
    
    if (!hasConsent) {
      this._debug('User has not given required consents');
      this._triggerEvent('consentRequired', {
        userId,
        requiredConsents: ['analytics']
      });
      return false;
    }
    
    // Activer la collecte d'événements
    this._startEventCollection();
    
    // Marquer comme initialisé
    this.initialized = true;
    
    this._debug('SDK fully initialized for user:', userId);
    return true;
  }
  
  /**
   * Démarre la collecte d'événements et configure les timers
   * 
   * @private
   */
  _startEventCollection() {
    // Configurer le timer pour l'envoi automatique
    this.flushTimer = setInterval(() => this.flush(), this.config.flushInterval);
    
    // Configurer le timer pour la session
    this._refreshSessionTimer();
    
    // Configurer l'écouteur pour l'envoi lors de la fermeture de la page
    if (typeof window !== 'undefined') {
      window.addEventListener('beforeunload', () => this.flush(true));
    }
    
    this._debug('Event collection started');
  }
  
  /**
   * Rafraîchit le timer de session
   * 
   * @private
   */
  _refreshSessionTimer() {
    // Annuler le timer existant
    if (this.sessionTimer) {
      clearTimeout(this.sessionTimer);
    }
    
    // Créer un nouveau timer
    this.sessionTimer = setTimeout(() => {
      // Générer un nouvel ID de session après l'expiration
      this.sessionId = this._generateSessionId();
      this._saveSessionId(this.sessionId);
      
      this._debug('Session expired, new session ID:', this.sessionId);
      
      // Déclencher l'événement de nouvelle session
      this._triggerEvent('newSession', { sessionId: this.sessionId });
    }, this.config.sessionTimeout);
  }
  
  /**
   * Récupère les informations sur le dispositif et le navigateur
   * 
   * @private
   * @returns {Object} - Informations sur le dispositif
   */
  _getDeviceInfo() {
    if (typeof window === 'undefined' || typeof navigator === 'undefined') {
      return {};
    }
    
    // Détection simple du type d'appareil
    const isMobile = /Mobi|Android|iPhone|iPad|iPod/i.test(navigator.userAgent);
    const isTablet = /Tablet|iPad/i.test(navigator.userAgent) || 
      (isMobile && Math.min(window.screen.width, window.screen.height) > 480);
    
    const deviceType = isTablet ? 'tablet' : (isMobile ? 'mobile' : 'desktop');
    
    // Détection du navigateur
    let browserName = 'unknown';
    if (navigator.userAgent.indexOf('Chrome') !== -1) browserName = 'chrome';
    else if (navigator.userAgent.indexOf('Firefox') !== -1) browserName = 'firefox';
    else if (navigator.userAgent.indexOf('Safari') !== -1) browserName = 'safari';
    else if (navigator.userAgent.indexOf('Edge') !== -1) browserName = 'edge';
    else if (navigator.userAgent.indexOf('MSIE') !== -1 || 
             navigator.userAgent.indexOf('Trident') !== -1) browserName = 'ie';
    
    // Détection du système d'exploitation
    let osName = 'unknown';
    if (navigator.userAgent.indexOf('Windows') !== -1) osName = 'windows';
    else if (navigator.userAgent.indexOf('Mac') !== -1) osName = 'macos';
    else if (navigator.userAgent.indexOf('Linux') !== -1) osName = 'linux';
    else if (navigator.userAgent.indexOf('Android') !== -1) osName = 'android';
    else if (navigator.userAgent.indexOf('iOS') !== -1 || 
             navigator.userAgent.indexOf('iPhone') !== -1 || 
             navigator.userAgent.indexOf('iPad') !== -1) osName = 'ios';
    
    return {
      deviceType,
      browserName,
      osName,
      screenWidth: window.screen.width,
      screenHeight: window.screen.height,
      timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      language: navigator.language || navigator.userLanguage || 'unknown',
      userAgent: navigator.userAgent,
    };
  }
  
  /**
   * Vérifie si tous les consentements requis sont accordés
   * 
   * @private
   * @param {Array<string>} requiredConsents - Liste des consentements requis
   * @returns {boolean} - True si tous les consentements sont accordés
   */
  _hasRequiredConsents(requiredConsents) {
    // En mode debug, on considère tous les consentements comme accordés
    if (this.config.debug) {
      return true;
    }
    
    return requiredConsents.every(consent => 
      this.consents[consent] && this.consents[consent].granted);
  }
  
  /**
   * Charge les consentements depuis le stockage local
   * 
   * @private
   * @returns {Object} - État des consentements
   */
  _loadConsents() {
    if (typeof localStorage === 'undefined') {
      return {};
    }
    
    try {
      const stored = localStorage.getItem(`${this.config.storageKey}_consents`);
      return stored ? JSON.parse(stored) : {};
    } catch (e) {
      this._error('Error loading consents:', e);
      return {};
    }
  }
  
  /**
   * Sauvegarde les consentements dans le stockage local
   * 
   * @private
   * @param {Object} consents - État des consentements à sauvegarder
   */
  _saveConsents(consents) {
    if (typeof localStorage === 'undefined') {
      return;
    }
    
    try {
      localStorage.setItem(
        `${this.config.storageKey}_consents`, 
        JSON.stringify(consents)
      );
    } catch (e) {
      this._error('Error saving consents:', e);
    }
  }
  
  /**
   * Récupère ou crée un ID de session
   * 
   * @private
   * @returns {string} - ID de session
   */
  _getOrCreateSessionId() {
    if (typeof sessionStorage === 'undefined') {
      return this._generateSessionId();
    }
    
    let sessionId = sessionStorage.getItem(`${this.config.storageKey}_session_id`);
    
    if (!sessionId) {
      sessionId = this._generateSessionId();
      this._saveSessionId(sessionId);
    }
    
    return sessionId;
  }
  
  /**
   * Sauvegarde l'ID de session
   * 
   * @private
   * @param {string} sessionId - ID de session à sauvegarder
   */
  _saveSessionId(sessionId) {
    if (typeof sessionStorage === 'undefined') {
      return;
    }
    
    try {
      sessionStorage.setItem(`${this.config.storageKey}_session_id`, sessionId);
    } catch (e) {
      this._error('Error saving session ID:', e);
    }
  }
  
  /**
   * Génère un ID de session unique
   * 
   * @private
   * @returns {string} - ID de session généré
   */
  _generateSessionId() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      const r = Math.random() * 16 | 0;
      const v = c === 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  }
  
  /**
   * Génère un ID d'événement unique
   * 
   * @private
   * @returns {string} - ID d'événement généré
   */
  _generateEventId() {
    return 'evt_' + Date.now().toString(36) + Math.random().toString(36).substr(2, 9);
  }
  
  /**
   * Affiche un message de débogage dans la console
   * 
   * @private
   * @param {string} message - Message à afficher
   * @param {any} data - Données supplémentaires à afficher
   */
  _debug(message, data) {
    if (this.config.debug && typeof console !== 'undefined') {
      if (data !== undefined) {
        console.log(`[Commitment Tracking] ${message}`, data);
      } else {
        console.log(`[Commitment Tracking] ${message}`);
      }
    }
  }
  
  /**
   * Affiche un message d'erreur dans la console
   * 
   * @private
   * @param {string} message - Message à afficher
   * @param {any} data - Données supplémentaires à afficher
   */
  _error(message, data) {
    if (typeof console !== 'undefined') {
      if (data !== undefined) {
        console.error(`[Commitment Tracking] ${message}`, data);
      } else {
        console.error(`[Commitment Tracking] ${message}`);
      }
    }
  }
  
  /**
   * Déclenche un événement personnalisé
   * 
   * @private
   * @param {string} eventName - Nom de l'événement
   * @param {Object} data - Données associées à l'événement
   */
  _triggerEvent(eventName, data) {
    if (this.listeners[eventName]) {
      this.listeners[eventName].forEach(callback => {
        try {
          callback(data);
        } catch (e) {
          this._error(`Error in ${eventName} event listener:`, e);
        }
      });
    }
  }
  
  /**
   * Ajoute un écouteur d'événement
   * 
   * @param {string} eventName - Nom de l'événement
   * @param {Function} callback - Fonction de rappel
   * @returns {Function} - Fonction pour supprimer l'écouteur
   */
  on(eventName, callback) {
    if (!this.listeners[eventName]) {
      this.listeners[eventName] = [];
    }
    
    this.listeners[eventName].push(callback);
    
    // Retourner une fonction pour supprimer l'écouteur
    return () => {
      this.listeners[eventName] = this.listeners[eventName].filter(cb => cb !== callback);
    };
  }
  
  /**
   * Vérifie si le SDK est correctement initialisé
   * 
   * @private
   * @returns {boolean} - True si le SDK est initialisé
   */
  _checkInitialized() {
    if (!this.initialized) {
      this._error('SDK not initialized. Call init() first.');
      return false;
    }
    
    return true;
  }
  
  /**
   * Définit l'état de consentement pour un type spécifique
   * 
   * @param {string} consentType - Type de consentement
   * @param {boolean} granted - Si le consentement est accordé
   * @returns {Promise<boolean>} - True si l'opération a réussi
   */
  async setConsent(consentType, granted) {
    // Mettre à jour l'état local
    this.consents[consentType] = {
      granted,
      timestamp: new Date().toISOString()
    };
    
    // Sauvegarder dans le stockage local
    this._saveConsents(this.consents);
    
    // Envoyer au serveur si l'utilisateur est défini
    if (this.userId) {
      try {
        const response = await fetch(`${this.config.consentUrl}/set`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            user_id: this.userId,
            consent_type: consentType,
            is_granted: granted,
            user_agent: navigator.userAgent,
            ip_address: this.config.anonymizeIp ? null : undefined
          })
        });
        
        if (!response.ok) {
          throw new Error(`Server responded with ${response.status}`);
        }
        
        this._debug(`Consent ${consentType} set to ${granted} on server`);
        
        // Si le consentement est accordé et que c'est le consentement analytics,
        // on peut initialiser le SDK s'il ne l'est pas déjà
        if (granted && consentType === 'analytics' && !this.initialized && this.userId) {
          this.init(this.userId);
        }
        
        return true;
      } catch (e) {
        this._error('Error setting consent on server:', e);
        return false;
      }
    } else {
      this._debug(`Consent ${consentType} set to ${granted} locally only`);
      return true;
    }
  }
  
  /**
   * Suit un événement de match proposé
   * 
   * @param {Object} matchData - Données du match
   * @param {string} matchData.matchId - ID du match
   * @param {number} matchData.matchScore - Score du match
   * @param {Object} matchData.matchParameters - Paramètres utilisés pour ce match
   * @param {number} matchData.alternativesCount - Nombre d'alternatives considérées
   * @param {Object} matchData.constraintSatisfaction - Niveau de satisfaction des contraintes
   * @returns {Promise<boolean>} - True si l'événement a été correctement traité
   */
  async trackMatchProposed(matchData) {
    if (!this._checkInitialized()) return false;
    
    const event = {
      event_id: this._generateEventId(),
      event_type: EventTypes.MATCH_PROPOSED,
      user_id: this.userId,
      session_id: this.sessionId,
      timestamp: new Date().toISOString(),
      client_timestamp: new Date().toISOString(),
      match_id: matchData.matchId,
      match_score: matchData.matchScore,
      match_parameters: matchData.matchParameters,
      alternatives_count: matchData.alternativesCount,
      constraint_satisfaction: matchData.constraintSatisfaction,
      ...this.deviceInfo
    };
    
    return this._queueEvent(event);
  }
  
  /**
   * Suit un événement de visualisation de match
   * 
   * @param {Object} viewData - Données de visualisation
   * @param {string} viewData.matchId - ID du match
   * @param {number} viewData.viewDurationSeconds - Durée de visualisation en secondes
   * @param {boolean} viewData.viewComplete - Si l'utilisateur a vu toutes les infos
   * @returns {Promise<boolean>} - True si l'événement a été correctement traité
   */
  async trackMatchViewed(viewData) {
    if (!this._checkInitialized()) return false;
    
    const event = {
      event_id: this._generateEventId(),
      event_type: EventTypes.MATCH_VIEWED,
      user_id: this.userId,
      session_id: this.sessionId,
      timestamp: new Date().toISOString(),
      client_timestamp: new Date().toISOString(),
      match_id: viewData.matchId,
      view_duration_seconds: viewData.viewDurationSeconds,
      view_complete: viewData.viewComplete,
      ...this.deviceInfo
    };
    
    return this._queueEvent(event);
  }
  
  /**
   * Suit un événement de décision (acceptation ou refus)
   * 
   * @param {Object} decisionData - Données de décision
   * @param {string} decisionData.matchId - ID du match
   * @param {boolean} decisionData.accepted - Si le match a été accepté
   * @param {number} decisionData.decisionTimeSeconds - Temps pris pour décider
   * @param {Array<string>} decisionData.reasons - Raisons de la décision
   * @returns {Promise<boolean>} - True si l'événement a été correctement traité
   */
  async trackMatchDecision(decisionData) {
    if (!this._checkInitialized()) return false;
    
    const event = {
      event_id: this._generateEventId(),
      event_type: decisionData.accepted ? EventTypes.MATCH_ACCEPTED : EventTypes.MATCH_REJECTED,
      user_id: this.userId,
      session_id: this.sessionId,
      timestamp: new Date().toISOString(),
      client_timestamp: new Date().toISOString(),
      match_id: decisionData.matchId,
      decision_time_seconds: decisionData.decisionTimeSeconds,
      reasons: decisionData.reasons,
      ...this.deviceInfo
    };
    
    return this._queueEvent(event);
  }
  
  /**
   * Suit un événement de feedback
   * 
   * @param {Object} feedbackData - Données de feedback
   * @param {string} feedbackData.matchId - ID du match
   * @param {number} feedbackData.rating - Note de 1 à 5
   * @param {string} feedbackData.feedbackText - Texte de feedback
   * @param {Object} feedbackData.specificAspects - Notation par aspect
   * @returns {Promise<boolean>} - True si l'événement a été correctement traité
   */
  async trackMatchFeedback(feedbackData) {
    if (!this._checkInitialized()) return false;
    
    const event = {
      event_id: this._generateEventId(),
      event_type: EventTypes.MATCH_FEEDBACK,
      user_id: this.userId,
      session_id: this.sessionId,
      timestamp: new Date().toISOString(),
      client_timestamp: new Date().toISOString(),
      match_id: feedbackData.matchId,
      rating: feedbackData.rating,
      feedback_text: feedbackData.feedbackText,
      specific_aspects: feedbackData.specificAspects,
      ...this.deviceInfo
    };
    
    return this._queueEvent(event);
  }
  
  /**
   * Suit un événement d'interaction après matching
   * 
   * @param {Object} interactionData - Données d'interaction
   * @param {string} interactionData.matchId - ID du match
   * @param {string} interactionData.interactionType - Type d'interaction
   * @param {number} interactionData.interactionCount - Nombre d'interactions
   * @param {Object} interactionData.details - Détails de l'interaction
   * @returns {Promise<boolean>} - True si l'événement a été correctement traité
   */
  async trackMatchInteraction(interactionData) {
    if (!this._checkInitialized()) return false;
    
    const event = {
      event_id: this._generateEventId(),
      event_type: EventTypes.MATCH_INTERACTION,
      user_id: this.userId,
      session_id: this.sessionId,
      timestamp: new Date().toISOString(),
      client_timestamp: new Date().toISOString(),
      match_id: interactionData.matchId,
      interaction_type: interactionData.interactionType,
      interaction_count: interactionData.interactionCount,
      details: interactionData.details,
      ...this.deviceInfo
    };
    
    return this._queueEvent(event);
  }
  
  /**
   * Suit un événement de complétion d'engagement
   * 
   * @param {Object} completionData - Données de complétion
   * @param {string} completionData.matchId - ID du match
   * @param {boolean} completionData.completed - Si l'engagement est terminé avec succès
   * @param {number} completionData.durationDays - Durée de l'engagement en jours
   * @param {number} completionData.completionRate - Niveau d'achèvement des objectifs (0-1)
   * @param {Object} completionData.successIndicators - Indicateurs de succès
   * @returns {Promise<boolean>} - True si l'événement a été correctement traité
   */
  async trackMatchCompletion(completionData) {
    if (!this._checkInitialized()) return false;
    
    const event = {
      event_id: this._generateEventId(),
      event_type: completionData.completed ? EventTypes.MATCH_COMPLETED : EventTypes.MATCH_ABANDONED,
      user_id: this.userId,
      session_id: this.sessionId,
      timestamp: new Date().toISOString(),
      client_timestamp: new Date().toISOString(),
      match_id: completionData.matchId,
      duration_days: completionData.durationDays,
      completion_rate: completionData.completionRate,
      success_indicators: completionData.successIndicators,
      ...this.deviceInfo
    };
    
    return this._queueEvent(event);
  }
  
  /**
   * Ajoute un événement à la file d'attente
   * 
   * @private
   * @param {Object} event - Événement à ajouter
   * @returns {boolean} - True si l'événement a été ajouté avec succès
   */
  _queueEvent(event) {
    // Vérifier le consentement
    if (!this._hasRequiredConsents(['analytics'])) {
      this._debug('Event not tracked - no consent:', event.event_type);
      return false;
    }
    
    // Ajouter à la file d'attente
    this.eventQueue.push(event);
    
    // Rafraîchir le timer de session
    this._refreshSessionTimer();
    
    this._debug(`Event ${event.event_type} queued`);
    
    // Envoyer si la file d'attente atteint la taille maximale
    if (this.eventQueue.length >= this.config.batchSize) {
      this.flush();
    }
    
    return true;
  }
  
  /**
   * Envoie tous les événements en attente au serveur
   * 
   * @param {boolean} useBeacon - Forcer l'utilisation de Navigator.sendBeacon (utile pour beforeunload)
   * @returns {Promise<boolean>} - True si les événements ont été envoyés avec succès
   */
  async flush(useBeacon = false) {
    if (this.eventQueue.length === 0) {
      return true;
    }
    
    const events = [...this.eventQueue];
    this.eventQueue = [];
    
    this._debug(`Flushing ${events.length} events`);
    
    // Utiliser Navigator.sendBeacon si disponible et demandé
    if ((useBeacon || this.config.useBeacon) && 
        typeof navigator !== 'undefined' && 
        navigator.sendBeacon) {
      
      try {
        const blob = new Blob([JSON.stringify({ events })], { type: 'application/json' });
        const success = navigator.sendBeacon(`${this.config.apiUrl}/track-batch`, blob);
        
        if (success) {
          this._debug('Events sent successfully using Beacon API');
          return true;
        } else {
          // Si sendBeacon échoue, on remet les événements dans la file d'attente
          this.eventQueue = [...events, ...this.eventQueue];
          this._error('Failed to send events using Beacon API');
          return false;
        }
      } catch (e) {
        // En cas d'erreur avec sendBeacon, on utilise fetch comme fallback
        this._error('Error using Beacon API, falling back to fetch:', e);
      }
    }
    
    // Utiliser fetch
    try {
      const response = await fetch(`${this.config.apiUrl}/track-batch`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ events })
      });
      
      if (!response.ok) {
        throw new Error(`Server responded with ${response.status}`);
      }
      
      this._debug('Events sent successfully using fetch');
      return true;
    } catch (e) {
      // En cas d'erreur, on remet les événements dans la file d'attente
      this.eventQueue = [...events, ...this.eventQueue];
      this._error('Error sending events:', e);
      return false;
    }
  }
  
  /**
   * Arrête le SDK et nettoie les ressources
   */
  destroy() {
    // Envoyer les événements restants
    this.flush(true);
    
    // Annuler les timers
    if (this.flushTimer) {
      clearInterval(this.flushTimer);
      this.flushTimer = null;
    }
    
    if (this.sessionTimer) {
      clearTimeout(this.sessionTimer);
      this.sessionTimer = null;
    }
    
    // Supprimer les écouteurs d'événements window
    if (typeof window !== 'undefined') {
      window.removeEventListener('beforeunload', () => this.flush(true));
    }
    
    this.initialized = false;
    this._debug('SDK destroyed');
  }
}

// Exporter les constantes et la classe
export { CommitmentTracking, EventTypes };

// Exporter une instance par défaut si dans un environnement browser
if (typeof window !== 'undefined') {
  window.CommitmentTracking = CommitmentTracking;
  window.CommitmentEventTypes = EventTypes;
  
  // Créer une instance par défaut
  window.commitmentTracker = new CommitmentTracking();
}
