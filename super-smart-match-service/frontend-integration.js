/**
 * SuperSmartMatch Frontend Integration
 * Module d'intégration pour connecter le front-end existant à SuperSmartMatch
 * 
 * Auteur: Nexten Team
 * Version: 1.0.0
 */

class SuperSmartMatchClient {
    constructor(config = {}) {
        this.baseUrl = config.baseUrl || 'http://localhost:5070';
        this.defaultAlgorithm = config.defaultAlgorithm || 'auto';
        this.timeout = config.timeout || 30000;
        this.debug = config.debug || false;
        
        this.log('SuperSmartMatch Client initialisé', { baseUrl: this.baseUrl });
    }
    
    /**
     * Matching principal - Point d'entrée unifié
     */
    async match(candidateData, jobsData, options = {}) {
        const payload = {
            candidate: this.formatCandidateData(candidateData),
            jobs: this.formatJobsData(jobsData),
            algorithm: options.algorithm || this.defaultAlgorithm,
            limit: options.limit || 10,
            options: {
                performance_priority: options.performancePriority || 'balanced',
                accuracy_priority: options.accuracyPriority || 'high',
                max_processing_time: options.maxProcessingTime || this.timeout
            }
        };
        
        try {
            this.log('Envoi de la requête de matching', payload);
            
            const response = await this.request('POST', '/api/v1/match', payload);
            
            this.log('Réponse de matching reçue', {
                algorithm: response.algorithm_used,
                matches: response.matches?.length,
                processingTime: response.processing_metadata?.total_execution_time
            });
            
            return this.formatMatchingResponse(response);
            
        } catch (error) {
            this.error('Erreur lors du matching', error);
            throw new Error(`Erreur SuperSmartMatch: ${error.message}`);
        }
    }
    
    /**
     * Recommandation d'algorithme
     */
    async recommendAlgorithm(candidateData, jobsData) {
        const payload = {
            candidate: this.formatCandidateData(candidateData),
            jobs: this.formatJobsData(jobsData)
        };
        
        try {
            const response = await this.request('POST', '/api/v1/recommend-algorithm', payload);
            return response;
        } catch (error) {
            this.error('Erreur lors de la recommandation', error);
            return { algorithm: 'enhanced', confidence: 50, reasoning: ['Algorithme par défaut'] };
        }
    }
    
    /**
     * Comparaison d'algorithmes
     */
    async compareAlgorithms(candidateData, jobsData) {
        const payload = {
            candidate: this.formatCandidateData(candidateData),
            jobs: this.formatJobsData(jobsData)
        };
        
        try {
            return await this.request('POST', '/api/v1/compare', payload);
        } catch (error) {
            this.error('Erreur lors de la comparaison', error);
            throw error;
        }
    }
    
    /**
     * Informations sur les algorithmes disponibles
     */
    async getAlgorithms() {
        try {
            return await this.request('GET', '/algorithms');
        } catch (error) {
            this.error('Erreur lors de la récupération des algorithmes', error);
            return [];
        }
    }
    
    /**
     * Statistiques du service
     */
    async getStats() {
        try {
            return await this.request('GET', '/api/v1/stats');
        } catch (error) {
            this.error('Erreur lors de la récupération des stats', error);
            return null;
        }
    }
    
    /**
     * Health check
     */
    async healthCheck() {
        try {
            const response = await this.request('GET', '/health');
            return response.status === 'healthy';
        } catch (error) {
            return false;
        }
    }
    
    /**
     * Formatage des données candidat pour l'API
     */
    formatCandidateData(data) {
        return {
            competences: data.competences || data.skills || [],
            annees_experience: data.annees_experience || data.experience || data.yearsExperience || 0,
            adresse: data.adresse || data.address || data.location || '',
            contrats_recherches: data.contrats_recherches || data.contractTypes || ['CDI'],
            salaire_souhaite: data.salaire_souhaite || data.expectedSalary || data.salary || 0,
            mobilite: data.mobilite || data.mobility || 'local',
            disponibilite: data.disponibilite || data.availability || 'immediate',
            formation: data.formation || data.education || '',
            temps_trajet_max: data.temps_trajet_max || data.maxCommute || 60
        };
    }
    
    /**
     * Formatage des données d'offres pour l'API
     */
    formatJobsData(jobs) {
        return jobs.map((job, index) => ({
            id: job.id || index + 1,
            titre: job.titre || job.title || job.name || '',
            competences: job.competences || job.skills || job.requirements || [],
            localisation: job.localisation || job.location || job.address || '',
            type_contrat: job.type_contrat || job.contractType || job.contract || 'CDI',
            salaire: job.salaire || job.salary || '',
            entreprise: job.entreprise || job.company || '',
            experience: job.experience || job.experienceRequired || '',
            description: job.description || '',
            politique_remote: job.politique_remote || job.remotePolicy || 'office'
        }));
    }
    
    /**
     * Formatage de la réponse de matching
     */
    formatMatchingResponse(response) {
        return {
            success: response.success,
            algorithm: response.algorithm_used,
            processingTime: response.processing_metadata?.total_execution_time,
            totalJobs: response.processing_metadata?.jobs_analyzed,
            returnedJobs: response.processing_metadata?.results_returned,
            matches: response.matches || [],
            metadata: {
                selectionReason: response.selection_reason,
                qualityMetrics: response.quality_metrics,
                candidateSummary: response.candidate_summary,
                fromCache: response.from_cache || false
            }
        };
    }
    
