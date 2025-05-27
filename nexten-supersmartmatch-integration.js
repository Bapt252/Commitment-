/**
 * SuperSmartMatch Integration pour Nexten
 * Module JavaScript pour intégrer SuperSmartMatch dans vos templates existants
 */

class NextenSuperSmartMatch {
    constructor(baseUrl = 'http://localhost:5060') {
        this.baseUrl = baseUrl;
        this.timeout = 30000;
        this.isHealthy = false;
        this.availableAlgorithms = [];
        
        // Initialisation automatique
        this.init();
    }

    async init() {
        try {
            await this.checkHealth();
            await this.loadAlgorithms();
            console.log('✅ SuperSmartMatch initialisé avec succès');
        } catch (error) {
            console.warn('⚠️ SuperSmartMatch non disponible:', error.message);
        }
    }

    // Vérifier la santé du service
    async checkHealth() {
        try {
            const response = await fetch(`${this.baseUrl}/api/health`, {
                method: 'GET',
                timeout: 5000
            });
            
            if (response.ok) {
                const data = await response.json();
                this.isHealthy = true;
                console.log(`✅ SuperSmartMatch connecté - ${data.algorithms_loaded} algorithmes disponibles`);
                return true;
            }
        } catch (error) {
            this.isHealthy = false;
            throw new Error('Service SuperSmartMatch non accessible');
        }
        return false;
    }

    // Charger les algorithmes disponibles
    async loadAlgorithms() {
        try {
            const response = await fetch(`${this.baseUrl}/api/algorithms`);
            const data = await response.json();
            this.availableAlgorithms = Object.keys(data.algorithms);
            return this.availableAlgorithms;
        } catch (error) {
            console.warn('Impossible de charger les algorithmes:', error);
            return [];
        }
    }

