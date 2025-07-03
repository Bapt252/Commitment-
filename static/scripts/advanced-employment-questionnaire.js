// ===== 🎯 PARCOURS CONDITIONNEL AVANCÉ ÉTAPE 4 - VERSION OPTIMISÉE =====
// 🔧 Corrections apportées :
// - Timing d'attachement des événements amélioré
// - Gestion robuste des événements checkboxes
// - Prévention des doublons d'événements
// - Débuggage amélioré

console.log('🎯 Chargement du parcours conditionnel avancé OPTIMISÉ...');

// ===== SYSTÈME DE PARCOURS CONDITIONNEL AVANCÉ OPTIMISÉ =====
window.advancedEmploymentQuestionnaire = {
    // 📊 Structure de données
    formData: {
        currentlyEmployed: null,
        listeningReasons: [],
        noticeTime: null,
        noticeNegotiable: null,
        recruitmentStatus: null,
        unemployedRecruitmentStatus: null,
        lastContractEndReasons: []
    },

    // 🔧 Initialisation avec timing amélioré
    init() {
        console.log('🔧 Initialisation du parcours conditionnel avancé OPTIMISÉ...');
        
        // Attendre que l'étape 4 soit prête avec plusieurs tentatives
        this.waitForStep4Ready(() => {
            this.replaceEmploymentQuestion();
            
            // Attendre un délai avant d'attacher les événements
            setTimeout(() => {
                this.setupEventListeners();
                this.attachCheckboxEventsRobust(); // Version renforcée
                this.preserveExistingFunctionality();
                this.validateSetup(); // Nouvelle validation
                
                console.log('✅ Parcours conditionnel avancé OPTIMISÉ initialisé');
            }, 300); // Délai augmenté
        });
    },

    // 🔄 Remplacer la question d'emploi (inchangé)
    replaceEmploymentQuestion() {
        console.log('🔄 Remplacement de la question d\'emploi...');
        
        const employmentQuestionContainer = this.findEmploymentQuestionContainer();
        if (!employmentQuestionContainer) {
            console.error('❌ Question d\'emploi non trouvée');
            return;
        }

        const questionTitle = employmentQuestionContainer.querySelector('.step4-question-title, h3');
        if (!questionTitle || !questionTitle.textContent.includes('Êtes-vous actuellement en poste')) {
            console.error('❌ Mauvaise question détectée');
            return;
        }

        const newEmploymentHTML = this.createAdvancedEmploymentHTML();
        employmentQuestionContainer.innerHTML = newEmploymentHTML;
        
        // Injecter les styles optimisés
        this.injectOptimizedStyles();
        
        console.log('✅ Question d\'emploi remplacée avec succès');
    },

    // 🆕 Styles CSS optimisés pour les checkboxes
    injectOptimizedStyles() {
        const existingStyle = document.getElementById('advanced-checkbox-styles-optimized');
        if (existingStyle) {
            existingStyle.remove();
        }

        const style = document.createElement('style');
        style.id = 'advanced-checkbox-styles-optimized';
        style.textContent = `
            /* Styles optimisés pour les checkboxes */
            .step4-checkbox-option {
                cursor: pointer !important;
                transition: all 0.3s ease !important;
                user-select: none !important;
                -webkit-user-select: none !important;
                -moz-user-select: none !important;
                -ms-user-select: none !important;
            }

            .step4-checkbox-option:hover {
                border-color: #a855f7 !important;
                background: rgba(124, 58, 237, 0.03) !important;
                transform: translateX(2px) !important;
            }

            .step4-checkbox-option.selected {
                border-color: #7c3aed !important;
                background: rgba(124, 58, 237, 0.08) !important;
                transform: translateX(2px) !important;
                box-shadow: 0 4px 12px rgba(124, 58, 237, 0.2) !important;
            }

            .step4-checkbox-option.selected .step4-checkbox {
                border-color: #7c3aed !important;
                background: #7c3aed !important;
                color: white !important;
            }

            .step4-checkbox-option.selected .step4-checkbox i {
                display: block !important;
                opacity: 1 !important;
                color: white !important;
            }

            .step4-checkbox {
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                width: 20px !important;
                height: 20px !important;
                border: 2px solid #d1d5db !important;
                border-radius: 4px !important;
                transition: all 0.2s ease !important;
                flex-shrink: 0 !important;
                background: white !important;
                pointer-events: none !important;
            }

            .step4-checkbox i {
                font-size: 0.75rem !important;
                display: none !important;
                opacity: 0 !important;
                transition: all 0.2s ease !important;
                pointer-events: none !important;
            }

            /* Amélioration du feedback visuel */
            .step4-checkbox-option::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                border-radius: inherit;
                z-index: -1;
                opacity: 0;
                transition: opacity 0.3s ease;
            }

            .step4-checkbox-option:hover::before {
                opacity: 1;
                background: linear-gradient(45deg, rgba(124, 58, 237, 0.1), rgba(168, 85, 247, 0.1));
            }

            .step4-checkbox-option.selected::before {
                opacity: 1;
                background: linear-gradient(45deg, rgba(124, 58, 237, 0.15), rgba(168, 85, 247, 0.15));
            }
        `;
        document.head.appendChild(style);
        console.log('✅ Styles CSS optimisés injectés');
    },

    // 🆕 Attachement d'événements robuste avec gestion des erreurs
    attachCheckboxEventsRobust() {
        console.log('🎯 Attachement d\'événements robuste pour les checkboxes...');
        
        // Utiliser setTimeout pour s'assurer que le DOM est stabilisé
        setTimeout(() => {
            const checkboxes = document.querySelectorAll('.step4-checkbox-option');
            console.log(`🔍 ${checkboxes.length} checkboxes détectées`);
            
            // Nettoyer les anciens événements
            checkboxes.forEach(checkbox => {
                checkbox.removeEventListener('click', this.handleCheckboxClick);
                checkbox.removeEventListener('click', this.handleCheckboxClickBound);
            });
            
            // Créer une fonction liée pour pouvoir la supprimer plus tard
            this.handleCheckboxClickBound = this.handleCheckboxClick.bind(this);
            
            // Attacher les nouveaux événements
            checkboxes.forEach((checkbox, index) => {
                // Vérifier que l'élément est bien une checkbox
                if (checkbox.classList.contains('step4-checkbox-option')) {
                    checkbox.addEventListener('click', this.handleCheckboxClickBound, { 
                        passive: false,
                        capture: true 
                    });
                    
                    // Assurer le curseur pointeur
                    checkbox.style.cursor = 'pointer';
                    
                    // Ajouter un attribut pour identifier la checkbox
                    checkbox.setAttribute('data-checkbox-index', index);
                    
                    console.log(`  ✓ Checkbox ${index + 1} attachée:`, checkbox.dataset.value);
                }
            });
            
            console.log('✅ Événements attachés avec succès');
            
            // Vérification post-attachement
            setTimeout(() => {
                this.validateCheckboxes();
            }, 100);
            
        }, 150);
    },

    // 🆕 Gestionnaire d'événements optimisé
    handleCheckboxClick(event) {
        // Prévenir la propagation
        event.preventDefault();
        event.stopPropagation();
        event.stopImmediatePropagation();
        
        const checkbox = event.currentTarget;
        const value = checkbox.dataset.value;
        
        if (!value) {
            console.warn('⚠️ Checkbox sans valeur détectée');
            return false;
        }
        
        console.log(`🎯 Clic sur checkbox: "${value}"`);
        
        // Basculer la sélection
        const isCurrentlySelected = checkbox.classList.contains('selected');
        
        if (isCurrentlySelected) {
            checkbox.classList.remove('selected');
            console.log(`  ❌ Désélection: "${value}"`);
        } else {
            checkbox.classList.add('selected');
            console.log(`  ✅ Sélection: "${value}"`);
        }
        
        // Mettre à jour les données
        this.updateCheckboxData(checkbox, value, !isCurrentlySelected);
        
        // Sauvegarder dans les champs cachés
        this.saveToHiddenFields();
        
        // Feedback visuel immédiat
        this.provideFeedback(checkbox, !isCurrentlySelected);
        
        return false;
    },

    // 🆕 Feedback visuel immédiat
    provideFeedback(checkbox, isSelected) {
        if (isSelected) {
            checkbox.style.transform = 'scale(1.05)';
            setTimeout(() => {
                checkbox.style.transform = 'translateX(2px)';
            }, 150);
        } else {
            checkbox.style.transform = 'scale(0.98)';
            setTimeout(() => {
                checkbox.style.transform = 'translateX(0)';
            }, 150);
        }
    },

    // 🆕 Validation de la configuration
    validateSetup() {
        console.log('🔍 Validation de la configuration...');
        
        const checkboxes = document.querySelectorAll('.step4-checkbox-option');
        const radioOptions = document.querySelectorAll('.step4-option[data-question="employment-status"]');
        
        console.log(`📊 État de la configuration:
        - Checkboxes: ${checkboxes.length}
        - Options radio: ${radioOptions.length}
        - Styles injectés: ${document.getElementById('advanced-checkbox-styles-optimized') ? 'Oui' : 'Non'}
        - Question timing préservée: ${this.validateTimingQuestionIntegrity() ? 'Oui' : 'Non'}`);
        
        // Vérifier que chaque checkbox a un gestionnaire d'événements
        const checkboxesWithEvents = Array.from(checkboxes).filter(cb => 
            cb.style.cursor === 'pointer' && cb.hasAttribute('data-checkbox-index')
        );
        
        console.log(`✅ Checkboxes avec événements: ${checkboxesWithEvents.length}/${checkboxes.length}`);
        
        if (checkboxesWithEvents.length === checkboxes.length) {
            console.log('🎉 Configuration validée avec succès !');
            return true;
        } else {
            console.warn('⚠️ Configuration incomplète, tentative de correction...');
            setTimeout(() => this.attachCheckboxEventsRobust(), 200);
            return false;
        }
    },

    // 🆕 Validation des checkboxes
    validateCheckboxes() {
        const checkboxes = document.querySelectorAll('.step4-checkbox-option');
        let validCheckboxes = 0;
        
        checkboxes.forEach((checkbox, index) => {
            const hasEvents = checkbox.hasAttribute('data-checkbox-index');
            const hasValue = checkbox.dataset.value;
            const hasClickHandler = checkbox.style.cursor === 'pointer';
            
            if (hasEvents && hasValue && hasClickHandler) {
                validCheckboxes++;
            } else {
                console.warn(`⚠️ Checkbox ${index + 1} invalide:`, {
                    hasEvents,
                    hasValue,
                    hasClickHandler,
                    value: hasValue
                });
            }
        });
        
        console.log(`✅ Validation: ${validCheckboxes}/${checkboxes.length} checkboxes valides`);
        return validCheckboxes === checkboxes.length;
    },

    // Méthodes existantes (inchangées)
    waitForStep4Ready(callback) {
        const checkStep4 = () => {
            const step4Container = document.getElementById('form-step4');
            const employmentSection = document.querySelector('[data-question="employment-status"]');
            const timingQuestion = this.validateTimingQuestionIntegrity();
            
            if (step4Container && employmentSection && timingQuestion) {
                console.log('✅ Étape 4 prête');
                callback();
            } else {
                setTimeout(checkStep4, 200);
            }
        };
        
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                setTimeout(checkStep4, 300);
            });
        } else {
            setTimeout(checkStep4, 100);
        }
    },

    validateTimingQuestionIntegrity() {
        const timingQuestions = document.querySelectorAll('#form-step4 .step4-question-title, #form-step4 h3');
        
        for (const question of timingQuestions) {
            const questionText = question.textContent.toLowerCase();
            if (questionText.includes('quand cherchez-vous')) {
                return true;
            }
        }
        
        const timingOptions = document.querySelector('[data-question="timing"]');
        return !!timingOptions;
    },

    findEmploymentQuestionContainer() {
        const allQuestionContainers = document.querySelectorAll('#form-step4 .step4-container');
        
        for (const container of allQuestionContainers) {
            const questionTitle = container.querySelector('.step4-question-title, h3');
            const employmentOptions = container.querySelector('[data-question="employment-status"]');
            
            if (questionTitle && employmentOptions) {
                const titleText = questionTitle.textContent.toLowerCase();
                if (titleText.includes('êtes-vous actuellement en poste')) {
                    return container;
                }
            }
        }
        
        const employmentOption = document.querySelector('[data-question="employment-status"]');
        if (employmentOption) {
            return employmentOption.closest('.step4-container');
        }
        
        return null;
    },

    createAdvancedEmploymentHTML() {
        return `
            <div class="step4-question">
                <h3 class="step4-question-title">
                    <i class="fas fa-briefcase"></i>
                    2) Êtes-vous actuellement en poste ?
                </h3>
                
                <div class="step4-options" id="employment-status-options">
                    <div class="step4-option" data-value="oui" data-question="employment-status">
                        <div class="step4-option-content">
                            <div class="step4-option-radio"></div>
                            <div class="step4-option-text">OUI</div>
                        </div>
                    </div>
                    
                    <div class="step4-option" data-value="non" data-question="employment-status">
                        <div class="step4-option-content">
                            <div class="step4-option-radio"></div>
                            <div class="step4-option-text">NON</div>
                        </div>
                    </div>
                </div>

                <!-- 🟢 PARCOURS EMPLOYÉ -->
                <div class="conditional-section" id="employment-yes-section">
                    <div class="conditional-section-title">
                        <i class="fas fa-user-tie"></i>
                        Parcours pour les personnes en poste
                    </div>
                    
                    <div class="step4-input-group">
                        <label class="step4-input-label">
                            <i class="fas fa-question-circle"></i>
                            Pourquoi êtes-vous de nouveau à l'écoute ? (plusieurs choix possibles)
                        </label>
                        <div class="step4-checkbox-group" id="listening-reasons-employed">
                            <div class="step4-checkbox-option" data-value="evolution">
                                <div class="step4-checkbox">
                                    <i class="fas fa-check"></i>
                                </div>
                                <div class="step4-checkbox-text">Manque de perspectives d'évolution</div>
                            </div>
                            <div class="step4-checkbox-option" data-value="remuneration">
                                <div class="step4-checkbox">
                                    <i class="fas fa-check"></i>
                                </div>
                                <div class="step4-checkbox-text">Rémunération trop faible</div>
                            </div>
                            <div class="step4-checkbox-option" data-value="distance">
                                <div class="step4-checkbox">
                                    <i class="fas fa-check"></i>
                                </div>
                                <div class="step4-checkbox-text">Poste trop loin de mon domicile</div>
                            </div>
                            <div class="step4-checkbox-option" data-value="flexibilite">
                                <div class="step4-checkbox">
                                    <i class="fas fa-check"></i>
                                </div>
                                <div class="step4-checkbox-text">Manque de flexibilité (pas de TT, RTT)</div>
                            </div>
                            <div class="step4-checkbox-option" data-value="problemes-internes">
                                <div class="step4-checkbox">
                                    <i class="fas fa-check"></i>
                                </div>
                                <div class="step4-checkbox-text">Problème en interne (organisation, management)</div>
                            </div>
                            <div class="step4-checkbox-option" data-value="ne-souhaite-pas">
                                <div class="step4-checkbox">
                                    <i class="fas fa-check"></i>
                                </div>
                                <div class="step4-checkbox-text">Je ne souhaite pas communiquer</div>
                            </div>
                            <div class="step4-checkbox-option" data-value="poste-different">
                                <div class="step4-checkbox">
                                    <i class="fas fa-check"></i>
                                </div>
                                <div class="step4-checkbox-text">Le poste ne coïncide pas avec le poste proposé initialement</div>
                            </div>
                            <div class="step4-checkbox-option" data-value="pse">
                                <div class="step4-checkbox">
                                    <i class="fas fa-check"></i>
                                </div>
                                <div class="step4-checkbox-text">PSE</div>
                            </div>
                            <div class="step4-checkbox-option" data-value="epanouissement">
                                <div class="step4-checkbox">
                                    <i class="fas fa-check"></i>
                                </div>
                                <div class="step4-checkbox-text">Je ne m'épanouis plus, je souhaite découvrir de nouvelles choses</div>
                            </div>
                        </div>
                    </div>

                    <div class="step4-input-group">
                        <label class="step4-input-label">
                            <i class="fas fa-calendar-alt"></i>
                            De combien de temps est votre préavis ?
                        </label>
                        <div class="step4-options" id="notice-time-options">
                            <div class="step4-option" data-value="aucun" data-question="notice-time">
                                <div class="step4-option-content">
                                    <div class="step4-option-radio"></div>
                                    <div class="step4-option-text">Je n'en ai pas, encore en PE</div>
                                </div>
                            </div>
                            <div class="step4-option" data-value="1mois" data-question="notice-time">
                                <div class="step4-option-content">
                                    <div class="step4-option-radio"></div>
                                    <div class="step4-option-text">1 mois</div>
                                </div>
                            </div>
                            <div class="step4-option" data-value="2mois" data-question="notice-time">
                                <div class="step4-option-content">
                                    <div class="step4-option-radio"></div>
                                    <div class="step4-option-text">2 mois</div>
                                </div>
                            </div>
                            <div class="step4-option" data-value="3mois" data-question="notice-time">
                                <div class="step4-option-content">
                                    <div class="step4-option-radio"></div>
                                    <div class="step4-option-text">3 mois</div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="step4-input-group">
                        <label class="step4-input-label">
                            <i class="fas fa-handshake"></i>
                            Est-il négociable ?
                        </label>
                        <div class="step4-options" id="notice-negotiable-options">
                            <div class="step4-option" data-value="oui" data-question="notice-negotiable">
                                <div class="step4-option-content">
                                    <div class="step4-option-radio"></div>
                                    <div class="step4-option-text">OUI</div>
                                </div>
                            </div>
                            <div class="step4-option" data-value="non" data-question="notice-negotiable">
                                <div class="step4-option-content">
                                    <div class="step4-option-radio"></div>
                                    <div class="step4-option-text">NON</div>
                                </div>
                            </div>
                            <div class="step4-option" data-value="ne-sais-pas" data-question="notice-negotiable">
                                <div class="step4-option-content">
                                    <div class="step4-option-radio"></div>
                                    <div class="step4-option-text">Je ne sais pas</div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="step4-input-group">
                        <label class="step4-input-label">
                            <i class="fas fa-search"></i>
                            Où en êtes-vous dans vos processus de recrutement ?
                        </label>
                        <div class="step4-options" id="recruitment-status-employed-options">
                            <div class="step4-option" data-value="aucune-piste" data-question="recruitment-status-employed">
                                <div class="step4-option-content">
                                    <div class="step4-option-radio"></div>
                                    <div class="step4-option-text">Je n'ai pas encore de piste</div>
                                </div>
                            </div>
                            <div class="step4-option" data-value="entretiens" data-question="recruitment-status-employed">
                                <div class="step4-option-content">
                                    <div class="step4-option-radio"></div>
                                    <div class="step4-option-text">J'avance sur différents entretiens</div>
                                </div>
                            </div>
                            <div class="step4-option" data-value="processus-final" data-question="recruitment-status-employed">
                                <div class="step4-option-content">
                                    <div class="step4-option-radio"></div>
                                    <div class="step4-option-text">Je suis en processus final</div>
                                </div>
                            </div>
                            <div class="step4-option" data-value="propositions" data-question="recruitment-status-employed">
                                <div class="step4-option-content">
                                    <div class="step4-option-radio"></div>
                                    <div class="step4-option-text">On m'a fait des propositions</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 🔴 PARCOURS DEMANDEUR D'EMPLOI -->
                <div class="conditional-section" id="employment-no-section">
                    <div class="conditional-section-title">
                        <i class="fas fa-user-plus"></i>
                        Parcours pour les demandeurs d'emploi
                    </div>
                    
                    <div class="step4-input-group">
                        <label class="step4-input-label">
                            <i class="fas fa-search"></i>
                            Où en êtes-vous dans vos processus de recrutement ?
                        </label>
                        <div class="step4-options" id="recruitment-status-unemployed-options">
                            <div class="step4-option" data-value="aucune-piste" data-question="recruitment-status-unemployed">
                                <div class="step4-option-content">
                                    <div class="step4-option-radio"></div>
                                    <div class="step4-option-text">Je n'ai pas encore de piste</div>
                                </div>
                            </div>
                            <div class="step4-option" data-value="entretiens" data-question="recruitment-status-unemployed">
                                <div class="step4-option-content">
                                    <div class="step4-option-radio"></div>
                                    <div class="step4-option-text">J'avance sur différents entretiens</div>
                                </div>
                            </div>
                            <div class="step4-option" data-value="processus-final" data-question="recruitment-status-unemployed">
                                <div class="step4-option-content">
                                    <div class="step4-option-radio"></div>
                                    <div class="step4-option-text">Je suis en processus final</div>
                                </div>
                            </div>
                            <div class="step4-option" data-value="propositions" data-question="recruitment-status-unemployed">
                                <div class="step4-option-content">
                                    <div class="step4-option-radio"></div>
                                    <div class="step4-option-text">On m'a fait des propositions</div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="step4-input-group">
                        <label class="step4-input-label">
                            <i class="fas fa-question-circle"></i>
                            Pourquoi votre dernier contrat s'est-il arrêté ? (plusieurs choix possibles)
                        </label>
                        <div class="step4-checkbox-group" id="last-contract-end-reasons">
                            <div class="step4-checkbox-option" data-value="epanouissement">
                                <div class="step4-checkbox">
                                    <i class="fas fa-check"></i>
                                </div>
                                <div class="step4-checkbox-text">Je ne m'épanouissais plus, je souhaite découvrir de nouvelles choses</div>
                            </div>
                            <div class="step4-checkbox-option" data-value="evolution">
                                <div class="step4-checkbox">
                                    <i class="fas fa-check"></i>
                                </div>
                                <div class="step4-checkbox-text">Manque de perspectives d'évolution</div>
                            </div>
                            <div class="step4-checkbox-option" data-value="distance">
                                <div class="step4-checkbox">
                                    <i class="fas fa-check"></i>
                                </div>
                                <div class="step4-checkbox-text">Poste trop loin de mon domicile</div>
                            </div>
                            <div class="step4-checkbox-option" data-value="flexibilite">
                                <div class="step4-checkbox">
                                    <i class="fas fa-check"></i>
                                </div>
                                <div class="step4-checkbox-text">Manque de flexibilité (pas de TT, RTT)</div>
                            </div>
                            <div class="step4-checkbox-option" data-value="problemes-internes">
                                <div class="step4-checkbox">
                                    <i class="fas fa-check"></i>
                                </div>
                                <div class="step4-checkbox-text">Problème en interne (organisation, management)</div>
                            </div>
                            <div class="step4-checkbox-option" data-value="poste-different">
                                <div class="step4-checkbox">
                                    <i class="fas fa-check"></i>
                                </div>
                                <div class="step4-checkbox-text">Poste ne coïncide pas avec le poste proposé initialement</div>
                            </div>
                            <div class="step4-checkbox-option" data-value="pse">
                                <div class="step4-checkbox">
                                    <i class="fas fa-check"></i>
                                </div>
                                <div class="step4-checkbox-text">PSE</div>
                            </div>
                            <div class="step4-checkbox-option" data-value="ne-souhaite-pas">
                                <div class="step4-checkbox">
                                    <i class="fas fa-check"></i>
                                </div>
                                <div class="step4-checkbox-text">Je ne souhaite pas communiquer</div>
                            </div>
                            <div class="step4-checkbox-option" data-value="remuneration">
                                <div class="step4-checkbox">
                                    <i class="fas fa-check"></i>
                                </div>
                                <div class="step4-checkbox-text">Rémunération trop faible</div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Champs cachés -->
                <input type="hidden" id="hidden-employment-status-advanced" name="employment-status-advanced">
                <input type="hidden" id="hidden-listening-reasons-employed" name="listening-reasons-employed">
                <input type="hidden" id="hidden-notice-time" name="notice-time">
                <input type="hidden" id="hidden-notice-negotiable" name="notice-negotiable">
                <input type="hidden" id="hidden-recruitment-status-employed" name="recruitment-status-employed">
                <input type="hidden" id="hidden-recruitment-status-unemployed" name="recruitment-status-unemployed">
                <input type="hidden" id="hidden-last-contract-end-reasons" name="last-contract-end-reasons">
            </div>
        `;
    },

    // Méthodes utilitaires (simplifiées)
    updateCheckboxData(checkbox, value, isSelected) {
        const container = checkbox.closest('.step4-checkbox-group');
        const groupId = container.id;
        
        if (groupId === 'listening-reasons-employed') {
            this.toggleArrayValue(this.formData.listeningReasons, value);
        } else if (groupId === 'last-contract-end-reasons') {
            this.toggleArrayValue(this.formData.lastContractEndReasons, value);
        }
    },

    toggleArrayValue(array, value) {
        const index = array.indexOf(value);
        if (index === -1) {
            array.push(value);
        } else {
            array.splice(index, 1);
        }
    },

    setupEventListeners() {
        document.addEventListener('click', (e) => {
            const option = e.target.closest('.step4-option[data-question]');
            if (option && this.isAdvancedEmploymentOption(option)) {
                this.handleRadioOption(option);
            }
        });
    },

    isAdvancedEmploymentOption(option) {
        const question = option.dataset.question;
        return ['employment-status', 'notice-time', 'notice-negotiable', 
                'recruitment-status-employed', 'recruitment-status-unemployed'].includes(question);
    },

    handleRadioOption(option) {
        const question = option.dataset.question;
        const value = option.dataset.value;
        
        document.querySelectorAll(`[data-question="${question}"]`).forEach(opt => {
            opt.classList.remove('selected');
        });
        
        option.classList.add('selected');
        this.updateFormData(question, value);
        this.handleConditionalDisplay(question, value);
        this.saveToHiddenFields();
    },

    updateFormData(question, value) {
        switch (question) {
            case 'employment-status':
                this.formData.currentlyEmployed = value;
                break;
            case 'notice-time':
                this.formData.noticeTime = value;
                break;
            case 'notice-negotiable':
                this.formData.noticeNegotiable = value;
                break;
            case 'recruitment-status-employed':
                this.formData.recruitmentStatus = value;
                break;
            case 'recruitment-status-unemployed':
                this.formData.unemployedRecruitmentStatus = value;
                break;
        }
    },

    handleConditionalDisplay(question, value) {
        if (question === 'employment-status') {
            const employedSection = document.getElementById('employment-yes-section');
            const unemployedSection = document.getElementById('employment-no-section');
            
            if (employedSection && unemployedSection) {
                if (value === 'oui') {
                    employedSection.classList.add('active');
                    unemployedSection.classList.remove('active');
                } else if (value === 'non') {
                    employedSection.classList.remove('active');
                    unemployedSection.classList.add('active');
                }
            }
        }
    },

    saveToHiddenFields() {
        const hiddenFields = {
            'hidden-employment-status-advanced': this.formData.currentlyEmployed,
            'hidden-listening-reasons-employed': this.formData.listeningReasons.join(','),
            'hidden-notice-time': this.formData.noticeTime,
            'hidden-notice-negotiable': this.formData.noticeNegotiable,
            'hidden-recruitment-status-employed': this.formData.recruitmentStatus,
            'hidden-recruitment-status-unemployed': this.formData.unemployedRecruitmentStatus,
            'hidden-last-contract-end-reasons': this.formData.lastContractEndReasons.join(',')
        };
        
        Object.entries(hiddenFields).forEach(([id, value]) => {
            const field = document.getElementById(id);
            if (field) {
                field.value = value || '';
            }
        });

        const oldEmploymentField = document.getElementById('hidden-employment-status');
        if (oldEmploymentField) {
            oldEmploymentField.value = this.formData.currentlyEmployed || '';
        }
    },

    preserveExistingFunctionality() {
        const existingSystem = window.step4System;
        if (existingSystem && existingSystem.updateFormData) {
            const originalUpdateFormData = existingSystem.updateFormData.bind(existingSystem);
            existingSystem.updateFormData = function() {
                originalUpdateFormData();
                if (window.advancedEmploymentQuestionnaire) {
                    Object.assign(this.formData, window.advancedEmploymentQuestionnaire.formData);
                }
            };
        }

        this.integrateWithLocalStorage();
    },

    integrateWithLocalStorage() {
        const originalForm = document.getElementById('questionnaire-form');
        if (originalForm) {
            originalForm.addEventListener('submit', (e) => {
                const currentData = JSON.parse(localStorage.getItem('questionnaire_data') || '{}');
                currentData.availability_situation = {
                    ...currentData.availability_situation,
                    advanced_employment: this.formData
                };
                localStorage.setItem('questionnaire_data', JSON.stringify(currentData));
            });
        }
    }
};

// ===== 🚀 INITIALISATION AUTOMATIQUE =====
function initializeAdvancedEmploymentQuestionnaire() {
    console.log('🚀 Initialisation du parcours conditionnel avancé OPTIMISÉ...');
    
    if (typeof window !== 'undefined' && document) {
        window.advancedEmploymentQuestionnaire.init();
    } else {
        console.error('❌ Environnement non compatible');
    }
}

// Lancement avec différents points d'entrée
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeAdvancedEmploymentQuestionnaire);
} else {
    setTimeout(initializeAdvancedEmploymentQuestionnaire, 500);
}

// Point d'entrée de secours
window.addEventListener('load', () => {
    setTimeout(() => {
        if (!window.advancedEmploymentQuestionnaire.formData.currentlyEmployed) {
            console.log('🔄 Réinitialisation de secours...');
            initializeAdvancedEmploymentQuestionnaire();
        }
    }, 1000);
});

console.log('✅ Script optimisé chargé avec succès');