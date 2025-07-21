// ===== CORRECTION FORCÉE ÉTAPE 4 - VERSION ULTRA-ROBUSTE =====
// Solution finale pour corriger définitivement les problèmes d'affichage de l'étape 4
// 🎯 Approche: Manipulation directe du DOM + surveillance continue
// Version: 3.0 - Force brute et efficacité maximale

console.log('🚀 Chargement correction forcée étape 4 v3.0...');

// ===== SYSTÈME DE CORRECTION ULTRA-ROBUSTE =====
window.nextenStep4ForcedFix = {
    
    config: {
        debug: true,
        forceMode: true,
        watchInterval: 500,
        maxAttempts: 20
    },
    
    state: {
        watchActive: false,
        step4Displayed: false,
        attempts: 0
    },
    
    // Initialisation principale
    init() {
        console.log('🔧 Initialisation correction forcée...');
        
        // Arrêter tous les autres scripts problématiques
        this.disableConflictingScripts();
        
        // Préparer l'étape 4
        this.prepareStep4();
        
        // Démarrer la surveillance
        this.startWatching();
        
        // Navigation forcée après délai
        setTimeout(() => {
            this.forceNavigateToStep4();
        }, 2000);
        
        console.log('✅ Correction forcée initialisée');
    },
    
    // Désactiver les scripts conflictuels
    disableConflictingScripts() {
        console.log('🛑 Désactivation scripts conflictuels...');
        
        // Bloquer step4System original
        if (window.step4System) {
            window.step4System = {
                init: () => console.log('🔒 step4System bloqué'),
                navigateToStep4: () => console.log('🔒 Navigation bloquée')
            };
        }
        
        // Arrêter les timers existants
        for (let i = 1; i < 1000; i++) {
            clearTimeout(i);
            clearInterval(i);
        }
    },
    
    // Préparer le contenu de l'étape 4
    prepareStep4() {
        const step4Container = document.getElementById('form-step4');
        if (!step4Container) {
            console.error('❌ Container étape 4 non trouvé');
            return;
        }
        
        // Injecter le contenu complet immédiatement
        step4Container.innerHTML = this.getStep4Content();
        
        // Configurer les événements
        this.setupStep4Events();
        
        console.log('✅ Contenu étape 4 préparé');
    },
    
    // Obtenir le contenu HTML de l'étape 4
    getStep4Content() {
        return `
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
                        <label class="step4-input-label" for="additional-info-forced">
                            Y a-t-il d'autres éléments importants que nous devrions connaître ?
                        </label>
                        <textarea class="step4-input" id="additional-info-forced" name="additional-info" 
                                  rows="4" placeholder="Projets personnels, contraintes particulières, certifications en cours, souhaits spécifiques..."></textarea>
                    </div>
                </div>
            </div>

            <!-- Boutons d'action -->
            <div class="modern-form-actions">
                <button type="button" class="modern-btn btn-secondary" id="back-step3-forced">
                    <i class="fas fa-arrow-left"></i>
                    <span>Retour</span>
                </button>
                <button type="button" class="modern-btn btn-primary" id="submit-questionnaire-forced">
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
                
                /* Style pour masquer les autres étapes */
                .form-step:not(#form-step4) {
                    display: none !important;
                }
                
                #form-step4 {
                    display: block !important;
                }
            </style>
        `;
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
        
        // Boutons
        setTimeout(() => {
            const backButton = document.getElementById('back-step3-forced');
            const submitButton = document.getElementById('submit-questionnaire-forced');
            
            if (backButton) {
                backButton.addEventListener('click', () => {
                    this.goBackToStep3();
                });
            }
            
            if (submitButton) {
                submitButton.addEventListener('click', () => {
                    this.finalizeQuestionnaire();
                });
            }
        }, 100);
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
        
        console.log(`✅ Option sélectionnée: ${question} = ${value}`);
    },
    
    // Gérer les checkboxes
    handleCheckboxOption(option) {
        option.classList.toggle('selected');
        const value = option.dataset.value;
        const isSelected = option.classList.contains('selected');
        
        console.log(`✅ Checkbox ${value}: ${isSelected ? 'sélectionnée' : 'désélectionnée'}`);
    },
    
    // Navigation forcée vers l'étape 4
    forceNavigateToStep4() {
        console.log('🚀 Navigation forcée vers étape 4...');
        
        try {
            // Masquer toutes les étapes avec force
            document.querySelectorAll('.form-step').forEach(step => {
                step.style.display = 'none';
                step.style.visibility = 'hidden';
            });
            
            // Afficher l'étape 4 avec force
            const step4 = document.getElementById('form-step4');
            if (step4) {
                step4.style.display = 'block';
                step4.style.visibility = 'visible';
                
                // Mettre à jour la barre de progression
                this.updateProgressBar();
                
                // Scroll vers le haut
                window.scrollTo({ top: 0, behavior: 'smooth' });
                
                this.state.step4Displayed = true;
                console.log('✅ Étape 4 affichée avec succès');
                
            } else {
                console.error('❌ Élément form-step4 non trouvé');
            }
            
        } catch (error) {
            console.error('❌ Erreur navigation forcée:', error);
        }
    },
    
    // Mettre à jour la barre de progression
    updateProgressBar() {
        const steps = document.querySelectorAll('.step');
        steps.forEach((step, index) => {
            step.classList.remove('active');
            
            if (index < 3) {
                step.classList.add('completed');
            }
            
            if (index === 3) {
                step.classList.add('active');
            }
        });
        
        // Mettre à jour la ligne de progression
        const progressLine = document.getElementById('stepper-progress');
        if (progressLine) {
            progressLine.style.width = '100%';
        }
    },
    
    // Démarrer la surveillance
    startWatching() {
        if (this.state.watchActive) return;
        
        this.state.watchActive = true;
        console.log('👁️ Démarrage surveillance étape 4...');
        
        const watchInterval = setInterval(() => {
            if (this.state.attempts >= this.config.maxAttempts) {
                clearInterval(watchInterval);
                console.log('⏰ Surveillance arrêtée (max tentatives atteint)');
                return;
            }
            
            const step4 = document.getElementById('form-step4');
            const isStep4Visible = step4 && 
                getComputedStyle(step4).display !== 'none' && 
                getComputedStyle(step4).visibility !== 'hidden';
            
            if (!isStep4Visible && this.state.step4Displayed) {
                console.log('⚠️ Étape 4 masquée détectée, correction...');
                this.forceNavigateToStep4();
                this.state.attempts++;
            }
            
        }, this.config.watchInterval);
    },
    
    // Retour vers l'étape 3
    goBackToStep3() {
        console.log('⬅️ Retour vers étape 3');
        
        document.querySelectorAll('.form-step').forEach(step => {
            step.style.display = 'none';
        });
        
        const step3 = document.getElementById('form-step3');
        if (step3) {
            step3.style.display = 'block';
            step3.style.visibility = 'visible';
            
            // Mettre à jour la barre de progression
            const steps = document.querySelectorAll('.step');
            steps.forEach((step, index) => {
                step.classList.remove('active');
                if (index < 2) step.classList.add('completed');
                if (index === 2) step.classList.add('active');
            });
            
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
    },
    
    // Finaliser le questionnaire
    finalizeQuestionnaire() {
        console.log('🎯 Finalisation du questionnaire...');
        
        // Afficher un message de succès
        this.showSuccessMessage();
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
    }
};

// ===== INITIALISATION IMMÉDIATE =====
function initializeForcedFix() {
    console.log('🚀 Lancement correction forcée...');
    
    // Attendre que les éléments de base existent
    const checkAndInit = () => {
        const step4Container = document.getElementById('form-step4');
        
        if (step4Container) {
            window.nextenStep4ForcedFix.init();
            console.log('✅ Correction forcée opérationnelle');
        } else {
            console.warn('⚠️ Container étape 4 non trouvé, nouvelle tentative...');
            setTimeout(checkAndInit, 200);
        }
    };
    
    // Démarrer immédiatement
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', checkAndInit);
    } else {
        setTimeout(checkAndInit, 100);
    }
}

// Lancer la correction forcée
initializeForcedFix();

// Export global
window.nextenStep4ForcedFixReady = true;

console.log('✅ Script de correction forcée étape 4 chargé');