    /**
     * Requête HTTP générique
     */
    async request(method, endpoint, data = null) {
        const url = `${this.baseUrl}${endpoint}`;
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            timeout: this.timeout
        };
        
        if (data && (method === 'POST' || method === 'PUT')) {
            options.body = JSON.stringify(data);
        }
        
        const response = await fetch(url, options);
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
        }
        
        return await response.json();
    }
    
    /**
     * Logging pour le debug
     */
    log(message, data = null) {
        if (this.debug) {
            console.log(`[SuperSmartMatch] ${message}`, data);
        }
    }
    
    error(message, error) {
        console.error(`[SuperSmartMatch Error] ${message}`, error);
    }
}

/**
 * Wrapper de compatibilité pour l'ancien système
 */
class CompatibilityWrapper {
    constructor(superSmartMatchClient) {
        this.client = superSmartMatchClient;
    }
    
    /**
     * Remplace les anciens appels de matching
     */
    async legacyMatch(cvData, questionnaireData, jobData, limit = 10) {
        const candidateData = {
            ...cvData,
            ...questionnaireData
        };
        
        const result = await this.client.match(candidateData, jobData, { limit });
        
        // Format de retour compatible avec l'ancien système
        return result.matches.map(match => ({
            ...match,
            matching_score: match.matching_score || 0
        }));
    }
    
    /**
     * Wrapper pour l'API de parsing CV (fallback)
     */
    async parseCV(file) {
        // Tentative d'utilisation du service CV Parser existant
        try {
            const formData = new FormData();
            formData.append('file', file);
            
            const response = await fetch('http://localhost:5051/api/parse-cv/', {
                method: 'POST',
                body: formData
            });
            
            return await response.json();
        } catch (error) {
            console.warn('Service CV Parser non disponible, utilisation du fallback');
            throw error;
        }
    }
    
    /**
     * Wrapper pour l'API d'analyse de job (fallback)
     */
    async analyzeJob(jobText) {
        try {
            const response = await fetch('http://localhost:5055/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: jobText })
            });
            
            return await response.json();
        } catch (error) {
            console.warn('Service Job Parser non disponible, utilisation du fallback');
            throw error;
        }
    }
}

/**
 * Configuration automatique pour l'intégration
 */
function autoConfigureSupermartMatch() {
    // Détection automatique de l'environnement
    const isDevelopment = window.location.hostname === 'localhost' || 
                         window.location.hostname === '127.0.0.1';
    
    const config = {
        baseUrl: isDevelopment ? 'http://localhost:5070' : 'https://api.nexten.com',
        defaultAlgorithm: 'auto',
        debug: isDevelopment,
        timeout: 30000
    };
    
    const client = new SuperSmartMatchClient(config);
    const wrapper = new CompatibilityWrapper(client);
    
    // Ajout au scope global pour faciliter l'intégration
    window.SuperSmartMatch = client;
    window.SuperSmartMatchCompat = wrapper;
    
    console.log('🚀 SuperSmartMatch configuré automatiquement', config);
    
    return { client, wrapper };
}

/**
 * Exemples d'utilisation
 */
const examples = {
    // Exemple basique
    async basicMatching() {
        const client = new SuperSmartMatchClient();
        
        const candidateData = {
            competences: ['Python', 'Django', 'React'],
            annees_experience: 3,
            adresse: 'Paris',
            contrats_recherches: ['CDI']
        };
        
        const jobsData = [{
            id: 1,
            titre: 'Développeur Full Stack',
            competences: ['Python', 'Django', 'React'],
            localisation: 'Paris',
            type_contrat: 'CDI'
        }];
        
        const result = await client.match(candidateData, jobsData);
        console.log('Résultats:', result);
    },
    
    // Exemple avec sélection d'algorithme
    async advancedMatching() {
        const client = new SuperSmartMatchClient({ debug: true });
        
        // D'abord, obtenir une recommandation
        const recommendation = await client.recommendAlgorithm(candidateData, jobsData);
        console.log('Algorithme recommandé:', recommendation.algorithm);
        
        // Utiliser l'algorithme recommandé
        const result = await client.match(candidateData, jobsData, {
            algorithm: recommendation.algorithm,
            performancePriority: 'accuracy'
        });
        
        return result;
    },
    
    // Exemple de comparaison
    async compareAllAlgorithms() {
        const client = new SuperSmartMatchClient();
        
        const comparison = await client.compareAlgorithms(candidateData, jobsData);
        console.log('Comparaison des algorithmes:', comparison);
        
        return comparison;
    }
};

// Export pour utilisation en module
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        SuperSmartMatchClient,
        CompatibilityWrapper,
        autoConfigureSupermartMatch,
        examples
    };
}

// Auto-configuration si chargé dans le navigateur
if (typeof window !== 'undefined') {
    document.addEventListener('DOMContentLoaded', autoConfigureSupermartMatch);
}
