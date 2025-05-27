/**
 * SuperSmartMatch Client JavaScript
 * Client officiel pour intégrer SuperSmartMatch avec votre front-end Nexten
 * 
 * @version 1.0.0
 * @author Nexten Team
 */

class SuperSmartMatchClient {
    /**
     * Initialise le client SuperSmartMatch
     * 
     * @param {Object} config - Configuration du client
     * @param {string} config.baseUrl - URL de base de l'API SuperSmartMatch
     * @param {string} config.apiKey - Clé API (optionnelle)
     * @param {number} config.timeout - Timeout en millisecondes (défaut: 30000)
     * @param {boolean} config.debug - Mode debug (défaut: false)
     */
    constructor(config = {}) {
        this.baseUrl = config.baseUrl || this._detectApiUrl();
        this.apiKey = config.apiKey || null;
        this.timeout = config.timeout || 30000;
        this.debug = config.debug || false;
        
        // Configuration par défaut
        this.defaultOptions = {
            algorithme: 'auto',
            limite: 10,
            details: true,
            explications: true,
            performance_tracking: true
        };
        
        // Cache pour les résultats
        this.cache = new Map();
        this.cacheTimeout = 5 * 60 * 1000; // 5 minutes
        
        this._log('SuperSmartMatch Client initialisé', { baseUrl: this.baseUrl });
    }
    
    /**
     * Détecte automatiquement l'URL de l'API
     * 
     * @private
     * @returns {string} URL de l'API détectée
     */
    _detectApiUrl() {
        // Ordre de priorité pour la détection
        const urls = [
            'http://localhost:5000',  // Développement local
            'https://api.nexten.fr',  // Production
            'https://supersmartmatch.herokuapp.com'  // Fallback
        ];
        
        // Vérifier si une URL est spécifiée dans les paramètres
        const urlParams = new URLSearchParams(window.location.search);
        const apiUrl = urlParams.get('apiUrl');
        if (apiUrl) {
            return apiUrl;
        }
        
        return urls[0]; // Par défaut en développement
    }
    
    /**
     * Effectue un matching entre un candidat et des offres
     * 
     * @param {Object} candidat - Données du candidat
     * @param {Array} offres - Liste des offres d'emploi
     * @param {Object} options - Options de matching (optionnel)
     * @returns {Promise<Object>} Résultats du matching
     */
    async match(candidat, offres, options = {}) {
        const mergedOptions = { ...this.defaultOptions, ...options };
        
        // Validation des données d'entrée
        this._validateMatchingData(candidat, offres);
        
        // Vérifier le cache
        const cacheKey = this._generateCacheKey(candidat, offres, mergedOptions);
        const cached = this._getFromCache(cacheKey);
        if (cached) {
            this._log('Résultat récupéré depuis le cache');
            return cached;
        }
        
        const requestData = {
            candidat,
            offres,
            options: mergedOptions
        };
        
        try {
            this._log('Envoi de la requête de matching', { 
                candidat: candidat.nom || 'Candidat anonyme',
                offres: offres.length,
                algorithme: mergedOptions.algorithme 
            });
            
            const result = await this._makeRequest('POST', '/api/v1/match', requestData);
            
            // Mettre en cache
            this._setCache(cacheKey, result);
            
            this._log('Matching réussi', { 
                resultats: result.resultats?.length || 0,
                algorithme: result.algorithme_utilise,
                temps: result.temps_execution 
            });
            
            return result;
            
        } catch (error) {
            this._log('Erreur lors du matching', error, 'error');
            throw new SuperSmartMatchError('Erreur lors du matching', error);
        }
    }
    
