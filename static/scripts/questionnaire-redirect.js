/**
 * NEXTEN - REDIRECTION AUTOMATIQUE VERS PAGE DE MATCHING
 * 🎯 Gestion de la redirection après soumission du questionnaire
 * ✅ Intégration avec le système existant
 * 📊 Transfert des données du questionnaire vers la page de matching
 */

console.log('🔄 Chargement du système de redirection...');

// ===== SYSTÈME DE REDIRECTION NEXTEN =====
window.NextenRedirectSystem = {
    // Configuration
    config: {
        matchingPageUrl: 'https://bapt252.github.io/Commitment-/templates/candidate-matching-improved.html',
        redirectDelay: 2000, // 2 secondes pour laisser le temps de lire le message de succès
        useLocalStorage: true, // Utiliser localStorage pour passer les données
        showRedirectMessage: true
    },

    // Initialisation
    init() {
        console.log('🚀 Initialisation du système de redirection...');
        
        // Intercepter la finalisation du questionnaire
        this.interceptQuestionnaireFinalization();
        
        // Configurer les événements
        this.setupRedirectEvents();
        
        console.log('✅ Système de redirection initialisé');
    },

    // Intercepter la soumission du questionnaire
    interceptQuestionnaireFinalization() {
        // Attendre que step4System soit disponible
        const waitForStep4System = () => {
            if (window.step4System) {
                this.enhanceStep4System();
            } else {
                setTimeout(waitForStep4System, 100);
            }
        };
        
        waitForStep4System();
    },

    // Améliorer le système étape 4 existant
    enhanceStep4System() {
        console.log('🔧 Amélioration du système étape 4 pour la redirection...');
        
        // Sauvegarder la méthode originale
        const originalFinalizeQuestionnaire = window.step4System.finalizeQuestionnaire;
        
        // Remplacer par notre version améliorée
        window.step4System.finalizeQuestionnaire = () => {
            console.log('🎯 Finalisation du questionnaire avec redirection...');
            
            // Valider les données d'abord
            const errors = window.step4System.validateStep4();
            
            if (errors.length > 0) {
                window.step4System.showValidationErrors(errors);
                return;
            }
            
            // Collecter toutes les données
            const allFormData = this.collectCompleteFormData();
            
            // Sauvegarder les données pour la page de matching
            if (this.config.useLocalStorage) {
                this.saveDataForMatching(allFormData);
            }
            
            // Afficher le message de succès avec redirection
            this.showSuccessWithRedirect(allFormData);
        };
        
        console.log('✅ Système étape 4 amélioré pour la redirection');
    },

    // Collecter toutes les données du questionnaire
    collectCompleteFormData() {
        console.log('📊 Collecte complète des données du questionnaire...');
        
        const data = {
            // Métadonnées
            timestamp: new Date().toISOString(),
            questionnaire_version: '3.0',
            
            // Étape 1 : Informations personnelles
            personal_info: {
                full_name: this.getFieldValue('full-name'),
                job_title: this.getFieldValue('job-title')
            },
            
            // Étape 2 : Mobilité et préférences
            mobility_preferences: {
                transport_methods: this.getCheckedValues('input[name="transport-method"]:checked'),
                travel_times: this.getTravelTimes(),
                address: this.getFieldValue('address'),
                address_coordinates: {
                    lat: this.getFieldValue('address-lat'),
                    lng: this.getFieldValue('address-lng'),
                    place_id: this.getFieldValue('address-place-id')
                },
                contract_preferences: this.getContractPreferences(),
                office_preference: this.getCheckedValue('input[name="office-preference"]:checked')
            },
            
            // Étape 3 : Motivations et secteurs
            motivations_sectors: {
                motivations: this.getMotivations(),
                selected_sectors: this.getSelectedSectors(),
                excluded_sectors: this.getExcludedSectors(),
                salary_range: this.getSalaryRange(),
                aspirations: this.getFieldValue('aspirations')
            },
            
            // Étape 4 : Disponibilité et situation
            availability_situation: window.step4System ? window.step4System.formData : {}
        };
        
        console.log('✅ Données collectées:', data);
        return data;
    },

    // Utilitaires pour récupérer les données
    getFieldValue(id) {
        const element = document.getElementById(id);
        return element ? element.value : '';
    },

    getCheckedValue(selector) {
        const element = document.querySelector(selector);
        return element ? element.value : '';
    },

    getCheckedValues(selector) {
        return Array.from(document.querySelectorAll(selector)).map(el => el.value);
    },

    getTravelTimes() {
        const times = {};
        const transportMethods = ['public-transport', 'vehicle', 'bike', 'walking'];
        
        transportMethods.forEach(method => {
            const timeField = document.querySelector(`input[name="travel-time-${method}"]`);
            if (timeField && timeField.value) {
                times[method] = parseInt(timeField.value);
            }
        });
        
        return times;
    },

    getContractPreferences() {
        // Récupérer les préférences de contrats depuis le système existant
        if (window.nextenQuestionnaire && window.nextenQuestionnaire.contractRanking) {
            return window.nextenQuestionnaire.contractRanking;
        }
        
        // Fallback
        return {
            ranking: this.getFieldValue('contract-ranking-order').split(',').filter(Boolean),
            types_selected: this.getFieldValue('contract-types-selected'),
            primary_choice: this.getFieldValue('contract-primary-choice')
        };
    },

    getMotivations() {
        // Récupérer les motivations depuis le système existant
        if (window.nextenQuestionnaire && window.nextenQuestionnaire.selectedMotivations) {
            return window.nextenQuestionnaire.selectedMotivations;
        }
        
        // Fallback
        return {
            selected: this.getFieldValue('hidden-motivations').split(',').filter(Boolean),
            ranking: this.getFieldValue('hidden-motivations-ranking').split(',').filter(Boolean),
            other_motivation: this.getFieldValue('autre-motivation-text')
        };
    },

    getSelectedSectors() {
        if (window.nextenQuestionnaire && window.nextenQuestionnaire.selectedSecteurs) {
            return window.nextenQuestionnaire.selectedSecteurs;
        }
        
        return this.getFieldValue('hidden-secteurs').split(',').filter(Boolean);
    },

    getExcludedSectors() {
        if (window.nextenQuestionnaire && window.nextenQuestionnaire.selectedRedhibitoires) {
            return window.nextenQuestionnaire.selectedRedhibitoires;
        }
        
        return this.getFieldValue('hidden-secteurs-redhibitoires').split(',').filter(Boolean);
    },

    getSalaryRange() {
        return {
            min: this.getFieldValue('salary-min') || this.getFieldValue('hidden-salary-min'),
            max: this.getFieldValue('salary-max') || this.getFieldValue('hidden-salary-max')
        };
    },

    // Sauvegarder les données pour la page de matching
    saveDataForMatching(data) {
        try {
            // Sauvegarder dans localStorage
            localStorage.setItem('nexten_questionnaire_data', JSON.stringify(data));
            localStorage.setItem('nexten_questionnaire_timestamp', Date.now().toString());
            
            // Sauvegarder un résumé pour un accès rapide
            const summary = {
                name: data.personal_info.full_name,
                job_title: data.personal_info.job_title,
                salary_min: data.motivations_sectors.salary_range.min,
                salary_max: data.motivations_sectors.salary_range.max,
                contract_preferences: data.mobility_preferences.contract_preferences,
                location: data.mobility_preferences.address,
                completed_at: data.timestamp
            };
            
            localStorage.setItem('nexten_candidate_summary', JSON.stringify(summary));
            
            console.log('✅ Données sauvegardées pour la page de matching');
            
            // Nettoyer les anciennes données (garder seulement les 3 dernières)
            this.cleanupOldData();
            
        } catch (error) {
            console.error('❌ Erreur lors de la sauvegarde:', error);
        }
    },

    // Nettoyer les anciennes données
    cleanupOldData() {
        try {
            const keys = Object.keys(localStorage);
            const nextenKeys = keys.filter(key => key.startsWith('nexten_questionnaire_'));
            
            if (nextenKeys.length > 6) { // 3 questionnaires max * 2 clés par questionnaire
                // Trier par timestamp et supprimer les plus anciens
                const dataKeys = nextenKeys.filter(key => key.includes('_data'));
                const timestamps = dataKeys.map(key => {
                    const data = JSON.parse(localStorage.getItem(key));
                    return {key, timestamp: data.timestamp};
                }).sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
                
                // Supprimer les plus anciens
                const toRemove = timestamps.slice(0, -3);
                toRemove.forEach(item => {
                    localStorage.removeItem(item.key);
                    localStorage.removeItem(item.key.replace('_data', '_timestamp'));
                });
            }
        } catch (error) {
            console.warn('⚠️ Erreur lors du nettoyage:', error);
        }
    },

    // Afficher le message de succès avec redirection
    showSuccessWithRedirect(data) {
        console.log('🎉 Affichage du message de succès avec redirection...');
        
        // Supprimer les anciens messages
        document.querySelectorAll('.step4-success-message, .nexten-redirect-message').forEach(msg => msg.remove());
        
        // Créer le message de succès avec redirection
        const successContainer = document.createElement('div');
        successContainer.className = 'nexten-redirect-message';
        successContainer.style.cssText = `
            position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
            background: linear-gradient(135deg, #10b981, #059669); color: white;
            padding: 32px; border-radius: 16px; text-align: center;
            box-shadow: 0 20px 40px rgba(0,0,0,0.3); z-index: 10000;
            max-width: 450px; width: 90%;
        `;
        
        successContainer.innerHTML = `
            <div style="font-size: 48px; margin-bottom: 16px;">
                <i class="fas fa-check-circle"></i>
            </div>
            <h3 style="margin: 0 0 8px 0; font-size: 24px;">Questionnaire complété !</h3>
            <p style="margin: 0 0 16px 0; opacity: 0.9;">
                Merci ${data.personal_info.full_name} ! Votre profil a été enregistré avec succès.
            </p>
            <div style="background: rgba(255,255,255,0.2); padding: 16px; border-radius: 12px; margin: 16px 0;">
                <div style="display: flex; align-items: center; justify-content: center; gap: 8px; margin-bottom: 8px;">
                    <i class="fas fa-arrow-right" style="font-size: 16px;"></i>
                    <strong>Redirection automatique en cours...</strong>
                </div>
                <div class="redirect-countdown" style="font-size: 24px; font-weight: bold;">
                    <span id="countdown-number">${Math.ceil(this.config.redirectDelay / 1000)}</span>
                </div>
                <p style="margin: 8px 0 0 0; font-size: 14px; opacity: 0.8;">
                    Vous allez être redirigé vers votre page de matching personnalisée
                </p>
            </div>
            <button onclick="window.NextenRedirectSystem.redirectNow()" 
                    style="background: white; color: #059669; border: none; padding: 12px 24px; 
                           border-radius: 8px; font-weight: 600; cursor: pointer; font-size: 14px;
                           transition: all 0.2s ease;">
                Accéder maintenant à mes recommandations
            </button>
        `;
        
        document.body.appendChild(successContainer);
        
        // Animation d'entrée
        successContainer.style.opacity = '0';
        successContainer.style.transform = 'translate(-50%, -50%) scale(0.8)';
        
        setTimeout(() => {
            successContainer.style.transition = 'all 0.3s ease-out';
            successContainer.style.opacity = '1';
            successContainer.style.transform = 'translate(-50%, -50%) scale(1)';
        }, 100);
        
        // Démarrer le compte à rebours
        this.startCountdown();
        
        // Programmer la redirection automatique
        setTimeout(() => {
            this.redirectToMatching();
        }, this.config.redirectDelay);
    },

    // Démarrer le compte à rebours
    startCountdown() {
        let timeLeft = Math.ceil(this.config.redirectDelay / 1000);
        const countdownElement = document.getElementById('countdown-number');
        
        const countdownTimer = setInterval(() => {
            timeLeft--;
            if (countdownElement) {
                countdownElement.textContent = timeLeft;
            }
            
            if (timeLeft <= 0) {
                clearInterval(countdownTimer);
            }
        }, 1000);
    },

    // Redirection immédiate (bouton)
    redirectNow() {
        console.log('🚀 Redirection immédiate demandée');
        this.redirectToMatching();
    },

    // Effectuer la redirection
    redirectToMatching() {
        console.log('🎯 Redirection vers la page de matching...');
        
        try {
            // Construire l'URL avec paramètres optionnels
            let targetUrl = this.config.matchingPageUrl;
            
            // Ajouter des paramètres URL pour un accès rapide aux données
            const params = new URLSearchParams();
            params.set('from', 'questionnaire');
            params.set('timestamp', Date.now().toString());
            
            // Ajouter quelques informations de base (non sensibles)
            const summary = JSON.parse(localStorage.getItem('nexten_candidate_summary') || '{}');
            if (summary.name) {
                params.set('candidate', encodeURIComponent(summary.name.split(' ')[0])); // Prénom seulement
            }
            
            targetUrl += '?' + params.toString();
            
            // Redirection
            window.location.href = targetUrl;
            
        } catch (error) {
            console.error('❌ Erreur lors de la redirection:', error);
            
            // Fallback simple
            window.location.href = this.config.matchingPageUrl;
        }
    },

    // Configuration des événements additionnels
    setupRedirectEvents() {
        // Écouter les modifications de configuration
        window.addEventListener('nexten:configure-redirect', (event) => {
            const newConfig = event.detail;
            this.config = { ...this.config, ...newConfig };
            console.log('🔧 Configuration de redirection mise à jour:', this.config);
        });
        
        // Écouter les demandes de redirection externe
        window.addEventListener('nexten:trigger-redirect', () => {
            this.redirectToMatching();
        });
    }
};

