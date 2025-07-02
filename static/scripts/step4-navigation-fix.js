// ===== CORRECTION NAVIGATION ÉTAPE 4 - NEXTEN QUESTIONNAIRE =====
// Fichier de correction spécifique pour résoudre les problèmes de navigation vers l'étape 4
// 🎯 Objectif: Corriger les conflits JavaScript et assurer la navigation fluide vers l'étape 4
// Version: 2.0 - Solution complète et sécurisée

console.log('🚀 Chargement de la correction navigation étape 4...');

// ===== SYSTÈME DE CORRECTION PRINCIPAL =====
window.nextenStep4Fix = {
    
    // Configuration
    config: {
        debug: true,
        maxRetries: 5,
        retryDelay: 200,
        forceStep4: true
    },
    
    // État de l'initialisation
    state: {
        initialized: false,
        step4Ready: false,
        navigationFixed: false,
        retryCount: 0
    },
    
    // Initialisation principale
    init() {
        if (this.state.initialized) {
            console.log('⚠️ Correction déjà initialisée');
            return;
        }
        
        console.log('🔧 Initialisation de la correction étape 4...');
        
        // Sécuriser l'exécution pour éviter les call stack
        this.safeInit();
    },
    
    // Initialisation sécurisée
    safeInit() {
        try {
            // Arrêter tous les scripts conflictuels
            this.stopConflictingScripts();
            
            // Corriger la navigation
            this.fixNavigation();
            
            // Assurer le contenu de l'étape 4
            this.ensureStep4Content();
            
            // Corriger les événements
            this.fixEventListeners();
            
            this.state.initialized = true;
            console.log('✅ Correction étape 4 initialisée avec succès');
            
        } catch (error) {
            console.error('❌ Erreur lors de l\'initialisation:', error);
            this.retryInit();
        }
    },
    
    // Arrêter les scripts conflictuels
    stopConflictingScripts() {
        console.log('🛑 Arrêt des scripts conflictuels...');
        
        // Empêcher les boucles infinies des scripts existants
        if (window.step4System && typeof window.step4System.init === 'function') {
            const originalInit = window.step4System.init;
            window.step4System.init = function() {
                console.log('🔒 Script step4System bloqué pour éviter les conflits');
                return;
            };
        }
        
        // Nettoyer les event listeners problématiques
        this.cleanupEventListeners();
    },
    
    // Nettoyer les event listeners
    cleanupEventListeners() {
        // Remplacer les boutons par des clones pour supprimer tous les événements
        const nextStep3Button = document.getElementById('next-step3');
        if (nextStep3Button) {
            const newButton = nextStep3Button.cloneNode(true);
            nextStep3Button.parentNode.replaceChild(newButton, nextStep3Button);
        }
    },
    
    // Corriger la navigation
    fixNavigation() {
        console.log('🔄 Correction de la navigation...');
        
        // Corriger le bouton de l'étape 3 vers l'étape 4
        const nextStep3Button = document.getElementById('next-step3');
        if (nextStep3Button) {
            nextStep3Button.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.navigateToStep4();
            });
        }
        
        // Ajouter la navigation directe sur l'étape 4 dans la barre de progression
        const step4Progress = document.getElementById('step4');
        if (step4Progress) {
            step4Progress.style.cursor = 'pointer';
            step4Progress.addEventListener('click', () => {
                this.navigateToStep4();
            });
        }
        
        this.state.navigationFixed = true;
    },
    
    // Navigation vers l'étape 4
    navigateToStep4() {
        console.log('➡️ Navigation vers étape 4...');
        
        try {
            // Masquer toutes les étapes
            document.querySelectorAll('.form-step').forEach(step => {
                step.style.display = 'none';
            });
            
            // Afficher l'étape 4
            const step4 = document.getElementById('form-step4');
            if (step4) {
                step4.style.display = 'block';
                
                // Mettre à jour la barre de progression
                this.updateProgressBar(4);
                
                // Scroll vers le haut
                window.scrollTo({ top: 0, behavior: 'smooth' });
                
                console.log('✅ Navigation vers étape 4 réussie');
                
                // Vérifier et compléter le contenu si nécessaire
                setTimeout(() => {
                    this.ensureStep4Content();
                }, 100);
                
            } else {
                console.error('❌ Élément form-step4 non trouvé');
            }
            
        } catch (error) {
            console.error('❌ Erreur navigation vers étape 4:', error);
        }
    },
    
    // Mettre à jour la barre de progression
    updateProgressBar(currentStep) {
        const steps = document.querySelectorAll('.step');
        steps.forEach((step, index) => {
            step.classList.remove('active');
            
            if (index < currentStep - 1) {
                step.classList.add('completed');
            } else {
                step.classList.remove('completed');
            }
            
            if (index === currentStep - 1) {
                step.classList.add('active');
            }
        });
        
        // Mettre à jour la ligne de progression
        const progressLine = document.getElementById('stepper-progress');
        if (progressLine) {
            const percentage = ((currentStep - 1) / 3) * 100;
            progressLine.style.width = `${percentage}%`;
        }
    },
    
    // Assurer le contenu de l'étape 4
    ensureStep4Content() {
        const step4Container = document.getElementById('form-step4');
        if (!step4Container) return;
        
        // Vérifier si le contenu complet est présent
        const hasCompleteContent = step4Container.innerHTML.includes('Quand cherchez-vous à prendre un poste');
        
        if (!hasCompleteContent) {
            console.log('📝 Injection du contenu complet étape 4...');
            this.injectCompleteStep4Content();
        } else {
            console.log('✅ Contenu étape 4 déjà complet');
        }
        
        // Configurer les événements de l'étape 4
        this.setupStep4Events();
        
        this.state.step4Ready = true;
    },
    
    // Injecter le contenu complet de l'étape 4
    injectCompleteStep4Content() {
        const step4Container = document.getElementById('form-step4');
        if (!step4Container) return;
        
        const completeContent = `
            <h2 class="form-section-title">🚀 Disponibilité & Situation</h2>
            <p class="step-description">
                Dernière étape ! Précisez votre situation actuelle et vos attentes pour finaliser votre profil candidat
            </p>

            <!-- Question 1: Timing -->
            <div class="step4-container">
                <div class="step4-question">
                    <h3 class="step4-question-title">
                        <i class="fas fa-calendar-check"></i>
                        1) Quand cherchez-vous à prendre un poste ?
                    </h3>
                    
                    <div class="step4-options" id="timing-options">
                        <div class="step4-option" data-value="immediat" data-question="timing">
                            <div class="step4-option-content">
                                <div class="step4-option-radio"></div>
                                <div class="step4-option-text">Immédiatement</div>
                            </div>
                        </div>
                        
                        <div class="step4-option" data-value="1mois" data-question="timing">
                            <div class="step4-option-content">
                                <div class="step4-option-radio"></div>
                                <div class="step4-option-text">Dans 1 mois</div>
                            </div>
                        </div>
                        
                        <div class="step4-option" data-value="2mois" data-question="timing">
                            <div class="step4-option-content">
                                <div class="step4-option-radio"></div>
                                <div class="step4-option-text">Dans 2 mois</div>
                            </div>
                        </div>
                        
                        <div class="step4-option" data-value="3mois" data-question="timing">
                            <div class="step4-option-content">
                                <div class="step4-option-radio"></div>
                                <div class="step4-option-text">Dans 3 mois ou plus</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Question 2: Situation d'emploi -->
            <div class="step4-container">
                <div class="step4-question">
                    <h3 class="step4-question-title">
                        <i class="fas fa-briefcase"></i>
                        2) Êtes-vous actuellement en poste ?
                    </h3>
                    
                    <div class="step4-options" id="employment-status-options">
                        <div class="step4-option" data-value="oui" data-question="employment-status">
                            <div class="step4-option-content">
                                <div class="step4-option-radio"></div>
                                <div class="step4-option-text">OUI - Je suis actuellement en poste</div>
                            </div>
                        </div>
                        
                        <div class="step4-option" data-value="non" data-question="employment-status">
                            <div class="step4-option-content">
                                <div class="step4-option-radio"></div>
                                <div class="step4-option-text">NON - Je recherche activement un emploi</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Question 3: Préférences de travail -->
            <div class="step4-container">
                <div class="step4-question">
                    <h3 class="step4-question-title">
                        <i class="fas fa-laptop-house"></i>
                        3) Vos préférences de travail
                    </h3>
                    
                    <div class="step4-input-group">
                        <label class="step4-input-label">
                            Quel mode de travail préférez-vous ? (Plusieurs choix possibles)
                        </label>
                        <div class="step4-checkbox-group" id="work-preferences">
                            <div class="step4-checkbox-option" data-value="presentiel">
                                <div class="step4-checkbox">
                                    <i class="fas fa-check"></i>
                                </div>
                                <div class="step4-checkbox-text">100% présentiel sur site</div>
                            </div>
                            <div class="step4-checkbox-option" data-value="hybride">
                                <div class="step4-checkbox">
                                    <i class="fas fa-check"></i>
                                </div>
                                <div class="step4-checkbox-text">Travail hybride (mix présentiel/télétravail)</div>
                            </div>
                            <div class="step4-checkbox-option" data-value="remote">
                                <div class="step4-checkbox">
                                    <i class="fas fa-check"></i>
                                </div>
                                <div class="step4-checkbox-text">100% télétravail</div>
                            </div>
                            <div class="step4-checkbox-option" data-value="flexible">
                                <div class="step4-checkbox">
                                    <i class="fas fa-check"></i>
                                </div>
                                <div class="step4-checkbox-text">Horaires flexibles</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Question 4: Mobilité géographique -->
            <div class="step4-container">
                <div class="step4-question">
                    <h3 class="step4-question-title">
                        <i class="fas fa-map-marked-alt"></i>
                        4) Accepteriez-vous de déménager pour un poste ?
                    </h3>
                    
                    <div class="step4-options" id="relocation-options">
                        <div class="step4-option" data-value="oui" data-question="relocation">
                            <div class="step4-option-content">
                                <div class="step4-option-radio"></div>
                                <div class="step4-option-text">OUI, je suis ouvert à la mobilité géographique</div>
                            </div>
                        </div>
                        
                        <div class="step4-option" data-value="selon-poste" data-question="relocation">
                            <div class="step4-option-content">
                                <div class="step4-option-radio"></div>
                                <div class="step4-option-text">Selon le poste et les conditions proposées</div>
                            </div>
                        </div>
                        
                        <div class="step4-option" data-value="non" data-question="relocation">
                            <div class="step4-option-content">
                                <div class="step4-option-radio"></div>
                                <div class="step4-option-text">NON, je souhaite rester dans ma région actuelle</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Question 5: Informations complémentaires -->
            <div class="step4-container">
                <div class="step4-question">
                    <h3 class="step4-question-title">
                        <i class="fas fa-comment-dots"></i>
                        5) Informations complémentaires (optionnel)
                    </h3>
                    
                    <div class="step4-input-group">
                        <label class="step4-input-label" for="additional-info">
                            Y a-t-il d'autres éléments importants que nous devrions connaître ?
                        </label>
                        <textarea class="step4-input" id="additional-info" name="additional-info" 
                                  rows="4" placeholder="Projets personnels, contraintes particulières, certifications en cours, souhaits spécifiques..."></textarea>
                    </div>
                </div>
            </div>

            <!-- Boutons d'action -->
            <div class="modern-form-actions">
                <button type="button" class="modern-btn btn-secondary" id="back-step3-fixed">
                    <i class="fas fa-arrow-left"></i>
                    <span>Retour</span>
                </button>
                <button type="button" class="modern-btn btn-primary" id="submit-questionnaire-fixed">
                    <span>Finaliser mon profil</span>
                    <i class="fas fa-check-circle"></i>
                </button>
            </div>

            <!-- Styles CSS intégrés pour l'étape 4 -->
            <style>
                .step4-container {
                    background: white;
                    border-radius: 16px;
                    padding: 24px;
                    margin: 20px 0;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
                    border: 1px solid #e5e7eb;
                }
                
                .step4-question-title {
                    font-size: 18px;
                    font-weight: 600;
                    color: #1f2937;
                    margin-bottom: 20px;
                    display: flex;
                    align-items: center;
                    gap: 12px;
                }
                
                .step4-question-title i {
                    color: #7c3aed;
                    font-size: 20px;
                }
                
                .step4-options {
                    display: flex;
                    flex-direction: column;
                    gap: 12px;
                }
                
                .step4-option {
                    background: #f9fafb;
                    border: 2px solid #e5e7eb;
                    border-radius: 12px;
                    padding: 16px;
                    cursor: pointer;
                    transition: all 0.2s ease;
                }
                
                .step4-option:hover {
                    border-color: #7c3aed;
                    background: #faf5ff;
                }
                
                .step4-option.selected {
                    border-color: #7c3aed;
                    background: linear-gradient(135deg, #faf5ff, #f3e8ff);
                }
                
                .step4-option-content {
                    display: flex;
                    align-items: center;
                    gap: 12px;
                }
                
                .step4-option-radio {
                    width: 20px;
                    height: 20px;
                    border: 2px solid #d1d5db;
                    border-radius: 50%;
                    position: relative;
                    transition: all 0.2s ease;
                }
                
                .step4-option.selected .step4-option-radio {
                    border-color: #7c3aed;
                    background: #7c3aed;
                }
                
                .step4-option.selected .step4-option-radio::after {
                    content: '';
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    width: 8px;
                    height: 8px;
                    background: white;
                    border-radius: 50%;
                }
                
                .step4-option-text {
                    font-weight: 500;
                    color: #374151;
                }
                
                .step4-checkbox-group {
                    display: flex;
                    flex-direction: column;
                    gap: 12px;
                }
                
                .step4-checkbox-option {
                    display: flex;
                    align-items: center;
                    gap: 12px;
                    padding: 12px;
                    border-radius: 8px;
                    cursor: pointer;
                    transition: all 0.2s ease;
                }
                
                .step4-checkbox-option:hover {
                    background: #f3f4f6;
                }
                
                .step4-checkbox-option.selected {
                    background: #faf5ff;
                }
                
                .step4-checkbox {
                    width: 20px;
                    height: 20px;
                    border: 2px solid #d1d5db;
                    border-radius: 4px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    transition: all 0.2s ease;
                }
                
                .step4-checkbox-option.selected .step4-checkbox {
                    border-color: #7c3aed;
                    background: #7c3aed;
                }
                
                .step4-checkbox i {
                    color: white;
                    font-size: 12px;
                    display: none;
                }
                
                .step4-checkbox-option.selected .step4-checkbox i {
                    display: block;
                }
                
                .step4-input-group {
                    margin: 20px 0;
                }
                
                .step4-input-label {
                    display: block;
                    font-weight: 600;
                    color: #374151;
                    margin-bottom: 8px;
                }
                
                .step4-input {
                    width: 100%;
                    padding: 12px;
                    border: 2px solid #e5e7eb;
                    border-radius: 8px;
                    font-size: 16px;
                    transition: border-color 0.2s ease;
                }
                
                .step4-input:focus {
                    outline: none;
                    border-color: #7c3aed;
                    box-shadow: 0 0 0 4px rgba(124, 58, 237, 0.1);
                }
                
                .modern-form-actions {
                    display: flex;
                    justify-content: space-between;
                    gap: 16px;
                    margin-top: 32px;
                    padding: 24px;
                    background: #f9fafb;
                    border-radius: 12px;
                }
                
                .modern-btn {
                    padding: 12px 24px;
                    border-radius: 8px;
                    font-weight: 600;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    border: none;
                    cursor: pointer;
                    transition: all 0.2s ease;
                }
                
                .btn-secondary {
                    background: #f3f4f6;
                    color: #374151;
                }
                
                .btn-secondary:hover {
                    background: #e5e7eb;
                }
                
                .btn-primary {
                    background: linear-gradient(135deg, #7c3aed, #8b5cf6);
                    color: white;
                }
                
                .btn-primary:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 8px 25px rgba(124, 58, 237, 0.3);
                }
            </style>
        `;
        
        step4Container.innerHTML = completeContent;
        console.log('✅ Contenu complet étape 4 injecté');
    },
    
    // Configurer les événements de l'étape 4
    setupStep4Events() {
        // Gestion des options radio
        document.addEventListener('click', (e) => {
            const option = e.target.closest('.step4-option[data-question]');
            if (option) {
                this.handleRadioOption(option);
            }
        });
        
        // Gestion des checkboxes
        document.addEventListener('click', (e) => {
            const checkboxOption = e.target.closest('.step4-checkbox-option');
            if (checkboxOption) {
                this.handleCheckboxOption(checkboxOption);
            }
        });
        
        // Bouton retour
        const backButton = document.getElementById('back-step3-fixed');
        if (backButton) {
            backButton.addEventListener('click', () => {
                this.goBackToStep3();
            });
        }
        
        // Bouton finalisation
        const submitButton = document.getElementById('submit-questionnaire-fixed');
        if (submitButton) {
            submitButton.addEventListener('click', () => {
                this.finalizeQuestionnaire();
            });
        }
    },
    
    // Gérer les options radio
    handleRadioOption(option) {
        const question = option.dataset.question;
        const value = option.dataset.value;
        
        // Désélectionner toutes les options du même groupe
        document.querySelectorAll(`[data-question="${question}"]`).forEach(opt => {
            opt.classList.remove('selected');
        });
        
        // Sélectionner l'option cliquée
        option.classList.add('selected');
        
        console.log(`Option sélectionnée: ${question} = ${value}`);
    },
    
    // Gérer les checkboxes
    handleCheckboxOption(option) {
        option.classList.toggle('selected');
        const value = option.dataset.value;
        const isSelected = option.classList.contains('selected');
        
        console.log(`Checkbox ${value}: ${isSelected ? 'sélectionnée' : 'désélectionnée'}`);
    },
    
    // Retour vers l'étape 3
    goBackToStep3() {
        console.log('⬅️ Retour vers étape 3');
        
        // Masquer toutes les étapes
        document.querySelectorAll('.form-step').forEach(step => {
            step.style.display = 'none';
        });
        
        // Afficher l'étape 3
        const step3 = document.getElementById('form-step3');
        if (step3) {
            step3.style.display = 'block';
            this.updateProgressBar(3);
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
    },
    
    // Finaliser le questionnaire
    finalizeQuestionnaire() {
        console.log('🎯 Finalisation du questionnaire...');
        
        // Collecter toutes les données
        const formData = this.collectFormData();
        
        // Afficher un message de succès
        this.showSuccessMessage();
        
        console.log('📊 Données collectées:', formData);
    },
    
    // Collecter les données du formulaire
    collectFormData() {
        const data = {
            step4: {
                timing: this.getSelectedValue('timing'),
                employmentStatus: this.getSelectedValue('employment-status'),
                relocation: this.getSelectedValue('relocation'),
                workPreferences: this.getSelectedCheckboxes('work-preferences'),
                additionalInfo: document.getElementById('additional-info')?.value || ''
            }
        };
        
        return data;
    },
    
    // Obtenir la valeur sélectionnée pour une question radio
    getSelectedValue(question) {
        const selected = document.querySelector(`[data-question="${question}"].selected`);
        return selected ? selected.dataset.value : null;
    },
    
    // Obtenir les checkboxes sélectionnées
    getSelectedCheckboxes(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return [];
        
        const selected = container.querySelectorAll('.step4-checkbox-option.selected');
        return Array.from(selected).map(option => option.dataset.value);
    },
    
    // Afficher un message de succès
    showSuccessMessage() {
        const message = document.createElement('div');
        message.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: linear-gradient(135deg, #10b981, #059669);
            color: white;
            padding: 32px;
            border-radius: 16px;
            text-align: center;
            box-shadow: 0 20px 40px rgba(0,0,0,0.3);
            z-index: 10000;
            max-width: 400px;
            width: 90%;
        `;
        
        message.innerHTML = `
            <div style="font-size: 48px; margin-bottom: 16px;">
                <i class="fas fa-check-circle"></i>
            </div>
            <h3 style="margin: 0 0 8px 0; font-size: 24px;">Questionnaire complété !</h3>
            <p style="margin: 0; opacity: 0.9;">
                Merci ! Nous analysons votre profil et reviendrons vers vous très prochainement avec des opportunités personnalisées.
            </p>
        `;
        
        document.body.appendChild(message);
        
        // Supprimer après 3 secondes
        setTimeout(() => {
            message.remove();
        }, 3000);
    },
    
    // Réessayer l'initialisation
    retryInit() {
        if (this.state.retryCount < this.config.maxRetries) {
            this.state.retryCount++;
            console.log(`🔄 Tentative ${this.state.retryCount}/${this.config.maxRetries}...`);
            
            setTimeout(() => {
                this.safeInit();
            }, this.config.retryDelay * this.state.retryCount);
        } else {
            console.error('❌ Échec de l\'initialisation après', this.config.maxRetries, 'tentatives');
        }
    },
    
    // Méthode publique pour forcer la navigation vers l'étape 4
    forceNavigateToStep4() {
        this.navigateToStep4();
    }
};

// ===== INITIALISATION AUTOMATIQUE =====
function initializeStep4Fix() {
    console.log('🚀 Lancement de la correction étape 4...');
    
    // Attendre que le DOM soit prêt
    const startFix = () => {
        // Vérifier que les éléments de base existent
        const step4Container = document.getElementById('form-step4');
        const nextStep3Button = document.getElementById('next-step3');
        
        if (step4Container && nextStep3Button) {
            // Initialiser la correction
            window.nextenStep4Fix.init();
            
            console.log('✅ Correction étape 4 opérationnelle');
            
            // Optionnel: navigation automatique vers l'étape 4 pour test
            if (window.nextenStep4Fix.config.forceStep4) {
                setTimeout(() => {
                    console.log('🎯 Test automatique: navigation vers étape 4');
                    window.nextenStep4Fix.forceNavigateToStep4();
                }, 1000);
            }
            
        } else {
            console.warn('⚠️ Éléments non trouvés, nouvelle tentative...');
            setTimeout(startFix, 300);
        }
    };
    
    // Démarrer après chargement
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            setTimeout(startFix, 100);
        });
    } else {
        setTimeout(startFix, 100);
    }
}

// Démarrer la correction
initializeStep4Fix();

// Export pour usage externe
window.nextenStep4FixReady = true;

console.log('✅ Script de correction navigation étape 4 chargé');