    /**
     * Compare tous les algorithmes sur les mêmes données
     * 
     * @param {Object} candidat - Données du candidat
     * @param {Array} offres - Liste des offres d'emploi
     * @returns {Promise<Object>} Résultats de comparaison
     */
    async compareAlgorithms(candidat, offres) {
        this._validateMatchingData(candidat, offres);
        
        const requestData = { candidat, offres };
        
        try {
            this._log('Comparaison des algorithmes', { offres: offres.length });
            
            const result = await this._makeRequest('POST', '/api/v1/compare', requestData);
            
            this._log('Comparaison réussie', { 
                algorithmes: Object.keys(result.comparaison?.performance_globale || {}).length 
            });
            
            return result;
            
        } catch (error) {
            this._log('Erreur lors de la comparaison', error, 'error');
            throw new SuperSmartMatchError('Erreur lors de la comparaison', error);
        }
    }
    
    /**
     * Explique la sélection d'algorithme pour des données données
     * 
     * @param {Object} candidat - Données du candidat
     * @param {Array} offres - Liste des offres d'emploi
     * @returns {Promise<Object>} Explication de la sélection
     */
    async explainSelection(candidat, offres) {
        this._validateMatchingData(candidat, offres);
        
        const requestData = { candidat, offres };
        
        try {
            const result = await this._makeRequest('POST', '/api/v1/explain', requestData);
            
            this._log('Explication générée', { 
                algorithme: result.explication?.algorithm_selected 
            });
            
            return result;
            
        } catch (error) {
            this._log('Erreur lors de l\'explication', error, 'error');
            throw new SuperSmartMatchError('Erreur lors de l\'explication', error);
        }
    }
    
    /**
     * Récupère les statistiques de performance
     * 
     * @returns {Promise<Object>} Statistiques de performance
     */
    async getPerformanceStats() {
        try {
            const result = await this._makeRequest('GET', '/api/v1/performance');
            
            this._log('Statistiques récupérées');
            
            return result;
            
        } catch (error) {
            this._log('Erreur lors de la récupération des stats', error, 'error');
            throw new SuperSmartMatchError('Erreur lors de la récupération des statistiques', error);
        }
    }
    
    /**
     * Liste tous les algorithmes disponibles
     * 
     * @returns {Promise<Object>} Liste des algorithmes
     */
    async getAvailableAlgorithms() {
        try {
            const result = await this._makeRequest('GET', '/api/v1/algorithms');
            
            this._log('Algorithmes disponibles récupérés', { 
                count: result.algorithms?.length || 0 
            });
            
            return result;
            
        } catch (error) {
            this._log('Erreur lors de la récupération des algorithmes', error, 'error');
            throw new SuperSmartMatchError('Erreur lors de la récupération des algorithmes', error);
        }
    }
    
    /**
     * Vérifie l'état du service
     * 
     * @returns {Promise<Object>} État du service
     */
    async healthCheck() {
        try {
            const result = await this._makeRequest('GET', '/api/v1/health');
            
            this._log('Health check réussi', { status: result.status });
            
            return result;
            
        } catch (error) {
            this._log('Health check échoué', error, 'error');
            throw new SuperSmartMatchError('Service indisponible', error);
        }
    }
    
    /**
     * Lance un benchmark des algorithmes
     * 
     * @param {Array} testCases - Cas de test pour le benchmark
     * @returns {Promise<Object>} Résultats du benchmark
     */
    async runBenchmark(testCases) {
        if (!Array.isArray(testCases) || testCases.length === 0) {
            throw new SuperSmartMatchError('Cases de test invalides pour le benchmark');
        }
        
        const requestData = { test_cases: testCases };
        
        try {
            this._log('Lancement du benchmark', { testCases: testCases.length });
            
            const result = await this._makeRequest('POST', '/api/v1/benchmark', requestData);
            
            this._log('Benchmark terminé');
            
            return result;
            
        } catch (error) {
            this._log('Erreur lors du benchmark', error, 'error');
            throw new SuperSmartMatchError('Erreur lors du benchmark', error);
        }
    }
    