// ===== FONCTIONS UTILITAIRES GLOBALES =====

// Configurer la redirection depuis l'extérieur
window.configureNextenRedirect = (config) => {
    window.dispatchEvent(new CustomEvent('nexten:configure-redirect', { detail: config }));
};

// Déclencher la redirection depuis l'extérieur
window.triggerNextenRedirect = () => {
    window.dispatchEvent(new CustomEvent('nexten:trigger-redirect'));
};

// ===== INITIALISATION AUTOMATIQUE =====
function initializeRedirectSystem() {
    console.log('🚀 Initialisation du système de redirection...');
    
    const checkAndInit = () => {
        // Vérifier que le questionnaire est présent
        const questionnaireForm = document.getElementById('questionnaire-form');
        
        if (questionnaireForm) {
            // Initialiser le système de redirection
            window.NextenRedirectSystem.init();
            
            console.log('✅ Système de redirection complètement initialisé');
        } else {
            console.warn('⚠️ Formulaire questionnaire non trouvé, nouvelle tentative...');
            setTimeout(checkAndInit, 500);
        }
    };
    
    // Initialiser après chargement
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            setTimeout(checkAndInit, 500);
        });
    } else {
        setTimeout(checkAndInit, 300);
    }
}

// Lancer l'initialisation
initializeRedirectSystem();

console.log('✅ Script de redirection Nexten chargé avec succès');
