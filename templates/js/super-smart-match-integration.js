/**
 * Intégration SuperSmartMatch pour les templates frontend existants
 * 
 * Ce fichier remplace les appels aux services individuels par SuperSmartMatch
 * Compatible avec candidate-questionnaire.html, client-questionnaire.html, etc.
 */

// Configuration SuperSmartMatch
const SUPERSMARTMATCH_CONFIG = {
    baseUrl: 'http://localhost:5070',
    fallbackUrls: {
        cvParser: 'http://localhost:5051',
        jobParser: 'http://localhost:5055',
        matching: 'http://localhost:5052',
        personalization: 'http://localhost:5060'
    },
    timeout: 30000,
    debug: window.location.hostname === 'localhost'
};

/**
 * Classe principale d'intégration SuperSmartMatch
 */
class SuperSmartMatchIntegration {
    constructor() {
        this.baseUrl = SUPERSMARTMATCH_CONFIG.baseUrl;
        this.isAvailable = false;
        this.init();
    }
    
    async init() {
        // Vérifier la disponibilité de SuperSmartMatch
        try {
            const response = await fetch(`${this.baseUrl}/health`, { 
                method: 'GET',
                timeout: 5000 
            });
            this.isAvailable = response.ok;
            
            if (this.isAvailable) {
                console.log('🚀 SuperSmartMatch disponible');
                this.showSuperSmartMatchStatus(true);
            } else {
                console.warn('⚠️ SuperSmartMatch non disponible, utilisation des services individuels');
                this.showSuperSmartMatchStatus(false);
            }
        } catch (error) {
            console.warn('⚠️ SuperSmartMatch non accessible:', error.message);
            this.isAvailable = false;
            this.showSuperSmartMatchStatus(false);
        }
    }
    
    /**
     * Affichage du statut SuperSmartMatch dans l'interface
     */
    showSuperSmartMatchStatus(available) {
        // Créer un indicateur de statut
        const statusDiv = document.createElement('div');
        statusDiv.id = 'supersmartmatch-status';
        statusDiv.style.cssText = `
            position: fixed;
            top: 10px;
            right: 10px;
            padding: 8px 12px;
            border-radius: 5px;
            font-size: 12px;
            font-weight: bold;
            z-index: 1000;
            color: white;
            background: ${available ? '#4CAF50' : '#FF9800'};
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        `;
        
        statusDiv.innerHTML = available ? 
            '🤖 SuperSmartMatch ACTIF' : 
            '⚙️ Services Individuels';
        
        document.body.appendChild(statusDiv);
        
        // Masquer après 3 secondes
        setTimeout(() => {
            statusDiv.style.opacity = '0.7';
            statusDiv.style.fontSize = '10px';
        }, 3000);
    }
    
    /**
     * Matching unifié - Point d'entrée principal
     */
    async performMatching(candidateData, jobsData, options = {}) {
        if (this.isAvailable) {
            return await this.superSmartMatchMatching(candidateData, jobsData, options);
        } else {
            return await this.fallbackMatching(candidateData, jobsData, options);
        }
    }
    
    /**
     * Matching via SuperSmartMatch
     */
    async superSmartMatchMatching(candidateData, jobsData, options = {}) {
        try {
            const payload = {
                candidate: candidateData,
                jobs: jobsData,
                algorithm: options.algorithm || 'auto',
                limit: options.limit || 10
            };
            
            console.log('🎯 Envoi vers SuperSmartMatch:', payload);
            
            const response = await fetch(`${this.baseUrl}/api/v1/match`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const result = await response.json();
            
            console.log('✅ Résultat SuperSmartMatch:', {
                algorithm: result.algorithm_used,
                matches: result.matches?.length,
                processingTime: result.processing_metadata?.total_execution_time
            });
            
            // Afficher les infos d'algorithme utilisé
            this.showAlgorithmInfo(result.algorithm_used, result.selection_reason);
            
            return result.matches || [];
            
        } catch (error) {
            console.error('❌ Erreur SuperSmartMatch:', error);
            // Fallback automatique
            console.log('🔄 Fallback vers services individuels...');
            return await this.fallbackMatching(candidateData, jobsData, options);
        }
    }
    
    /**
     * Matching fallback avec services individuels
     */
    async fallbackMatching(candidateData, jobsData, options = {}) {
        try {
            // Simulation du matching avec l'ancien système
            const response = await fetch(`${SUPERSMARTMATCH_CONFIG.fallbackUrls.matching}/api/match`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    cv_data: {
                        competences: candidateData.competences || [],
                        annees_experience: candidateData.annees_experience || 0
                    },
                    questionnaire_data: {
                        contrats_recherches: candidateData.contrats_recherches || ['CDI'],
                        adresse: candidateData.adresse || '',
                        salaire_min: candidateData.salaire_souhaite || 0
                    },
                    job_data: jobsData,
                    limit: options.limit || 10
                })
            });
            
