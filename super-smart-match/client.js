/**
 * SuperSmartMatch JavaScript Client
 * Adaptateur pour intégrer facilement SuperSmartMatch dans vos pages front-end existantes
 */

class SuperSmartMatchClient {
    constructor(baseUrl = 'http://localhost:5060') {
        this.baseUrl = baseUrl;
        this.apiVersion = 'v1';
        this.defaultTimeout = 30000; // 30 secondes
    }

    /**
     * Vérifie la santé du service SuperSmartMatch
     * @returns {Promise<Object>} Statut du service
     */
    async health() {
        try {
            const response = await this._makeRequest('GET', '/api/health');
            return {
                success: true,
                data: response,
                available: true
            };
        } catch (error) {
            return {
                success: false,
                error: error.message,
                available: false
            };
        }
    }

    /**
     * Récupère la liste des algorithmes disponibles
     * @returns {Promise<Object>} Liste des algorithmes
     */
    async getAlgorithms() {
        try {
            const response = await this._makeRequest('GET', '/api/algorithms');
            return {
                success: true,
                algorithms: response.algorithms,
                count: response.total_count,
                default: response.default_algorithm
            };
        } catch (error) {
            return {
                success: false,
                error: error.message,
                algorithms: {}
            };
        }
    }

    /**
     * Exécute le matching principal
     * @param {Object} cvData - Données du CV
     * @param {Object} questionnaireData - Données du questionnaire
     * @param {Array} jobData - Liste des offres d'emploi
     * @param {Object} options - Options de matching
     * @returns {Promise<Object>} Résultats du matching
     */
    async match(cvData, questionnaireData, jobData, options = {}) {
        const {
            algorithm = 'auto',
            limit = 10,
            timeout = this.defaultTimeout
        } = options;

        try {
            // Validation des données
            const validation = this._validateMatchingData(cvData, questionnaireData, jobData);
            if (!validation.valid) {
                return {
                    success: false,
                    error: validation.error,
                    results: []
                };
            }

            const requestData = {
                cv_data: cvData,
                questionnaire_data: questionnaireData,
                job_data: jobData,
                algorithm: algorithm,
                limit: limit
            };

            const response = await this._makeRequest('POST', '/api/match', requestData, timeout);

            return {
                success: true,
                algorithm_used: response.algorithm_used,
                execution_time: response.execution_time,
                total_results: response.total_results,
                results: response.results,
                metadata: response.metadata,
                fallback_used: response.fallback_used || false
            };

        } catch (error) {
            return {
                success: false,
                error: error.message,
                results: [],
                fallback_used: false
            };
        }
    }

    /**
     * Exécute le matching avec sélection automatique de l'algorithme
     * @param {Object} cvData - Données du CV
     * @param {Object} questionnaireData - Données du questionnaire
     * @param {Array} jobData - Liste des offres d'emploi
     * @param {number} limit - Nombre maximum de résultats
     * @returns {Promise<Object>} Résultats du matching
     */
    async autoMatch(cvData, questionnaireData, jobData, limit = 10) {
        return this.match(cvData, questionnaireData, jobData, {
            algorithm: 'auto',
            limit: limit
        });
    }

    /**
     * Exécute le matching avec l'algorithme hybride (meilleure précision)
     * @param {Object} cvData - Données du CV
     * @param {Object} questionnaireData - Données du questionnaire
     * @param {Array} jobData - Liste des offres d'emploi
     * @param {number} limit - Nombre maximum de résultats
     * @returns {Promise<Object>} Résultats du matching
     */
    async hybridMatch(cvData, questionnaireData, jobData, limit = 10) {
        return this.match(cvData, questionnaireData, jobData, {
            algorithm: 'hybrid',
            limit: limit
        });
    }

    /**
     * Exécute tous les algorithmes et compare les résultats
     * @param {Object} cvData - Données du CV
     * @param {Object} questionnaireData - Données du questionnaire
     * @param {Array} jobData - Liste des offres d'emploi
     * @param {number} limit - Nombre maximum de résultats par algorithme
     * @returns {Promise<Object>} Comparaison détaillée
     */
    async compareAlgorithms(cvData, questionnaireData, jobData, limit = 5) {
        return this.match(cvData, questionnaireData, jobData, {
            algorithm: 'comparison',
            limit: limit,
            timeout: 60000 // Plus de temps pour la comparaison
        });
    }