    /**
     * Intégration facile avec les formulaires existants
     * 
     * @param {string} formSelector - Sélecteur CSS du formulaire
     * @param {Object} config - Configuration de l'intégration
     */
    integrateWithForm(formSelector, config = {}) {
        const form = document.querySelector(formSelector);
        if (!form) {
            throw new SuperSmartMatchError(`Formulaire non trouvé: ${formSelector}`);
        }
        
        const {
            candidatFieldsMapping = {},
            offresSource = null,
            onResults = null,
            onError = null,
            autoSubmit = false
        } = config;
        
        // Ajouter un bouton de matching s'il n'existe pas
        let matchButton = form.querySelector('.supersmartmatch-button');
        if (!matchButton) {
            matchButton = document.createElement('button');
            matchButton.type = 'button';
            matchButton.className = 'supersmartmatch-button btn btn-primary';
            matchButton.textContent = '🚀 Lancer SuperSmartMatch';
            form.appendChild(matchButton);
        }
        
        // Gestionnaire d'événement
        matchButton.addEventListener('click', async (e) => {
            e.preventDefault();
            
            try {
                // Extraire les données du candidat depuis le formulaire
                const candidat = this._extractCandidateFromForm(form, candidatFieldsMapping);
                
                // Obtenir les offres
                const offres = await this._getOffersData(offresSource);
                
                // Afficher un indicateur de chargement
                this._showLoading(matchButton);
                
                // Lancer le matching
                const results = await this.match(candidat, offres);
                
                // Gérer les résultats
                if (onResults) {
                    onResults(results);
                } else {
                    this._displayDefaultResults(results, form);
                }
                
            } catch (error) {
                if (onError) {
                    onError(error);
                } else {
                    this._displayError(error, form);
                }
            } finally {
                this._hideLoading(matchButton);
            }
        });
        
        // Auto-submit si configuré
        if (autoSubmit) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                matchButton.click();
            });
        }
        
        this._log('Intégration formulaire configurée', { formSelector });
    }
    
    /**
     * Utilitaire pour créer des données de test
     * 
     * @returns {Object} Données de test
     */
    static createTestData() {
        return {
            candidat: {
                nom: 'Jean Dupont',
                competences: ['JavaScript', 'React', 'Node.js', 'Python'],
                annees_experience: 3,
                adresse: 'Paris',
                salaire_souhaite: 45000,
                contrats_recherches: ['CDI'],
                mobilite: 'hybrid'
            },
            offres: [
                {
                    id: 'test_1',
                    titre: 'Développeur Full Stack',
                    competences: ['JavaScript', 'React', 'Node.js'],
                    localisation: 'Paris',
                    type_contrat: 'CDI',
                    salaire: '40-50K€'
                },
                {
                    id: 'test_2',
                    titre: 'Développeur Python',
                    competences: ['Python', 'Django', 'PostgreSQL'],
                    localisation: 'Lyon',
                    type_contrat: 'CDI',
                    salaire: '45-55K€'
                }
            ]
        };
    }
    
    // Méthodes privées
    
    /**
     * Effectue une requête HTTP vers l'API
     * 
     * @private
     * @param {string} method - Méthode HTTP
     * @param {string} endpoint - Endpoint de l'API
     * @param {Object} data - Données à envoyer
     * @returns {Promise<Object>} Réponse de l'API
     */
    async _makeRequest(method, endpoint, data = null) {
        const url = `${this.baseUrl}${endpoint}`;
        
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
            },
            signal: AbortSignal.timeout(this.timeout)
        };
        
        // Ajouter la clé API si disponible
        if (this.apiKey) {
            options.headers['Authorization'] = `Bearer ${this.apiKey}`;
        }
        
        // Ajouter les données pour les requêtes POST/PUT
        if (data && (method === 'POST' || method === 'PUT')) {
            options.body = JSON.stringify(data);
        }
        
        const response = await fetch(url, options);
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(`API Error ${response.status}: ${errorData.message || response.statusText}`);
        }
        
        return response.json();
    }
    
    /**
     * Valide les données de matching
     * 
     * @private
     * @param {Object} candidat - Données candidat
     * @param {Array} offres - Liste des offres
     */
    _validateMatchingData(candidat, offres) {
        if (!candidat || typeof candidat !== 'object') {
            throw new SuperSmartMatchError('Données candidat invalides');
        }
        
        if (!Array.isArray(offres) || offres.length === 0) {
            throw new SuperSmartMatchError('Liste d\'offres invalide ou vide');
        }
        
        // Validation basique des champs requis
        if (!candidat.competences && !candidat.skills) {
            console.warn('SuperSmartMatch: Aucune compétence trouvée pour le candidat');
        }
    }
    
    /**
     * Génère une clé de cache pour les résultats
     * 
     * @private
     * @param {Object} candidat - Données candidat
     * @param {Array} offres - Liste des offres
     * @param {Object} options - Options de matching
     * @returns {string} Clé de cache
     */
    _generateCacheKey(candidat, offres, options) {
        const key = JSON.stringify({
            candidat_hash: this._hashObject(candidat),
            offres_hash: this._hashObject(offres),
            options
        });
        return btoa(key).substring(0, 32); // Hash simple
    }
    
    /**
     * Hash simple d'un objet
     * 
     * @private
     * @param {Object} obj - Objet à hasher
     * @returns {string} Hash de l'objet
     */
    _hashObject(obj) {
        return JSON.stringify(obj).split('').reduce((hash, char) => {
            hash = ((hash << 5) - hash) + char.charCodeAt(0);
            return hash & hash;
        }, 0).toString();
    }
    
    /**
     * Récupère une valeur du cache
     * 
     * @private
     * @param {string} key - Clé de cache
     * @returns {Object|null} Valeur en cache ou null
     */
    _getFromCache(key) {
        const cached = this.cache.get(key);
        if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
            return cached.data;
        }
        return null;
    }
    
    /**
     * Met une valeur en cache
     * 
     * @private
     * @param {string} key - Clé de cache
     * @param {Object} data - Données à mettre en cache
     */
    _setCache(key, data) {
        this.cache.set(key, {
            data,
            timestamp: Date.now()
        });
        
        // Nettoyer le cache si trop volumineux
        if (this.cache.size > 100) {
            const firstKey = this.cache.keys().next().value;
            this.cache.delete(firstKey);
        }
    }
    
    /**
     * Extrait les données candidat depuis un formulaire
     * 
     * @private
     * @param {HTMLFormElement} form - Formulaire
     * @param {Object} mapping - Mapping des champs
     * @returns {Object} Données candidat
     */
    _extractCandidateFromForm(form, mapping) {
        const formData = new FormData(form);
        const candidat = {};
        
        // Mapping par défaut
        const defaultMapping = {
            'nom': 'nom',
            'prenom': 'prenom',
            'email': 'email',
            'competences': 'competences',
            'experience': 'annees_experience',
            'salaire': 'salaire_souhaite',
            'adresse': 'adresse',
            'mobilite': 'mobilite'
        };
        
        const finalMapping = { ...defaultMapping, ...mapping };
        
        // Extraire les données selon le mapping
        for (const [formField, candidatField] of Object.entries(finalMapping)) {
            const value = formData.get(formField);
            if (value) {
                // Traitement spécial pour certains champs
                if (candidatField === 'competences' && typeof value === 'string') {
                    candidat[candidatField] = value.split(',').map(s => s.trim());
                } else if (candidatField === 'annees_experience' || candidatField === 'salaire_souhaite') {
                    candidat[candidatField] = parseInt(value) || 0;
                } else {
                    candidat[candidatField] = value;
                }
            }
        }
        
        return candidat;
    }
    
    /**
     * Récupère les données d'offres
     * 
     * @private
     * @param {string|Array|Function} source - Source des offres
     * @returns {Promise<Array>} Liste des offres
     */
    async _getOffersData(source) {
        if (Array.isArray(source)) {
            return source;
        }
        
        if (typeof source === 'function') {
            return await source();
        }
        
        if (typeof source === 'string') {
            // URL vers des offres JSON
            const response = await fetch(source);
            return response.json();
        }
        
        // Fallback: utiliser des données de test
        return SuperSmartMatchClient.createTestData().offres;
    }
    
    /**
     * Affiche un indicateur de chargement
     * 
     * @private
     * @param {HTMLElement} button - Bouton à modifier
     */
    _showLoading(button) {
        button.disabled = true;
        button.originalText = button.textContent;
        button.textContent = '⏳ Matching en cours...';
        button.classList.add('loading');
    }
    
    /**
     * Cache l'indicateur de chargement
     * 
     * @private
     * @param {HTMLElement} button - Bouton à restaurer
     */
    _hideLoading(button) {
        button.disabled = false;
        button.textContent = button.originalText || '🚀 Lancer SuperSmartMatch';
        button.classList.remove('loading');
    }
    
    /**
     * Affiche les résultats par défaut
     * 
     * @private
     * @param {Object} results - Résultats du matching
     * @param {HTMLElement} container - Conteneur pour les résultats
     */
    _displayDefaultResults(results, container) {
        let resultsDiv = container.querySelector('.supersmartmatch-results');
        if (!resultsDiv) {
            resultsDiv = document.createElement('div');
            resultsDiv.className = 'supersmartmatch-results';
            container.appendChild(resultsDiv);
        }
        
        const html = `
            <div class="matching-results">
                <h3>📊 Résultats SuperSmartMatch</h3>
                <div class="matching-meta">
                    <span class="badge badge-info">Algorithme: ${results.algorithme_utilise}</span>
                    <span class="badge badge-secondary">Temps: ${results.temps_execution?.toFixed(3)}s</span>
                    <span class="badge badge-success">${results.resultats?.length || 0} résultats</span>
                </div>
                <div class="matching-list">
                    ${results.resultats?.map(result => `
                        <div class="matching-item" data-score="${result.score_global}">
                            <div class="matching-header">
                                <h4>${result.titre}</h4>
                                <span class="matching-score">${result.score_global}%</span>
                            </div>
                            <div class="matching-details">
                                ${Object.entries(result.scores_details || {}).map(([key, value]) => 
                                    `<span class="detail-badge">${key}: ${Math.round(value)}%</span>`
                                ).join('')}
                            </div>
                            ${result.explications?.skills ? `<p class="matching-explanation">${result.explications.skills}</p>` : ''}
                        </div>
                    `).join('') || '<p>Aucun résultat trouvé</p>'}
                </div>
            </div>
        `;
        
        resultsDiv.innerHTML = html;
    }
    
    /**
     * Affiche une erreur
     * 
     * @private
     * @param {Error} error - Erreur à afficher
     * @param {HTMLElement} container - Conteneur pour l'erreur
     */
    _displayError(error, container) {
        let errorDiv = container.querySelector('.supersmartmatch-error');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.className = 'supersmartmatch-error alert alert-danger';
            container.appendChild(errorDiv);
        }
        
        errorDiv.innerHTML = `
            <h4>❌ Erreur SuperSmartMatch</h4>
            <p>${error.message}</p>
            ${this.debug ? `<pre>${error.stack}</pre>` : ''}
        `;
    }
    
    /**
     * Fonction de logging
     * 
     * @private
     * @param {string} message - Message à logger
     * @param {*} data - Données additionnelles
     * @param {string} level - Niveau de log
     */
    _log(message, data = null, level = 'info') {
        if (!this.debug && level !== 'error') return;
        
        const logMethod = console[level] || console.log;
        if (data) {
            logMethod(`[SuperSmartMatch] ${message}`, data);
        } else {
            logMethod(`[SuperSmartMatch] ${message}`);
        }
    }
}

/**
 * Classe d'erreur personnalisée pour SuperSmartMatch
 */
class SuperSmartMatchError extends Error {
    constructor(message, originalError = null) {
        super(message);
        this.name = 'SuperSmartMatchError';
        this.originalError = originalError;
        
        if (originalError) {
            this.stack = originalError.stack;
        }
    }
}

// Export pour utilisation en module
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { SuperSmartMatchClient, SuperSmartMatchError };
}

// Disponible globalement pour utilisation directe
if (typeof window !== 'undefined') {
    window.SuperSmartMatchClient = SuperSmartMatchClient;
    window.SuperSmartMatchError = SuperSmartMatchError;
}