            if (response.ok) {
                const result = await response.json();
                return result.matches || result;
            } else {
                throw new Error('Service de matching non disponible');
            }
            
        } catch (error) {
            console.error('❌ Erreur fallback matching:', error);
            // Matching basique en dernier recours
            return this.basicMatching(candidateData, jobsData);
        }
    }
    
    /**
     * Matching basique en cas d'échec total
     */
    basicMatching(candidateData, jobsData) {
        console.log('🔧 Utilisation du matching basique local');
        
        const candidateSkills = new Set((candidateData.competences || []).map(s => s.toLowerCase()));
        
        return jobsData.map((job, index) => {
            const jobSkills = new Set((job.competences || []).map(s => s.toLowerCase()));
            const commonSkills = [...candidateSkills].filter(skill => jobSkills.has(skill));
            
            const score = jobSkills.size > 0 ? 
                Math.round((commonSkills.length / jobSkills.size) * 100) : 
                50;
            
            return {
                ...job,
                matching_score: score,
                id: job.id || index + 1,
                algorithm_version: 'basic-fallback'
            };
        }).sort((a, b) => b.matching_score - a.matching_score);
    }
    
    /**
     * Affichage des informations d'algorithme utilisé
     */
    showAlgorithmInfo(algorithm, reasoning) {
        // Créer une notification temporaire
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #2196F3;
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            max-width: 300px;
            z-index: 1001;
            font-size: 14px;
            line-height: 1.4;
        `;
        
        notification.innerHTML = `
            <div style="font-weight: bold; margin-bottom: 5px;">
                🤖 Algorithme: ${algorithm}
            </div>
            <div style="font-size: 12px; opacity: 0.9;">
                ${Array.isArray(reasoning) ? reasoning.join(', ') : reasoning || 'Sélection automatique'}
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Animation d'apparition
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            notification.style.transition = 'transform 0.3s ease';
            notification.style.transform = 'translateX(0)';
        }, 100);
        
        // Masquer après 5 secondes
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => notification.remove(), 300);
        }, 5000);
    }
    
    /**
     * Recommandation d'algorithme
     */
    async recommendAlgorithm(candidateData, jobsData) {
        if (!this.isAvailable) {
            return { algorithm: 'enhanced', confidence: 70, reasoning: ['Service SuperSmartMatch non disponible'] };
        }
        
        try {
            const response = await fetch(`${this.baseUrl}/api/v1/recommend-algorithm`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    candidate: candidateData,
                    jobs: jobsData
                })
            });
            
            return await response.json();
        } catch (error) {
            console.warn('Erreur recommandation:', error);
            return { algorithm: 'enhanced', confidence: 50, reasoning: ['Erreur de recommandation'] };
        }
    }
}

/**
 * Intégration avec les formulaires existants
 */
class FormIntegration {
    constructor(superSmartMatch) {
        this.ssm = superSmartMatch;
        this.initFormEnhancements();
    }
    
    initFormEnhancements() {
        // Ajouter un sélecteur d'algorithme aux formulaires
        this.addAlgorithmSelector();
        
        // Améliorer les boutons de matching existants
        this.enhanceMatchingButtons();
        
        // Ajouter des indicateurs de performance
        this.addPerformanceIndicators();
    }
    
    addAlgorithmSelector() {
        const forms = document.querySelectorAll('form[id*="questionnaire"], form[id*="matching"]');
        
        forms.forEach(form => {
            if (form.querySelector('#algorithm-selector')) return; // Déjà ajouté
            
            const selectorDiv = document.createElement('div');
            selectorDiv.className = 'algorithm-selector-container';
            selectorDiv.innerHTML = `
                <div style="margin: 15px 0; padding: 15px; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #2196F3;">
                    <label style="font-weight: bold; color: #333; margin-bottom: 8px; display: block;">
                        🤖 Algorithme de matching:
                    </label>
                    <select id="algorithm-selector" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;">
                        <option value="auto">🎯 Sélection automatique (recommandé)</option>
                        <option value="enhanced">⚡ Enhanced - Précision maximale</option>
                        <option value="smart-match">🌍 SmartMatch - Géolocalisation avancée</option>
                        <option value="semantic">🧠 Sémantique - Technologies liées</option>
                        <option value="hybrid">🔬 Hybride - Combine plusieurs algorithmes</option>
                        <option value="original">🏃 Original - Rapidité</option>
                    </select>
                    <small style="color: #666; margin-top: 5px; display: block;">
                        💡 La sélection automatique choisit le meilleur algorithme selon votre profil
                    </small>
                </div>
            `;
            
            // Insérer avant le bouton de soumission
            const submitButton = form.querySelector('button[type="submit"], input[type="submit"]');
            if (submitButton) {
                submitButton.parentNode.insertBefore(selectorDiv, submitButton);
            } else {
                form.appendChild(selectorDiv);
            }
        });
    }
    