    /**
     * Adapte les données du front-end Nexten au format SuperSmartMatch
     * @param {Object} frontendData - Données du front-end existant
     * @returns {Object} Données formatées pour SuperSmartMatch
     */
    adaptFrontendData(frontendData) {
        const adapted = {
            cv_data: {},
            questionnaire_data: {},
            job_data: []
        };

        // Adaptation des données CV
        if (frontendData.candidate) {
            const candidate = frontendData.candidate;
            
            adapted.cv_data = {
                competences: candidate.skills || candidate.competences || [],
                annees_experience: candidate.experience || candidate.annees_experience || 0,
                formation: candidate.education || candidate.formation || '',
                certifications: candidate.certifications || [],
                langues: candidate.languages || candidate.langues || []
            };
        }

        // Adaptation des données questionnaire
        if (frontendData.questionnaire) {
            const quest = frontendData.questionnaire;
            
            adapted.questionnaire_data = {
                contrats_recherches: quest.contract_types || quest.contrats_recherches || ['CDI'],
                adresse: quest.location || quest.adresse || '',
                salaire_souhaite: quest.salary_expectation || quest.salaire_souhaite || 0,
                mobilite: quest.mobility || quest.mobilite || 'on_site',
                disponibilite: quest.availability || quest.disponibilite || 'immediate',
                secteurs_interesse: quest.sectors || quest.secteurs_interesse || []
            };
        }

        // Adaptation des données d'emploi
        if (frontendData.jobs && Array.isArray(frontendData.jobs)) {
            adapted.job_data = frontendData.jobs.map((job, index) => ({
                id: job.id || index + 1,
                titre: job.title || job.titre || '',
                competences: job.skills || job.competences || [],
                type_contrat: job.contract_type || job.type_contrat || 'CDI',
                salaire: job.salary || job.salaire || '',
                localisation: job.location || job.localisation || '',
                politique_remote: job.remote_policy || job.politique_remote || 'on_site',
                experience_requise: job.required_experience || job.experience_requise || 0,
                description: job.description || '',
                entreprise: job.company || job.entreprise || ''
            }));
        }

        return adapted;
    }

    /**
     * Méthode de fallback utilisant l'ancien système de matching
     * @param {Object} cvData - Données du CV
     * @param {Object} questionnaireData - Données du questionnaire
     * @param {Array} jobData - Liste des offres d'emploi
     * @returns {Promise<Object>} Résultats du matching local
     */
    async fallbackMatch(cvData, questionnaireData, jobData) {
        console.warn('SuperSmartMatch non disponible, utilisation du fallback local');

        // Matching local simple en cas d'échec de SuperSmartMatch
        const results = jobData.map((job, index) => {
            const score = this._calculateSimpleScore(cvData, questionnaireData, job);
            return {
                ...job,
                matching_score: score,
                fallback: true
            };
        });

        // Tri par score décroissant
        results.sort((a, b) => b.matching_score - a.matching_score);

        return {
            success: true,
            algorithm_used: 'fallback_local',
            execution_time: 0.001,
            total_results: results.length,
            results: results,
            fallback_used: true,
            warning: 'SuperSmartMatch non disponible - matching local utilisé'
        };
    }

    /**
     * Méthode principale avec fallback automatique
     * @param {Object} frontendData - Données du front-end
     * @param {Object} options - Options de matching
     * @returns {Promise<Object>} Résultats du matching
     */
    async smartMatch(frontendData, options = {}) {
        try {
            // Vérifier la disponibilité de SuperSmartMatch
            const healthCheck = await this.health();
            
            if (!healthCheck.available) {
                console.warn('SuperSmartMatch non disponible, passage en mode fallback');
                const adapted = this.adaptFrontendData(frontendData);
                return this.fallbackMatch(
                    adapted.cv_data,
                    adapted.questionnaire_data,
                    adapted.job_data
                );
            }

            // Adapter les données du front-end
            const adapted = this.adaptFrontendData(frontendData);

            // Exécuter le matching
            const result = await this.match(
                adapted.cv_data,
                adapted.questionnaire_data,
                adapted.job_data,
                options
            );

            if (!result.success) {
                // Fallback en cas d'erreur
                console.warn('Erreur SuperSmartMatch, passage en mode fallback:', result.error);
                return this.fallbackMatch(
                    adapted.cv_data,
                    adapted.questionnaire_data,
                    adapted.job_data
                );
            }

            return result;

        } catch (error) {
            console.error('Erreur lors du matching:', error);
            
            // Fallback final
            const adapted = this.adaptFrontendData(frontendData);
            return this.fallbackMatch(
                adapted.cv_data,
                adapted.questionnaire_data,
                adapted.job_data
            );
        }
    }