    // Fonction principale de matching
    async match(cvData, questionnaireData, jobsData, options = {}) {
        if (!this.isHealthy) {
            throw new Error('SuperSmartMatch non disponible - utilisez le fallback');
        }

        const payload = {
            cv_data: cvData,
            questionnaire_data: questionnaireData,
            job_data: jobsData,
            algorithm: options.algorithm || 'auto',
            limit: options.limit || 10
        };

        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), this.timeout);

            const response = await fetch(`${this.baseUrl}/api/match`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload),
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(`Matching failed: ${errorData.error || response.statusText}`);
            }

            const result = await response.json();
            
            // Post-traitement pour Nexten
            return this.formatForNexten(result);

        } catch (error) {
            if (error.name === 'AbortError') {
                throw new Error('Timeout - SuperSmartMatch met trop de temps à répondre');
            }
            console.error('SuperSmartMatch error:', error);
            throw error;
        }
    }

    // Formatage des résultats pour l'interface Nexten
    formatForNexten(apiResult) {
        const results = apiResult.results || [];
        
        return {
            // Métadonnées du matching
            metadata: {
                algorithm: apiResult.algorithm_used,
                executionTime: apiResult.execution_time,
                totalResults: apiResult.total_results,
                timestamp: new Date().toISOString(),
                success: true
            },
            
            // Résultats formatés pour votre interface
            matches: results.map((job, index) => ({
                rank: index + 1,
                jobId: job.id,
                title: job.titre || job.title,
                company: job.entreprise || job.company,
                location: job.localisation || job.location,
                matchingScore: job.matching_score,
                scorePercentage: job.matching_score,
                
                // Informations salariales
                salary: {
                    min: job.salaire_min || job.salary_min,
                    max: job.salaire_max || job.salary_max,
                    currency: '€'
                },
                
                // Autres infos
                contractType: job.type_contrat || job.contract_type,
                requiredExperience: job.experience_requise || job.required_experience,
                skills: job.competences || job.skills || [],
                sector: job.secteur || job.sector,
                remotePolicy: job.politique_remote || job.remote_policy,
                description: job.description,
                
                // Détails algorithmiques (pour debug)
                algorithmDetails: job.hybrid_details || job.score_details,
                
                // Classes CSS pour l'affichage
                scoreClass: this.getScoreClass(job.matching_score),
                scoreLabel: this.getScoreLabel(job.matching_score),
                
                // Badge de compatibilité
                compatibilityBadge: this.getCompatibilityBadge(job.matching_score)
            })),
            
            // Statistiques pour le dashboard
            statistics: {
                averageScore: results.length > 0 
                    ? Math.round(results.reduce((sum, job) => sum + job.matching_score, 0) / results.length)
                    : 0,
                excellentMatches: results.filter(job => job.matching_score >= 80).length,
                goodMatches: results.filter(job => job.matching_score >= 60 && job.matching_score < 80).length,
                averageMatches: results.filter(job => job.matching_score >= 40 && job.matching_score < 60).length,
                poorMatches: results.filter(job => job.matching_score < 40).length,
                
                // Répartition par secteur/localisation
                topSkills: this.getTopSkills(results),
                topLocations: this.getTopLocations(results)
            }
        };
    }

    // Classes CSS pour les scores
    getScoreClass(score) {
        if (score >= 80) return 'nexten-score-excellent';
        if (score >= 60) return 'nexten-score-good';
        if (score >= 40) return 'nexten-score-average';
        return 'nexten-score-low';
    }

    // Labels pour les scores
    getScoreLabel(score) {
        if (score >= 90) return 'Match parfait';
        if (score >= 80) return 'Excellent match';
        if (score >= 70) return 'Très bon match';
        if (score >= 60) return 'Bon match';
        if (score >= 40) return 'Match partiel';
        return 'Match faible';
    }

    // Badge de compatibilité
    getCompatibilityBadge(score) {
        if (score >= 80) return { text: 'RECOMMANDÉ', class: 'badge-success' };
        if (score >= 60) return { text: 'COMPATIBLE', class: 'badge-info' };
        if (score >= 40) return { text: 'À CONSIDÉRER', class: 'badge-warning' };
        return { text: 'PEU COMPATIBLE', class: 'badge-danger' };
    }

    // Analyse des compétences les plus demandées
    getTopSkills(results) {
        const skillCount = {};
        results.forEach(job => {
            (job.competences || job.skills || []).forEach(skill => {
                skillCount[skill] = (skillCount[skill] || 0) + 1;
            });
        });
        
        return Object.entries(skillCount)
            .sort(([,a], [,b]) => b - a)
            .slice(0, 5)
            .map(([skill, count]) => ({ skill, count }));
    }

    // Analyse des localisations les plus fréquentes
    getTopLocations(results) {
        const locationCount = {};
        results.forEach(job => {
            const location = job.localisation || job.location || 'Non spécifié';
            locationCount[location] = (locationCount[location] || 0) + 1;
        });
        
        return Object.entries(locationCount)
            .sort(([,a], [,b]) => b - a)
            .slice(0, 3)
            .map(([location, count]) => ({ location, count }));
    }

    // Algorithme de fallback si SuperSmartMatch n'est pas disponible
    fallbackMatch(cvData, questionnaireData, jobsData) {
        console.warn('🔄 Utilisation de l\'algorithme de fallback');
        
        const candidateSkills = new Set(cvData.competences || []);
        const candidateExperience = cvData.annees_experience || 0;
        
        const results = jobsData.map(job => {
            const jobSkills = new Set(job.competences || job.skills || []);
            const requiredExperience = job.experience_requise || job.required_experience || 0;
            
            // Score simple basé sur les compétences communes
            let score = 0;
            if (candidateSkills.size > 0 && jobSkills.size > 0) {
                const commonSkills = new Set([...candidateSkills].filter(x => jobSkills.has(x)));
                score = (commonSkills.size / jobSkills.size) * 100;
            }
            
            // Bonus/malus expérience
            if (candidateExperience >= requiredExperience) {
                score += 10;
            } else if (requiredExperience > candidateExperience) {
                score -= (requiredExperience - candidateExperience) * 5;
            }
            
            return {
                ...job,
                matching_score: Math.max(0, Math.min(100, Math.round(score)))
            };
        });
        
        // Trier par score
        results.sort((a, b) => b.matching_score - a.matching_score);
        
        return this.formatForNexten({
            algorithm_used: 'fallback',
            execution_time: 0.001,
            total_results: results.length,
            results: results
        });
    }

    // Méthode principale avec fallback automatique
    async matchWithFallback(cvData, questionnaireData, jobsData, options = {}) {
        try {
            // Essayer SuperSmartMatch d'abord
            return await this.match(cvData, questionnaireData, jobsData, options);
        } catch (error) {
            console.warn('SuperSmartMatch échoué, utilisation du fallback:', error.message);
            
            // Utiliser l'algorithme de fallback
            return this.fallbackMatch(cvData, questionnaireData, jobsData);
        }
    }
}