    enhanceMatchingButtons() {
        const buttons = document.querySelectorAll('button[onclick*="match"], button[id*="match"], .btn-matching');
        
        buttons.forEach(button => {
            const originalOnClick = button.onclick;
            
            button.onclick = async (event) => {
                event.preventDefault();
                
                // Ajouter un indicateur de chargement
                const originalText = button.textContent;
                button.textContent = '🔄 Analyse en cours...';
                button.disabled = true;
                
                try {
                    // Récupérer l'algorithme sélectionné
                    const algorithmSelector = document.getElementById('algorithm-selector');
                    const selectedAlgorithm = algorithmSelector ? algorithmSelector.value : 'auto';
                    
                    // Exécuter le matching original mais avec SuperSmartMatch
                    if (originalOnClick) {
                        await originalOnClick.call(button, event);
                    }
                    
                } finally {
                    button.textContent = originalText;
                    button.disabled = false;
                }
            };
        });
    }
    
    addPerformanceIndicators() {
        // Ajouter un panneau de métriques de performance
        if (document.getElementById('performance-panel')) return;
        
        const panel = document.createElement('div');
        panel.id = 'performance-panel';
        panel.style.cssText = `
            position: fixed;
            bottom: 80px;
            right: 20px;
            background: #fff;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            font-size: 12px;
            max-width: 250px;
            z-index: 1000;
            display: none;
        `;
        
        panel.innerHTML = `
            <div style="font-weight: bold; margin-bottom: 10px; color: #333;">
                📊 Métriques de Performance
            </div>
            <div id="metrics-content">Aucun matching effectué</div>
        `;
        
        document.body.appendChild(panel);
    }
    
    updatePerformanceMetrics(metrics) {
        const panel = document.getElementById('performance-panel');
        const content = document.getElementById('metrics-content');
        
        if (panel && content) {
            content.innerHTML = `
                <div>⏱️ Temps: ${metrics.processingTime || 'N/A'}s</div>
                <div>🤖 Algorithme: ${metrics.algorithm || 'N/A'}</div>
                <div>📈 Résultats: ${metrics.matches || 0}</div>
                <div>💾 Cache: ${metrics.fromCache ? 'Oui' : 'Non'}</div>
            `;
            
            panel.style.display = 'block';
            
            // Masquer après 10 secondes
            setTimeout(() => {
                panel.style.display = 'none';
            }, 10000);
        }
    }
}

/**
 * Instance globale SuperSmartMatch
 */
let globalSuperSmartMatch = null;
let globalFormIntegration = null;

/**
 * Initialisation automatique
 */
document.addEventListener('DOMContentLoaded', async () => {
    console.log('🚀 Initialisation SuperSmartMatch Integration');
    
    // Créer l'instance globale
    globalSuperSmartMatch = new SuperSmartMatchIntegration();
    
    // Attendre que SuperSmartMatch soit initialisé
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Initialiser l'intégration des formulaires
    globalFormIntegration = new FormIntegration(globalSuperSmartMatch);
    
    // Exposer les fonctions globalement pour compatibilité
    window.performSuperSmartMatching = async (candidateData, jobsData, options = {}) => {
        const result = await globalSuperSmartMatch.performMatching(candidateData, jobsData, options);
        
        // Mettre à jour les métriques
        if (globalFormIntegration && result.metadata) {
            globalFormIntegration.updatePerformanceMetrics({
                processingTime: result.metadata.processingTime,
                algorithm: result.metadata.algorithm,
                matches: result.length,
                fromCache: result.metadata.fromCache
            });
        }
        
        return result;
    };
    
    window.recommendAlgorithm = (candidateData, jobsData) => {
        return globalSuperSmartMatch.recommendAlgorithm(candidateData, jobsData);
    };
    
    console.log('✅ SuperSmartMatch Integration prêt');
});

/**
 * Export pour modules
 */
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        SuperSmartMatchIntegration,
        FormIntegration,
        SUPERSMARTMATCH_CONFIG
    };
}