    /**
     * Calcul de score simple pour le fallback
     * @private
     */
    _calculateSimpleScore(cvData, questionnaireData, job) {
        let score = 50; // Score de base

        // Compétences
        const cvSkills = (cvData.competences || []).map(s => s.toLowerCase());
        const jobSkills = (job.competences || []).map(s => s.toLowerCase());
        const commonSkills = cvSkills.filter(skill => jobSkills.includes(skill));
        
        if (jobSkills.length > 0) {
            score += (commonSkills.length / jobSkills.length) * 30;
        }

        // Type de contrat
        const wantedContracts = questionnaireData.contrats_recherches || ['CDI'];
        if (wantedContracts.includes(job.type_contrat)) {
            score += 10;
        }

        // Localisation (simple)
        if (questionnaireData.adresse && job.localisation) {
            const candidateCity = questionnaireData.adresse.toLowerCase();
            const jobCity = job.localisation.toLowerCase();
            if (jobCity.includes(candidateCity) || candidateCity.includes(jobCity)) {
                score += 10;
            }
        }

        return Math.min(100, Math.max(0, Math.round(score)));
    }

    /**
     * Validation des données de matching
     * @private
     */
    _validateMatchingData(cvData, questionnaireData, jobData) {
        if (!cvData || typeof cvData !== 'object') {
            return { valid: false, error: 'cv_data requis et doit être un objet' };
        }

        if (!questionnaireData || typeof questionnaireData !== 'object') {
            return { valid: false, error: 'questionnaire_data requis et doit être un objet' };
        }

        if (!Array.isArray(jobData) || jobData.length === 0) {
            return { valid: false, error: 'job_data doit être un tableau non vide' };
        }

        return { valid: true };
    }

    /**
     * Effectue une requête HTTP vers l'API
     * @private
     */
    async _makeRequest(method, endpoint, data = null, timeout = this.defaultTimeout) {
        const url = `${this.baseUrl}${endpoint}`;
        
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        };

        if (data) {
            options.body = JSON.stringify(data);
        }

        // Gestion du timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeout);
        options.signal = controller.signal;

        try {
            const response = await fetch(url, options);
            clearTimeout(timeoutId);

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`HTTP ${response.status}: ${errorText}`);
            }

            return await response.json();

        } catch (error) {
            clearTimeout(timeoutId);
            
            if (error.name === 'AbortError') {
                throw new Error(`Timeout après ${timeout}ms`);
            }
            
            throw error;
        }
    }
}

// Export pour Node.js et navigateur
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SuperSmartMatchClient;
} else {
    window.SuperSmartMatchClient = SuperSmartMatchClient;
}

// Exemple d'utilisation
if (typeof window !== 'undefined') {
    window.exampleUsage = async function() {
        const client = new SuperSmartMatchClient();

        // Données d'exemple compatibles avec votre front-end
        const frontendData = {
            candidate: {
                skills: ['Python', 'JavaScript', 'React'],
                experience: 3,
                education: 'Master Informatique'
            },
            questionnaire: {
                contract_types: ['CDI'],
                location: 'Paris',
                salary_expectation: 50000,
                mobility: 'hybrid'
            },
            jobs: [
                {
                    id: 1,
                    title: 'Développeur Full Stack',
                    skills: ['Python', 'React', 'Django'],
                    contract_type: 'CDI',
                    salary: '45K-55K€',
                    location: 'Paris'
                }
            ]
        };

        try {
            // Matching intelligent avec fallback automatique
            const result = await client.smartMatch(frontendData, {
                algorithm: 'auto',
                limit: 10
            });

            console.log('Résultats du matching:', result);
            return result;

        } catch (error) {
            console.error('Erreur:', error);
        }
    };
}