// Initialisation globale pour vos templates
window.NextenMatching = NextenSuperSmartMatch;

// Instance par défaut
window.nextenMatching = new NextenSuperSmartMatch();

// Export pour modules ES6 si nécessaire
if (typeof module !== 'undefined' && module.exports) {
    module.exports = NextenSuperSmartMatch;
}

/* 
=======================================
GUIDE D'UTILISATION DANS VOS TEMPLATES
=======================================

1. UTILISATION BASIQUE :
------------------------

// Dans vos pages de matching existantes
async function lancerMatching() {
    const cvData = {
        competences: ['Python', 'JavaScript', 'React'],
        annees_experience: 3,
        niveau_etudes: 'Master'
    };
    
    const questionnaireData = {
        adresse: 'Paris',
        salaire_souhaite: 45000,
        mobilite: 'hybrid'
    };
    
    const jobsData = [
        // Vos offres d'emploi...
    ];
    
    try {
        const result = await window.nextenMatching.matchWithFallback(
            cvData, 
            questionnaireData, 
            jobsData, 
            { algorithm: 'enhanced', limit: 10 }
        );
        
        // Afficher les résultats
        afficherResultats(result.matches);
        afficherStatistiques(result.statistics);
        
    } catch (error) {
        console.error('Erreur matching:', error);
    }
}

2. REMPLACEMENT D'ALGORITHMES EXISTANTS :
----------------------------------------

// Si vous avez déjà du code comme ça :
// const matches = ancien_algorithme_matching(cv, questionnaire, jobs);

// Remplacez par :
const result = await window.nextenMatching.matchWithFallback(cv, questionnaire, jobs);
const matches = result.matches;

3. AFFICHAGE DES RÉSULTATS :
---------------------------

function afficherResultats(matches) {
    matches.forEach(match => {
        console.log(`${match.rank}. ${match.title} - ${match.scoreLabel} (${match.scorePercentage}%)`);
        
        // Utiliser les classes CSS
        const element = document.createElement('div');
        element.className = `job-card ${match.scoreClass}`;
        element.innerHTML = `
            <h3>${match.title}</h3>
            <p>${match.company} - ${match.location}</p>
            <span class="${match.compatibilityBadge.class}">${match.compatibilityBadge.text}</span>
            <div class="score">${match.scorePercentage}%</div>
        `;
    });
}

4. CSS SUGGÉRÉ :
---------------

.nexten-score-excellent { background: #d4edda; border-left: 4px solid #28a745; }
.nexten-score-good { background: #cce5ff; border-left: 4px solid #007bff; }
.nexten-score-average { background: #fff3cd; border-left: 4px solid #ffc107; }
.nexten-score-low { background: #f8d7da; border-left: 4px solid #dc3545; }

.badge-success { background: #28a745; color: white; }
.badge-info { background: #17a2b8; color: white; }
.badge-warning { background: #ffc107; color: black; }
.badge-danger { background: #dc3545; color: white; }

*/
